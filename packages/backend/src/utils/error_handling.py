"""
Comprehensive error handling utilities for VyaparSaathi.

This module provides:
- Custom exception classes with specific error types
- Error response formatter with clear messages
- Retry logic with exponential backoff
- Circuit breaker for external service calls
"""

import time
import functools
import json
from typing import Any, Callable, Dict, Optional, Type
from enum import Enum
from datetime import datetime, timedelta
from botocore.exceptions import ClientError


class ErrorType(str, Enum):
    """Error type enumeration for categorizing errors."""
    VALIDATION_ERROR = "validation_error"
    DATA_NOT_FOUND = "data_not_found"
    AUTHENTICATION_ERROR = "authentication_error"
    AUTHORIZATION_ERROR = "authorization_error"
    EXTERNAL_SERVICE_ERROR = "external_service_error"
    DATABASE_ERROR = "database_error"
    TIMEOUT_ERROR = "timeout_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
    INTERNAL_ERROR = "internal_error"


class VyaparSaathiError(Exception):
    """Base exception class for VyaparSaathi errors."""
    
    def __init__(
        self,
        message: str,
        error_type: ErrorType = ErrorType.INTERNAL_ERROR,
        details: Optional[Dict[str, Any]] = None,
        recoverable: bool = False
    ):
        """
        Initialize VyaparSaathi error.
        
        Args:
            message: Human-readable error message
            error_type: Type of error
            details: Additional error details
            recoverable: Whether the error is recoverable with retry
        """
        super().__init__(message)
        self.message = message
        self.error_type = error_type
        self.details = details or {}
        self.recoverable = recoverable
        self.timestamp = datetime.utcnow().isoformat()


class ValidationError(VyaparSaathiError):
    """Error for invalid input data."""
    
    def __init__(self, message: str, field: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_type=ErrorType.VALIDATION_ERROR,
            details={**(details or {}), 'field': field} if field else details,
            recoverable=False
        )


class DataNotFoundError(VyaparSaathiError):
    """Error when requested data is not found."""
    
    def __init__(self, message: str, resource: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_type=ErrorType.DATA_NOT_FOUND,
            details={**(details or {}), 'resource': resource} if resource else details,
            recoverable=False
        )


class ExternalServiceError(VyaparSaathiError):
    """Error when external service call fails."""
    
    def __init__(self, message: str, service: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_type=ErrorType.EXTERNAL_SERVICE_ERROR,
            details={**(details or {}), 'service': service},
            recoverable=True
        )


class DatabaseError(VyaparSaathiError):
    """Error when database operation fails."""
    
    def __init__(self, message: str, operation: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_type=ErrorType.DATABASE_ERROR,
            details={**(details or {}), 'operation': operation} if operation else details,
            recoverable=True
        )


class TimeoutError(VyaparSaathiError):
    """Error when operation times out."""
    
    def __init__(self, message: str, timeout_seconds: Optional[float] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_type=ErrorType.TIMEOUT_ERROR,
            details={**(details or {}), 'timeout_seconds': timeout_seconds} if timeout_seconds else details,
            recoverable=True
        )


class RateLimitError(VyaparSaathiError):
    """Error when rate limit is exceeded."""
    
    def __init__(self, message: str, retry_after: Optional[int] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_type=ErrorType.RATE_LIMIT_ERROR,
            details={**(details or {}), 'retry_after': retry_after} if retry_after else details,
            recoverable=True
        )


class ErrorResponseFormatter:
    """Format error responses for API Gateway."""
    
    @staticmethod
    def format_error(
        error: Exception,
        include_details: bool = True
    ) -> Dict[str, Any]:
        """
        Format error into API Gateway response.
        
        Args:
            error: Exception to format
            include_details: Whether to include detailed error information
            
        Returns:
            API Gateway response dictionary
        """
        if isinstance(error, VyaparSaathiError):
            status_code = ErrorResponseFormatter._get_status_code(error.error_type)
            
            response_body = {
                'error': error.error_type.value,
                'message': error.message,
                'timestamp': error.timestamp,
            }
            
            if include_details and error.details:
                response_body['details'] = error.details
            
            if error.recoverable:
                response_body['recoverable'] = True
                response_body['recovery_options'] = ErrorResponseFormatter._get_recovery_options(error)
            
        elif isinstance(error, ClientError):
            # AWS SDK errors
            status_code = 500
            error_code = error.response.get('Error', {}).get('Code', 'Unknown')
            error_message = error.response.get('Error', {}).get('Message', str(error))
            
            response_body = {
                'error': 'external_service_error',
                'message': f'AWS service error: {error_message}',
                'timestamp': datetime.utcnow().isoformat(),
            }
            
            if include_details:
                response_body['details'] = {
                    'aws_error_code': error_code,
                    'service': error.response.get('ResponseMetadata', {}).get('HTTPHeaders', {}).get('x-amzn-requestid')
                }
        
        else:
            # Generic errors
            status_code = 500
            response_body = {
                'error': 'internal_error',
                'message': 'An unexpected error occurred. Please try again later.',
                'timestamp': datetime.utcnow().isoformat(),
            }
            
            if include_details:
                response_body['details'] = {
                    'error_type': type(error).__name__,
                    'error_message': str(error)
                }
        
        return {
            'statusCode': status_code,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            'body': json.dumps(response_body)
        }
    
    @staticmethod
    def _get_status_code(error_type: ErrorType) -> int:
        """Get HTTP status code for error type."""
        status_codes = {
            ErrorType.VALIDATION_ERROR: 400,
            ErrorType.DATA_NOT_FOUND: 404,
            ErrorType.AUTHENTICATION_ERROR: 401,
            ErrorType.AUTHORIZATION_ERROR: 403,
            ErrorType.EXTERNAL_SERVICE_ERROR: 502,
            ErrorType.DATABASE_ERROR: 500,
            ErrorType.TIMEOUT_ERROR: 504,
            ErrorType.RATE_LIMIT_ERROR: 429,
            ErrorType.INTERNAL_ERROR: 500,
        }
        return status_codes.get(error_type, 500)
    
    @staticmethod
    def _get_recovery_options(error: VyaparSaathiError) -> list:
        """Get recovery options for error."""
        if error.error_type == ErrorType.RATE_LIMIT_ERROR:
            retry_after = error.details.get('retry_after', 60)
            return [
                f"Wait {retry_after} seconds and retry the request",
                "Reduce request frequency"
            ]
        elif error.error_type == ErrorType.TIMEOUT_ERROR:
            return [
                "Retry the request",
                "Reduce the data size or complexity",
                "Contact support if the issue persists"
            ]
        elif error.error_type == ErrorType.EXTERNAL_SERVICE_ERROR:
            return [
                "Retry the request after a short delay",
                "Check service status",
                "Contact support if the issue persists"
            ]
        elif error.error_type == ErrorType.DATABASE_ERROR:
            return [
                "Retry the request",
                "Contact support if the issue persists"
            ]
        else:
            return ["Retry the request", "Contact support if the issue persists"]


