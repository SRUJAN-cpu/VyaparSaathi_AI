/**
 * Test utilities for VyaparSaathi infrastructure tests.
 * 
 * This module provides helper functions for testing CDK constructs.
 */

import { Stack, App } from 'aws-cdk-lib';
import { Template } from 'aws-cdk-lib/assertions';

/**
 * Create a test stack for CDK construct testing.
 * 
 * @param stackName - Optional stack name
 * @returns Stack instance
 */
export function createTestStack(stackName = 'TestStack'): Stack {
  const app = new App();
  return new Stack(app, stackName, {
    env: {
      account: '123456789012',
      region: 'us-east-1',
    },
  });
}

/**
 * Get CloudFormation template from a stack.
 * 
 * @param stack - CDK Stack
 * @returns Template for assertions
 */
export function getTemplate(stack: Stack): Template {
  return Template.fromStack(stack);
}

/**
 * Assert that a resource exists in the template.
 * 
 * @param template - CloudFormation template
 * @param resourceType - AWS resource type (e.g., 'AWS::Lambda::Function')
 * @param count - Expected count (default: at least 1)
 */
export function assertResourceExists(
  template: Template,
  resourceType: string,
  count?: number
): void {
  if (count !== undefined) {
    template.resourceCountIs(resourceType, count);
  } else {
    template.resourceCountIs(resourceType, 1);
  }
}

/**
 * Assert that a resource has specific properties.
 * 
 * @param template - CloudFormation template
 * @param resourceType - AWS resource type
 * @param properties - Expected properties
 */
export function assertResourceHasProperties(
  template: Template,
  resourceType: string,
  properties: Record<string, any>
): void {
  template.hasResourceProperties(resourceType, properties);
}

/**
 * Get all resources of a specific type from template.
 * 
 * @param template - CloudFormation template
 * @param resourceType - AWS resource type
 * @returns Array of resources
 */
export function getResourcesByType(
  template: Template,
  resourceType: string
): any[] {
  const resources = template.findResources(resourceType);
  return Object.values(resources);
}

/**
 * Assert Lambda function has correct configuration.
 * 
 * @param template - CloudFormation template
 * @param functionName - Function name pattern
 * @param runtime - Expected runtime
 * @param timeout - Expected timeout
 * @param memorySize - Expected memory size
 */
export function assertLambdaFunction(
  template: Template,
  functionName: string,
  runtime?: string,
  timeout?: number,
  memorySize?: number
): void {
  const properties: Record<string, any> = {};
  
  if (runtime) properties.Runtime = runtime;
  if (timeout) properties.Timeout = timeout;
  if (memorySize) properties.MemorySize = memorySize;
  
  template.hasResourceProperties('AWS::Lambda::Function', properties);
}

/**
 * Assert DynamoDB table has correct configuration.
 * 
 * @param template - CloudFormation template
 * @param tableName - Table name pattern
 * @param partitionKey - Partition key name
 * @param sortKey - Optional sort key name
 */
export function assertDynamoDBTable(
  template: Template,
  tableName: string,
  partitionKey: string,
  sortKey?: string
): void {
  const keySchema: any[] = [
    {
      AttributeName: partitionKey,
      KeyType: 'HASH',
    },
  ];
  
  if (sortKey) {
    keySchema.push({
      AttributeName: sortKey,
      KeyType: 'RANGE',
    });
  }
  
  template.hasResourceProperties('AWS::DynamoDB::Table', {
    KeySchema: keySchema,
  });
}

/**
 * Assert S3 bucket has encryption enabled.
 * 
 * @param template - CloudFormation template
 */
export function assertS3BucketEncrypted(template: Template): void {
  template.hasResourceProperties('AWS::S3::Bucket', {
    BucketEncryption: {
      ServerSideEncryptionConfiguration: [
        {
          ServerSideEncryptionByDefault: {
            SSEAlgorithm: 'AES256',
          },
        },
      ],
    },
  });
}

/**
 * Assert API Gateway has throttling configured.
 * 
 * @param template - CloudFormation template
 * @param rateLimit - Expected rate limit
 * @param burstLimit - Expected burst limit
 */
