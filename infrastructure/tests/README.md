# VyaparSaathi Access Control Property Tests

This directory contains property-based tests for the VyaparSaathi access control system.

## Overview

The access control property test validates **Property 14: Access Control** from the design document, which states:

> "For any data access request, the system should prevent unauthorized access to user data and forecasting results"

This validates **Requirements 7.4**: "THE VyaparSaathi SHALL implement access controls to prevent unauthorized data access"

## Test Coverage

The property-based test validates the following access control properties:

1. **Unauthorized requests rejected**: Requests without authentication tokens are rejected with 401 status
2. **Expired tokens rejected**: Requests with expired JWT tokens are rejected with 401 status
3. **Invalid tokens rejected**: Requests with invalid JWT signatures are rejected with 401 status
4. **Users access own data only**: Users can only access resources that belong to them
5. **Valid tokens grant access**: Valid tokens grant access to the user's own resources
6. **Consistent across resource types**: Access control rules apply consistently across all resource types
7. **Cross-user access denied**: Users cannot access other users' data under any circumstances

## Running the Tests

### Prerequisites

1. Install Python 3.11 or higher
2. Install test dependencies:

```bash
cd infrastructure/tests
pip install -r requirements.txt
```

### Run All Tests

```bash
# Run all property tests with verbose output
pytest test_access_control_property.py -v

# Run with coverage report
pytest test_access_control_property.py --cov=. --cov-report=html

# Run specific test
pytest test_access_control_property.py::test_property_unauthorized_requests_rejected -v
```

### Run with Hypothesis Statistics

```bash
# Show detailed Hypothesis statistics
pytest test_access_control_property.py -v --hypothesis-show-statistics
```

## Test Configuration

The property tests use Hypothesis with the following configuration:

- **Max examples**: 100 iterations per property test
- **JWT secret**: Test secret key (production uses Cognito-managed keys)
- **Token expiration**: 1 hour for valid tokens
- **User ID range**: 1-1000 for test user generation

## Architecture

The test implements a mock access control system that simulates the production architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                    Property Test Suite                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │         AccessControlValidator                       │   │
│  │  - validate_token()                                  │   │
│  │  - check_resource_access()                           │   │
│  │  - authorize_request()                               │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                   │
│                          ▼                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │         MockDynamoDBService                          │   │
│  │  - UserProfiles table                                │   │
│  │  - Forecasts table                                   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

This mirrors the production architecture where:
- API Gateway uses Cognito Authorizer for JWT validation
- Lambda functions check resource ownership before data access
- DynamoDB stores user data with userId as partition key

## Property Test Strategies

The test uses Hypothesis strategies to generate test data:

- **user_id_strategy**: Generates valid user IDs (user-1 to user-1000)
- **jwt_token_strategy**: Generates JWT tokens with various validity states
- **data_access_request_strategy**: Generates data access requests for different resource types

## Integration with Production

This test validates the access control logic that should be implemented in:

1. **API Gateway Cognito Authorizer**: Validates JWT tokens from Cognito User Pool
2. **Lambda Authorizer Functions**: Additional authorization logic for resource-level access
3. **Lambda Function Code**: Resource ownership checks before data operations
4. **DynamoDB Access Patterns**: Partition key design that enforces user isolation

## Expected Results

All property tests should pass, confirming that:

- ✅ Unauthorized requests are always rejected
- ✅ Invalid/expired tokens are always rejected
- ✅ Users can access their own resources
- ✅ Cross-user data access is always prevented
- ✅ Access control is consistent across all resource types

## Troubleshooting

### Test Failures

If tests fail, check:

1. **JWT token generation**: Ensure tokens are properly signed and not expired
2. **Resource ID format**: Resource IDs should follow the pattern `userId#resourceIdentifier`
3. **User ID matching**: Access is granted only when token user_id matches resource owner

### Performance

Property tests run 100 examples per test by default. To run faster during development:

```bash
# Run with fewer examples
pytest test_access_control_property.py -v --hypothesis-max-examples=10
```

## Next Steps

After validating the property tests:

1. Implement the access control logic in Lambda functions
2. Configure API Gateway Cognito Authorizer
3. Add resource-level authorization checks in Lambda code
4. Test with real Cognito tokens in integration tests
5. Deploy and validate in AWS environment

## References

- Design Document: `.kiro/specs/vyapar-saathi/design.md` (Property 14)
- Requirements Document: `.kiro/specs/vyapar-saathi/requirements.md` (Requirement 7.4)
- CDK Stack: `infrastructure/lib/vyapar-saathi-stack.ts` (Cognito and API Gateway setup)
