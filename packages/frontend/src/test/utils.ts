/**
 * Test utilities for VyaparSaathi frontend tests.
 * 
 * This module provides helper functions for testing React components and utilities.
 */

import { render, RenderOptions } from '@testing-library/react';
import { ReactElement } from 'react';

/**
 * Custom render function that wraps components with common providers.
 * 
 * @param ui - The React component to render
 * @param options - Additional render options
 * @returns Render result with all testing-library utilities
 */
export function renderWithProviders(
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) {
  // Add any global providers here (Router, Theme, etc.)
  // For now, just use the default render
  return render(ui, options);
}

/**
 * Helper to wait for async operations to complete.
 * Useful for testing components with async data fetching.
 * 
 * @param ms - Milliseconds to wait
 */
export const wait = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

/**
 * Mock API response helper.
 * 
 * @param data - The data to return
 * @param delay - Optional delay in milliseconds
 */
export const mockApiResponse = <T>(data: T, delay = 0): Promise<T> => {
  return new Promise(resolve => {
    setTimeout(() => resolve(data), delay);
  });
};

/**
 * Mock API error helper.
 * 
 * @param error - The error message or object
 * @param delay - Optional delay in milliseconds
 */
export const mockApiError = (error: string | Error, delay = 0): Promise<never> => {
  return new Promise((_, reject) => {
    setTimeout(() => {
      reject(typeof error === 'string' ? new Error(error) : error);
    }, delay);
  });
};

/**
 * Helper to create a mock file for file upload testing.
 * 
 * @param name - File name
 * @param content - File content
 * @param type - MIME type
 */
export const createMockFile = (
  name: string,
  content: string,
  type = 'text/csv'
): File => {
  const blob = new Blob([content], { type });
  return new File([blob], name, { type });
};

/**
 * Helper to format CSV data for testing.
 * 
 * @param headers - CSV headers
 * @param rows - CSV data rows
 */
export const createCsvContent = (headers: string[], rows: string[][]): string => {
  const headerLine = headers.join(',');
  const dataLines = rows.map(row => row.join(',')).join('\n');
  return `${headerLine}\n${dataLines}`;
};

/**
 * Helper to validate date strings.
 * 
 * @param dateString - Date string to validate
 */
export const isValidDateString = (dateString: string): boolean => {
  const date = new Date(dateString);
  return date instanceof Date && !isNaN(date.getTime());
};

/**
 * Helper to check if a value is within a range.
 * 
 * @param value - Value to check
 * @param min - Minimum value (inclusive)
 * @param max - Maximum value (inclusive)
 */
export const isInRange = (value: number, min: number, max: number): boolean => {
  return value >= min && value <= max;
};

/**
 * Helper to validate confidence indicators (0-1 range).
 * 
 * @param confidence - Confidence value to validate
 */
export const isValidConfidence = (confidence: number): boolean => {
  return isInRange(confidence, 0, 1);
};

/**
 * Helper to validate forecast horizon (7-14 days as per spec).
 * 
 * @param horizon - Forecast horizon in days
 */
export const isValidForecastHorizon = (horizon: number): boolean => {
  return isInRange(horizon, 7, 14);
};

/**
 * Helper to check if an array has unique values.
 * 
 * @param arr - Array to check
 */
export const hasUniqueValues = <T>(arr: T[]): boolean => {
  return new Set(arr).size === arr.length;
};

/**
 * Helper to validate SKU format.
 * 
 * @param sku - SKU string to validate
 */
export const isValidSku = (sku: string): boolean => {
  return /^SKU[A-Z0-9]{5,10}$/.test(sku);
};

/**
 * Helper to validate required fields in an object.
 * 
 * @param obj - Object to validate
 * @param requiredFields - Array of required field names
 */
export const hasRequiredFields = (
  obj: Record<string, any>,
  requiredFields: string[]
): boolean => {
  return requiredFields.every(field => field in obj && obj[field] !== undefined);
};

/**
 * Helper to calculate percentage difference.
 * 
 * @param baseline - Baseline value
 * @param comparison - Comparison value
 */
export const percentageDifference = (baseline: number, comparison: number): number => {
  if (baseline === 0) return comparison === 0 ? 0 : Infinity;
  return ((comparison - baseline) / baseline) * 100;
};

/**
 * Helper to check if a date is within a festival period.
 * 
 * @param date - Date to check
 * @param festivalDate - Festival start date
 * @param duration - Festival duration in days
 */
export const isInFestivalPeriod = (
  date: Date,
  festivalDate: Date,
  duration: number
): boolean => {
  const festivalEnd = new Date(festivalDate);
  festivalEnd.setDate(festivalEnd.getDate() + duration);
  return date >= festivalDate && date <= festivalEnd;
};

// Re-export commonly used testing-library utilities
export { screen, waitFor, within, fireEvent } from '@testing-library/react';
export { default as userEvent } from '@testing-library/user-event';
