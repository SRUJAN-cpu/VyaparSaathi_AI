"""
Explanation generation handler and orchestration.

This module provides high-level functions for generating explanations
for different contexts (forecasts, risks, recommendations, conversations).
"""

import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

import boto3
from botocore.exceptions import ClientError

# Import internal modules
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from .bedrock_client import invoke_bedrock_model
from .prompt_templates import (
    SYSTEM_PROMPT,
    create_forecast_explanation_prompt,
    create_risk_explanation_prompt,
    create_recommendation_explanation_prompt,
    create_conversational_prompt
)
from forecast_engine.storage import get_latest_forecast_for_sku
from utils.error_handling import (
    ValidationError,
    ErrorResponseFormatter,
    VyaparSaathiError
)
from utils.performance import lambda_handler_wrapper


# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')

# Environment variables
FORECASTS_TABLE = os.environ.get('FORECASTS_TABLE', 'VyaparSaathi-Forecasts')
USER_PROFILE_TABLE = os.environ.get('USER_PROFILE_TABLE', 'VyaparSaathi-UserProfile')


def parse_explanation_response(response_text: str) -> Dict[str, Any]:
    """
    Parse the AI-generated explanation into structured components.
    
    Args:
        response_text: Raw text response from Bedrock
        
    Returns:
        Dictionary with parsed explanation components
    """
    # Initialize components
    explanation = response_text
    key_insights = []
    assumptions = []
    limitations = []
    confidence = ""
    next_steps = []
    
    # Try to extract structured sections
    lines = response_text.split('\n')
    current_section = None
    
    for line in lines:
        line = line.strip()
        
        # Detect section headers
        if 'key insight' in line.lower() or line.startswith('1.'):
            current_section = 'insights'
            continue
        elif 'assumption' in line.lower() or line.startswith('2.'):
            current_section = 'assumptions'
            continue
        elif 'limitation' in line.lower() or line.startswith('3.'):
            current_section = 'limitations'
            continue
        elif 'confidence' in line.lower() or line.startswith('4.'):
            current_section = 'confidence'
            continue
        elif 'next step' in line.lower() or line.startswith('5.'):
            current_section = 'next_steps'
            continue
        
        # Extract content based on current section
        if line and current_section:
            # Remove bullet points and numbering
            clean_line = line.lstrip('•-*').strip()
            if clean_line and not clean_line.endswith(':'):
                if current_section == 'insights':
                    key_insights.append(clean_line)
                elif current_section == 'assumptions':
                    assumptions.append(clean_line)
                elif current_section == 'limitations':
                    limitations.append(clean_line)
                elif current_section == 'confidence':
                    confidence += clean_line + " "
                elif current_section == 'next_steps':
                    next_steps.append(clean_line)
    
    return {
        'explanation': explanation,
        'keyInsights': key_insights[:5],  # Limit to 5
        'assumptions': assumptions[:5],
        'limitations': limitations[:5],
        'confidence': confidence.strip(),
        'nextSteps': next_steps[:5]
    }


