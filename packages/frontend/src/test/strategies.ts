/**
 * Fast-check strategies for generating test data for VyaparSaathi frontend.
 * 
 * This module provides custom arbitraries for property-based testing using fast-check.
 * Strategies generate realistic sales data, festival calendars, and user inputs.
 */

import * as fc from 'fast-check';

// Type definitions
export interface SalesRecord {
  date: string;
  sku: string;
  quantity: number;
  category?: string;
  price?: number;
}

export interface FestivalEvent {
  festivalId: string;
  name: string;
  date: string;
  region: string[];
  category: string;
  demandMultipliers: Record<string, number>;
  duration: number;
  preparationDays: number;
}

export interface UserProfile {
  userId: string;
  businessInfo: {
    name: string;
    type: string;
    location: {
      city: string;
      state: string;
      region: string;
    };
    size: string;
  };
  dataCapabilities: {
    hasHistoricalData: boolean;
    dataQuality: string;
    lastUpdated: string;
  };
  preferences: {
    forecastHorizon: number;
    riskTolerance: string;
  };
}

export interface ForecastRequest {
  userId: string;
  forecastHorizon: number;
  targetFestivals: string[];
  dataMode: 'structured' | 'low-data';
  confidence: number;
}

export interface DailyPrediction {
  date: string;
  demandForecast: number;
  lowerBound: number;
  upperBound: number;
  festivalMultiplier: number;
}

// Constants
const BUSINESS_TYPES = ['grocery', 'apparel', 'electronics', 'general'] as const;
const STORE_SIZES = ['small', 'medium', 'large'] as const;
const REGIONS = ['north', 'south', 'east', 'west', 'central'] as const;
const RISK_TOLERANCES = ['conservative', 'moderate', 'aggressive'] as const;
const DATA_QUALITIES = ['poor', 'fair', 'good'] as const;
const CATEGORIES = ['grocery', 'apparel', 'electronics', 'home', 'beauty'] as const;
const FESTIVAL_NAMES = ['Diwali', 'Eid', 'Holi', 'Christmas', 'Pongal', 'Onam', 'Durga Puja'] as const;

/**
 * Generate a valid sales record with required fields.
 */
export const salesRecordArbitrary = (): fc.Arbitrary<SalesRecord> => {
  return fc.record({
    date: fc.date({ min: new Date('2021-01-01'), max: new Date() }).map(d => d.toISOString().split('T')[0]),
    sku: fc.stringMatching(/^SKU[A-Z0-9]{5,10}$/),
    quantity: fc.integer({ min: 1, max: 1000 }),
    category: fc.constantFrom(...CATEGORIES),
    price: fc.float({ min: 1.0, max: 10000.0, noNaN: true }),
  });
};

/**
 * Generate a list of sales records.
 */
export const salesDataListArbitrary = (minSize = 1, maxSize = 100): fc.Arbitrary<SalesRecord[]> => {
  return fc.array(salesRecordArbitrary(), { minLength: minSize, maxLength: maxSize });
};

/**
 * Generate an invalid sales record missing required fields or with invalid data.
 */
export const invalidSalesRecordArbitrary = (): fc.Arbitrary<Partial<SalesRecord>> => {
  return fc.oneof(
    // Missing date
    fc.record({
      sku: fc.string({ minLength: 5, maxLength: 10 }),
      quantity: fc.integer({ min: 1, max: 1000 }),
    }),
    // Missing sku
    fc.record({
      date: fc.date().map(d => d.toISOString().split('T')[0]),
      quantity: fc.integer({ min: 1, max: 1000 }),
    }),
    // Missing quantity
    fc.record({
      date: fc.date().map(d => d.toISOString().split('T')[0]),
      sku: fc.string({ minLength: 5, maxLength: 10 }),
    }),
    // Invalid quantity (negative or zero)
    fc.record({
      date: fc.date().map(d => d.toISOString().split('T')[0]),
      sku: fc.string({ minLength: 5, maxLength: 10 }),
      quantity: fc.integer({ max: 0 }),
    }),
    // Invalid date format
    fc.record({
      date: fc.string({ maxLength: 5 }),
      sku: fc.string({ minLength: 5, maxLength: 10 }),
      quantity: fc.integer({ min: 1, max: 1000 }),
    }),
  );
};

