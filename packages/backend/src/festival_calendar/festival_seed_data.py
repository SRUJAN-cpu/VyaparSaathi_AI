"""
Festival calendar seed data for VyaparSaathi

This module contains seed data for major Indian festivals including:
- Diwali
- Eid (Eid-ul-Fitr and Eid-ul-Adha)
- Holi
- Pongal
- Onam
- Durga Puja

Each festival includes regional variations, demand multipliers by product category,
preparation days, and duration.
"""

from typing import Dict, List, Any

# Product categories used across festivals
CATEGORIES = {
    'SWEETS': 'sweets',
    'CLOTHING': 'clothing',
    'ELECTRONICS': 'electronics',
    'DECORATIONS': 'decorations',
    'GROCERIES': 'groceries',
    'GIFTS': 'gifts',
    'JEWELRY': 'jewelry',
    'FLOWERS': 'flowers',
    'PUJA_ITEMS': 'puja_items',
    'MEAT': 'meat',
    'DAIRY': 'dairy',
    'FRUITS': 'fruits',
    'VEGETABLES': 'vegetables',
    'FIREWORKS': 'fireworks',
    'COLORS': 'colors',
    'LAMPS': 'lamps',
}

# Festival seed data for 2024
FESTIVAL_SEED_DATA: List[Dict[str, Any]] = [
    # Diwali - Major pan-India festival
    {
        'festivalId': 'diwali-2024',
        'name': 'Diwali',
        'date': '2024-11-01',
        'region': ['north', 'south', 'east', 'west', 'central'],
        'category': 'religious',
        'demandMultipliers': {
            CATEGORIES['SWEETS']: 4.5,
            CATEGORIES['CLOTHING']: 3.2,
            CATEGORIES['ELECTRONICS']: 2.8,
            CATEGORIES['DECORATIONS']: 5.0,
            CATEGORIES['GROCERIES']: 2.5,
            CATEGORIES['GIFTS']: 3.8,
            CATEGORIES['JEWELRY']: 4.0,
            CATEGORIES['FIREWORKS']: 6.0,
            CATEGORIES['LAMPS']: 5.5,
            CATEGORIES['PUJA_ITEMS']: 4.2,
        },
        'duration': 5,
        'preparationDays': 14,
        'importance': 'major',
        'historicalImpact': {
            'averageIncrease': 350,
            'peakDayOffset': -1,
            'pattern': 'gradual',
        },
        'metadata': {
            'description': 'Festival of Lights, one of the most important Hindu festivals',
            'significance': 'Celebrates victory of light over darkness and good over evil',
            'activities': ['lighting diyas', 'fireworks', 'family gatherings', 'gift exchange', 'puja'],
            'associatedCategories': [
                CATEGORIES['SWEETS'],
                CATEGORIES['DECORATIONS'],
                CATEGORIES['FIREWORKS'],
                CATEGORIES['CLOTHING'],
                CATEGORIES['JEWELRY'],
            ],
        },
    },
    
    # Eid-ul-Fitr - Major Islamic festival
    {
        'festivalId': 'eid-ul-fitr-2024',
        'name': 'Eid-ul-Fitr',
        'date': '2024-04-11',
        'region': ['north', 'south', 'east', 'west', 'central'],
        'category': 'religious',
        'demandMultipliers': {
            CATEGORIES['SWEETS']: 4.0,
            CATEGORIES['CLOTHING']: 4.5,
            CATEGORIES['GROCERIES']: 3.5,
            CATEGORIES['GIFTS']: 3.2,
            CATEGORIES['MEAT']: 5.0,
            CATEGORIES['DAIRY']: 3.8,
            CATEGORIES['FRUITS']: 3.0,
            CATEGORIES['JEWELRY']: 3.5,
        },
        'duration': 3,
        'preparationDays': 7,
        'importance': 'major',
        'historicalImpact': {
            'averageIncrease': 280,
            'peakDayOffset': 0,
            'pattern': 'spike',
        },
        'metadata': {
            'description': 'Festival marking the end of Ramadan',
            'significance': 'Celebrates the conclusion of fasting month',
            'activities': ['prayers', 'feasting', 'charity', 'family visits', 'gift giving'],
            'associatedCategories': [
                CATEGORIES['CLOTHING'],
                CATEGORIES['MEAT'],
                CATEGORIES['SWEETS'],
                CATEGORIES['GIFTS'],
            ],
        },
    },
    
    # Eid-ul-Adha - Major Islamic festival
    {
        'festivalId': 'eid-ul-adha-2024',
        'name': 'Eid-ul-Adha',
        'date': '2024-06-17',
        'region': ['north', 'south', 'east', 'west', 'central'],
        'category': 'religious',
        'demandMultipliers': {
            CATEGORIES['MEAT']: 6.0,
            CATEGORIES['CLOTHING']: 3.8,
            CATEGORIES['GROCERIES']: 3.2,
            CATEGORIES['GIFTS']: 2.8,
            CATEGORIES['SWEETS']: 3.5,
            CATEGORIES['DAIRY']: 3.0,
        },
        'duration': 4,
        'preparationDays': 7,
        'importance': 'major',
        'historicalImpact': {
            'averageIncrease': 260,
            'peakDayOffset': 0,
            'pattern': 'spike',
        },
        'metadata': {
            'description': 'Festival of Sacrifice',
            'significance': 'Commemorates Prophet Ibrahim\'s willingness to sacrifice',
            'activities': ['prayers', 'animal sacrifice', 'charity', 'feasting', 'family gatherings'],
            'associatedCategories': [
                CATEGORIES['MEAT'],
                CATEGORIES['CLOTHING'],
                CATEGORIES['GROCERIES'],
            ],
        },
    },
    
    # Holi - Major North Indian festival
    {
        'festivalId': 'holi-2024',
        'name': 'Holi',
        'date': '2024-03-25',
        'region': ['north', 'central', 'west'],
        'category': 'religious',
        'demandMultipliers': {
            CATEGORIES['COLORS']: 8.0,
            CATEGORIES['SWEETS']: 3.5,
            CATEGORIES['GROCERIES']: 2.8,
            CATEGORIES['CLOTHING']: 2.2,
            CATEGORIES['DAIRY']: 3.2,
        },
        'duration': 2,
        'preparationDays': 5,
        'importance': 'major',
        'historicalImpact': {
            'averageIncrease': 220,
            'peakDayOffset': 0,
            'pattern': 'spike',
        },
        'metadata': {
            'description': 'Festival of Colors',
            'significance': 'Celebrates arrival of spring and victory of good over evil',
            'activities': ['playing with colors', 'water fights', 'music', 'dancing', 'feasting'],
            'associatedCategories': [
                CATEGORIES['COLORS'],
                CATEGORIES['SWEETS'],
                CATEGORIES['GROCERIES'],
            ],
        },
    },
    
    # Pongal - Major South Indian harvest festival
    {
        'festivalId': 'pongal-2024',
        'name': 'Pongal',
        'date': '2024-01-15',
        'region': ['south'],
        'category': 'harvest',
        'demandMultipliers': {
            CATEGORIES['GROCERIES']: 4.5,
            CATEGORIES['SWEETS']: 4.0,
            CATEGORIES['CLOTHING']: 3.0,
            CATEGORIES['PUJA_ITEMS']: 3.5,
            CATEGORIES['DAIRY']: 4.2,
            CATEGORIES['VEGETABLES']: 3.8,
            CATEGORIES['FRUITS']: 3.5,
        },
        'duration': 4,
        'preparationDays': 7,
        'importance': 'major',
        'historicalImpact': {
            'averageIncrease': 240,
            'peakDayOffset': 1,
            'pattern': 'sustained',
        },
        'metadata': {
            'description': 'Tamil harvest festival',
            'significance': 'Thanksgiving to Sun God for agricultural abundance',
            'activities': ['cooking pongal', 'decorating homes', 'cattle worship', 'family gatherings'],
            'associatedCategories': [
                CATEGORIES['GROCERIES'],
                CATEGORIES['SWEETS'],
                CATEGORIES['DAIRY'],
                CATEGORIES['PUJA_ITEMS'],
            ],
        },
    },
    
    # Onam - Major Kerala festival
    {
        'festivalId': 'onam-2024',
        'name': 'Onam',
        'date': '2024-09-15',
        'region': ['south'],
        'category': 'harvest',
        'demandMultipliers': {
            CATEGORIES['CLOTHING']: 4.5,
            CATEGORIES['FLOWERS']: 6.0,
            CATEGORIES['GROCERIES']: 4.0,
            CATEGORIES['SWEETS']: 3.8,
            CATEGORIES['VEGETABLES']: 4.2,
            CATEGORIES['FRUITS']: 3.5,
            CATEGORIES['GIFTS']: 3.0,
        },
        'duration': 10,
        'preparationDays': 10,
        'importance': 'major',
        'historicalImpact': {
            'averageIncrease': 280,
            'peakDayOffset': 9,
            'pattern': 'sustained',
        },
        'metadata': {
            'description': 'Kerala harvest festival',
            'significance': 'Celebrates homecoming of King Mahabali',
            'activities': ['flower arrangements', 'boat races', 'traditional dance', 'feasting', 'games'],
            'associatedCategories': [
                CATEGORIES['FLOWERS'],
                CATEGORIES['CLOTHING'],
                CATEGORIES['GROCERIES'],
                CATEGORIES['SWEETS'],
            ],
        },
    },
    
    # Durga Puja - Major East Indian festival
    {
        'festivalId': 'durga-puja-2024',
        'name': 'Durga Puja',
        'date': '2024-10-10',
        'region': ['east', 'north'],
        'category': 'religious',
        'demandMultipliers': {
            CATEGORIES['CLOTHING']: 4.2,
            CATEGORIES['SWEETS']: 5.0,
            CATEGORIES['DECORATIONS']: 4.5,
            CATEGORIES['PUJA_ITEMS']: 5.5,
            CATEGORIES['FLOWERS']: 5.0,
            CATEGORIES['GROCERIES']: 3.5,
            CATEGORIES['GIFTS']: 3.8,
            CATEGORIES['JEWELRY']: 3.5,
        },
        'duration': 5,
        'preparationDays': 14,
        'importance': 'major',
        'historicalImpact': {
            'averageIncrease': 320,
            'peakDayOffset': 4,
            'pattern': 'gradual',
        },
        'metadata': {
            'description': 'Worship of Goddess Durga',
            'significance': 'Celebrates victory of Goddess Durga over demon Mahishasura',
            'activities': ['pandal visits', 'cultural programs', 'feasting', 'shopping', 'family gatherings'],
            'associatedCategories': [
                CATEGORIES['SWEETS'],
                CATEGORIES['CLOTHING'],
                CATEGORIES['PUJA_ITEMS'],
                CATEGORIES['FLOWERS'],
                CATEGORIES['DECORATIONS'],
            ],
        },
    },
]

