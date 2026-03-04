"""
Property-based test for regional festival customization.

Feature: vyapar-saathi
Property 5: Regional Festival Customization
Validates: Requirements 2.3

This test validates that forecasts generated for different regions should vary
based on regional festival patterns and demand multipliers.
"""
import pytest
from hypothesis import given, strategies as st, assume, settings
from typing import Dict, Any, List
from datetime import datetime, timedelta

# Import festival calendar functions
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from festival_calendar.festival_seed_data import (
    FESTIVAL_SEED_DATA,
    REGIONAL_VARIATIONS,
    apply_regional_variation,
    get_festivals_by_region,
    CATEGORIES,
)


# Custom strategies for regional festival testing
@st.composite
def multi_region_festival_strategy(draw) -> Dict[str, Any]:
    """
    Generate a festival that occurs in multiple regions.
    
    Returns a festival from seed data that has multiple regions.
    """
    # Filter festivals that occur in multiple regions
    multi_region_festivals = [
        f for f in FESTIVAL_SEED_DATA
        if len(f['region']) > 1
    ]
    
    assume(len(multi_region_festivals) > 0)
    
    return draw(st.sampled_from(multi_region_festivals))


@st.composite
def region_pair_strategy(draw, festival: Dict[str, Any]) -> tuple[str, str]:
    """
    Generate a pair of different regions from a festival's region list.
    
    Args:
        festival: Festival data with region list
        
    Returns:
        Tuple of two different region strings
    """
    regions = festival['region']
    assume(len(regions) >= 2)
    
    region1 = draw(st.sampled_from(regions))
    region2 = draw(st.sampled_from([r for r in regions if r != region1]))
    
    return region1, region2


@st.composite
def product_category_strategy(draw, festival: Dict[str, Any]) -> str:
    """
    Generate a product category from a festival's demand multipliers.
    
    Args:
        festival: Festival data with demandMultipliers
        
    Returns:
        Product category string
    """
    categories = list(festival['demandMultipliers'].keys())
    assume(len(categories) > 0)
    
    return draw(st.sampled_from(categories))


# Property Tests

@settings(max_examples=100)
@given(data=st.data())
def test_regional_variation_exists_for_multi_region_festivals(data):
    """
    Property: For any festival occurring in multiple regions, forecasts should
    vary based on regional patterns.
    
    This test verifies that when a festival occurs in multiple regions,
    the demand multipliers are adjusted according to regional variations.
    """
    # Generate a multi-region festival
    festival = data.draw(multi_region_festival_strategy())
    
    # Get two different regions
    region1, region2 = data.draw(region_pair_strategy(festival))
    
    # Apply regional variations
    regional_festival_1 = apply_regional_variation(festival, region1)
    regional_festival_2 = apply_regional_variation(festival, region2)
    
    # Property: Regional variations should exist
    # At least one demand multiplier should differ between regions
    multipliers_differ = False
    for category in festival['demandMultipliers'].keys():
        mult1 = regional_festival_1['demandMultipliers'].get(category, 0)
        mult2 = regional_festival_2['demandMultipliers'].get(category, 0)
        
        if mult1 != mult2:
            multipliers_differ = True
            break
    
    # If regional variations are defined for this festival, multipliers should differ
    festival_name = festival['name'].lower().replace(' ', '-').replace("'", '')
    has_regional_variations = festival_name in REGIONAL_VARIATIONS
    
    if has_regional_variations:
        # Check if both regions have variations defined
        region1_has_variation = region1 in REGIONAL_VARIATIONS.get(festival_name, {})
        region2_has_variation = region2 in REGIONAL_VARIATIONS.get(festival_name, {})
        
        if region1_has_variation and region2_has_variation:
            # Get adjustment factors
            adj1 = REGIONAL_VARIATIONS[festival_name][region1]['multiplierAdjustment']
            adj2 = REGIONAL_VARIATIONS[festival_name][region2]['multiplierAdjustment']
            
            # If adjustments differ, multipliers should differ
            if adj1 != adj2:
                assert multipliers_differ, (
                    f"Festival {festival['name']} has different regional adjustments "
                    f"({region1}: {adj1}, {region2}: {adj2}) but multipliers are identical"
                )


