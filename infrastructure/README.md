# VyaparSaathi Infrastructure

AWS CDK infrastructure for the VyaparSaathi festival demand and inventory risk forecasting platform.

## Architecture Overview

This CDK stack deploys the following AWS resources:

### DynamoDB Tables
- **UserProfiles**: Stores user business information and preferences
  - Partition Key: `userId`
  - GSI: `LocationIndex` (region, city)
  - Billing: On-demand
  
- **Forecasts**: Stores demand forecast results
  - Partition Key: `userId`, Sort Key: `sku`
  - GSI: `DateIndex` (userId, forecastDate)
  - TTL: Enabled (30 days)
  - Billing: On-demand
  
- **FestivalCalendar**: Stores festival event data
  - Partition Key: `festivalId`
  - GSI: `RegionIndex` (region, date)
  - GSI: `DateIndex` (date)
  - Billing: On-demand

### S3 Buckets
- **Raw Data Bucket**: Stores uploaded CSV files
  - Encryption: SSE-S3
  - Lifecycle: Glacier after 90 days, delete after 365 days
  - CORS: Enabled for frontend uploads
  
- **Processed Data Bucket**: Stores processed sales data
  - Encryption: SSE-S3
  - Lifecycle: Glacier after 90 days, delete after 365 days

### API Gateway
- **REST API**: Main API endpoint
  - Rate Limiting: 100 requests/minute per user
  - Request Validation: Enabled
  - CloudWatch Logging: Enabled
  - CORS: Enabled
  
- **Endpoints**:
  - `POST /data/upload` - Upload sales data
  - `POST /forecast` - Generate demand forecasts
  - `POST /risk` - Calculate inventory risks
  - `POST /explanation` - Get AI explanations

### Lambda Functions
- **DataUploadFunction**: Handles CSV uploads and validation
- **ForecastFunction**: Generates demand forecasts
- **RiskAssessmentFunction**: Calculates inventory risks
- **ExplanationFunction**: Generates AI explanations using Bedrock

### Amazon Cognito
- **User Pool**: User authentication and management
  - Sign-in: Email/password
  - Password Policy: 8+ chars, complexity requirements
  - Social Providers: Google, Facebook (requires configuration)
  - MFA: Optional
  
- **User Pool Client**: Web/mobile app client
  - OAuth Flows: Authorization code, implicit
  - Scopes: email, openid, profile

## Prerequisites

1. **AWS Account**: Active AWS account with appropriate permissions
2. **AWS CLI**: Installed and configured with credentials
3. **Node.js**: Version 18.x or later
4. **AWS CDK**: Version 2.100.0 or later

## Installation

1. Install dependencies:
```bash
cd infrastructure
npm install
```

2. Configure AWS credentials:
```bash
aws configure
# Enter your AWS Access Key ID, Secret Access Key, and default region
```

3. Bootstrap CDK (first time only):
```bash
npx cdk bootstrap aws://ACCOUNT-ID/REGION
```

## Deployment

### 1. Synthesize CloudFormation Template

Preview the CloudFormation template that will be generated:

```bash
npm run synth
```

This creates a `cdk.out` directory with the CloudFormation template.

### 2. Deploy the Stack

Deploy all resources to AWS:

```bash
npm run deploy
```

Or use CDK directly:

```bash
npx cdk deploy
```

The deployment will:
- Create all DynamoDB tables
- Create S3 buckets with lifecycle policies
- Deploy Lambda functions
- Create API Gateway with endpoints
- Set up Cognito user pool and client
- Configure IAM roles and permissions

### 3. Verify Deployment

After deployment, CDK will output important values:

