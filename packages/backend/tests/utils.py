"""
Test utilities for VyaparSaathi backend tests.

This module provides helper functions for testing Lambda functions and utilities.
"""
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import json


def create_api_gateway_event(
    body: Optional[Dict[str, Any]] = None,
    path_parameters: Optional[Dict[str, str]] = None,
    query_parameters: Optional[Dict[str, str]] = None,
    headers: Optional[Dict[str, str]] = None,
    http_method: str = "POST",
    path: str = "/",
) -> Dict[str, Any]:
    """
    Create a mock API Gateway event for Lambda testing.
    
    Args:
        body: Request body as dictionary
        path_parameters: Path parameters
        query_parameters: Query string parameters
        headers: Request headers
        http_method: HTTP method (GET, POST, etc.)
        path: Request path
        
    Returns:
        API Gateway event dictionary
    """
    return {
        "httpMethod": http_method,
        "path": path,
        "pathParameters": path_parameters or {},
        "queryStringParameters": query_parameters or {},
        "headers": headers or {"Content-Type": "application/json"},
        "body": json.dumps(body) if body else None,
        "requestContext": {
            "requestId": "test-request-id",
            "authorizer": {"claims": {"sub": "test-user-123"}},
        },
        "isBase64Encoded": False,
    }


def create_lambda_context(
    function_name: str = "test-function",
    memory_limit: int = 512,
    timeout: int = 30,
) -> Any:
    """
    Create a mock Lambda context for testing.
    
    Args:
        function_name: Lambda function name
        memory_limit: Memory limit in MB
        timeout: Timeout in seconds
        
    Returns:
        Mock Lambda context object
    """
    
    class MockLambdaContext:
        def __init__(self):
            self.function_name = function_name
            self.memory_limit_in_mb = memory_limit
            self.invoked_function_arn = f"arn:aws:lambda:us-east-1:123456789012:function:{function_name}"
            self.aws_request_id = "test-request-id"
            self.log_group_name = f"/aws/lambda/{function_name}"
            self.log_stream_name = "test-stream"
            self._remaining_time = timeout * 1000
            
        def get_remaining_time_in_millis(self):
            return self._remaining_time
    
    return MockLambdaContext()


def create_csv_content(headers: List[str], rows: List[List[str]]) -> str:
    """
    Create CSV content from headers and rows.
    
    Args:
        headers: List of column headers
        rows: List of data rows
        
    Returns:
        CSV content as string
    """
    header_line = ",".join(headers)
    data_lines = "\n".join([",".join(row) for row in rows])
    return f"{header_line}\n{data_lines}"


def create_sales_csv(records: List[Dict[str, Any]]) -> str:
    """
    Create a CSV string from sales records.
    
    Args:
        records: List of sales record dictionaries
        
    Returns:
        CSV content as string
    """
    if not records:
        return "date,sku,quantity\n"
    
    headers = list(records[0].keys())
    rows = [[str(record.get(h, "")) for h in headers] for record in records]
    return create_csv_content(headers, rows)


