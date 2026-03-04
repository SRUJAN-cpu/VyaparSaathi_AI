/**
 * Dashboard Page
 * Forecast and risk visualization
 */

import React, { useEffect, useState } from 'react';
import ForecastChart from '../components/ForecastChart';
import RiskIndicator from '../components/RiskIndicator';
import ReorderCard from '../components/ReorderCard';
import { getForecast, getRiskAssessment } from '../services/api';

const DashboardPage: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [forecastData, setForecastData] = useState<any>(null);
  const [riskData, setRiskData] = useState<any>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    setError(null);

    // Load forecast data
    const forecastResult = await getForecast({ forecastHorizon: 14 });
    if (!forecastResult.success) {
      setError(forecastResult.error || 'Failed to load forecast data');
      setLoading(false);
      return;
    }

    // Load risk assessment data
    const riskResult = await getRiskAssessment();
    if (!riskResult.success) {
      setError(riskResult.error || 'Failed to load risk assessment');
      setLoading(false);
      return;
    }

    setForecastData(forecastResult.data);
    setRiskData(riskResult.data);
    setLoading(false);
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '3rem' }}>
        <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>⏳</div>
        <p>Loading dashboard data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div>
        <h1>Dashboard</h1>
        <div style={{
          padding: '1.5rem',
          backgroundColor: '#ffebee',
          color: '#c62828',
          borderRadius: '8px',
          border: '1px solid #ef5350',
          marginTop: '1rem',
        }}>
          <p style={{ margin: 0, marginBottom: '1rem' }}>{error}</p>
          <button
            onClick={loadData}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: '#c62828',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
            }}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  // Mock data for demonstration (replace with actual API data)
  const mockForecast = forecastData || {
    predictions: [
      { date: '2024-01-01', demandForecast: 100, lowerBound: 80, upperBound: 120 },
      { date: '2024-01-02', demandForecast: 110, lowerBound: 90, upperBound: 130 },
      { date: '2024-01-03', demandForecast: 150, lowerBound: 130, upperBound: 170 },
      { date: '2024-01-04', demandForecast: 180, lowerBound: 160, upperBound: 200 },
      { date: '2024-01-05', demandForecast: 200, lowerBound: 180, upperBound: 220 },
      { date: '2024-01-06', demandForecast: 190, lowerBound: 170, upperBound: 210 },
      { date: '2024-01-07', demandForecast: 160, lowerBound: 140, upperBound: 180 },
    ],
  };

  const mockRisks = riskData || [
    {
      sku: 'DIYA-001',
      category: 'Decorations',
      currentStock: 50,
      stockoutRisk: { probability: 0.75 },
      overstockRisk: { probability: 0.15 },
      recommendation: {
        action: 'reorder',
        suggestedQuantity: 200,
        urgency: 'high',
        reasoning: [
          'High demand expected during Diwali',
          'Current stock insufficient for 7-day forecast',
          'Historical stockout during last festival',
        ],
        confidence: 0.85,
      },
    },
    {
      sku: 'SWEET-002',
      category: 'Food Items',
      currentStock: 300,
      stockoutRisk: { probability: 0.25 },
      overstockRisk: { probability: 0.45 },
      recommendation: {
        action: 'maintain',
        suggestedQuantity: 300,
        urgency: 'low',
        reasoning: [
          'Current stock adequate for forecast period',
          'Balanced risk profile',
        ],
        confidence: 0.72,
      },
    },
  ];

  return (
    <div>
      <h1 style={{ marginBottom: '0.5rem' }}>Dashboard</h1>
      <p style={{ color: '#666', marginBottom: '2rem' }}>
        View your demand forecasts and inventory risk assessments
      </p>

      {/* Forecast Section */}
      <section style={{ marginBottom: '2rem' }}>
        <h2 style={{ marginBottom: '1rem' }}>📈 Demand Forecast</h2>
        <ForecastChart predictions={mockForecast.predictions} />
      </section>

      {/* Risk Overview Section */}
      <section style={{ marginBottom: '2rem' }}>
        <h2 style={{ marginBottom: '1rem' }}>⚠️ Risk Overview</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
          {mockRisks.map((risk: any) => (
            <React.Fragment key={risk.sku}>
              <RiskIndicator
                type="stockout"
                probability={risk.stockoutRisk.probability}
                label={`${risk.sku} - Stockout`}
              />
              <RiskIndicator
                type="overstock"
                probability={risk.overstockRisk.probability}
                label={`${risk.sku} - Overstock`}
              />
            </React.Fragment>
          ))}
        </div>
      </section>

      {/* Reorder Recommendations Section */}
      <section>
        <h2 style={{ marginBottom: '1rem' }}>📦 Reorder Recommendations</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: '1.5rem' }}>
          {mockRisks.map((risk: any) => (
            <ReorderCard
              key={risk.sku}
              sku={risk.sku}
              category={risk.category}
              currentStock={risk.currentStock}
              recommendation={risk.recommendation}
            />
          ))}
        </div>
      </section>
    </div>
  );
};

export default DashboardPage;
