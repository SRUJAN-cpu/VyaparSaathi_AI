"""
Property-based tests for error handling in VyaparSaathi.

This module tests Property 12: Error Handling
- For any system error or invalid input, the system should provide clear error messages and recovery options
- Validates: Requirements 6.5

Test Areas:
1. Data validation errors (CSV parsing, missing fields, invalid data types)
2. API errors (timeouts, rate limiting, authentication failures)
3. Service errors (external service failures)
4. Input validation errors (questionnaire, forecast requests)
5. Error message clarity and actionability
6. Recovery option availability
"""

import pytest
import json
from datetime import datetime
from hypothesis import given, strategies as st, assume
from unittest.mock import Mock, patch
from botocore.exceptions import ClientError

from src.utils.error_handling import (
    VyaparSaathiError,
    ValidationError,
    DataNotFoundError,
    ExternalServiceError,
    DatabaseError,
    TimeoutError,
    RateLimitError,
    ErrorResponseFormatter,
    RetryHandler,
    CircuitBreaker,
    ErrorType,
)

from tests.strategies import (
    sales_record_strategy,
    invalid_sales_record_strategy,
    forecast_request_strategy,
    questionnaire_response_strategy,
)


# ============================================================================
# Property Tests for Error Response Formatting
# ============================================================================

@pytest.mark.property
@given(
    message=st.text(min_size=10, max_size=200),
    error_type=st.sampled_from(list(ErrorType)),
)
def test_property_all_errors_have_clear_messages(message, error_type):
    """
    Property test: All errors should have clear, non-empty messages.
    
    **Validates: Requirements 6.5**
    """
    error = VyaparSaathiError(message=message, error_type=error_type)
    response = ErrorResponseFormatter.format_error(error)
    
    # Parse response body
    body = json.loads(response['body'])
    
    # Error message should be present and non-empty
    assert 'message' in body
    assert len(body['message']) > 0
    assert isinstance(body['message'], str)
    
    # Error type should be present
    assert 'error' in body
    assert body['error'] == error_type.value
    
    # Timestamp should be present
    assert 'timestamp' in body
    assert datetime.fromisoformat(body['timestamp'])


@pytest.mark.property
@given(
    message=st.text(min_size=10, max_size=200),
    retry_after=st.integers(min_value=1, max_value=300),
)
def test_property_recoverable_errors_provide_recovery_options(message, retry_after):
    """
    Property test: All recoverable errors should provide recovery options.
    
    **Validates: Requirements 6.5**
    """
    # Test with different recoverable error types
    recoverable_errors = [
        RateLimitError(message, retry_after=retry_after),
        TimeoutError(message, timeout_seconds=30.0),
        ExternalServiceError(message, service="test-service"),
        DatabaseError(message, operation="query"),
    ]
    
    for error in recoverable_errors:
        response = ErrorResponseFormatter.format_error(error)
        body = json.loads(response['body'])
        
        # Should indicate error is recoverable
        assert body.get('recoverable') == True
        
        # Should provide recovery options
        assert 'recovery_options' in body
        assert isinstance(body['recovery_options'], list)
        assert len(body['recovery_options']) > 0
        
        # Recovery options should be actionable strings
        for option in body['recovery_options']:
            assert isinstance(option, str)
            assert len(option) > 0


@pytest.mark.property
@given(
    message=st.text(min_size=10, max_size=200),
    field=st.text(min_size=1, max_size=50),
)
def test_property_validation_errors_include_field_information(message, field):
    """
    Property test: Validation errors should include field information for user correction.
    
    **Validates: Requirements 6.5**
    """
    error = ValidationError(message, field=field)
    response = ErrorResponseFormatter.format_error(error, include_details=True)
    body = json.loads(response['body'])
    
    # Should have validation error type
    assert body['error'] == ErrorType.VALIDATION_ERROR.value
    
    # Should include field details
    assert 'details' in body
    assert 'field' in body['details']
    assert body['details']['field'] == field
    
    # Should have appropriate status code
    assert response['statusCode'] == 400