@settings(max_examples=100)
@given(data=st.data())
def test_regional_multiplier_adjustment_applied_correctly(data):
    """
    Property: Regional multiplier adjustments should be applied correctly
    to all demand multipliers.
    
    This test verifies that the regional adjustment factor is correctly
    multiplied with base demand multipliers.
    """
    # Generate a multi-region festival
    festival = data.draw(multi_region_festival_strategy())
    
    # Get a region from the festival
    region = data.draw(st.sampled_from(festival['region']))
    
    # Apply regional variation
    regional_festival = apply_regional_variation(festival, region)
    
    # Check if regional variations exist for this festival
    festival_name = festival['name'].lower().replace(' ', '-').replace("'", '')
    
    if festival_name in REGIONAL_VARIATIONS:
        regional_data = REGIONAL_VARIATIONS[festival_name].get(region)
        
        if regional_data:
            adjustment = regional_data['multiplierAdjustment']
            
            # Property: Each multiplier should be adjusted by the regional factor
            for category, base_multiplier in festival['demandMultipliers'].items():
                expected_multiplier = base_multiplier * adjustment
                actual_multiplier = regional_festival['demandMultipliers'][category]
                
                # Allow small floating point differences
                assert abs(actual_multiplier - expected_multiplier) < 0.001, (
                    f"Category {category} multiplier not adjusted correctly. "
                    f"Expected {expected_multiplier}, got {actual_multiplier}"
                )


@settings(max_examples=100)
@given(data=st.data())
def test_regional_festivals_filtered_by_region(data):
    """
    Property: Querying festivals by region should only return festivals
    that occur in that region.
    
    This test verifies that regional filtering works correctly.
    """
    # Generate a region
    region = data.draw(st.sampled_from(['north', 'south', 'east', 'west', 'central']))
    
    # Get festivals for this region
    regional_festivals = get_festivals_by_region(region)
    
    # Property: All returned festivals should include the specified region
    for festival in regional_festivals:
        assert region in festival['region'], (
            f"Festival {festival['name']} returned for region {region} "
            f"but only occurs in {festival['region']}"
        )


@settings(max_examples=100)
@given(data=st.data())
def test_regional_emphasis_categories_have_higher_multipliers(data):
    """
    Property: Categories emphasized in a region should have higher or equal
    multipliers compared to the base festival.
    
    This test verifies that regional emphasis is reflected in demand multipliers.
    """
    # Generate a multi-region festival
    festival = data.draw(multi_region_festival_strategy())
    
    # Get a region from the festival
    region = data.draw(st.sampled_from(festival['region']))
    
    # Check if regional variations exist
    festival_name = festival['name'].lower().replace(' ', '-').replace("'", '')
    
    if festival_name not in REGIONAL_VARIATIONS:
        assume(False)  # Skip if no regional variations defined
    
    regional_data = REGIONAL_VARIATIONS[festival_name].get(region)
    
    if not regional_data:
        assume(False)  # Skip if no data for this region
    
    # Apply regional variation
    regional_festival = apply_regional_variation(festival, region)
    
    # Property: Regional adjustment should be positive (>= 1.0) or maintain base values
    adjustment = regional_data['multiplierAdjustment']
    
    for category in festival['demandMultipliers'].keys():
        base_multiplier = festival['demandMultipliers'][category]
        regional_multiplier = regional_festival['demandMultipliers'][category]
        
        # Regional multiplier should be base * adjustment
        expected = base_multiplier * adjustment
        
        assert abs(regional_multiplier - expected) < 0.001, (
            f"Regional multiplier for {category} in {region} doesn't match expected adjustment"
        )


@settings(max_examples=50)
@given(data=st.data())
def test_same_festival_different_regions_produce_different_forecasts(data):
    """
    Property: The same festival in different regions should produce different
    demand forecasts when regional variations exist.
    
    This is the core property for regional customization.
    """
    # Generate a multi-region festival
    festival = data.draw(multi_region_festival_strategy())
    
    # Get two different regions
    region1, region2 = data.draw(region_pair_strategy(festival))
    
    # Get a product category
    category = data.draw(product_category_strategy(festival))
    
    # Apply regional variations
    regional_festival_1 = apply_regional_variation(festival, region1)
    regional_festival_2 = apply_regional_variation(festival, region2)
    
    # Get demand multipliers for the category
    multiplier_1 = regional_festival_1['demandMultipliers'].get(category, 1.0)
    multiplier_2 = regional_festival_2['demandMultipliers'].get(category, 1.0)
    
    # Check if regional variations are defined
    festival_name = festival['name'].lower().replace(' ', '-').replace("'", '')
    
    if festival_name in REGIONAL_VARIATIONS:
        region1_data = REGIONAL_VARIATIONS[festival_name].get(region1)
        region2_data = REGIONAL_VARIATIONS[festival_name].get(region2)
        
        if region1_data and region2_data:
            adj1 = region1_data['multiplierAdjustment']
            adj2 = region2_data['multiplierAdjustment']
            
            # Property: If adjustments differ, multipliers should differ
            if adj1 != adj2:
                assert multiplier_1 != multiplier_2, (
                    f"Festival {festival['name']} in {region1} and {region2} "
                    f"should have different multipliers for {category} "
                    f"(adjustments: {adj1} vs {adj2})"
                )
                
                # Property: The ratio of multipliers should match the ratio of adjustments
                ratio_multipliers = multiplier_1 / multiplier_2 if multiplier_2 != 0 else 0
                ratio_adjustments = adj1 / adj2 if adj2 != 0 else 0
                
                assert abs(ratio_multipliers - ratio_adjustments) < 0.001, (
                    f"Multiplier ratio ({ratio_multipliers}) doesn't match "
                    f"adjustment ratio ({ratio_adjustments})"
                )