export function assertApiGatewayThrottling(
  template: Template,
  rateLimit?: number,
  burstLimit?: number
): void {
  const properties: Record<string, any> = {};
  
  if (rateLimit !== undefined) properties.RateLimit = rateLimit;
  if (burstLimit !== undefined) properties.BurstLimit = burstLimit;
  
  if (Object.keys(properties).length > 0) {
    template.hasResourceProperties('AWS::ApiGateway::UsagePlan', properties);
  }
}

/**
 * Assert Cognito User Pool has password policy.
 * 
 * @param template - CloudFormation template
 * @param minLength - Minimum password length
 */
export function assertCognitoPasswordPolicy(
  template: Template,
  minLength: number
): void {
  template.hasResourceProperties('AWS::Cognito::UserPool', {
    Policies: {
      PasswordPolicy: {
        MinimumLength: minLength,
      },
    },
  });
}

/**
 * Assert IAM role has specific managed policies.
 * 
 * @param template - CloudFormation template
 * @param policyArns - Array of policy ARNs
 */
export function assertIAMRoleHasPolicies(
  template: Template,
  policyArns: string[]
): void {
  for (const arn of policyArns) {
    template.hasResourceProperties('AWS::IAM::Role', {
      ManagedPolicyArns: expect.arrayContaining([
        expect.objectContaining({
          'Fn::Join': expect.arrayContaining([
            expect.arrayContaining([expect.stringContaining(arn)]),
          ]),
        }),
      ]),
    });
  }
}

/**
 * Assert resource has specific tags.
 * 
 * @param template - CloudFormation template
 * @param resourceType - AWS resource type
 * @param tags - Expected tags
 */
export function assertResourceHasTags(
  template: Template,
  resourceType: string,
  tags: Record<string, string>
): void {
  const tagArray = Object.entries(tags).map(([key, value]) => ({
    Key: key,
    Value: value,
  }));
  
  template.hasResourceProperties(resourceType, {
    Tags: expect.arrayContaining(tagArray),
  });
}

/**
 * Validate that all Lambda functions have proper error handling.
 * 
 * @param template - CloudFormation template
 */
export function assertLambdaErrorHandling(template: Template): void {
  const functions = getResourcesByType(template, 'AWS::Lambda::Function');
  
  for (const func of functions) {
    // Check for dead letter queue or destination configuration
    const hasErrorHandling =
      func.Properties?.DeadLetterConfig ||
      func.Properties?.EventInvokeConfig?.DestinationConfig;
    
    expect(hasErrorHandling).toBeTruthy();
  }
}

/**
 * Validate that all resources follow naming conventions.
 * 
 * @param template - CloudFormation template
 * @param prefix - Expected resource name prefix
 */
export function assertNamingConvention(
  template: Template,
  prefix: string
): void {
  const allResources = template.toJSON().Resources;
  
  for (const [logicalId, resource] of Object.entries(allResources)) {
    // Check if resource has a Name property
    const name = (resource as any).Properties?.Name;
    if (name && typeof name === 'string') {
      expect(name).toMatch(new RegExp(`^${prefix}`));
    }
  }
}

/**
 * Helper to check if a value is within a range.
 * 
 * @param value - Value to check
 * @param min - Minimum value
 * @param max - Maximum value
 */
export function isInRange(value: number, min: number, max: number): boolean {
  return value >= min && value <= max;
}

/**
 * Helper to validate AWS resource name format.
 * 
 * @param name - Resource name
 */
export function isValidAwsResourceName(name: string): boolean {
  return /^[a-z][a-z0-9-]{2,62}[a-z0-9]$/.test(name);
}

/**
 * Helper to validate AWS region format.
 * 
 * @param region - Region name
 */
export function isValidAwsRegion(region: string): boolean {
  const validRegions = [
    'us-east-1',
    'us-east-2',
    'us-west-1',
    'us-west-2',
    'eu-west-1',
    'eu-west-2',
    'eu-central-1',
    'ap-south-1',
    'ap-southeast-1',
    'ap-southeast-2',
    'ap-northeast-1',
    'ap-northeast-2',
  ];
  return validRegions.includes(region);
}
