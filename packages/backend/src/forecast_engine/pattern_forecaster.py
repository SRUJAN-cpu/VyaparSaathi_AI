"""
Pattern-based forecasting for low-data mode

This module implements pattern-based forecasting using synthetic patterns
and festival multipliers for users with minimal historical data.
"""

import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import random

# Import internal modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from synthetic_data.pattern_generator import (
    generate_synthetic_pattern,
    get_baseline_demand,
    get_seasonal_factors,
    get_festival_multipliers,
    BusinessType
)
from .data_quality import calculate_confidence_adjustment


def get_business_type_from_profile(user_profile: Optional[Dict[str, Any]]) -> str:
    """
    Extract business type from user profile.
    
    Args:
        user_profile: User profile dictionary
        
    Returns:
        Business type string
    """
    if not user_profile:
        return 'general'
    
    business_info = user_profile.get('businessInfo', {})
    business_type = business_info.get('type', 'general')
    
    # Normalize business type
    if isinstance(business_type, str):
        return business_type.lower()
    
    return 'general'


def get_region_from_profile(user_profile: Optional[Dict[str, Any]]) -> str:
    """
    Extract region from user profile.
    
    Args:
        user_profile: User profile dictionary
        
    Returns:
        Region string
    """
    if not user_profile:
        return 'north'
    
    location = user_profile.get('businessInfo', {}).get('location', {})
    region = location.get('region', 'north')
    
    return region


def get_categories_from_context(
    forecast_context: Dict[str, Any],
    business_type: str
) -> List[str]:
    """
    Determine categories to forecast based on context and business type.
    
    Args:
        forecast_context: Forecast context dictionary
        business_type: Business type
        
    Returns:
        List of category strings
    """
    # Check if categories are specified in context
    specified_categories = forecast_context.get('categories')
    if specified_categories:
        return specified_categories
    
    # Use default categories for business type
    default_categories = {
        'grocery': ['staples', 'vegetables', 'dairy', 'snacks', 'beverages', 'sweets'],
        'apparel': ['traditional', 'casual', 'formal', 'kids', 'accessories'],
        'electronics': ['mobile', 'laptop', 'tv', 'appliances', 'accessories'],
        'general': ['household', 'personal_care', 'stationery', 'gifts'],
    }
    
    return default_categories.get(business_type, default_categories['general'])


def calculate_baseline_demand(
    category: str,
    business_type: str,
    date: datetime,
    seasonal_factors: Dict[int, float]
) -> float:
    """
    Calculate baseline demand for a category on a specific date.
    
    Args:
        category: Product category
        business_type: Business type
        date: Date for calculation
        seasonal_factors: Monthly seasonal adjustment factors
        
    Returns:
        Baseline demand value
    """
    # Get base demand and variance
    base_demand, variance = get_baseline_demand(business_type, category)
    
    # Apply seasonal factor
    month = date.month
    seasonal_factor = seasonal_factors.get(month, 1.0)
    
    # Apply day-of-week variation
    # Weekends typically have higher demand
    day_of_week = date.weekday()
    day_factor = 1.0
    if day_of_week in [5, 6]:  # Saturday, Sunday
        day_factor = 1.2
    elif day_of_week == 4:  # Friday
        day_factor = 1.1
    
    # Calculate baseline with some random variation
    random_factor = 1.0 + random.uniform(-variance/2, variance/2)
    
    baseline = base_demand * seasonal_factor * day_factor * random_factor
    
    return baseline


