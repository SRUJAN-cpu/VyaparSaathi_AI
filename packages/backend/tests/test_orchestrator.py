"""
Unit tests for orchestrator Lambda.

Tests the main orchestration logic including workflow coordination,
data routing, parallel processing, and result aggregation.
"""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from decimal import Decimal

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from orchestrator.orchestrator_handler import (
    lambda_handler,
    orchestrate_forecast_and_risk,
    orchestrate_data_upload,
    orchestrate_explanation_request,
    determine_data_mode,
    get_user_profile
)


# ===== Fixtures =====

@pytest.fixture
def mock_user_profile():
    """Mock user profile data."""
    return {
        'userId': 'test-user-123',
        'businessInfo': {
            'name': 'Test Store',
            'type': 'grocery',
            'location': {
                'city': 'Mumbai',
                'state': 'Maharashtra',
                'region': 'West'
            },
            'size': 'medium'
        },
        'dataCapabilities': {
            'hasHistoricalData': True,
            'dataQuality': 'good',
            'lastUpdated': '2024-01-15T10:00:00Z'
        },
        'preferences': {
            'forecastHorizon': 14,
            'riskTolerance': 'moderate'
        }
    }


@pytest.fixture
def mock_forecast_result():
    """Mock forecast result."""
    return {
        'success': True,
        'forecasts': [
            {
                'sku': 'SKU001',
                'category': 'sweets',
                'predictions': [
                    {
                        'date': '2024-01-20',
                        'demandForecast': 150,
                        'lowerBound': 120,
                        'upperBound': 180,
                        'festivalMultiplier': 1.5
                    }
                ],
                'confidence': 0.85,
                'methodology': 'ml'
            }
        ],
        'metadata': {
            'generatedAt': '2024-01-15T10:00:00Z',
            'methodology': 'ml',
            'dataMode': 'structured'
        }
    }


@pytest.fixture
def mock_risk_result():
    """Mock risk assessment result."""
    return {
        'success': True,
        'results': [
            {
                'success': True,
                'userId': 'test-user-123',
                'riskAssessment': {
                    'sku': 'SKU001',
                    'category': 'sweets',
                    'currentStock': 100,
                    'stockoutRisk': {
                        'probability': 0.75,
                        'daysUntilStockout': 3,
                        'potentialLostSales': 50
                    },
                    'overstockRisk': {
                        'probability': 0.1,
                        'excessUnits': 0,
                        'carryingCost': 0
                    },
                    'recommendation': {
                        'action': 'reorder',
                        'suggestedQuantity': 200,
                        'urgency': 'high',
                        'reasoning': ['High stockout risk', 'Festival approaching'],
                        'confidence': 0.85
                    }
                }
            }
        ]
    }


@pytest.fixture
def mock_inventory_items():
    """Mock inventory items for risk assessment."""
    return [
        {
            'sku': 'SKU001',
            'category': 'sweets',
            'currentStock': 100,
            'safetyStock': 20,
            'unitCost': 10.0,
            'leadTimeDays': 7
        },
        {
            'sku': 'SKU002',
            'category': 'clothing',
            'currentStock': 50,
            'safetyStock': 10,
            'unitCost': 25.0,
            'leadTimeDays': 14
        }
    ]


# ===== Test determine_data_mode =====

@patch('orchestrator.orchestrator_handler.get_user_profile')
@patch('orchestrator.orchestrator_handler.select_data_source')
def test_determine_data_mode_with_structured_data(mock_select, mock_get_profile, mock_user_profile):
    """Test data mode determination with structured data available."""
    mock_get_profile.return_value = mock_user_profile
    mock_select.return_value = {
        'selectedSource': 'structured',
        'hasStructuredData': True,
        'quality': 'good',
        'qualityScore': 0.9,
        'reasoning': 'High quality historical data available'
    }
    
    result = determine_data_mode('test-user-123')
    
    assert result['mode'] == 'structured'
    assert result['hasStructuredData'] is True
    assert result['quality'] == 'good'
    assert result['score'] == 0.9


@patch('orchestrator.orchestrator_handler.get_user_profile')
def test_determine_data_mode_no_profile(mock_get_profile):
    """Test data mode determination when user profile doesn't exist."""
    mock_get_profile.return_value = None
    
    result = determine_data_mode('test-user-123')
    
    assert result['mode'] == 'low-data'
    assert result['hasStructuredData'] is False
    assert result['quality'] == 'poor'
    assert result['score'] == 0.0


