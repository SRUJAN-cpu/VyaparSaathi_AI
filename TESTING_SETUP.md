# VyaparSaathi Testing Framework Configuration

## Overview

This document describes the testing framework setup for the VyaparSaathi project. The testing infrastructure supports both unit tests and property-based tests across all three packages: frontend, backend, and infrastructure.

## Testing Frameworks

### Frontend (TypeScript/React)
- **Test Runner**: Vitest v0.34.6
- **Property-Based Testing**: fast-check v3.12.0
- **React Testing**: @testing-library/react, @testing-library/jest-dom, @testing-library/user-event
- **Test Environment**: jsdom (for DOM simulation)
- **Coverage**: V8 provider with HTML, JSON, and text reports

### Backend (Python)
- **Test Runner**: pytest v9.0.2
- **Property-Based Testing**: Hypothesis v6.151.9
- **Coverage**: pytest-cov v7.0.0
- **Mocking**: moto v5.1.21 (for AWS service mocking)

### Infrastructure (TypeScript/CDK)
- **Test Runner**: Jest v29.6.1
- **Property-Based Testing**: fast-check v3.12.0
- **CDK Testing**: aws-cdk-lib/assertions
- **TypeScript Support**: ts-jest v29.1.1

## Configuration Files

### Frontend Configuration

**vite.config.ts**
```typescript
test: {
  globals: true,
  environment: 'jsdom',
  setupFiles: './src/test/setup.ts',
  coverage: {
    provider: 'v8',
    reporter: ['text', 'json', 'html'],
    exclude: ['node_modules/', 'src/test/', '**/*.test.ts', '**/*.test.tsx'],
  },
}
```

**Fast-check Configuration** (in setup.ts)
- Default: 100 iterations per property test (as per spec requirement)
- Configurable via `fc.configureGlobal()`

### Backend Configuration

**pyproject.toml**
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--cov=src",
    "--cov-report=html",
    "--cov-report=term-missing",
    "--cov-report=xml",
    "--verbose",
    "--strict-markers",
]
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "property: Property-based tests",
    "slow: Slow running tests",
]
```

**Hypothesis Configuration** (in conftest.py)
- `default` profile: 100 examples (standard testing)
- `ci` profile: 200 examples (CI/CD pipeline)
- `dev` profile: 10 examples (fast feedback during development)
- `debug` profile: 10 examples with verbose output

### Infrastructure Configuration

**jest.config.js**
```javascript
{
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/test', '<rootDir>/lib'],
  testMatch: ['**/*.test.ts', '**/__tests__/**/*.ts'],
  testTimeout: 30000,
}
```

## Test Structure

### Frontend Tests
```
packages/frontend/src/test/
├── setup.ts              # Vitest setup and fast-check configuration
├── strategies.ts         # Fast-check arbitraries for data generation
├── fixtures.ts           # Sample data for unit tests
├── utils.ts              # Test helper functions
├── example.test.ts       # Example tests demonstrating patterns
└── README.md             # Frontend testing guide
```

### Backend Tests
```
packages/backend/tests/
├── conftest.py           # Pytest configuration and fixtures
├── strategies.py         # Hypothesis strategies for data generation
├── utils.py              # Test helper functions
├── test_example.py       # Example tests demonstrating patterns
└── README.md             # Backend testing guide
```

### Infrastructure Tests
```
packages/infrastructure/test/
├── strategies.ts         # Fast-check arbitraries for CDK testing
├── utils.ts              # CDK test helper functions
└── README.md             # Infrastructure testing guide
```

## Running Tests

### Frontend
```bash
cd packages/frontend

# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run with coverage
npm test -- --coverage

# Run specific test file
npm test -- example.test.ts

# Run with UI
npm test -- --ui
```

### Backend
```bash
cd packages/backend

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run only unit tests
pytest -m "not property"

# Run only property-based tests
pytest -m property

# Run specific test file
pytest tests/test_example.py