def is_valid_date_string(date_string: str) -> bool:
    """
    Validate if a string is a valid ISO date.
    
    Args:
        date_string: Date string to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        datetime.fromisoformat(date_string.replace("Z", "+00:00"))
        return True
    except (ValueError, AttributeError):
        return False


def is_in_range(value: float, min_value: float, max_value: float) -> bool:
    """
    Check if a value is within a range (inclusive).
    
    Args:
        value: Value to check
        min_value: Minimum value
        max_value: Maximum value
        
    Returns:
        True if in range, False otherwise
    """
    return min_value <= value <= max_value


def is_valid_confidence(confidence: float) -> bool:
    """
    Validate confidence indicator (0-1 range).
    
    Args:
        confidence: Confidence value
        
    Returns:
        True if valid, False otherwise
    """
    return is_in_range(confidence, 0.0, 1.0)


def is_valid_forecast_horizon(horizon: int) -> bool:
    """
    Validate forecast horizon (7-14 days as per spec).
    
    Args:
        horizon: Forecast horizon in days
        
    Returns:
        True if valid, False otherwise
    """
    return is_in_range(horizon, 7, 14)


def has_required_fields(obj: Dict[str, Any], required_fields: List[str]) -> bool:
    """
    Check if an object has all required fields.
    
    Args:
        obj: Dictionary to check
        required_fields: List of required field names
        
    Returns:
        True if all fields present, False otherwise
    """
    return all(field in obj and obj[field] is not None for field in required_fields)


def calculate_percentage_difference(baseline: float, comparison: float) -> float:
    """
    Calculate percentage difference between two values.
    
    Args:
        baseline: Baseline value
        comparison: Comparison value
        
    Returns:
        Percentage difference
    """
    if baseline == 0:
        return float("inf") if comparison != 0 else 0.0
    return ((comparison - baseline) / baseline) * 100


def is_in_festival_period(
    date: datetime, festival_date: datetime, duration: int
) -> bool:
    """
    Check if a date is within a festival period.
    
    Args:
        date: Date to check
        festival_date: Festival start date
        duration: Festival duration in days
        
    Returns:
        True if in festival period, False otherwise
    """
    festival_end = festival_date + timedelta(days=duration)
    return festival_date <= date <= festival_end


def generate_date_range(start_date: datetime, days: int) -> List[str]:
    """
    Generate a list of date strings for a given range.
    
    Args:
        start_date: Starting date
        days: Number of days
        
    Returns:
        List of ISO date strings
    """
    return [
        (start_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days)
    ]


def mock_s3_object(bucket: str, key: str, content: str) -> Dict[str, Any]:
    """
    Create a mock S3 object for testing.
    
    Args:
        bucket: S3 bucket name
        key: S3 object key
        content: Object content
        
    Returns:
        Mock S3 object dictionary
    """
    return {
        "Bucket": bucket,
        "Key": key,
        "Body": content.encode("utf-8"),
        "ContentLength": len(content),
        "ContentType": "text/csv",
        "LastModified": datetime.now(),
    }


def mock_dynamodb_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a mock DynamoDB item with proper type formatting.
    
    Args:
        item: Item dictionary
        
    Returns:
        DynamoDB formatted item
    """
    
    def format_value(value: Any) -> Dict[str, Any]:
        if isinstance(value, str):
            return {"S": value}
        elif isinstance(value, (int, float)):
            return {"N": str(value)}
        elif isinstance(value, bool):
            return {"BOOL": value}
        elif isinstance(value, dict):
            return {"M": {k: format_value(v) for k, v in value.items()}}
        elif isinstance(value, list):
            return {"L": [format_value(v) for v in value]}
        elif value is None:
            return {"NULL": True}
        else:
            return {"S": str(value)}
    
    return {k: format_value(v) for k, v in item.items()}


def assert_api_response(
    response: Dict[str, Any],
    expected_status: int = 200,
    expected_body_keys: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Assert API Gateway response format and return parsed body.
    
    Args:
        response: API Gateway response
        expected_status: Expected status code
        expected_body_keys: Expected keys in response body
        
    Returns:
        Parsed response body
    """
    assert "statusCode" in response
    assert response["statusCode"] == expected_status
    assert "body" in response
    
    body = json.loads(response["body"]) if isinstance(response["body"], str) else response["body"]
    
    if expected_body_keys:
        for key in expected_body_keys:
            assert key in body, f"Expected key '{key}' not found in response body"
    
    return body


def assert_forecast_result_valid(forecast: Dict[str, Any]) -> None:
    """
    Assert that a forecast result has valid structure and values.
    
    Args:
        forecast: Forecast result dictionary
    """
    required_fields = ["sku", "category", "predictions", "confidence", "methodology"]
    assert has_required_fields(forecast, required_fields)
    assert is_valid_confidence(forecast["confidence"])
    assert forecast["methodology"] in ["ml", "pattern", "hybrid"]
    assert isinstance(forecast["predictions"], list)
    assert len(forecast["predictions"]) > 0
    
    for prediction in forecast["predictions"]:
        assert has_required_fields(
            prediction, ["date", "demandForecast", "lowerBound", "upperBound"]
        )
        assert is_valid_date_string(prediction["date"])
        assert prediction["demandForecast"] >= 0
        assert prediction["lowerBound"] <= prediction["demandForecast"]
        assert prediction["upperBound"] >= prediction["demandForecast"]


def assert_risk_assessment_valid(risk: Dict[str, Any]) -> None:
    """
    Assert that a risk assessment has valid structure and values.
    
    Args:
        risk: Risk assessment dictionary
    """
    required_fields = ["sku", "category", "currentStock", "stockoutRisk", "overstockRisk", "recommendation"]
    assert has_required_fields(risk, required_fields)
    
    # Validate stockout risk
    assert has_required_fields(risk["stockoutRisk"], ["probability", "daysUntilStockout", "potentialLostSales"])
    assert is_valid_confidence(risk["stockoutRisk"]["probability"])
    
    # Validate overstock risk
    assert has_required_fields(risk["overstockRisk"], ["probability", "excessUnits", "carryingCost"])
    assert is_valid_confidence(risk["overstockRisk"]["probability"])
    
    # Validate recommendation
    assert has_required_fields(risk["recommendation"], ["action", "suggestedQuantity", "urgency", "confidence"])
    assert risk["recommendation"]["action"] in ["reorder", "reduce", "maintain"]
    assert risk["recommendation"]["urgency"] in ["low", "medium", "high"]
    assert is_valid_confidence(risk["recommendation"]["confidence"])
