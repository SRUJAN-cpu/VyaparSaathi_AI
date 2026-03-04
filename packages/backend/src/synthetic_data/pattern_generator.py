"""
Synthetic pattern generator for VyaparSaathi.

Generates realistic demand patterns based on business type, seasonal factors,
and festival impacts.
"""

import os
import sys
import random
from dataclasses import dataclass, field
from typing import Dict, List, Tuple
from enum import Enum

# Import performance monitoring utilities
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.performance import Cache


class BusinessType(str, Enum):
    """Business type enumeration."""
    GROCERY = "grocery"
    APPAREL = "apparel"
    ELECTRONICS = "electronics"
    GENERAL = "general"


@dataclass
class CategoryPattern:
    """Demand pattern for a specific product category."""
    category: str
    normal_demand: float
    festival_multiplier: float
    peak_days: List[int]
    variance: float


@dataclass
class SyntheticPattern:
    """
    Synthetic demand pattern for a business type.
    
    Attributes:
        business_type: Type of business (grocery, apparel, electronics, general)
        region: Geographic region
        baseline_patterns: Demand patterns by category
        seasonal_factors: Monthly seasonal adjustment factors
        festival_multipliers: Festival-specific demand multipliers by category
    """
    business_type: str
    region: str
    baseline_patterns: List[CategoryPattern] = field(default_factory=list)
    seasonal_factors: Dict[int, float] = field(default_factory=dict)
    festival_multipliers: Dict[str, Dict[str, float]] = field(default_factory=dict)


def get_baseline_demand(business_type: str, category: str) -> Tuple[float, float]:
    """
    Get baseline demand and variance for a business type and category.
    
    Args:
        business_type: Type of business
        category: Product category
        
    Returns:
        Tuple of (baseline_demand, variance)
    """
    # Baseline demand patterns by business type and category
    demand_patterns = {
        BusinessType.GROCERY: {
            "staples": (100.0, 0.15),  # Rice, wheat, dal - stable demand
            "vegetables": (80.0, 0.25),  # Higher variance due to freshness
            "dairy": (60.0, 0.20),
            "snacks": (50.0, 0.30),
            "beverages": (45.0, 0.25),
            "sweets": (30.0, 0.40),  # High variance, festival-dependent
        },
        BusinessType.APPAREL: {
            "traditional": (40.0, 0.50),  # High festival impact
            "casual": (50.0, 0.30),
            "formal": (30.0, 0.35),
            "kids": (35.0, 0.40),
            "accessories": (25.0, 0.45),
        },
        BusinessType.ELECTRONICS: {
            "mobile": (20.0, 0.40),
            "laptop": (10.0, 0.45),
            "tv": (8.0, 0.50),
            "appliances": (15.0, 0.40),
            "accessories": (40.0, 0.35),
        },
        BusinessType.GENERAL: {
            "household": (50.0, 0.30),
            "personal_care": (40.0, 0.25),
            "stationery": (30.0, 0.35),
            "gifts": (25.0, 0.50),
        },
    }
    
    bt = BusinessType(business_type)
    if bt in demand_patterns and category in demand_patterns[bt]:
        return demand_patterns[bt][category]
    
    # Default values for unknown categories
    return (50.0, 0.30)


def get_seasonal_factors(business_type: str) -> Dict[int, float]:
    """
    Get seasonal adjustment factors by month for a business type.
    
    Args:
        business_type: Type of business
        
    Returns:
        Dictionary mapping month (1-12) to seasonal factor
    """
    seasonal_patterns = {
        BusinessType.GROCERY: {
            1: 1.0,   # January - normal
            2: 0.95,  # February - slight dip
            3: 1.05,  # March - Holi season
            4: 1.0,   # April
            5: 0.95,  # May - summer slowdown
            6: 0.90,  # June - monsoon start
            7: 0.95,  # July
            8: 1.05,  # August - festival prep
            9: 1.10,  # September - festival season
            10: 1.25, # October - Diwali peak
            11: 1.15, # November - post-Diwali
            12: 1.10, # December - year-end
        },
        BusinessType.APPAREL: {
            1: 0.90,  # January - post-season
            2: 0.85,  # February - low season
            3: 1.10,  # March - spring/Holi
            4: 1.05,  # April - wedding season
            5: 0.95,  # May
            6: 0.90,  # June - monsoon
            7: 0.95,  # July
            8: 1.15,  # August - festival prep
            9: 1.25,  # September - festival shopping
            10: 1.40, # October - Diwali peak
            11: 1.20, # November - wedding season
            12: 1.15, # December - year-end
        },
        BusinessType.ELECTRONICS: {
            1: 1.05,  # January - New Year sales
            2: 0.95,  # February
            3: 1.00,  # March
            4: 1.05,  # April - new launches
            5: 0.95,  # May
            6: 0.90,  # June
            7: 0.95,  # July
            8: 1.10,  # August - festival prep
            9: 1.20,  # September - festival offers
            10: 1.50, # October - Diwali peak
            11: 1.25, # November - continued sales
            12: 1.20, # December - year-end
        },
        BusinessType.GENERAL: {
            1: 1.0,   # January
            2: 0.95,  # February
            3: 1.05,  # March
            4: 1.0,   # April
            5: 0.95,  # May
            6: 0.95,  # June
            7: 1.0,   # July
            8: 1.10,  # August
            9: 1.15,  # September
            10: 1.30, # October - Diwali
            11: 1.15, # November
            12: 1.10, # December
        },
    }
    
    bt = BusinessType(business_type)
    return seasonal_patterns.get(bt, seasonal_patterns[BusinessType.GENERAL])