# Use different Hypothesis profile
pytest --hypothesis-profile=dev
```

### Infrastructure
```bash
cd packages/infrastructure

# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run with coverage
npm test -- --coverage

# Run specific test file
npm test -- example.test.ts
```

### Run All Tests (from root)
```bash
# Run all tests across all packages
npm test
```

## Test Utilities and Strategies

### Frontend Strategies (fast-check)

Available arbitraries in `strategies.ts`:
- `salesRecordArbitrary()` - Generate valid sales records
- `salesDataListArbitrary()` - Generate lists of sales records
- `invalidSalesRecordArbitrary()` - Generate invalid sales records
- `festivalEventArbitrary()` - Generate festival events
- `userProfileArbitrary()` - Generate user profiles
- `forecastRequestArbitrary()` - Generate forecast requests
- `dailyPredictionArbitrary()` - Generate daily predictions
- `inventoryDataArbitrary()` - Generate inventory data

### Backend Strategies (Hypothesis)

Available strategies in `strategies.py`:
- `sales_record_strategy()` - Generate valid sales records
- `sales_data_list_strategy()` - Generate lists of sales records
- `invalid_sales_record_strategy()` - Generate invalid sales records
- `festival_event_strategy()` - Generate festival events
- `user_profile_strategy()` - Generate user profiles
- `questionnaire_response_strategy()` - Generate questionnaire responses
- `forecast_request_strategy()` - Generate forecast requests
- `inventory_data_strategy()` - Generate inventory data

### Infrastructure Strategies (fast-check)

Available arbitraries in `strategies.ts`:
- `awsResourceNameArbitrary()` - Generate valid AWS resource names
- `awsRegionArbitrary()` - Generate valid AWS region names
- `dynamoDbTableConfigArbitrary()` - Generate DynamoDB table configurations
- `s3BucketConfigArbitrary()` - Generate S3 bucket configurations
- `lambdaConfigArbitrary()` - Generate Lambda function configurations
- `apiGatewayConfigArbitrary()` - Generate API Gateway configurations
- `cognitoUserPoolConfigArbitrary()` - Generate Cognito User Pool configurations

## Test Fixtures

### Frontend Fixtures
- `sampleSalesData` - Sample sales records
- `sampleFestivalData` - Sample festival event
- `sampleUserProfile` - Sample user profile
- `sampleForecastRequest` - Sample forecast request
- `sampleDailyPredictions` - Sample daily predictions
- `sampleRiskAssessment` - Sample risk assessment

### Backend Fixtures
- `sample_sales_data` - Sample sales records
- `sample_festival_data` - Sample festival event
- `sample_user_profile` - Sample user profile

## Helper Functions

### Frontend Utilities
- `renderWithProviders()` - Render React components with providers
- `mockApiResponse()` - Mock API responses
- `mockApiError()` - Mock API errors
- `createMockFile()` - Create mock files for upload testing
- `createCsvContent()` - Format CSV data
- `isValidDateString()` - Validate date strings
- `isInRange()` - Check if value is in range
- `isValidConfidence()` - Validate confidence indicators (0-1)
- `isValidForecastHorizon()` - Validate forecast horizon (7-14 days)
- `hasRequiredFields()` - Check required fields in objects
- `percentageDifference()` - Calculate percentage difference
- `isInFestivalPeriod()` - Check if date is in festival period

### Backend Utilities
- `create_api_gateway_event()` - Create mock API Gateway events
- `create_lambda_context()` - Create mock Lambda contexts
- `create_csv_content()` - Create CSV content from data
- `create_sales_csv()` - Create CSV from sales records
- `is_valid_date_string()` - Validate ISO date strings
- `is_in_range()` - Check if value is in range
- `is_valid_confidence()` - Validate confidence indicators
- `is_valid_forecast_horizon()` - Validate forecast horizon
- `has_required_fields()` - Check required fields
- `calculate_percentage_difference()` - Calculate percentage difference
- `is_in_festival_period()` - Check if date is in festival period
- `generate_date_range()` - Generate date ranges
- `mock_s3_object()` - Create mock S3 objects
- `mock_dynamodb_item()` - Create mock DynamoDB items
- `assert_api_response()` - Assert API response format
- `assert_forecast_result_valid()` - Assert forecast result validity
- `assert_risk_assessment_valid()` - Assert risk assessment validity

### Infrastructure Utilities
- `createTestStack()` - Create test CDK stack
- `getTemplate()` - Get CloudFormation template from stack
- `assertResourceExists()` - Assert resource exists
- `assertResourceHasProperties()` - Assert resource properties
- `assertLambdaFunction()` - Assert Lambda configuration
- `assertDynamoDBTable()` - Assert DynamoDB table configuration
- `assertS3BucketEncrypted()` - Assert S3 encryption
- `assertApiGatewayThrottling()` - Assert API Gateway throttling
- `assertCognitoPasswordPolicy()` - Assert Cognito password policy
- `assertIAMRoleHasPolicies()` - Assert IAM role policies
- `assertResourceHasTags()` - Assert resource tags
- `isInRange()` - Check if value is in range
- `isValidAwsResourceName()` - Validate AWS resource names
- `isValidAwsRegion()` - Validate AWS regions

## Writing Tests

### Unit Test Example (Frontend)
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

### Property-Based Test Example (Frontend)
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

### Unit Test Example (Backend)
```python
def test_valid_sales_record(sample_sales_data):
    """Test that valid sales records pass validation."""
    for record in sample_sales_data:
        assert validate_sales_record(record)