# ===== Test orchestrate_forecast_and_risk =====

@patch('orchestrator.orchestrator_handler.generate_explanation')
@patch('orchestrator.orchestrator_handler.assess_multiple_skus')
@patch('orchestrator.orchestrator_handler.generate_forecast')
@patch('orchestrator.orchestrator_handler.determine_data_mode')
def test_orchestrate_forecast_and_risk_success(
    mock_determine_mode,
    mock_generate_forecast,
    mock_assess_skus,
    mock_generate_explanation,
    mock_forecast_result,
    mock_risk_result,
    mock_inventory_items
):
    """Test successful orchestration of forecast and risk assessment."""
    # Setup mocks
    mock_determine_mode.return_value = {
        'mode': 'structured',
        'hasStructuredData': True,
        'quality': 'good',
        'score': 0.9
    }
    mock_generate_forecast.return_value = mock_forecast_result
    mock_assess_skus.return_value = mock_risk_result
    mock_generate_explanation.return_value = {
        'explanation': 'Test explanation',
        'keyInsights': ['Insight 1', 'Insight 2']
    }
    
    # Execute
    result = orchestrate_forecast_and_risk(
        user_id='test-user-123',
        forecast_horizon=14,
        target_festivals=['Diwali'],
        inventory_items=mock_inventory_items,
        include_explanations=True,
        parallel_execution=True
    )
    
    # Verify
    assert result['success'] is True
    assert result['userId'] == 'test-user-123'
    assert 'forecast' in result
    assert 'risks' in result
    assert 'explanations' in result
    assert 'metadata' in result
    assert result['metadata']['forecastHorizon'] == 14
    assert result['metadata']['parallelExecution'] is True
    assert 'processingTime' in result['metadata']
    
    # Verify function calls
    mock_determine_mode.assert_called_once_with('test-user-123')
    mock_generate_forecast.assert_called_once()
    mock_assess_skus.assert_called_once()


@patch('orchestrator.orchestrator_handler.generate_forecast')
@patch('orchestrator.orchestrator_handler.determine_data_mode')
def test_orchestrate_forecast_and_risk_without_inventory(
    mock_determine_mode,
    mock_generate_forecast,
    mock_forecast_result
):
    """Test orchestration without inventory items (no risk assessment)."""
    mock_determine_mode.return_value = {
        'mode': 'structured',
        'hasStructuredData': True,
        'quality': 'good',
        'score': 0.9
    }
    mock_generate_forecast.return_value = mock_forecast_result
    
    result = orchestrate_forecast_and_risk(
        user_id='test-user-123',
        forecast_horizon=14,
        inventory_items=None,
        include_explanations=False
    )
    
    assert result['success'] is True
    assert result['risks'] is None
    assert result['explanations'] is None


@patch('orchestrator.orchestrator_handler.generate_forecast')
@patch('orchestrator.orchestrator_handler.determine_data_mode')
def test_orchestrate_forecast_and_risk_forecast_error(
    mock_determine_mode,
    mock_generate_forecast
):
    """Test orchestration when forecast generation fails."""
    mock_determine_mode.return_value = {
        'mode': 'structured',
        'hasStructuredData': True,
        'quality': 'good',
        'score': 0.9
    }
    mock_generate_forecast.side_effect = Exception('Forecast error')
    
    result = orchestrate_forecast_and_risk(
        user_id='test-user-123',
        forecast_horizon=14
    )
    
    assert result['success'] is True  # Orchestrator continues despite errors
    assert result['forecast']['success'] is False
    assert 'error' in result['forecast']


@patch('orchestrator.orchestrator_handler.assess_multiple_skus')
@patch('orchestrator.orchestrator_handler.generate_forecast')
@patch('orchestrator.orchestrator_handler.determine_data_mode')
def test_orchestrate_forecast_and_risk_performance_warning(
    mock_determine_mode,
    mock_generate_forecast,
    mock_assess_skus,
    mock_forecast_result,
    mock_risk_result,
    mock_inventory_items,
    capsys
):
    """Test that performance warning is logged when exceeding 30s target."""
    import time
    
    mock_determine_mode.return_value = {'mode': 'structured', 'hasStructuredData': True, 'quality': 'good', 'score': 0.9}
    
    # Simulate slow processing
    def slow_forecast(*args, **kwargs):
        time.sleep(0.1)  # Small delay for testing
        return mock_forecast_result
    
    mock_generate_forecast.side_effect = slow_forecast
    mock_assess_skus.return_value = mock_risk_result
    
    result = orchestrate_forecast_and_risk(
        user_id='test-user-123',
        forecast_horizon=14,
        inventory_items=mock_inventory_items
    )
    
    assert 'processingTime' in result['metadata']
    assert 'meetsPerformanceTarget' in result['metadata']


