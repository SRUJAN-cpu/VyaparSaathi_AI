/**
 * Test setup file for Vitest
 * 
 * This file is executed before running tests and sets up the test environment.
 */

import { expect, afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';
import '@testing-library/jest-dom/vitest';

// Cleanup after each test
afterEach(() => {
  cleanup();
});

// Configure fast-check defaults
import * as fc from 'fast-check';

// Set default configuration for property-based tests
// Minimum 100 iterations as per spec requirements
fc.configureGlobal({
  numRuns: 100,
  verbose: false,
});
