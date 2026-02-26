"""
Example test file demonstrating unit tests and property-based tests.

This file shows how to use pytest, Hypothesis, and the custom strategies.
"""
import pytest
from hypothesis import given, example
from tests.strategies import (
    sales_record_strategy,
    sales_data_list_strategy,
    festival_event_strategy,
)


def validate_sales_record(record: dict) -> bool:
    """
    Validate that a sales record has required fields.
    
    Args:
        record: Sales record dictionary
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = ["date", "sku", "quantity"]
    return all(field in record for field in required_fields)


class TestSalesDataValidation:
    """Unit tests for sales data validation."""
    
    def test_valid_sales_record(self, sample_sales_data):
        """Test that valid sales records pass validation."""
        for record in sample_sales_data:
            assert validate_sales_record(record)
    
    def test_missing_required_field(self):
        """Test that records missing required fields fail validation."""
        invalid_record = {"date": "2023-10-01", "sku": "SKU001"}  # Missing quantity
        assert not validate_sales_record(invalid_record)
    
    @pytest.mark.property
    @given(record=sales_record_strategy())
    def test_property_all_generated_records_are_valid(self, record):
        """
        Property test: All generated sales records should be valid.
        
        **Validates: Requirements 1.1, 1.5**
        """
        assert validate_sales_record(record)
        assert isinstance(record["quantity"], int)
        assert record["quantity"] > 0
    
    @pytest.mark.property
    @given(records=sales_data_list_strategy(min_size=1, max_size=50))
    def test_property_list_validation(self, records):
        """
        Property test: All records in a list should be valid.
        
        **Validates: Requirements 1.1**
        """
        assert len(records) > 0
        for record in records:
            assert validate_sales_record(record)


class TestFestivalData:
    """Unit tests for festival data."""
    
    def test_festival_has_demand_multipliers(self, sample_festival_data):
        """Test that festival data includes demand multipliers."""
        assert "demandMultipliers" in sample_festival_data
        assert "grocery" in sample_festival_data["demandMultipliers"]
    
    @pytest.mark.property
    @given(festival=festival_event_strategy())
    def test_property_festival_multipliers_valid(self, festival):
        """
        Property test: Festival demand multipliers should be >= 1.0.
        
        **Validates: Requirements 2.2**
        """
        for category, multiplier in festival["demandMultipliers"].items():
            assert multiplier >= 1.0
            assert multiplier <= 5.0
    
    @pytest.mark.property
    @given(festival=festival_event_strategy())
    def test_property_festival_has_region(self, festival):
        """
        Property test: All festivals should have at least one region.
        
        **Validates: Requirements 2.3**
        """
        assert len(festival["region"]) > 0
        assert all(isinstance(r, str) for r in festival["region"])
