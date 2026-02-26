/**
 * Fast-check strategies for generating test data for VyaparSaathi infrastructure tests.
 * 
 * This module provides custom arbitraries for property-based testing of CDK constructs.
 */

import * as fc from 'fast-check';

/**
 * Generate valid AWS resource names (alphanumeric with hyphens).
 */
export const awsResourceNameArbitrary = (): fc.Arbitrary<string> => {
  return fc.stringMatching(/^[a-z][a-z0-9-]{2,62}[a-z0-9]$/);
};

/**
 * Generate valid AWS region names.
 */
export const awsRegionArbitrary = (): fc.Arbitrary<string> => {
  return fc.constantFrom(
    'us-east-1',
    'us-east-2',
    'us-west-1',
    'us-west-2',
    'eu-west-1',
    'eu-central-1',
    'ap-south-1',
    'ap-southeast-1',
    'ap-northeast-1'
  );
};

/**
 * Generate valid DynamoDB table configuration.
 */
export const dynamoDbTableConfigArbitrary = () => {
  return fc.record({
    tableName: awsResourceNameArbitrary(),
    partitionKey: fc.string({ minLength: 1, maxLength: 255 }),
    sortKey: fc.option(fc.string({ minLength: 1, maxLength: 255 })),
    billingMode: fc.constantFrom('PAY_PER_REQUEST', 'PROVISIONED'),
    ttlAttribute: fc.option(fc.string({ minLength: 1, maxLength: 255 })),
  });
};

/**
 * Generate valid S3 bucket configuration.
 */
export const s3BucketConfigArbitrary = () => {
  return fc.record({
    bucketName: awsResourceNameArbitrary(),
    encryption: fc.constantFrom('AES256', 'aws:kms'),
    versioning: fc.boolean(),
    lifecycleRules: fc.array(
      fc.record({
        id: fc.string({ minLength: 1, maxLength: 255 }),
        enabled: fc.boolean(),
        expirationDays: fc.integer({ min: 1, max: 3650 }),
        transitionDays: fc.option(fc.integer({ min: 1, max: 365 })),
      }),
      { maxLength: 5 }
    ),
  });
};

/**
 * Generate valid Lambda function configuration.
 */
export const lambdaConfigArbitrary = () => {
  return fc.record({
    functionName: awsResourceNameArbitrary(),
    runtime: fc.constantFrom('nodejs18.x', 'python3.11'),
    memorySize: fc.constantFrom(128, 256, 512, 1024, 2048, 3008),
    timeout: fc.integer({ min: 3, max: 900 }),
    environment: fc.dictionary(
      fc.string({ minLength: 1, maxLength: 50 }),
      fc.string({ maxLength: 4096 })
    ),
  });
};

/**
 * Generate valid API Gateway configuration.
 */
export const apiGatewayConfigArbitrary = () => {
  return fc.record({
    apiName: awsResourceNameArbitrary(),
    throttleRateLimit: fc.integer({ min: 1, max: 10000 }),
    throttleBurstLimit: fc.integer({ min: 1, max: 5000 }),
    corsEnabled: fc.boolean(),
    authorizationType: fc.constantFrom('NONE', 'AWS_IAM', 'COGNITO_USER_POOLS'),
  });
};

/**
 * Generate valid Cognito User Pool configuration.
 */
export const cognitoUserPoolConfigArbitrary = () => {
  return fc.record({
    userPoolName: awsResourceNameArbitrary(),
    passwordMinLength: fc.integer({ min: 6, max: 99 }),
    requireUppercase: fc.boolean(),
    requireLowercase: fc.boolean(),
    requireNumbers: fc.boolean(),
    requireSymbols: fc.boolean(),
    mfaConfiguration: fc.constantFrom('OFF', 'OPTIONAL', 'REQUIRED'),
  });
};
