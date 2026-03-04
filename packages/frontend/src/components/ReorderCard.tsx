/**
 * Reorder Recommendation Card
 * Displays reorder recommendations with urgency indicators
 */

import React from 'react';

interface ReorderRecommendation {
  action: 'reorder' | 'reduce' | 'maintain';
  suggestedQuantity: number;
  urgency: 'low' | 'medium' | 'high';
  reasoning: string[];
  confidence: number;
}

interface ReorderCardProps {
  sku: string;
  category: string;
  currentStock: number;
  recommendation: ReorderRecommendation;
}

const ReorderCard: React.FC<ReorderCardProps> = ({ sku, category, currentStock, recommendation }) => {
  const getActionColor = (action: string): string => {
    switch (action) {
      case 'reorder':
        return '#1a73e8';
      case 'reduce':
        return '#ff9800';
      case 'maintain':
        return '#4caf50';
      default:
        return '#666';
    }
  };

  const getUrgencyColor = (urgency: string): string => {
    switch (urgency) {
      case 'low':
        return '#4caf50';
      case 'medium':
        return '#ff9800';
      case 'high':
        return '#f44336';
      default:
        return '#666';
    }
  };

  const actionColor = getActionColor(recommendation.action);
  const urgencyColor = getUrgencyColor(recommendation.urgency);

  return (
    <div style={{
      backgroundColor: 'white',
      padding: '1.5rem',
      borderRadius: '8px',
      boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
      borderTop: `4px solid ${actionColor}`,
    }}>
      {/* Header */}
      <div style={{ marginBottom: '1rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '0.5rem' }}>
          <div>
            <h4 style={{ margin: 0, marginBottom: '0.25rem' }}>{sku}</h4>
            <p style={{ margin: 0, color: '#666', fontSize: '0.9rem' }}>{category}</p>
          </div>
          <span style={{
            padding: '0.25rem 0.75rem',
            backgroundColor: urgencyColor,
            color: 'white',
            borderRadius: '12px',
            fontSize: '0.75rem',
            fontWeight: 'bold',
            textTransform: 'uppercase',
          }}>
            {recommendation.urgency} urgency
          </span>
        </div>
      </div>

      {/* Current Stock */}
      <div style={{
        padding: '0.75rem',
        backgroundColor: '#f5f5f5',
        borderRadius: '4px',
        marginBottom: '1rem',
      }}>
        <span style={{ fontSize: '0.85rem', color: '#666' }}>Current Stock: </span>
        <span style={{ fontSize: '1rem', fontWeight: 'bold' }}>{currentStock} units</span>
      </div>

      {/* Recommendation */}
      <div style={{ marginBottom: '1rem' }}>
        <div style={{
          padding: '1rem',
          backgroundColor: `${actionColor}15`,
          borderRadius: '4px',
          borderLeft: `3px solid ${actionColor}`,
        }}>
          <p style={{ margin: 0, marginBottom: '0.5rem', fontWeight: 'bold', color: actionColor, textTransform: 'uppercase' }}>
            {recommendation.action === 'reorder' && '📦 Reorder Recommended'}
            {recommendation.action === 'reduce' && '⬇️ Reduce Stock'}
            {recommendation.action === 'maintain' && '✅ Maintain Current Level'}
          </p>
          {recommendation.action !== 'maintain' && (
            <p style={{ margin: 0, fontSize: '1.2rem', fontWeight: 'bold' }}>
              Suggested: {recommendation.suggestedQuantity} units
            </p>
          )}
        </div>
      </div>

      {/* Reasoning */}
      <div style={{ marginBottom: '1rem' }}>
        <p style={{ fontSize: '0.85rem', fontWeight: 'bold', marginBottom: '0.5rem', color: '#666' }}>
          Reasoning:
        </p>
        <ul style={{ margin: 0, paddingLeft: '1.5rem', fontSize: '0.9rem', color: '#666' }}>
          {recommendation.reasoning.map((reason, index) => (
            <li key={index} style={{ marginBottom: '0.25rem' }}>{reason}</li>
          ))}
        </ul>
      </div>

      {/* Confidence */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <span style={{ fontSize: '0.85rem', color: '#666' }}>Confidence:</span>
        <div style={{
          flex: 1,
          height: '6px',
          backgroundColor: '#e0e0e0',
          borderRadius: '3px',
          overflow: 'hidden',
        }}>
          <div style={{
            width: `${recommendation.confidence * 100}%`,
            height: '100%',
            backgroundColor: '#1a73e8',
          }} />
        </div>
        <span style={{ fontSize: '0.85rem', fontWeight: 'bold' }}>
          {Math.round(recommendation.confidence * 100)}%
        </span>
      </div>
    </div>
  );
};

export default ReorderCard;
