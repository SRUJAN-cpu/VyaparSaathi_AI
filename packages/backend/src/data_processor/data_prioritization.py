"""
Data source prioritization logic for VyaparSaathi
Evaluates data quality and selects best data source for forecasting
"""

import json
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta
import boto3
from botocore.exceptions import ClientError


class DataSource:
    """Represents a data source with quality metrics"""
    
    def __init__(self, source_type: str, quality_score: float, 
                 completeness: float, recency_days: int, consistency: float):
        self.source_type = source_type  # 'structured' or 'manual'
        self.quality_score = quality_score
        self.completeness = completeness
        self.recency_days = recency_days
        self.consistency = consistency
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'sourceType': self.source_type,
            'qualityScore': self.quality_score,
            'completeness': self.completeness,
            'recencyDays': self.recency_days,
            'consistency': self.consistency
        }


class DataSourceMetadata:
    """Metadata about available data sources"""
    
    def __init__(self, user_id: str, selected_source: str, 
                 structured_data: DataSource = None,
                 manual_estimates: DataSource = None,
                 selection_reason: str = ""):
        self.user_id = user_id
        self.selected_source = selected_source
        self.structured_data = structured_data
        self.manual_estimates = manual_estimates
        self.selection_reason = selection_reason
        self.evaluated_at = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {
            'userId': self.user_id,
            'selectedSource': self.selected_source,
            'selectionReason': self.selection_reason,
            'evaluatedAt': self.evaluated_at
        }
        
        if self.structured_data:
            result['structuredData'] = self.structured_data.to_dict()
        
        if self.manual_estimates:
            result['manualEstimates'] = self.manual_estimates.to_dict()
        
        return result


def calculate_completeness_score(record_count: int, expected_count: int) -> float:
    """
    Calculate completeness score based on record count
    
    Args:
        record_count: Actual number of records
        expected_count: Expected number of records (e.g., days * SKUs)
    
    Returns:
        Completeness score (0-1)
    """
    if expected_count == 0:
        return 0.0
    
    return min(1.0, record_count / expected_count)


def calculate_recency_score(last_update_date: str) -> Tuple[float, int]:
    """
    Calculate recency score based on how recent the data is
    
    Args:
        last_update_date: ISO format date string
    
    Returns:
        Tuple of (recency_score, days_old)
    """
    try:
        last_update = datetime.fromisoformat(last_update_date.replace('Z', '+00:00'))
        now = datetime.utcnow()
        days_old = (now - last_update).days
        
        # Score decreases as data gets older
        if days_old <= 7:
            score = 1.0
        elif days_old <= 30:
            score = 0.8
        elif days_old <= 90:
            score = 0.6
        elif days_old <= 180:
            score = 0.4
        else:
            score = 0.2
        
        return score, days_old
        
    except (ValueError, AttributeError):
        return 0.0, 999


def calculate_consistency_score(data_points: List[float]) -> float:
    """
    Calculate consistency score based on variance in data
    Lower variance = higher consistency
    
    Args:
        data_points: List of numeric values
    
    Returns:
        Consistency score (0-1)
    """
    if len(data_points) < 2:
        return 0.5  # Neutral score for insufficient data
    
    # Calculate coefficient of variation (CV)
    mean = sum(data_points) / len(data_points)
    if mean == 0:
        return 0.5
    
    variance = sum((x - mean) ** 2 for x in data_points) / len(data_points)
    std_dev = variance ** 0.5
    cv = std_dev / mean
    
    # Convert CV to consistency score (lower CV = higher consistency)
    # CV > 1.0 is considered highly variable
    if cv <= 0.2:
        score = 1.0
    elif cv <= 0.5:
        score = 0.8
    elif cv <= 1.0:
        score = 0.6
    elif cv <= 2.0:
        score = 0.4
    else:
        score = 0.2
    
    return score


