"""
CSV upload and validation handler for VyaparSaathi
Implements Lambda function for CSV parsing with validation
"""

import csv
import io
import json
from datetime import datetime
from typing import Dict, List, Any, Tuple
import boto3
from botocore.exceptions import ClientError


class ValidationResult:
    """Result of data validation process"""
    
    def __init__(self):
        self.success = False
        self.parsed_records = 0
        self.error_records = 0
        self.error_messages: List[str] = []
        self.warnings: List[str] = []
        self.quality_score = 0.0
        self.missing_fields: List[str] = []
        self.format_issues: List[str] = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'success': self.success,
            'parsedRecords': self.parsed_records,
            'errorRecords': self.error_records,
            'errorMessages': self.error_messages,
            'warnings': self.warnings,
            'qualityScore': self.quality_score,
            'missingFields': self.missing_fields,
            'formatIssues': self.format_issues,
        }


class SalesRecord:
    """Individual sales record from historical data"""
    
    def __init__(self, date: str, sku: str, quantity: float, 
                 category: str = None, price: float = None):
        self.date = date
        self.sku = sku
        self.quantity = quantity
        self.category = category
        self.price = price
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {
            'date': self.date,
            'sku': self.sku,
            'quantity': self.quantity,
        }
        if self.category:
            result['category'] = self.category
        if self.price is not None:
            result['price'] = self.price
        return result


def validate_date(date_str: str) -> Tuple[bool, str]:
    """
    Validate date format (ISO format YYYY-MM-DD)
    Returns (is_valid, error_message)
    """
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True, ""
    except ValueError:
        return False, f"Invalid date format: {date_str}. Expected YYYY-MM-DD"


def validate_quantity(quantity_str: str) -> Tuple[bool, float, str]:
    """
    Validate quantity is a positive number
    Returns (is_valid, parsed_value, error_message)
    """
    try:
        quantity = float(quantity_str)
        if quantity < 0:
            return False, 0, f"Quantity must be non-negative: {quantity_str}"
        return True, quantity, ""
    except (ValueError, TypeError):
        return False, 0, f"Invalid quantity value: {quantity_str}"


def validate_price(price_str: str) -> Tuple[bool, float, str]:
    """
    Validate price is a positive number
    Returns (is_valid, parsed_value, error_message)
    """
    if not price_str or price_str.strip() == '':
        return True, None, ""  # Price is optional
    
    try:
        price = float(price_str)
        if price < 0:
            return False, 0, f"Price must be non-negative: {price_str}"
        return True, price, ""
    except (ValueError, TypeError):
        return False, 0, f"Invalid price value: {price_str}"


def detect_duplicates(records: List[SalesRecord]) -> List[str]:
    """
    Detect duplicate records (same date and SKU)
    Returns list of warning messages
    """
    seen = set()
    duplicates = []
    
    for record in records:
        key = (record.date, record.sku)
        if key in seen:
            duplicates.append(f"Duplicate record found: date={record.date}, sku={record.sku}")
        seen.add(key)
    
    return duplicates


def detect_outliers(records: List[SalesRecord]) -> List[str]:
    """
    Detect outliers in quantity values using simple statistical method
    Returns list of warning messages
    """
    if len(records) < 10:
        return []  # Not enough data for outlier detection
    
    quantities = [r.quantity for r in records]
    mean = sum(quantities) / len(quantities)
    variance = sum((q - mean) ** 2 for q in quantities) / len(quantities)
    std_dev = variance ** 0.5
    
    outliers = []
    threshold = 3  # 3 standard deviations
    
    for record in records:
        if abs(record.quantity - mean) > threshold * std_dev:
            outliers.append(
                f"Potential outlier detected: date={record.date}, sku={record.sku}, "
                f"quantity={record.quantity} (mean={mean:.2f}, std={std_dev:.2f})"
            )
    
    return outliers


def calculate_quality_score(validation_result: ValidationResult, 
                           total_records: int) -> float:
    """
    Calculate data quality score (0-1) based on validation results
    """
    if total_records == 0:
        return 0.0
    
    # Base score from successful parsing
    parse_score = validation_result.parsed_records / total_records
    
    # Penalty for errors
    error_penalty = validation_result.error_records / total_records * 0.5
    
    # Penalty for warnings (less severe)
    warning_penalty = len(validation_result.warnings) / total_records * 0.2
    
    # Penalty for missing optional fields
    missing_penalty = len(validation_result.missing_fields) * 0.05
    
    quality_score = max(0.0, parse_score - error_penalty - warning_penalty - missing_penalty)
    
    return min(1.0, quality_score)