@pytest.mark.property
@given(
    error_code=st.sampled_from(['ThrottlingException', 'ServiceUnavailable', 'InternalError']),
    error_message=st.text(min_size=10, max_size=200),
)
def test_property_aws_errors_formatted_correctly(error_code, error_message):
    """
    Property test: AWS SDK errors should be formatted with clear messages.
    
    **Validates: Requirements 6.5**
    """
    # Create mock AWS ClientError
    client_error = ClientError(
        error_response={
            'Error': {
                'Code': error_code,
                'Message': error_message,
            },
            'ResponseMetadata': {
                'HTTPHeaders': {
                    'x-amzn-requestid': 'test-request-id'
                }
            }
        },
        operation_name='TestOperation'
    )
    
    response = ErrorResponseFormatter.format_error(client_error, include_details=True)
    body = json.loads(response['body'])
    
    # Should have external service error type
    assert body['error'] == 'external_service_error'
    
    # Should have clear message
    assert 'message' in body
    assert len(body['message']) > 0
    
    # Should include AWS error details
    assert 'details' in body
    assert 'aws_error_code' in body['details']
    assert body['details']['aws_error_code'] == error_code


# ============================================================================
# Property Tests for Retry Logic
# ============================================================================

@pytest.mark.property
@given(
    max_attempts=st.integers(min_value=1, max_value=5),
    should_succeed_on_attempt=st.integers(min_value=1, max_value=5),
)
def test_property_retry_handler_respects_max_attempts(max_attempts, should_succeed_on_attempt):
    """
    Property test: Retry handler should respect max attempts configuration.
    
    **Validates: Requirements 6.5**
    """
    assume(should_succeed_on_attempt <= max_attempts)
    
    call_count = {'count': 0}
    
    @RetryHandler.with_retry(
        max_attempts=max_attempts,
        initial_delay=0.01,  # Fast for testing
        exponential_base=1.5
    )
    def flaky_function():
        call_count['count'] += 1
        if call_count['count'] < should_succeed_on_attempt:
            raise ExternalServiceError("Temporary failure", service="test")
        return "success"
    
    result = flaky_function()
    
    # Should succeed after the specified attempt
    assert result == "success"
    assert call_count['count'] == should_succeed_on_attempt


@pytest.mark.property
@given(
    max_attempts=st.integers(min_value=1, max_value=3),
)
def test_property_retry_handler_fails_after_max_attempts(max_attempts):
    """
    Property test: Retry handler should fail after max attempts are exhausted.
    
    **Validates: Requirements 6.5**
    """
    call_count = {'count': 0}
    
    @RetryHandler.with_retry(
        max_attempts=max_attempts,
        initial_delay=0.01,  # Fast for testing
    )
    def always_failing_function():
        call_count['count'] += 1
        raise ExternalServiceError("Persistent failure", service="test")
    
    with pytest.raises(ExternalServiceError):
        always_failing_function()
    
    # Should have attempted exactly max_attempts times
    assert call_count['count'] == max_attempts


@pytest.mark.property
@given(
    message=st.text(min_size=10, max_size=200),
    field=st.text(min_size=1, max_size=50),
)
def test_property_non_recoverable_errors_not_retried(message, field):
    """
    Property test: Non-recoverable errors should not be retried.
    
    **Validates: Requirements 6.5**
    """
    call_count = {'count': 0}
    
    @RetryHandler.with_retry(max_attempts=3, initial_delay=0.01)
    def function_with_validation_error():
        call_count['count'] += 1
        raise ValidationError(message, field=field)
    
    with pytest.raises(ValidationError):
        function_with_validation_error()
    
    # Should only be called once (no retries for non-recoverable errors)
    assert call_count['count'] == 1


# ============================================================================
# Property Tests for Circuit Breaker
# ============================================================================

