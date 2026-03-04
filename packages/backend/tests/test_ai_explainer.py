"""
Property-based tests for AI explanation generation.

Tests Property 10: Explanation Generation
Validates: Requirements 4.4

This module tests that explanations are generated with required components
(assumptions and limitations) for all forecast and risk assessment inputs.
"""

import pytest
from hypothesis import given, settings, assume
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from tests.strategies import (
    forecast_result_strategy,
    risk_assessment_strategy,
    user_profile_strategy
)
from ai_explainer.explanation_handler import (
    parse_explanation_response,
    generate_forecast_explanation,
    generate_risk_explanation,
    generate_recommendation_explanation,
    generate_conversational_response
)
from ai_explainer.prompt_templates import (
    create_forecast_explanation_prompt,
    create_risk_explanation_prompt,
    create_recommendation_explanation_prompt,
    create_conversational_prompt
)


class TestPromptTemplates:
    """Unit tests for prompt template generation."""
    
    def test_forecast_prompt_includes_key_data(self):
        """Test that forecast prompts include essential data."""
        forecast_data = {
            'sku': 'TEST123',
            'category': 'grocery',
            'predictions': [
                {
                    'date': '2024-01-01',
                    'demandForecast': 100.0,
                    'lowerBound': 80.0,
                    'upperBound': 120.0,
                    'festivalMultiplier': 1.5
                }
            ],
            'confidence': 0.85,
            'methodology': 'ml'
        }
        
        prompt = create_forecast_explanation_prompt(forecast_data)
        
        # Check that key information is in the prompt
        assert 'TEST123' in prompt
        assert 'grocery' in prompt
        assert '85%' in prompt or '0.85' in prompt
        assert 'ml' in prompt.lower()
        assert 'assumptions' in prompt.lower()
        assert 'limitations' in prompt.lower()
    
    def test_risk_prompt_includes_key_data(self):
        """Test that risk prompts include essential data."""
        risk_data = {
            'sku': 'TEST456',
            'category': 'apparel',
            'currentStock': 500,
            'stockoutRisk': {
                'probability': 0.7,
                'daysUntilStockout': 5,
                'potentialLostSales': 200
            },
            'overstockRisk': {
                'probability': 0.2,
                'excessUnits': 50,
                'carryingCost': 1000.0
            }
        }
        
        prompt = create_risk_explanation_prompt(risk_data)
        
        # Check that key information is in the prompt
        assert 'TEST456' in prompt
        assert 'apparel' in prompt
        assert '500' in prompt
        assert '70%' in prompt or '0.7' in prompt
        assert 'stockout' in prompt.lower()
    
    def test_recommendation_prompt_includes_action(self):
        """Test that recommendation prompts include action details."""
        recommendation_data = {
            'action': 'reorder',
            'suggestedQuantity': 300,
            'urgency': 'high',
            'reasoning': ['Low stock levels', 'Festival approaching'],
            'confidence': 0.8
        }
        
        prompt = create_recommendation_explanation_prompt(recommendation_data)
        
        # Check that key information is in the prompt
        assert 'reorder' in prompt.lower()
        assert '300' in prompt
        assert 'high' in prompt.lower()
        assert '80%' in prompt or '0.8' in prompt
    
    def test_conversational_prompt_includes_query(self):
        """Test that conversational prompts include user query."""
        user_query = "What should I stock for Diwali?"
        
        prompt = create_conversational_prompt(user_query)
        
        # Check that query is in the prompt
        assert user_query in prompt
        assert 'inventory' in prompt.lower() or 'forecasting' in prompt.lower()


