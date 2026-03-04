"""
Festival calendar query Lambda handler

This module provides Lambda functions to query festivals by date range and region.
Includes caching layer for performance optimization.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from decimal import Decimal

import boto3
from botocore.exceptions import ClientError

# Import performance monitoring utilities
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.performance import PerformanceMonitor, Cache, lambda_handler_wrapper


# Initialize DynamoDB client
dynamodb = boto3.client('dynamodb')
dynamodb_resource = boto3.resource('dynamodb')

# Get table name from environment
FESTIVAL_CALENDAR_TABLE = os.environ.get(
    'FESTIVAL_CALENDAR_TABLE',
    'VyaparSaathi-FestivalCalendar'
)

# In-memory cache for Lambda environment reuse
# This cache persists across invocations in the same Lambda container
FESTIVAL_CACHE: Dict[str, Any] = {}
CACHE_TTL_SECONDS = 3600  # 1 hour


class DecimalEncoder(json.JSONEncoder):
    """JSON encoder that handles Decimal types from DynamoDB."""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)


def get_cache_key(
    start_date: str,
    end_date: str,
    region: Optional[str] = None,
    categories: Optional[List[str]] = None
) -> str:
    """
    Generate cache key for festival query.
    
    Args:
        start_date: Start date in ISO format
        end_date: End date in ISO format
        region: Optional region filter
        categories: Optional category filters
        
    Returns:
        Cache key string
    """
    key_parts = [start_date, end_date]
    if region:
        key_parts.append(region)
    if categories:
        key_parts.append(','.join(sorted(categories)))
    return ':'.join(key_parts)


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


@PerformanceMonitor.measure_execution_time
def query_festivals_by_date_range(
    start_date: str,
    end_date: str,
    region: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Query festivals within a date range, optionally filtered by region.
    
    Uses DynamoDB GSI for efficient querying.
    
    Args:
        start_date: Start date in ISO format (YYYY-MM-DD)
        end_date: End date in ISO format (YYYY-MM-DD)
        region: Optional region filter (north, south, east, west, central)
        
    Returns:
        List of festival dictionaries
    """
    table = dynamodb_resource.Table(FESTIVAL_CALENDAR_TABLE)
    festivals = []
    
    try:
        if region:
            # Use RegionIndex GSI for region-based queries
            response = table.query(
                IndexName='RegionIndex',
                KeyConditionExpression='#region = :region AND #date BETWEEN :start_date AND :end_date',
                ExpressionAttributeNames={
                    '#region': 'region',
                    '#date': 'date',
                },
                ExpressionAttributeValues={
                    ':region': region,
                    ':start_date': start_date,
                    ':end_date': end_date,
                }
            )
            festivals.extend(response.get('Items', []))
            
            # Handle pagination
            while 'LastEvaluatedKey' in response:
                response = table.query(
                    IndexName='RegionIndex',
                    KeyConditionExpression='#region = :region AND #date BETWEEN :start_date AND :end_date',
                    ExpressionAttributeNames={
                        '#region': 'region',
                        '#date': 'date',
                    },
                    ExpressionAttributeValues={
                        ':region': region,
                        ':start_date': start_date,
                        ':end_date': end_date,
                    },
                    ExclusiveStartKey=response['LastEvaluatedKey']
                )
                festivals.extend(response.get('Items', []))
        else:
            # Use DateIndex GSI for date-only queries
            response = table.query(
                IndexName='DateIndex',
                KeyConditionExpression='#date BETWEEN :start_date AND :end_date',
                ExpressionAttributeNames={
                    '#date': 'date',
                },
                ExpressionAttributeValues={
                    ':start_date': start_date,
                    ':end_date': end_date,
                }
            )
            festivals.extend(response.get('Items', []))
            
            # Handle pagination
            while 'LastEvaluatedKey' in response:
                response = table.query(
                    IndexName='DateIndex',
                    KeyConditionExpression='#date BETWEEN :start_date AND :end_date',
                    ExpressionAttributeNames={
                        '#date': 'date',
                    },
                    ExpressionAttributeValues={
                        ':start_date': start_date,
                        ':end_date': end_date,
                    },
                    ExclusiveStartKey=response['LastEvaluatedKey']
                )
                festivals.extend(response.get('Items', []))
        
        # Filter out regional variations if no region specified
        # (keep only base festivals)
        if not region:
            festivals = [
                f for f in festivals
                if not f.get('isRegionalVariation', False)
            ]
        
        return festivals
        
    except ClientError as e:
        print(f"Error querying festivals: {e}")
        raise


