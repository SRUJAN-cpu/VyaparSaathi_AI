# Frontend-Backend Integration Guide

This document explains how the VyaparSaathi frontend integrates with the backend AWS infrastructure.

## Architecture Overview

```
┌─────────────────┐
│   React App     │
│   (Frontend)    │
└────────┬────────┘
         │
         │ AWS Amplify
         │
    ┌────▼─────┐
    │ Cognito  │ ◄── Authentication
    │User Pool │
    └────┬─────┘
         │
         │ JWT Token
         │
    ┌────▼─────────┐
    │ API Gateway  │ ◄── REST API
    └────┬─────────┘
         │
    ┌────▼─────────┐
    │   Lambda     │ ◄── Business Logic
    │  Functions   │
    └──────────────┘
```

## Authentication Flow

### 1. User Sign Up

```typescript
// Handled by AWS Amplify Authenticator component
// User provides: email, password
// Cognito sends verification code to email
// User enters code to verify account
```

**Backend:**
- Cognito User Pool creates user account
- Sends verification email
- Stores user attributes (email, custom attributes)

### 2. User Sign In

```typescript
// Handled by AWS Amplify Authenticator component
// User provides: email, password
// Amplify exchanges credentials for JWT tokens
```

**Backend:**
- Cognito validates credentials
- Issues JWT tokens (ID token, Access token, Refresh token)
- Tokens stored securely by Amplify

### 3. Authenticated API Calls

```typescript
// services/api.ts
import { post } from 'aws-amplify/api';
import { fetchAuthSession } from 'aws-amplify/auth';

// Get user ID from session
const session = await fetchAuthSession();
const userId = session.userSub;

// Make authenticated request
const response = await post({
  apiName: 'VyaparSaathiAPI',
  path: '/forecast',
  options: {
    body: { userId, forecastHorizon: 14 }
  }
}).response;
```

**Backend:**
- API Gateway validates JWT token
- Extracts user identity
- Routes to Lambda function
- Lambda processes request with user context

## API Endpoints

### Data Upload Endpoint

**Frontend:**
```typescript
uploadSalesData(file: File)
```

**Request:**
```http
POST /data/upload
Content-Type: application/json
Authorization: Bearer <JWT_TOKEN>

{
  "userId": "user-123",
  "dataType": "csv",
  "fileContent": "date,sku,quantity\n2024-01-01,PROD-001,100",
  "fileName": "sales.csv"
}
```

**Backend Lambda:**
- Validates CSV format
- Parses sales data
- Stores in S3 (raw-data bucket)
- Updates user profile in DynamoDB
- Returns validation result

**Response:**
```json
{
  "success": true,
  "recordsProcessed": 150,
  "validationErrors": [],
  "dataQuality": "good"
}
```

### Questionnaire Endpoint

**Frontend:**
```typescript
submitQuestionnaire(data: QuestionnaireData)
```

**Request:**
```http
POST /data/upload
Content-Type: application/json
Authorization: Bearer <JWT_TOKEN>

{
  "userId": "user-123",
  "dataType": "questionnaire",
  "questionnaireData": {
    "businessType": "grocery",
    "storeSize": "medium",
    "lastFestivalPerformance": {
      "salesIncrease": 50,
      "topCategories": ["Sweets", "Decorations"],
      "stockoutItems": ["Diyas"]
    },
    "targetFestivals": ["Diwali", "Holi"]
  }
}
```

**Backend Lambda:**
- Validates questionnaire data
- Generates synthetic baseline patterns
- Stores in DynamoDB user profile
- Returns confirmation

**Response:**
```json
{
  "success": true,
  "message": "Questionnaire processed successfully",
  "dataMode": "low-data"
}
```

### Forecast Endpoint

**Frontend:**
```typescript
getForecast({ forecastHorizon: 14, targetFestivals: ['Diwali'] })
```

**Request:**
```http
POST /forecast
Content-Type: application/json
Authorization: Bearer <JWT_TOKEN>

{
  "userId": "user-123",
  "forecastHorizon": 14,
  "targetFestivals": ["Diwali"]
}
```

**Backend Lambda:**
- Retrieves user data from DynamoDB
- Fetches festival calendar data
- Generates forecast using ML or pattern-based method
- Stores forecast in DynamoDB
- Returns predictions

