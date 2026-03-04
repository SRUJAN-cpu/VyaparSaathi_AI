"""
Unit and property-based tests for risk assessment component.

Tests the risk calculator, alert generator, reorder engine, and storage.
"""

import pytest
from datetime import datetime, timedelta
from hypothesis import given, strategies as st
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from risk_assessor.risk_calculator import (
    calculate_stockout_risk,
    calculate_overstock_risk,
    calculate_risk_assessment
)
from risk_assessor.alert_generator import (
    get_risk_level,
    generate_alert,
    generate_stockout_recommendations,
    generate_overstock_recommendations,
    RISK_THRESHOLDS
)
from risk_assessor.reorder_engine import (
    calculate_suggested_quantity,
    determine_action,
    determine_urgency,
    calculate_confidence,
    calculate_reorder_recommendation
)

# Import test strategies
from tests.strategies import (
    sales_record_strategy,
    inventory_data_strategy
)


# Helper function to create demand forecast
def create_demand_forecast(days: int, daily_demand: float) -> list:
    """Create a simple demand forecast for testing."""
    forecasts = []
    start_date = datetime.utcnow().date()
    
    for i in range(days):
        date = start_date + timedelta(days=i)
        forecasts.append({
            'date': date.isoformat(),
            'demandForecast': daily_demand,
            'lowerBound': daily_demand * 0.8,
            'upperBound': daily_demand * 1.2,
            'festivalMultiplier': 1.0,
            'confidence': 0.7
        })
    
    return forecasts


class TestRiskCalculator:
    """Test risk calculation functions."""
    
    def test_calculate_stockout_risk_no_stockout(self):
        """Test stockout risk when stock is sufficient."""
        demand_forecast = create_demand_forecast(days=7, daily_demand=10)
        
        result = calculate_stockout_risk(
            current_stock=100,
            demand_forecast=demand_forecast,
            safety_stock=10
        )
        
        assert result['probability'] == 0.1  # Low probability
        assert result['daysUntilStockout'] == float('inf')
        assert result['potentialLostSales'] == 0
    
    def test_calculate_stockout_risk_imminent(self):
        """Test stockout risk when stockout is imminent."""
        demand_forecast = create_demand_forecast(days=7, daily_demand=20)
        
        result = calculate_stockout_risk(
            current_stock=50,
            demand_forecast=demand_forecast,
            safety_stock=10
        )
        
        # Stock will run out in 3 days (50 - 10 safety = 40, after day 2: 40 consumed, day 3 exceeds)
        assert result['probability'] == 0.9  # High probability
        assert result['daysUntilStockout'] == 3
        assert result['potentialLostSales'] > 0
    
    def test_calculate_stockout_risk_medium_term(self):
        """Test stockout risk for medium-term stockout."""
        demand_forecast = create_demand_forecast(days=14, daily_demand=10)
        
        result = calculate_stockout_risk(
            current_stock=100,
            demand_forecast=demand_forecast,
            safety_stock=10
        )
        
        # Stock will run out in 10 days (100 - 10 safety = 90, after day 9: 90 consumed, day 10 exceeds)
        assert result['probability'] == 0.5  # Medium probability
        assert result['daysUntilStockout'] == 10
        assert result['potentialLostSales'] > 0
    
    def test_calculate_stockout_risk_empty_forecast(self):
        """Test stockout risk with empty forecast."""
        result = calculate_stockout_risk(
            current_stock=100,
            demand_forecast=[],
            safety_stock=10
        )
        
        assert result['probability'] == 0.0
        assert result['daysUntilStockout'] == float('inf')
        assert result['potentialLostSales'] == 0
    
    def test_calculate_overstock_risk_no_overstock(self):
        """Test overstock risk when stock is balanced."""
        demand_forecast = create_demand_forecast(days=7, daily_demand=15)
        
        result = calculate_overstock_risk(
            current_stock=100,
            demand_forecast=demand_forecast,
            shelf_life_days=None,
            unit_cost=10.0,
            carrying_cost_rate=0.02
        )
        
        # Total demand = 15 * 7 = 105, so no excess
        assert result['probability'] == 0.0
        assert result['excessUnits'] == 0
        assert result['carryingCost'] == 0.0
    
    def test_calculate_overstock_risk_with_excess(self):
        """Test overstock risk with excess inventory."""
        demand_forecast = create_demand_forecast(days=7, daily_demand=10)
        
        result = calculate_overstock_risk(
            current_stock=150,
            demand_forecast=demand_forecast,
            shelf_life_days=None,
            unit_cost=10.0,
            carrying_cost_rate=0.02
        )
        
        # Total demand = 10 * 7 = 70, excess = 150 - 70 = 80
        assert result['probability'] > 0.5  # High excess ratio
        assert result['excessUnits'] == 80
        assert result['carryingCost'] > 0
    
    def test_calculate_overstock_risk_perishable(self):
        """Test overstock risk for perishable items."""
        demand_forecast = create_demand_forecast(days=14, daily_demand=10)
        
        result = calculate_overstock_risk(
            current_stock=200,
            demand_forecast=demand_forecast,
            shelf_life_days=10,  # Shelf life shorter than forecast
            unit_cost=5.0,
            carrying_cost_rate=0.02
        )
        
        # High risk due to shelf life
        assert result['probability'] >= 0.5
        assert result['excessUnits'] > 0
    
    def test_calculate_risk_assessment_complete(self):
        """Test complete risk assessment calculation."""
        demand_forecast = create_demand_forecast(days=7, daily_demand=15)
        
        result = calculate_risk_assessment(
            sku='SKU001',
            category='grocery',
            current_stock=100,
            demand_forecast=demand_forecast,
            safety_stock=10,
            shelf_life_days=30,
            unit_cost=10.0,
            lead_time_days=7,
            carrying_cost_rate=0.02
        )
        
        # Check structure
        assert result['sku'] == 'SKU001'
        assert result['category'] == 'grocery'
        assert result['currentStock'] == 100
        assert 'stockoutRisk' in result
        assert 'overstockRisk' in result
        assert 'assessmentDate' in result
        assert 'forecastPeriodDays' in result
        assert 'parameters' in result
        
        # Check risk components
        assert 'probability' in result['stockoutRisk']
        assert 'daysUntilStockout' in result['stockoutRisk']
        assert 'potentialLostSales' in result['stockoutRisk']
        
        assert 'probability' in result['overstockRisk']
        assert 'excessUnits' in result['overstockRisk']
        assert 'carryingCost' in result['overstockRisk']