```

### Property-Based Test Example (Backend)
```python
from hypothesis import given
from tests.strategies import sales_record_strategy

@pytest.mark.property
@given(record=sales_record_strategy())
def test_property_all_generated_records_are_valid(record):
    """
    Property test: All generated sales records should be valid.
    
    **Validates: Requirements 1.1, 1.5**
    """
    assert validate_sales_record(record)
    assert record["quantity"] > 0
```

## Best Practices

### General
1. **Document properties**: Include docstrings explaining what property is being tested
2. **Link to requirements**: Use `**Validates: Requirements X.Y**` format
3. **Use appropriate strategies/arbitraries**: Choose generators that match your input domain
4. **Test edge cases**: Write unit tests for specific edge cases
5. **Keep tests fast**: Limit iterations during development, increase for CI/CD

### Frontend-Specific
1. **Test user interactions**: Use `@testing-library/user-event` for user interactions
2. **Mock external dependencies**: Mock API calls and external services
3. **Use fixtures for unit tests**: Use fixtures for predictable test data
4. **Use arbitraries for property tests**: Use arbitraries for comprehensive coverage
5. **Test accessibility**: Ensure components are accessible

### Backend-Specific
1. **Mark property tests**: Use `@pytest.mark.property` for property-based tests
2. **Use appropriate Hypothesis profile**: Use `dev` profile during development
3. **Mock AWS services**: Use moto for AWS service mocking
4. **Test Lambda handlers**: Test complete Lambda handler functions
5. **Test error handling**: Verify error responses and recovery

### Infrastructure-Specific
1. **Test infrastructure as code**: Verify CDK constructs generate correct CloudFormation
2. **Test security**: Always verify encryption, IAM policies, and access controls
3. **Test scalability**: Verify auto-scaling and throttling configurations
4. **Use CDK assertions**: Leverage CDK's built-in assertion methods
5. **Test naming conventions**: Verify resource names follow conventions

## Test Coverage

### Coverage Reports

**Frontend**: Coverage reports are generated in `packages/frontend/coverage/`
- HTML report: `coverage/index.html`
- JSON report: `coverage/coverage-final.json`

**Backend**: Coverage reports are generated in `packages/backend/htmlcov/`
- HTML report: `htmlcov/index.html`
- XML report: `coverage.xml`

**Infrastructure**: Coverage reports are generated in `packages/infrastructure/coverage/`
- HTML report: `coverage/index.html`

### Coverage Goals
- Aim for >80% code coverage
- Focus on critical business logic
- Property-based tests provide broad coverage
- Unit tests provide specific edge case coverage

## Continuous Integration

### GitHub Actions (Recommended)
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      # Frontend tests
      - name: Install frontend dependencies
        run: npm ci
        working-directory: packages/frontend
      - name: Run frontend tests
        run: npm test -- --run --coverage
        working-directory: packages/frontend
      
      # Backend tests
      - name: Install backend dependencies
        run: pip install -r requirements.txt -r requirements-dev.txt
        working-directory: packages/backend
      - name: Run backend tests
        run: pytest --hypothesis-profile=ci
        working-directory: packages/backend
      
      # Infrastructure tests
      - name: Install infrastructure dependencies
        run: npm ci
        working-directory: packages/infrastructure
      - name: Run infrastructure tests
        run: npm test
        working-directory: packages/infrastructure
```

