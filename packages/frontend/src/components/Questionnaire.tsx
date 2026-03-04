/**
 * Questionnaire Component
 * Low-data mode questionnaire for manual estimates
 */

import React, { useState } from 'react';
import { submitQuestionnaire } from '../services/api';

interface QuestionnaireProps {
  onSubmitSuccess: (data: any) => void;
  onSubmitError: (error: string) => void;
}

const Questionnaire: React.FC<QuestionnaireProps> = ({ onSubmitSuccess, onSubmitError }) => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    businessType: '',
    storeSize: '',
    lastFestivalSalesIncrease: '',
    topCategories: '',
    stockoutItems: '',
    currentInventory: '',
    averageDailySales: '',
    targetFestivals: [] as string[],
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleFestivalChange = (festival: string) => {
    setFormData(prev => ({
      ...prev,
      targetFestivals: prev.targetFestivals.includes(festival)
        ? prev.targetFestivals.filter(f => f !== festival)
        : [...prev.targetFestivals, festival],
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validation
    if (!formData.businessType || !formData.storeSize || formData.targetFestivals.length === 0) {
      onSubmitError('Please fill in all required fields');
      return;
    }

    setIsSubmitting(true);
    const result = await submitQuestionnaire({
      businessType: formData.businessType,
      storeSize: formData.storeSize,
      lastFestivalPerformance: {
        salesIncrease: parseFloat(formData.lastFestivalSalesIncrease) || 0,
        topCategories: formData.topCategories.split(',').map(c => c.trim()).filter(Boolean),
        stockoutItems: formData.stockoutItems.split(',').map(i => i.trim()).filter(Boolean),
      },
      currentInventory: formData.currentInventory,
      averageDailySales: parseFloat(formData.averageDailySales) || 0,
      targetFestivals: formData.targetFestivals,
    });
    setIsSubmitting(false);

    if (result.success) {
      onSubmitSuccess(result.data);
    } else {
      onSubmitError(result.error || 'Submission failed');
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ width: '100%' }}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        {/* Business Type */}
        <div>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>
            Business Type <span style={{ color: 'red' }}>*</span>
          </label>
          <select
            name="businessType"
            value={formData.businessType}
            onChange={handleChange}
            required
            style={{
              width: '100%',
              padding: '0.75rem',
              border: '1px solid #ccc',
              borderRadius: '4px',
              fontSize: '1rem',
            }}
          >
            <option value="">Select business type</option>
            <option value="grocery">Grocery</option>
            <option value="apparel">Apparel</option>
            <option value="electronics">Electronics</option>
            <option value="general">General Store</option>
          </select>
        </div>

        {/* Store Size */}
        <div>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>
            Store Size <span style={{ color: 'red' }}>*</span>
          </label>
          <select
            name="storeSize"
            value={formData.storeSize}
            onChange={handleChange}
            required
            style={{
              width: '100%',
              padding: '0.75rem',
              border: '1px solid #ccc',
              borderRadius: '4px',
              fontSize: '1rem',
            }}
          >
            <option value="">Select store size</option>
            <option value="small">Small (1-2 employees)</option>
            <option value="medium">Medium (3-10 employees)</option>
            <option value="large">Large (10+ employees)</option>
          </select>
        </div>

        {/* Last Festival Sales Increase */}
        <div>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>
            Last Festival Sales Increase (%)
          </label>
          <input
            type="number"
            name="lastFestivalSalesIncrease"
            value={formData.lastFestivalSalesIncrease}
            onChange={handleChange}
            placeholder="e.g., 50 for 50% increase"
            style={{
              width: '100%',
              padding: '0.75rem',
              border: '1px solid #ccc',
              borderRadius: '4px',
              fontSize: '1rem',
            }}
          />
        </div>

        {/* Top Categories */}
        <div>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>
            Top Selling Categories (comma-separated)
          </label>
          <input
            type="text"
            name="topCategories"
            value={formData.topCategories}
            onChange={handleChange}
            placeholder="e.g., Sweets, Decorations, Clothing"
            style={{
              width: '100%',
              padding: '0.75rem',
              border: '1px solid #ccc',
              borderRadius: '4px',
              fontSize: '1rem',
            }}
          />
        </div>

        {/* Stockout Items */}
        <div>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>
            Items That Ran Out of Stock (comma-separated)
          </label>
          <input
            type="text"
            name="stockoutItems"
            value={formData.stockoutItems}
            onChange={handleChange}
            placeholder="e.g., Diyas, Rangoli colors"
            style={{
              width: '100%',
              padding: '0.75rem',
              border: '1px solid #ccc',
              borderRadius: '4px',
              fontSize: '1rem',
            }}
          />
        </div>

        {/* Average Daily Sales */}
        <div>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>
            Average Daily Sales (units)
          </label>
          <input
            type="number"
            name="averageDailySales"
            value={formData.averageDailySales}
            onChange={handleChange}
            placeholder="e.g., 100"
            style={{
              width: '100%',
              padding: '0.75rem',
              border: '1px solid #ccc',
              borderRadius: '4px',
              fontSize: '1rem',
            }}
          />
        </div>

        {/* Target Festivals */}
        <div>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>
            Target Festivals <span style={{ color: 'red' }}>*</span>
          </label>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem' }}>
            {['Diwali', 'Eid', 'Holi', 'Durga Puja', 'Christmas', 'Pongal'].map(festival => (
              <label key={festival} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <input
                  type="checkbox"
                  checked={formData.targetFestivals.includes(festival)}
                  onChange={() => handleFestivalChange(festival)}
                  style={{ width: '1.2rem', height: '1.2rem' }}
                />
                <span>{festival}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isSubmitting}
          style={{
            padding: '0.75rem 2rem',
            backgroundColor: isSubmitting ? '#ccc' : '#1a73e8',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            fontSize: '1rem',
            cursor: isSubmitting ? 'not-allowed' : 'pointer',
            marginTop: '1rem',
          }}
        >
          {isSubmitting ? 'Submitting...' : 'Generate Forecast'}
        </button>
      </div>
    </form>
  );
};

export default Questionnaire;
