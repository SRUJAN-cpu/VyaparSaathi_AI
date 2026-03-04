"""
Unit tests for forecast engine

Tests the forecasting engine components including data quality assessment,
pattern-based forecasting, and storage.
"""

import pytest
from datetime import datetime, timedelta
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from forecast_engine.data_quality import (
    assess_data_quality,
    determine_forecasting_method,
    calculate_confidence_adjustment
)
from forecast_engine.pattern_forecaster import (
    get_business_type_from_profile,
    get_region_from_profile,
    calculate_baseline_demand,
    apply_festival_impact,
    calculate_confidence_bounds
)


class TestDataQuality:
    """Test data quality assessment functions."""
    
    def test_assess_data_quality_good(self):
        """Test data quality assessment with good data."""
        result = assess_data_quality(
            record_count=100,
            completeness=0.95,
            recency_days=5,
            consistency_score=0.9
        )
        
        assert result['quality'] == 'good'
        assert result['score'] >= 0.7
        assert 'components' in result
        assert 'metrics' in result
    
    def test_assess_data_quality_fair(self):
        """Test data quality assessment with fair data."""
        result = assess_data_quality(
            record_count=40,
            completeness=0.7,
            recency_days=20,
            consistency_score=0.6
        )
        
        assert result['quality'] == 'fair'
        assert 0.4 <= result['score'] < 0.7
    
    def test_assess_data_quality_poor(self):
        """Test data quality assessment with poor data."""
        result = assess_data_quality(
            record_count=10,
            completeness=0.5,
            recency_days=100,
            consistency_score=0.3
        )
        
        assert result['quality'] == 'poor'
        assert result['score'] < 0.4
    
    def test_determine_forecasting_method_low_data(self):
        """Test method determination for low-data mode."""
        method = determine_forecasting_method(0.5, 'low-data')
        assert method == 'pattern'
    
    def test_determine_forecasting_method_structured_high_quality(self):
        """Test method determination for high quality structured data."""
        method = determine_forecasting_method(0.8, 'structured')
        assert method == 'ml'
    
    def test_determine_forecasting_method_structured_medium_quality(self):
        """Test method determination for medium quality structured data."""
        method = determine_forecasting_method(0.5, 'structured')
        assert method == 'hybrid'
    
    def test_determine_forecasting_method_structured_low_quality(self):
        """Test method determination for low quality structured data."""
        method = determine_forecasting_method(0.3, 'structured')
        assert method == 'pattern'
    
    def test_calculate_confidence_adjustment(self):
        """Test confidence adjustment calculation."""
        # ML with high quality
        confidence = calculate_confidence_adjustment(0.9, 'ml')
        assert 0.85 <= confidence <= 0.95
        
        # Pattern with low quality
        confidence = calculate_confidence_adjustment(0.3, 'pattern')
        assert 0.5 <= confidence <= 0.7


class TestPatternForecaster:
    """Test pattern-based forecasting functions."""
    
    def test_get_business_type_from_profile(self):
        """Test business type extraction from profile."""
        profile = {
            'businessInfo': {
                'type': 'grocery'
            }
        }
        
        business_type = get_business_type_from_profile(profile)
        assert business_type == 'grocery'
    
    def test_get_business_type_from_profile_default(self):
        """Test business type extraction with no profile."""
        business_type = get_business_type_from_profile(None)
        assert business_type == 'general'
    
    def test_get_region_from_profile(self):
        """Test region extraction from profile."""
        profile = {
            'businessInfo': {
                'location': {
                    'region': 'south'
                }
            }
        }
        
        region = get_region_from_profile(profile)
        assert region == 'south'
    
    def test_get_region_from_profile_default(self):
        """Test region extraction with no profile."""
        region = get_region_from_profile(None)
        assert region == 'north'
    
    def test_calculate_baseline_demand(self):
        """Test baseline demand calculation."""
        from synthetic_data.pattern_generator import get_seasonal_factors
        
        seasonal_factors = get_seasonal_factors('grocery')
        date = datetime(2024, 10, 15)  # October - festival season
        
        baseline = calculate_baseline_demand(
            category='sweets',
            business_type='grocery',
            date=date,
            seasonal_factors=seasonal_factors
        )
        
        # Should be positive
        assert baseline > 0
        
        # October should have higher demand due to seasonal factor
        assert baseline > 30  # Base demand for sweets is 30
    
    def test_apply_festival_impact(self):
        """Test festival impact application."""
        festivals = [
            {
                'name': 'Diwali',
                'date': '2024-10-20',
                'preparationDays': 3,
                'duration': 2,
                'demandMultipliers': {
                    'sweets': 3.5
                }
            }
        ]
        
        # Date during festival
        date = datetime(2024, 10, 20)
        baseline = 100.0
        
        adjusted_demand, multiplier, contributing = apply_festival_impact(
            baseline_demand=baseline,
            date=date,
            category='sweets',
            festivals=festivals,
            business_type='grocery'
        )
        
        # Should have festival impact
        assert adjusted_demand > baseline
        assert multiplier > 1.0
        assert 'Diwali' in contributing
    
    def test_apply_festival_impact_no_festival(self):
        """Test festival impact with no festivals."""
        festivals = []
        
        date = datetime(2024, 10, 20)
        baseline = 100.0
        
        adjusted_demand, multiplier, contributing = apply_festival_impact(
            baseline_demand=baseline,
            date=date,
            category='sweets',
            festivals=festivals,
            business_type='grocery'
        )
        
        # Should have no impact
        assert adjusted_demand == baseline
        assert multiplier == 1.0
        assert len(contributing) == 0
    
    def test_calculate_confidence_bounds(self):
        """Test confidence bounds calculation."""
        lower, upper, confidence = calculate_confidence_bounds(
            demand_forecast=100.0,
            data_quality_score=0.7,
            festival_multiplier=1.5,
            variance=0.3
        )
        
        # Bounds should be around forecast
        assert lower < 100.0
        assert upper > 100.0
        assert lower >= 0  # Should not be negative
        
        # Confidence should be reasonable
        assert 0.5 <= confidence <= 0.95
    
    def test_calculate_confidence_bounds_high_festival_impact(self):
        """Test confidence bounds with high festival impact."""
        lower, upper, confidence = calculate_confidence_bounds(
            demand_forecast=100.0,
            data_quality_score=0.7,
            festival_multiplier=3.0,  # High multiplier
            variance=0.3
        )
        
        # High festival impact should reduce confidence
        assert confidence < 0.8
        
        # Bounds should be wider
        assert (upper - lower) > 50


