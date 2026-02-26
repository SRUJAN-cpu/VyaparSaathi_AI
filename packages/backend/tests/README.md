# VyaparSaathi Backend Testing Guide

This directory contains tests for the VyaparSaathi backend Lambda functions.

## Test Structure

- `conftest.py` - Pytest configuration and shared fixtures
- `strategies.py` - Hypothesis strategies for property-based testing
- `test_*.py` - Test files (unit and property-based tests)

## Running Tests

### Run all tests
```bash
cd packages/backend
pytest
```

### Run with coverage
```bash
pytest --cov=src --cov-report=html
```

### Run only unit tests
```bash
pytest -m "not property"
```

### Run only property-based tests
```bash
pytest -m property
```

### Run specific test file
```bash
pytest tests/test_example.py
```

### Run with verbose output
```bash
pytest -v
```

## Writing Tests

### Unit Tests

Unit tests verify specific examples and edge cases:

```python
def test_valid_sales_record(sample_sales_data):
    """Test that valid sales records pass validation."""
    for record in sample_sales_data:
        assert validate_sales_record(record)
```

### Property-Based Tests

Property-based tests verify universal properties across many inputs:

```python
from hypothesis import given
from tests.strategies import sales_record_strategy

@pytest.mark.property
@given(record=sales_record_strategy())
def test_property_all_generated_records_are_valid(record):
    """
    Property test: All generated sales records should be valid.
    
    **Validates: Requirements 1.1, 1.5**
    """
    assert validate_sales_record(record)
    assert record["quantity"] > 0
```

## Hypothesis Configuration

Hypothesis profiles are configured in `conftest.py`:

- `default` - 100 examples per test (standard testing)
- `ci` - 200 examples per test (CI/CD pipeline)
- `dev` - 10 examples per test (fast feedback during development)
- `debug` - 10 examples with verbose output (debugging failures)

To use a different profile:
```bash
pytest --hypothesis-profile=dev
```

## Custom Strategies

The `strategies.py` module provides custom Hypothesis strategies:

- `sales_record_strategy()` - Generate valid sales records
- `sales_data_list_strategy()` - Generate lists of sales records
- `invalid_sales_record_strategy()` - Generate invalid sales records
- `festival_event_strategy()` - Generate festival events
- `user_profile_strategy()` - Generate user profiles
- `questionnaire_response_strategy()` - Generate questionnaire responses
- `forecast_request_strategy()` - Generate forecast requests
- `inventory_data_strategy()` - Generate inventory data

## Fixtures

Common fixtures are defined in `conftest.py`:

- `sample_sales_data` - Sample sales records
- `sample_festival_data` - Sample festival event
- `sample_user_profile` - Sample user profile

## Best Practices

1. **Mark property tests**: Use `@pytest.mark.property` for property-based tests
2. **Document properties**: Include docstrings explaining what property is being tested
3. **Link to requirements**: Use `**Validates: Requirements X.Y**` format
4. **Use appropriate strategies**: Choose strategies that match your input domain
5. **Test edge cases**: Write unit tests for specific edge cases
6. **Keep tests fast**: Use the `dev` profile during development
7. **Run full suite in CI**: Use the `ci` profile for comprehensive testing