@settings(max_examples=100)
@given(data=st.data())
def test_regional_variation_preserves_festival_structure(data):
    """
    Property: Applying regional variations should preserve the festival structure
    and only modify demand multipliers.
    
    This test ensures that regional variations don't corrupt other festival data.
    """
    # Generate a multi-region festival
    festival = data.draw(multi_region_festival_strategy())
    
    # Get a region from the festival
    region = data.draw(st.sampled_from(festival['region']))
    
    # Apply regional variation
    regional_festival = apply_regional_variation(festival, region)
    
    # Property: Core festival attributes should remain unchanged
    assert regional_festival['festivalId'] == festival['festivalId']
    assert regional_festival['name'] == festival['name']
    assert regional_festival['date'] == festival['date']
    assert regional_festival['region'] == festival['region']
    assert regional_festival['category'] == festival['category']
    assert regional_festival['duration'] == festival['duration']
    assert regional_festival['preparationDays'] == festival['preparationDays']
    
    # Property: All original categories should still exist
    for category in festival['demandMultipliers'].keys():
        assert category in regional_festival['demandMultipliers'], (
            f"Category {category} missing after regional variation"
        )


@settings(max_examples=100)
@given(data=st.data())
def test_regional_multipliers_remain_positive(data):
    """
    Property: Regional demand multipliers should always remain positive
    after applying regional variations.
    
    This ensures that regional adjustments don't produce invalid negative multipliers.
    """
    # Generate a multi-region festival
    festival = data.draw(multi_region_festival_strategy())
    
    # Get a region from the festival
    region = data.draw(st.sampled_from(festival['region']))
    
    # Apply regional variation
    regional_festival = apply_regional_variation(festival, region)
    
    # Property: All multipliers should be positive
    for category, multiplier in regional_festival['demandMultipliers'].items():
        assert multiplier > 0, (
            f"Category {category} has non-positive multiplier {multiplier} "
            f"after regional variation for {region}"
        )


# Integration test with realistic scenarios
def test_diwali_regional_variations():
    """
    Concrete example: Diwali should have different demand patterns
    in different regions.
    
    This is a concrete test that complements the property-based tests.
    """
    # Get Diwali festival
    diwali = next((f for f in FESTIVAL_SEED_DATA if f['name'] == 'Diwali'), None)
    assert diwali is not None, "Diwali festival not found in seed data"
    
    # Apply regional variations for different regions
    diwali_north = apply_regional_variation(diwali, 'north')
    diwali_south = apply_regional_variation(diwali, 'south')
    diwali_west = apply_regional_variation(diwali, 'west')
    
    # Check that multipliers differ between regions
    # North should have higher emphasis on fireworks and jewelry
    if 'fireworks' in diwali['demandMultipliers']:
        north_fireworks = diwali_north['demandMultipliers']['fireworks']
        south_fireworks = diwali_south['demandMultipliers']['fireworks']
        
        # North has 1.1 adjustment, south has 1.0
        assert north_fireworks > south_fireworks, (
            "North should have higher fireworks demand than South for Diwali"
        )


def test_pongal_regional_specificity():
    """
    Concrete example: Pongal should only occur in South region.
    
    This tests that region-specific festivals are correctly filtered.
    """
    # Get Pongal festival
    pongal = next((f for f in FESTIVAL_SEED_DATA if f['name'] == 'Pongal'), None)
    assert pongal is not None, "Pongal festival not found in seed data"
    
    # Pongal should only be in south region
    assert pongal['region'] == ['south'], (
        f"Pongal should only occur in south region, but found in {pongal['region']}"
    )
    
    # Get festivals by region
    south_festivals = get_festivals_by_region('south')
    north_festivals = get_festivals_by_region('north')
    
    # Pongal should be in south festivals
    assert any(f['name'] == 'Pongal' for f in south_festivals), (
        "Pongal not found in south region festivals"
    )
    
    # Pongal should NOT be in north festivals
    assert not any(f['name'] == 'Pongal' for f in north_festivals), (
        "Pongal should not appear in north region festivals"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--hypothesis-show-statistics"])
