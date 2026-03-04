"""
Festival impact calculation utilities

This module provides functions to calculate festival impact on demand,
handle overlapping festivals, and support multi-day festival periods.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
from decimal import Decimal


def parse_date(date_str: str) -> datetime:
    """
    Parse ISO date string to datetime object.
    
    Args:
        date_str: Date string in ISO format (YYYY-MM-DD)
        
    Returns:
        datetime object
    """
    return datetime.fromisoformat(date_str)


def get_festival_date_range(festival: Dict[str, Any