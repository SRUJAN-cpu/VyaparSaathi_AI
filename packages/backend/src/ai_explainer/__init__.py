"""
AI Explainer Component

This module provides natural language explanations for forecasts, risk assessments,
and conversational queries using Amazon Bedrock.
"""

from .bedrock_client import invoke_bedrock_model, BedrockError
from .prompt_templates import (
    create_forecast_explanation_prompt,
    create_risk_explanation_prompt,
    create_recommendation_explanation_prompt,
    create_conversational_prompt
)
from .explanation_handler import (
    generate_explanation,
    generate_forecast_explanation,
    generate_risk_explanation,
    generate_conversational_response
)

__all__ = [
    'invoke_bedrock_model',
    'BedrockError',
    'create_forecast_explanation_prompt',
    'create_risk_explanation_prompt',
    'create_recommendation_explanation_prompt',
    'create_conversational_prompt',
    'generate_explanation',
    'generate_forecast_explanation',
    'generate_risk_explanation',
    'generate_conversational_response'
]
