"""
Amazon Bedrock client for AI explanation generation.

This module provides the core integration with Amazon Bedrock API,
including error handling, retry logic, and token usage tracking.
"""

import json
import time
import os
import sys
from typing import Dict, Any, Optional
from decimal import Decimal

import boto3
from botocore.exceptions import ClientError

# Import error handling utilities
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.error_handling import (
    ExternalServiceError,
    TimeoutError,
    RateLimitError,
    RetryHandler,
    with_circuit_breaker
)
from utils.performance import PerformanceMonitor


# Initialize Bedrock client
bedrock_runtime = boto3.client('bedrock-runtime', region_name=os.environ.get('AWS_REGION', 'us-east-1'))

# Model configuration
DEFAULT_MODEL_ID = os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-3-haiku-20240307-v1:0')
MAX_TOKENS = int(os.environ.get('BEDROCK_MAX_TOKENS', '2048'))
TEMPERATURE = float(os.environ.get('BEDROCK_TEMPERATURE', '0.7'))

# Retry configuration
MAX_RETRIES = 3
INITIAL_RETRY_DELAY = 1.0  # seconds
MAX_RETRY_DELAY = 10.0  # seconds


class BedrockError(Exception):
    """Custom exception for Bedrock API errors."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, retryable: bool = False):
        super().__init__(message)
        self.error_code = error_code
        self.retryable = retryable


@with_circuit_breaker('bedrock')
@RetryHandler.with_retry(
    max_attempts=3,
    initial_delay=1.0,
    exceptions=(ClientError, ExternalServiceError)
)
@PerformanceMonitor.measure_execution_time
def invoke_bedrock_model(
    prompt: str,
    model_id: Optional[str] = None,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
    system_prompt: Optional[str] = None,
    track_usage: bool = True
) -> Dict[str, Any]:
    """
    Invoke Amazon Bedrock model with retry logic and error handling.
    
    Args:
        prompt: The user prompt/question
        model_id: Bedrock model ID (defaults to Claude 3 Haiku)
        max_tokens: Maximum tokens to generate
        temperature: Temperature for generation (0-1)
        system_prompt: Optional system prompt for context
        track_usage: Whether to track token usage
        
    Returns:
        Dictionary containing:
            - text: Generated text response
            - usage: Token usage statistics (if track_usage=True)
            - model_id: Model used
            - stop_reason: Why generation stopped
            
    Raises:
        ExternalServiceError: If API call fails after retries
    """
    # Use defaults if not specified
    model_id = model_id or DEFAULT_MODEL_ID
    max_tokens = max_tokens or MAX_TOKENS
    temperature = temperature or TEMPERATURE
    
    # Prepare request body based on model
    if 'claude' in model_id.lower():
        # Claude 3 format
        messages = [
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages
        }
        
        if system_prompt:
            request_body["system"] = system_prompt
    else:
        # Generic format for other models
        request_body = {
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
    
    try:
        # Invoke Bedrock model
        response = bedrock_runtime.invoke_model(
            modelId=model_id,
            contentType='application/json',
            accept='application/json',
            body=json.dumps(request_body)
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        
        # Extract text based on model format
        if 'claude' in model_id.lower():
            # Claude 3 format
            text = response_body.get('content', [{}])[0].get('text', '')
            stop_reason = response_body.get('stop_reason', 'unknown')
            usage = response_body.get('usage', {})
        else:
            # Generic format
            text = response_body.get('completion', response_body.get('text', ''))
            stop_reason = response_body.get('stop_reason', 'unknown')
            usage = {
                'input_tokens': response_body.get('input_tokens', 0),
                'output_tokens': response_body.get('output_tokens', 0)
            }
        
        # Build result
        result = {
            'text': text,
            'model_id': model_id,
            'stop_reason': stop_reason
        }
        
        if track_usage:
            result['usage'] = {
                'input_tokens': usage.get('input_tokens', 0),
                'output_tokens': usage.get('output_tokens', 0),
                'total_tokens': usage.get('input_tokens', 0) + usage.get('output_tokens', 0)
            }
            
            # Calculate approximate cost (Claude 3 Haiku pricing)
            if 'haiku' in model_id.lower():
                input_cost = usage.get('input_tokens', 0) * 0.00025 / 1000  # $0.25 per 1M tokens
                output_cost = usage.get('output_tokens', 0) * 0.00125 / 1000  # $1.25 per 1M tokens
                result['usage']['estimated_cost_usd'] = input_cost + output_cost
            elif 'sonnet' in model_id.lower():
                input_cost = usage.get('input_tokens', 0) * 0.003 / 1000  # $3 per 1M tokens
                output_cost = usage.get('output_tokens', 0) * 0.015 / 1000  # $15 per 1M tokens
                result['usage']['estimated_cost_usd'] = input_cost + output_cost
        
        return result
        
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        error_message = e.response.get('Error', {}).get('Message', str(e))
        
        # Handle specific error types
        if error_code in ['ThrottlingException', 'TooManyRequestsException']:
            raise RateLimitError(
                message=f"Bedrock API rate limit exceeded: {error_message}",
                retry_after=60,
                details={'error_code': error_code}
            )
        elif error_code == 'TimeoutException':
            raise TimeoutError(
                message=f"Bedrock API timeout: {error_message}",
                timeout_seconds=30,
                details={'error_code': error_code}
            )
        else:
            raise ExternalServiceError(
                message=f"Bedrock API error: {error_message}",
                service='bedrock',
                details={'error_code': error_code}
            )
    
    except Exception as e:
        raise ExternalServiceError(
            message=f"Unexpected error invoking Bedrock: {str(e)}",
            service='bedrock'
        )


def test_bedrock_connection() -> Dict[str, Any]:
    """
    Test Bedrock connection with a simple prompt.
    
    Returns:
        Dictionary with test results
    """
    try:
        result = invoke_bedrock_model(
            prompt="Say 'Hello' in one word.",
            max_tokens=10,
            temperature=0.1
        )
        
        return {
            'success': True,
            'model_id': result['model_id'],
            'response': result['text'],
            'usage': result.get('usage')
        }
    except BedrockError as e:
        return {
            'success': False,
            'error': str(e),
            'error_code': e.error_code,
            'retryable': e.retryable
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
