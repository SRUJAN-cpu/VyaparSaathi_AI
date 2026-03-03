# VyaparSaathi Infrastructure Deployment Guide

This guide provides step-by-step instructions for deploying the VyaparSaathi AWS infrastructure using CDK.

## Prerequisites Checklist

Before deploying, ensure you have:

- [ ] AWS Account with administrator access
- [ ] AWS CLI installed (version 2.x)
- [ ] Node.js installed (version 18.x or later)
- [ ] npm or yarn package manager
- [ ] AWS credentials configured locally

## Step 1: Configure AWS Credentials

### Option A: Using AWS CLI Configure

```bash
aws configure
```

Enter when prompted:
- AWS Access Key ID
- AWS Secret Access Key
- Default region (e.g., `us-east-1`)
- Default output format (e.g., `json`)

### Option B: Using Environment Variables

```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"
```

### Verify Configuration

```bash
aws sts get-caller-identity
```

Expected output:
```json
{
    "UserId": "AIDAXXXXXXXXXXXXXXXXX",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/your-username"
}
```

## Step 2: Install Dependencies

Navigate to the infrastructure directory and install packages:

```bash
cd infrastructure
npm install
```

This installs:
- AWS CDK CLI tools
- AWS CDK libraries
- TypeScript compiler
- Required dependencies

## Step 3: Bootstrap CDK (First Time Only)

CDK requires a bootstrap stack in your AWS account to manage deployment assets.

```bash
npx cdk bootstrap aws://ACCOUNT-ID/REGION
```

Replace:
- `ACCOUNT-ID` with your AWS account ID (from Step 1)
- `REGION` with your target region (e.g., `us-east-1`)

Example:
```bash
npx cdk bootstrap aws://123456789012/us-east-1
```

This creates:
- S3 bucket for CDK assets
- IAM roles for deployments
- CloudFormation stack named `CDKToolkit`

## Step 4: Review Infrastructure

### Synthesize CloudFormation Template

Generate the CloudFormation template without deploying:

```bash
npm run synth
```

This creates a `cdk.out` directory containing:
- CloudFormation template (JSON)
- Asset manifests
- Tree metadata

### Review Resources

Check what will be created:

```bash
npx cdk diff
```

Expected resources:
- 3 DynamoDB tables
- 2 S3 buckets
- 1 API Gateway REST API
- 4 Lambda functions
- 1 Cognito User Pool
- IAM roles and policies
- CloudWatch log groups

## Step 5: Deploy Infrastructure

### Deploy All Resources

```bash
npm run deploy
```

Or with CDK directly:

```bash
npx cdk deploy
```

### Deployment Process

The deployment will:
1. Package Lambda functions
2. Upload assets to S3
3. Create CloudFormation stack
4. Provision all resources
5. Configure permissions

This typically takes 5-10 minutes.

### Confirm Deployment

CDK will ask for confirmation before creating resources:

```
Do you wish to deploy these changes (y/n)?
```

Type `y` and press Enter.

### Monitor Progress

Watch the deployment progress in the terminal. You'll see:
- Resource creation events
- Status updates
- Any errors or warnings

## Step 6: Save Outputs

After successful deployment, CDK outputs important values:

```
Outputs:
VyaparSaathiStack.ApiEndpoint = https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod/
VyaparSaathiStack.UserPoolId = us-east-1_AbCdEfGhI
VyaparSaathiStack.UserPoolClientId = 1a2b3c4d5e6f7g8h9i0j
VyaparSaathiStack.UserPoolDomain = vyapar-saathi-123456789012
VyaparSaathiStack.UserProfileTableName = VyaparSaathi-UserProfiles
VyaparSaathiStack.ForecastsTableName = VyaparSaathi-Forecasts
VyaparSaathiStack.FestivalCalendarTableName = VyaparSaathi-FestivalCalendar
VyaparSaathiStack.RawDataBucketName = vyapar-saathi-raw-data-123456789012
VyaparSaathiStack.ProcessedDataBucketName = vyapar-saathi-processed-data-123456789012
```

**IMPORTANT**: Save these values! You'll need them for:
- Frontend configuration
- Lambda function environment variables
- Testing and development

## Step 7: Verify Deployment

### Check AWS Console

1. **DynamoDB Tables**:
   - Go to AWS Console → DynamoDB → Tables
   - Verify 3 tables exist: UserProfiles, Forecasts, FestivalCalendar

2. **S3 Buckets**:
   - Go to AWS Console → S3
   - Verify 2 buckets exist with encryption enabled

3. **API Gateway**:
   - Go to AWS Console → API Gateway
   - Verify "VyaparSaathi API" exists with 4 endpoints

4. **Lambda Functions**:
   - Go to AWS Console → Lambda
   - Verify 4 functions exist with correct environment variables