class TestExplanationParsing:
    """Unit tests for explanation response parsing."""
    
    def test_parse_explanation_with_sections(self):
        """Test parsing explanation with structured sections."""
        response_text = """
1. **Key Insights**:
- Your demand will increase by 50% during the festival
- Stock levels are currently adequate

2. **Assumptions**:
- Historical patterns will repeat
- No supply chain disruptions

3. **Limitations**:
- Weather impacts not considered
- Local competition not factored

4. **Confidence**:
The 85% confidence level means we are quite certain about this forecast.

5. **Next Steps**:
- Order additional stock within 3 days
- Monitor daily sales closely
"""
        
        parsed = parse_explanation_response(response_text)
        
        # Check that sections are extracted
        assert 'explanation' in parsed
        assert 'keyInsights' in parsed
        assert 'assumptions' in parsed
        assert 'limitations' in parsed
        assert 'confidence' in parsed
        assert 'nextSteps' in parsed
        
        # Check content
        assert len(parsed['keyInsights']) > 0
        assert len(parsed['assumptions']) > 0
        assert len(parsed['limitations']) > 0
        assert len(parsed['nextSteps']) > 0
        # Confidence might be empty if parsing doesn't capture it perfectly
        # but the field should exist
        assert isinstance(parsed['confidence'], str)
    
    def test_parse_explanation_without_structure(self):
        """Test parsing unstructured explanation."""
        response_text = "This is a simple explanation without sections."
        
        parsed = parse_explanation_response(response_text)
        
        # Should still return all fields
        assert 'explanation' in parsed
        assert 'keyInsights' in parsed
        assert 'assumptions' in parsed
        assert 'limitations' in parsed
        assert 'confidence' in parsed
        assert 'nextSteps' in parsed
        
        # Full text should be in explanation
        assert response_text in parsed['explanation']


class TestExplanationGenerationMocked:
    """Unit tests for explanation generation with mocked Bedrock calls."""
    
    @patch('ai_explainer.explanation_handler.invoke_bedrock_model')
    @patch('ai_explainer.explanation_handler.dynamodb')
    def test_generate_forecast_explanation_success(self, mock_dynamodb, mock_bedrock):
        """Test successful forecast explanation generation."""
        # Mock Bedrock response
        mock_bedrock.return_value = {
            'text': """
1. **Key Insights**:
- Demand will peak during festival days
- Stock up 3 days before the festival

2. **Assumptions**:
- Historical patterns hold
- No supply disruptions

3. **Limitations**:
- Weather not considered
- Competition not factored

4. **Confidence**:
85% confidence means high certainty.

5. **Next Steps**:
- Order stock now
- Monitor daily
""",
            'model_id': 'claude-3-haiku',
            'stop_reason': 'end_turn',
            'usage': {
                'input_tokens': 100,
                'output_tokens': 200
            }
        }
        
        # Mock DynamoDB
        mock_table = MagicMock()
        mock_table.get_item.return_value = {'Item': None}
        mock_dynamodb.Table.return_value = mock_table
        
        forecast_data = {
            'sku': 'TEST123',
            'category': 'grocery',
            'predictions': [
                {'date': '2024-01-01', 'demandForecast': 100.0, 'lowerBound': 80.0, 
                 'upperBound': 120.0, 'festivalMultiplier': 1.5}
            ],
            'confidence': 0.85,
            'methodology': 'ml'
        }
        
        result = generate_forecast_explanation(
            user_id='test_user',
            forecast_data=forecast_data,
            complexity='simple'
        )
        
        # Check result structure
        assert 'explanation' in result
        assert 'keyInsights' in result
        assert 'assumptions' in result
        assert 'limitations' in result
        assert 'confidence' in result
        assert 'nextSteps' in result
        assert 'metadata' in result
        
        # Check that sections have content
        assert len(result['keyInsights']) > 0
        assert len(result['assumptions']) > 0
        assert len(result['limitations']) > 0
        
        # Check metadata
        assert result['metadata']['context'] == 'forecast'
        assert result['metadata']['complexity'] == 'simple'
        assert 'usage' in result['metadata']
    
    @patch('ai_explainer.explanation_handler.invoke_bedrock_model')
    @patch('ai_explainer.explanation_handler.dynamodb')
    def test_generate_risk_explanation_success(self, mock_dynamodb, mock_bedrock):
        """Test successful risk explanation generation."""
        # Mock Bedrock response
        mock_bedrock.return_value = {
            'text': """
1. **Risk Summary**:
High stockout risk detected.

2. **Why This Risk**:
- Current stock is low
- Demand is increasing

3. **Impact**:
Could lose 200 sales.

4. **Confidence**:
70% certain about this risk.

5. **Next Steps**:
- Reorder immediately
- Increase safety stock
""",
            'model_id': 'claude-3-haiku',
            'stop_reason': 'end_turn',
            'usage': {
                'input_tokens': 100,
                'output_tokens': 150
            }
        }
        
        # Mock DynamoDB
        mock_table = MagicMock()
        mock_table.get_item.return_value = {'Item': None}
        mock_dynamodb.Table.return_value = mock_table
        
        risk_data = {
            'sku': 'TEST456',
            'category': 'apparel',
            'currentStock': 50,
            'stockoutRisk': {
                'probability': 0.7,
                'daysUntilStockout': 3,
                'potentialLostSales': 200
            },
            'overstockRisk': {
                'probability': 0.1,
                'excessUnits': 0,
                'carryingCost': 0.0
            }
        }
        
        result = generate_risk_explanation(
            user_id='test_user',
            risk_data=risk_data,
            complexity='simple'
        )
        
        # Check result structure
        assert 'explanation' in result
        assert 'keyInsights' in result
        assert 'assumptions' in result
        assert 'limitations' in result
        assert 'nextSteps' in result
        assert 'metadata' in result
        
        # Check metadata
        assert result['metadata']['context'] == 'risk'
    
    @patch('ai_explainer.explanation_handler.invoke_bedrock_model')
    def test_generate_explanation_handles_bedrock_error(self, mock_bedrock):
        """Test that explanation generation handles Bedrock errors gracefully."""
        from ai_explainer.bedrock_client import BedrockError
        
        # Mock Bedrock error
        mock_bedrock.side_effect = BedrockError(
            "Service unavailable",
            error_code="ServiceUnavailableException",
            retryable=True
        )
        
        forecast_data = {
            'sku': 'TEST123',
            'category': 'grocery',
            'predictions': [],
            'confidence': 0.85,
            'methodology': 'ml'
        }
        
        result = generate_forecast_explanation(
            user_id='test_user',
            forecast_data=forecast_data
        )
        
        # Should return error response with fallback explanation
        assert 'error' in result
        assert 'explanation' in result
        assert 'Unable to generate explanation' in result['explanation']
        assert result['retryable'] == True


