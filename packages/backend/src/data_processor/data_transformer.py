"""
Data transformation and storage for VyaparSaathi
Transforms validated data into standardized format and stores in S3
"""

import json
import os
import sys
from typing import Dict, List, Any, Tuple
from datetime import datetime
import boto3
from botocore.exceptions import ClientError

# Import utilities
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.error_handling import (
    ValidationError,
    DatabaseError,
    ErrorResponseFormatter,
    VyaparSaathiError
)
from utils.performance import lambda_handler_wrapper, PerformanceMonitor


class StandardizedSalesRecord:
    """Standardized sales record format"""
    
    def __init__(self, user_id: str, date: str, sku: str, quantity: float,
                 category: str = None, price: float = None, 
                 source: str = 'csv', metadata: Dict[str, Any] = None):
        self.user_id = user_id
        self.date = date
        self.sku = sku
        self.quantity = quantity
        self.category = category
        self.price = price
        self.source = source  # 'csv', 'manual', 'synthetic'
        self.metadata = metadata or {}
        self.processed_at = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {
            'userId': self.user_id,
            'date': self.date,
            'sku': self.sku,
            'quantity': self.quantity,
            'source': self.source,
            'processedAt': self.processed_at
        }
        
        if self.category:
            result['category'] = self.category
        if self.price is not None:
            result['price'] = self.price
        if self.metadata:
            result['metadata'] = self.metadata
        
        return result
    
    def to_json_line(self) -> str:
        """Convert to JSON line format for storage"""
        return json.dumps(self.to_dict())


class DataCapabilitiesMetadata:
    """Metadata about user's data capabilities"""
    
    def __init__(self, has_historical_data: bool, data_quality: str,
                 completeness_score: float, data_history_months: int,
                 record_count: int, sku_count: int, category_count: int):
        self.has_historical_data = has_historical_data
        self.data_quality = data_quality
        self.completeness_score = completeness_score
        self.data_history_months = data_history_months
        self.record_count = record_count
        self.sku_count = sku_count
        self.category_count = category_count
        self.last_updated = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'hasHistoricalData': self.has_historical_data,
            'dataQuality': self.data_quality,
            'completenessScore': self.completeness_score,
            'dataHistoryMonths': self.data_history_months,
            'recordCount': self.record_count,
            'skuCount': self.sku_count,
            'categoryCount': self.category_count,
            'lastUpdated': self.last_updated
        }


def transform_sales_records(user_id: str, raw_records: List[Dict[str, Any]], 
                           source: str = 'csv') -> List[StandardizedSalesRecord]:
    """
    Transform raw sales records into standardized format
    
    Args:
        user_id: User identifier
        raw_records: List of raw sales records
        source: Data source type
    
    Returns:
        List of standardized sales records
    """
    standardized_records = []
    
    for record in raw_records:
        standardized = StandardizedSalesRecord(
            user_id=user_id,
            date=record.get('date'),
            sku=record.get('sku'),
            quantity=record.get('quantity'),
            category=record.get('category'),
            price=record.get('price'),
            source=source,
            metadata=record.get('metadata', {})
        )
        standardized_records.append(standardized)
    
    return standardized_records


def calculate_data_history_months(records: List[StandardizedSalesRecord]) -> int:
    """
    Calculate the number of months of historical data
    
    Args:
        records: List of standardized sales records
    
    Returns:
        Number of months of data
    """
    if not records:
        return 0
    
    try:
        dates = [datetime.strptime(r.date, '%Y-%m-%d') for r in records]
        min_date = min(dates)
        max_date = max(dates)
        
        # Calculate months difference
        months = (max_date.year - min_date.year) * 12 + (max_date.month - min_date.month)
        return max(1, months)
        
    except (ValueError, AttributeError):
        return 0


def calculate_data_capabilities(records: List[StandardizedSalesRecord],
                                quality_score: float) -> DataCapabilitiesMetadata:
    """
    Calculate data capabilities metadata from records
    
    Args:
        records: List of standardized sales records
        quality_score: Data quality score from validation
    
    Returns:
        DataCapabilitiesMetadata object
    """
    if not records:
        return DataCapabilitiesMetadata(
            has_historical_data=False,
            data_quality='poor',
            completeness_score=0.0,
            data_history_months=0,
            record_count=0,
            sku_count=0,
            category_count=0
        )
    
    # Count unique SKUs and categories
    unique_skus = set(r.sku for r in records)
    unique_categories = set(r.category for r in records if r.category)
    
    # Calculate history months
    history_months = calculate_data_history_months(records)
    
    # Determine data quality level
    if quality_score >= 0.8:
        data_quality = 'good'
    elif quality_score >= 0.5:
        data_quality = 'fair'
    else:
        data_quality = 'poor'
    
    return DataCapabilitiesMetadata(
        has_historical_data=True,
        data_quality=data_quality,
        completeness_score=quality_score,
        data_history_months=history_months,
        record_count=len(records),
        sku_count=len(unique_skus),
        category_count=len(unique_categories)
    )