5. **Cognito**:
   - Go to AWS Console → Cognito
   - Verify User Pool exists with email sign-in enabled

### Test API Endpoint

Test the API Gateway endpoint:

```bash
curl https://YOUR-API-ENDPOINT/prod/data/upload
```

Expected response (since Lambda is placeholder):
```json
{"message": "Data upload endpoint - to be implemented"}
```

## Step 8: Post-Deployment Configuration

### Configure Social Identity Providers (Optional)

To enable Google and Facebook login:

1. **Google OAuth**:
   - Go to Google Cloud Console
   - Create OAuth 2.0 credentials
   - Update `lib/vyapar-saathi-stack.ts` with client ID and secret
   - Redeploy: `npm run deploy`

2. **Facebook Login**:
   - Go to Facebook Developers
   - Create a Facebook App
   - Update `lib/vyapar-saathi-stack.ts` with app ID and secret
   - Redeploy: `npm run deploy`

### Update CORS for Production

For production, restrict CORS origins:

1. Edit `lib/vyapar-saathi-stack.ts`
2. Change `allowOrigins: apigateway.Cors.ALL_ORIGINS`
3. To: `allowOrigins: ['https://your-domain.com']`
4. Redeploy: `npm run deploy`

### Populate Festival Calendar

The FestivalCalendar table is empty after deployment. You'll need to:

1. Create festival seed data (Task 4.1)
2. Run data migration script (Task 4.2)

## Troubleshooting

### Error: "Unable to resolve AWS account"

**Solution**: Configure AWS credentials (see Step 1)

### Error: "CDK bootstrap required"

**Solution**: Run bootstrap command (see Step 3)

### Error: "Resource limit exceeded"

**Solution**: Check AWS service quotas in your account

### Error: "Stack already exists"

**Solution**: 
- If updating: Use `npx cdk deploy` (it will update)
- If starting fresh: Delete old stack first: `npx cdk destroy`

### Deployment Hangs

**Solution**:
- Check AWS Console CloudFormation for error details
- Look for resource creation failures
- May need to manually delete failed resources

## Rollback

If deployment fails or you need to remove resources:

```bash
npx cdk destroy
```

**WARNING**: This deletes most resources, but:
- DynamoDB tables are retained (RETAIN policy)
- S3 buckets are retained (RETAIN policy)
- You may need to manually delete these

To force delete everything:
1. Empty S3 buckets manually
2. Delete DynamoDB tables manually
3. Run `npx cdk destroy`

## Cost Estimation

After deployment, monitor costs:

1. Go to AWS Console → Billing Dashboard
2. Check "Cost Explorer"
3. Filter by service to see breakdown

Expected monthly costs (low usage):
- DynamoDB: $5-10 (on-demand)
- S3: $1-5 (storage + requests)
- Lambda: $0-5 (free tier covers most)
- API Gateway: $3-10 (per million requests)
- Cognito: $0 (free tier up to 50K MAUs)

**Total**: ~$10-30/month for development/testing

## Next Steps

After successful deployment:

1. [ ] Implement Lambda function code (currently placeholders)
2. [ ] Populate FestivalCalendar table with data
3. [ ] Configure social identity providers
4. [ ] Set up frontend application
5. [ ] Test API endpoints with real data
6. [ ] Configure custom domain (optional)
7. [ ] Set up CloudWatch alarms
8. [ ] Enable AWS WAF for API protection (optional)

## Support Resources

- AWS CDK Documentation: https://docs.aws.amazon.com/cdk/
- AWS CDK API Reference: https://docs.aws.amazon.com/cdk/api/v2/
- AWS Support: https://console.aws.amazon.com/support/
- VyaparSaathi Spec: `.kiro/specs/vyapar-saathi/`

## Deployment Checklist

Use this checklist to track deployment progress:

- [ ] AWS credentials configured
- [ ] Dependencies installed
- [ ] CDK bootstrapped
- [ ] Infrastructure synthesized and reviewed
- [ ] Stack deployed successfully
- [ ] Outputs saved
- [ ] Resources verified in AWS Console
- [ ] API endpoint tested
- [ ] Social providers configured (optional)
- [ ] CORS updated for production
- [ ] Festival calendar populated
- [ ] Monitoring configured

## Maintenance

### Update Infrastructure

To update infrastructure after code changes:

```bash
npm run deploy
```

CDK will detect changes and update only modified resources.

### View Current Stack

```bash
npx cdk ls
```

### Compare Local vs Deployed

```bash
npx cdk diff
```

### View Stack Events

```bash
aws cloudformation describe-stack-events --stack-name VyaparSaathiStack
```

---

**Deployment Complete!** Your VyaparSaathi infrastructure is now running on AWS.
