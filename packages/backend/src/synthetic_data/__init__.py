"""
Synthetic data generation module for VyaparSaathi.

This module provides functionality to generate realistic synthetic sales data
for demonstration and testing purposes.
"""

from .pattern_generator import (
    SyntheticPattern,
    generate_synthetic_pattern,
    get_baseline_demand,
    get_seasonal_factors,
    get_festival_multipliers,
)
from .sales_generator import (
    generate_synthetic_sales,
    generate_sales_for_period,
)
from .demo_mode import (
    is_demo_mode,
    set_demo_mode,
    get_data_source,
    add_demo_indicator,
    switch_mode,
    get_demo_indicator_text,
)
from .scenarios import (
    generate_grocery_scenario,
    generate_apparel_scenario,
    generate_electronics_scenario,
)

__all__ = [
    "SyntheticPattern",
    "generate_synthetic_pattern",
    "get_baseline_demand",
    "get_seasonal_factors",
    "get_festival_multipliers",
    "generate_synthetic_sales",
    "generate_sales_for_period",
    "is_demo_mode",
    "set_demo_mode",
    "get_data_source",
    "add_demo_indicator",
    "switch_mode",
    "get_demo_indicator_text",
    "generate_grocery_scenario",
    "generate_apparel_scenario",
    "generate_electronics_scenario",
]