**Response:**
```json
{
  "success": true,
  "forecasts": [
    {
      "sku": "PROD-001",
      "category": "Sweets",
      "predictions": [
        {
          "date": "2024-01-01",
          "demandForecast": 150,
          "lowerBound": 130,
          "upperBound": 170,
          "festivalMultiplier": 1.5
        }
      ],
      "confidence": 0.85,
      "methodology": "ml"
    }
  ]
}
```

### Risk Assessment Endpoint

**Frontend:**
```typescript
getRiskAssessment()
```

**Request:**
```http
POST /risk
Content-Type: application/json
Authorization: Bearer <JWT_TOKEN>

{
  "userId": "user-123"
}
```

**Backend Lambda:**
- Retrieves forecasts from DynamoDB
- Retrieves current inventory from user profile
- Calculates stockout and overstock risks
- Generates reorder recommendations
- Returns risk assessment

**Response:**
```json
{
  "success": true,
  "risks": [
    {
      "sku": "PROD-001",
      "category": "Sweets",
      "currentStock": 50,
      "stockoutRisk": {
        "probability": 0.75,
        "daysUntilStockout": 3,
        "potentialLostSales": 500
      },
      "overstockRisk": {
        "probability": 0.15,
        "excessUnits": 0,
        "carryingCost": 0
      },
      "recommendation": {
        "action": "reorder",
        "suggestedQuantity": 200,
        "urgency": "high",
        "reasoning": [
          "High demand expected during Diwali",
          "Current stock insufficient"
        ],
        "confidence": 0.85
      }
    }
  ]
}
```

### AI Explanation Endpoint

**Frontend:**
```typescript
askCopilot(query: string, context?: any)
getExplanation(type: 'forecast' | 'risk', data: any)
```

**Request:**
```http
POST /explanation
Content-Type: application/json
Authorization: Bearer <JWT_TOKEN>

{
  "userId": "user-123",
  "query": "Why is my stockout risk high for diyas?",
  "context": {
    "sku": "DIYA-001",
    "currentRisk": 0.75
  },
  "complexity": "simple"
}
```

**Backend Lambda:**
- Retrieves relevant forecast/risk data
- Constructs prompt for Amazon Bedrock
- Calls Bedrock API (Claude model)
- Formats response for frontend
- Returns explanation

**Response:**
```json
{
  "success": true,
  "explanation": "Your stockout risk for diyas is high because Diwali is approaching in 5 days, and based on last year's sales, demand typically increases by 300% during this period. Your current stock of 50 units will likely run out in 3 days.",
  "keyInsights": [
    "Diwali demand spike expected",
    "Current stock insufficient for 5 days",
    "Historical data shows 300% increase"
  ],
  "assumptions": [
    "Demand pattern similar to last year",
    "No supply chain delays",
    "Normal customer behavior"
  ],
  "confidence": "High"
}
```

## Error Handling

### Frontend Error Handling

All API functions return a consistent response format:

```typescript
interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}
```

**Usage:**
```typescript
const result = await uploadSalesData(file);
if (result.success) {
  // Handle success
  setData(result.data);
} else {
  // Handle error
  setError(result.error);
}
```

### Backend Error Responses

**Validation Error:**
```json
{
  "statusCode": 400,
  "body": {
    "error": "Invalid CSV format",
    "details": "Missing required column: sku"
  }
}
```

**Authentication Error:**
```json
{
  "statusCode": 401,
  "body": {
    "error": "Unauthorized",
    "message": "Invalid or expired token"
  }
}
```

**Server Error:**
```json
{
  "statusCode": 500,
  "body": {
    "error": "Internal server error",
    "message": "Failed to process request"
  }
}
```

### Frontend Error Display

Components display errors using consistent UI patterns:

```typescript
{error && (
  <div style={{
    padding: '1rem',
    backgroundColor: '#ffebee',
    color: '#c62828',
    borderRadius: '4px',
    border: '1px solid #ef5350',
  }}>
    {error}
  </div>
)}
```

## Loading States

All async operations show loading indicators:

```typescript
const [loading, setLoading] = useState(false);

const loadData = async () => {
  setLoading(true);
  const result = await getForecast({ forecastHorizon: 14 });
  setLoading(false);
  
  if (result.success) {
    setData(result.data);
  }
};

if (loading) {
  return <LoadingSpinner />;
}
```

## Data Flow Examples

### Complete Upload Flow

1. **User selects CSV file**
   - CSVUpload component validates file type
   - Shows file name in UI

2. **User clicks "Upload"**
   - Component sets loading state
   - Calls `uploadSalesData(file)`