def filter_festivals_by_categories(
    festivals: List[Dict[str, Any]],
    categories: List[str]
) -> List[Dict[str, Any]]:
    """
    Filter festivals to include only demand multipliers for specified categories.
    
    Args:
        festivals: List of festival dictionaries
        categories: List of product categories to include
        
    Returns:
        List of festivals with filtered demand multipliers
    """
    filtered_festivals = []
    
    for festival in festivals:
        filtered_festival = festival.copy()
        
        # Filter demand multipliers
        if 'demandMultipliers' in festival:
            filtered_multipliers = {
                category: multiplier
                for category, multiplier in festival['demandMultipliers'].items()
                if category in categories
            }
            filtered_festival['demandMultipliers'] = filtered_multipliers
        
        # Only include festival if it has relevant categories
        if filtered_festival.get('demandMultipliers'):
            filtered_festivals.append(filtered_festival)
    
    return filtered_festivals


@lambda_handler_wrapper
def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for festival calendar queries.
    
    Expected event structure:
    {
        "startDate": "2024-01-01",
        "endDate": "2024-12-31",
        "region": "north",  // optional
        "categories": ["sweets", "clothing"]  // optional
    }
    
    Args:
        event: Lambda event with query parameters
        context: Lambda context
        
    Returns:
        API Gateway response with festival data
    """
    try:
        # Parse request body
        if 'body' in event:
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        else:
            body = event
        
        # Extract parameters
        start_date = body.get('startDate')
        end_date = body.get('endDate')
        region = body.get('region')
        categories = body.get('categories')
        
        # Validate required parameters
        if not start_date or not end_date:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'body': json.dumps({
                    'error': 'Missing required parameters: startDate and endDate'
                })
            }
        
        # Validate date format
        try:
            datetime.fromisoformat(start_date)
            datetime.fromisoformat(end_date)
        except ValueError:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'body': json.dumps({
                    'error': 'Invalid date format. Use ISO format (YYYY-MM-DD)'
                })
            }
        
        # Check cache
        cache_key = get_cache_key(start_date, end_date, region, categories)
        if cache_key in FESTIVAL_CACHE and is_cache_valid(FESTIVAL_CACHE[cache_key]):
            print(f"Cache hit for key: {cache_key}")
            festivals = FESTIVAL_CACHE[cache_key]['data']
        else:
            print(f"Cache miss for key: {cache_key}")
            
            # Query festivals from DynamoDB
            festivals = query_festivals_by_date_range(start_date, end_date, region)
            
            # Filter by categories if specified
            if categories:
                festivals = filter_festivals_by_categories(festivals, categories)
            
            # Update cache
            FESTIVAL_CACHE[cache_key] = {
                'data': festivals,
                'timestamp': datetime.utcnow().isoformat()
            }
        
        # Sort festivals by date
        festivals.sort(key=lambda f: f['date'])
        
        # Return response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            'body': json.dumps({
                'festivals': festivals,
                'count': len(festivals),
                'dateRange': {
                    'start': start_date,
                    'end': end_date,
                },
                'filters': {
                    'region': region,
                    'categories': categories,
                }
            }, cls=DecimalEncoder)
        }
        
    except Exception as e:
        print(f"Error processing request: {e}")
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


def get_upcoming_festivals(
    days_ahead: int = 30,
    region: Optional[str] = None,
    categories: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Get upcoming festivals within specified number of days.
    
    Convenience function for common use case.
    
    Args:
        days_ahead: Number of days to look ahead
        region: Optional region filter
        categories: Optional category filters
        
    Returns:
        List of upcoming festivals
    """
    start_date = datetime.utcnow().date().isoformat()
    end_date = (datetime.utcnow().date() + timedelta(days=days_ahead)).isoformat()
    
    festivals = query_festivals_by_date_range(start_date, end_date, region)
    
    if categories:
        festivals = filter_festivals_by_categories(festivals, categories)
    
    return festivals


def get_festival_by_id(festival_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a specific festival by its ID.
    
    Args:
        festival_id: Festival identifier
        
    Returns:
        Festival dictionary or None if not found
    """
    table = dynamodb_resource.Table(FESTIVAL_CALENDAR_TABLE)
    
    try:
        response = table.get_item(Key={'festivalId': festival_id})
        return response.get('Item')
    except ClientError as e:
        print(f"Error getting festival {festival_id}: {e}")
        return None
