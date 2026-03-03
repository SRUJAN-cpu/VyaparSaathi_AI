# VyaparSaathi Frontend Testing Guide

This directory contains test utilities and examples for the VyaparSaathi frontend.

## Test Structure

- `setup.ts` - Vitest setup and configuration
- `strategies.ts` - Fast-check arbitraries for property-based testing
- `fixtures.ts` - Sample data for unit tests
- `*.test.ts` - Test files (unit and property-based tests)

## Running Tests

### Run all tests
```bash
cd packages/frontend
npm test
```

### Run tests in watch mode
```bash
npm test -- --watch
```

### Run with coverage
```bash
npm test -- --coverage
```

### Run specific test file
```bash
npm test -- example.test.ts
```

### Run with UI
```bash
npm test -- --ui
```

## Writing Tests

### Unit Tests

Unit tests verify specific examples and edge cases:

```typescript
import { describe, it, expect } from 'vitest';
import { sampleSalesData } from './fixtures';

describe('Sales Data Validation', () => {
  it('should validate correct sales records', () => {
    for (const record of sampleSalesData) {
      expect(validateSalesRecord(record)).toBe(true);
    }
  });
});
```

### Property-Based Tests

Property-based tests verify universal properties across many inputs:

```typescript
import { describe, it, expect } from 'vitest';
import * as fc from 'fast-check';
import { salesRecordArbitrary } from './strategies';

describe('Sales Data Validation', () => {
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
      }),
      { numRuns: 100 }
    );
  });
});
```

## Fast-check Configuration

Fast-check is configured with:
- `numRuns: 100` - Number of test cases to generate (default)
- Increase for more thorough testing or decrease for faster feedback

## Custom Arbitraries

The `strategies.ts` module provides custom fast-check arbitraries:

- `salesRecordArbitrary()` - Generate valid sales records
- `salesDataListArbitrary()` - Generate lists of sales records
- `invalidSalesRecordArbitrary()` - Generate invalid sales records
- `festivalEventArbitrary()` - Generate festival events
- `userProfileArbitrary()` - Generate user profiles
- `forecastRequestArbitrary()` - Generate forecast requests
- `dailyPredictionArbitrary()` - Generate daily predictions
- `inventoryDataArbitrary()` - Generate inventory data

## Fixtures

Common fixtures are defined in `fixtures.ts`:

- `sampleSalesData` - Sample sales records
- `sampleFestivalData` - Sample festival event
- `sampleUserProfile` - Sample user profile
- `sampleForecastRequest` - Sample forecast request
- `sampleDailyPredictions` - Sample daily predictions
- `sampleRiskAssessment` - Sample risk assessment

## Testing React Components

For React component tests, use `@testing-library/react`:

```typescript
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import MyComponent from './MyComponent';

describe('MyComponent', () => {
  it('should render correctly', () => {
    render(<MyComponent />);
    expect(screen.getByText('Hello')).toBeInTheDocument();
  });
});
```

## Best Practices

1. **Document properties**: Include docstrings explaining what property is being tested
2. **Link to requirements**: Use `**Validates: Requirements X.Y**` format
3. **Use appropriate arbitraries**: Choose arbitraries that match your input domain
4. **Test edge cases**: Write unit tests for specific edge cases
5. **Keep tests fast**: Limit `numRuns` during development
6. **Test user interactions**: Use `@testing-library/user-event` for user interactions
7. **Mock external dependencies**: Mock API calls and external services
8. **Use fixtures for unit tests**: Use fixtures for predictable test data
9. **Use arbitraries for property tests**: Use arbitraries for comprehensive coverage