class TestAlertGenerator:
    """Test alert generation functions."""
    
    def test_get_risk_level_low(self):
        """Test risk level determination for low risk."""
        assert get_risk_level(0.2) == 'low'
        assert get_risk_level(0.29) == 'low'
    
    def test_get_risk_level_medium(self):
        """Test risk level determination for medium risk."""
        assert get_risk_level(0.3) == 'medium'
        assert get_risk_level(0.5) == 'medium'
        assert get_risk_level(0.59) == 'medium'
    
    def test_get_risk_level_high(self):
        """Test risk level determination for high risk."""
        assert get_risk_level(0.6) == 'high'
        assert get_risk_level(0.8) == 'high'
        assert get_risk_level(0.95) == 'high'
    
    def test_generate_stockout_recommendations_high_risk(self):
        """Test stockout recommendations for high risk."""
        risk_assessment = {
            'sku': 'SKU001',
            'stockoutRisk': {
                'probability': 0.9,
                'daysUntilStockout': 2,
                'potentialLostSales': 100
            }
        }
        
        recommendations = generate_stockout_recommendations(risk_assessment)
        
        assert len(recommendations) > 0
        assert any('URGENT' in rec for rec in recommendations)
        assert any('emergency order' in rec.lower() for rec in recommendations)
    
    def test_generate_stockout_recommendations_medium_risk(self):
        """Test stockout recommendations for medium risk."""
        risk_assessment = {
            'sku': 'SKU001',
            'stockoutRisk': {
                'probability': 0.5,
                'daysUntilStockout': 10,
                'potentialLostSales': 50
            }
        }
        
        recommendations = generate_stockout_recommendations(risk_assessment)
        
        assert len(recommendations) > 0
        assert any('monitor' in rec.lower() for rec in recommendations)
    
    def test_generate_overstock_recommendations_high_risk(self):
        """Test overstock recommendations for high risk."""
        risk_assessment = {
            'sku': 'SKU001',
            'overstockRisk': {
                'probability': 0.8,
                'excessUnits': 100,
                'carryingCost': 50.0
            },
            'parameters': {
                'shelfLifeDays': 30
            }
        }
        
        recommendations = generate_overstock_recommendations(risk_assessment)
        
        assert len(recommendations) > 0
        assert any('excess' in rec.lower() for rec in recommendations)
        assert any('promotional' in rec.lower() or 'discount' in rec.lower() for rec in recommendations)
    
    def test_generate_alert_stockout_only(self):
        """Test alert generation for stockout risk only."""
        risk_assessment = {
            'sku': 'SKU001',
            'category': 'grocery',
            'currentStock': 50,
            'stockoutRisk': {
                'probability': 0.7,
                'daysUntilStockout': 5,
                'potentialLostSales': 80
            },
            'overstockRisk': {
                'probability': 0.1,
                'excessUnits': 0,
                'carryingCost': 0.0
            },
            'assessmentDate': datetime.utcnow().isoformat()
        }
        
        alert = generate_alert(risk_assessment, alert_type='stockout')
        
        assert alert['sku'] == 'SKU001'
        assert alert['severity'] == 'high'
        assert alert['alertType'] == 'stockout'
        assert alert['stockoutAlert']['triggered'] is True
        assert len(alert['recommendations']) > 0
    
    def test_generate_alert_both_risks(self):
        """Test alert generation for both risks."""
        risk_assessment = {
            'sku': 'SKU001',
            'category': 'grocery',
            'currentStock': 100,
            'stockoutRisk': {
                'probability': 0.5,
                'daysUntilStockout': 8,
                'potentialLostSales': 50
            },
            'overstockRisk': {
                'probability': 0.4,
                'excessUnits': 30,
                'carryingCost': 15.0
            },
            'assessmentDate': datetime.utcnow().isoformat()
        }
        
        alert = generate_alert(risk_assessment, alert_type='both')
        
        assert alert['sku'] == 'SKU001'
        assert alert['severity'] in ['low', 'medium', 'high']
        assert alert['alertType'] == 'both'
        assert len(alert['recommendations']) > 0
    
    def test_generate_alert_no_alert_needed(self):
        """Test alert generation when risks are low."""
        risk_assessment = {
            'sku': 'SKU001',
            'category': 'grocery',
            'currentStock': 100,
            'stockoutRisk': {
                'probability': 0.1,
                'daysUntilStockout': float('inf'),
                'potentialLostSales': 0
            },
            'overstockRisk': {
                'probability': 0.1,
                'excessUnits': 5,
                'carryingCost': 2.0
            },
            'assessmentDate': datetime.utcnow().isoformat()
        }
        
        alert = generate_alert(risk_assessment, alert_type='both')
        
        # Should still generate alert structure but with low severity
        assert alert['severity'] == 'low'


