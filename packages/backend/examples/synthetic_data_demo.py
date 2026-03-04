"""
Demonstration script for synthetic data generation.

This script shows how to use the synthetic data generator to create
realistic sales data for different business types.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.synthetic_data import (
    generate_synthetic_pattern,
    generate_synthetic_sales,
    generate_grocery_scenario,
    generate_apparel_scenario,
    generate_electronics_scenario,
    set_demo_mode,
    is_demo_mode,
    add_demo_indicator,
)


def demo_pattern_generation():
    """Demonstrate pattern generation."""
    print("=" * 80)
    print("DEMO 1: Pattern Generation")
    print("=" * 80)
    
    pattern = generate_synthetic_pattern("grocery", "north")
    
    print(f"\nBusiness Type: {pattern.business_type}")
    print(f"Region: {pattern.region}")
    print(f"\nCategories and Baseline Demand:")
    for p in pattern.baseline_patterns:
        print(f"  - {p.category}: {p.normal_demand:.1f} units/day (variance: {p.variance:.2f})")
    
    print(f"\nSeasonal Factors (sample):")
    for month in [1, 6, 10, 12]:
        factor = pattern.seasonal_factors[month]
        print(f"  - Month {month}: {factor:.2f}x")
    
    print(f"\nFestival Multipliers (Diwali):")
    if "Diwali" in pattern.festival_multipliers:
        for category, mult in pattern.festival_multipliers["Diwali"].items():
            print(f"  - {category}: {mult:.2f}x")


def demo_sales_generation():
    """Demonstrate sales data generation."""
    print("\n" + "=" * 80)
    print("DEMO 2: Sales Data Generation")
    print("=" * 80)
    
    sales = generate_synthetic_sales(
        business_type="apparel",
        region="west",
        days=30,
        skus_per_category=2,
    )
    
    print(f"\nGenerated {len(sales)} sales records over 30 days")
    print(f"\nSample records:")
    for i, record in enumerate(sales[:5]):
        print(f"  {i+1}. Date: {record['date']}, SKU: {record['sku']}, "
              f"Category: {record['category']}, Qty: {record['quantity']}, "
              f"Price: ₹{record['price']:.2f}")
    
    # Calculate statistics
    total_quantity = sum(r['quantity'] for r in sales)
    total_revenue = sum(r['quantity'] * r['price'] for r in sales)
    
    print(f"\nStatistics:")
    print(f"  - Total quantity sold: {total_quantity}")
    print(f"  - Total revenue: ₹{total_revenue:,.2f}")
    print(f"  - Average daily sales: {total_quantity / 30:.1f} units")


def demo_scenarios():
    """Demonstrate pre-built scenarios."""
    print("\n" + "=" * 80)
    print("DEMO 3: Pre-built Scenarios")
    print("=" * 80)
    
    scenarios = {
        "Grocery": generate_grocery_scenario(days=60),
        "Apparel": generate_apparel_scenario(days=60),
        "Electronics": generate_electronics_scenario(days=60),
    }
    
    for name, scenario in scenarios.items():
        print(f"\n{name} Store Scenario:")
        print(f"  - Description: {scenario['description'][:80]}...")
        print(f"  - Date range: {scenario['date_range']['start']} to {scenario['date_range']['end']}")
        print(f"  - Festivals: {', '.join(f['name'] for f in scenario['festivals'])}")
        print(f"  - Categories: {', '.join(scenario['categories'])}")
        print(f"  - Total records: {scenario['total_records']}")


def demo_mode_management():
    """Demonstrate demo mode management."""
    print("\n" + "=" * 80)
    print("DEMO 4: Demo Mode Management")
    print("=" * 80)
    
    user_id = "demo-user-123"
    
    # Start in real mode
    print(f"\nInitial mode: {is_demo_mode(user_id)}")
    
    # Switch to demo mode
    set_demo_mode(user_id, True)
    print(f"After enabling demo mode: {is_demo_mode(user_id)}")
    
    # Add demo indicator to response
    response = {
        "forecast": "Sample forecast data",
        "confidence": 0.85,
    }
    
    response_with_indicator = add_demo_indicator(response, user_id)
    
    print(f"\nResponse with demo indicator:")
    print(f"  - Demo mode: {response_with_indicator['_demo_mode']}")
    print(f"  - Notice: {response_with_indicator['_demo_notice'][:60]}...")
    
    # Switch back to real mode
    set_demo_mode(user_id, False)
    print(f"\nAfter disabling demo mode: {is_demo_mode(user_id)}")


def demo_festival_impact():
    """Demonstrate festival impact on sales."""
    print("\n" + "=" * 80)
    print("DEMO 5: Festival Impact Analysis")
    print("=" * 80)
    
    # Generate scenario with festivals
    scenario = generate_grocery_scenario(include_festivals=True, days=90)
    
    if scenario['festivals']:
        festival = scenario['festivals'][0]
        print(f"\nAnalyzing impact of {festival['name']} on {festival['date']}")
        
        # Find sales around festival date
        from datetime import datetime, timedelta
        festival_date = datetime.strptime(festival['date'], "%Y-%m-%d")
        
        # Group sales by date and category
        sales_by_date = {}
        for record in scenario['sales_data']:
            date = record['date']
            category = record['category']
            if date not in sales_by_date:
                sales_by_date[date] = {}
            if category not in sales_by_date[date]:
                sales_by_date[date][category] = 0
            sales_by_date[date][category] += record['quantity']
        
        # Show sales for a few days around festival
        print(f"\nSales around festival (sample category: sweets):")
        for offset in [-7, -3, 0, 3]:
            check_date = (festival_date + timedelta(days=offset)).strftime("%Y-%m-%d")
            if check_date in sales_by_date and 'sweets' in sales_by_date[check_date]:
                qty = sales_by_date[check_date]['sweets']
                print(f"  - Day {offset:+2d}: {qty:4d} units")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("VyaparSaathi Synthetic Data Generator - Demonstration")
    print("=" * 80)
    
    demo_pattern_generation()
    demo_sales_generation()
    demo_scenarios()
    demo_mode_management()
    demo_festival_impact()
    
    print("\n" + "=" * 80)
    print("Demonstration Complete!")
    print("=" * 80)
    print("\nThe synthetic data generator is ready for use in VyaparSaathi.")
    print("It provides realistic sales data for demo purposes and low-data mode forecasting.")
