"""
Prompt templates for different explanation contexts.

This module provides prompt templates for generating explanations
for forecasts, risk assessments, recommendations, and conversational queries.
"""

from typing import Dict, Any, List, Optional


# System prompt for all explanations
SYSTEM_PROMPT = """You are VyaparSaathi's AI assistant, helping small and mid-size retailers understand their inventory forecasts and risks. Your role is to:

1. Explain complex forecasting and risk concepts in simple, non-technical language
2. Use examples and analogies that resonate with small business owners
3. Be concise and actionable - focus on what matters for decision-making
4. Always communicate assumptions and limitations clearly
5. Provide practical next steps when appropriate

Remember: Your audience may have basic digital literacy and no data science background. Avoid jargon and technical terms. Use everyday language."""


def create_forecast_explanation_prompt(
    forecast_data: Dict[str, Any],
    user_context: Optional[Dict[str, Any]] = None,
    complexity: str = 'simple'
) -> str:
    """
    Create prompt for forecast explanation.
    
    Args:
        forecast_data: Forecast result data including predictions, methodology, etc.
        user_context: Optional user profile and business context
        complexity: 'simple' or 'detailed'
        
    Returns:
        Formatted prompt string
    """
    sku = forecast_data.get('sku', 'Unknown')
    category = forecast_data.get('category', 'Unknown')
    predictions = forecast_data.get('predictions', [])
    confidence = forecast_data.get('confidence', 0.0)
    methodology = forecast_data.get('methodology', 'unknown')
    
    # Calculate summary statistics
    if predictions:
        total_demand = sum(p.get('demandForecast', 0) for p in predictions)
        avg_daily_demand = total_demand / len(predictions) if predictions else 0
        peak_demand = max(p.get('demandForecast', 0) for p in predictions)
        peak_date = next((p.get('date') for p in predictions if p.get('demandForecast') == peak_demand), None)
    else:
        total_demand = 0
        avg_daily_demand = 0
        peak_demand = 0
        peak_date = None
    
    # Build context about festivals
    festival_info = ""
    festivals = [p for p in predictions if p.get('festivalMultiplier', 1.0) > 1.0]
    if festivals:
        festival_dates = [p.get('date') for p in festivals[:3]]  # First 3 festival days
        festival_info = f"\nFestival periods detected on: {', '.join(festival_dates)}"
    
    # Build user context
    user_info = ""
    if user_context:
        business_type = user_context.get('businessInfo', {}).get('type', '')
        location = user_context.get('businessInfo', {}).get('location', {})
        if business_type:
            user_info = f"\nBusiness type: {business_type}"
        if location.get('city'):
            user_info += f"\nLocation: {location.get('city')}, {location.get('state', '')}"
    
    detail_level = "detailed" if complexity == 'detailed' else "simple"
    
    prompt = f"""Explain this demand forecast to a small retailer in simple language:

Product: {sku} ({category})
Forecast Period: {len(predictions)} days
Total Expected Demand: {total_demand:.0f} units
Average Daily Demand: {avg_daily_demand:.1f} units
Peak Demand: {peak_demand:.0f} units on {peak_date}
Confidence Level: {confidence * 100:.0f}%
Forecasting Method: {methodology}{festival_info}{user_info}

Please provide a {detail_level} explanation that includes:

1. **Key Insights**: What are the 2-3 most important things to know about this forecast?
2. **Assumptions**: What assumptions were made in creating this forecast?
3. **Limitations**: What should the retailer be cautious about?
4. **Confidence**: What does the {confidence * 100:.0f}% confidence level mean in practical terms?
5. **Next Steps**: What should the retailer do with this information?

Use simple language, avoid technical jargon, and be concise. Focus on actionable insights."""

    return prompt