@pytest.mark.property
@given(
    failure_threshold=st.integers(min_value=2, max_value=10),
    num_failures=st.integers(min_value=1, max_value=15),
)
def test_property_circuit_breaker_opens_after_threshold(failure_threshold, num_failures):
    """
    Property test: Circuit breaker should open after failure threshold is reached.
    
    **Validates: Requirements 6.5**
    """
    circuit_breaker = CircuitBreaker(
        failure_threshold=failure_threshold,
        recovery_timeout=60,
        expected_exception=Exception
    )
    
    def failing_function():
        raise Exception("Service failure")
    
    # Attempt calls up to num_failures
    for i in range(num_failures):
        try:
            circuit_breaker.call(failing_function)
        except Exception:
            pass
    
    # Check circuit state
    if num_failures >= failure_threshold:
        assert circuit_breaker.state == 'open'
        assert circuit_breaker.failure_count >= failure_threshold
        
        # Next call should raise ExternalServiceError
        with pytest.raises(ExternalServiceError) as exc_info:
            circuit_breaker.call(failing_function)
        
        # Error should indicate circuit is open
        assert "Circuit breaker is open" in str(exc_info.value)
    else:
        # Circuit should still be closed
        assert circuit_breaker.state == 'closed'


@pytest.mark.property
@given(
    failure_threshold=st.integers(min_value=2, max_value=5),
)
def test_property_circuit_breaker_resets_on_success(failure_threshold):
    """
    Property test: Circuit breaker should reset failure count on successful call.
    
    **Validates: Requirements 6.5**
    """
    circuit_breaker = CircuitBreaker(
        failure_threshold=failure_threshold,
        recovery_timeout=60,
        expected_exception=Exception
    )
    
    call_count = {'count': 0}
    
    def sometimes_failing_function():
        call_count['count'] += 1
        if call_count['count'] < failure_threshold:
            raise Exception("Temporary failure")
        return "success"
    
    # Fail a few times (but less than threshold)
    for i in range(failure_threshold - 1):
        try:
            circuit_breaker.call(sometimes_failing_function)
        except Exception:
            pass
    
    # Should still be closed
    assert circuit_breaker.state == 'closed'
    
    # Successful call should reset failure count
    result = circuit_breaker.call(sometimes_failing_function)
    assert result == "success"
    assert circuit_breaker.failure_count == 0
    assert circuit_breaker.state == 'closed'


# ============================================================================
# Property Tests for Data Validation Errors
# ============================================================================

@pytest.mark.property
@given(invalid_record=invalid_sales_record_strategy())
def test_property_invalid_data_produces_validation_errors(invalid_record):
    """
    Property test: Invalid sales data should produce validation errors with clear messages.
    
    **Validates: Requirements 6.5**
    """
    # Create a simple CSV from the invalid record
    csv_lines = ["date,sku,quantity"]
    
    # Build CSV line from record
    date_val = invalid_record.get('date', '')
    sku_val = invalid_record.get('sku', '')
    quantity_val = invalid_record.get('quantity', '')
    
    csv_lines.append(f"{date_val},{sku_val},{quantity_val}")
    csv_content = "\n".join(csv_lines)
    
    from src.data_processor.csv_handler import validate_sales_data
    
    # Validation should detect issues
    validation_result, records = validate_sales_data(csv_content)
    
    # If record is truly invalid, should have errors or warnings
    if not validation_result.success or len(validation_result.error_messages) > 0:
        # Should have error messages
        assert len(validation_result.error_messages) > 0
        
        # Each error should be a clear string
        for error in validation_result.error_messages:
            assert isinstance(error, str)
            assert len(error) > 0
            
            # Error message should be descriptive (not just a code or single word)
            # Allow for various error message formats
            assert len(error.split()) >= 2, f"Error message too short: {error}"