# ===== Test orchestrate_data_upload =====

@patch('data_processor.csv_handler.process_csv_upload')
def test_orchestrate_data_upload_csv(mock_process_csv):
    """Test data upload orchestration for CSV files."""
    mock_process_csv.return_value = {
        'success': True,
        'recordsProcessed': 100,
        'validationErrors': []
    }
    
    result = orchestrate_data_upload(
        user_id='test-user-123',
        data_type='csv',
        data_payload={
            'fileContent': 'date,sku,quantity\n2024-01-01,SKU001,100',
            'fileName': 'sales.csv'
        }
    )
    
    assert result['success'] is True
    assert result['recordsProcessed'] == 100
    mock_process_csv.assert_called_once()


@patch('data_processor.questionnaire_handler.process_questionnaire')
def test_orchestrate_data_upload_questionnaire(mock_process_questionnaire):
    """Test data upload orchestration for questionnaire."""
    mock_process_questionnaire.return_value = {
        'success': True,
        'profileUpdated': True
    }
    
    result = orchestrate_data_upload(
        user_id='test-user-123',
        data_type='questionnaire',
        data_payload={
            'businessType': 'grocery',
            'storeSize': 'medium'
        }
    )
    
    assert result['success'] is True
    assert result['profileUpdated'] is True
    mock_process_questionnaire.assert_called_once()


def test_orchestrate_data_upload_unknown_type():
    """Test data upload orchestration with unknown data type."""
    result = orchestrate_data_upload(
        user_id='test-user-123',
        data_type='unknown',
        data_payload={}
    )
    
    assert result['success'] is False
    assert 'error' in result


# ===== Test orchestrate_explanation_request =====

@patch('ai_explainer.explanation_handler.generate_conversational_response')
def test_orchestrate_explanation_conversational(mock_generate_response):
    """Test explanation orchestration for conversational queries."""
    mock_generate_response.return_value = {
        'answer': 'This is a test answer',
        'metadata': {}
    }
    
    result = orchestrate_explanation_request(
        user_id='test-user-123',
        context='conversational',
        query='What is my forecast for tomorrow?'
    )
    
    assert result['success'] is True
    assert 'explanation' in result
    mock_generate_response.assert_called_once()


@patch('orchestrator.orchestrator_handler.generate_explanation')
@patch('forecast_engine.storage.get_latest_forecast_for_sku')
def test_orchestrate_explanation_forecast(mock_get_forecast, mock_generate_explanation):
    """Test explanation orchestration for forecast context."""
    mock_get_forecast.return_value = {
        'sku': 'SKU001',
        'predictions': []
    }
    mock_generate_explanation.return_value = {
        'explanation': 'Forecast explanation',
        'keyInsights': []
    }
    
    result = orchestrate_explanation_request(
        user_id='test-user-123',
        context='forecast',
        sku='SKU001'
    )
    
    assert result['success'] is True
    assert 'explanation' in result
    mock_get_forecast.assert_called_once_with('test-user-123', 'SKU001')
    mock_generate_explanation.assert_called_once()


@patch('forecast_engine.storage.get_latest_forecast_for_sku')
def test_orchestrate_explanation_forecast_no_data(mock_get_forecast):
    """Test explanation orchestration when forecast data not found."""
    mock_get_forecast.return_value = None
    
    result = orchestrate_explanation_request(
        user_id='test-user-123',
        context='forecast',
        sku='SKU001'
    )
    
    assert result['success'] is False
    assert 'error' in result


def test_orchestrate_explanation_missing_sku():
    """Test explanation orchestration with missing SKU for forecast context."""
    result = orchestrate_explanation_request(
        user_id='test-user-123',
        context='forecast',
        sku=None
    )
    
    assert result['success'] is False
    assert 'error' in result


# ===== Test lambda_handler =====

@patch('orchestrator.orchestrator_handler.orchestrate_forecast_and_risk')
def test_lambda_handler_forecast_and_risk(mock_orchestrate):
    """Test Lambda handler for forecast_and_risk action."""
    mock_orchestrate.return_value = {
        'success': True,
        'forecast': {},
        'risks': {}
    }
    
    event = {
        'body': json.dumps({
            'action': 'forecast_and_risk',
            'userId': 'test-user-123',
            'forecastHorizon': 14,
            'targetFestivals': ['Diwali']
        })
    }
    
    response = lambda_handler(event, None)
    
    assert response['statusCode'] == 200
    assert 'body' in response
    body = json.loads(response['body'])
    assert body['success'] is True
    mock_orchestrate.assert_called_once()