3. **API service processes request**
   - Reads file content
   - Gets user ID from Cognito session
   - Sends POST request to `/data/upload`

4. **Backend processes data**
   - Lambda validates CSV format
   - Parses records
   - Stores in S3
   - Updates DynamoDB

5. **Frontend receives response**
   - Clears loading state
   - Shows success message
   - Redirects to dashboard

### Complete Forecast Flow

1. **User navigates to dashboard**
   - DashboardPage component mounts
   - useEffect triggers data load

2. **Component requests forecast**
   - Sets loading state
   - Calls `getForecast({ forecastHorizon: 14 })`

3. **API service makes request**
   - Gets user ID from session
   - Sends POST to `/forecast`

4. **Backend generates forecast**
   - Retrieves user data
   - Fetches festival calendar
   - Runs forecasting algorithm
   - Stores results
   - Returns predictions

5. **Frontend displays results**
   - Clears loading state
   - Renders ForecastChart with data
   - Shows risk indicators
   - Displays recommendations

## Session Management

### Token Refresh

Amplify automatically handles token refresh:

```typescript
// Tokens are refreshed automatically before expiration
// No manual intervention needed
const session = await fetchAuthSession();
// Always returns valid tokens or throws error
```

### Session Persistence

Sessions persist across page reloads:

```typescript
// On app load, Amplify checks for existing session
// If valid, user remains authenticated
// If expired, redirects to login
```

### Sign Out

```typescript
// Layout.tsx
const { signOut } = useAuthenticator();

<button onClick={signOut}>Sign Out</button>
// Clears all tokens and session data
// Redirects to login page
```

## CORS Configuration

API Gateway must allow frontend origin:

```typescript
// infrastructure/lib/vyapar-saathi-stack.ts
defaultCorsPreflightOptions: {
  allowOrigins: [
    'http://localhost:5173',  // Development
    'https://vyaparsaathi.example.com'  // Production
  ],
  allowMethods: ['GET', 'POST', 'OPTIONS'],
  allowHeaders: [
    'Content-Type',
    'Authorization',
    'X-Amz-Date',
    'X-Api-Key',
    'X-Amz-Security-Token'
  ]
}
```

## Security Considerations

### Token Storage

- JWT tokens stored securely by Amplify
- Never exposed in localStorage or cookies
- Automatically included in API requests

### API Security

- All endpoints require authentication
- JWT tokens validated by API Gateway
- User ID extracted from token (not from request body)

### Data Privacy

- User data isolated by userId
- No cross-user data access
- Encryption in transit (HTTPS)
- Encryption at rest (S3, DynamoDB)

## Testing Integration

### Mock API Responses

For testing without backend:

```typescript
// services/api.test.ts
vi.mock('aws-amplify/api', () => ({
  post: vi.fn(() => ({
    response: Promise.resolve({
      body: {
        json: () => Promise.resolve({ success: true })
      }
    })
  }))
}));
```

### Integration Tests

Test complete flows:

```typescript
test('upload and forecast flow', async () => {
  // Upload data
  const uploadResult = await uploadSalesData(mockFile);
  expect(uploadResult.success).toBe(true);
  
  // Get forecast
  const forecastResult = await getForecast({ forecastHorizon: 14 });
  expect(forecastResult.success).toBe(true);
  expect(forecastResult.data.forecasts).toBeDefined();
});
```

## Troubleshooting

### "Configuration Error" on startup

**Cause:** Missing environment variables

**Fix:** Create `.env` file with required variables

### "Unauthorized" errors

**Cause:** Invalid or expired JWT token

**Fix:** Sign out and sign in again

### CORS errors

**Cause:** API Gateway not configured for frontend origin

**Fix:** Update CORS settings in infrastructure

### API timeout errors

**Cause:** Lambda function taking too long

**Fix:** Check CloudWatch logs, optimize Lambda code

## Monitoring

### Frontend Monitoring

Use browser console to monitor:
- API request/response logs
- Authentication state changes
- Error messages

### Backend Monitoring

Check CloudWatch logs:
- API Gateway access logs
- Lambda function logs
- Error rates and latency

## Next Steps

1. Deploy infrastructure (see infrastructure/DEPLOYMENT.md)
2. Configure frontend environment (see DEPLOYMENT.md)
3. Test authentication flow
4. Test data upload
5. Verify forecast generation
6. Test AI copilot
7. Monitor for errors
8. Optimize performance