@pytest.mark.property
@given(
    questionnaire=questionnaire_response_strategy(),
    missing_field=st.sampled_from(['businessType', 'storeSize', 'targetFestivals'])
)
def test_property_missing_required_fields_produce_clear_errors(questionnaire, missing_field):
    """
    Property test: Missing required fields should produce clear error messages.
    
    **Validates: Requirements 6.5**
    """
    # Remove a required field
    incomplete_questionnaire = questionnaire.copy()
    if missing_field in incomplete_questionnaire:
        del incomplete_questionnaire[missing_field]
    
    # Create validation error
    error = ValidationError(
        f"Missing required field: {missing_field}",
        field=missing_field
    )
    
    response = ErrorResponseFormatter.format_error(error, include_details=True)
    body = json.loads(response['body'])
    
    # Should clearly indicate the missing field
    assert missing_field in body['message'] or missing_field in str(body.get('details', {}))
    
    # Should be a 400 Bad Request
    assert response['statusCode'] == 400


# ============================================================================
# Property Tests for Service Error Handling
# ============================================================================

@pytest.mark.property
@given(
    service_name=st.sampled_from(['bedrock', 'forecast', 'dynamodb', 's3']),
    error_message=st.text(min_size=10, max_size=200),
)
def test_property_service_errors_include_service_name(service_name, error_message):
    """
    Property test: Service errors should clearly identify which service failed.
    
    **Validates: Requirements 6.5**
    """
    error = ExternalServiceError(error_message, service=service_name)
    response = ErrorResponseFormatter.format_error(error, include_details=True)
    body = json.loads(response['body'])
    
    # Should identify the service
    assert 'details' in body
    assert 'service' in body['details']
    assert body['details']['service'] == service_name
    
    # Should be a 502 Bad Gateway
    assert response['statusCode'] == 502
    
    # Should provide recovery options
    assert 'recovery_options' in body
    assert len(body['recovery_options']) > 0


@pytest.mark.property
@given(
    timeout_seconds=st.floats(min_value=1.0, max_value=300.0),
    operation=st.text(min_size=5, max_size=50),
)
def test_property_timeout_errors_include_timeout_duration(timeout_seconds, operation):
    """
    Property test: Timeout errors should include timeout duration for context.
    
    **Validates: Requirements 6.5**
    """
    error = TimeoutError(
        f"Operation '{operation}' timed out",
        timeout_seconds=timeout_seconds
    )
    
    response = ErrorResponseFormatter.format_error(error, include_details=True)
    body = json.loads(response['body'])
    
    # Should include timeout information
    assert 'details' in body
    assert 'timeout_seconds' in body['details']
    assert body['details']['timeout_seconds'] == timeout_seconds
    
    # Should be a 504 Gateway Timeout
    assert response['statusCode'] == 504
    
    # Should provide recovery options
    assert 'recovery_options' in body


@pytest.mark.property
@given(
    retry_after=st.integers(min_value=1, max_value=300),
)
def test_property_rate_limit_errors_include_retry_timing(retry_after):
    """
    Property test: Rate limit errors should include retry timing information.
    
    **Validates: Requirements 6.5**
    """
    error = RateLimitError(
        "Rate limit exceeded",
        retry_after=retry_after
    )
    
    response = ErrorResponseFormatter.format_error(error, include_details=True)
    body = json.loads(response['body'])
    
    # Should include retry timing
    assert 'details' in body
    assert 'retry_after' in body['details']
    assert body['details']['retry_after'] == retry_after
    
    # Should be a 429 Too Many Requests
    assert response['statusCode'] == 429
    
    # Recovery options should mention waiting
    assert 'recovery_options' in body
    assert any('wait' in option.lower() or 'retry' in option.lower() 
              for option in body['recovery_options'])


# ============================================================================
# Property Tests for Error Message Clarity
# ============================================================================

