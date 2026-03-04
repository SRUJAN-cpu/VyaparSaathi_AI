"""
Reorder recommendation engine for inventory management.

This module calculates suggested reorder quantities, determines action types,
assigns urgency levels, and provides reasoning for recommendations.
"""

from typing import Dict, List, Any, Optional


def calculate_suggested_quantity(
    demand_forecast: List[Dict[str, Any]],
    current_stock: int,
    safety_stock: int,
    lead_time_days: int
) -> int:
    """
    Calculate suggested reorder quantity based on forecast and lead time.
    
    Uses the formula:
    Reorder Quantity = (Demand during lead time + Safety stock) - Current stock
    
    Args:
        demand_forecast: List of daily demand predictions
        current_stock: Current inventory level
        safety_stock: Minimum safety stock level
        lead_time_days: Supplier lead time in days
        
    Returns:
        Suggested reorder quantity (0 if no reorder needed)
    """
    if not demand_forecast:
        return 0
    
    # Calculate demand during lead time
    lead_time_demand = 0
    for i, day_forecast in enumerate(demand_forecast):
        if i < lead_time_days:
            lead_time_demand += day_forecast.get('demandForecast', 0)
        else:
            break
    
    # Calculate total demand over forecast period
    total_forecast_demand = sum(day.get('demandForecast', 0) for day in demand_forecast)
    
    # Calculate reorder point (demand during lead time + safety stock)
    reorder_point = lead_time_demand + safety_stock
    
    # Calculate suggested quantity
    # Order enough to cover forecast period plus safety stock
    suggested_quantity = max(0, (total_forecast_demand + safety_stock) - current_stock)
    
    return round(suggested_quantity)


def determine_action(
    stockout_risk: Dict[str, Any],
    overstock_risk: Dict[str, Any],
    current_stock: int,
    suggested_quantity: int
) -> str:
    """
    Determine recommended action based on risk assessment.
    
    Args:
        stockout_risk: Stockout risk dictionary
        overstock_risk: Overstock risk dictionary
        current_stock: Current inventory level
        suggested_quantity: Calculated reorder quantity
        
    Returns:
        Action: 'reorder', 'reduce', or 'maintain'
    """
    stockout_probability = stockout_risk.get('probability', 0)
    overstock_probability = overstock_risk.get('probability', 0)
    
    # High stockout risk - recommend reorder
    if stockout_probability >= 0.6:
        return 'reorder'
    
    # High overstock risk - recommend reduce
    if overstock_probability >= 0.6:
        return 'reduce'
    
    # Medium stockout risk with low overstock - recommend reorder
    if stockout_probability >= 0.3 and overstock_probability < 0.3:
        return 'reorder'
    
    # Medium overstock risk with low stockout - recommend reduce
    if overstock_probability >= 0.3 and stockout_probability < 0.3:
        return 'reduce'
    
    # Balanced risks or low risks - maintain current levels
    return 'maintain'


def determine_urgency(
    action: str,
    stockout_risk: Dict[str, Any],
    overstock_risk: Dict[str, Any]
) -> str:
    """
    Determine urgency level based on action and risk levels.
    
    Args:
        action: Recommended action ('reorder', 'reduce', 'maintain')
        stockout_risk: Stockout risk dictionary
        overstock_risk: Overstock risk dictionary
        
    Returns:
        Urgency: 'low', 'medium', or 'high'
    """
    days_until_stockout = stockout_risk.get('daysUntilStockout', float('inf'))
    stockout_probability = stockout_risk.get('probability', 0)
    overstock_probability = overstock_risk.get('probability', 0)
    
    if action == 'reorder':
        # Urgency based on days until stockout
        if days_until_stockout <= 3:
            return 'high'
        elif days_until_stockout <= 7:
            return 'medium'
        elif stockout_probability >= 0.6:
            return 'medium'
        else:
            return 'low'
    
    elif action == 'reduce':
        # Urgency based on overstock probability
        if overstock_probability >= 0.8:
            return 'high'
        elif overstock_probability >= 0.6:
            return 'medium'
        else:
            return 'low'
    
    else:  # maintain
        return 'low'


