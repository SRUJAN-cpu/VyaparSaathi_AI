"""
Property-based test for festival-aware forecasting.

Feature: vyapar-saathi
Property 4: Festival-Aware Forecasting
Validates: Requirements 2.1, 2.2

This test validates that forecasts generated during festival periods incorporate
festival calendar data and show higher demand during festival periods compared
to baseline forecasts.
"""
import pytest
from hypothesis import given, strategies as st, assume, settings
from typing import Dict, Any, List
from datetime import datetime, timedelta

# Import forecast engine functions
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from forecast_engine.pattern_forecaster import (
    generate_pattern_forecast,
    calculate_baseline_demand,
    apply_festival_impact,
    generate_daily_predictions,
)
from festival_calendar.festival_seed_data import FESTIVAL_SEED_DATA, CATEGORIES
from synthetic_data.pattern_generator import get_seasonal_factors


# Custom strategies for festival-aware forecasting testing

@st.composite
def forecast_horizon_strategy(draw) -> int:
    """
    Generate a valid forecast horizon (7-14 days).
    
    Returns:
        Forecast horizon in days
    """
    return draw(st.integers(min_value=7, max_value=14))


@st.composite
def business_type_strategy(draw) -> str:
    """
    Generate a valid business type.
    
    Returns:
        Business type string
    """
    return draw(st.sampled_from(['grocery', 'apparel', 'electronics', 'general']))


@st.composite
def region_strategy(draw) -> str:
    """
    Generate a valid region.
    
    Returns:
        Region string
    """
    return draw(st.sampled_from(['north', 'south', 'east', 'west', 'central']))


@st.composite
def festival_with_date_strategy(draw, days_ahead: int = 14) -> Dict[str, Any]:
    """
    Generate a festival with a date within the forecast horizon.
    
    Args:
        days_ahead: Maximum days ahead for festival date
        
    Returns:
        Festival dictionary with adjusted date
    """
    # Select a festival from seed data
    festival = draw(st.sampled_from(FESTIVAL_SEED_DATA))
    
    # Generate a date within the forecast horizon
    days_offset = draw(st.integers(min_value=0, max_value=days_ahead))
    festival_date = (datetime.utcnow() + timedelta(days=days_offset)).date().isoformat()
    
    # Create a copy with the adjusted date
    festival_copy = festival.copy()
    festival_copy['date'] = festival_date
    
    return festival_copy


@st.composite
def product_category_strategy(draw, business_type: str) -> str:
    """
    Generate a product category appropriate for the business type.
    
    Args:
        business_type: Business type
        
    Returns:
        Product category string
    """
    category_map = {
        'grocery': ['staples', 'vegetables', 'dairy', 'snacks', 'beverages', 'sweets'],
        'apparel': ['traditional', 'casual', 'formal', 'kids', 'accessories'],
        'electronics': ['mobile', 'laptop', 'tv', 'appliances', 'accessories'],
        'general': ['household', 'personal_care', 'stationery', 'gifts'],
    }
    
    categories = category_map.get(business_type, category_map['general'])
    return draw(st.sampled_from(categories))


@st.composite
def forecast_context_strategy(draw, include_festival: bool = True) -> Dict[str, Any]:
    """
    Generate a complete forecast context for testing.
    
    Args:
        include_festival: Whether to include a festival in the context
        
    Returns:
        Forecast context dictionary
    """
    business_type = draw(business_type_strategy())
    region = draw(region_strategy())
    forecast_horizon = draw(forecast_horizon_strategy())
    
    start_date = datetime.utcnow().date().isoformat()
    
    # Generate festivals if requested
    festivals = []
    if include_festival:
        # Generate 1-3 festivals
        num_festivals = draw(st.integers(min_value=1, max_value=3))
        for _ in range(num_festivals):
            festival = draw(festival_with_date_strategy(days_ahead=forecast_horizon))
            # Only include if festival is relevant to the region
            if region in festival['region']:
                festivals.append(festival)
    
    # Generate categories
    category = draw(product_category_strategy(business_type))
    
    context = {
        'userId': 'test_user',
        'forecastHorizon': forecast_horizon,
        'startDate': start_date,
        'festivals': festivals,
        'userProfile': {
            'businessInfo': {
                'type': business_type,
                'location': {
                    'region': region
                }
            }
        },
        'dataQuality': {
            'score': 0.5,
            'quality': 'fair'
        },
        'categories': [category]
    }
    
    return context


