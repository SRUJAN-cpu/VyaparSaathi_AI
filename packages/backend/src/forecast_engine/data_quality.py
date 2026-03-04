"""
Data quality assessment for forecasting

This module provides functions to assess data quality and determine
the appropriate forecasting methodology based on data availability.
"""

from typing import Dict, Any, Literal


def assess_data_quality(
    record_count: int,
    completeness: float,
    recency_days: int,
    consistency_score: float
) -> Dict[str, Any]:
    """
    Assess data quality based on multiple factors.
    
    Args:
        record_count: Number of historical records
        completeness: Percentage of complete records (0-1)
        recency_days: Days since last data point
        consistency_score: Data consistency score (0-1)
        
    Returns:
        Data quality assessment with score and rating
    """
    # Calculate component scores
    
    # Record count score (need at least 30 days of data for good quality)
    if record_count >= 90:
        count_score = 1.0
    elif record_count >= 30:
        count_score = 0.7
    elif record_count >= 14:
        count_score = 0.4
    else:
        count_score = 0.2
    
    # Completeness score (already 0-1)
    completeness_score = completeness
    
    # Recency score (data should be recent)
    if recency_days <= 7:
        recency_score = 1.0
    elif recency_days <= 30:
        recency_score = 0.8
    elif recency_days <= 90:
        recency_score = 0.5
    else:
        recency_score = 0.2
    
    # Consistency score (already 0-1)
    consistency = consistency_score
    
    # Weighted average
    weights = {
        'count': 0.3,
        'completeness': 0.3,
        'recency': 0.2,
        'consistency': 0.2
    }
    
    overall_score = (
        count_score * weights['count'] +
        completeness_score * weights['completeness'] +
        recency_score * weights['recency'] +
        consistency * weights['consistency']
    )
    
    # Determine quality rating
    if overall_score >= 0.7:
        quality = 'good'
    elif overall_score >= 0.4:
        quality = 'fair'
    else:
        quality = 'poor'
    
    return {
        'score': overall_score,
        'quality': quality,
        'components': {
            'recordCount': count_score,
            'completeness': completeness_score,
            'recency': recency_score,
            'consistency': consistency
        },
        'metrics': {
            'recordCount': record_count,
            'completeness': completeness,
            'recencyDays': recency_days,
            'consistencyScore': consistency_score
        }
    }


def determine_forecasting_method(
    data_quality_score: float,
    data_mode: Literal['structured', 'low-data']
) -> Literal['ml', 'pattern', 'hybrid']:
    """
    Determine the appropriate forecasting methodology.
    
    Args:
        data_quality_score: Overall data quality score (0-1)
        data_mode: Data mode ('structured' or 'low-data')
        
    Returns:
        Forecasting methodology: 'ml', 'pattern', or 'hybrid'
    """
    if data_mode == 'low-data':
        # Always use pattern-based for low-data mode
        return 'pattern'
    
    # For structured data mode, decide based on quality
    if data_quality_score >= 0.7:
        # High quality data - use ML
        return 'ml'
    elif data_quality_score >= 0.4:
        # Medium quality - use hybrid approach
        return 'hybrid'
    else:
        # Low quality - fall back to pattern-based
        return 'pattern'


def calculate_confidence_adjustment(
    data_quality_score: float,
    methodology: Literal['ml', 'pattern', 'hybrid']
) -> float:
    """
    Calculate confidence adjustment factor based on data quality and methodology.
    
    Args:
        data_quality_score: Overall data quality score (0-1)
        methodology: Forecasting methodology used
        
    Returns:
        Confidence adjustment factor (0-1)
    """
    # Base confidence by methodology
    base_confidence = {
        'ml': 0.85,
        'hybrid': 0.70,
        'pattern': 0.60
    }
    
    base = base_confidence.get(methodology, 0.60)
    
    # Adjust based on data quality
    # Higher quality data increases confidence
    adjustment = data_quality_score * 0.15
    
    # Final confidence (capped at 0.95)
    confidence = min(base + adjustment, 0.95)
    
    return confidence