def generate_reasoning(
    action: str,
    risk_assessment: Dict[str, Any],
    suggested_quantity: int,
    confidence: float
) -> List[str]:
    """
    Generate reasoning for the recommendation.
    
    Args:
        action: Recommended action
        risk_assessment: Complete risk assessment dictionary
        suggested_quantity: Calculated reorder quantity
        confidence: Confidence score for the recommendation
        
    Returns:
        List of reasoning strings
    """
    reasoning = []
    
    stockout_risk = risk_assessment.get('stockoutRisk', {})
    overstock_risk = risk_assessment.get('overstockRisk', {})
    current_stock = risk_assessment.get('currentStock', 0)
    
    stockout_probability = stockout_risk.get('probability', 0)
    overstock_probability = overstock_risk.get('probability', 0)
    days_until_stockout = stockout_risk.get('daysUntilStockout', float('inf'))
    excess_units = overstock_risk.get('excessUnits', 0)
    
    if action == 'reorder':
        reasoning.append(
            f"Stockout risk is {stockout_probability:.0%} with current inventory of {current_stock} units."
        )
        
        if days_until_stockout != float('inf'):
            reasoning.append(
                f"Current stock expected to last approximately {days_until_stockout} days based on demand forecast."
            )
        
        reasoning.append(
            f"Recommended order quantity: {suggested_quantity} units to maintain adequate inventory levels."
        )
        
        if overstock_probability > 0.3:
            reasoning.append(
                f"Note: Overstock risk is {overstock_probability:.0%}. Monitor inventory levels after reorder."
            )
    
    elif action == 'reduce':
        reasoning.append(
            f"Overstock risk is {overstock_probability:.0%} with {excess_units:.0f} excess units."
        )
        
        reasoning.append(
            f"Current inventory of {current_stock} units exceeds forecasted demand."
        )
        
        reasoning.append(
            "Consider reducing future order quantities or implementing promotional strategies."
        )
        
        parameters = risk_assessment.get('parameters', {})
        if parameters.get('shelfLifeDays'):
            reasoning.append(
                f"Perishable item with {parameters['shelfLifeDays']}-day shelf life requires urgent action."
            )
    
    else:  # maintain
        reasoning.append(
            f"Current inventory of {current_stock} units is well-balanced with forecasted demand."
        )
        
        reasoning.append(
            f"Stockout risk: {stockout_probability:.0%}, Overstock risk: {overstock_probability:.0%}."
        )
        
        reasoning.append(
            "Continue monitoring inventory levels and adjust as demand patterns change."
        )
    
    # Add confidence note
    if confidence < 0.6:
        reasoning.append(
            f"Recommendation confidence is {confidence:.0%}. Consider reviewing forecast assumptions."
        )
    
    return reasoning


def calculate_confidence(
    risk_assessment: Dict[str, Any],
    data_quality: Optional[Dict[str, Any]] = None
) -> float:
    """
    Calculate confidence indicator for the recommendation.
    
    Confidence is based on:
    - Data quality (if available)
    - Forecast period coverage
    - Risk level clarity (not borderline)
    
    Args:
        risk_assessment: Risk assessment dictionary
        data_quality: Optional data quality assessment
        
    Returns:
        Confidence score (0-1)
    """
    confidence = 0.7  # Base confidence
    
    # Adjust based on data quality
    if data_quality:
        quality_score = data_quality.get('score', 0.5)
        confidence = confidence * (0.5 + 0.5 * quality_score)
    
    # Adjust based on forecast period
    forecast_days = risk_assessment.get('forecastPeriodDays', 0)
    if forecast_days >= 14:
        confidence *= 1.1  # More data points increase confidence
    elif forecast_days < 7:
        confidence *= 0.9  # Less data points decrease confidence
    
    # Adjust based on risk clarity
    stockout_risk = risk_assessment.get('stockoutRisk', {})
    overstock_risk = risk_assessment.get('overstockRisk', {})
    
    stockout_prob = stockout_risk.get('probability', 0)
    overstock_prob = overstock_risk.get('probability', 0)
    
    # Reduce confidence if risks are borderline (around thresholds)
    if 0.25 <= stockout_prob <= 0.35 or 0.55 <= stockout_prob <= 0.65:
        confidence *= 0.9
    
    if 0.25 <= overstock_prob <= 0.35 or 0.55 <= overstock_prob <= 0.65:
        confidence *= 0.9
    
    # Cap confidence at 0.95
    return min(0.95, round(confidence, 2))


def calculate_reorder_recommendation(
    risk_assessment: Dict[str, Any],
    demand_forecast: List[Dict[str, Any]],
    data_quality: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Calculate comprehensive reorder recommendation.
    
    This is the main function that generates a complete ReorderRecommendation
    including action, suggested quantity, urgency, reasoning, and confidence.
    
    Args:
        risk_assessment: Risk assessment dictionary from calculate_risk_assessment
        demand_forecast: List of daily demand predictions
        data_quality: Optional data quality assessment
        
    Returns:
        ReorderRecommendation dictionary
    """
    stockout_risk = risk_assessment.get('stockoutRisk', {})
    overstock_risk = risk_assessment.get('overstockRisk', {})
    current_stock = risk_assessment.get('currentStock', 0)
    parameters = risk_assessment.get('parameters', {})
    
    safety_stock = parameters.get('safetyStock', 0)
    lead_time_days = parameters.get('leadTimeDays', 7)
    
    # Calculate suggested quantity
    suggested_quantity = calculate_suggested_quantity(
        demand_forecast=demand_forecast,
        current_stock=current_stock,
        safety_stock=safety_stock,
        lead_time_days=lead_time_days
    )
    
    # Determine action
    action = determine_action(
        stockout_risk=stockout_risk,
        overstock_risk=overstock_risk,
        current_stock=current_stock,
        suggested_quantity=suggested_quantity
    )
    
    # Determine urgency
    urgency = determine_urgency(
        action=action,
        stockout_risk=stockout_risk,
        overstock_risk=overstock_risk
    )
    
    # Calculate confidence
    confidence = calculate_confidence(
        risk_assessment=risk_assessment,
        data_quality=data_quality
    )
    
    # Generate reasoning
    reasoning = generate_reasoning(
        action=action,
        risk_assessment=risk_assessment,
        suggested_quantity=suggested_quantity,
        confidence=confidence
    )
    
    # Build recommendation
    recommendation = {
        'action': action,
        'suggestedQuantity': suggested_quantity if action == 'reorder' else 0,
        'urgency': urgency,
        'reasoning': reasoning,
        'confidence': confidence
    }
    
    return recommendation