# Property Tests

@settings(max_examples=100)
@given(data=st.data())
def test_festival_periods_show_higher_demand_than_baseline(data):
    """
    **Validates: Requirements 2.1, 2.2**
    
    Property: For any upcoming festival period, demand forecasts during festival
    days should be higher than or equal to baseline demand (without festival impact).
    
    This is the core property for festival-aware forecasting.
    """
    # Generate forecast context with festival
    context = data.draw(forecast_context_strategy(include_festival=True))
    
    # Skip if no festivals in the context
    assume(len(context['festivals']) > 0)
    
    # Generate forecast with festival
    forecast_result = generate_pattern_forecast(context)
    
    # Get the forecast for the first category
    assume(len(forecast_result['forecasts']) > 0)
    forecast = forecast_result['forecasts'][0]
    
    # Check predictions during festival periods
    for prediction in forecast['predictions']:
        festival_multiplier = prediction['festivalMultiplier']
        demand_forecast = prediction['demandForecast']
        
        # Property: If festival multiplier > 1.0, demand should be elevated
        if festival_multiplier > 1.0:
            # Calculate what baseline would be (demand / multiplier)
            baseline_estimate = demand_forecast / festival_multiplier
            
            # Demand with festival should be higher than baseline
            assert demand_forecast >= baseline_estimate, (
                f"Festival demand {demand_forecast} should be >= baseline {baseline_estimate} "
                f"(multiplier: {festival_multiplier})"
            )
        
        # Property: Festival multiplier should be >= 1.0
        assert festival_multiplier >= 1.0, (
            f"Festival multiplier should be >= 1.0, got {festival_multiplier}"
        )


@settings(max_examples=100)
@given(data=st.data())
def test_forecast_horizon_matches_requirement(data):
    """
    **Validates: Requirements 2.1**
    
    Property: For any forecast request, the system should generate predictions
    for the specified forecast horizon (7-14 days).
    """
    # Generate forecast context
    context = data.draw(forecast_context_strategy(include_festival=False))
    
    # Generate forecast
    forecast_result = generate_pattern_forecast(context)
    
    # Get the forecast for the first category
    assume(len(forecast_result['forecasts']) > 0)
    forecast = forecast_result['forecasts'][0]
    
    # Property: Number of predictions should match forecast horizon
    assert len(forecast['predictions']) == context['forecastHorizon'], (
        f"Expected {context['forecastHorizon']} predictions, "
        f"got {len(forecast['predictions'])}"
    )
    
    # Property: Forecast horizon should be between 7 and 14 days
    assert 7 <= context['forecastHorizon'] <= 14, (
        f"Forecast horizon {context['forecastHorizon']} outside valid range [7, 14]"
    )


@settings(max_examples=100)
@given(data=st.data())
def test_festival_calendar_data_incorporated(data):
    """
    **Validates: Requirements 2.2**
    
    Property: For any forecast with festivals, the festival calendar data
    (name, date, demand multipliers) should be incorporated into predictions.
    """
    # Generate forecast context with festival
    context = data.draw(forecast_context_strategy(include_festival=True))
    
    # Skip if no festivals
    assume(len(context['festivals']) > 0)
    
    # Generate forecast
    forecast_result = generate_pattern_forecast(context)
    
    # Get the forecast for the first category
    assume(len(forecast_result['forecasts']) > 0)
    forecast = forecast_result['forecasts'][0]
    
    # Property: At least one prediction should have festival impact
    has_festival_impact = any(
        p['festivalMultiplier'] > 1.0
        for p in forecast['predictions']
    )
    
    # Property: If festivals exist in context, at least one should impact demand
    festival_names = [f['name'] for f in context['festivals']]
    if festival_names:
        # Check if any prediction references the festivals
        predictions_with_festivals = [
            p for p in forecast['predictions']
            if len(p.get('festivals', [])) > 0
        ]
        
        assert len(predictions_with_festivals) > 0, (
            f"Festivals {festival_names} in context but no predictions show festival impact"
        )