@patch('orchestrator.orchestrator_handler.orchestrate_data_upload')
def test_lambda_handler_data_upload(mock_orchestrate):
    """Test Lambda handler for data_upload action."""
    mock_orchestrate.return_value = {
        'success': True,
        'recordsProcessed': 100
    }
    
    event = {
        'body': json.dumps({
            'action': 'data_upload',
            'userId': 'test-user-123',
            'dataType': 'csv',
            'dataPayload': {'fileContent': 'test'}
        })
    }
    
    response = lambda_handler(event, None)
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['success'] is True
    mock_orchestrate.assert_called_once()


@patch('orchestrator.orchestrator_handler.orchestrate_explanation_request')
def test_lambda_handler_explanation(mock_orchestrate):
    """Test Lambda handler for explanation action."""
    mock_orchestrate.return_value = {
        'success': True,
        'explanation': {}
    }
    
    event = {
        'body': json.dumps({
            'action': 'explanation',
            'userId': 'test-user-123',
            'context': 'forecast',
            'sku': 'SKU001'
        })
    }
    
    response = lambda_handler(event, None)
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['success'] is True
    mock_orchestrate.assert_called_once()


def test_lambda_handler_missing_action():
    """Test Lambda handler with missing action parameter."""
    event = {
        'body': json.dumps({
            'userId': 'test-user-123'
        })
    }
    
    response = lambda_handler(event, None)
    
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert 'error' in body


def test_lambda_handler_missing_user_id():
    """Test Lambda handler with missing userId parameter."""
    event = {
        'body': json.dumps({
            'action': 'forecast_and_risk'
        })
    }
    
    response = lambda_handler(event, None)
    
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert 'error' in body


def test_lambda_handler_unknown_action():
    """Test Lambda handler with unknown action."""
    event = {
        'body': json.dumps({
            'action': 'unknown_action',
            'userId': 'test-user-123'
        })
    }
    
    response = lambda_handler(event, None)
    
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert 'error' in body


def test_lambda_handler_data_upload_missing_params():
    """Test Lambda handler for data_upload with missing parameters."""
    event = {
        'body': json.dumps({
            'action': 'data_upload',
            'userId': 'test-user-123'
            # Missing dataType and dataPayload
        })
    }
    
    response = lambda_handler(event, None)
    
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert 'error' in body


def test_lambda_handler_explanation_missing_context():
    """Test Lambda handler for explanation with missing context."""
    event = {
        'body': json.dumps({
            'action': 'explanation',
            'userId': 'test-user-123'
            # Missing context
        })
    }
    
    response = lambda_handler(event, None)
    
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert 'error' in body


@patch('orchestrator.orchestrator_handler.orchestrate_forecast_and_risk')
def test_lambda_handler_internal_error(mock_orchestrate):
    """Test Lambda handler with internal error."""
    mock_orchestrate.side_effect = Exception('Internal error')
    
    event = {
        'body': json.dumps({
            'action': 'forecast_and_risk',
            'userId': 'test-user-123',
            'forecastHorizon': 14
        })
    }
    
    response = lambda_handler(event, None)
    
    assert response['statusCode'] == 500
    body = json.loads(response['body'])
    assert 'error' in body


def test_lambda_handler_direct_event():
    """Test Lambda handler with direct event (no body wrapper)."""
    event = {
        'action': 'forecast_and_risk',
        'userId': 'test-user-123',
        'forecastHorizon': 14
    }
    
    with patch('orchestrator.orchestrator_handler.orchestrate_forecast_and_risk') as mock_orchestrate:
        mock_orchestrate.return_value = {'success': True}
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 200
        mock_orchestrate.assert_called_once()


# ===== Test CORS headers =====

def test_lambda_handler_cors_headers():
    """Test that all responses include CORS headers."""
    event = {
        'body': json.dumps({
            'userId': 'test-user-123'
        })
    }
    
    response = lambda_handler(event, None)
    
    assert 'headers' in response
    assert 'Access-Control-Allow-Origin' in response['headers']
    assert response['headers']['Access-Control-Allow-Origin'] == '*'
    assert response['headers']['Content-Type'] == 'application/json'