def apply_festival_impact(
    baseline_demand: float,
    date: datetime,
    category: str,
    festivals: List[Dict[str, Any]],
    business_type: str
) -> tuple[float, float, List[str]]:
    """
    Apply festival impact to baseline demand.
    
    Args:
        baseline_demand: Baseline demand without festival impact
        date: Date for calculation
        category: Product category
        festivals: List of relevant festivals
        business_type: Business type
        
    Returns:
        Tuple of (adjusted_demand, festival_multiplier, contributing_festivals)
    """
    date_str = date.date().isoformat()
    max_multiplier = 1.0
    contributing_festivals = []
    
    # Check each festival for impact on this date
    for festival in festivals:
        festival_date = datetime.fromisoformat(festival['date']).date()
        current_date = date.date()
        
        # Calculate days from festival
        days_diff = (current_date - festival_date).days
        
        # Festival impact window (preparation days before to duration after)
        prep_days = festival.get('preparationDays', 3)
        duration = festival.get('duration', 1)
        
        # Check if date is within festival impact window
        if -prep_days <= days_diff <= duration:
            # Get festival multiplier for this category
            multiplier = festival.get('demandMultipliers', {}).get(category, 1.0)
            
            # Apply distance decay (impact is strongest on festival day)
            if days_diff < 0:
                # Before festival - gradual increase
                distance_factor = 1.0 + (multiplier - 1.0) * (1 + days_diff / prep_days)
            elif days_diff == 0:
                # Festival day - full impact
                distance_factor = multiplier
            else:
                # After festival - gradual decrease
                distance_factor = 1.0 + (multiplier - 1.0) * (1 - days_diff / duration)
            
            if distance_factor > max_multiplier:
                max_multiplier = distance_factor
            
            contributing_festivals.append(festival['name'])
    
    adjusted_demand = baseline_demand * max_multiplier
    
    return adjusted_demand, max_multiplier, contributing_festivals


def calculate_confidence_bounds(
    demand_forecast: float,
    data_quality_score: float,
    festival_multiplier: float,
    variance: float
) -> tuple[float, float, float]:
    """
    Calculate confidence bounds for demand forecast.
    
    Args:
        demand_forecast: Predicted demand
        data_quality_score: Data quality score (0-1)
        festival_multiplier: Festival impact multiplier
        variance: Category variance
        
    Returns:
        Tuple of (lower_bound, upper_bound, confidence)
    """
    # Base confidence from data quality
    base_confidence = calculate_confidence_adjustment(data_quality_score, 'pattern')
    
    # Adjust confidence based on festival impact
    # Higher festival multipliers mean more uncertainty
    if festival_multiplier > 2.0:
        confidence_adjustment = 0.9
    elif festival_multiplier > 1.5:
        confidence_adjustment = 0.95
    else:
        confidence_adjustment = 1.0
    
    confidence = base_confidence * confidence_adjustment
    
    # Calculate bounds based on variance and confidence
    # Lower confidence means wider bounds
    bound_width = demand_forecast * variance * (1.5 - confidence)
    
    lower_bound = max(0, demand_forecast - bound_width)
    upper_bound = demand_forecast + bound_width
    
    return lower_bound, upper_bound, confidence


def generate_daily_predictions(
    category: str,
    business_type: str,
    start_date: datetime,
    forecast_horizon: int,
    festivals: List[Dict[str, Any]],
    data_quality_score: float,
    seasonal_factors: Dict[int, float]
) -> List[Dict[str, Any]]:
    """
    Generate daily predictions for a category.
    
    Args:
        category: Product category
        business_type: Business type
        start_date: Start date for forecast
        forecast_horizon: Number of days to forecast
        festivals: List of relevant festivals
        data_quality_score: Data quality score (0-1)
        seasonal_factors: Monthly seasonal factors
        
    Returns:
        List of DailyPrediction dictionaries
    """
    predictions = []
    base_demand, variance = get_baseline_demand(business_type, category)
    
    for day_offset in range(forecast_horizon):
        current_date = start_date + timedelta(days=day_offset)
        
        # Calculate baseline demand
        baseline = calculate_baseline_demand(
            category,
            business_type,
            current_date,
            seasonal_factors
        )
        
        # Apply festival impact
        adjusted_demand, festival_multiplier, contributing_festivals = apply_festival_impact(
            baseline,
            current_date,
            category,
            festivals,
            business_type
        )
        
        # Calculate confidence bounds
        lower_bound, upper_bound, confidence = calculate_confidence_bounds(
            adjusted_demand,
            data_quality_score,
            festival_multiplier,
            variance
        )
        
        prediction = {
            'date': current_date.date().isoformat(),
            'demandForecast': round(adjusted_demand, 2),
            'lowerBound': round(lower_bound, 2),
            'upperBound': round(upper_bound, 2),
            'festivalMultiplier': round(festival_multiplier, 2),
            'confidence': round(confidence, 2),
            'festivals': contributing_festivals
        }
        
        predictions.append(prediction)
    
    return predictions


