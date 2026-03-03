/**
 * Test fixtures for VyaparSaathi frontend tests.
 * 
 * This module provides sample data for unit tests.
 */

import type { SalesRecord, FestivalEvent, UserProfile } from './strategies';

export const sampleSalesData: SalesRecord[] = [
  {
    date: '2023-10-01',
    sku: 'SKU001',
    quantity: 10,
    category: 'grocery',
    price: 50.0,
  },
  {
    date: '2023-10-02',
    sku: 'SKU001',
    quantity: 15,
    category: 'grocery',
    price: 50.0,
  },
  {
    date: '2023-10-03',
    sku: 'SKU002',
    quantity: 8,
    category: 'apparel',
    price: 500.0,
  },
];

export const sampleFestivalData: FestivalEvent = {
  festivalId: 'diwali-2023',
  name: 'Diwali',
  date: '2023-11-12',
  region: ['north', 'west'],
  category: 'festival',
  demandMultipliers: {
    grocery: 2.5,
    apparel: 3.0,
    electronics: 2.0,
  },
  duration: 5,
  preparationDays: 14,
};

export const sampleUserProfile: UserProfile = {
  userId: 'test-user-123',
  businessInfo: {
    name: 'Test Store',
    type: 'grocery',
    location: {
      city: 'Mumbai',
      state: 'Maharashtra',
      region: 'west',
    },
    size: 'medium',
  },
  dataCapabilities: {
    hasHistoricalData: true,
    dataQuality: 'good',
    lastUpdated: '2023-10-01T00:00:00Z',
  },
  preferences: {
    forecastHorizon: 14,
    riskTolerance: 'moderate',
  },
};

export const sampleForecastRequest = {
  userId: 'test-user-123',
  forecastHorizon: 14,
  targetFestivals: ['diwali-2023'],
  dataMode: 'structured' as const,
  confidence: 0.8,
};

export const sampleDailyPredictions = [
  {
    date: '2023-11-01',
    demandForecast: 100,
    lowerBound: 80,
    upperBound: 120,
    festivalMultiplier: 1.0,
  },
  {
    date: '2023-11-12',
    demandForecast: 250,
    lowerBound: 200,
    upperBound: 300,
    festivalMultiplier: 2.5,
  },
];

export const sampleRiskAssessment = {
  sku: 'SKU001',
  category: 'grocery',
  currentStock: 50,
  stockoutRisk: {
    probability: 0.75,
    daysUntilStockout: 3,
    potentialLostSales: 150,
  },
  overstockRisk: {
    probability: 0.1,
    excessUnits: 0,
    carryingCost: 0,
  },
  recommendation: {
    action: 'reorder' as const,
    suggestedQuantity: 200,
    urgency: 'high' as const,
    reasoning: ['High stockout risk during festival period', 'Current stock insufficient for demand'],
    confidence: 0.85,
  },
};
