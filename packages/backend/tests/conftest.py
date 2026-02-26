"""
Pytest configuration and fixtures for VyaparSaathi backend tests.
"""
import pytest
from hypothesis import settings, Verbosity, HealthCheck

# Configure Hypothesis settings
settings.register_profile("default", max_examples=100, deadline=None)
settings.register_profile(
    "ci",
    max_examples=200,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow],
)
settings.register_profile("dev", max_examples=10, verbosity=Verbosity.verbose)
settings.register_profile("debug", max_examples=10, verbosity=Verbosity.debug)

# Load the appropriate profile
settings.load_profile("default")


@pytest.fixture
def sample_sales_data():
    """Fixture providing sample sales data for testing."""
    return [
        {"date": "2023-10-01", "sku": "SKU001", "quantity": 10},
        {"date": "2023-10-02", "sku": "SKU001", "quantity": 15},
        {"date": "2023-10-03", "sku": "SKU002", "quantity": 8},
    ]


@pytest.fixture
def sample_festival_data():
    """Fixture providing sample festival data for testing."""
    return {
        "festivalId": "diwali-2023",
        "name": "Diwali",
        "date": "2023-11-12",
        "region": ["north", "west"],
        "category": "festival",
        "demandMultipliers": {"grocery": 2.5, "apparel": 3.0, "electronics": 2.0},
        "duration": 5,
        "preparationDays": 14,
    }


@pytest.fixture
def sample_user_profile():
    """Fixture providing sample user profile for testing."""
    return {
        "userId": "test-user-123",
        "businessInfo": {
            "name": "Test Store",
            "type": "grocery",
            "location": {"city": "Mumbai", "state": "Maharashtra", "region": "west"},
            "size": "medium",
        },
        "dataCapabilities": {
            "hasHistoricalData": True,
            "dataQuality": "good",
            "lastUpdated": "2023-10-01T00:00:00Z",
        },
        "preferences": {
            "forecastHorizon": 14,
            "riskTolerance": "moderate",
        },
    }