# Regional variations for festivals
REGIONAL_VARIATIONS: Dict[str, Dict[str, Any]] = {
    'diwali': {
        'north': {
            'emphasis': ['sweets', 'fireworks', 'jewelry'],
            'multiplierAdjustment': 1.1,
        },
        'south': {
            'emphasis': ['sweets', 'clothing', 'puja_items'],
            'multiplierAdjustment': 1.0,
        },
        'east': {
            'emphasis': ['sweets', 'decorations', 'puja_items'],
            'multiplierAdjustment': 1.05,
        },
        'west': {
            'emphasis': ['sweets', 'jewelry', 'clothing'],
            'multiplierAdjustment': 1.08,
        },
        'central': {
            'emphasis': ['sweets', 'decorations', 'clothing'],
            'multiplierAdjustment': 1.0,
        },
    },
    'eid-ul-fitr': {
        'north': {
            'emphasis': ['clothing', 'meat', 'sweets'],
            'multiplierAdjustment': 1.1,
        },
        'south': {
            'emphasis': ['clothing', 'sweets', 'groceries'],
            'multiplierAdjustment': 1.0,
        },
        'east': {
            'emphasis': ['clothing', 'sweets', 'meat'],
            'multiplierAdjustment': 1.0,
        },
        'west': {
            'emphasis': ['clothing', 'jewelry', 'sweets'],
            'multiplierAdjustment': 1.05,
        },
        'central': {
            'emphasis': ['clothing', 'meat', 'sweets'],
            'multiplierAdjustment': 1.0,
        },
    },
}


