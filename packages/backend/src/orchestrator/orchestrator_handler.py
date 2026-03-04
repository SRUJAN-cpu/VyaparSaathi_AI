"""
Main orchestration Lambda to coordinate workflow.

This module serves as the main entry point for the VyaparSaathi system,
coordinating the workflow between data processing, forecasting, risk assessment,
and AI explanation components. It routes requests based on data availability,
implements parallel processing for performance optimization, and aggregates
results for the frontend.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from decimal import Decimal

import boto3
from botocore.exceptions import ClientError

# Import internal modules
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from forecast_engine.forecast_handler import generate_forecast
from risk_assessor.risk_handler import assess_inventory_risk, assess_multiple_skus
from ai_explainer.explanation_handler import generate_explanation
from data_processor.data_prioritization import select_data_source
from utils.error_handling import (
    ValidationError,
    DataNotFoundError,
    ErrorResponseFormatter,
    VyaparSaathiError
)
from utils.performance import lambda_handler_wrapper, PerformanceMonitor


# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')

# Environment variables
USER_PROFILE_TABLE = os.environ.get('USER_PROFILE_TABLE', 'VyaparSaathi-UserProfile')
FORECASTS_TABLE = os.environ.get('FORECASTS_TABLE', 'VyaparSaathi-Forecasts')


class DecimalEncoder(json.JSONEncoder):
    """JSON encoder that handles Decimal types from DynamoDB."""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)


def get_user_profile(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve user profile from DynamoDB.
    
    Args:
        user_id: User identifier
        
    Returns:
        User profile dictionary or None if not found
    """
    table = dynamodb.Table(USER_PROFILE_TABLE)
    
    try:
        response = table.get_item(Key={'userId': user_id})
        return response.get('Item')
    except ClientError as e:
        print(f"Error retrieving user profile: {e}")
        return None


def determine_data_mode(user_id: str) -> Dict[str, Any]:
    """
    Determine data availability and quality for routing decisions.
    
    This implements Requirement 1.4: prioritize structured data over manual estimates.
    
    Args:
        user_id: User identifier
        
    Returns:
        Dictionary with data mode information
    """
    user_profile = get_user_profile(user_id)
    
    if not user_profile:
        return {
            'mode': 'low-data',
            'hasStructuredData': False,
            'quality': 'poor',
            'score': 0.0
        }
    
    # Use data prioritization logic
    data_source = select_data_source(user_id)
    
    return {
        'mode': data_source.get('selectedSource', 'low-data'),
        'hasStructuredData': data_source.get('hasStructuredData', False),
        'quality': data_source.get('quality', 'poor'),
        'score': data_source.get('qualityScore', 0.0),
        'reasoning': data_source.get('reasoning', '')
    }