class TestReorderEngine:
    """Test reorder recommendation engine."""
    
    def test_calculate_suggested_quantity_reorder_needed(self):
        """Test suggested quantity calculation when reorder is needed."""
        demand_forecast = create_demand_forecast(days=14, daily_demand=20)
        
        quantity = calculate_suggested_quantity(
            demand_forecast=demand_forecast,
            current_stock=100,
            safety_stock=50,
            lead_time_days=7
        )
        
        # Total demand = 20 * 14 = 280
        # Target = 280 + 50 safety = 330
        # Suggested = 330 - 100 = 230
        assert quantity == 230
    
    def test_calculate_suggested_quantity_no_reorder(self):
        """Test suggested quantity when no reorder is needed."""
        demand_forecast = create_demand_forecast(days=7, daily_demand=10)
        
        quantity = calculate_suggested_quantity(
            demand_forecast=demand_forecast,
            current_stock=200,
            safety_stock=20,
            lead_time_days=7
        )
        
        # Total demand = 10 * 7 = 70
        # Target = 70 + 20 = 90
        # Current = 200, so no reorder needed
        assert quantity == 0
    
    def test_determine_action_reorder(self):
        """Test action determination for reorder."""
        stockout_risk = {'probability': 0.7, 'daysUntilStockout': 5}
        overstock_risk = {'probability': 0.1, 'excessUnits': 0}
        
        action = determine_action(
            stockout_risk=stockout_risk,
            overstock_risk=overstock_risk,
            current_stock=50,
            suggested_quantity=100
        )
        
        assert action == 'reorder'
    
    def test_determine_action_reduce(self):
        """Test action determination for reduce."""
        stockout_risk = {'probability': 0.1, 'daysUntilStockout': float('inf')}
        overstock_risk = {'probability': 0.8, 'excessUnits': 100}
        
        action = determine_action(
            stockout_risk=stockout_risk,
            overstock_risk=overstock_risk,
            current_stock=200,
            suggested_quantity=0
        )
        
        assert action == 'reduce'
    
    def test_determine_action_maintain(self):
        """Test action determination for maintain."""
        stockout_risk = {'probability': 0.2, 'daysUntilStockout': 20}
        overstock_risk = {'probability': 0.2, 'excessUnits': 10}
        
        action = determine_action(
            stockout_risk=stockout_risk,
            overstock_risk=overstock_risk,
            current_stock=100,
            suggested_quantity=0
        )
        
        assert action == 'maintain'
    
    def test_determine_urgency_high(self):
        """Test urgency determination for high urgency."""
        stockout_risk = {'probability': 0.9, 'daysUntilStockout': 2}
        overstock_risk = {'probability': 0.1, 'excessUnits': 0}
        
        urgency = determine_urgency(
            action='reorder',
            stockout_risk=stockout_risk,
            overstock_risk=overstock_risk
        )
        
        assert urgency == 'high'
    
    def test_determine_urgency_medium(self):
        """Test urgency determination for medium urgency."""
        stockout_risk = {'probability': 0.7, 'daysUntilStockout': 6}
        overstock_risk = {'probability': 0.1, 'excessUnits': 0}
        
        urgency = determine_urgency(
            action='reorder',
            stockout_risk=stockout_risk,
            overstock_risk=overstock_risk
        )
        
        assert urgency == 'medium'
    
    def test_determine_urgency_low(self):
        """Test urgency determination for low urgency."""
        stockout_risk = {'probability': 0.2, 'daysUntilStockout': 20}
        overstock_risk = {'probability': 0.2, 'excessUnits': 10}
        
        urgency = determine_urgency(
            action='maintain',
            stockout_risk=stockout_risk,
            overstock_risk=overstock_risk
        )
        
        assert urgency == 'low'
    
    def test_calculate_confidence_high_quality(self):
        """Test confidence calculation with high quality data."""
        risk_assessment = {
            'forecastPeriodDays': 14,
            'stockoutRisk': {'probability': 0.8},
            'overstockRisk': {'probability': 0.1}
        }
        
        data_quality = {'score': 0.9, 'quality': 'good'}
        
        confidence = calculate_confidence(risk_assessment, data_quality)
        
        assert 0.7 <= confidence <= 0.95
    
    def test_calculate_confidence_low_quality(self):
        """Test confidence calculation with low quality data."""
        risk_assessment = {
            'forecastPeriodDays': 7,
            'stockoutRisk': {'probability': 0.5},
            'overstockRisk': {'probability': 0.5}
        }
        
        data_quality = {'score': 0.3, 'quality': 'poor'}
        
        confidence = calculate_confidence(risk_assessment, data_quality)
        
        assert confidence < 0.7
    
    def test_calculate_reorder_recommendation_complete(self):
        """Test complete reorder recommendation calculation."""
        demand_forecast = create_demand_forecast(days=14, daily_demand=15)
        
        risk_assessment = {
            'sku': 'SKU001',
            'category': 'grocery',
            'currentStock': 100,
            'stockoutRisk': {
                'probability': 0.7,
                'daysUntilStockout': 6,
                'potentialLostSales': 80
            },
            'overstockRisk': {
                'probability': 0.2,
                'excessUnits': 0,
                'carryingCost': 0.0
            },
            'forecastPeriodDays': 14,
            'parameters': {
                'safetyStock': 30,
                'leadTimeDays': 7
            }
        }
        
        data_quality = {'score': 0.7, 'quality': 'good'}
        
        recommendation = calculate_reorder_recommendation(
            risk_assessment=risk_assessment,
            demand_forecast=demand_forecast,
            data_quality=data_quality
        )
        
        # Check structure
        assert 'action' in recommendation
        assert 'suggestedQuantity' in recommendation
        assert 'urgency' in recommendation
        assert 'reasoning' in recommendation
        assert 'confidence' in recommendation
        
        # Check values
        assert recommendation['action'] in ['reorder', 'reduce', 'maintain']
        assert recommendation['urgency'] in ['low', 'medium', 'high']
        assert 0 <= recommendation['confidence'] <= 1
        assert len(recommendation['reasoning']) > 0


