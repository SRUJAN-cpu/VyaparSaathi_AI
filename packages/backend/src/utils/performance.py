"""
Performance monitoring and optimization utilities for VyaparSaathi.

This module provides:
- CloudWatch metrics publishing for response times
- In-memory caching for festival calendar and synthetic patterns
- Performance decorators for Lambda functions
"""

import time
import functools
import json
from typing import Any, Callable, Dict, Optional
from datetime import datetime, timedelta
import boto3
from botocore.exceptions import ClientError

# Initialize CloudWatch client
cloudwatch = boto3.client('cloudwatch')

# In-memory cache with TTL
_cache: Dict[str, Dict[str, Any]] = {}


class PerformanceMonitor:
    """Monitor and publish performance metrics to CloudWatch."""
    
    @staticmethod
    def publish_metric(
        metric_name: str,
        value: float,
        unit: str = 'Milliseconds',
        dimensions: Optional[Dict[str, str]] = None
    ) -> None:
        """
        Publish a metric to CloudWatch.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            unit: Unit of measurement (default: Milliseconds)
            dimensions: Optional dimensions for the metric
        """
        try:
            metric_data = {
                'MetricName': metric_name,
                'Value': value,
                'Unit': unit,
                'Timestamp': datetime.utcnow()
            }
            
            if dimensions:
                metric_data['Dimensions'] = [
                    {'Name': k, 'Value': v} for k, v in dimensions.items()
                ]
            
            cloudwatch.put_metric_data(
                Namespace='VyaparSaathi',
                MetricData=[metric_data]
            )
        except ClientError as e:
            # Log error but don't fail the request
            print(f"Failed to publish metric {metric_name}: {str(e)}")
    
    @staticmethod
    def measure_execution_time(func: Callable) -> Callable:
        """
        Decorator to measure and publish function execution time.
        
        Usage:
            @PerformanceMonitor.measure_execution_time
            def my_function():
                pass
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                execution_time = (time.time() - start_time) * 1000  # Convert to ms
                
                # Publish metric to CloudWatch
                PerformanceMonitor.publish_metric(
                    metric_name=f'{func.__name__}_ExecutionTime',
                    value=execution_time,
                    unit='Milliseconds',
                    dimensions={
                        'FunctionName': func.__name__,
                        'Component': func.__module__.split('.')[-2] if '.' in func.__module__ else 'unknown'
                    }
                )
                
                # Log execution time
                print(f"Function {func.__name__} executed in {execution_time:.2f}ms")
        
        return wrapper


class Cache:
    """In-memory cache with TTL support for Lambda functions."""
    
    @staticmethod
    def get(key: str) -> Optional[Any]:
        """
        Get value from cache if not expired.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found or expired
        """
        if key not in _cache:
            return None
        
        entry = _cache[key]
        if datetime.utcnow() > entry['expires_at']:
            # Entry expired, remove it
            del _cache[key]
            return None
        
        return entry['value']
    
    @staticmethod
    def set(key: str, value: Any, ttl_seconds: int = 300) -> None:
        """
        Set value in cache with TTL.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Time to live in seconds (default: 5 minutes)
        """
        _cache[key] = {
            'value': value,
            'expires_at': datetime.utcnow() + timedelta(seconds=ttl_seconds)
        }
    
    @staticmethod
    def clear() -> None:
        """Clear all cache entries."""
        _cache.clear()
    
    @staticmethod
    def cached(ttl_seconds: int = 300, key_prefix: str = ''):
        """
        Decorator to cache function results.
        
        Args:
            ttl_seconds: Time to live in seconds (default: 5 minutes)
            key_prefix: Prefix for cache key
            
        Usage:
            @Cache.cached(ttl_seconds=600, key_prefix='festivals')
            def get_festivals(region):
                return fetch_festivals(region)
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key from function name and arguments
                cache_key = f"{key_prefix}:{func.__name__}:{json.dumps(args)}:{json.dumps(kwargs, sort_keys=True)}"
                
                # Try to get from cache
                cached_value = Cache.get(cache_key)
                if cached_value is not None:
                    print(f"Cache hit for {func.__name__}")
                    return cached_value
                
                # Cache miss, execute function
                print(f"Cache miss for {func.__name__}")
                result = func(*args, **kwargs)
                
                # Store in cache
                Cache.set(cache_key, result, ttl_seconds)
                
                return result
            
            return wrapper
        return decorator


def lambda_handler_wrapper(func: Callable) -> Callable:
    """
    Wrapper for Lambda handlers that adds performance monitoring.
    
    Usage:
        @lambda_handler_wrapper
        def handler(event, context):
            return {'statusCode': 200}
    """
    @functools.wraps(func)
    def wrapper(event, context):
        start_time = time.time()
        
        try:
            result = func(event, context)
            
            # Measure execution time
            execution_time = (time.time() - start_time) * 1000
            
            # Publish metrics
            PerformanceMonitor.publish_metric(
                metric_name='LambdaExecutionTime',
                value=execution_time,
                unit='Milliseconds',
                dimensions={
                    'FunctionName': context.function_name if context else 'unknown',
                    'Handler': func.__name__
                }
            )
            
            # Log performance
            print(f"Lambda {context.function_name if context else 'unknown'} executed in {execution_time:.2f}ms")
            
            return result
            
        except Exception as e:
            # Publish error metric
            PerformanceMonitor.publish_metric(
                metric_name='LambdaErrors',
                value=1,
                unit='Count',
                dimensions={
                    'FunctionName': context.function_name if context else 'unknown',
                    'ErrorType': type(e).__name__
                }
            )
            raise
    
    return wrapper