def create_risk_explanation_prompt(
    risk_data: Dict[str, Any],
    user_context: Optional[Dict[str, Any]] = None,
    complexity: str = 'simple'
) -> str:
    """
    Create prompt for risk assessment explanation.
    
    Args:
        risk_data: Risk assessment data including stockout/overstock risks
        user_context: Optional user profile and business context
        complexity: 'simple' or 'detailed'
        
    Returns:
        Formatted prompt string
    """
    sku = risk_data.get('sku', 'Unknown')
    category = risk_data.get('category', 'Unknown')
    current_stock = risk_data.get('currentStock', 0)
    
    stockout_risk = risk_data.get('stockoutRisk', {})
    stockout_prob = stockout_risk.get('probability', 0.0)
    days_until_stockout = stockout_risk.get('daysUntilStockout', 0)
    potential_lost_sales = stockout_risk.get('potentialLostSales', 0)
    
    overstock_risk = risk_data.get('overstockRisk', {})
    overstock_prob = overstock_risk.get('probability', 0.0)
    excess_units = overstock_risk.get('excessUnits', 0)
    carrying_cost = overstock_risk.get('carryingCost', 0.0)
    
    # Determine primary risk
    if stockout_prob > overstock_prob:
        primary_risk = "stockout"
        risk_level = "high" if stockout_prob > 0.6 else "medium" if stockout_prob > 0.3 else "low"
    else:
        primary_risk = "overstock"
        risk_level = "high" if overstock_prob > 0.6 else "medium" if overstock_prob > 0.3 else "low"
    
    detail_level = "detailed" if complexity == 'detailed' else "simple"
    
    prompt = f"""Explain this inventory risk assessment to a small retailer in simple language:

Product: {sku} ({category})
Current Stock: {current_stock} units

Stockout Risk:
- Probability: {stockout_prob * 100:.0f}%
- Days Until Stockout: {days_until_stockout}
- Potential Lost Sales: {potential_lost_sales:.0f} units

Overstock Risk:
- Probability: {overstock_prob * 100:.0f}%
- Excess Units: {excess_units:.0f}
- Carrying Cost: ₹{carrying_cost:.2f}

Primary Risk: {primary_risk} ({risk_level} level)

Please provide a {detail_level} explanation that includes:

1. **Risk Summary**: What is the main risk this retailer faces with this product?
2. **Why This Risk**: What factors are contributing to this risk?
3. **Impact**: What could happen if this risk materializes?
4. **Confidence**: How certain are we about this assessment?
5. **Next Steps**: What specific actions should the retailer take?

Use simple language, avoid technical jargon, and focus on practical implications."""

    return prompt


def create_recommendation_explanation_prompt(
    recommendation_data: Dict[str, Any],
    risk_data: Optional[Dict[str, Any]] = None,
    user_context: Optional[Dict[str, Any]] = None,
    complexity: str = 'simple'
) -> str:
    """
    Create prompt for reorder recommendation explanation.
    
    Args:
        recommendation_data: Reorder recommendation data
        risk_data: Optional risk assessment data for context
        user_context: Optional user profile and business context
        complexity: 'simple' or 'detailed'
        
    Returns:
        Formatted prompt string
    """
    action = recommendation_data.get('action', 'maintain')
    suggested_quantity = recommendation_data.get('suggestedQuantity', 0)
    urgency = recommendation_data.get('urgency', 'low')
    reasoning = recommendation_data.get('reasoning', [])
    confidence = recommendation_data.get('confidence', 0.0)
    
    # Get SKU info from risk data if available
    sku = 'Unknown'
    category = 'Unknown'
    current_stock = 0
    if risk_data:
        sku = risk_data.get('sku', 'Unknown')
        category = risk_data.get('category', 'Unknown')
        current_stock = risk_data.get('currentStock', 0)
    
    detail_level = "detailed" if complexity == 'detailed' else "simple"
    
    reasoning_text = "\n".join(f"- {r}" for r in reasoning) if reasoning else "Not specified"
    
    prompt = f"""Explain this reorder recommendation to a small retailer in simple language:

Product: {sku} ({category})
Current Stock: {current_stock} units

Recommendation:
- Action: {action.upper()}
- Suggested Quantity: {suggested_quantity} units
- Urgency: {urgency.upper()}
- Confidence: {confidence * 100:.0f}%

Reasoning:
{reasoning_text}

Please provide a {detail_level} explanation that includes:

1. **Recommendation Summary**: What should the retailer do and why?
2. **Timing**: When should this action be taken?
3. **Rationale**: Why is this the right recommendation based on the data?
4. **Alternatives**: What happens if the retailer doesn't follow this recommendation?
5. **Next Steps**: Specific actions to take (e.g., contact supplier, place order, etc.)

Use simple language, be specific about quantities and timing, and focus on actionable advice."""

    return prompt


