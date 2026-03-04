"""
Forecast result storage and retrieval

This module handles storing ForecastResult in DynamoDB with TTL,
GSI for efficient retrieval, and caching for frequently accessed forecasts.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from decimal import Decimal

import boto3
from botocore.exceptions import ClientError


# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')

# Environment variables
FORECASTS_TABLE = os.environ.get('FORECASTS_TABLE', 'VyaparSaathi-Forecasts')

# In-memory cache for Lambda environment reuse
FORECAST_CACHE: Dict[str, Any] = {}
CACHE_TTL_SECONDS = 1800  # 30 minutes


class DecimalEncoder(json.JSONEncoder):
    """JSON encoder that handles Decimal types from DynamoDB."""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)


def convert_floats_to_decimal(obj: Any) -> Any:
    """
    Convert float values to Decimal for DynamoDB storage.
    
    Args:
        obj: Object to convert
        
    Returns:
        Object with floats converted to Decimal
    """
    if isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, dict):
        return {k: convert_floats_to_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_floats_to_decimal(item) for item in obj]
    else:
        return obj


def convert_decimals_to_float(obj: Any) -> Any:
    """
    Convert Decimal values to float for JSON serialization.
    
    Args:
        obj: Object to convert
        
    Returns:
        Object with Decimals converted to float
    """
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: convert_decimals_to_float(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimals_to_float(item) for item in obj]
    else:
        return obj


def generate_forecast_id(user_id: str, sku: str, generated_at: str) -> str:
    """
    Generate unique forecast ID.
    
    Args:
        user_id: User identifier
        sku: Product SKU
        generated_at: Generation timestamp
        
    Returns:
        Forecast ID string
    """
    timestamp = generated_at.replace(':', '').replace('-', '').replace('.', '')[:14]
    return f"{user_id}#{sku}#{timestamp}"


def store_forecast_result(
    user_id: str,
    forecast_result: Dict[str, Any],
    ttl_days: int = 30
) -> bool:
    """
    Store forecast result in DynamoDB with TTL.
    
    Args:
        user_id: User identifier
        forecast_result: Forecast result dictionary
        ttl_days: Time-to-live in days (default 30)
        
    Returns:
        True if successful, False otherwise
    """
    table = dynamodb.Table(FORECASTS_TABLE)
    
    try:
        # Calculate TTL (Unix timestamp)
        ttl_timestamp = int((datetime.utcnow() + timedelta(days=ttl_days)).timestamp())
        
        # Generate forecast ID
        sku = forecast_result.get('sku', 'unknown')
        generated_at = forecast_result.get('generatedAt', datetime.utcnow().isoformat())
        forecast_id = generate_forecast_id(user_id, sku, generated_at)
        
        # Prepare item for storage
        item = {
            'forecastId': forecast_id,
            'userId': user_id,
            'sku': sku,
            'category': forecast_result.get('category', ''),
            'generatedAt': generated_at,
            'expiresAt': forecast_result.get('expiresAt', ''),
            'ttl': ttl_timestamp,
            'confidence': forecast_result.get('confidence', 0.0),
            'methodology': forecast_result.get('methodology', 'pattern'),
            'predictions': forecast_result.get('predictions', []),
            'assumptions': forecast_result.get('assumptions', []),
        }
        
        # Convert floats to Decimal for DynamoDB
        item = convert_floats_to_decimal(item)
        
        # Store in DynamoDB
        table.put_item(Item=item)
        
        # Invalidate cache for this user
        cache_key = f"{user_id}:*"
        keys_to_remove = [k for k in FORECAST_CACHE.keys() if k.startswith(f"{user_id}:")]
        for key in keys_to_remove:
            del FORECAST_CACHE[key]
        
        return True
        
    except ClientError as e:
        print(f"Error storing forecast result: {e}")
        return False


def store_forecast_results(
    user_id: str,
    forecast_results: List[Dict[str, Any]],
    ttl_days: int = 30
) -> Dict[str, Any]:
    """
    Store multiple forecast results in DynamoDB.
    
    Args:
        user_id: User identifier
        forecast_results: List of forecast result dictionaries
        ttl_days: Time-to-live in days (default 30)
        
    Returns:
        Dictionary with success count and errors
    """
    success_count = 0
    errors = []
    
    for forecast_result in forecast_results:
        try:
            if store_forecast_result(user_id, forecast_result, ttl_days):
                success_count += 1
            else:
                errors.append(f"Failed to store forecast for SKU {forecast_result.get('sku')}")
        except Exception as e:
            errors.append(f"Error storing forecast for SKU {forecast_result.get('sku')}: {str(e)}")
    
    return {
        'successCount': success_count,
        'totalCount': len(forecast_results),
        'errors': errors
    }


def get_forecast_by_id(forecast_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve forecast by ID.
    
    Args:
        forecast_id: Forecast identifier
        
    Returns:
        Forecast dictionary or None if not found
    """
    table = dynamodb.Table(FORECASTS_TABLE)
    
    try:
        response = table.get_item(Key={'forecastId': forecast_id})
        item = response.get('Item')
        
        if item:
            return convert_decimals_to_float(item)
        
        return None
        
    except ClientError as e:
        print(f"Error retrieving forecast: {e}")
        return None