def get_festival_multipliers(business_type: str) -> Dict[str, Dict[str, float]]:
    """
    Get festival-specific demand multipliers by category.
    
    Args:
        business_type: Type of business
        
    Returns:
        Dictionary mapping festival names to category multipliers
    """
    festival_patterns = {
        BusinessType.GROCERY: {
            "Diwali": {
                "staples": 1.5,
                "vegetables": 1.3,
                "dairy": 1.4,
                "snacks": 2.0,
                "beverages": 1.6,
                "sweets": 3.5,
            },
            "Eid": {
                "staples": 1.4,
                "vegetables": 1.2,
                "dairy": 1.5,
                "snacks": 1.8,
                "beverages": 1.5,
                "sweets": 3.0,
            },
            "Holi": {
                "staples": 1.2,
                "vegetables": 1.1,
                "dairy": 1.3,
                "snacks": 1.6,
                "beverages": 2.0,
                "sweets": 2.5,
            },
        },
        BusinessType.APPAREL: {
            "Diwali": {
                "traditional": 3.5,
                "casual": 1.8,
                "formal": 2.0,
                "kids": 2.5,
                "accessories": 2.2,
            },
            "Eid": {
                "traditional": 3.0,
                "casual": 1.5,
                "formal": 1.8,
                "kids": 2.2,
                "accessories": 2.0,
            },
            "Holi": {
                "traditional": 1.5,
                "casual": 2.0,
                "formal": 1.2,
                "kids": 1.8,
                "accessories": 1.6,
            },
        },
        BusinessType.ELECTRONICS: {
            "Diwali": {
                "mobile": 2.5,
                "laptop": 2.2,
                "tv": 3.0,
                "appliances": 2.8,
                "accessories": 2.0,
            },
            "Eid": {
                "mobile": 1.8,
                "laptop": 1.6,
                "tv": 2.0,
                "appliances": 1.9,
                "accessories": 1.7,
            },
            "Holi": {
                "mobile": 1.3,
                "laptop": 1.2,
                "tv": 1.4,
                "appliances": 1.3,
                "accessories": 1.5,
            },
        },
        BusinessType.GENERAL: {
            "Diwali": {
                "household": 2.0,
                "personal_care": 1.8,
                "stationery": 1.5,
                "gifts": 3.5,
            },
            "Eid": {
                "household": 1.7,
                "personal_care": 1.6,
                "stationery": 1.3,
                "gifts": 3.0,
            },
            "Holi": {
                "household": 1.4,
                "personal_care": 1.5,
                "stationery": 1.2,
                "gifts": 2.5,
            },
        },
    }
    
    bt = BusinessType(business_type)
    return festival_patterns.get(bt, festival_patterns[BusinessType.GENERAL])


@Cache.cached(ttl_seconds=3600, key_prefix='synthetic_pattern')
def generate_synthetic_pattern(
    business_type: str,
    region: str = "north",
    categories: List[str] = None
) -> SyntheticPattern:
    """
    Generate a complete synthetic demand pattern for a business.
    
    Args:
        business_type: Type of business (grocery, apparel, electronics, general)
        region: Geographic region
        categories: List of product categories (uses defaults if None)
        
    Returns:
        SyntheticPattern with baseline patterns, seasonal factors, and festival multipliers
    """
    # Default categories by business type
    default_categories = {
        BusinessType.GROCERY: ["staples", "vegetables", "dairy", "snacks", "beverages", "sweets"],
        BusinessType.APPAREL: ["traditional", "casual", "formal", "kids", "accessories"],
        BusinessType.ELECTRONICS: ["mobile", "laptop", "tv", "appliances", "accessories"],
        BusinessType.GENERAL: ["household", "personal_care", "stationery", "gifts"],
    }
    
    bt = BusinessType(business_type)
    if categories is None:
        categories = default_categories.get(bt, default_categories[BusinessType.GENERAL])
    
    # Generate baseline patterns for each category
    baseline_patterns = []
    for category in categories:
        baseline_demand, variance = get_baseline_demand(business_type, category)
        
        # Generate peak days (typically weekends and month-end)
        peak_days = [5, 6, 0]  # Friday, Saturday, Sunday (0 = Sunday)
        if random.random() > 0.5:
            peak_days.append(random.choice([28, 29, 30]))  # Month-end
        
        # Get festival multiplier for this category
        festival_mults = get_festival_multipliers(business_type)
        avg_festival_mult = sum(
            fest_cats.get(category, 1.5)
            for fest_cats in festival_mults.values()
        ) / len(festival_mults)
        
        pattern = CategoryPattern(
            category=category,
            normal_demand=baseline_demand,
            festival_multiplier=avg_festival_mult,
            peak_days=peak_days,
            variance=variance,
        )
        baseline_patterns.append(pattern)
    
    # Get seasonal factors
    seasonal_factors = get_seasonal_factors(business_type)
    
    # Get festival multipliers
    festival_multipliers = get_festival_multipliers(business_type)
    
    return SyntheticPattern(
        business_type=business_type,
        region=region,
        baseline_patterns=baseline_patterns,
        seasonal_factors=seasonal_factors,
        festival_multipliers=festival_multipliers,
    )
