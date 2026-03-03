"""
Low-data mode questionnaire handler for VyaparSaathi
Processes user estimates and questionnaire responses
"""

import json
from typing import Dict, List, Any, Tuple
from datetime import datetime
import boto3
from botocore.exceptions import ClientError


class InventoryEstimate:
    """Inventory estimate for low-data mode"""
    
    def __init__(self, category: str, current_stock: float, 
                 average_daily_sales: float, confidence: str):
        self.category = category
        self.current_stock = current_stock
        self.average_daily_sales = average_daily_sales
        self.confidence = confidence
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'category': self.category,
            'currentStock': self.current_stock,
            'averageDailySales': self.average_daily_sales,
            'confidence': self.confidence
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'InventoryEstimate':
        """Create from dictionary"""
        return InventoryEstimate(
            category=data.get('category', ''),
            current_stock=data.get('currentStock', 0),
            average_daily_sales=data.get('averageDailySales', 0),
            confidence=data.get('confidence', 'low')
        )


class QuestionnaireResponse:
    """Low-data mode questionnaire response"""
    
    def __init__(self, user_id: str, business_type: str, store_size: str,
                 last_festival_performance: Dict[str, Any],
                 current_inventory: List[InventoryEstimate],
                 target_festivals: List[str]):
        self.user_id = user_id
        self.business_type = business_type
        self.store_size = store_size
        self.last_festival_performance = last_festival_performance
        self.current_inventory = current_inventory
        self.target_festivals = target_festivals
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'userId': self.user_id,
            'businessType': self.business_type,
            'storeSize': self.store_size,
            'lastFestivalPerformance': self.last_festival_performance,
            'currentInventory': [inv.to_dict() for inv in self.current_inventory],
            'targetFestivals': self.target_festivals
        }


class QuestionnaireValidationResult:
    """Result of questionnaire validation"""
    
    def __init__(self):
        self.success = False
        self.error_messages: List[str] = []
        self.warnings: List[str] = []
        self.confidence_score = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'success': self.success,
            'errorMessages': self.error_messages,
            'warnings': self.warnings,
            'confidenceScore': self.confidence_score
        }


def validate_business_type(business_type: str) -> Tuple[bool, str]:
    """Validate business type"""
    valid_types = ['grocery', 'apparel', 'electronics', 'general']
    if business_type not in valid_types:
        return False, f"Invalid business type: {business_type}. Must be one of: {', '.join(valid_types)}"
    return True, ""


def validate_store_size(store_size: str) -> Tuple[bool, str]:
    """Validate store size"""
    valid_sizes = ['small', 'medium', 'large']
    if store_size not in valid_sizes:
        return False, f"Invalid store size: {store_size}. Must be one of: {', '.join(valid_sizes)}"
    return True, ""


def validate_confidence_level(confidence: str) -> Tuple[bool, str]:
    """Validate confidence level"""
    valid_levels = ['low', 'medium', 'high']
    if confidence not in valid_levels:
        return False, f"Invalid confidence level: {confidence}. Must be one of: {', '.join(valid_levels)}"
    return True, ""


def validate_last_festival_performance(performance: Dict[str, Any]) -> List[str]:
    """Validate last festival performance data"""
    errors = []
    
    if not performance:
        errors.append("Last festival performance data is required")
        return errors
    
    # Validate festival name
    festival = performance.get('festival', '').strip()
    if not festival:
        errors.append("Festival name is required in last festival performance")
    
    # Validate sales increase
    sales_increase = performance.get('salesIncrease')
    if sales_increase is None:
        errors.append("Sales increase percentage is required")
    else:
        try:
            sales_increase = float(sales_increase)
            if sales_increase < -100:
                errors.append("Sales increase cannot be less than -100%")
        except (ValueError, TypeError):
            errors.append(f"Invalid sales increase value: {sales_increase}")
    
    # Validate top categories
    top_categories = performance.get('topCategories', [])
    if not isinstance(top_categories, list):
        errors.append("Top categories must be a list")
    elif len(top_categories) == 0:
        errors.append("At least one top category is required")
    
    # Validate stockout items
    stockout_items = performance.get('stockoutItems', [])
    if not isinstance(stockout_items, list):
        errors.append("Stockout items must be a list")
    
    return errors


def validate_inventory_estimate(estimate: Dict[str, Any], index: int) -> List[str]:
    """Validate a single inventory estimate"""
    errors = []
    
    # Validate category
    category = estimate.get('category', '').strip()
    if not category:
        errors.append(f"Inventory estimate {index}: Category is required")
    
    # Validate current stock
    current_stock = estimate.get('currentStock')
    if current_stock is None:
        errors.append(f"Inventory estimate {index}: Current stock is required")
    else:
        try:
            current_stock = float(current_stock)
            if current_stock < 0:
                errors.append(f"Inventory estimate {index}: Current stock cannot be negative")
        except (ValueError, TypeError):
            errors.append(f"Inventory estimate {index}: Invalid current stock value")
    
    # Validate average daily sales
    avg_daily_sales = estimate.get('averageDailySales')
    if avg_daily_sales is None:
        errors.append(f"Inventory estimate {index}: Average daily sales is required")
    else:
        try:
            avg_daily_sales = float(avg_daily_sales)
            if avg_daily_sales < 0:
                errors.append(f"Inventory estimate {index}: Average daily sales cannot be negative")
        except (ValueError, TypeError):
            errors.append(f"Inventory estimate {index}: Invalid average daily sales value")
    
    # Validate confidence
    confidence = estimate.get('confidence', '').lower()
    is_valid, error = validate_confidence_level(confidence)
    if not is_valid:
        errors.append(f"Inventory estimate {index}: {error}")
    
    return errors