# Property-based tests
class TestRiskAssessmentProperties:
    """Property-based tests for risk assessment."""
    
    @pytest.mark.property
    @given(
        current_stock=st.integers(min_value=0, max_value=10000),
        daily_demand=st.floats(min_value=1, max_value=500, allow_nan=False, allow_infinity=False),
        forecast_days=st.integers(min_value=7, max_value=14)
    )
    def test_property_risk_assessment_completeness(self, current_stock, daily_demand, forecast_days):
        """
        Property 7: Risk Assessment Completeness
        
        For any SKU/category with current inventory and demand forecast,
        the system should calculate both stockout and overstock risks
        with associated probabilities.
        
        **Validates: Requirements 3.1, 3.2**
        """
        demand_forecast = create_demand_forecast(days=forecast_days, daily_demand=daily_demand)
        
        result = calculate_risk_assessment(
            sku='TEST_SKU',
            category='test_category',
            current_stock=current_stock,
            demand_forecast=demand_forecast,
            safety_stock=0,
            unit_cost=10.0,
            lead_time_days=7
        )
        
        # Must have both risk types
        assert 'stockoutRisk' in result
        assert 'overstockRisk' in result
        
        # Must have probabilities
        assert 'probability' in result['stockoutRisk']
        assert 'probability' in result['overstockRisk']
        
        # Probabilities must be in valid range
        assert 0 <= result['stockoutRisk']['probability'] <= 1
        assert 0 <= result['overstockRisk']['probability'] <= 1
    
    @pytest.mark.property
    @given(
        probability=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
    )
    def test_property_risk_based_alert_generation(self, probability):
        """
        Property 8: Risk-Based Alert Generation
        
        For any risk assessment where calculated risk exceeds predefined thresholds,
        the system should generate alerts with appropriate severity indicators.
        
        **Validates: Requirements 3.3**
        """
        risk_assessment = {
            'sku': 'TEST_SKU',
            'category': 'test_category',
            'currentStock': 100,
            'stockoutRisk': {
                'probability': probability,
                'daysUntilStockout': 5,
                'potentialLostSales': 50
            },
            'overstockRisk': {
                'probability': 0.1,
                'excessUnits': 0,
                'carryingCost': 0.0
            },
            'assessmentDate': datetime.utcnow().isoformat()
        }
        
        alert = generate_alert(risk_assessment, alert_type='stockout')
        
        # If probability exceeds threshold, alert should be triggered
        if probability >= RISK_THRESHOLDS['low']:
            assert alert['stockoutAlert']['triggered'] is True
            assert alert['severity'] in ['low', 'medium', 'high']
            
            # Severity should match probability level
            expected_level = get_risk_level(probability)
            assert alert['stockoutAlert']['level'] == expected_level
        
        # Alert should always have recommendations
        assert 'recommendations' in alert
        assert isinstance(alert['recommendations'], list)
    
    @pytest.mark.property
    @given(
        current_stock=st.integers(min_value=0, max_value=10000),
        daily_demand=st.floats(min_value=1, max_value=500, allow_nan=False, allow_infinity=False),
        forecast_days=st.integers(min_value=7, max_value=14)
    )
    def test_property_reorder_recommendations(self, current_stock, daily_demand, forecast_days):
        """
        Property 9: Reorder Recommendations
        
        For any risk assessment indicating stockout risk, the system should provide
        reorder recommendations with specific suggested quantities and confidence indicators.
        
        **Validates: Requirements 3.4, 3.5**
        """
        demand_forecast = create_demand_forecast(days=forecast_days, daily_demand=daily_demand)
        
        risk_assessment = calculate_risk_assessment(
            sku='TEST_SKU',
            category='test_category',
            current_stock=current_stock,
            demand_forecast=demand_forecast,
            safety_stock=10,
            unit_cost=10.0,
            lead_time_days=7
        )
        
        recommendation = calculate_reorder_recommendation(
            risk_assessment=risk_assessment,
            demand_forecast=demand_forecast,
            data_quality={'score': 0.7, 'quality': 'good'}
        )
        
        # Must have all required fields
        assert 'action' in recommendation
        assert 'suggestedQuantity' in recommendation
        assert 'urgency' in recommendation
        assert 'reasoning' in recommendation
        assert 'confidence' in recommendation
        
        # Action must be valid
        assert recommendation['action'] in ['reorder', 'reduce', 'maintain']
        
        # Urgency must be valid
        assert recommendation['urgency'] in ['low', 'medium', 'high']
        
        # Confidence must be in valid range
        assert 0 <= recommendation['confidence'] <= 1
        
        # Reasoning must be non-empty
        assert len(recommendation['reasoning']) > 0
        
        # If action is reorder, suggested quantity should be positive
        if recommendation['action'] == 'reorder':
            assert recommendation['suggestedQuantity'] >= 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
