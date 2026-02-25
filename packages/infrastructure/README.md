# VyaparSaathi Infrastructure

AWS CDK infrastructure code for the VyaparSaathi platform.

## Prerequisites

- AWS CLI configured with appropriate credentials
- Node.js 18+ and npm 9+
- AWS CDK CLI: `npm install -g aws-cdk`

## Useful Commands

- `npm run build` - Compile TypeScript to JavaScript
- `npm run watch` - Watch for changes and compile
- `npm run test` - Run unit tests
- `npm run cdk deploy` - Deploy this stack to your default AWS account/region
- `npm run cdk diff` - Compare deployed stack with current state
- `npm run cdk synth` - Emit the synthesized CloudFormation template

## Architecture

The infrastructure includes:

- **API Gateway**: REST API endpoints
- **Lambda Functions**: Serverless compute for backend logic
- **DynamoDB**: NoSQL database for user data and forecasts
- **S3**: Object storage for raw and processed data
- **Cognito**: User authentication and authorization
- **Bedrock**: AI-powered explanations
- **Forecast**: Demand forecasting service

## Deployment

```bash
# Bootstrap CDK (first time only)
cdk bootstrap

# Deploy the stack
npm run cdk deploy
```