def get_forecasts_by_user(
    user_id: str,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Retrieve forecasts for a user using GSI.
    
    Args:
        user_id: User identifier
        limit: Maximum number of results
        
    Returns:
        List of forecast dictionaries
    """
    # Check cache first
    cache_key = f"{user_id}:all:{limit}"
    if cache_key in FORECAST_CACHE:
        cache_entry = FORECAST_CACHE[cache_key]
        if is_cache_valid(cache_entry):
            return cache_entry['data']
    
    table = dynamodb.Table(FORECASTS_TABLE)
    
    try:
        response = table.query(
            IndexName='UserIdIndex',
            KeyConditionExpression='userId = :userId',
            ExpressionAttributeValues={
                ':userId': user_id
            },
            Limit=limit,
            ScanIndexForward=False  # Most recent first
        )
        
        items = response.get('Items', [])
        forecasts = [convert_decimals_to_float(item) for item in items]
        
        # Update cache
        FORECAST_CACHE[cache_key] = {
            'data': forecasts,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return forecasts
        
    except ClientError as e:
        print(f"Error retrieving forecasts for user: {e}")
        return []


def get_forecasts_by_user_and_sku(
    user_id: str,
    sku: str,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Retrieve forecasts for a specific user and SKU.
    
    Args:
        user_id: User identifier
        sku: Product SKU
        limit: Maximum number of results
        
    Returns:
        List of forecast dictionaries
    """
    # Check cache first
    cache_key = f"{user_id}:{sku}:{limit}"
    if cache_key in FORECAST_CACHE:
        cache_entry = FORECAST_CACHE[cache_key]
        if is_cache_valid(cache_entry):
            return cache_entry['data']
    
    table = dynamodb.Table(FORECASTS_TABLE)
    
    try:
        response = table.query(
            IndexName='UserSkuIndex',
            KeyConditionExpression='userId = :userId AND sku = :sku',
            ExpressionAttributeValues={
                ':userId': user_id,
                ':sku': sku
            },
            Limit=limit,
            ScanIndexForward=False  # Most recent first
        )
        
        items = response.get('Items', [])
        forecasts = [convert_decimals_to_float(item) for item in items]
        
        # Update cache
        FORECAST_CACHE[cache_key] = {
            'data': forecasts,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return forecasts
        
    except ClientError as e:
        print(f"Error retrieving forecasts for user and SKU: {e}")
        return []


def get_forecasts_by_date_range(
    user_id: str,
    start_date: str,
    end_date: str
) -> List[Dict[str, Any]]:
    """
    Retrieve forecasts within a date range.
    
    Args:
        user_id: User identifier
        start_date: Start date in ISO format
        end_date: End date in ISO format
        
    Returns:
        List of forecast dictionaries
    """
    # Check cache first
    cache_key = f"{user_id}:{start_date}:{end_date}"
    if cache_key in FORECAST_CACHE:
        cache_entry = FORECAST_CACHE[cache_key]
        if is_cache_valid(cache_entry):
            return cache_entry['data']
    
    table = dynamodb.Table(FORECASTS_TABLE)
    
    try:
        response = table.query(
            IndexName='UserDateIndex',
            KeyConditionExpression='userId = :userId AND generatedAt BETWEEN :start_date AND :end_date',
            ExpressionAttributeValues={
                ':userId': user_id,
                ':start_date': start_date,
                ':end_date': end_date
            },
            ScanIndexForward=False  # Most recent first
        )
        
        items = response.get('Items', [])
        forecasts = [convert_decimals_to_float(item) for item in items]
        
        # Update cache
        FORECAST_CACHE[cache_key] = {
            'data': forecasts,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return forecasts
        
    except ClientError as e:
        print(f"Error retrieving forecasts by date range: {e}")
        return []


def get_latest_forecast_for_sku(
    user_id: str,
    sku: str
) -> Optional[Dict[str, Any]]:
    """
    Get the most recent forecast for a specific SKU.
    
    Args:
        user_id: User identifier
        sku: Product SKU
        
    Returns:
        Latest forecast dictionary or None if not found
    """
    forecasts = get_forecasts_by_user_and_sku(user_id, sku, limit=1)
    
    if forecasts:
        return forecasts[0]
    
    return None


def is_cache_valid(cache_entry: Dict[str, Any]) -> bool:
    """
    Check if cache entry is still valid.
    
    Args:
        cache_entry: Cache entry with timestamp
        
    Returns:
        True if cache is valid, False otherwise
    """
    if 'timestamp' not in cache_entry:
        return False
    
    cache_time = datetime.fromisoformat(cache_entry['timestamp'])
    current_time = datetime.utcnow()
    age_seconds = (current_time - cache_time).total_seconds()
    
    return age_seconds < CACHE_TTL_SECONDS


def invalidate_cache(user_id: Optional[str] = None):
    """
    Invalidate forecast cache.
    
    Args:
        user_id: Optional user ID to invalidate specific user's cache
    """
    if user_id:
        # Invalidate cache for specific user
        keys_to_remove = [k for k in FORECAST_CACHE.keys() if k.startswith(f"{user_id}:")]
        for key in keys_to_remove:
            del FORECAST_CACHE[key]
    else:
        # Invalidate entire cache
        FORECAST_CACHE.clear()


def delete_forecast(forecast_id: str) -> bool:
    """
    Delete a forecast from DynamoDB.
    
    Args:
        forecast_id: Forecast identifier
        
    Returns:
        True if successful, False otherwise
    """
    table = dynamodb.Table(FORECASTS_TABLE)
    
    try:
        table.delete_item(Key={'forecastId': forecast_id})
        return True
    except ClientError as e:
        print(f"Error deleting forecast: {e}")
        return False


def delete_user_forecasts(user_id: str) -> Dict[str, Any]:
    """
    Delete all forecasts for a user.
    
    Args:
        user_id: User identifier
        
    Returns:
        Dictionary with deletion results
    """
    forecasts = get_forecasts_by_user(user_id, limit=1000)
    
    deleted_count = 0
    errors = []
    
    for forecast in forecasts:
        forecast_id = forecast.get('forecastId')
        if forecast_id:
            if delete_forecast(forecast_id):
                deleted_count += 1
            else:
                errors.append(f"Failed to delete forecast {forecast_id}")
    
    # Invalidate cache
    invalidate_cache(user_id)
    
    return {
        'deletedCount': deleted_count,
        'totalCount': len(forecasts),
        'errors': errors
    }