def orchestrate_forecast_and_risk(
    user_id: str,
    forecast_horizon: int = 14,
    target_festivals: Optional[List[str]] = None,
    inventory_items: Optional[List[Dict[str, Any]]] = None,
    include_explanations: bool = True,
    parallel_execution: bool = True
) -> Dict[str, Any]:
    """
    Orchestrate forecast generation and risk assessment workflow.
    
    This is the main orchestration function that:
    1. Determines data availability and quality
    2. Routes to appropriate forecasting method
    3. Executes forecast and risk assessment (in parallel if enabled)
    4. Optionally generates AI explanations
    5. Aggregates and returns results
    
    Implements Requirements:
    - 1.4: Data source prioritization
    - 6.1: 30-second performance requirement
    
    Args:
        user_id: User identifier
        forecast_horizon: Number of days to forecast (7-14)
        target_festivals: Optional list of festival names
        inventory_items: Optional list of inventory items for risk assessment
        include_explanations: Whether to generate AI explanations
        parallel_execution: Whether to run forecast and risk in parallel
        
    Returns:
        Aggregated results dictionary
    """
    start_time = datetime.utcnow()
    
    # Step 1: Determine data mode and routing
    data_mode_info = determine_data_mode(user_id)
    
    # Step 2: Generate forecast
    try:
        forecast_result = generate_forecast(
            user_id=user_id,
            forecast_horizon=forecast_horizon,
            target_festivals=target_festivals,
            data_mode=data_mode_info['mode']
        )
    except Exception as e:
        print(f"Error generating forecast: {e}")
        forecast_result = {
            'success': False,
            'error': str(e)
        }
    
    # Step 3: Assess risks (parallel or sequential)
    risk_results = None
    
    if inventory_items and forecast_result.get('forecasts'):
        try:
            if parallel_execution:
                # Execute risk assessments in parallel using ThreadPoolExecutor
                risk_results = assess_multiple_skus(
                    user_id=user_id,
                    inventory_items=inventory_items,
                    generate_alerts=True,
                    store_results=True
                )
            else:
                # Sequential execution
                risk_results = assess_multiple_skus(
                    user_id=user_id,
                    inventory_items=inventory_items,
                    generate_alerts=True,
                    store_results=True
                )
        except Exception as e:
            print(f"Error assessing risks: {e}")
            risk_results = {
                'success': False,
                'error': str(e)
            }
    
    # Step 4: Generate explanations (if requested)
    explanations = {}
    
    if include_explanations:
        # Generate forecast explanation
        if forecast_result.get('forecasts'):
            try:
                forecast_explanation = generate_explanation(
                    user_id=user_id,
                    context='forecast',
                    data=forecast_result,
                    complexity='simple'
                )
                explanations['forecast'] = forecast_explanation
            except Exception as e:
                print(f"Error generating forecast explanation: {e}")
                explanations['forecast'] = {'error': str(e)}
        
        # Generate risk explanations
        if risk_results and risk_results.get('results'):
            try:
                # Generate explanation for the highest priority risk
                high_priority_risks = [
                    r for r in risk_results['results']
                    if r.get('riskAssessment', {}).get('recommendation', {}).get('urgency') == 'high'
                ]
                
                if high_priority_risks:
                    risk_explanation = generate_explanation(
                        user_id=user_id,
                        context='risk',
                        data=high_priority_risks[0],
                        complexity='simple'
                    )
                    explanations['risk'] = risk_explanation
            except Exception as e:
                print(f"Error generating risk explanation: {e}")
                explanations['risk'] = {'error': str(e)}
    
    # Step 5: Aggregate results
    end_time = datetime.utcnow()
    processing_time = (end_time - start_time).total_seconds()
    
    result = {
        'success': True,
        'userId': user_id,
        'dataMode': data_mode_info,
        'forecast': forecast_result,
        'risks': risk_results,
        'explanations': explanations if include_explanations else None,
        'metadata': {
            'processingTime': processing_time,
            'timestamp': end_time.isoformat(),
            'parallelExecution': parallel_execution,
            'forecastHorizon': forecast_horizon,
            'performanceTarget': 30.0,
            'meetsPerformanceTarget': processing_time <= 30.0
        }
    }
    
    # Log performance warning if exceeding target
    if processing_time > 30.0:
        print(f"WARNING: Processing time {processing_time}s exceeds 30s target")
    
    return result


