"""
Risk assessment request handler and orchestration Lambda.

This module processes risk assessment requests and orchestrates the workflow
for calculating risks, generating alerts, creating recommendations, and
storing results.
"""

import json
import os
from typing import Dict, List, Any, Optional

import boto3
from botocore.exceptions import ClientError

# Import internal modules
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from .risk_calculator import calculate_risk_assessment
from .alert_generator import generate_alert
from .reorder_engine import calculate_reorder_recommendation
from .storage import store_risk_assessment
from forecast_engine.storage import get_latest_forecast_for_sku


# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')

# Environment variables
USER_PROFILE_TABLE = os.environ.get('USER_PROFILE_TABLE', 'VyaparSaathi-UserProfile')


class DecimalEncoder(json.JSONEncoder):
    """JSON encoder that handles Decimal types from DynamoDB."""
    def default(self, obj):
        from decimal import Decimal
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


def assess_inventory_risk(
    user_id: str,
    sku: str,
    category: str,
    current_stock: int,
    safety_stock: int = 0,
    shelf_life_days: Optional[int] = None,
    unit_cost: float = 0.0,
    lead_time_days: int = 7,
    carrying_cost_rate: float = 0.02,
    generate_alerts: bool = True,
    store_results: bool = True
) -> Dict[str, Any]:
    """
    Assess inventory risk for a SKU.
    
    This is the main orchestration function that:
    1. Retrieves demand forecast for the SKU
    2. Calculates risk assessment
    3. Generates reorder recommendation
    4. Generates alerts if enabled
    5. Stores results if enabled
    
    Args:
        user_id: User identifier
        sku: Product SKU identifier
        category: Product category
        current_stock: Current inventory level
        safety_stock: Minimum safety stock level
        shelf_life_days: Product shelf life (None for non-perishable)
        unit_cost: Cost per unit
        lead_time_days: Supplier lead time in days
        carrying_cost_rate: Monthly carrying cost rate
        generate_alerts: Whether to generate alerts
        store_results: Whether to store results in DynamoDB
        
    Returns:
        Complete risk assessment result with recommendation and optional alert
    """
    # Get user profile for data quality assessment
    user_profile = get_user_profile(user_id)
    data_quality = None
    if user_profile:
        data_capabilities = user_profile.get('dataCapabilities', {})
        quality_scores = {'poor': 0.3, 'fair': 0.6, 'good': 0.9}
        data_quality = {
            'quality': data_capabilities.get('dataQuality', 'fair'),
            'score': quality_scores.get(data_capabilities.get('dataQuality', 'fair'), 0.6)
        }
    
    # Retrieve demand forecast for the SKU
    forecast_data = get_latest_forecast_for_sku(user_id, sku)
    
    if not forecast_data:
        return {
            'success': False,
            'error': f'No forecast data found for SKU {sku}',
            'sku': sku,
            'userId': user_id
        }
    
    # Extract demand predictions
    demand_forecast = forecast_data.get('predictions', [])
    
    if not demand_forecast:
        return {
            'success': False,
            'error': f'No demand predictions found in forecast for SKU {sku}',
            'sku': sku,
            'userId': user_id
        }
    
    # Calculate risk assessment
    risk_assessment = calculate_risk_assessment(
        sku=sku,
        category=category,
        current_stock=current_stock,
        demand_forecast=demand_forecast,
        safety_stock=safety_stock,
        shelf_life_days=shelf_life_days,
        unit_cost=unit_cost,
        lead_time_days=lead_time_days,
        carrying_cost_rate=carrying_cost_rate
    )
    
    # Calculate reorder recommendation
    recommendation = calculate_reorder_recommendation(
        risk_assessment=risk_assessment,
        demand_forecast=demand_forecast,
        data_quality=data_quality
    )
    
    # Add recommendation to risk assessment
    risk_assessment['recommendation'] = recommendation
    
    # Generate alert if enabled
    alert = None
    if generate_alerts:
        alert = generate_alert(risk_assessment, alert_type='both')
    
    # Store results if enabled
    storage_result = None
    if store_results:
        storage_result = store_risk_assessment(
            user_id=user_id,
            risk_assessment=risk_assessment,
            recommendation=recommendation,
            alert=alert,
            ttl_days=90
        )
    
    # Build response
    result = {
        'success': True,
        'userId': user_id,
        'riskAssessment': risk_assessment,
        'alert': alert,
        'forecastMetadata': {
            'forecastId': forecast_data.get('forecastId'),
            'methodology': forecast_data.get('methodology'),
            'confidence': forecast_data.get('confidence')
        }
    }
    
    if storage_result:
        result['storage'] = storage_result
    
    return result


