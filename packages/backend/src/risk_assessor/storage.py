"""
DynamoDB storage and retrieval for risk assessments.

This module handles storing risk assessment results, indexing for efficient
retrieval by userId and urgency, and notification triggers for high-urgency alerts.
"""

import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from decimal import Decimal

import boto3
from botocore.exceptions import ClientError


# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
sns_client = boto3.client('sns')

# Environment variables
RISK_ASSESSMENTS_TABLE = os.environ.get('RISK_ASSESSMENTS_TABLE', 'VyaparSaathi-RiskAssessments')
ALERT_TOPIC_ARN = os.environ.get('ALERT_TOPIC_ARN', '')


def convert_floats_to_decimal(obj: Any) -> Any:
    """
    Convert float values to Decimal for DynamoDB storage.
    
    Args:
        obj: Object to convert (dict, list, or primitive)
        
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


def convert_decimal_to_float(obj: Any) -> Any:
    """
    Convert Decimal values to float for JSON serialization.
    
    Args:
        obj: Object to convert (dict, list, or primitive)
        
    Returns:
        Object with Decimals converted to float
    """
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: convert_decimal_to_float(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimal_to_float(item) for item in obj]
    else:
        return obj


def store_risk_assessment(
    user_id: str,
    risk_assessment: Dict[str, Any],
    recommendation: Dict[str, Any],
    alert: Optional[Dict[str, Any]] = None,
    ttl_days: int = 90
) -> Dict[str, Any]:
    """
    Store risk assessment result in DynamoDB.
    
    Args:
        user_id: User identifier
        risk_assessment: Risk assessment dictionary
        recommendation: Reorder recommendation dictionary
        alert: Optional alert dictionary
        ttl_days: Time-to-live in days (default: 90)
        
    Returns:
        Storage result with assessmentId and status
    """
    table = dynamodb.Table(RISK_ASSESSMENTS_TABLE)
    
    # Generate unique assessment ID
    assessment_id = str(uuid.uuid4())
    
    # Calculate TTL (Unix timestamp)
    ttl_timestamp = int((datetime.utcnow() + timedelta(days=ttl_days)).timestamp())
    
    # Prepare item for storage
    item = {
        'assessmentId': assessment_id,
        'userId': user_id,
        'sku': risk_assessment.get('sku'),
        'category': risk_assessment.get('category'),
        'currentStock': risk_assessment.get('currentStock'),
        'stockoutRisk': convert_floats_to_decimal(risk_assessment.get('stockoutRisk')),
        'overstockRisk': convert_floats_to_decimal(risk_assessment.get('overstockRisk')),
        'recommendation': convert_floats_to_decimal(recommendation),
        'assessmentDate': risk_assessment.get('assessmentDate', datetime.utcnow().isoformat()),
        'urgency': recommendation.get('urgency'),
        'action': recommendation.get('action'),
        'ttl': ttl_timestamp,
        'createdAt': datetime.utcnow().isoformat()
    }
    
    # Add alert if present
    if alert:
        item['alert'] = convert_floats_to_decimal(alert)
        item['alertSeverity'] = alert.get('severity')
    
    # Add parameters
    if 'parameters' in risk_assessment:
        item['parameters'] = convert_floats_to_decimal(risk_assessment.get('parameters'))
    
    try:
        # Store in DynamoDB
        table.put_item(Item=item)
        
        # Trigger notification for high-urgency alerts
        if recommendation.get('urgency') == 'high' and ALERT_TOPIC_ARN:
            trigger_high_urgency_notification(user_id, risk_assessment, recommendation)
        
        return {
            'success': True,
            'assessmentId': assessment_id,
            'userId': user_id,
            'sku': risk_assessment.get('sku'),
            'storedAt': item['createdAt']
        }
        
    except ClientError as e:
        print(f"Error storing risk assessment: {e}")
        return {
            'success': False,
            'error': str(e),
            'assessmentId': assessment_id
        }


def get_risk_assessments_by_user(
    user_id: str,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Retrieve risk assessments for a user.
    
    Args:
        user_id: User identifier
        limit: Maximum number of results (default: 50)
        
    Returns:
        List of risk assessment dictionaries
    """
    table = dynamodb.Table(RISK_ASSESSMENTS_TABLE)
    
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
        return [convert_decimal_to_float(item) for item in items]
        
    except ClientError as e:
        print(f"Error retrieving risk assessments: {e}")
        return []


