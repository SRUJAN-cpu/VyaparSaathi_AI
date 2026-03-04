"""
Alert generation logic for risk assessment.

This module generates alerts when risk levels exceed configurable thresholds,
assigns severity indicators, and provides actionable recommendations.
"""

from typing import Dict, List, Any, Optional


# Configurable risk thresholds
RISK_THRESHOLDS = {
    'low': 0.30,      # Risk < 30%
    'medium': 0.30,   # 30% <= Risk < 60%
    'high': 0.60      # Risk >= 60%
}


def get_risk_level(probability: float) -> str:
    """
    Determine risk level based on probability.
    
    Args:
        probability: Risk probability (0-1)
        
    Returns:
        Risk level: 'low', 'medium', or 'high'
    """
    if probability >= RISK_THRESHOLDS['high']:
        return 'high'
    elif probability >= RISK_THRESHOLDS['medium']:
        return 'medium'
    else:
        return 'low'


def generate_stockout_recommendations(
    risk_assessment: Dict[str, Any]
) -> List[str]:
    """
    Generate actionable recommendations for stockout risk.
    
    Args:
        risk_assessment: Risk assessment dictionary with stockout risk data
        
    Returns:
        List of recommendation strings
    """
    recommendations = []
    stockout_risk = risk_assessment.get('stockoutRisk', {})
    probability = stockout_risk.get('probability', 0)
    days_until_stockout = stockout_risk.get('daysUntilStockout', float('inf'))
    potential_lost_sales = stockout_risk.get('potentialLostSales', 0)
    
    if probability >= RISK_THRESHOLDS['high']:
        if days_until_stockout <= 3:
            recommendations.append(
                f"URGENT: Stock expected to run out in {days_until_stockout} days. "
                "Place emergency order immediately."
            )
        elif days_until_stockout <= 7:
            recommendations.append(
                f"Stock expected to run out in {days_until_stockout} days. "
                "Initiate reorder process now to avoid stockout."
            )
        else:
            recommendations.append(
                f"Stock will run out in {days_until_stockout} days. "
                "Plan reorder to maintain inventory levels."
            )
        
        if potential_lost_sales > 0:
            recommendations.append(
                f"Potential lost sales: {potential_lost_sales:.0f} units. "
                "Consider expedited shipping to minimize revenue loss."
            )
    
    elif probability >= RISK_THRESHOLDS['medium']:
        recommendations.append(
            "Monitor inventory levels closely. "
            "Prepare reorder documentation in case demand increases."
        )
        
        if days_until_stockout < 14:
            recommendations.append(
                f"Current stock may last approximately {days_until_stockout} days. "
                "Review supplier lead times."
            )
    
    else:
        recommendations.append(
            "Inventory levels are adequate for forecasted demand. "
            "Continue regular monitoring."
        )
    
    return recommendations


def generate_overstock_recommendations(
    risk_assessment: Dict[str, Any]
) -> List[str]:
    """
    Generate actionable recommendations for overstock risk.
    
    Args:
        risk_assessment: Risk assessment dictionary with overstock risk data
        
    Returns:
        List of recommendation strings
    """
    recommendations = []
    overstock_risk = risk_assessment.get('overstockRisk', {})
    probability = overstock_risk.get('probability', 0)
    excess_units = overstock_risk.get('excessUnits', 0)
    carrying_cost = overstock_risk.get('carryingCost', 0)
    
    parameters = risk_assessment.get('parameters', {})
    shelf_life_days = parameters.get('shelfLifeDays')
    
    if probability >= RISK_THRESHOLDS['high']:
        if excess_units > 0:
            recommendations.append(
                f"Excess inventory detected: {excess_units:.0f} units beyond forecasted demand."
            )
        
        if shelf_life_days is not None:
            recommendations.append(
                f"Perishable item with {shelf_life_days}-day shelf life. "
                "Consider promotional pricing or discounts to move inventory."
            )
        else:
            recommendations.append(
                "Consider reducing future order quantities to optimize inventory levels."
            )
        
        if carrying_cost > 0:
            recommendations.append(
                f"Estimated carrying cost for excess inventory: ${carrying_cost:.2f}. "
                "Evaluate storage optimization opportunities."
            )
    
    elif probability >= RISK_THRESHOLDS['medium']:
        recommendations.append(
            "Inventory levels slightly exceed forecasted demand. "
            "Monitor sales velocity and adjust future orders accordingly."
        )
        
        if shelf_life_days is not None:
            recommendations.append(
                "Track expiration dates closely for perishable items."
            )
    
    else:
        recommendations.append(
            "Inventory levels are well-balanced with demand forecast."
        )
    
    return recommendations


def generate_alert(
    risk_assessment: Dict[str, Any],
    alert_type: str = 'both',
    custom_thresholds: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Generate alert with severity indicators and recommendations.
    
    Args:
        risk_assessment: Risk assessment dictionary
        alert_type: Type of alert to generate ('stockout', 'overstock', or 'both')
        custom_thresholds: Optional custom risk thresholds
        
    Returns:
        Alert dictionary with severity, recommendations, and metadata
    """
    # Use custom thresholds if provided
    thresholds = custom_thresholds if custom_thresholds else RISK_THRESHOLDS
    
    stockout_risk = risk_assessment.get('stockoutRisk', {})
    overstock_risk = risk_assessment.get('overstockRisk', {})
    
    stockout_probability = stockout_risk.get('probability', 0)
    overstock_probability = overstock_risk.get('probability', 0)
    
    # Determine which alerts to generate
    generate_stockout_alert = (
        alert_type in ['stockout', 'both'] and
        stockout_probability >= thresholds['low']
    )
    
    generate_overstock_alert = (
        alert_type in ['overstock', 'both'] and
        overstock_probability >= thresholds['low']
    )
    
    # Determine overall severity (highest of the two risks)
    stockout_level = get_risk_level(stockout_probability) if generate_stockout_alert else 'low'
    overstock_level = get_risk_level(overstock_probability) if generate_overstock_alert else 'low'
    
    severity_order = {'low': 0, 'medium': 1, 'high': 2}
    overall_severity = max(
        stockout_level,
        overstock_level,
        key=lambda x: severity_order[x]
    )
    
    # Generate recommendations
    recommendations = []
    
    if generate_stockout_alert:
        recommendations.extend(generate_stockout_recommendations(risk_assessment))
    
    if generate_overstock_alert:
        recommendations.extend(generate_overstock_recommendations(risk_assessment))
    
    # Build alert
    alert = {
        'sku': risk_assessment.get('sku'),
        'category': risk_assessment.get('category'),
        'severity': overall_severity,
        'alertType': alert_type,
        'stockoutAlert': {
            'triggered': generate_stockout_alert,
            'level': stockout_level,
            'probability': stockout_probability
        } if generate_stockout_alert else None,
        'overstockAlert': {
            'triggered': generate_overstock_alert,
            'level': overstock_level,
            'probability': overstock_probability
        } if generate_overstock_alert else None,
        'recommendations': recommendations,
        'generatedAt': risk_assessment.get('assessmentDate'),
        'thresholds': thresholds
    }
    
    # Remove None values
    alert = {k: v for k, v in alert.items() if v is not None}
    
    return alert