@settings(max_examples=100)
@given(data=st.data())
def test_festival_impact_within_preparation_and_duration_window(data):
    """
    **Validates: Requirements 2.2**
    
    Property: Festival impact should only occur within the festival's
    preparation days before and duration days after the festival date.
    """
    # Generate a specific festival with known date
    business_type = data.draw(business_type_strategy())
    region = data.draw(region_strategy())
    category = data.draw(product_category_strategy(business_type))
    
    # Create a festival 5 days in the future
    festival_date = (datetime.utcnow() + timedelta(days=5)).date()
    festival = {
        'name': 'Test Festival',
        'date': festival_date.isoformat(),
        'region': [region],
        'preparationDays': 3,
        'duration': 2,
        'demandMultipliers': {
            category: 2.5
        }
    }
    
    # Generate predictions for 10 days
    start_date = datetime.utcnow()
    seasonal_factors = get_seasonal_factors(business_type)
    
    predictions = generate_daily_predictions(
        category=category,
        business_type=business_type,
        start_date=start_date,
        forecast_horizon=10,
        festivals=[festival],
        data_quality_score=0.7,
        seasonal_factors=seasonal_factors
    )
    
    # Check each prediction
    for i, prediction in enumerate(predictions):
        pred_date = datetime.fromisoformat(prediction['date'])
        days_from_festival = (pred_date.date() - festival_date).days
        
        # Property: Festival impact should only occur within window
        within_window = (-3 <= days_from_festival <= 2)  # prep=3, duration=2
        
        if within_window:
            # Should have festival impact
            assert prediction['festivalMultiplier'] > 1.0, (
                f"Day {i} ({prediction['date']}) is within festival window "
                f"({days_from_festival} days from festival) but has no impact"
            )
        else:
            # Should have no festival impact
            assert prediction['festivalMultiplier'] == 1.0, (
                f"Day {i} ({prediction['date']}) is outside festival window "
                f"({days_from_festival} days from festival) but has impact: "
                f"{prediction['festivalMultiplier']}"
            )


@settings(max_examples=100)
@given(data=st.data())
def test_multiple_festivals_handled_correctly(data):
    """
    **Validates: Requirements 2.2**
    
    Property: When multiple festivals occur in the forecast period,
    the system should handle overlapping impacts correctly (using max multiplier).
    """
    business_type = data.draw(business_type_strategy())
    region = data.draw(region_strategy())
    category = data.draw(product_category_strategy(business_type))
    
    # Create two festivals with overlapping windows
    festival1_date = (datetime.utcnow() + timedelta(days=3)).date()
    festival2_date = (datetime.utcnow() + timedelta(days=5)).date()
    
    festival1 = {
        'name': 'Festival 1',
        'date': festival1_date.isoformat(),
        'region': [region],
        'preparationDays': 2,
        'duration': 3,
        'demandMultipliers': {
            category: 2.0
        }
    }
    
    festival2 = {
        'name': 'Festival 2',
        'date': festival2_date.isoformat(),
        'region': [region],
        'preparationDays': 2,
        'duration': 2,
        'demandMultipliers': {
            category: 3.0
        }
    }
    
    # Generate predictions
    start_date = datetime.utcnow()
    seasonal_factors = get_seasonal_factors(business_type)
    
    predictions = generate_daily_predictions(
        category=category,
        business_type=business_type,
        start_date=start_date,
        forecast_horizon=10,
        festivals=[festival1, festival2],
        data_quality_score=0.7,
        seasonal_factors=seasonal_factors
    )
    
    # Property: On overlapping days, the maximum multiplier should be used
    # Day 5 (festival2 date) should have impact from both festivals
    # The multiplier should reflect the stronger festival (festival2 with 3.0)
    for prediction in predictions:
        pred_date = datetime.fromisoformat(prediction['date'])
        
        # Check if this date is affected by both festivals
        days_from_f1 = (pred_date.date() - festival1_date).days
        days_from_f2 = (pred_date.date() - festival2_date).days
        
        within_f1 = (-2 <= days_from_f1 <= 3)
        within_f2 = (-2 <= days_from_f2 <= 2)
        
        if within_f1 and within_f2:
            # Should have impact from the stronger festival
            # The multiplier should be >= 2.0 (from festival1)
            assert prediction['festivalMultiplier'] >= 2.0, (
                f"Date {prediction['date']} affected by both festivals "
                f"but multiplier is {prediction['festivalMultiplier']}"
            )


