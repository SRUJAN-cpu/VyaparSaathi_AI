# Synthetic Data Generator

This module provides synthetic data generation capabilities for VyaparSaathi, enabling demonstration and testing of the festival demand forecasting system without requiring real business data.

## Features

### 1. Pattern Generation (`pattern_generator.py`)

Generates realistic demand patterns based on business type, including:

- **Baseline Demand**: Category-specific normal demand levels with variance
- **Seasonal Factors**: Monthly adjustment factors (e.g., higher demand in October for Diwali)
- **Festival Multipliers**: Festival-specific demand increases by category

**Supported Business Types:**
- `grocery`: Staples, vegetables, dairy, snacks, beverages, sweets
- `apparel`: Traditional, casual, formal, kids, accessories
- `electronics`: Mobile, laptop, TV, appliances, accessories
- `general`: Household, personal care, stationery, gifts

**Example:**
```python
from src.synthetic_data import generate_synthetic_pattern

pattern = generate_synthetic_pattern("grocery", "north")
print(f"Business: {pattern.business_type}")
print(f"Categories: {[p.category for p in pattern.baseline_patterns]}")
print(f"Seasonal factors: {pattern.seasonal_factors}")
```

### 2. Sales Data Generation (`sales_generator.py`)

Generates realistic sales records with:

- Daily/weekly demand variations (weekends higher)
- Seasonal adjustments by month
- Festival impact (7 days before to 3 days after)
- Random variance and noise
- Realistic pricing by category

**Example:**
```python
from src.synthetic_data import generate_synthetic_sales

sales = generate_synthetic_sales(
    business_type="grocery",
    region="north",
    days=90,
    skus_per_category=3,
)

print(f"Generated {len(sales)} sales records")
print(f"Sample: {sales[0]}")
```

### 3. Demo Mode Management (`demo_mode.py`)

Manages switching between demo (synthetic) and real data modes:

- User-specific mode tracking
- Clear demo mode indicators
- Validation for mode switching
- Visual warnings for demo data

**Example:**
```python
from src.synthetic_data import set_demo_mode, is_demo_mode, add_demo_indicator

# Enable demo mode
set_demo_mode("user-123", True)

# Check mode
if is_demo_mode("user-123"):
    print("User is in demo mode")

# Add indicator to response
response = {"forecast": "data"}
response = add_demo_indicator(response, "user-123")
# Response now includes _demo_mode and _demo_notice fields
```

### 4. Sample Scenarios (`scenarios.py`)

Pre-configured scenarios for different retailer types:

- **Grocery Store**: 90 days of data with Diwali, Eid, Holi festivals
- **Apparel Store**: Wedding and festival season data
- **Electronics Store**: Diwali sale season data

Each scenario includes:
- Pre-festival period (preparation)
- During-festival period (peak demand)
- Post-festival period (normalization)

**Example:**
```python
from src.synthetic_data import (
    generate_grocery_scenario,
    generate_apparel_scenario,
    generate_electronics_scenario,
)

# Generate grocery scenario
scenario = generate_grocery_scenario(include_festivals=True, days=90)

print(f"Scenario: {scenario['scenario_name']}")
print(f"Business: {scenario['business_type']}")
print(f"Date range: {scenario['date_range']}")
print(f"Festivals: {[f['name'] for f in scenario['festivals']]}")
print(f"Total records: {scenario['total_records']}")
print(f"Categories: {scenario['categories']}")
```

## Data Characteristics

### Realistic Patterns

1. **Day-of-Week Variation**:
   - Weekends (Sat/Sun): 10-30% higher demand
   - Fridays: 5-15% higher demand
   - Weekdays: Normal demand

2. **Seasonal Patterns**:
   - Festival months (Sep-Nov): 10-50% higher demand
   - Summer months (May-Jun): 5-10% lower demand
   - Varies by business type

3. **Festival Impact**:
   - Gradual increase 7 days before festival
   - Peak on festival day (1.5x to 3.5x normal demand)
   - Gradual decrease 3 days after festival
   - Category-specific multipliers (e.g., sweets 3.5x during Diwali)

4. **Random Variance**:
   - Category-specific variance (15-50%)
   - Gaussian noise for realism
   - Non-negative quantities

### Festival Multipliers by Business Type

**Grocery (Diwali)**:
- Sweets: 3.5x
- Snacks: 2.0x
- Beverages: 1.6x
- Staples: 1.5x

**Apparel (Diwali)**:
- Traditional: 3.5x
- Kids: 2.5x
- Accessories: 2.2x
- Formal: 2.0x

**Electronics (Diwali)**:
- TV: 3.0x
- Appliances: 2.8x
- Mobile: 2.5x
- Laptop: 2.2x

## Usage in VyaparSaathi

### Demo Mode Workflow

1. **User Registration**: New users start in demo mode by default
2. **Exploration**: Users explore forecasts using synthetic data
3. **Data Upload**: Users upload real sales data
4. **Mode Switch**: System switches to real data mode
5. **Clear Indicators**: All responses show demo/real mode status

### Integration Points

- **Data Processor**: Falls back to synthetic data when no real data available
- **Forecast Engine**: Uses synthetic patterns for low-data mode forecasting
- **Risk Assessor**: Generates realistic risk scenarios for demos
- **AI Explainer**: Provides explanations for synthetic data insights

## Testing

The module includes comprehensive tests:

- **Unit Tests** (`test_synthetic_data.py`): Test individual components
- **Integration Tests** (`test_synthetic_integration.py`): Test complete workflows

Run tests:
```bash
cd packages/backend
python -m pytest tests/test_synthetic_data.py -v
python -m pytest tests/test_synthetic_integration.py -v
```

## Requirements Validation

This implementation satisfies:

- **Requirement 8.1**: Generates realistic synthetic sales data
- **Requirement 8.2**: Creates festival demand patterns based on industry research
- **Requirement 8.3**: Clearly indicates demo mode usage
- **Requirement 8.4**: Provides sample scenarios for different retailer types
- **Requirement 8.5**: Allows switching between demo and real data modes

## Future Enhancements

Potential improvements:

1. **Regional Variations**: More detailed regional demand patterns
2. **Weather Impact**: Incorporate weather effects on demand
3. **Competitor Events**: Model competitive promotions
4. **Custom Scenarios**: User-defined scenario parameters
5. **Historical Calibration**: Calibrate synthetic patterns to user's real data