## Property-Based Testing Strategy

### Minimum Iterations
As per the design specification, all property-based tests must run with a minimum of 100 iterations to ensure comprehensive input coverage.

### Test Categories
1. **Data Validation Properties**: Verify input validation across all possible inputs
2. **Business Logic Properties**: Verify core business rules hold universally
3. **Transformation Properties**: Verify data transformations preserve invariants
4. **API Contract Properties**: Verify API responses match expected schemas
5. **Infrastructure Properties**: Verify CDK constructs generate valid CloudFormation

### Property Test Naming Convention
- Use descriptive names starting with "property:"
- Include the requirement being validated in docstring
- Example: `property: all generated sales records should be valid`

## Troubleshooting

### Frontend Tests Failing
- Ensure all dependencies are installed: `npm install`
- Check that jsdom is properly configured in vite.config.ts
- Verify setup.ts is being loaded correctly

### Backend Tests Failing
- Ensure virtual environment is activated
- Install all dependencies: `pip install -r requirements.txt -r requirements-dev.txt`
- Check Hypothesis profile is loaded correctly

### Infrastructure Tests Failing
- Ensure CDK dependencies are installed: `npm install`
- Verify jest.config.js is properly configured
- Check that ts-jest is transforming TypeScript correctly

### Property Tests Taking Too Long
- Use `dev` profile during development (10 examples)
- Increase iterations for CI/CD (`ci` profile with 200 examples)
- Optimize strategies to generate valid data more efficiently

## Resources

### Documentation
- [Vitest Documentation](https://vitest.dev/)
- [fast-check Documentation](https://fast-check.dev/)
- [pytest Documentation](https://docs.pytest.org/)
- [Hypothesis Documentation](https://hypothesis.readthedocs.io/)
- [Jest Documentation](https://jestjs.io/)
- [Testing Library Documentation](https://testing-library.com/)
- [CDK Assertions Documentation](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.assertions-readme.html)

### Additional Reading
- [Property-Based Testing with fast-check](https://fast-check.dev/docs/introduction/)
- [Property-Based Testing with Hypothesis](https://hypothesis.works/articles/what-is-property-based-testing/)
- [Testing React Components](https://testing-library.com/docs/react-testing-library/intro/)
- [Testing AWS CDK Applications](https://docs.aws.amazon.com/cdk/v2/guide/testing.html)

## Summary

The VyaparSaathi testing framework is fully configured with:
- ✅ Vitest for frontend unit and property-based tests
- ✅ fast-check for TypeScript property-based testing (frontend & infrastructure)
- ✅ pytest for backend unit and property-based tests
- ✅ Hypothesis for Python property-based testing
- ✅ Jest for infrastructure unit tests
- ✅ Comprehensive test utilities and strategies
- ✅ Example tests demonstrating patterns
- ✅ Coverage reporting for all packages
- ✅ Minimum 100 iterations for property-based tests (as per spec)

All testing frameworks are ready for use in implementing the 16 correctness properties defined in the design document.