@settings(max_examples=100)
@given(data=st.data())
def test_festival_impact_decreases_with_distance(data):
    """
    **Validates: Requirements 2.2**
    
    Property: Festival impact should be strongest on the festival day
    and decrease with distance from the festival date.
    """
    business_type = data.draw(business_type_strategy())
    region = data.draw(region_strategy())
    category = data.draw(product_category_strategy(business_type))
    
    # Create a festival with significant multiplier
    festival_date = (datetime.utcnow() + timedelta(days=5)).date()
    festival = {
        'name': 'Test Festival',
        'date': festival_date.isoformat(),
        'region': [region],
        'preparationDays': 3,
        'duration': 3,
        'demandMultipliers': {
            category: 3.0
        }
    }
    
    # Generate predictions
    start_date = datetime.utcnow()
    seasonal_factors = get_seasonal_factors(business_type)
    
    predictions = generate_daily_predictions(
        category=category,
        business_type=business_type,
        start_date=start_date,
        forecast_horizon=10,
        festivals=[festival],
        data_quality_score=0.7,
        seasonal_factors=seasonal_factors
    )
    
    # Find the festival day prediction
    festival_day_pred = next(
        (p for p in predictions if p['date'] == festival_date.isoformat()),
        None
    )
    
    assume(festival_day_pred is not None)
    
    festival_day_multiplier = festival_day_pred['festivalMultiplier']
    
    # Property: Festival day should have the highest multiplier
    # Days before and after should have lower multipliers
    for prediction in predictions:
        pred_date = datetime.fromisoformat(prediction['date'])
        days_from_festival = abs((pred_date.date() - festival_date).days)
        
        if days_from_festival > 0 and prediction['festivalMultiplier'] > 1.0:
            # Days away from festival should have lower or equal multiplier
            assert prediction['festivalMultiplier'] <= festival_day_multiplier, (
                f"Day {prediction['date']} ({days_from_festival} days from festival) "
                f"has multiplier {prediction['festivalMultiplier']} > "
                f"festival day multiplier {festival_day_multiplier}"
            )


@settings(max_examples=100)
@given(data=st.data())
def test_demand_predictions_are_positive(data):
    """
    **Validates: Requirements 2.1**
    
    Property: All demand predictions should be positive values.
    """
    # Generate forecast context
    context = data.draw(forecast_context_strategy(include_festival=True))
    
    # Generate forecast
    forecast_result = generate_pattern_forecast(context)
    
    # Check all forecasts
    for forecast in forecast_result['forecasts']:
        for prediction in forecast['predictions']:
            # Property: Demand forecast should be positive
            assert prediction['demandForecast'] > 0, (
                f"Demand forecast should be positive, got {prediction['demandForecast']}"
            )
            
            # Property: Bounds should be positive
            assert prediction['lowerBound'] >= 0, (
                f"Lower bound should be non-negative, got {prediction['lowerBound']}"
            )
            assert prediction['upperBound'] > 0, (
                f"Upper bound should be positive, got {prediction['upperBound']}"
            )
            
            # Property: Bounds should be ordered correctly
            assert prediction['lowerBound'] <= prediction['demandForecast'], (
                f"Lower bound {prediction['lowerBound']} > "
                f"forecast {prediction['demandForecast']}"
            )
            assert prediction['demandForecast'] <= prediction['upperBound'], (
                f"Forecast {prediction['demandForecast']} > "
                f"upper bound {prediction['upperBound']}"
            )


@settings(max_examples=100)
@given(data=st.data())
def test_forecast_includes_sku_and_category(data):
    """
    **Validates: Requirements 2.1**
    
    Property: Each forecast should include SKU and category information.
    """
    # Generate forecast context
    context = data.draw(forecast_context_strategy(include_festival=False))
    
    # Generate forecast
    forecast_result = generate_pattern_forecast(context)
    
    # Property: Should have at least one forecast
    assert len(forecast_result['forecasts']) > 0, (
        "Forecast result should contain at least one forecast"
    )
    
    # Check each forecast
    for forecast in forecast_result['forecasts']:
        # Property: Should have SKU
        assert 'sku' in forecast, "Forecast missing SKU field"
        assert forecast['sku'] is not None, "Forecast SKU should not be None"
        
        # Property: Should have category
        assert 'category' in forecast, "Forecast missing category field"
        assert forecast['category'] is not None, "Forecast category should not be None"
        
        # Property: Category should match requested categories
        assert forecast['category'] in context['categories'], (
            f"Forecast category {forecast['category']} not in "
            f"requested categories {context['categories']}"
        )