def evaluate_structured_data_quality(user_id: str, s3_bucket: str, 
                                     dynamodb_table: str) -> DataSource:
    """
    Evaluate quality of structured historical data
    
    Args:
        user_id: User identifier
        s3_bucket: S3 bucket containing processed data
        dynamodb_table: DynamoDB table with user profile
    
    Returns:
        DataSource object with quality metrics
    """
    try:
        # Get user profile from DynamoDB
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(dynamodb_table)
        
        response = table.get_item(Key={'userId': user_id})
        
        if 'Item' not in response:
            return DataSource('structured', 0.0, 0.0, 999, 0.0)
        
        user_profile = response['Item']
        data_capabilities = user_profile.get('dataCapabilities', {})
        
        # Check if user has historical data
        has_historical = data_capabilities.get('hasHistoricalData', False)
        if not has_historical:
            return DataSource('structured', 0.0, 0.0, 999, 0.0)
        
        # Get quality metrics
        base_quality = data_capabilities.get('qualityScore', 0.5)
        completeness = data_capabilities.get('completenessScore', 0.5)
        
        # Calculate recency
        last_updated = data_capabilities.get('lastUpdated', '')
        recency_score, days_old = calculate_recency_score(last_updated)
        
        # Get consistency (if available)
        consistency = data_capabilities.get('consistencyScore', 0.5)
        
        # Calculate overall quality score
        quality_score = (
            base_quality * 0.4 +
            completeness * 0.3 +
            recency_score * 0.2 +
            consistency * 0.1
        )
        
        return DataSource(
            source_type='structured',
            quality_score=quality_score,
            completeness=completeness,
            recency_days=days_old,
            consistency=consistency
        )
        
    except Exception as e:
        print(f"Error evaluating structured data: {str(e)}")
        return DataSource('structured', 0.0, 0.0, 999, 0.0)


def evaluate_manual_estimates_quality(user_id: str, 
                                      dynamodb_table: str) -> DataSource:
    """
    Evaluate quality of manual estimates from questionnaire
    
    Args:
        user_id: User identifier
        dynamodb_table: DynamoDB table with user profile
    
    Returns:
        DataSource object with quality metrics
    """
    try:
        # Get user profile from DynamoDB
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(dynamodb_table)
        
        response = table.get_item(Key={'userId': user_id})
        
        if 'Item' not in response:
            return DataSource('manual', 0.0, 0.0, 999, 0.0)
        
        user_profile = response['Item']
        low_data_mode = user_profile.get('lowDataModeData', {})
        
        if not low_data_mode:
            return DataSource('manual', 0.0, 0.0, 999, 0.0)
        
        # Calculate completeness based on inventory estimates
        inventory = low_data_mode.get('currentInventory', [])
        completeness = min(1.0, len(inventory) / 5.0)  # Expect ~5 categories
        
        # Calculate confidence score from estimates
        confidence_scores = {
            'high': 1.0,
            'medium': 0.6,
            'low': 0.3
        }
        
        avg_confidence = 0.5
        if inventory:
            confidence_values = [
                confidence_scores.get(inv.get('confidence', 'low'), 0.3)
                for inv in inventory
            ]
            avg_confidence = sum(confidence_values) / len(confidence_values)
        
        # Calculate recency
        submitted_at = low_data_mode.get('submittedAt', '')
        recency_score, days_old = calculate_recency_score(submitted_at)
        
        # Manual estimates have lower consistency (more subjective)
        consistency = 0.5
        
        # Calculate overall quality score
        # Manual estimates generally score lower than structured data
        quality_score = (
            avg_confidence * 0.4 +
            completeness * 0.3 +
            recency_score * 0.2 +
            consistency * 0.1
        ) * 0.7  # Apply penalty factor for manual estimates
        
        return DataSource(
            source_type='manual',
            quality_score=quality_score,
            completeness=completeness,
            recency_days=days_old,
            consistency=consistency
        )
        
    except Exception as e:
        print(f"Error evaluating manual estimates: {str(e)}")
        return DataSource('manual', 0.0, 0.0, 999, 0.0)


