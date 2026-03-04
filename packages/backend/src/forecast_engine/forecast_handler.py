"""
Forecast request handler and orchestration Lambda

This module processes ForecastRequest and orchestrates the forecasting workflow.
It determines the appropriate forecasting methodology based on data availability
and quality, integrates with the festival calendar, and coordinates between
ML-based and pattern-based forecasting approaches.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from decimal import Decimal

import boto3
from botocore.exceptions import ClientError

# Import internal modules
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from festival_calendar.query_handler import query_festivals_by_date_range
from .data_quality import assess_data_quality, determine_forecasting_method
from .storage import store_forecast_results
from utils.error_handling import (
    ValidationError,
    DataNotFoundError,
    ErrorResponseFormatter,
    VyaparSaathiError
)
from utils.performance import lambda_handler_wrapper, PerformanceMonitor


# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
s3_client = boto3.client('s3')

# Environment variables
USER_PROFILE_TABLE = os.environ.get('USER_PROFILE_TABLE', 'VyaparSaathi-UserProfile')
FORECASTS_TABLE = os.environ.get('FORECASTS_TABLE', 'VyaparSaathi-Forecasts')
PROCESSED_DATA_BUCKET = os.environ.get('PROCESSED_DATA_BUCKET', 'vyaparsaathi-processed-data')


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


def get_user_data_quality(user_id: str) -> Dict[str, Any]:
    """
    Assess data quality for a user based on their profile and stored data.
    
    Args:
        user_id: User identifier
        
    Returns:
        Data quality assessment dictionary
    """
    user_profile = get_user_profile(user_id)
    
    if not user_profile:
        return {
            'hasData': False,
            'quality': 'poor',
            'score': 0.0,
            'recordCount': 0,
            'dataMode': 'low-data'
        }
    
    data_capabilities = user_profile.get('dataCapabilities', {})
    has_historical_data = data_capabilities.get('hasHistoricalData', False)
    data_quality = data_capabilities.get('dataQuality', 'poor')
    
    # Map quality to score
    quality_scores = {
        'poor': 0.3,
        'fair': 0.6,
        'good': 0.9
    }
    
    score = quality_scores.get(data_quality, 0.0)
    
    return {
        'hasData': has_historical_data,
        'quality': data_quality,
        'score': score,
        'dataMode': 'structured' if has_historical_data and score >= 0.6 else 'low-data'
    }


def fetch_relevant_festivals(
    start_date: str,
    end_date: str,
    user_profile: Optional[Dict[str, Any]] = None,
    target_festivals: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Fetch relevant festivals for the forecast period.
    
    Args:
        start_date: Start date in ISO format
        end_date: End date in ISO format
        user_profile: Optional user profile with location info
        target_festivals: Optional list of specific festival names to include
        
    Returns:
        List of festival dictionaries
    """
    # Determine region from user profile
    region = None
    if user_profile:
        location = user_profile.get('businessInfo', {}).get('location', {})
        region = location.get('region')
    
    # Query festivals from calendar
    festivals = query_festivals_by_date_range(start_date, end_date, region)
    
    # Filter by target festivals if specified
    if target_festivals:
        festivals = [
            f for f in festivals
            if f['name'] in target_festivals
        ]
    
    return festivals