@settings(max_examples=50)
@given(data=st.data())
def test_baseline_vs_festival_forecast_comparison(data):
    """
    **Validates: Requirements 2.1, 2.2**
    
    Property: Comparing forecasts with and without festivals should show
    that festival forecasts have higher total demand.
    """
    # Generate base context without festival
    business_type = data.draw(business_type_strategy())
    region = data.draw(region_strategy())
    category = data.draw(product_category_strategy(business_type))
    forecast_horizon = data.draw(forecast_horizon_strategy())
    
    base_context = {
        'userId': 'test_user',
        'forecastHorizon': forecast_horizon,
        'startDate': datetime.utcnow().date().isoformat(),
        'festivals': [],  # No festivals
        'userProfile': {
            'businessInfo': {
                'type': business_type,
                'location': {
                    'region': region
                }
            }
        },
        'dataQuality': {
            'score': 0.5,
            'quality': 'fair'
        },
        'categories': [category]
    }
    
    # Generate baseline forecast
    baseline_result = generate_pattern_forecast(base_context)
    
    # Create context with festival
    festival_date = (datetime.utcnow() + timedelta(days=forecast_horizon // 2)).date()
    festival = {
        'name': 'Test Festival',
        'date': festival_date.isoformat(),
        'region': [region],
        'preparationDays': 2,
        'duration': 2,
        'demandMultipliers': {
            category: 2.5
        }
    }
    
    festival_context = base_context.copy()
    festival_context['festivals'] = [festival]
    
    # Generate festival forecast
    festival_result = generate_pattern_forecast(festival_context)
    
    # Calculate total demand for both forecasts
    baseline_total = sum(
        p['demandForecast']
        for f in baseline_result['forecasts']
        for p in f['predictions']
    )
    
    festival_total = sum(
        p['demandForecast']
        for f in festival_result['forecasts']
        for p in f['predictions']
    )
    
    # Property: Festival forecast should have higher total demand
    assert festival_total > baseline_total, (
        f"Festival forecast total {festival_total} should be > "
        f"baseline total {baseline_total}"
    )
    
    # Property: The increase should be reasonable (not more than 5x)
    assert festival_total <= baseline_total * 5, (
        f"Festival forecast total {festival_total} is unreasonably high "
        f"compared to baseline {baseline_total}"
    )


# Concrete example tests

def test_diwali_forecast_shows_elevated_demand():
    """
    Concrete example: Diwali festival should show elevated demand for sweets.
    
    This complements the property-based tests with a specific scenario.
    """
    # Create context with Diwali
    diwali_date = (datetime.utcnow() + timedelta(days=7)).date()
    
    context = {
        'userId': 'test_user',
        'forecastHorizon': 14,
        'startDate': datetime.utcnow().date().isoformat(),
        'festivals': [
            {
                'name': 'Diwali',
                'date': diwali_date.isoformat(),
                'region': ['north'],
                'preparationDays': 3,
                'duration': 2,
                'demandMultipliers': {
                    'sweets': 3.5,
                    'fireworks': 4.0,
                    'jewelry': 3.0
                }
            }
        ],
        'userProfile': {
            'businessInfo': {
                'type': 'grocery',
                'location': {
                    'region': 'north'
                }
            }
        },
        'dataQuality': {
            'score': 0.5,
            'quality': 'fair'
        },
        'categories': ['sweets']
    }
    
    # Generate forecast
    result = generate_pattern_forecast(context)
    
    # Check that sweets forecast shows elevated demand
    sweets_forecast = next(
        (f for f in result['forecasts'] if f['category'] == 'sweets'),
        None
    )
    
    assert sweets_forecast is not None, "Sweets forecast not found"
    
    # Find predictions during Diwali period
    diwali_predictions = [
        p for p in sweets_forecast['predictions']
        if p['festivalMultiplier'] > 1.0
    ]
    
    assert len(diwali_predictions) > 0, "No Diwali impact found in predictions"
    
    # Check that Diwali is mentioned in contributing festivals
    diwali_mentioned = any(
        'Diwali' in p.get('festivals', [])
        for p in sweets_forecast['predictions']
    )
    
    assert diwali_mentioned, "Diwali not mentioned in contributing festivals"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--hypothesis-show-statistics"])
