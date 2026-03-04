/**
 * Risk Indicator Component
 * Visual indicator for risk levels with color coding
 */

import React from 'react';

interface RiskIndicatorProps {
  type: 'stockout' | 'overstock';
  probability: number;
  label?: string;
}

const RiskIndicator: React.FC<RiskIndicatorProps> = ({ type, probability, label }) => {
  const getRiskLevel = (prob: number): 'low' | 'medium' | 'high' => {
    if (prob < 0.3) return 'low';
    if (prob < 0.6) return 'medium';
    return 'high';
  };

  const getRiskColor = (level: 'low' | 'medium' | 'high'): string => {
    switch (level) {
      case 'low':
        return '#4caf50';
      case 'medium':
        return '#ff9800';
      case 'high':
        return '#f44336';
    }
  };

  const riskLevel = getRiskLevel(probability);
  const color = getRiskColor(riskLevel);
  const percentage = Math.round(probability * 100);

  return (
    <div style={{
      backgroundColor: 'white',
      padding: '1.5rem',
      borderRadius: '8px',
      boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
      borderLeft: `4px solid ${color}`,
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h4 style={{ margin: 0 }}>
          {type === 'stockout' ? '⚠️ Stockout Risk' : '📦 Overstock Risk'}
        </h4>
        <span style={{
          padding: '0.25rem 0.75rem',
          backgroundColor: color,
          color: 'white',
          borderRadius: '12px',
          fontSize: '0.85rem',
          fontWeight: 'bold',
          textTransform: 'uppercase',
        }}>
          {riskLevel}
        </span>
      </div>

      <div style={{ marginBottom: '1rem' }}>
        <div style={{
          width: '100%',
          height: '8px',
          backgroundColor: '#e0e0e0',
          borderRadius: '4px',
          overflow: 'hidden',
        }}>
          <div style={{
            width: `${percentage}%`,
            height: '100%',
            backgroundColor: color,
            transition: 'width 0.3s ease',
          }} />
        </div>
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span style={{ fontSize: '0.9rem', color: '#666' }}>
          {label || 'Risk Probability'}
        </span>
        <span style={{ fontSize: '1.5rem', fontWeight: 'bold', color }}>
          {percentage}%
        </span>
      </div>
    </div>
  );
};

export default RiskIndicator;
