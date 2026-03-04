"""
Forecasting engine for VyaparSaathi

This module provides demand forecasting capabilities using dual-mode approach:
- Structured data mode: ML-based forecasting with Amazon Forecast
- Low-data mode: Pattern-based forecasting with synthetic patterns
"""

from .forecast_handler import lambda_handler, generate_forecast
from .data_quality import assess_data_quality, determine_forecasting_method
from .storage import (
    store_forecast_result,
    store_forecast_results,
    get_forecast_by_id,
    get_forecasts_by_user,
    get_forecasts_by_user_and_sku,
    get_latest_forecast_for_sku,
    delete_forecast,
    delete_user_forecasts
)

__all__ = [
    'lambda_handler',
    'generate_forecast',
    'assess_data_quality',
    'determine_forecasting_method',
    'store_forecast_result',
    'store_forecast_results',
    'get_forecast_by_id',
    'get_forecasts_by_user',
    'get_forecasts_by_user_and_sku',
    'get_latest_forecast_for_sku',
    'delete_forecast',
    'delete_user_forecasts',
]
