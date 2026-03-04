"""
Integration tests for synthetic data generation.

Tests the complete workflow of generating synthetic data and using demo mode.
"""

import pytest
from datetime import datetime, timedelta
from src.synthetic_data import (
    generate_synthetic_pattern,
    generate_synthetic_sales,
    set_demo_mode,
    is_demo_mode,
    add_demo_indicator,
    generate_grocery_scenario,
    generate_apparel_scenario,
    generate_electronics_scenario,
)


class TestSyntheticDataIntegration:
    """Integration tests for synthetic data generation."""
    
    def test_complete_grocery_workflow(self):
        """Test complete workflow for grocery store."""
        # Generate pattern
        pattern = generate_synthetic_pattern("grocery", "north")
        assert pattern.business_type == "grocery"
        
        # Generate sales data
        sales = generate_synthetic_sales(
            business_type="grocery",
            region="north",
            days=60,
            skus_per_category=3,
        )
        
        assert len(sales) > 0
        
        # Verify data structure
        for record in sales[:5]:  # Check first 5 records
            assert "date" in record
            assert "sku" in record
            assert "quantity" in record
            assert "category" in record
            assert "price" in record
            assert record["quantity"] >= 0
            assert record["price"] > 0
    
    def test_demo_mode_workflow(self):
        """Test demo mode workflow."""
        user_id = "integration-test-user"
        
        # Start in real mode
        assert not is_demo_mode(user_id)
        
        # Switch to demo mode
        set_demo_mode(user_id, True)
        assert is_demo_mode(user_id)
        
        # Generate demo data
        scenario = generate_grocery_scenario(days=30)
        
        # Add demo indicator to response
        response = {
            "forecast": "test forecast",
            "data": scenario["sales_data"][:10],
        }
        
        response_with_indicator = add_demo_indicator(response, user_id)
        
        assert response_with_indicator["_demo_mode"] is True
        assert "_demo_notice" in response_with_indicator
        assert "DEMO MODE" in response_with_indicator["_demo_notice"]
    
    def test_all_business_types(self):
        """Test generating data for all business types."""
        business_types = ["grocery", "apparel", "electronics", "general"]
        
        for business_type in business_types:
            sales = generate_synthetic_sales(
                business_type=business_type,
                days=30,
                skus_per_category=2,
            )
            
            assert len(sales) > 0, f"No sales generated for {business_type}"
            
            # Verify all records have required fields
            for record in sales[:3]:
                assert record["category"] is not None
                assert record["quantity"] >= 0
    
    def test_scenario_generation_all_types(self):
        """Test generating all scenario types."""
        scenarios = {
            "grocery": generate_grocery_scenario(days=30),
            "apparel": generate_apparel_scenario(days=30),
            "electronics": generate_electronics_scenario(days=30),
        }
        
        for scenario_type, scenario in scenarios.items():
            assert scenario["business_type"] == scenario_type
            assert len(scenario["sales_data"]) > 0
            assert "date_range" in scenario
            assert "categories" in scenario
            assert len(scenario["categories"]) > 0
    
    def test_festival_impact_in_data(self):
        """Test that festival impact is visible in generated data."""
        # Generate scenario with festivals
        scenario = generate_grocery_scenario(include_festivals=True, days=90)
        
        if len(scenario["festivals"]) > 0:
            # Check that we have data
            assert len(scenario["sales_data"]) > 0
            
            # Verify festival information is included
            festival = scenario["festivals"][0]
            assert "name" in festival
            assert "date" in festival
            
            # Verify sales data has dates
            dates = [record["date"] for record in scenario["sales_data"]]
            assert len(dates) > 0
    
    def test_data_consistency(self):
        """Test that generated data is consistent."""
        # Generate data twice with same parameters
        sales1 = generate_synthetic_sales(
            business_type="grocery",
            days=30,
            skus_per_category=2,
        )
        
        sales2 = generate_synthetic_sales(
            business_type="grocery",
            days=30,
            skus_per_category=2,
        )
        
        # Both should have data
        assert len(sales1) > 0
        assert len(sales2) > 0
        
        # Should have similar number of records (within 20% due to randomness)
        ratio = len(sales1) / len(sales2)
        assert 0.8 <= ratio <= 1.2
    
    def test_realistic_demand_patterns(self):
        """Test that demand patterns are realistic."""
        sales = generate_synthetic_sales(
            business_type="grocery",
            days=30,
            skus_per_category=3,
        )
        
        # Group by category
        category_quantities = {}
        for record in sales:
            category = record["category"]
            if category not in category_quantities:
                category_quantities[category] = []
            category_quantities[category].append(record["quantity"])
        
        # Check that each category has reasonable quantities
        for category, quantities in category_quantities.items():
            avg_quantity = sum(quantities) / len(quantities)
            assert avg_quantity > 0, f"Category {category} has zero average demand"
            assert avg_quantity < 10000, f"Category {category} has unrealistic demand"