def generate_forecast(
    user_id: str,
    forecast_horizon: int,
    target_festivals: Optional[List[str]] = None,
    data_mode: Optional[str] = None,
    confidence_threshold: float = 0.5,
    skus: Optional[List[str]] = None,
    categories: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Generate demand forecast for a user.
    
    This is the main orchestration function that:
    1. Assesses data quality
    2. Determines forecasting methodology
    3. Fetches relevant festivals
    4. Delegates to appropriate forecasting mode
    5. Returns forecast results
    
    Args:
        user_id: User identifier
        forecast_horizon: Number of days to forecast (7-14)
        target_festivals: Optional list of festival names to consider
        data_mode: Optional override for data mode ('structured' or 'low-data')
        confidence_threshold: Minimum confidence threshold (0-1)
        skus: Optional list of specific SKUs to forecast
        categories: Optional list of categories to forecast
        
    Returns:
        Forecast result dictionary
    """
    # Get user profile
    user_profile = get_user_profile(user_id)
    
    # Assess data quality
    data_quality = get_user_data_quality(user_id)
    
    # Determine forecasting method
    if data_mode:
        # Use specified mode
        selected_mode = data_mode
    else:
        # Auto-select based on data quality
        selected_mode = data_quality['dataMode']
    
    methodology = determine_forecasting_method(
        data_quality['score'],
        selected_mode
    )
    
    # Calculate date range
    start_date = datetime.utcnow().date().isoformat()
    end_date = (datetime.utcnow().date() + timedelta(days=forecast_horizon)).isoformat()
    
    # Fetch relevant festivals
    festivals = fetch_relevant_festivals(
        start_date,
        end_date,
        user_profile,
        target_festivals
    )
    
    # Prepare forecast context
    forecast_context = {
        'userId': user_id,
        'forecastHorizon': forecast_horizon,
        'startDate': start_date,
        'endDate': end_date,
        'festivals': festivals,
        'dataQuality': data_quality,
        'methodology': methodology,
        'userProfile': user_profile,
        'skus': skus,
        'categories': categories,
        'confidenceThreshold': confidence_threshold
    }
    
    # Delegate to appropriate forecasting mode
    if methodology == 'ml' and selected_mode == 'structured':
        # Use Amazon Forecast (ML-based)
        from .ml_forecaster import generate_ml_forecast
        forecast_results = generate_ml_forecast(forecast_context)
    else:
        # Use pattern-based forecasting
        from .pattern_forecaster import generate_pattern_forecast
        forecast_results = generate_pattern_forecast(forecast_context)
    
    # Add metadata
    forecast_results['metadata'] = {
        'generatedAt': datetime.utcnow().isoformat(),
        'methodology': methodology,
        'dataMode': selected_mode,
        'dataQuality': data_quality['quality'],
        'festivalCount': len(festivals),
        'forecastHorizon': forecast_horizon
    }
    
    # Store forecast results in DynamoDB
    if 'forecasts' in forecast_results:
        storage_result = store_forecast_results(
            user_id=user_id,
            forecast_results=forecast_results['forecasts'],
            ttl_days=30
        )
        forecast_results['storage'] = storage_result
    
    return forecast_results


@lambda_handler_wrapper
def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for forecast requests.
    
    Expected event structure:
    {
        "userId": "user123",
        "forecastHorizon": 14,
        "targetFestivals": ["Diwali", "Dhanteras"],
        "dataMode": "structured",  // optional
        "confidence": 0.7,  // optional
        "skus": ["SKU001", "SKU002"],  // optional
        "categories": ["sweets", "clothing"]  // optional
    }
    
    Args:
        event: Lambda event with forecast request
        context: Lambda context
        
    Returns:
        API Gateway response with forecast results
    """
    try:
        # Parse request body
        if 'body' in event:
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        else:
            body = event
        
        # Extract parameters
        user_id = body.get('userId')
        forecast_horizon = body.get('forecastHorizon', 14)
        target_festivals = body.get('targetFestivals')
        data_mode = body.get('dataMode')
        confidence = body.get('confidence', 0.5)
        skus = body.get('skus')
        categories = body.get('categories')
        
        # Validate required parameters
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
        
        # Validate forecast horizon
        if not (7 <= forecast_horizon <= 14):
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'body': json.dumps({
                    'error': 'Forecast horizon must be between 7 and 14 days'
                })
            }
        
        # Validate confidence threshold
        if not (0 <= confidence <= 1):
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'body': json.dumps({
                    'error': 'Confidence threshold must be between 0 and 1'
                })
            }
        
        # Generate forecast
        forecast_results = generate_forecast(
            user_id=user_id,
            forecast_horizon=forecast_horizon,
            target_festivals=target_festivals,
            data_mode=data_mode,
            confidence_threshold=confidence,
            skus=skus,
            categories=categories
        )
        
        # Return response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            'body': json.dumps(forecast_results, cls=DecimalEncoder)
        }
        
    except Exception as e:
        print(f"Error processing forecast request: {e}")
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