def generate_pattern_forecast(forecast_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate pattern-based forecast for low-data mode.
    
    This is the main entry point for pattern-based forecasting.
    
    Args:
        forecast_context: Context dictionary with all forecast parameters
        
    Returns:
        Forecast results dictionary
    """
    user_id = forecast_context['userId']
    forecast_horizon = forecast_context['forecastHorizon']
    start_date_str = forecast_context['startDate']
    festivals = forecast_context['festivals']
    user_profile = forecast_context.get('userProfile')
    data_quality = forecast_context['dataQuality']
    
    # Extract business context
    business_type = get_business_type_from_profile(user_profile)
    region = get_region_from_profile(user_profile)
    categories = get_categories_from_context(forecast_context, business_type)
    
    # Generate synthetic pattern
    synthetic_pattern = generate_synthetic_pattern(business_type, region, categories)
    
    # Parse start date
    start_date = datetime.fromisoformat(start_date_str)
    
    # Generate forecasts for each category
    forecast_results = []
    
    for category in categories:
        # Generate daily predictions
        predictions = generate_daily_predictions(
            category=category,
            business_type=business_type,
            start_date=start_date,
            forecast_horizon=forecast_horizon,
            festivals=festivals,
            data_quality_score=data_quality['score'],
            seasonal_factors=synthetic_pattern.seasonal_factors
        )
        
        # Calculate overall confidence
        avg_confidence = sum(p['confidence'] for p in predictions) / len(predictions)
        
        # Generate assumptions
        assumptions = [
            f"Using pattern-based forecasting for {business_type} business",
            f"Baseline demand patterns derived from industry benchmarks",
            f"Festival impacts based on historical regional patterns",
            f"Data quality: {data_quality['quality']}",
        ]
        
        if festivals:
            festival_names = [f['name'] for f in festivals]
            assumptions.append(f"Considering festivals: {', '.join(festival_names)}")
        
        # Create forecast result
        forecast_result = {
            'sku': f"{category}_default",  # Placeholder SKU
            'category': category,
            'predictions': predictions,
            'confidence': round(avg_confidence, 2),
            'methodology': 'pattern',
            'assumptions': assumptions,
            'generatedAt': datetime.utcnow().isoformat(),
            'expiresAt': (datetime.utcnow() + timedelta(days=30)).isoformat()
        }
        
        forecast_results.append(forecast_result)
    
    # Calculate summary statistics
    total_demand = sum(
        sum(p['demandForecast'] for p in fr['predictions'])
        for fr in forecast_results
    )
    
    avg_confidence = sum(fr['confidence'] for fr in forecast_results) / len(forecast_results)
    
    # Find peak demand day
    all_predictions = []
    for fr in forecast_results:
        for pred in fr['predictions']:
            all_predictions.append((pred['date'], pred['demandForecast']))
    
    peak_day = max(all_predictions, key=lambda x: x[1])[0] if all_predictions else start_date_str
    
    return {
        'userId': user_id,
        'forecasts': forecast_results,
        'summary': {
            'totalSkus': len(forecast_results),
            'averageConfidence': round(avg_confidence, 2),
            'peakDemandDay': peak_day,
            'totalDemand': round(total_demand, 2),
            'metadata': {
                'dataQuality': data_quality['quality'],
                'festivalCount': len(festivals),
                'methodologyBreakdown': {
                    'ml': 0,
                    'pattern': len(forecast_results),
                    'hybrid': 0
                }
            }
        }
    }