class RetryHandler:
    """Handle retries with exponential backoff."""
    
    @staticmethod
    def with_retry(
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 30.0,
        exponential_base: float = 2.0,
        exceptions: tuple = (Exception,)
    ):
        """
        Decorator to retry function with exponential backoff.
        
        Args:
            max_attempts: Maximum number of retry attempts
            initial_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
            exponential_base: Base for exponential backoff
            exceptions: Tuple of exceptions to catch and retry
            
        Usage:
            @RetryHandler.with_retry(max_attempts=3, initial_delay=1.0)
            def my_function():
                pass
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                attempt = 0
                delay = initial_delay
                
                while attempt < max_attempts:
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        attempt += 1
                        
                        # Check if error is recoverable
                        if isinstance(e, VyaparSaathiError) and not e.recoverable:
                            raise
                        
                        if attempt >= max_attempts:
                            print(f"Max retry attempts ({max_attempts}) reached for {func.__name__}")
                            raise
                        
                        # Calculate delay with exponential backoff
                        current_delay = min(delay * (exponential_base ** (attempt - 1)), max_delay)
                        
                        print(f"Attempt {attempt} failed for {func.__name__}, retrying in {current_delay:.2f}s: {str(e)}")
                        time.sleep(current_delay)
                
                # Should never reach here
                raise Exception(f"Unexpected retry loop exit for {func.__name__}")
            
            return wrapper
        return decorator


class CircuitBreaker:
    """Circuit breaker pattern for external service calls."""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: Type[Exception] = Exception
    ):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before attempting recovery
            expected_exception: Exception type to catch
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = 'closed'  # closed, open, half_open
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Call function with circuit breaker protection.
        
        Args:
            func: Function to call
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            ExternalServiceError: When circuit is open
        """
        if self.state == 'open':
            if self._should_attempt_reset():
                self.state = 'half_open'
            else:
                raise ExternalServiceError(
                    message=f"Circuit breaker is open for {func.__name__}. Service temporarily unavailable.",
                    service=func.__name__,
                    details={
                        'failure_count': self.failure_count,
                        'retry_after': self.recovery_timeout
                    }
                )
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.last_failure_time is None:
            return True
        
        time_since_failure = (datetime.utcnow() - self.last_failure_time).total_seconds()
        return time_since_failure >= self.recovery_timeout
    
    def _on_success(self):
        """Handle successful call."""
        self.failure_count = 0
        self.state = 'closed'
    
    def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        
        if self.failure_count >= self.failure_threshold:
            self.state = 'open'
            print(f"Circuit breaker opened after {self.failure_count} failures")


# Global circuit breakers for external services
_circuit_breakers: Dict[str, CircuitBreaker] = {}


def get_circuit_breaker(service_name: str) -> CircuitBreaker:
    """
    Get or create circuit breaker for a service.
    
    Args:
        service_name: Name of the service
        
    Returns:
        CircuitBreaker instance
    """
    if service_name not in _circuit_breakers:
        _circuit_breakers[service_name] = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60,
            expected_exception=Exception
        )
    
    return _circuit_breakers[service_name]


def with_circuit_breaker(service_name: str):
    """
    Decorator to protect function with circuit breaker.
    
    Usage:
        @with_circuit_breaker('bedrock')
        def call_bedrock_api():
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            circuit_breaker = get_circuit_breaker(service_name)
            return circuit_breaker.call(func, *args, **kwargs)
        
        return wrapper
    return decorator