/**
 * Generate a festival event with all required fields.
 */
export const festivalEventArbitrary = (): fc.Arbitrary<FestivalEvent> => {
  return fc.record({
    festivalId: fc.constantFrom(...FESTIVAL_NAMES).chain(name =>
      fc.integer({ min: 2023, max: 2025 }).map(year => `${name.toLowerCase()}-${year}`)
    ),
    name: fc.constantFrom(...FESTIVAL_NAMES),
    date: fc.date({ min: new Date(), max: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000) })
      .map(d => d.toISOString().split('T')[0]),
    region: fc.array(fc.constantFrom(...REGIONS), { minLength: 1, maxLength: 3 }).map(arr => [...new Set(arr)]),
    category: fc.constant('festival'),
    demandMultipliers: fc.record({
      grocery: fc.float({ min: 1.0, max: 5.0, noNaN: true }),
      apparel: fc.float({ min: 1.0, max: 5.0, noNaN: true }),
      electronics: fc.float({ min: 1.0, max: 5.0, noNaN: true }),
    }),
    duration: fc.integer({ min: 1, max: 10 }),
    preparationDays: fc.integer({ min: 7, max: 30 }),
  });
};

/**
 * Generate a user profile with business information and preferences.
 */
export const userProfileArbitrary = (): fc.Arbitrary<UserProfile> => {
  return fc.record({
    userId: fc.hexaString({ minLength: 8, maxLength: 12 }).map(s => `user-${s}`),
    businessInfo: fc.record({
      name: fc.string({ minLength: 5, maxLength: 50 }),
      type: fc.constantFrom(...BUSINESS_TYPES),
      location: fc.record({
        city: fc.string({ minLength: 3, maxLength: 30 }),
        state: fc.string({ minLength: 3, maxLength: 30 }),
        region: fc.constantFrom(...REGIONS),
      }),
      size: fc.constantFrom(...STORE_SIZES),
    }),
    dataCapabilities: fc.record({
      hasHistoricalData: fc.boolean(),
      dataQuality: fc.constantFrom(...DATA_QUALITIES),
      lastUpdated: fc.date().map(d => d.toISOString()),
    }),
    preferences: fc.record({
      forecastHorizon: fc.integer({ min: 7, max: 14 }),
      riskTolerance: fc.constantFrom(...RISK_TOLERANCES),
    }),
  });
};

/**
 * Generate a forecast request.
 */
export const forecastRequestArbitrary = (): fc.Arbitrary<ForecastRequest> => {
  return fc.record({
    userId: fc.hexaString({ minLength: 8, maxLength: 12 }).map(s => `user-${s}`),
    forecastHorizon: fc.integer({ min: 7, max: 14 }),
    targetFestivals: fc.array(fc.string({ minLength: 3, maxLength: 20 }), { maxLength: 3 }),
    dataMode: fc.constantFrom('structured', 'low-data'),
    confidence: fc.float({ min: 0.0, max: 1.0, noNaN: true }),
  });
};

/**
 * Generate a daily prediction.
 */
export const dailyPredictionArbitrary = (): fc.Arbitrary<DailyPrediction> => {
  return fc.record({
    date: fc.date({ min: new Date(), max: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000) })
      .map(d => d.toISOString().split('T')[0]),
    demandForecast: fc.float({ min: 0, max: 1000, noNaN: true }),
    lowerBound: fc.float({ min: 0, max: 500, noNaN: true }),
    upperBound: fc.float({ min: 500, max: 1500, noNaN: true }),
    festivalMultiplier: fc.float({ min: 1.0, max: 5.0, noNaN: true }),
  });
};

/**
 * Generate inventory data for risk assessment.
 */
export const inventoryDataArbitrary = () => {
  return fc.record({
    sku: fc.stringMatching(/^SKU[A-Z0-9]{5,10}$/),
    category: fc.constantFrom(...CATEGORIES),
    currentStock: fc.integer({ min: 0, max: 10000 }),
    reorderPoint: fc.integer({ min: 10, max: 500 }),
    leadTimeDays: fc.integer({ min: 1, max: 30 }),
  });
};