def store_processed_data_to_s3(user_id: str, 
                               records: List[StandardizedSalesRecord],
                               bucket_name: str) -> Tuple[bool, str]:
    """
    Store processed data in S3 as JSON lines
    
    Args:
        user_id: User identifier
        records: List of standardized sales records
        bucket_name: S3 bucket name
    
    Returns:
        Tuple of (success, s3_key or error_message)
    """
    try:
        s3_client = boto3.client('s3')
        
        # Generate S3 key with timestamp
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        s3_key = f"processed-data/{user_id}/{timestamp}_processed_sales.jsonl"
        
        # Convert records to JSON lines format
        json_lines = '\n'.join(record.to_json_line() for record in records)
        
        # Upload to S3
        s3_client.put_object(
            Bucket=bucket_name,
            Key=s3_key,
            Body=json_lines.encode('utf-8'),
            ContentType='application/x-ndjson',
            ServerSideEncryption='AES256',
            Metadata={
                'userId': user_id,
                'recordCount': str(len(records)),
                'processedAt': timestamp
            }
        )
        
        return True, s3_key
        
    except ClientError as e:
        return False, f"S3 upload failed: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error during S3 upload: {str(e)}"


def update_user_profile_capabilities(user_id: str, 
                                     capabilities: DataCapabilitiesMetadata,
                                     s3_key: str,
                                     dynamodb_table: str) -> Tuple[bool, str]:
    """
    Update UserProfile with data capabilities metadata
    
    Args:
        user_id: User identifier
        capabilities: Data capabilities metadata
        s3_key: S3 key where data is stored
        dynamodb_table: DynamoDB table name
    
    Returns:
        Tuple of (success, error_message)
    """
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(dynamodb_table)
        
        # Update user profile
        table.update_item(
            Key={'userId': user_id},
            UpdateExpression='''
                SET dataCapabilities = :capabilities,
                    processedDataLocation = :s3_key,
                    updatedAt = :timestamp
            ''',
            ExpressionAttributeValues={
                ':capabilities': capabilities.to_dict(),
                ':s3_key': s3_key,
                ':timestamp': capabilities.last_updated
            }
        )
        
        return True, ""
        
    except ClientError as e:
        return False, f"DynamoDB error: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


def transform_and_store_data(user_id: str, raw_records: List[Dict[str, Any]],
                             quality_score: float, source: str = 'csv',
                             s3_bucket: str = None,
                             dynamodb_table: str = None) -> Dict[str, Any]:
    """
    Transform validated data and store in S3 and DynamoDB
    
    Args:
        user_id: User identifier
        raw_records: List of raw sales records
        quality_score: Data quality score from validation
        source: Data source type
        s3_bucket: S3 bucket name (optional)
        dynamodb_table: DynamoDB table name (optional)
    
    Returns:
        Dictionary with transformation results
    """
    # Default values
    if not s3_bucket:
        s3_bucket = 'vyapar-saathi-processed-data'
    if not dynamodb_table:
        dynamodb_table = 'vyapar-saathi-user-profiles'
    
    result = {
        'success': False,
        'recordsProcessed': 0,
        's3Key': None,
        'capabilities': None,
        'errors': []
    }
    
    try:
        # Transform records
        standardized_records = transform_sales_records(user_id, raw_records, source)
        result['recordsProcessed'] = len(standardized_records)
        
        if not standardized_records:
            result['errors'].append("No records to process")
            return result
        
        # Store to S3
        s3_success, s3_result = store_processed_data_to_s3(
            user_id, 
            standardized_records, 
            s3_bucket
        )
        
        if not s3_success:
            result['errors'].append(s3_result)
            return result
        
        result['s3Key'] = s3_result
        
        # Calculate capabilities
        capabilities = calculate_data_capabilities(standardized_records, quality_score)
        result['capabilities'] = capabilities.to_dict()
        
        # Update user profile
        db_success, db_error = update_user_profile_capabilities(
            user_id,
            capabilities,
            s3_result,
            dynamodb_table
        )
        
        if not db_success:
            result['errors'].append(db_error)
            return result
        
        result['success'] = True
        
    except Exception as e:
        result['errors'].append(f"Transformation error: {str(e)}")
    
    return result


@lambda_handler_wrapper
def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for data transformation and storage
    
    Args:
        event: Lambda event containing user_id, records, and quality_score
        context: Lambda context
    
    Returns:
        API Gateway response with transformation results
    """
    try:
        # Extract parameters
        body = json.loads(event.get('body', '{}'))
        user_id = body.get('userId')
        raw_records = body.get('records', [])
        quality_score = body.get('qualityScore', 0.5)
        source = body.get('source', 'csv')
        
        if not user_id:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'success': False,
                    'error': 'Missing required parameter: userId'
                })
            }
        
        if not raw_records:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'success': False,
                    'error': 'Missing required parameter: records'
                })
            }
        
        # Get configuration from event
        s3_bucket = event.get('s3Bucket')
        dynamodb_table = event.get('dynamodbTable')
        
        # Transform and store data
        result = transform_and_store_data(
            user_id,
            raw_records,
            quality_score,
            source,
            s3_bucket,
            dynamodb_table
        )
        
        return {
            'statusCode': 200 if result['success'] else 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(result)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': False,
                'error': f'Internal server error: {str(e)}'
            })
        }
