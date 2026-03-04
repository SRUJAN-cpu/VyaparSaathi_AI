"""
Hypothesis strategies for generating test data for VyaparSaathi.

This module provides custom strategies for property-based testing using Hypothesis.
Strategies generate realistic sales data, festival calendars, and user inputs.
"""
from datetime import datetime, timedelta
from hypothesis import strategies as st
from typing import Any, Dict, List


# Business types
BUSINESS_TYPES = ["grocery", "apparel", "electronics", "general"]
STORE_SIZES = ["small", "medium", "large"]
REGIONS = ["north", "south", "east", "west", "central"]
RISK_TOLERANCES = ["conservative", "moderate", "aggressive"]
DATA_QUALITIES = ["poor", "fair", "good"]


@st.composite
def sales_record_strategy(draw) -> Dict[str, Any]:
    """
    Generate a valid sales record with required fields.
    
    Returns a dictionary with date, sku, and quantity fields.
    """
    # Generate date within last 2 years
    days_ago = draw(st.integers(min_value=0, max_value=730))
    date = datetime.now() - timedelta(days=days_ago)
    
    return {
        "date": date.strftime("%Y-%m-%d"),
        "sku": draw(st.text(alphabet=st.characters(whitelist_categories=("Lu", "Nd")), min_size=5, max_size=10)),
        "quantity": draw(st.integers(min_value=1, max_value=1000)),
        "category": draw(st.sampled_from(["grocery", "apparel", "electronics", "home", "beauty"])),
        "price": draw(st.floats(min_value=1.0, max_value=10000.0, allow_nan=False, allow_infinity=False)),
    }


@st.composite
def sales_data_list_strategy(draw, min_size: int = 1, max_size: int = 100) -> List[Dict[str, Any]]:
    """
    Generate a list of sales records.
    
    Args:
        min_size: Minimum number of records
        max_size: Maximum number of records
    """
    return draw(st.lists(sales_record_strategy(), min_size=min_size, max_size=max_size))


@st.composite
def invalid_sales_record_strategy(draw) -> Dict[str, Any]:
    """
    Generate an invalid sales record missing required fields or with invalid data.
    """
    record = {}
    
    # Randomly omit required fields
    if draw(st.booleans()):
        record["date"] = draw(st.one_of(
            st.just("invalid-date"),
            st.text(max_size=5),
            st.none(),
        ))
    
    if draw(st.booleans()):
        record["sku"] = draw(st.one_of(
            st.text(max_size=2),  # Too short
            st.none(),
        ))
    
    if draw(st.booleans()):
        record["quantity"] = draw(st.one_of(
            st.integers(max_value=0),  # Invalid quantity
            st.floats(allow_nan=True),
            st.none(),
        ))
    
    return record


@st.composite
def festival_event_strategy(draw) -> Dict[str, Any]:
    """
    Generate a festival event with all required fields.
    """
    festival_names = ["Diwali", "Eid", "Holi", "Christmas", "Pongal", "Onam", "Durga Puja"]
    
    # Generate date within next year
    days_ahead = draw(st.integers(min_value=1, max_value=365))
    date = datetime.now() + timedelta(days=days_ahead)
    
    return {
        "festivalId": f"{draw(st.sampled_from(festival_names)).lower()}-{date.year}",
        "name": draw(st.sampled_from(festival_names)),
        "date": date.strftime("%Y-%m-%d"),
        "region": draw(st.lists(st.sampled_from(REGIONS), min_size=1, max_size=3, unique=True)),
        "category": "festival",
        "demandMultipliers": {
            "grocery": draw(st.floats(min_value=1.0, max_value=5.0)),
            "apparel": draw(st.floats(min_value=1.0, max_value=5.0)),
            "electronics": draw(st.floats(min_value=1.0, max_value=5.0)),
        },
        "duration": draw(st.integers(min_value=1, max_value=10)),
        "preparationDays": draw(st.integers(min_value=7, max_value=30)),
    }