def calculate_confidence_score(response: QuestionnaireResponse) -> float:
    """
    Calculate overall confidence score based on questionnaire data
    Returns score between 0 and 1
    """
    score = 0.0
    
    # Base score from having data
    score += 0.2
    
    # Score from last festival performance
    if response.last_festival_performance:
        score += 0.2
        
        # Bonus for having stockout data
        stockout_items = response.last_festival_performance.get('stockoutItems', [])
        if len(stockout_items) > 0:
            score += 0.1
    
    # Score from inventory estimates
    if response.current_inventory:
        score += 0.2
        
        # Bonus based on confidence levels
        high_confidence = sum(1 for inv in response.current_inventory if inv.confidence == 'high')
        medium_confidence = sum(1 for inv in response.current_inventory if inv.confidence == 'medium')
        
        confidence_bonus = (high_confidence * 0.1 + medium_confidence * 0.05) / len(response.current_inventory)
        score += min(0.2, confidence_bonus)
    
    # Score from target festivals
    if response.target_festivals and len(response.target_festivals) > 0:
        score += 0.1
    
    return min(1.0, score)


def validate_questionnaire(data: Dict[str, Any]) -> Tuple[QuestionnaireValidationResult, QuestionnaireResponse]:
    """
    Validate questionnaire response data
    
    Args:
        data: Questionnaire data dictionary
    
    Returns:
        Tuple of (ValidationResult, QuestionnaireResponse or None)
    """
    result = QuestionnaireValidationResult()
    
    # Validate user_id
    user_id = data.get('userId', '').strip()
    if not user_id:
        result.error_messages.append("User ID is required")
        return result, None
    
    # Validate business type
    business_type = data.get('businessType', '').lower()
    is_valid, error = validate_business_type(business_type)
    if not is_valid:
        result.error_messages.append(error)
    
    # Validate store size
    store_size = data.get('storeSize', '').lower()
    is_valid, error = validate_store_size(store_size)
    if not is_valid:
        result.error_messages.append(error)
    
    # Validate last festival performance
    last_festival_performance = data.get('lastFestivalPerformance', {})
    perf_errors = validate_last_festival_performance(last_festival_performance)
    result.error_messages.extend(perf_errors)
    
    # Validate current inventory
    current_inventory_data = data.get('currentInventory', [])
    if not isinstance(current_inventory_data, list):
        result.error_messages.append("Current inventory must be a list")
        current_inventory_data = []
    
    if len(current_inventory_data) == 0:
        result.error_messages.append("At least one inventory estimate is required")
    
    current_inventory = []
    for i, inv_data in enumerate(current_inventory_data):
        inv_errors = validate_inventory_estimate(inv_data, i + 1)
        result.error_messages.extend(inv_errors)
        
        if not inv_errors:
            current_inventory.append(InventoryEstimate.from_dict(inv_data))
    
    # Validate target festivals
    target_festivals = data.get('targetFestivals', [])
    if not isinstance(target_festivals, list):
        result.error_messages.append("Target festivals must be a list")
        target_festivals = []
    
    if len(target_festivals) == 0:
        result.warnings.append("No target festivals specified")
    
    # If validation failed, return
    if result.error_messages:
        result.success = False
        return result, None
    
    # Create questionnaire response
    response = QuestionnaireResponse(
        user_id=user_id,
        business_type=business_type,
        store_size=store_size,
        last_festival_performance=last_festival_performance,
        current_inventory=current_inventory,
        target_festivals=target_festivals
    )
    
    # Calculate confidence score
    result.confidence_score = calculate_confidence_score(response)
    result.success = True
    
    return result, response


def store_user_estimates_to_dynamodb(response: QuestionnaireResponse, 
                                    table_name: str) -> Tuple[bool, str]:
    """
    Store user estimates in DynamoDB UserProfile table
    
    Args:
        response: Validated questionnaire response
        table_name: DynamoDB table name
    
    Returns:
        Tuple of (success, error_message)
    """
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(table_name)
        
        # Prepare item for DynamoDB
        timestamp = datetime.utcnow().isoformat()
        
        item = {
            'userId': response.user_id,
            'businessInfo': {
                'type': response.business_type,
                'size': response.store_size,
            },
            'dataCapabilities': {
                'hasHistoricalData': False,
                'dataQuality': 'fair',  # Based on questionnaire
                'lastUpdated': timestamp,
            },
            'lowDataModeData': {
                'lastFestivalPerformance': response.last_festival_performance,
                'currentInventory': [inv.to_dict() for inv in response.current_inventory],
                'targetFestivals': response.target_festivals,
                'submittedAt': timestamp,
            },
            'updatedAt': timestamp,
        }
        
        # Update or create user profile
        table.put_item(Item=item)
        
        return True, ""
        
    except ClientError as e:
        return False, f"DynamoDB error: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


def process_questionnaire(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for questionnaire processing
    
    Args:
        event: Lambda event containing questionnaire data
        context: Lambda context
    
    Returns:
        API Gateway response with validation results
    """
    try:
        # Extract parameters from event
        body = json.loads(event.get('body', '{}'))
        table_name = event.get('tableName', 'vyapar-saathi-user-profiles')
        
        # Validate questionnaire
        validation_result, questionnaire_response = validate_questionnaire(body)
        
        # Store to DynamoDB if validation successful
        if validation_result.success:
            success, error = store_user_estimates_to_dynamodb(
                questionnaire_response, 
                table_name
            )
            if not success:
                validation_result.warnings.append(f"Failed to store data: {error}")
        
        # Prepare response
        response_body = {
            'success': validation_result.success,
            'validation': validation_result.to_dict(),
        }
        
        if questionnaire_response:
            response_body['data'] = questionnaire_response.to_dict()
        
        return {
            'statusCode': 200 if validation_result.success else 400,
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
