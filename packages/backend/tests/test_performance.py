"""
Property-based tests for performance requirements

Tests that the VyaparSaathi system generates forecasts and risk assessments
within the required 30-second time limit for various valid inputs.

**Validates: Requirements 6.1**
"""

import pytest
import time
import sys
import os
from datetime import datetime, timedelta
from hypothesis import given, settings, strategies as st
from typing import Dict, Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from forecast_engine.forecast_handler import generate_forecast
from risk_assessor.risk_handler import assess_inventory_risk, assess_multiple_skus
from tests.strategies import (
    forecast_request_strategy,
    inventory_data_strategy,
    festival_event_strategy,
    user_profile_strategy
)


# Performance threshold from requirements
PERFORMANCE_THRESHOLD_SECONDS = 30.0


@given(
    forecast_horizon=st.integers(min_value=7, max_value=14),
    data_mode=st.sampled_from(["structured", "low-data"]),
    num_festivals=st.integers(min_value=0, max_value=3),
    num_categories=st.integers(min_value=1, max_value=5)
)
@settings(max_examples=50, deadline=None)
def test_forecast_generation_performance(
    forecast_horizon: int,
    data_mode: str,
    num_festivals: int,
    num_categories: int
):
    """
    Property 11: Performance Requirements
    
    **Validates: Requirements 6.1**
    
    For any valid forecast request with varying horizons, data modes, festivals,
    and categories, the system should generate forecasts within 30 seconds.
    
    This test validates that forecast generation meets performance requirements
    across different input configurations.
    """
    # Generate test user ID
    user_id = f"perf_test_user_{int(time.time() * 1000)}"
    
    # Generate festival list
    target_festivals = []
    if num_festivals > 0:
        festival_names = ["Diwali", "Eid", "Holi", "Christmas", "Pongal"]
        target_festivals = festival_names[:num_festivals]
    
    # Generate category list
    categories = ["grocery", "apparel", "electronics", "home", "beauty"][:num_categories]
    
    # Measure execution time
    start_time = time.time()
    
    try:
        # Generate forecast
        result = generate_forecast(
            user_id=user_id,
            forecast_horizon=forecast_horizon,
            target_festivals=target_festivals if target_festivals else None,
            data_mode=data_mode,
            confidence_threshold=0.5,
            categories=categories
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Assert performance requirement
        assert execution_time < PERFORMANCE_THRESHOLD_SECONDS, (
            f"Forecast generation took {execution_time:.2f}s, "
            f"exceeding {PERFORMANCE_THRESHOLD_SECONDS}s threshold. "
            f"Config: horizon={forecast_horizon}, mode={data_mode}, "
            f"festivals={num_festivals}, categories={num_categories}"
        )
        
        # Verify result structure
        assert 'forecasts' in result or 'summary' in result, (
            "Result should contain forecasts or summary"
        )
        assert 'metadata' in result, "Result should contain metadata"
        
    except Exception as e:
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Even if there's an error, check if it happened within time limit
        assert execution_time < PERFORMANCE_THRESHOLD_SECONDS, (
            f"Forecast generation failed after {execution_time:.2f}s, "
            f"exceeding {PERFORMANCE_THRESHOLD_SECONDS}s threshold. Error: {str(e)}"
        )
        
        # Re-raise the exception for proper error reporting
        raise


@given(
    num_skus=st.integers(min_value=1, max_value=10),
    stock_level=st.integers(min_value=0, max_value=10000),
    forecast_horizon=st.integers(min_value=7, max_value=14)
)
@settings(max_examples=50, deadline=None)
def test_risk_assessment_performance(
    num_skus: int,
    stock_level: int,
    forecast_horizon: int
):
    """
    Property 11: Performance Requirements (Risk Assessment)
    
    **Validates: Requirements 6.1**
    
    For any valid risk assessment request with varying numbers of SKUs,
    stock levels, and forecast horizons, the system should generate
    risk assessments within 30 seconds.
    
    This test validates that risk assessment meets performance requirements
    across different input configurations.
    """
    # Generate test user ID
    user_id = f"perf_test_user_{int(time.time() * 1000)}"
    
    # Generate inventory data for multiple SKUs
    inventory_items = []
    for i in range(num_skus):
        inventory_items.append({
            'sku': f"SKU{i:04d}",
            'category': ['grocery', 'apparel', 'electronics'][i % 3],
            'currentStock': stock_level + (i * 10),
            'reorderPoint': max(10, stock_level // 4),
            'leadTimeDays': 7
        })
    
    # Generate mock forecast data
    forecast_data = []
    start_date = datetime.utcnow().date()
    for item in inventory_items:
        predictions = []
        for day in range(forecast_horizon):
            date = start_date + timedelta(days=day)
            predictions.append({
                'date': date.isoformat(),
                'demandForecast': 50.0 + (day * 5),
                'lowerBound': 40.0 + (day * 4),
                'upperBound': 60.0 + (day * 6),
                'confidence': 0.75
            })
        
        forecast_data.append({
            'sku': item['sku'],
            'category': item['category'],
            'predictions': predictions,
            'confidence': 0.75,
            'methodology': 'pattern'
        })
    
    # Measure execution time
    start_time = time.time()
    
    try:
        # Assess risk for multiple SKUs
        result = assess_multiple_skus(
            user_id=user_id,
            inventory_items=inventory_items,
            forecast_data=forecast_data
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Assert performance requirement
        assert execution_time < PERFORMANCE_THRESHOLD_SECONDS, (
            f"Risk assessment took {execution_time:.2f}s, "
            f"exceeding {PERFORMANCE_THRESHOLD_SECONDS}s threshold. "
            f"Config: skus={num_skus}, stock={stock_level}, horizon={forecast_horizon}"
        )
        
        # Verify result structure
        assert 'assessments' in result, "Result should contain assessments"
        assert len(result['assessments']) == num_skus, (
            f"Should have {num_skus} assessments, got {len(result['assessments'])}"
        )
        
    except Exception as e:
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Even if there's an error, check if it happened within time limit
        assert execution_time < PERFORMANCE_THRESHOLD_SECONDS, (
            f"Risk assessment failed after {execution_time:.2f}s, "
            f"exceeding {PERFORMANCE_THRESHOLD_SECONDS}s threshold. Error: {str(e)}"
        )
        
        # Re-raise the exception for proper error reporting
        raise


@given(
    forecast_horizon=st.integers(min_value=7, max_value=14),
    data_mode=st.sampled_from(["structured", "low-data"]),
    num_skus=st.integers(min_value=1, max_value=5)
)
@settings(max_examples=30, deadline=None)
def test_combined_forecast_and_risk_performance(
    forecast_horizon: int,
    data_mode: str,
    num_skus: int
):
    """
    Property 11: Performance Requirements (Combined Operations)
    
    **Validates: Requirements 6.1**
    
    For any valid user input requiring both forecast generation and risk assessment,
    the combined operation should complete within 30 seconds.
    
    This test validates end-to-end performance when both forecasting and risk
    assessment are performed together, as would happen in typical user workflows.
    """
    # Generate test user ID
    user_id = f"perf_test_user_{int(time.time() * 1000)}"
    
    # Generate categories
    categories = ["grocery", "apparel", "electronics"][:num_skus]
    
    # Measure execution time for combined operations
    start_time = time.time()
    
    try:
        # Step 1: Generate forecast
        forecast_result = generate_forecast(
            user_id=user_id,
            forecast_horizon=forecast_horizon,
            data_mode=data_mode,
            confidence_threshold=0.5,
            categories=categories
        )
        
        # Step 2: Generate inventory data based on forecast
        inventory_items = []
        forecast_data = forecast_result.get('forecasts', [])
        
        for i, forecast in enumerate(forecast_data[:num_skus]):
            inventory_items.append({
                'sku': forecast.get('sku', f"SKU{i:04d}"),
                'category': forecast.get('category', 'general'),
                'currentStock': 500,
                'reorderPoint': 100,
                'leadTimeDays': 7
            })
        
        # Step 3: Assess risk using forecast data
        if inventory_items and forecast_data:
            risk_result = assess_multiple_skus(
                user_id=user_id,
                inventory_items=inventory_items,
                forecast_data=forecast_data
            )
        else:
            risk_result = {'assessments': []}
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Assert performance requirement for combined operations
        assert execution_time < PERFORMANCE_THRESHOLD_SECONDS, (
            f"Combined forecast and risk assessment took {execution_time:.2f}s, "
            f"exceeding {PERFORMANCE_THRESHOLD_SECONDS}s threshold. "
            f"Config: horizon={forecast_horizon}, mode={data_mode}, skus={num_skus}"
        )
        
        # Verify both operations completed successfully
        assert 'forecasts' in forecast_result or 'summary' in forecast_result, (
            "Forecast result should contain forecasts or summary"
        )
        assert 'assessments' in risk_result, (
            "Risk result should contain assessments"
        )
        
    except Exception as e:
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Even if there's an error, check if it happened within time limit
        assert execution_time < PERFORMANCE_THRESHOLD_SECONDS, (
            f"Combined operations failed after {execution_time:.2f}s, "
            f"exceeding {PERFORMANCE_THRESHOLD_SECONDS}s threshold. Error: {str(e)}"
        )
        
        # Re-raise the exception for proper error reporting
        raise


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