def get_festival_by_id(festival_id: str) -> Dict[str, Any] | None:
    """
    Get festival data by festival ID.
    
    Args:
        festival_id: Unique festival identifier
        
    Returns:
        Festival data dictionary or None if not found
    """
    for festival in FESTIVAL_SEED_DATA:
        if festival['festivalId'] == festival_id:
            return festival
    return None


def get_festivals_by_region(region: str) -> List[Dict[str, Any]]:
    """
    Get all festivals for a specific region.
    
    Args:
        region: Region identifier (north, south, east, west, central)
        
    Returns:
        List of festival data dictionaries
    """
    return [
        festival for festival in FESTIVAL_SEED_DATA
        if region in festival['region']
    ]


def get_festivals_by_date_range(start_date: str, end_date: str) -> List[Dict[str, Any]]:
    """
    Get festivals within a date range.
    
    Args:
        start_date: Start date in ISO format (YYYY-MM-DD)
        end_date: End date in ISO format (YYYY-MM-DD)
        
    Returns:
        List of festival data dictionaries
    """
    return [
        festival for festival in FESTIVAL_SEED_DATA
        if start_date <= festival['date'] <= end_date
    ]


def apply_regional_variation(
    festival: Dict[str, Any],
    region: str
) -> Dict[str, Any]:
    """
    Apply regional variations to festival demand multipliers.
    
    Args:
        festival: Base festival data
        region: Target region
        
    Returns:
        Festival data with regional adjustments applied
    """
    festival_name = festival['name'].lower().replace(' ', '-').replace("'", '')
    
    if festival_name not in REGIONAL_VARIATIONS:
        return festival
    
    regional_data = REGIONAL_VARIATIONS[festival_name].get(region)
    if not regional_data:
        return festival
    
    # Create a copy to avoid modifying original
    adjusted_festival = festival.copy()
    adjusted_festival['demandMultipliers'] = festival['demandMultipliers'].copy()
    
    # Apply regional multiplier adjustment
    adjustment = regional_data['multiplierAdjustment']
    for category in adjusted_festival['demandMultipliers']:
        adjusted_festival['demandMultipliers'][category] *= adjustment
    
    return adjusted_festival
