"""
Risk calculation engine for stockout and overstock risk assessment.

This module implements the core risk calculation logic for VyaparSaathi,
calculating stockout probability, days until stockout, potential lost sales,
overstock probability, excess units, and carrying costs.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta


def calculate_stockout_risk(
    current_stock: int,
    demand_forecast: List[Dict[str, Any]],
    safety_stock: int = 0
) -> Dict[str, Any]:
    """
    Calculate stockout risk based on current inventory and demand forecast.
    
    Args:
        current_stock: Current inventory level
        demand_forecast: List of daily demand predictions with 'date' and 'demandForecast' keys
        safety_stock: Minimum safety stock level (default: 0)
        
    Returns:
        Dictionary with stockout risk metrics:
        - probability: Stockout probability (0-1)
        - daysUntilStockout: Estimated days until stockout occurs
        - potentialLostSales: Estimated units of lost sales during stockout
    """
    if not demand_forecast:
        return {
            'probability': 0.0,
            'daysUntilStockout': float('inf'),
            'potentialLostSales': 0
        }
    
    # Calculate cumulative demand and find stockout point
    cumulative_demand = 0
    days_until_stockout = len(demand_forecast)
    stockout_occurred = False
    
    for i, day_forecast in enumerate(demand_forecast):
        daily_demand = day_forecast.get('demandForecast', 0)
        cumulative_demand += daily_demand
        
        # Check if stock runs out (considering safety stock)
        if cumulative_demand > (current_stock - safety_stock) and not stockout_occurred:
            days_until_stockout = i + 1
            stockout_occurred = True
            break
    
    # Calculate stockout probability
    if stockout_occurred:
        # Higher probability if stockout is imminent
        if days_until_stockout <= 3:
            probability = 0.9
        elif days_until_stockout <= 7:
            probability = 0.7
        else:
            probability = 0.5
    else:
        # Low probability if stock lasts through forecast period
        probability = 0.1
    
    # Calculate potential lost sales after stockout
    potential_lost_sales = 0
    if stockout_occurred:
        for i in range(days_until_stockout, len(demand_forecast)):
            potential_lost_sales += demand_forecast[i].get('demandForecast', 0)
    
    return {
        'probability': round(probability, 2),
        'daysUntilStockout': days_until_stockout if stockout_occurred else float('inf'),
        'potentialLostSales': round(potential_lost_sales, 2)
    }


def calculate_overstock_risk(
    current_stock: int,
    demand_forecast: List[Dict[str, Any]],
    shelf_life_days: Optional[int] = None,
    unit_cost: float = 0.0,
    carrying_cost_rate: float = 0.02
) -> Dict[str, Any]:
    """
    Calculate overstock risk based on demand forecast and shelf life.
    
    Args:
        current_stock: Current inventory level
        demand_forecast: List of daily demand predictions
        shelf_life_days: Product shelf life in days (None for non-perishable)
        unit_cost: Cost per unit for carrying cost calculation
        carrying_cost_rate: Monthly carrying cost rate (default: 2% per month)
        
    Returns:
        Dictionary with overstock risk metrics:
        - probability: Overstock probability (0-1)
        - excessUnits: Number of excess units beyond demand
        - carryingCost: Estimated carrying cost for excess inventory
    """
    if not demand_forecast:
        return {
            'probability': 0.0,
            'excessUnits': 0,
            'carryingCost': 0.0
        }
    
    # Calculate total demand over forecast period
    total_demand = sum(day.get('demandForecast', 0) for day in demand_forecast)
    
    # Calculate excess units
    excess_units = max(0, current_stock - total_demand)
    
    # Calculate overstock probability
    if excess_units == 0:
        probability = 0.0
    else:
        excess_ratio = excess_units / max(current_stock, 1)
        
        # Consider shelf life for perishable items
        if shelf_life_days is not None:
            forecast_days = len(demand_forecast)
            if forecast_days >= shelf_life_days:
                # High risk if forecast period exceeds shelf life
                probability = min(0.95, 0.5 + excess_ratio)
            else:
                probability = min(0.8, excess_ratio)
        else:
            # Non-perishable items have lower overstock risk
            if excess_ratio > 0.5:
                probability = 0.7
            elif excess_ratio > 0.3:
                probability = 0.5
            else:
                probability = 0.3
    
    # Calculate carrying cost
    # Carrying cost = excess units * unit cost * carrying rate * (days / 30)
    forecast_days = len(demand_forecast)
    carrying_cost = excess_units * unit_cost * carrying_cost_rate * (forecast_days / 30.0)
    
    return {
        'probability': round(probability, 2),
        'excessUnits': round(excess_units, 2),
        'carryingCost': round(carrying_cost, 2)
    }


def calculate_risk_assessment(
    sku: str,
    category: str,
    current_stock: int,
    demand_forecast: List[Dict[str, Any]],
    safety_stock: int = 0,
    shelf_life_days: Optional[int] = None,
    unit_cost: float = 0.0,
    lead_time_days: int = 7,
    carrying_cost_rate: float = 0.02
) -> Dict[str, Any]:
    """
    Calculate comprehensive risk assessment for a SKU.
    
    This is the main function that combines stockout and overstock risk
    calculations and prepares data for recommendation generation.
    
    Args:
        sku: Product SKU identifier
        category: Product category
        current_stock: Current inventory level
        demand_forecast: List of daily demand predictions
        safety_stock: Minimum safety stock level
        shelf_life_days: Product shelf life (None for non-perishable)
        unit_cost: Cost per unit
        lead_time_days: Supplier lead time in days
        carrying_cost_rate: Monthly carrying cost rate
        
    Returns:
        Risk assessment dictionary with stockout and overstock risks
    """
    # Calculate stockout risk
    stockout_risk = calculate_stockout_risk(
        current_stock=current_stock,
        demand_forecast=demand_forecast,
        safety_stock=safety_stock
    )
    
    # Calculate overstock risk
    overstock_risk = calculate_overstock_risk(
        current_stock=current_stock,
        demand_forecast=demand_forecast,
        shelf_life_days=shelf_life_days,
        unit_cost=unit_cost,
        carrying_cost_rate=carrying_cost_rate
    )
    
    # Prepare risk assessment result
    risk_assessment = {
        'sku': sku,
        'category': category,
        'currentStock': current_stock,
        'stockoutRisk': stockout_risk,
        'overstockRisk': overstock_risk,
        'assessmentDate': datetime.utcnow().isoformat(),
        'forecastPeriodDays': len(demand_forecast),
        'parameters': {
            'safetyStock': safety_stock,
            'shelfLifeDays': shelf_life_days,
            'unitCost': unit_cost,
            'leadTimeDays': lead_time_days,
            'carryingCostRate': carrying_cost_rate
        }
    }
    
    return risk_assessment