class TestForecastIntegration:
    """Integration tests for forecast generation."""
    
    def test_generate_pattern_forecast_basic(self):
        """Test basic pattern forecast generation."""
        from forecast_engine.pattern_forecaster import generate_pattern_forecast
        
        forecast_context = {
            'userId': 'test_user',
            'forecastHorizon': 7,
            'startDate': datetime.utcnow().date().isoformat(),
            'festivals': [],
            'userProfile': {
                'businessInfo': {
                    'type': 'grocery',
                    'location': {
                        'region': 'north'
                    }
                }
            },
            'dataQuality': {
                'score': 0.5,
                'quality': 'fair'
            },
            'categories': ['sweets', 'snacks']
        }
        
        result = generate_pattern_forecast(forecast_context)
        
        # Check result structure
        assert 'userId' in result
        assert 'forecasts' in result
        assert 'summary' in result
        
        # Check forecasts
        assert len(result['forecasts']) == 2  # Two categories
        
        for forecast in result['forecasts']:
            assert 'sku' in forecast
            assert 'category' in forecast
            assert 'predictions' in forecast
            assert 'confidence' in forecast
            assert 'methodology' in forecast
            assert forecast['methodology'] == 'pattern'
            
            # Check predictions
            assert len(forecast['predictions']) == 7  # 7 days
            
            for prediction in forecast['predictions']:
                assert 'date' in prediction
                assert 'demandForecast' in prediction
                assert 'lowerBound' in prediction
                assert 'upperBound' in prediction
                assert 'festivalMultiplier' in prediction
                assert 'confidence' in prediction
                
                # Validate bounds
                assert prediction['lowerBound'] <= prediction['demandForecast']
                assert prediction['demandForecast'] <= prediction['upperBound']
    
    def test_generate_pattern_forecast_with_festival(self):
        """Test pattern forecast with festival impact."""
        from forecast_engine.pattern_forecaster import generate_pattern_forecast
        
        # Festival in 3 days
        festival_date = (datetime.utcnow() + timedelta(days=3)).date().isoformat()
        
        forecast_context = {
            'userId': 'test_user',
            'forecastHorizon': 7,
            'startDate': datetime.utcnow().date().isoformat(),
            'festivals': [
                {
                    'name': 'Diwali',
                    'date': festival_date,
                    'preparationDays': 3,
                    'duration': 2,
                    'demandMultipliers': {
                        'sweets': 3.5,
                        'snacks': 2.0
                    }
                }
            ],
            'userProfile': {
                'businessInfo': {
                    'type': 'grocery',
                    'location': {
                        'region': 'north'
                    }
                }
            },
            'dataQuality': {
                'score': 0.5,
                'quality': 'fair'
            },
            'categories': ['sweets']
        }
        
        result = generate_pattern_forecast(forecast_context)
        
        # Check that festival impact is present
        forecast = result['forecasts'][0]
        predictions = forecast['predictions']
        
        # Find predictions around festival date
        festival_predictions = [
            p for p in predictions
            if p['festivalMultiplier'] > 1.0
        ]
        
        # Should have some predictions with festival impact
        assert len(festival_predictions) > 0
        
        # Check that Diwali is in contributing festivals
        diwali_predictions = [
            p for p in predictions
            if 'Diwali' in p['festivals']
        ]
        assert len(diwali_predictions) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