@st.composite
def user_profile_strategy(draw) -> Dict[str, Any]:
    """
    Generate a user profile with business information and preferences.
    """
    return {
        "userId": f"user-{draw(st.text(alphabet=st.characters(whitelist_categories=('Ll', 'Nd')), min_size=8, max_size=12))}",
        "businessInfo": {
            "name": draw(st.text(min_size=5, max_size=50)),
            "type": draw(st.sampled_from(BUSINESS_TYPES)),
            "location": {
                "city": draw(st.text(min_size=3, max_size=30)),
                "state": draw(st.text(min_size=3, max_size=30)),
                "region": draw(st.sampled_from(REGIONS)),
            },
            "size": draw(st.sampled_from(STORE_SIZES)),
        },
        "dataCapabilities": {
            "hasHistoricalData": draw(st.booleans()),
            "dataQuality": draw(st.sampled_from(DATA_QUALITIES)),
            "lastUpdated": datetime.now().isoformat(),
        },
        "preferences": {
            "forecastHorizon": draw(st.integers(min_value=7, max_value=14)),
            "riskTolerance": draw(st.sampled_from(RISK_TOLERANCES)),
        },
    }


@st.composite
def questionnaire_response_strategy(draw) -> Dict[str, Any]:
    """
    Generate a questionnaire response for low-data mode.
    """
    return {
        "userId": f"user-{draw(st.text(alphabet=st.characters(whitelist_categories=('Ll', 'Nd')), min_size=8, max_size=12))}",
        "businessType": draw(st.sampled_from(BUSINESS_TYPES)),
        "storeSize": draw(st.sampled_from(STORE_SIZES)),
        "lastFestivalPerformance": {
            "festival": draw(st.sampled_from(["Diwali", "Eid", "Holi", "Christmas"])),
            "salesIncrease": draw(st.floats(min_value=0.0, max_value=500.0)),
            "topCategories": draw(st.lists(st.sampled_from(["grocery", "apparel", "electronics"]), min_size=1, max_size=3, unique=True)),
            "stockoutItems": draw(st.lists(st.text(min_size=3, max_size=20), min_size=0, max_size=5)),
        },
        "currentInventory": draw(st.lists(
            st.fixed_dictionaries({
                "category": st.sampled_from(["grocery", "apparel", "electronics"]),
                "currentStock": st.integers(min_value=0, max_value=10000),
                "averageDailySales": st.integers(min_value=1, max_value=500),
                "confidence": st.sampled_from(["low", "medium", "high"]),
            }),
            min_size=1,
            max_size=5,
        )),
        "targetFestivals": draw(st.lists(st.sampled_from(["Diwali", "Eid", "Holi", "Christmas"]), min_size=1, max_size=3, unique=True)),
    }


@st.composite
def forecast_request_strategy(draw) -> Dict[str, Any]:
    """
    Generate a forecast request.
    """
    return {
        "userId": f"user-{draw(st.text(alphabet=st.characters(whitelist_categories=('Ll', 'Nd')), min_size=8, max_size=12))}",
        "forecastHorizon": draw(st.integers(min_value=7, max_value=14)),
        "targetFestivals": draw(st.lists(st.text(min_size=3, max_size=20), min_size=0, max_size=3)),
        "dataMode": draw(st.sampled_from(["structured", "low-data"])),
        "confidence": draw(st.floats(min_value=0.0, max_value=1.0)),
    }


@st.composite
def inventory_data_strategy(draw) -> Dict[str, Any]:
    """
    Generate inventory data for risk assessment.
    """
    return {
        "sku": draw(st.text(alphabet=st.characters(whitelist_categories=("Lu", "Nd")), min_size=5, max_size=10)),
        "category": draw(st.sampled_from(["grocery", "apparel", "electronics"])),
        "currentStock": draw(st.integers(min_value=0, max_value=10000)),
        "reorderPoint": draw(st.integers(min_value=10, max_value=500)),
        "leadTimeDays": draw(st.integers(min_value=1, max_value=30)),
    }


