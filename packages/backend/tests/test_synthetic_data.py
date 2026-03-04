"""
Tests for synthetic data generation module.
"""

import pytest
from datetime import datetime, timedelta
from src.synthetic_data.pattern_generator import (
    generate_synthetic_pattern,
    get_baseline_demand,
    get_seasonal_factors,
    get_festival_multipliers,
    BusinessType,
)
from src.synthetic_data.sales_generator import (
    generate_synthetic_sales,
    generate_sales_for_period,
    get_festival_impact,
)
from src.synthetic_data.demo_mode import (
    set_demo_mode,
    is_demo_mode,
    get_data_source,
    add_demo_indicator,
    switch_mode,
)
from src.synthetic_data.scenarios import (
    generate_grocery_scenario,
    generate_apparel_scenario,
    generate_electronics_scenario,
)


class TestPatternGenerator:
    """Tests for pattern generator."""
    
    def test_generate_synthetic_pattern_grocery(self):
        """Test generating pattern for grocery store."""
        pattern = generate_synthetic_pattern("grocery", "north")
        
        assert pattern.business_type == "grocery"
        assert pattern.region == "north"
        assert len(pattern.baseline_patterns) > 0
        assert len(pattern.seasonal_factors) == 12
        assert len(pattern.festival_multipliers) > 0
    
    def test_generate_synthetic_pattern_apparel(self):
        """Test generating pattern for apparel store."""
        pattern = generate_synthetic_pattern("apparel", "south")
        
        assert pattern.business_type == "apparel"
        assert pattern.region == "south"
        assert len(pattern.baseline_patterns) > 0
    
    def test_get_baseline_demand(self):
        """Test baseline demand retrieval."""
        demand, variance = get_baseline_demand("grocery", "staples")
        
        assert demand > 0
        assert 0 < variance < 1
    
    def test_get_seasonal_factors(self):
        """Test seasonal factors retrieval."""
        factors = get_seasonal_factors("grocery")
        
        assert len(factors) == 12
        assert all(1 <= month <= 12 for month in factors.keys())
        assert all(factor > 0 for factor in factors.values())
    
    def test_get_festival_multipliers(self):
        """Test festival multipliers retrieval."""
        multipliers = get_festival_multipliers("grocery")
        
        assert "Diwali" in multipliers
        assert len(multipliers["Diwali"]) > 0
        assert all(mult >= 1.0 for mult in multipliers["Diwali"].values())


class TestSalesGenerator:
    """Tests for sales data generator."""
    
    def test_generate_synthetic_sales(self):
        """Test generating synthetic sales data."""
        sales = generate_synthetic_sales(
            business_type="grocery",
            region="north",
            days=30,
            skus_per_category=2,
        )
        
        assert len(sales) > 0
        assert all("date" in record for record in sales)
        assert all("sku" in record for record in sales)
        assert all("quantity" in record for record in sales)
        assert all("category" in record for record in sales)
    
    def test_generate_sales_with_festivals(self):
        """Test generating sales with festival impact."""
        festivals = [
            {
                "festivalId": "diwali-2024",
                "name": "Diwali",
                "date": (datetime.now() - timedelta(days=15)).strftime("%Y-%m-%d"),
                "region": ["north"],
                "category": "religious",
                "duration": 5,
                "preparationDays": 14,
            }
        ]
        
        pattern = generate_synthetic_pattern("grocery", "north")
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()
        
        sales = generate_sales_for_period(
            pattern=pattern,
            start_date=start_date,
            end_date=end_date,
            festivals=festivals,
            skus_per_category=2,
        )
        
        assert len(sales) > 0
    
    def test_get_festival_impact(self):
        """Test festival impact calculation."""
        festivals = [
            {
                "festivalId": "diwali-2024",
                "name": "Diwali",
                "date": "2024-10-24",
                "region": ["north"],
            }
        ]
        
        festival_multipliers = get_festival_multipliers("grocery")
        
        # Test on festival day
        festival_date = datetime(2024, 10, 24)
        impact = get_festival_impact(
            festival_date,
            festivals,
            "sweets",
            festival_multipliers,
        )
        
        assert impact > 1.0  # Should have festival impact
        
        # Test far from festival
        far_date = datetime(2024, 8, 1)
        impact_far = get_festival_impact(
            far_date,
            festivals,
            "sweets",
            festival_multipliers,
        )
        
        assert impact_far == 1.0  # No festival impact


class TestDemoMode:
    """Tests for demo mode management."""
    
    def test_set_and_check_demo_mode(self):
        """Test setting and checking demo mode."""
        user_id = "test-user-1"
        
        # Default should be real mode
        assert not is_demo_mode(user_id)
        assert get_data_source(user_id) == "real"
        
        # Enable demo mode
        set_demo_mode(user_id, True)
        assert is_demo_mode(user_id)
        assert get_data_source(user_id) == "demo"
        
        # Disable demo mode
        set_demo_mode(user_id, False)
        assert not is_demo_mode(user_id)
        assert get_data_source(user_id) == "real"
    
    def test_add_demo_indicator(self):
        """Test adding demo indicator to response."""
        user_id = "test-user-2"
        response = {"data": "test"}
        
        # Real mode - no indicator
        set_demo_mode(user_id, False)
        result = add_demo_indicator(response.copy(), user_id)
        assert result["_demo_mode"] is False
        assert "_demo_notice" not in result
        
        # Demo mode - with indicator
        set_demo_mode(user_id, True)
        result = add_demo_indicator(response.copy(), user_id)
        assert result["_demo_mode"] is True
        assert "_demo_notice" in result
        assert "DEMO MODE" in result["_demo_notice"]
    
    def test_switch_mode_validation(self):
        """Test mode switching with validation."""
        user_id = "test-user-3"
        
        # Switch to demo mode (always allowed)
        result = switch_mode(user_id, "demo", has_real_data=False)
        assert result["success"] is True
        assert result["current_mode"] == "demo"
        
        # Try to switch to real mode without data (should fail)
        result = switch_mode(user_id, "real", has_real_data=False)
        assert result["success"] is False
        assert "error" in result
        
        # Switch to real mode with data (should succeed)
        result = switch_mode(user_id, "real", has_real_data=True)
        assert result["success"] is True
        assert result["current_mode"] == "real"


class TestScenarios:
    """Tests for sample scenarios."""
    
    def test_generate_grocery_scenario(self):
        """Test generating grocery scenario."""
        scenario = generate_grocery_scenario(include_festivals=True, days=30)
        
        assert scenario["business_type"] == "grocery"
        assert "sales_data" in scenario
        assert len(scenario["sales_data"]) > 0
        assert "date_range" in scenario
        assert scenario["date_range"]["days"] == 30
    
    def test_generate_apparel_scenario(self):
        """Test generating apparel scenario."""
        scenario = generate_apparel_scenario(include_festivals=True, days=30)
        
        assert scenario["business_type"] == "apparel"
        assert "sales_data" in scenario
        assert len(scenario["sales_data"]) > 0
    
    def test_generate_electronics_scenario(self):
        """Test generating electronics scenario."""
        scenario = generate_electronics_scenario(include_festivals=True, days=30)
        
        assert scenario["business_type"] == "electronics"
        assert "sales_data" in scenario
        assert len(scenario["sales_data"]) > 0
    
    def test_scenario_without_festivals(self):
        """Test generating scenario without festivals."""
        scenario = generate_grocery_scenario(include_festivals=False, days=30)
        
        assert len(scenario["festivals"]) == 0
        assert len(scenario["sales_data"]) > 0
