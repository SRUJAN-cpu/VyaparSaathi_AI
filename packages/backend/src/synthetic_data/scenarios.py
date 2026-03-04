"""
Sample scenarios for different retailer types.

Provides pre-configured scenarios for grocery, apparel, and electronics stores
with realistic data covering pre-festival, during-festival, and post-festival periods.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any
from .pattern_generator import generate_synthetic_pattern
from .sales_generator import generate_sales_for_period


def get_diwali_festivals(year: int = None) -> List[Dict[str, Any]]:
    """
    Get Diwali festival data for scenario generation.
    
    Args:
        year: Year for festival (defaults to current year)
        
    Returns:
        List of festival events
    """
    if year is None:
        year = datetime.now().year
    
    # Diwali typically falls in October/November
    # Using approximate dates for demonstration
    diwali_date = datetime(year, 10, 24)
    
    return [
        {
            "festivalId": f"diwali-{year}",
            "name": "Diwali",
            "date": diwali_date.strftime("%Y-%m-%d"),
            "region": ["north", "south", "east", "west", "central"],
            "category": "religious",
            "duration": 5,
            "preparationDays": 14,
        }
    ]


def get_eid_festivals(year: int = None) -> List[Dict[str, Any]]:
    """
    Get Eid festival data for scenario generation.
    
    Args:
        year: Year for festival (defaults to current year)
        
    Returns:
        List of festival events
    """
    if year is None:
        year = datetime.now().year
    
    # Eid dates vary by lunar calendar, using approximate dates
    eid_date = datetime(year, 4, 22)
    
    return [
        {
            "festivalId": f"eid-{year}",
            "name": "Eid",
            "date": eid_date.strftime("%Y-%m-%d"),
            "region": ["north", "south", "east", "west", "central"],
            "category": "religious",
            "duration": 3,
            "preparationDays": 10,
        }
    ]


def get_holi_festivals(year: int = None) -> List[Dict[str, Any]]:
    """
    Get Holi festival data for scenario generation.
    
    Args:
        year: Year for festival (defaults to current year)
        
    Returns:
        List of festival events
    """
    if year is None:
        year = datetime.now().year
    
    # Holi typically falls in March
    holi_date = datetime(year, 3, 8)
    
    return [
        {
            "festivalId": f"holi-{year}",
            "name": "Holi",
            "date": holi_date.strftime("%Y-%m-%d"),
            "region": ["north", "central"],
            "category": "cultural",
            "duration": 2,
            "preparationDays": 7,
        }
    ]


def generate_grocery_scenario(
    include_festivals: bool = True,
    days: int = 90,
) -> Dict[str, Any]:
    """
    Generate sample scenario for a grocery store.
    
    Includes data for staples, vegetables, dairy, snacks, beverages, and sweets
    with realistic demand patterns and festival impacts.
    
    Args:
        include_festivals: Whether to include festival periods
        days: Number of days of data to generate
        
    Returns:
        Dictionary with scenario metadata and sales data
    """
    business_type = "grocery"
    region = "north"
    
    # Generate pattern
    pattern = generate_synthetic_pattern(business_type, region)
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days - 1)
    
    # Get festivals if requested
    festivals = []
    if include_festivals:
        year = end_date.year
        # Check which festivals fall in the date range
        all_festivals = (
            get_diwali_festivals(year) +
            get_eid_festivals(year) +
            get_holi_festivals(year)
        )
        
        for festival in all_festivals:
            fest_date = datetime.strptime(festival["date"], "%Y-%m-%d")
            if start_date <= fest_date <= end_date:
                festivals.append(festival)
    
    # Generate sales data
    sales_data = generate_sales_for_period(
        pattern=pattern,
        start_date=start_date,
        end_date=end_date,
        festivals=festivals,
        skus_per_category=5,
    )
    
    return {
        "scenario_name": "Grocery Store - Festival Season",
        "business_type": business_type,
        "region": region,
        "description": (
            "A medium-sized grocery store in North India selling staples, "
            "vegetables, dairy, snacks, beverages, and sweets. Data includes "
            "pre-festival, during-festival, and post-festival periods."
        ),
        "date_range": {
            "start": start_date.strftime("%Y-%m-%d"),
            "end": end_date.strftime("%Y-%m-%d"),
            "days": days,
        },
        "festivals": festivals,
        "categories": [p.category for p in pattern.baseline_patterns],
        "total_records": len(sales_data),
        "sales_data": sales_data,
    }


def generate_apparel_scenario(
    include_festivals: bool = True,
    days: int = 90,
) -> Dict[str, Any]:
    """
    Generate sample scenario for an apparel store.
    
    Includes data for traditional, casual, formal, kids, and accessories
    with strong festival demand patterns.
    
    Args:
        include_festivals: Whether to include festival periods
        days: Number of days of data to generate
        
    Returns:
        Dictionary with scenario metadata and sales data
    """
    business_type = "apparel"
    region = "west"
    
    # Generate pattern
    pattern = generate_synthetic_pattern(business_type, region)
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days - 1)
    
    # Get festivals if requested
    festivals = []
    if include_festivals:
        year = end_date.year
        all_festivals = (
            get_diwali_festivals(year) +
            get_eid_festivals(year) +
            get_holi_festivals(year)
        )
        
        for festival in all_festivals:
            fest_date = datetime.strptime(festival["date"], "%Y-%m-%d")
            if start_date <= fest_date <= end_date:
                festivals.append(festival)
    
    # Generate sales data
    sales_data = generate_sales_for_period(
        pattern=pattern,
        start_date=start_date,
        end_date=end_date,
        festivals=festivals,
        skus_per_category=4,
    )
    
    return {
        "scenario_name": "Apparel Store - Wedding & Festival Season",
        "business_type": business_type,
        "region": region,
        "description": (
            "A fashion boutique in West India selling traditional wear, casual "
            "clothing, formal attire, kids' wear, and accessories. Strong demand "
            "during festival and wedding seasons."
        ),
        "date_range": {
            "start": start_date.strftime("%Y-%m-%d"),
            "end": end_date.strftime("%Y-%m-%d"),
            "days": days,
        },
        "festivals": festivals,
        "categories": [p.category for p in pattern.baseline_patterns],
        "total_records": len(sales_data),
        "sales_data": sales_data,
    }


def generate_electronics_scenario(
    include_festivals: bool = True,
    days: int = 90,
) -> Dict[str, Any]:
    """
    Generate sample scenario for an electronics store.
    
    Includes data for mobiles, laptops, TVs, appliances, and accessories
    with peak demand during Diwali season.
    
    Args:
        include_festivals: Whether to include festival periods
        days: Number of days of data to generate
        
    Returns:
        Dictionary with scenario metadata and sales data
    """
    business_type = "electronics"
    region = "south"
    
    # Generate pattern
    pattern = generate_synthetic_pattern(business_type, region)
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days - 1)
    
    # Get festivals if requested
    festivals = []
    if include_festivals:
        year = end_date.year
        all_festivals = (
            get_diwali_festivals(year) +
            get_eid_festivals(year)
        )
        
        for festival in all_festivals:
            fest_date = datetime.strptime(festival["date"], "%Y-%m-%d")
            if start_date <= fest_date <= end_date:
                festivals.append(festival)
    
    # Generate sales data
    sales_data = generate_sales_for_period(
        pattern=pattern,
        start_date=start_date,
        end_date=end_date,
        festivals=festivals,
        skus_per_category=3,
    )
    
    return {
        "scenario_name": "Electronics Store - Diwali Sale Season",
        "business_type": business_type,
        "region": region,
        "description": (
            "An electronics retail store in South India selling mobile phones, "
            "laptops, TVs, home appliances, and accessories. Peak sales during "
            "Diwali with significant festival offers."
        ),
        "date_range": {
            "start": start_date.strftime("%Y-%m-%d"),
            "end": end_date.strftime("%Y-%m-%d"),
            "days": days,
        },
        "festivals": festivals,
        "categories": [p.category for p in pattern.baseline_patterns],
        "total_records": len(sales_data),
        "sales_data": sales_data,
    }


def generate_all_scenarios(days: int = 90) -> Dict[str, Dict[str, Any]]:
    """
    Generate all sample scenarios.
    
    Args:
        days: Number of days of data to generate for each scenario
        
    Returns:
        Dictionary mapping scenario names to scenario data
    """
    return {
        "grocery": generate_grocery_scenario(include_festivals=True, days=days),
        "apparel": generate_apparel_scenario(include_festivals=True, days=days),
        "electronics": generate_electronics_scenario(include_festivals=True, days=days),
    }