def validate_sales_data(csv_content: str) -> Tuple[ValidationResult, List[SalesRecord]]:
    """
    Validate CSV sales data
    
    Args:
        csv_content: CSV file content as string
    
    Returns:
        Tuple of (ValidationResult, List of valid SalesRecords)
    """
    result = ValidationResult()
    valid_records: List[SalesRecord] = []
    
    try:
        # Parse CSV
        csv_file = io.StringIO(csv_content)
        reader = csv.DictReader(csv_file)
        
        # Check for required fields
        if reader.fieldnames is None:
            result.error_messages.append("CSV file is empty or has no header row")
            return result, valid_records
        
        required_fields = {'date', 'sku', 'quantity'}
        header_fields = set(field.lower().strip() for field in reader.fieldnames)
        
        missing = required_fields - header_fields
        if missing:
            result.missing_fields = list(missing)
            result.error_messages.append(
                f"Missing required fields: {', '.join(missing)}. "
                f"Required fields are: date, sku, quantity"
            )
            return result, valid_records
        
        # Track optional fields
        has_category = 'category' in header_fields
        has_price = 'price' in header_fields
        
        if not has_category:
            result.warnings.append("Optional field 'category' not found")
        if not has_price:
            result.warnings.append("Optional field 'price' not found")
        
        # Validate each row
        row_num = 1
        for row in reader:
            row_num += 1
            row_errors = []
            
            # Normalize field names (case-insensitive)
            normalized_row = {k.lower().strip(): v.strip() for k, v in row.items()}
            
            # Validate date
            date_str = normalized_row.get('date', '')
            date_valid, date_error = validate_date(date_str)
            if not date_valid:
                row_errors.append(f"Row {row_num}: {date_error}")
            
            # Validate SKU
            sku = normalized_row.get('sku', '').strip()
            if not sku:
                row_errors.append(f"Row {row_num}: SKU cannot be empty")
            
            # Validate quantity
            quantity_str = normalized_row.get('quantity', '')
            quantity_valid, quantity, quantity_error = validate_quantity(quantity_str)
            if not quantity_valid:
                row_errors.append(f"Row {row_num}: {quantity_error}")
            
            # Validate price (optional)
            price_str = normalized_row.get('price', '')
            price_valid, price, price_error = validate_price(price_str)
            if not price_valid:
                row_errors.append(f"Row {row_num}: {price_error}")
            
            # If row has errors, record them and skip
            if row_errors:
                result.error_records += 1
                result.error_messages.extend(row_errors)
                continue
            
            # Create valid record
            category = normalized_row.get('category', '').strip() or None
            record = SalesRecord(
                date=date_str,
                sku=sku,
                quantity=quantity,
                category=category,
                price=price
            )
            valid_records.append(record)
            result.parsed_records += 1
        
        # Data quality checks
        if valid_records:
            # Duplicate detection
            duplicate_warnings = detect_duplicates(valid_records)
            result.warnings.extend(duplicate_warnings)
            
            # Outlier detection
            outlier_warnings = detect_outliers(valid_records)
            result.warnings.extend(outlier_warnings)
        
        # Calculate quality score
        total_records = result.parsed_records + result.error_records
        result.quality_score = calculate_quality_score(result, total_records)
        
        # Determine success
        result.success = result.parsed_records > 0 and result.error_records == 0
        
        if result.parsed_records == 0:
            result.error_messages.append("No valid records found in CSV file")
        
    except Exception as e:
        result.error_messages.append(f"Error parsing CSV: {str(e)}")
        result.format_issues.append(f"CSV parsing failed: {str(e)}")
    
    return result, valid_records


def store_raw_file_to_s3(user_id: str, file_content: str, 
                         bucket_name: str) -> Tuple[bool, str]:
    """
    Store raw CSV file to S3
    
    Args:
        user_id: User identifier
        file_content: CSV file content
        bucket_name: S3 bucket name
    
    Returns:
        Tuple of (success, s3_key or error_message)
    """
    try:
        s3_client = boto3.client('s3')
        
        # Generate S3 key with timestamp
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        s3_key = f"raw-data/{user_id}/{timestamp}_sales_data.csv"
        
        # Upload to S3
        s3_client.put_object(
            Bucket=bucket_name,
            Key=s3_key,
            Body=file_content.encode('utf-8'),
            ContentType='text/csv',
            ServerSideEncryption='AES256'
        )
        
        return True, s3_key
        
    except ClientError as e:
        return False, f"S3 upload failed: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error during S3 upload: {str(e)}"


def process_csv_upload(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for CSV upload and validation
    
    Args:
        event: Lambda event containing CSV file content and user_id
        context: Lambda context
    
    Returns:
        API Gateway response with validation results
    """
    try:
        # Extract parameters from event
        body = json.loads(event.get('body', '{}'))
        user_id = body.get('userId')
        csv_content = body.get('csvContent')
        bucket_name = event.get('bucketName', 'vyapar-saathi-raw-data')
        
        if not user_id:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'success': False,
                    'error': 'Missing required parameter: userId'
                })
            }
        
        if not csv_content:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'success': False,
                    'error': 'Missing required parameter: csvContent'
                })
            }
        
        # Validate CSV data
        validation_result, valid_records = validate_sales_data(csv_content)
        
        # Store raw file to S3 if validation successful
        s3_key = None
        if validation_result.success:
            success, result = store_raw_file_to_s3(user_id, csv_content, bucket_name)
            if success:
                s3_key = result
            else:
                validation_result.warnings.append(f"Failed to store raw file: {result}")
        
        # Prepare response
        response_body = {
            'success': validation_result.success,
            'validation': validation_result.to_dict(),
            'recordCount': len(valid_records),
            's3Key': s3_key
        }
        
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