def select_data_source(structured: DataSource, 
                       manual: DataSource) -> Tuple[str, str]:
    """
    Select the best data source based on quality metrics
    
    Args:
        structured: Structured data source
        manual: Manual estimates data source
    
    Returns:
        Tuple of (selected_source_type, selection_reason)
    """
    # If only one source is available, use it
    if structured.quality_score == 0.0 and manual.quality_score > 0.0:
        return 'manual', 'Only manual estimates available'
    
    if manual.quality_score == 0.0 and structured.quality_score > 0.0:
        return 'structured', 'Only structured data available'
    
    if structured.quality_score == 0.0 and manual.quality_score == 0.0:
        return 'none', 'No data sources available'
    
    # Both sources available - prioritize structured data
    # Structured data is preferred unless quality is significantly lower
    quality_threshold = 0.3  # Structured must be at least 0.3 lower to choose manual
    
    if structured.quality_score >= manual.quality_score - quality_threshold:
        reasons = []
        if structured.quality_score > manual.quality_score:
            reasons.append(f"Higher quality score ({structured.quality_score:.2f} vs {manual.quality_score:.2f})")
        if structured.completeness > manual.completeness:
            reasons.append(f"Better completeness ({structured.completeness:.2f} vs {manual.completeness:.2f})")
        if structured.recency_days < manual.recency_days:
            reasons.append(f"More recent data ({structured.recency_days} vs {manual.recency_days} days old)")
        
        if not reasons:
            reasons.append("Structured data preferred by default")
        
        return 'structured', '; '.join(reasons)
    else:
        return 'manual', f"Manual estimates have significantly higher quality ({manual.quality_score:.2f} vs {structured.quality_score:.2f})"


def store_data_source_metadata(metadata: DataSourceMetadata, 
                               dynamodb_table: str) -> Tuple[bool, str]:
    """
    Store data source metadata in DynamoDB
    
    Args:
        metadata: Data source metadata
        dynamodb_table: DynamoDB table name
    
    Returns:
        Tuple of (success, error_message)
    """
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(dynamodb_table)
        
        # Update user profile with data source metadata
        table.update_item(
            Key={'userId': metadata.user_id},
            UpdateExpression='SET dataSourceMetadata = :metadata, updatedAt = :timestamp',
            ExpressionAttributeValues={
                ':metadata': metadata.to_dict(),
                ':timestamp': metadata.evaluated_at
            }
        )
        
        return True, ""
        
    except ClientError as e:
        return False, f"DynamoDB error: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


def prioritize_data_source(user_id: str, s3_bucket: str = None, 
                          dynamodb_table: str = None) -> DataSourceMetadata:
    """
    Evaluate and prioritize data sources for a user
    
    Args:
        user_id: User identifier
        s3_bucket: S3 bucket name (optional)
        dynamodb_table: DynamoDB table name (optional)
    
    Returns:
        DataSourceMetadata with selected source and quality metrics
    """
    # Default values
    if not s3_bucket:
        s3_bucket = 'vyapar-saathi-processed-data'
    if not dynamodb_table:
        dynamodb_table = 'vyapar-saathi-user-profiles'
    
    # Evaluate both data sources
    structured = evaluate_structured_data_quality(user_id, s3_bucket, dynamodb_table)
    manual = evaluate_manual_estimates_quality(user_id, dynamodb_table)
    
    # Select best source
    selected_source, reason = select_data_source(structured, manual)
    
    # Create metadata
    metadata = DataSourceMetadata(
        user_id=user_id,
        selected_source=selected_source,
        structured_data=structured if structured.quality_score > 0 else None,
        manual_estimates=manual if manual.quality_score > 0 else None,
        selection_reason=reason
    )
    
    # Store metadata
    store_data_source_metadata(metadata, dynamodb_table)
    
    return metadata


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for data source prioritization
    
    Args:
        event: Lambda event containing user_id
        context: Lambda context
    
    Returns:
        API Gateway response with data source selection
    """
    try:
        # Extract parameters
        body = json.loads(event.get('body', '{}'))
        user_id = body.get('userId')
        
        if not user_id:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'success': False,
                    'error': 'Missing required parameter: userId'
                })
            }
        
        # Get configuration from event
        s3_bucket = event.get('s3Bucket')
        dynamodb_table = event.get('dynamodbTable')
        
        # Prioritize data source
        metadata = prioritize_data_source(user_id, s3_bucket, dynamodb_table)
        
        # Prepare response
        response_body = {
            'success': True,
            'dataSourceMetadata': metadata.to_dict()
        }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(response_body)
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