def get_risk_assessments_by_urgency(
    user_id: str,
    urgency: str,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Retrieve risk assessments by user and urgency level.
    
    Args:
        user_id: User identifier
        urgency: Urgency level ('low', 'medium', 'high')
        limit: Maximum number of results (default: 50)
        
    Returns:
        List of risk assessment dictionaries
    """
    table = dynamodb.Table(RISK_ASSESSMENTS_TABLE)
    
    try:
        response = table.query(
            IndexName='UserUrgencyIndex',
            KeyConditionExpression='userId = :userId AND urgency = :urgency',
            ExpressionAttributeValues={
                ':userId': user_id,
                ':urgency': urgency
            },
            Limit=limit,
            ScanIndexForward=False  # Most recent first
        )
        
        items = response.get('Items', [])
        return [convert_decimal_to_float(item) for item in items]
        
    except ClientError as e:
        print(f"Error retrieving risk assessments by urgency: {e}")
        return []


def get_risk_assessment_by_id(
    assessment_id: str
) -> Optional[Dict[str, Any]]:
    """
    Retrieve a specific risk assessment by ID.
    
    Args:
        assessment_id: Assessment identifier
        
    Returns:
        Risk assessment dictionary or None if not found
    """
    table = dynamodb.Table(RISK_ASSESSMENTS_TABLE)
    
    try:
        response = table.get_item(
            Key={'assessmentId': assessment_id}
        )
        
        item = response.get('Item')
        return convert_decimal_to_float(item) if item else None
        
    except ClientError as e:
        print(f"Error retrieving risk assessment: {e}")
        return None


def get_latest_risk_for_sku(
    user_id: str,
    sku: str
) -> Optional[Dict[str, Any]]:
    """
    Retrieve the latest risk assessment for a specific SKU.
    
    Args:
        user_id: User identifier
        sku: Product SKU identifier
        
    Returns:
        Latest risk assessment dictionary or None if not found
    """
    table = dynamodb.Table(RISK_ASSESSMENTS_TABLE)
    
    try:
        response = table.query(
            IndexName='UserSkuIndex',
            KeyConditionExpression='userId = :userId AND sku = :sku',
            ExpressionAttributeValues={
                ':userId': user_id,
                ':sku': sku
            },
            Limit=1,
            ScanIndexForward=False  # Most recent first
        )
        
        items = response.get('Items', [])
        if items:
            return convert_decimal_to_float(items[0])
        return None
        
    except ClientError as e:
        print(f"Error retrieving latest risk for SKU: {e}")
        return None


def delete_risk_assessment(
    assessment_id: str
) -> Dict[str, Any]:
    """
    Delete a risk assessment.
    
    Args:
        assessment_id: Assessment identifier
        
    Returns:
        Deletion result dictionary
    """
    table = dynamodb.Table(RISK_ASSESSMENTS_TABLE)
    
    try:
        table.delete_item(
            Key={'assessmentId': assessment_id}
        )
        
        return {
            'success': True,
            'assessmentId': assessment_id,
            'deletedAt': datetime.utcnow().isoformat()
        }
        
    except ClientError as e:
        print(f"Error deleting risk assessment: {e}")
        return {
            'success': False,
            'error': str(e),
            'assessmentId': assessment_id
        }


def trigger_high_urgency_notification(
    user_id: str,
    risk_assessment: Dict[str, Any],
    recommendation: Dict[str, Any]
) -> None:
    """
    Trigger SNS notification for high-urgency alerts.
    
    Args:
        user_id: User identifier
        risk_assessment: Risk assessment dictionary
        recommendation: Reorder recommendation dictionary
    """
    if not ALERT_TOPIC_ARN:
        print("Alert topic ARN not configured, skipping notification")
        return
    
    try:
        sku = risk_assessment.get('sku')
        action = recommendation.get('action')
        urgency = recommendation.get('urgency')
        
        # Build notification message
        message = {
            'userId': user_id,
            'sku': sku,
            'urgency': urgency,
            'action': action,
            'stockoutRisk': risk_assessment.get('stockoutRisk'),
            'recommendation': recommendation,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Publish to SNS
        sns_client.publish(
            TopicArn=ALERT_TOPIC_ARN,
            Subject=f'High Urgency Alert: {sku}',
            Message=str(message),
            MessageAttributes={
                'userId': {'DataType': 'String', 'StringValue': user_id},
                'urgency': {'DataType': 'String', 'StringValue': urgency},
                'sku': {'DataType': 'String', 'StringValue': sku}
            }
        )
        
        print(f"High urgency notification sent for user {user_id}, SKU {sku}")
        
    except ClientError as e:
        print(f"Error sending notification: {e}")