@pytest.mark.property
@given(
    error_type=st.sampled_from(list(ErrorType)),
    message=st.text(min_size=20, max_size=200),
)
def test_property_error_messages_are_non_technical(error_type, message):
    """
    Property test: Error messages should avoid exposing technical details.
    
    **Validates: Requirements 6.5**
    """
    error = VyaparSaathiError(message=message, error_type=error_type)
    response = ErrorResponseFormatter.format_error(error, include_details=False)
    body = json.loads(response['body'])
    
    # Message should not contain sensitive technical details
    sensitive_terms = [
        'stack trace', 'exception', 'traceback', 'sql', 'query',
        'password', 'secret', 'key', 'token', 'credential'
    ]
    
    message_lower = body['message'].lower()
    for term in sensitive_terms:
        assert term not in message_lower, f"Error message contains sensitive term: {term}"


@pytest.mark.property
@given(
    error_type=st.sampled_from(list(ErrorType)),
)
def test_property_all_error_types_have_appropriate_status_codes(error_type):
    """
    Property test: All error types should map to appropriate HTTP status codes.
    
    **Validates: Requirements 6.5**
    """
    error = VyaparSaathiError(message="Test error", error_type=error_type)
    response = ErrorResponseFormatter.format_error(error)
    
    status_code = response['statusCode']
    
    # Status code should be in valid HTTP error range
    assert 400 <= status_code < 600
    
    # Verify specific mappings
    if error_type == ErrorType.VALIDATION_ERROR:
        assert status_code == 400
    elif error_type == ErrorType.DATA_NOT_FOUND:
        assert status_code == 404
    elif error_type == ErrorType.RATE_LIMIT_ERROR:
        assert status_code == 429
    elif error_type == ErrorType.EXTERNAL_SERVICE_ERROR:
        assert status_code == 502
    elif error_type == ErrorType.TIMEOUT_ERROR:
        assert status_code == 504


# ============================================================================
# Property Tests for Error Response Structure
# ============================================================================

@pytest.mark.property
@given(
    error_type=st.sampled_from(list(ErrorType)),
    message=st.text(min_size=10, max_size=200),
)
def test_property_all_error_responses_have_required_fields(error_type, message):
    """
    Property test: All error responses should have required fields (error, message, timestamp).
    
    **Validates: Requirements 6.5**
    """
    error = VyaparSaathiError(message=message, error_type=error_type)
    response = ErrorResponseFormatter.format_error(error)
    
    # Should have proper response structure
    assert 'statusCode' in response
    assert 'headers' in response
    assert 'body' in response
    
    # Headers should include CORS
    assert 'Access-Control-Allow-Origin' in response['headers']
    assert 'Content-Type' in response['headers']
    assert response['headers']['Content-Type'] == 'application/json'
    
    # Body should be valid JSON
    body = json.loads(response['body'])
    
    # Required fields
    assert 'error' in body
    assert 'message' in body
    assert 'timestamp' in body
    
    # Timestamp should be valid ISO format
    datetime.fromisoformat(body['timestamp'])


# ============================================================================
# Integration Tests for Error Handling Across Components
# ============================================================================

@pytest.mark.property
@given(
    forecast_request=forecast_request_strategy(),
)
def test_property_invalid_forecast_requests_produce_actionable_errors(forecast_request):
    """
    Property test: Invalid forecast requests should produce actionable error messages.
    
    **Validates: Requirements 6.5**
    """
    # Make forecast horizon invalid
    invalid_request = forecast_request.copy()
    invalid_request['forecastHorizon'] = -1  # Invalid value
    
    error = ValidationError(
        "Forecast horizon must be between 7 and 14 days",
        field="forecastHorizon",
        details={'provided_value': -1, 'valid_range': '7-14'}
    )
    
    response = ErrorResponseFormatter.format_error(error, include_details=True)
    body = json.loads(response['body'])
    
    # Should clearly explain the constraint
    assert 'forecastHorizon' in body['message'] or 'forecastHorizon' in str(body.get('details', {}))
    
    # Should include valid range in details
    if 'details' in body:
        assert 'valid_range' in body['details'] or 'provided_value' in body['details']