```
Outputs:
VyaparSaathiStack.ApiEndpoint = https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/prod/
VyaparSaathiStack.UserPoolId = us-east-1_xxxxxxxxx
VyaparSaathiStack.UserPoolClientId = xxxxxxxxxxxxxxxxxxxxxxxxxx
VyaparSaathiStack.UserProfileTableName = VyaparSaathi-UserProfiles
VyaparSaathiStack.ForecastsTableName = VyaparSaathi-Forecasts
VyaparSaathiStack.FestivalCalendarTableName = VyaparSaathi-FestivalCalendar
VyaparSaathiStack.RawDataBucketName = vyapar-saathi-raw-data-ACCOUNT-ID
VyaparSaathiStack.ProcessedDataBucketName = vyapar-saathi-processed-data-ACCOUNT-ID
```

Save these values for frontend configuration.

## Configuration

### Social Identity Providers

To enable Google and Facebook login, update the placeholder credentials in `lib/vyapar-saathi-stack.ts`:

1. **Google OAuth**:
   - Create OAuth credentials in Google Cloud Console
   - Replace `GOOGLE_CLIENT_ID_PLACEHOLDER` and `GOOGLE_CLIENT_SECRET_PLACEHOLDER`

2. **Facebook Login**:
   - Create a Facebook App in Facebook Developers
   - Replace `FACEBOOK_APP_ID_PLACEHOLDER` and `FACEBOOK_APP_SECRET_PLACEHOLDER`

After updating, redeploy:
```bash
npm run deploy
```

### CORS Configuration

For production, update CORS settings to restrict origins:

In `lib/vyapar-saathi-stack.ts`, change:
```typescript
allowOrigins: apigateway.Cors.ALL_ORIGINS
```

To:
```typescript
allowOrigins: ['https://your-frontend-domain.com']
```

## Useful CDK Commands

- `npm run build` - Compile TypeScript to JavaScript
- `npm run watch` - Watch for changes and compile
- `npm run synth` - Synthesize CloudFormation template
- `npm run deploy` - Deploy stack to AWS
- `npx cdk diff` - Compare deployed stack with current state
- `npx cdk destroy` - Remove all resources (use with caution)

## Cost Optimization

The infrastructure is designed for cost efficiency:

1. **DynamoDB**: On-demand billing (pay per request)
2. **S3**: Lifecycle policies move old data to Glacier
3. **Lambda**: Pay per invocation
4. **API Gateway**: Pay per request
5. **Cognito**: Free tier covers up to 50,000 MAUs

Estimated monthly cost for low-medium usage: $20-50

## Security Features

- All data encrypted at rest (DynamoDB, S3)
- All data encrypted in transit (HTTPS)
- S3 buckets block public access
- IAM roles follow least-privilege principle
- API Gateway rate limiting prevents abuse
- Cognito password policies enforce strong passwords
- Request validation prevents malformed inputs

## Monitoring

CloudWatch logs are automatically configured for:
- API Gateway requests
- Lambda function executions
- DynamoDB operations

Access logs in AWS Console:
1. Go to CloudWatch
2. Navigate to Log Groups
3. Find `/aws/apigateway/vyapar-saathi` and Lambda log groups

## Troubleshooting

### Deployment Fails

1. Check AWS credentials:
```bash
aws sts get-caller-identity
```

2. Verify CDK bootstrap:
```bash
npx cdk bootstrap
```

3. Check for resource limits in your AWS account

### Stack Update Fails

If a stack update fails, you may need to manually fix resources or rollback:
```bash
npx cdk deploy --rollback
```

### Delete Stack

To remove all resources:
```bash
npx cdk destroy
```

Note: DynamoDB tables and S3 buckets have `RETAIN` policy and won't be deleted automatically.

## Next Steps

After deploying infrastructure:

1. Implement Lambda function code (currently placeholders)
2. Populate FestivalCalendar table with festival data
3. Configure social identity providers
4. Set up frontend application with Cognito integration
5. Test API endpoints
6. Configure custom domain for API Gateway
7. Set up CloudWatch alarms for monitoring

## Support

For issues or questions, refer to:
- AWS CDK Documentation: https://docs.aws.amazon.com/cdk/
- VyaparSaathi Design Document: `.kiro/specs/vyapar-saathi/design.md`
- VyaparSaathi Requirements: `.kiro/specs/vyapar-saathi/requirements.md`