def generate_forecast_explanation(
    user_id: str,
    forecast_data: Dict[str, Any],
    complexity: str = 'simple',
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate explanation for a demand forecast.
    
    Args:
        user_id: User identifier
        forecast_data: Forecast result data
        complexity: 'simple' or 'detailed'
        user_context: Optional user profile data
        
    Returns:
        ExplanationResponse dictionary
    """
    try:
        # Get user profile if not provided
        if not user_context:
            table = dynamodb.Table(USER_PROFILE_TABLE)
            try:
                response = table.get_item(Key={'userId': user_id})
                user_context = response.get('Item')
            except ClientError:
                user_context = None
        
        # Create prompt
        prompt = create_forecast_explanation_prompt(
            forecast_data=forecast_data,
            user_context=user_context,
            complexity=complexity
        )
        
        # Invoke Bedrock
        result = invoke_bedrock_model(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            temperature=0.7,
            max_tokens=1500
        )
        
        # Parse response
        parsed = parse_explanation_response(result['text'])
        
        # Add metadata
        parsed['metadata'] = {
            'generatedAt': datetime.utcnow().isoformat(),
            'context': 'forecast',
            'complexity': complexity,
            'modelId': result['model_id'],
            'usage': result.get('usage')
        }
        
        return parsed
        
    except VyaparSaathiError as e:
        return {
            'error': str(e),
            'errorType': e.error_type.value,
            'recoverable': e.recoverable,
            'explanation': 'Unable to generate explanation at this time. Please try again later.',
            'keyInsights': [],
            'assumptions': [],
            'limitations': [],
            'confidence': '',
            'nextSteps': []
        }
    except Exception as e:
        return {
            'error': str(e),
            'explanation': 'An error occurred while generating the explanation.',
            'keyInsights': [],
            'assumptions': [],
            'limitations': [],
            'confidence': '',
            'nextSteps': []
        }


def generate_risk_explanation(
    user_id: str,
    risk_data: Dict[str, Any],
    complexity: str = 'simple',
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate explanation for a risk assessment.
    
    Args:
        user_id: User identifier
        risk_data: Risk assessment data
        complexity: 'simple' or 'detailed'
        user_context: Optional user profile data
        
    Returns:
        ExplanationResponse dictionary
    """
    try:
        # Get user profile if not provided
        if not user_context:
            table = dynamodb.Table(USER_PROFILE_TABLE)
            try:
                response = table.get_item(Key={'userId': user_id})
                user_context = response.get('Item')
            except ClientError:
                user_context = None
        
        # Create prompt
        prompt = create_risk_explanation_prompt(
            risk_data=risk_data,
            user_context=user_context,
            complexity=complexity
        )
        
        # Invoke Bedrock
        result = invoke_bedrock_model(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            temperature=0.7,
            max_tokens=1500
        )
        
        # Parse response
        parsed = parse_explanation_response(result['text'])
        
        # Add metadata
        parsed['metadata'] = {
            'generatedAt': datetime.utcnow().isoformat(),
            'context': 'risk',
            'complexity': complexity,
            'modelId': result['model_id'],
            'usage': result.get('usage')
        }
        
        return parsed
        
    except VyaparSaathiError as e:
        return {
            'error': str(e),
            'errorType': e.error_type.value,
            'recoverable': e.recoverable,
            'explanation': 'Unable to generate explanation at this time. Please try again later.',
            'keyInsights': [],
            'assumptions': [],
            'limitations': [],
            'confidence': '',
            'nextSteps': []
        }
    except Exception as e:
        return {
            'error': str(e),
            'explanation': 'An error occurred while generating the explanation.',
            'keyInsights': [],
            'assumptions': [],
            'limitations': [],
            'confidence': '',
            'nextSteps': []
        }


def generate_recommendation_explanation(
    user_id: str,
    recommendation_data: Dict[str, Any],
    risk_data: Optional[Dict[str, Any]] = None,
    complexity: str = 'simple',
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate explanation for a reorder recommendation.
    
    Args:
        user_id: User identifier
        recommendation_data: Reorder recommendation data
        risk_data: Optional risk assessment data for context
        complexity: 'simple' or 'detailed'
        user_context: Optional user profile data
        
    Returns:
        ExplanationResponse dictionary
    """
    try:
        # Get user profile if not provided
        if not user_context:
            table = dynamodb.Table(USER_PROFILE_TABLE)
            try:
                response = table.get_item(Key={'userId': user_id})
                user_context = response.get('Item')
            except ClientError:
                user_context = None
        
        # Create prompt
        prompt = create_recommendation_explanation_prompt(
            recommendation_data=recommendation_data,
            risk_data=risk_data,
            user_context=user_context,
            complexity=complexity
        )
        
        # Invoke Bedrock
        result = invoke_bedrock_model(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            temperature=0.7,
            max_tokens=1500
        )
        
        # Parse response
        parsed = parse_explanation_response(result['text'])
        
        # Add metadata
        parsed['metadata'] = {
            'generatedAt': datetime.utcnow().isoformat(),
            'context': 'recommendation',
            'complexity': complexity,
            'modelId': result['model_id'],
            'usage': result.get('usage')
        }
        
        return parsed
        
    except VyaparSaathiError as e:
        return {
            'error': str(e),
            'errorType': e.error_type.value,
            'recoverable': e.recoverable,
            'explanation': 'Unable to generate explanation at this time. Please try again later.',
            'keyInsights': [],
            'assumptions': [],
            'limitations': [],
            'confidence': '',
            'nextSteps': []
        }
    except Exception as e:
        return {
            'error': str(e),
            'explanation': 'An error occurred while generating the explanation.',
            'keyInsights': [],
            'assumptions': [],
            'limitations': [],
            'confidence': '',
            'nextSteps': []
        }


def generate_conversational_response(
    user_id: str,
    user_query: str,
    conversation_history: Optional[List[Dict[str, str]]] = None,
    include_context: bool = True
) -> Dict[str, Any]:
    """
    Generate response for a conversational query.
    
    Args:
        user_id: User identifier
        user_query: User's question
        conversation_history: Optional previous conversation turns
        include_context: Whether to include forecast/risk context
        
    Returns:
        Response dictionary with answer and metadata
    """
    try:
        # Build context data if requested
        context_data = None
        if include_context:
            context_data = {}
            
            # Get user profile
            table = dynamodb.Table(USER_PROFILE_TABLE)
            try:
                response = table.get_item(Key={'userId': user_id})
                context_data['userProfile'] = response.get('Item')
            except ClientError:
                pass
            
            # Get recent forecasts (simplified - would need proper query in production)
            # For now, just indicate that context is available
            context_data['forecasts'] = []
            context_data['risks'] = []
        
        # Create prompt
        prompt = create_conversational_prompt(
            user_query=user_query,
            context_data=context_data,
            conversation_history=conversation_history
        )
        
        # Invoke Bedrock
        result = invoke_bedrock_model(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            temperature=0.8,  # Slightly higher for conversational
            max_tokens=1000
        )
        
        return {
            'answer': result['text'],
            'metadata': {
                'generatedAt': datetime.utcnow().isoformat(),
                'context': 'conversational',
                'modelId': result['model_id'],
                'usage': result.get('usage')
            }
        }
        
    except VyaparSaathiError as e:
        return {
            'error': str(e),
            'errorType': e.error_type.value,
            'recoverable': e.recoverable,
            'answer': 'I apologize, but I am unable to answer your question at this time. Please try again later.'
        }
    except Exception as e:
        return {
            'error': str(e),
            'answer': 'An error occurred while processing your question.'
        }


def generate_explanation(
    user_id: str,
    context: str,
    data: Dict[str, Any],
    user_query: Optional[str] = None,
    complexity: str = 'simple'
) -> Dict[str, Any]:
    """
    Main entry point for generating explanations.
    
    This function routes to the appropriate explanation generator based on context.
    
    Args:
        user_id: User identifier
        context: 'forecast', 'risk', 'recommendation', or 'conversational'
        data: Context-specific data (forecast, risk, recommendation, etc.)
        user_query: Optional user query for conversational context
        complexity: 'simple' or 'detailed'
        
    Returns:
        ExplanationResponse dictionary
    """
    if context == 'forecast':
        return generate_forecast_explanation(
            user_id=user_id,
            forecast_data=data,
            complexity=complexity
        )
    elif context == 'risk':
        return generate_risk_explanation(
            user_id=user_id,
            risk_data=data,
            complexity=complexity
        )
    elif context == 'recommendation':
        risk_data = data.get('riskAssessment')
        recommendation_data = data.get('recommendation', data)
        return generate_recommendation_explanation(
            user_id=user_id,
            recommendation_data=recommendation_data,
            risk_data=risk_data,
            complexity=complexity
        )
    elif context == 'conversational':
        return generate_conversational_response(
            user_id=user_id,
            user_query=user_query or data.get('query', ''),
            conversation_history=data.get('history')
        )
    else:
        return {
            'error': f'Unknown context: {context}',
            'explanation': 'Invalid explanation context specified.',
            'keyInsights': [],
            'assumptions': [],
            'limitations': [],
            'confidence': '',
            'nextSteps': []
        }