def assess_multiple_skus(
    user_id: str,
    inventory_items: List[Dict[str, Any]],
    generate_alerts: bool = True,
    store_results: bool = True
) -> Dict[str, Any]:
    """
    Assess inventory risk for multiple SKUs.
    
    Args:
        user_id: User identifier
        inventory_items: List of inventory item dictionaries with SKU details
        generate_alerts: Whether to generate alerts
        store_results: Whether to store results
        
    Returns:
        Dictionary with results for all SKUs
    """
    results = []
    errors = []
    
    for item in inventory_items:
        try:
            result = assess_inventory_risk(
                user_id=user_id,
                sku=item.get('sku'),
                category=item.get('category'),
                current_stock=item.get('currentStock'),
                safety_stock=item.get('safetyStock', 0),
                shelf_life_days=item.get('shelfLifeDays'),
                unit_cost=item.get('unitCost', 0.0),
                lead_time_days=item.get('leadTimeDays', 7),
                carrying_cost_rate=item.get('carryingCostRate', 0.02),
                generate_alerts=generate_alerts,
                store_results=store_results
            )
            
            if result.get('success'):
                results.append(result)
            else:
                errors.append(result)
                
        except Exception as e:
            errors.append({
                'sku': item.get('sku'),
                'error': str(e)
            })
    
    return {
        'success': len(errors) == 0,
        'userId': user_id,
        'totalItems': len(inventory_items),
        'successCount': len(results),
        'errorCount': len(errors),
        'results': results,
        'errors': errors if errors else None
    }


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for risk assessment requests.
    
    Expected event structure for single SKU:
    {
        "userId": "user123",
        "sku": "SKU001",
        "category": "grocery",
        "currentStock": 100,
        "safetyStock": 20,
        "shelfLifeDays": 30,  // optional
        "unitCost": 10.0,
        "leadTimeDays": 7,
        "carryingCostRate": 0.02,
        "generateAlerts": true,  // optional
        "storeResults": true  // optional
    }
    
    For multiple SKUs:
    {
        "userId": "user123",
        "inventoryItems": [
            { "sku": "SKU001", "category": "grocery", "currentStock": 100, ... },
            { "sku": "SKU002", "category": "apparel", "currentStock": 50, ... }
        ],
        "generateAlerts": true,
        "storeResults": true
    }
    
    Args:
        event: Lambda event with risk assessment request
        context: Lambda context
        
    Returns:
        API Gateway response with risk assessment results
    """
    try:
        # Parse request body
        if 'body' in event:
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        else:
            body = event
        
        # Extract parameters
        user_id = body.get('userId')
        
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
        
        # Check if multiple SKUs or single SKU
        inventory_items = body.get('inventoryItems')
        
        if inventory_items:
            # Multiple SKUs
            generate_alerts = body.get('generateAlerts', True)
            store_results = body.get('storeResults', True)
            
            result = assess_multiple_skus(
                user_id=user_id,
                inventory_items=inventory_items,
                generate_alerts=generate_alerts,
                store_results=store_results
            )
        else:
            # Single SKU
            sku = body.get('sku')
            category = body.get('category')
            current_stock = body.get('currentStock')
            
            if not all([sku, category, current_stock is not None]):
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                    },
                    'body': json.dumps({
                        'error': 'Missing required parameters: sku, category, currentStock'
                    })
                }
            
            result = assess_inventory_risk(
                user_id=user_id,
                sku=sku,
                category=category,
                current_stock=current_stock,
                safety_stock=body.get('safetyStock', 0),
                shelf_life_days=body.get('shelfLifeDays'),
                unit_cost=body.get('unitCost', 0.0),
                lead_time_days=body.get('leadTimeDays', 7),
                carrying_cost_rate=body.get('carryingCostRate', 0.02),
                generate_alerts=body.get('generateAlerts', True),
                store_results=body.get('storeResults', True)
            )
        
        # Return response
        status_code = 200 if result.get('success') else 400
        
        return {
            'statusCode': status_code,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            'body': json.dumps(result, cls=DecimalEncoder)
        }
        
    except Exception as e:
        print(f"Error processing risk assessment request: {e}")
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