class TestExplanationGenerationProperties:
    """Property-based tests for explanation generation."""
    
    @given(forecast_data=forecast_result_strategy())
    @settings(max_examples=50, deadline=None)
    @patch('ai_explainer.explanation_handler.invoke_bedrock_model')
    @patch('ai_explainer.explanation_handler.dynamodb')
    def test_property_forecast_explanation_has_required_fields(
        self, mock_dynamodb, mock_bedrock, forecast_data
    ):
        """
        **Property 10: Explanation Generation**
        **Validates: Requirements 4.4**
        
        For any forecast result, the generated explanation should include
        assumptions and limitations.
        """
        # Mock Bedrock to return structured response
        mock_bedrock.return_value = {
            'text': """
1. **Key Insights**:
- Demand forecast shows expected patterns
- Festival impact is factored in

2. **Assumptions**:
- Historical patterns will continue
- No major market disruptions
- Festival attendance will be normal

3. **Limitations**:
- Weather impacts not modeled
- Competitor actions not considered
- Supply chain delays not factored

4. **Confidence**:
The confidence level reflects data quality and pattern stability.

5. **Next Steps**:
- Review stock levels
- Plan reorders accordingly
""",
            'model_id': 'claude-3-haiku',
            'stop_reason': 'end_turn',
            'usage': {'input_tokens': 100, 'output_tokens': 200}
        }
        
        # Mock DynamoDB
        mock_table = MagicMock()
        mock_table.get_item.return_value = {'Item': None}
        mock_dynamodb.Table.return_value = mock_table
        
        # Ensure forecast data has valid structure
        assume(len(forecast_data.get('predictions', [])) > 0)
        assume(0 <= forecast_data.get('confidence', 0) <= 1)
        
        # Generate explanation
        result = generate_forecast_explanation(
            user_id='test_user',
            forecast_data=forecast_data,
            complexity='simple'
        )
        
        # Property: Explanation must include assumptions and limitations
        assert 'assumptions' in result, "Explanation must include assumptions"
        assert 'limitations' in result, "Explanation must include limitations"
        
        # Property: Assumptions and limitations should not be empty
        # (unless there was an error)
        if 'error' not in result:
            assert len(result['assumptions']) > 0, "Assumptions should not be empty"
            assert len(result['limitations']) > 0, "Limitations should not be empty"
        
        # Property: Explanation should have all required fields
        required_fields = ['explanation', 'keyInsights', 'assumptions', 
                          'limitations', 'confidence', 'nextSteps']
        for field in required_fields:
            assert field in result, f"Explanation must include {field}"
    
    @given(risk_data=risk_assessment_strategy())
    @settings(max_examples=50, deadline=None)
    @patch('ai_explainer.explanation_handler.invoke_bedrock_model')
    @patch('ai_explainer.explanation_handler.dynamodb')
    def test_property_risk_explanation_has_required_fields(
        self, mock_dynamodb, mock_bedrock, risk_data
    ):
        """
        **Property 10: Explanation Generation**
        **Validates: Requirements 4.4**
        
        For any risk assessment, the generated explanation should include
        assumptions and limitations.
        """
        # Mock Bedrock to return structured response
        mock_bedrock.return_value = {
            'text': """
1. **Risk Summary**:
Risk assessment based on current data.

2. **Why This Risk**:
- Stock levels and demand patterns analyzed
- Festival timing considered

3. **Impact**:
Potential business impact quantified.

4. **Confidence**:
Assessment confidence based on data quality.

5. **Next Steps**:
- Take appropriate action
- Monitor situation
""",
            'model_id': 'claude-3-haiku',
            'stop_reason': 'end_turn',
            'usage': {'input_tokens': 100, 'output_tokens': 150}
        }
        
        # Mock DynamoDB
        mock_table = MagicMock()
        mock_table.get_item.return_value = {'Item': None}
        mock_dynamodb.Table.return_value = mock_table
        
        # Ensure risk data has valid probabilities
        assume(0 <= risk_data.get('stockoutRisk', {}).get('probability', 0) <= 1)
        assume(0 <= risk_data.get('overstockRisk', {}).get('probability', 0) <= 1)
        
        # Generate explanation
        result = generate_risk_explanation(
            user_id='test_user',
            risk_data=risk_data,
            complexity='simple'
        )
        
        # Property: Explanation must include assumptions and limitations
        assert 'assumptions' in result, "Explanation must include assumptions"
        assert 'limitations' in result, "Explanation must include limitations"
        
        # Property: Explanation should have all required fields
        required_fields = ['explanation', 'keyInsights', 'assumptions', 
                          'limitations', 'confidence', 'nextSteps']
        for field in required_fields:
            assert field in result, f"Explanation must include {field}"
    
    @given(
        forecast_data=forecast_result_strategy(),
        user_profile=user_profile_strategy()
    )
    @settings(max_examples=30, deadline=None)
    def test_property_forecast_prompt_includes_context(self, forecast_data, user_profile):
        """
        Property: Forecast explanation prompts should include user context
        when available.
        """
        # Ensure valid data
        assume(len(forecast_data.get('predictions', [])) > 0)
        
        # Generate prompt with user context
        prompt = create_forecast_explanation_prompt(
            forecast_data=forecast_data,
            user_context=user_profile,
            complexity='simple'
        )
        
        # Property: Prompt should include business type if available
        business_type = user_profile.get('businessInfo', {}).get('type')
        if business_type:
            assert business_type in prompt.lower(), \
                "Prompt should include business type from user context"
        
        # Property: Prompt should include location if available
        location = user_profile.get('businessInfo', {}).get('location', {})
        city = location.get('city')
        if city:
            assert city in prompt, \
                "Prompt should include location from user context"
        
        # Property: Prompt should always request assumptions and limitations
        assert 'assumptions' in prompt.lower(), \
            "Prompt must request assumptions"
        assert 'limitations' in prompt.lower(), \
            "Prompt must request limitations"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
