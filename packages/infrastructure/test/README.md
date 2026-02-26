# VyaparSaathi Infrastructure Testing Guide

This directory contains tests for the VyaparSaathi AWS CDK infrastructure.

## Test Structure

- `strategies.ts` - Fast-check arbitraries for property-based testing
- `utils.ts` - Test utilities and helper functions
- `*.test.ts` - Test files (unit and property-based tests)

## Running Tests

### Run all tests
```bash
cd packages/infrastructure
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

## Writing Tests

### Unit Tests

Unit tests verify specific CDK construct configurations:

```typescript
import { createTestStack, getTemplate, assertResourceExists } from './utils';
import { MyStack } from '../lib/my-stack';

describe('MyStack', () => {
  it('should create Lambda function', () => {
    const stack = createTestStack();
    new MyStack(stack, 'MyStack');
    
    const template = getTemplate(stack);
    assertResourceExists(template, 'AWS::Lambda::Function', 1);
  });
});
```

### Property-Based Tests

Property-based tests verify infrastructure properties across many configurations:

```typescript
import * as fc from 'fast-check';
import { lambdaConfigArbitrary } from './strategies';
import { createTestStack, getTemplate } from './utils';

describe('Lambda Configuration', () => {
  it('property: all Lambda functions should have valid configuration', () => {
    /**
     * Property test: All Lambda configurations should be valid.
     * 
     * **Validates: Requirements 6.1, 6.3**
     */
    fc.assert(
      fc.property(lambdaConfigArbitrary(), (config) => {
        const stack = createTestStack();
        // Create Lambda with config
        // Assert valid configuration
        expect(config.memorySize).toBeGreaterThanOrEqual(128);
        expect(config.timeout).toBeLessThanOrEqual(900);
      }),
      { numRuns: 100 }
    );
  });
});
```

## Fast-check Configuration

Fast-check is configured with:
- `numRuns: 100` - Number of test cases to generate (minimum as per spec)
- Increase for more thorough testing or decrease for faster feedback

## Custom Arbitraries

The `strategies.ts` module provides custom fast-check arbitraries:

- `awsResourceNameArbitrary()` - Generate valid AWS resource names
- `awsRegionArbitrary()` - Generate valid AWS region names
- `dynamoDbTableConfigArbitrary()` - Generate DynamoDB table configurations
- `s3BucketConfigArbitrary()` - Generate S3 bucket configurations
- `lambdaConfigArbitrary()` - Generate Lambda function configurations
- `apiGatewayConfigArbitrary()` - Generate API Gateway configurations
- `cognitoUserPoolConfigArbitrary()` - Generate Cognito User Pool configurations

## Test Utilities

The `utils.ts` module provides helper functions:

### Stack Creation
- `createTestStack()` - Create a test stack
- `getTemplate()` - Get CloudFormation template from stack

### Assertions
- `assertResourceExists()` - Assert resource exists in template
- `assertResourceHasProperties()` - Assert resource has specific properties
- `assertLambdaFunction()` - Assert Lambda function configuration
- `assertDynamoDBTable()` - Assert DynamoDB table configuration
- `assertS3BucketEncrypted()` - Assert S3 bucket encryption
- `assertApiGatewayThrottling()` - Assert API Gateway throttling
- `assertCognitoPasswordPolicy()` - Assert Cognito password policy
- `assertIAMRoleHasPolicies()` - Assert IAM role policies
- `assertResourceHasTags()` - Assert resource tags

### Validation
- `isInRange()` - Check if value is in range
- `isValidAwsResourceName()` - Validate AWS resource name format
- `isValidAwsRegion()` - Validate AWS region format

## Testing CDK Constructs

### Testing Stack Creation
```typescript
import { createTestStack, getTemplate } from './utils';
import { VyaparSaathiStack } from '../lib/vyapar-saathi-stack';

describe('VyaparSaathiStack', () => {
  it('should create all required resources', () => {
    const stack = createTestStack();
    new VyaparSaathiStack(stack, 'VyaparSaathiStack');
    
    const template = getTemplate(stack);
    
    // Assert Lambda functions
    assertResourceExists(template, 'AWS::Lambda::Function', 5);
    
    // Assert DynamoDB tables
    assertResourceExists(template, 'AWS::DynamoDB::Table', 3);
    
    // Assert S3 buckets
    assertResourceExists(template, 'AWS::S3::Bucket', 2);
  });
});
```

### Testing Resource Properties
```typescript
import { getTemplate, assertResourceHasProperties } from './utils';

it('should configure Lambda with correct timeout', () => {
  const stack = createTestStack();
  // Create your stack
  
  const template = getTemplate(stack);
  assertResourceHasProperties(template, 'AWS::Lambda::Function', {
    Timeout: 30,
    MemorySize: 512,
  });
});
```

### Testing Security Configuration
```typescript
import { getTemplate, assertS3BucketEncrypted } from './utils';

it('should enable encryption on S3 buckets', () => {
  const stack = createTestStack();
  // Create your stack
  
  const template = getTemplate(stack);
  assertS3BucketEncrypted(template);
});
```

## Best Practices

1. **Test infrastructure as code**: Verify CDK constructs generate correct CloudFormation
2. **Use property-based tests**: Test infrastructure properties across many configurations
3. **Document properties**: Include docstrings explaining what property is being tested
4. **Link to requirements**: Use `**Validates: Requirements X.Y**` format
5. **Test security**: Always verify encryption, IAM policies, and access controls
6. **Test scalability**: Verify auto-scaling and throttling configurations
7. **Use utilities**: Leverage test utilities for common assertions
8. **Keep tests fast**: Mock external dependencies and avoid actual AWS calls
9. **Test naming conventions**: Verify resource names follow conventions
10. **Test tags**: Verify all resources have required tags

## CDK Assertions

The CDK provides powerful assertion methods:

```typescript
import { Template, Match } from 'aws-cdk-lib/assertions';

const template = Template.fromStack(stack);

// Exact match
template.hasResourceProperties('AWS::Lambda::Function', {
  Runtime: 'nodejs18.x',
});

// Partial match
template.hasResourceProperties('AWS::Lambda::Function', {
  Runtime: Match.stringLikeRegexp('nodejs.*'),
});

// Array contains
template.hasResourceProperties('AWS::IAM::Role', {
  ManagedPolicyArns: Match.arrayWith([
    Match.stringLikeRegexp('.*AWSLambdaBasicExecutionRole.*'),
  ]),
});

// Object contains
template.hasResourceProperties('AWS::Lambda::Function', {
  Environment: Match.objectLike({
    Variables: Match.objectLike({
      TABLE_NAME: Match.anyValue(),
    }),
  }),
});
```

## Debugging Tests

### View generated CloudFormation
```typescript
const template = getTemplate(stack);
console.log(JSON.stringify(template.toJSON(), null, 2));
```

### View specific resources
```typescript
const resources = template.findResources('AWS::Lambda::Function');
console.log(JSON.stringify(resources, null, 2));
```

### Enable verbose output
```bash
npm test -- --verbose
```