def orchestrate_data_upload(
    user_id: str,
    data_type: str,
    data_payload: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Orchestrate data upload workflow.
    
    Routes to appropriate data processor based on data type.
    
    Args:
        user_id: User identifier
        data_type: 'csv' or 'questionnaire'
        data_payload: Data to process
        
    Returns:
        Processing result dictionary
    """
    from data_processor.csv_handler import process_csv_upload
    from data_processor.questionnaire_handler import process_questionnaire
    
    try:
        if data_type == 'csv':
            result = process_csv_upload(
                user_id=user_id,
                file_content=data_payload.get('fileContent'),
                file_name=data_payload.get('fileName')
            )
        elif data_type == 'questionnaire':
            result = process_questionnaire(
                user_id=user_id,
                questionnaire_data=data_payload
            )
        else:
            return {
                'success': False,
                'error': f'Unknown data type: {data_type}'
            }
        
        return result
        
    except Exception as e:
        print(f"Error processing data upload: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def orchestrate_explanation_request(
    user_id: str,
    context: str,
    query: Optional[str] = None,
    sku: Optional[str] = None
) -> Dict[str, Any]:
    """
    Orchestrate explanation generation request.
    
    Fetches relevant data and generates explanation.
    
    Args:
        user_id: User identifier
        context: 'forecast', 'risk', 'recommendation', or 'conversational'
        query: Optional user query for conversational context
        sku: Optional SKU for specific forecast/risk explanation
        
    Returns:
        Explanation result dictionary
    """
    try:
        if context == 'conversational':
            # Handle conversational query
            from ai_explainer.explanation_handler import generate_conversational_response
            
            result = generate_conversational_response(
                user_id=user_id,
                user_query=query or '',
                include_context=True
            )
        else:
            # Fetch relevant data based on context
            if context == 'forecast':
                from forecast_engine.storage import get_latest_forecast_for_sku
                
                if not sku:
                    return {
                        'success': False,
                        'error': 'SKU required for forecast explanation'
                    }
                
                data = get_latest_forecast_for_sku(user_id, sku)
                if not data:
                    return {
                        'success': False,
                        'error': f'No forecast found for SKU {sku}'
                    }
            
            elif context in ['risk', 'recommendation']:
                from risk_assessor.storage import get_latest_risk_for_sku
                
                if not sku:
                    return {
                        'success': False,
                        'error': 'SKU required for risk explanation'
                    }
                
                data = get_latest_risk_for_sku(user_id, sku)
                if not data:
                    return {
                        'success': False,
                        'error': f'No risk assessment found for SKU {sku}'
                    }
            else:
                return {
                    'success': False,
                    'error': f'Unknown context: {context}'
                }
            
            # Generate explanation
            result = generate_explanation(
                user_id=user_id,
                context=context,
                data=data,
                complexity='simple'
            )
        
        return {
            'success': True,
            'explanation': result
        }
        
    except Exception as e:
        print(f"Error generating explanation: {e}")
        return {
            'success': False,
            'error': str(e)
        }


@lambda_handler_wrapper
def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler for orchestration requests.
    
    Routes requests to appropriate orchestration functions based on action type.
    
    Expected event structure:
    {
        "action": "forecast_and_risk" | "data_upload" | "explanation",
        "userId": "user123",
        ... action-specific parameters
    }
    
    For forecast_and_risk:
    {
        "action": "forecast_and_risk",
        "userId": "user123",
        "forecastHorizon": 14,
        "targetFestivals": ["Diwali"],
        "inventoryItems": [...],
        "includeExplanations": true,
        "parallelExecution": true
    }
    
    For data_upload:
    {
        "action": "data_upload",
        "userId": "user123",
        "dataType": "csv" | "questionnaire",
        "dataPayload": {...}
    }
    
    For explanation:
    {
        "action": "explanation",
        "userId": "user123",
        "context": "forecast" | "risk" | "conversational",
        "query": "...",
        "sku": "SKU001"
    }
    
    Args:
        event: Lambda event with orchestration request
        context: Lambda context
        
    Returns:
        API Gateway response with orchestration results
    """
    try:
        # Parse request body
        if 'body' in event:
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        else:
            body = event
        
        # Extract common parameters
        action = body.get('action')
        user_id = body.get('userId')
        
        # Validate required parameters
        if not action:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'body': json.dumps({
                    'error': 'Missing required parameter: action'
                })
            }
        
        if not user_id:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'body': json.dumps({
                    'error': 'Missing required parameter: userId'
                })
            }
        
        # Route to appropriate orchestration function
        if action == 'forecast_and_risk':
            result = orchestrate_forecast_and_risk(
                user_id=user_id,
                forecast_horizon=body.get('forecastHorizon', 14),
                target_festivals=body.get('targetFestivals'),
                inventory_items=body.get('inventoryItems'),
                include_explanations=body.get('includeExplanations', True),
                parallel_execution=body.get('parallelExecution', True)
            )
        
        elif action == 'data_upload':
            data_type = body.get('dataType')
            data_payload = body.get('dataPayload')
            
            if not data_type or not data_payload:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                    },
                    'body': json.dumps({
                        'error': 'Missing required parameters: dataType, dataPayload'
                    })
                }
            
            result = orchestrate_data_upload(
                user_id=user_id,
                data_type=data_type,
                data_payload=data_payload
            )
        
        elif action == 'explanation':
            context_type = body.get('context')
            
            if not context_type:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                    },
                    'body': json.dumps({
                        'error': 'Missing required parameter: context'
                    })
                }
            
            result = orchestrate_explanation_request(
                user_id=user_id,
                context=context_type,
                query=body.get('query'),
                sku=body.get('sku')
            )
        
        else:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'body': json.dumps({
                    'error': f'Unknown action: {action}'
                })
            }
        
        # Return response
        status_code = 200 if result.get('success', True) else 400
        
        return {
            'statusCode': status_code,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            'body': json.dumps(result, cls=DecimalEncoder)
        }
        
    except Exception as e:
        print(f"Error processing orchestration request: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }
