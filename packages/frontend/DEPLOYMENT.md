# VyaparSaathi Frontend Deployment Guide

This guide explains how to configure and deploy the VyaparSaathi frontend application.

## Prerequisites

- Node.js 18.x or later
- npm or yarn
- AWS account with deployed VyaparSaathi infrastructure
- AWS Cognito User Pool and API Gateway endpoints

## Configuration

### Step 1: Set Up Environment Variables

1. Copy the example environment file:
   ```bash
   cd packages/frontend
   cp .env.example .env
   ```

2. Edit `.env` and fill in your AWS configuration:
   ```env
   # AWS Cognito Configuration
   VITE_USER_POOL_ID=us-east-1_AbCdEfGhI
   VITE_USER_POOL_CLIENT_ID=1a2b3c4d5e6f7g8h9i0j
   VITE_IDENTITY_POOL_ID=us-east-1:12345678-1234-1234-1234-123456789012
   
   # API Configuration
   VITE_API_ENDPOINT=https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod
   VITE_AWS_REGION=us-east-1
   ```

### Step 2: Get AWS Configuration Values

You can find these values from your infrastructure deployment:

**From CDK Outputs:**
```bash
cd infrastructure
npx cdk deploy --outputs-file outputs.json
```

The outputs will include:
- `UserPoolId` → Use for `VITE_USER_POOL_ID`
- `UserPoolClientId` → Use for `VITE_USER_POOL_CLIENT_ID`
- `ApiEndpoint` → Use for `VITE_API_ENDPOINT`

**From AWS Console:**

1. **Cognito User Pool ID:**
   - Go to AWS Console → Cognito → User Pools
   - Select "VyaparSaathi-UserPool"
   - Copy the "User pool ID" (format: `us-east-1_XXXXXXXXX`)

2. **Cognito User Pool Client ID:**
   - In the same User Pool, go to "App integration" tab
   - Under "App clients", find "VyaparSaathi-WebClient"
   - Copy the "Client ID"

3. **API Gateway Endpoint:**
   - Go to AWS Console → API Gateway
   - Select "VyaparSaathi API"
   - Go to "Stages" → "prod"
   - Copy the "Invoke URL"

4. **Identity Pool ID (Optional):**
   - Go to AWS Console → Cognito → Identity Pools
   - If you created an identity pool, copy its ID
   - Otherwise, leave this empty

## Development

### Install Dependencies

```bash
npm install
```

### Run Development Server

```bash
npm run dev
```

The application will be available at `http://localhost:5173`

### Build for Production

```bash
npm run build
```

This creates an optimized production build in the `dist` directory.

### Preview Production Build

```bash
npm run preview
```

## Authentication Flow

The application uses AWS Amplify Authenticator for user authentication:

1. **Sign Up:**
   - Users can create an account with email and password
   - Email verification is required
   - Password must meet complexity requirements (8+ chars, uppercase, lowercase, numbers, symbols)

2. **Sign In:**
   - Users sign in with email and password
   - JWT tokens are automatically managed by Amplify
   - Tokens are included in all API requests

3. **Sign Out:**
   - Click "Sign Out" button in the header
   - Clears local session and redirects to login

## API Integration

All API calls are handled through the `services/api.ts` module:

### Available API Functions

- `uploadSalesData(file)` - Upload CSV sales data
- `submitQuestionnaire(data)` - Submit low-data mode questionnaire
- `getForecast(params)` - Get demand forecasts
- `getRiskAssessment()` - Get inventory risk assessment
- `askCopilot(query, context)` - Ask AI copilot questions
- `getExplanation(type, data)` - Get explanations for forecasts/risks

### Authentication

All API calls automatically include:
- User ID from Cognito session
- JWT authentication token in headers
- Proper error handling and retry logic

### Error Handling

The API service provides consistent error handling:
```typescript
const result = await uploadSalesData(file);
if (result.success) {
  // Handle success
  console.log(result.data);
} else {
  // Handle error
  console.error(result.error);
}
```

## Components

### Pages

- **HomePage** - Landing page with overview
- **DataInputPage** - CSV upload or questionnaire
- **DashboardPage** - Forecasts and risk visualizations
- **CopilotPage** - AI assistant chat interface

### Components

- **CSVUpload** - Drag-and-drop file upload
- **Questionnaire** - Low-data mode form
- **ForecastChart** - Demand forecast visualization
- **RiskIndicator** - Risk level display
- **ReorderCard** - Reorder recommendations
- **ChatInterface** - AI copilot chat
- **Layout** - Main layout with navigation

## Deployment to AWS

### Option 1: AWS Amplify Hosting

1. **Connect Repository:**
   ```bash
   amplify init
   amplify add hosting
   amplify publish
   ```

2. **Configure Build Settings:**
   ```yaml
   version: 1
   frontend:
     phases:
       preBuild:
         commands:
           - cd packages/frontend
           - npm install
       build:
         commands:
           - npm run build
     artifacts:
       baseDirectory: packages/frontend/dist
       files:
         - '**/*'
     cache:
       paths:
         - node_modules/**/*
   ```

3. **Set Environment Variables:**
   - Go to Amplify Console → App Settings → Environment Variables
   - Add all `VITE_*` variables from your `.env` file

### Option 2: S3 + CloudFront

1. **Build the Application:**
   ```bash
   npm run build
   ```

2. **Create S3 Bucket:**
   ```bash
   aws s3 mb s3://vyapar-saathi-frontend
   aws s3 website s3://vyapar-saathi-frontend --index-document index.html
   ```

3. **Upload Build:**
   ```bash
   aws s3 sync dist/ s3://vyapar-saathi-frontend --delete
   ```

4. **Create CloudFront Distribution:**
   - Point to S3 bucket
   - Configure custom domain (optional)
   - Enable HTTPS

### Option 3: Vercel/Netlify

1. **Connect Repository:**
   - Import project from GitHub
   - Set root directory to `packages/frontend`

2. **Configure Build:**
   - Build command: `npm run build`
   - Output directory: `dist`

3. **Set Environment Variables:**
   - Add all `VITE_*` variables in the platform's settings

## Troubleshooting

### Configuration Error on Startup

**Problem:** Red error screen saying "Configuration Error"

**Solution:**
1. Ensure `.env` file exists in `packages/frontend`
2. Verify all required variables are set
3. Restart the development server

### Authentication Fails

**Problem:** Cannot sign in or sign up

**Solution:**
1. Verify `VITE_USER_POOL_ID` and `VITE_USER_POOL_CLIENT_ID` are correct
2. Check Cognito User Pool is deployed and active
3. Ensure callback URLs are configured in Cognito

### API Calls Fail

**Problem:** API requests return errors

**Solution:**
1. Verify `VITE_API_ENDPOINT` is correct and includes `/prod` stage
2. Check API Gateway is deployed and endpoints exist
3. Verify Lambda functions are deployed and working
4. Check CloudWatch logs for backend errors

### CORS Errors

**Problem:** Browser shows CORS policy errors

**Solution:**
1. Verify API Gateway has CORS enabled
2. Check allowed origins include your frontend URL
3. Ensure preflight OPTIONS requests are handled

## Testing

### Run Unit Tests

```bash
npm test
```

### Run E2E Tests (if configured)

```bash
npm run test:e2e
```

## Performance Optimization

### Production Build Optimizations

The production build includes:
- Code splitting for faster initial load
- Tree shaking to remove unused code
- Minification and compression
- Asset optimization

### Lazy Loading

Routes are lazy-loaded to improve performance:
```typescript
const DashboardPage = lazy(() => import('./pages/DashboardPage'));
```

### Caching

API responses can be cached using React Query or SWR (optional enhancement).

## Security Considerations

1. **Environment Variables:**
   - Never commit `.env` files to version control
   - Use different values for development and production

2. **Authentication:**
   - JWT tokens are stored securely by Amplify
   - Tokens automatically refresh before expiration

3. **API Security:**
   - All API calls require authentication
   - HTTPS is enforced in production

4. **CORS:**
   - Restrict allowed origins in production
   - Update API Gateway CORS settings

## Monitoring

### CloudWatch Logs

Monitor frontend errors using CloudWatch RUM (optional):
```typescript
import { AwsRum } from 'aws-rum-web';

const awsRum = new AwsRum(
  'vyapar-saathi-frontend',
  '1.0.0',
  'us-east-1',
  {
    sessionSampleRate: 1,
    guestRoleArn: 'arn:aws:iam::ACCOUNT:role/RUM-Monitor',
    identityPoolId: 'IDENTITY_POOL_ID',
    endpoint: 'https://dataplane.rum.us-east-1.amazonaws.com',
    telemetries: ['errors', 'performance', 'http'],
  }
);
```

### Error Tracking

Consider integrating error tracking services:
- Sentry
- Rollbar
- Bugsnag

## Support

For issues or questions:
1. Check CloudWatch logs for backend errors
2. Review browser console for frontend errors
3. Verify AWS configuration is correct
4. Consult the main project documentation

## Next Steps

After deployment:
1. Test authentication flow
2. Upload sample data
3. Verify forecasts are generated
4. Test AI copilot functionality
5. Configure custom domain (optional)
6. Set up monitoring and alerts
7. Enable CloudFront CDN for better performance
