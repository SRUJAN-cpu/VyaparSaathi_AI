"""
Synthetic sales data generator for VyaparSaathi.

Generates realistic sales records with seasonal patterns and festival impacts.
"""

import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from .pattern_generator import (
    SyntheticPattern,
    generate_synthetic_pattern,
    BusinessType,
)


def generate_sales_record(
    date: datetime,
    sku: str,
    category: str,
    base_demand: float,
    seasonal_factor: float,
    festival_multiplier: float,
    variance: float,
    price: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Generate a single sales record with realistic demand.
    
    Args:
        date: Date of the sale
        sku: Product SKU
        category: Product category
        base_demand: Baseline daily demand
        seasonal_factor: Seasonal adjustment factor
        festival_multiplier: Festival impact multiplier
        variance: Random variance factor (0-1)
        price: Optional unit price
        
    Returns:
        Sales record dictionary
    """
    # Calculate demand with all factors
    demand = base_demand * seasonal_factor * festival_multiplier
    
    # Add day-of-week variation (weekends typically higher)
    day_of_week = date.weekday()
    if day_of_week in [5, 6]:  # Saturday, Sunday
        demand *= random.uniform(1.1, 1.3)
    elif day_of_week == 4:  # Friday
        demand *= random.uniform(1.05, 1.15)
    
    # Add random variance
    noise = random.gauss(0, variance)
    demand = demand * (1 + noise)
    
    # Ensure non-negative demand
    quantity = max(0, int(round(demand)))
    
    # Generate price if not provided
    if price is None:
        # Price varies by category
        price_ranges = {
            "staples": (50, 500),
            "vegetables": (20, 100),
            "dairy": (30, 150),
            "snacks": (10, 100),
            "beverages": (20, 150),
            "sweets": (100, 500),
            "traditional": (500, 5000),
            "casual": (300, 2000),
            "formal": (800, 5000),
            "kids": (200, 1500),
            "accessories": (100, 1000),
            "mobile": (5000, 50000),
            "laptop": (20000, 100000),
            "tv": (15000, 80000),
            "appliances": (5000, 50000),
            "household": (100, 2000),
            "personal_care": (50, 500),
            "stationery": (10, 200),
            "gifts": (100, 5000),
        }
        min_price, max_price = price_ranges.get(category, (50, 500))
        price = random.uniform(min_price, max_price)
    
    return {
        "date": date.strftime("%Y-%m-%d"),
        "sku": sku,
        "quantity": quantity,
        "category": category,
        "price": round(price, 2),
    }


def get_festival_impact(
    date: datetime,
    festivals: List[Dict[str, Any]],
    category: str,
    festival_multipliers: Dict[str, Dict[str, float]],
) -> float:
    """
    Calculate festival impact multiplier for a given date and category.
    
    Args:
        date: Date to check
        festivals: List of festival events
        category: Product category
        festival_multipliers: Festival multipliers by festival and category
        
    Returns:
        Combined festival multiplier (1.0 if no festival impact)
    """
    multiplier = 1.0
    
    for festival in festivals:
        festival_date = datetime.strptime(festival["date"], "%Y-%m-%d")
        days_diff = (date - festival_date).days
        
        # Festival impact window: 7 days before to 3 days after
        if -7 <= days_diff <= 3:
            # Get festival multiplier for this category
            fest_name = festival["name"]
            if fest_name in festival_multipliers:
                cat_multiplier = festival_multipliers[fest_name].get(category, 1.0)
                
                # Impact increases as festival approaches, peaks on festival day
                if days_diff < 0:  # Before festival
                    impact_factor = 1 + (cat_multiplier - 1) * (7 + days_diff) / 7
                elif days_diff == 0:  # Festival day
                    impact_factor = cat_multiplier
                else:  # After festival
                    impact_factor = 1 + (cat_multiplier - 1) * (3 - days_diff) / 3
                
                # Combine multiple festival impacts (multiplicative)
                multiplier *= impact_factor
    
    return multiplier


def generate_sales_for_period(
    pattern: SyntheticPattern,
    start_date: datetime,
    end_date: datetime,
    festivals: List[Dict[str, Any]] = None,
    skus_per_category: int = 3,
) -> List[Dict[str, Any]]:
    """
    Generate sales data for a time period.
    
    Args:
        pattern: Synthetic pattern with baseline demand
        start_date: Start date for data generation
        end_date: End date for data generation
        festivals: List of festival events in the period
        skus_per_category: Number of SKUs to generate per category
        
    Returns:
        List of sales records
    """
    if festivals is None:
        festivals = []
    
    sales_records = []
    
    # Generate SKUs for each category
    category_skus = {}
    for cat_pattern in pattern.baseline_patterns:
        category = cat_pattern.category
        skus = [
            f"{pattern.business_type[:3].upper()}-{category[:3].upper()}-{i:03d}"
            for i in range(1, skus_per_category + 1)
        ]
        category_skus[category] = skus
    
    # Generate sales for each day
    current_date = start_date
    while current_date <= end_date:
        month = current_date.month
        seasonal_factor = pattern.seasonal_factors.get(month, 1.0)
        
        # Generate sales for each category
        for cat_pattern in pattern.baseline_patterns:
            category = cat_pattern.category
            
            # Calculate festival impact
            festival_multiplier = get_festival_impact(
                current_date,
                festivals,
                category,
                pattern.festival_multipliers,
            )
            
            # Generate sales for each SKU in this category
            for sku in category_skus[category]:
                # Not all SKUs sell every day (add some randomness)
                if random.random() < 0.7:  # 70% chance of sale
                    record = generate_sales_record(
                        date=current_date,
                        sku=sku,
                        category=category,
                        base_demand=cat_pattern.normal_demand / skus_per_category,
                        seasonal_factor=seasonal_factor,
                        festival_multiplier=festival_multiplier,
                        variance=cat_pattern.variance,
                    )
                    sales_records.append(record)
        
        current_date += timedelta(days=1)
    
    return sales_records


def generate_synthetic_sales(
    business_type: str,
    region: str = "north",
    days: int = 365,
    categories: List[str] = None,
    festivals: List[Dict[str, Any]] = None,
    skus_per_category: int = 3,
) -> List[Dict[str, Any]]:
    """
    Generate synthetic sales data for a business.
    
    Args:
        business_type: Type of business (grocery, apparel, electronics, general)
        region: Geographic region
        days: Number of days of data to generate
        categories: List of product categories (uses defaults if None)
        festivals: List of festival events (optional)
        skus_per_category: Number of SKUs per category
        
    Returns:
        List of sales records
    """
    # Generate pattern
    pattern = generate_synthetic_pattern(business_type, region, categories)
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days - 1)
    
    # Generate sales data
    return generate_sales_for_period(
        pattern=pattern,
        start_date=start_date,
        end_date=end_date,
        festivals=festivals,
        skus_per_category=skus_per_category,
    )
