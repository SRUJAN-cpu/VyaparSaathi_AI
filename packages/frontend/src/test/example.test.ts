/**
 * Example test file demonstrating unit tests and property-based tests.
 * 
 * This file shows how to use Vitest, fast-check, and the custom strategies.
 */

import { describe, it, expect } from 'vitest';
import * as fc from 'fast-check';
import {
  salesRecordArbitrary,
  salesDataListArbitrary,
  festivalEventArbitrary,
  type SalesRecord,
} from './strategies';
import { sampleSalesData, sampleFestivalData } from './fixtures';

/**
 * Validate that a sales record has required fields.
 */
function validateSalesRecord(record: Partial<SalesRecord>): boolean {
  return (
    typeof record.date === 'string' &&
    typeof record.sku === 'string' &&
    typeof record.quantity === 'number' &&
    record.quantity > 0
  );
}

describe('Sales Data Validation', () => {
  it('should validate correct sales records', () => {
    for (const record of sampleSalesData) {
      expect(validateSalesRecord(record)).toBe(true);
    }
  });

  it('should reject records missing required fields', () => {
    const invalidRecord = { date: '2023-10-01', sku: 'SKU001' }; // Missing quantity
    expect(validateSalesRecord(invalidRecord)).toBe(false);
  });

  it('should reject records with invalid quantity', () => {
    const invalidRecord = { date: '2023-10-01', sku: 'SKU001', quantity: 0 };
    expect(validateSalesRecord(invalidRecord)).toBe(false);
  });

  it('property: all generated sales records should be valid', () => {
    /**
     * Property test: All generated sales records should be valid.
     * 
     * **Validates: Requirements 1.1, 1.5**
     */
    fc.assert(
      fc.property(salesRecordArbitrary(), (record) => {
        expect(validateSalesRecord(record)).toBe(true);
        expect(record.quantity).toBeGreaterThan(0);
        expect(record.sku).toMatch(/^SKU[A-Z0-9]{5,10}$/);
      }),
      { numRuns: 100 }
    );
  });

  it('property: all records in a list should be valid', () => {
    /**
     * Property test: All records in a list should be valid.
     * 
     * **Validates: Requirements 1.1**
     */
    fc.assert(
      fc.property(salesDataListArbitrary(1, 50), (records) => {
        expect(records.length).toBeGreaterThan(0);
        for (const record of records) {
          expect(validateSalesRecord(record)).toBe(true);
        }
      }),
      { numRuns: 100 }
    );
  });
});

describe('Festival Data', () => {
  it('should have demand multipliers', () => {
    expect(sampleFestivalData.demandMultipliers).toBeDefined();
    expect(sampleFestivalData.demandMultipliers.grocery).toBeGreaterThan(0);
  });

  it('property: festival demand multipliers should be >= 1.0', () => {
    /**
     * Property test: Festival demand multipliers should be >= 1.0.
     * 
     * **Validates: Requirements 2.2**
     */
    fc.assert(
      fc.property(festivalEventArbitrary(), (festival) => {
        for (const [category, multiplier] of Object.entries(festival.demandMultipliers)) {
          expect(multiplier).toBeGreaterThanOrEqual(1.0);
          expect(multiplier).toBeLessThanOrEqual(5.0);
        }
      }),
      { numRuns: 100 }
    );
  });

  it('property: all festivals should have at least one region', () => {
    /**
     * Property test: All festivals should have at least one region.
     * 
     * **Validates: Requirements 2.3**
     */
    fc.assert(
      fc.property(festivalEventArbitrary(), (festival) => {
        expect(festival.region.length).toBeGreaterThan(0);
        for (const region of festival.region) {
          expect(typeof region).toBe('string');
        }
      }),
      { numRuns: 100 }
    );
  });
});