def create_conversational_prompt(
    user_query: str,
    context_data: Optional[Dict[str, Any]] = None,
    conversation_history: Optional[List[Dict[str, str]]] = None
) -> str:
    """
    Create prompt for conversational queries.
    
    Args:
        user_query: User's question or query
        context_data: Optional context including forecasts, risks, user profile
        conversation_history: Optional previous conversation turns
        
    Returns:
        Formatted prompt string
    """
    # Build context section
    context_section = ""
    
    if context_data:
        # Add forecast context if available
        if 'forecasts' in context_data:
            forecasts = context_data['forecasts']
            if forecasts:
                context_section += "\n\nAvailable Forecast Data:\n"
                for forecast in forecasts[:3]:  # Limit to 3 forecasts
                    sku = forecast.get('sku', 'Unknown')
                    total_demand = sum(p.get('demandForecast', 0) for p in forecast.get('predictions', []))
                    confidence = forecast.get('confidence', 0.0)
                    context_section += f"- {sku}: {total_demand:.0f} units forecasted, {confidence * 100:.0f}% confidence\n"
        
        # Add risk context if available
        if 'risks' in context_data:
            risks = context_data['risks']
            if risks:
                context_section += "\n\nCurrent Risk Assessments:\n"
                for risk in risks[:3]:  # Limit to 3 risks
                    sku = risk.get('sku', 'Unknown')
                    stockout_prob = risk.get('stockoutRisk', {}).get('probability', 0.0)
                    overstock_prob = risk.get('overstockRisk', {}).get('probability', 0.0)
                    context_section += f"- {sku}: Stockout risk {stockout_prob * 100:.0f}%, Overstock risk {overstock_prob * 100:.0f}%\n"
        
        # Add user profile context if available
        if 'userProfile' in context_data:
            profile = context_data['userProfile']
            business_info = profile.get('businessInfo', {})
            if business_info:
                context_section += f"\n\nBusiness Context:\n"
                context_section += f"- Type: {business_info.get('type', 'Unknown')}\n"
                location = business_info.get('location', {})
                if location.get('city'):
                    context_section += f"- Location: {location.get('city')}, {location.get('state', '')}\n"
    
    # Build conversation history section
    history_section = ""
    if conversation_history:
        history_section = "\n\nPrevious Conversation:\n"
        for turn in conversation_history[-3:]:  # Last 3 turns
            role = turn.get('role', 'user')
            content = turn.get('content', '')
            history_section += f"{role.capitalize()}: {content}\n"
    
    # Build prompt
    prompt = f"""You are VyaparSaathi's AI assistant helping a small retailer with their inventory questions.

User Question: {user_query}{context_section}{history_section}

Please provide a helpful, concise answer that:

1. Directly addresses the user's question
2. Uses simple, non-technical language
3. References specific data from the context when relevant
4. Provides actionable advice when appropriate
5. Admits when you don't have enough information to answer

If the question is outside the scope of inventory forecasting and risk assessment, politely explain what you can help with instead.

Keep your response focused and practical."""

    return prompt