@st.composite
def daily_prediction_strategy(draw) -> Dict[str, Any]:
    """
    Generate a daily prediction for forecast results.
    """
    days_ahead = draw(st.integers(min_value=0, max_value=14))
    date = datetime.now() + timedelta(days=days_ahead)
    
    demand_forecast = draw(st.floats(min_value=1.0, max_value=1000.0, allow_nan=False, allow_infinity=False))
    festival_multiplier = draw(st.floats(min_value=1.0, max_value=5.0, allow_nan=False, allow_infinity=False))
    
    # Calculate bounds around forecast
    variance = draw(st.floats(min_value=0.1, max_value=0.5))
    lower_bound = max(0, demand_forecast * (1 - variance))
    upper_bound = demand_forecast * (1 + variance)
    
    return {
        "date": date.strftime("%Y-%m-%d"),
        "demandForecast": demand_forecast,
        "lowerBound": lower_bound,
        "upperBound": upper_bound,
        "festivalMultiplier": festival_multiplier,
        "confidence": draw(st.floats(min_value=0.5, max_value=0.95)),
        "festivals": draw(st.lists(st.sampled_from(["Diwali", "Eid", "Holi", "Christmas"]), max_size=2))
    }


@st.composite
def forecast_result_strategy(draw) -> Dict[str, Any]:
    """
    Generate a complete forecast result for testing explanations.
    """
    predictions = draw(st.lists(daily_prediction_strategy(), min_size=7, max_size=14))
    
    return {
        "sku": draw(st.text(alphabet=st.characters(whitelist_categories=("Lu", "Nd")), min_size=5, max_size=10)),
        "category": draw(st.sampled_from(["grocery", "apparel", "electronics", "home", "beauty"])),
        "predictions": predictions,
        "confidence": draw(st.floats(min_value=0.5, max_value=0.95)),
        "methodology": draw(st.sampled_from(["ml", "pattern", "hybrid"])),
        "assumptions": draw(st.lists(st.text(min_size=10, max_size=100), min_size=1, max_size=5))
    }


@st.composite
def risk_assessment_strategy(draw) -> Dict[str, Any]:
    """
    Generate a risk assessment for testing explanations.
    """
    current_stock = draw(st.integers(min_value=0, max_value=10000))
    
    stockout_prob = draw(st.floats(min_value=0.0, max_value=1.0))
    overstock_prob = draw(st.floats(min_value=0.0, max_value=1.0))
    
    return {
        "sku": draw(st.text(alphabet=st.characters(whitelist_categories=("Lu", "Nd")), min_size=5, max_size=10)),
        "category": draw(st.sampled_from(["grocery", "apparel", "electronics", "home", "beauty"])),
        "currentStock": current_stock,
        "stockoutRisk": {
            "probability": stockout_prob,
            "daysUntilStockout": draw(st.integers(min_value=0, max_value=30)),
            "potentialLostSales": draw(st.floats(min_value=0.0, max_value=5000.0))
        },
        "overstockRisk": {
            "probability": overstock_prob,
            "excessUnits": draw(st.integers(min_value=0, max_value=5000)),
            "carryingCost": draw(st.floats(min_value=0.0, max_value=10000.0))
        },
        "recommendation": {
            "action": draw(st.sampled_from(["reorder", "reduce", "maintain"])),
            "suggestedQuantity": draw(st.integers(min_value=0, max_value=5000)),
            "urgency": draw(st.sampled_from(["low", "medium", "high"])),
            "reasoning": draw(st.lists(st.text(min_size=10, max_size=100), min_size=1, max_size=5)),
            "confidence": draw(st.floats(min_value=0.5, max_value=0.95))
        }
    }
