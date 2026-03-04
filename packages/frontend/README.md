# VyaparSaathi Frontend

React-based web application for the VyaparSaathi festival demand and inventory risk forecasting platform.

## Features Implemented

### ✅ Task 12.1: React Application Structure
- React 18 with TypeScript
- React Router for navigation
- AWS Amplify integration for authentication and API calls
- Modular component architecture

### ✅ Task 12.2: Data Input Interface
- CSV upload component with drag-and-drop
- Low-data mode questionnaire form
- Input validation and error display
- User-friendly mode selection

### ✅ Task 12.3: Forecast and Risk Visualization
- Dashboard with forecast charts (area charts with confidence bounds)
- Risk indicator components with color coding (low/medium/high)
- Reorder recommendation cards with urgency levels
- Recharts integration for data visualization

### ✅ Task 12.4: AI Copilot Interface
- Chat-style interface for user queries
- Display explanations with key insights and assumptions
- Contextual help tooltips
- Suggested questions for quick access

### ✅ Task 12.5: Mobile Responsiveness
- Responsive layouts for mobile devices
- Touch-friendly interactions (44px minimum touch targets)
- Optimized navigation for small screens
- Fluid typography with clamp()

### ✅ Task 13.1: Wire Frontend to Backend APIs
- Connected all components to API Gateway endpoints
- Implemented authentication flow with Cognito
- Added loading states and error handling
- Automatic JWT token management
- User session management

## Technology Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **React Router 6** - Client-side routing
- **AWS Amplify 6** - Authentication and API integration
- **Recharts** - Data visualization
- **Vite** - Build tool and dev server
- **Vitest** - Testing framework

## Quick Start

### Automated Setup (Recommended)

**Linux/macOS:**
```bash
cd packages/frontend
./setup.sh
```

**Windows:**
```powershell
cd packages\frontend
.\setup.ps1
```

The setup script will:
1. Create `.env` file from template
2. Auto-configure from infrastructure outputs (if available)
3. Prompt for manual configuration if needed

### Manual Setup

1. **Install Dependencies:**
   ```bash
   npm install
   ```

2. **Configure Environment:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your AWS configuration:
   ```env
   VITE_USER_POOL_ID=us-east-1_AbCdEfGhI
   VITE_USER_POOL_CLIENT_ID=1a2b3c4d5e6f7g8h9i0j
   VITE_IDENTITY_POOL_ID=us-east-1:12345678-1234-1234-1234-123456789012
   VITE_API_ENDPOINT=https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod
   VITE_AWS_REGION=us-east-1
   ```

3. **Get Configuration Values:**
   
   From CDK deployment:
   ```bash
   cd ../../infrastructure
   npx cdk deploy --outputs-file outputs.json
   ```
   
   Or from AWS Console:
   - Cognito → User Pools → VyaparSaathi-UserPool
   - API Gateway → VyaparSaathi API → Stages → prod

4. **Start Development Server:**
   ```bash
   npm run dev
   ```

## Development

### Available Scripts

```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build
npm run test         # Run tests
npm run type-check   # TypeScript type checking
npm run lint         # Lint code
```

### Environment Variables

Required variables:
- `VITE_USER_POOL_ID` - Cognito User Pool ID
- `VITE_USER_POOL_CLIENT_ID` - Cognito App Client ID
- `VITE_API_ENDPOINT` - API Gateway endpoint URL
- `VITE_AWS_REGION` - AWS region (default: us-east-1)

Optional:
- `VITE_IDENTITY_POOL_ID` - Cognito Identity Pool ID

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── Layout.tsx      # Main layout with navigation
│   ├── CSVUpload.tsx   # CSV file upload
│   ├── Questionnaire.tsx # Low-data mode form
│   ├── ForecastChart.tsx # Demand forecast visualization
│   ├── RiskIndicator.tsx # Risk level display
│   ├── ReorderCard.tsx  # Reorder recommendations
│   ├── ChatInterface.tsx # AI copilot chat
│   └── HelpTooltip.tsx  # Contextual help
├── pages/              # Page components
│   ├── HomePage.tsx    # Landing page
│   ├── DataInputPage.tsx # Data input interface
│   ├── DashboardPage.tsx # Forecast dashboard
│   └── CopilotPage.tsx  # AI copilot
├── routes/             # Route configuration
├── services/           # API services
│   └── api.ts         # Backend API integration
├── config/             # AWS Amplify config
│   └── amplify.ts     # Amplify configuration
├── styles/             # Global styles
└── test/               # Test utilities
```

## API Integration

All API calls are handled through `services/api.ts`:

### Available Functions

```typescript
// Data upload
uploadSalesData(file: File): Promise<ApiResponse<any>>
submitQuestionnaire(data: any): Promise<ApiResponse<any>>

// Forecasting
getForecast(params: { forecastHorizon?: number, targetFestivals?: string[] }): Promise<ApiResponse<any>>

// Risk assessment
getRiskAssessment(): Promise<ApiResponse<any>>

// AI copilot
askCopilot(query: string, context?: any): Promise<ApiResponse<any>>
getExplanation(type: 'forecast' | 'risk', data: any): Promise<ApiResponse<any>>
```

### Authentication

All API calls automatically include:
- User ID from Cognito session
- JWT authentication token
- Proper error handling

Example usage:
```typescript
const result = await uploadSalesData(file);
if (result.success) {
  console.log('Upload successful:', result.data);
} else {
  console.error('Upload failed:', result.error);
}
```

## Authentication Flow

1. **Sign Up:**
   - Email and password required
   - Email verification via code
   - Password complexity enforced

2. **Sign In:**
   - Email/password authentication
   - JWT tokens managed automatically
   - Session persists across page reloads

3. **Sign Out:**
   - Click "Sign Out" in header
   - Clears session and redirects to login

## Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed deployment instructions including:
- AWS Amplify Hosting
- S3 + CloudFront
- Vercel/Netlify
- Environment configuration
- Troubleshooting

## Troubleshooting

### Configuration Error on Startup

**Problem:** Red error screen about missing configuration

**Solution:**
1. Ensure `.env` file exists
2. Verify all required variables are set
3. Restart dev server

### Authentication Fails

**Problem:** Cannot sign in or sign up

**Solution:**
1. Verify Cognito configuration in `.env`
2. Check User Pool is active in AWS Console
3. Ensure callback URLs are configured

### API Calls Fail

**Problem:** API requests return errors

**Solution:**
1. Verify API endpoint in `.env`
2. Check Lambda functions are deployed
3. Review CloudWatch logs for backend errors
4. Verify CORS is configured in API Gateway

## Testing

```bash
# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run tests with coverage
npm test -- --coverage
```

## Key Features

- **Authentication**: AWS Cognito with Amplify Authenticator
- **Data Input**: Dual-mode (CSV upload or questionnaire)
- **Visualization**: Interactive charts with Recharts
- **AI Copilot**: Chat interface for explanations
- **Mobile-First**: Responsive design for all devices
- **Type-Safe**: Full TypeScript coverage
- **Error Handling**: Comprehensive error handling and user feedback
- **Loading States**: Visual feedback for async operations

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Performance

- Code splitting for faster initial load
- Lazy loading of routes
- Optimized bundle size
- Asset optimization in production

## Security

- HTTPS enforced in production
- JWT token authentication
- Secure session management
- Environment variables for sensitive data
- CORS protection

## Contributing

1. Follow TypeScript best practices
2. Write tests for new features
3. Ensure mobile responsiveness
4. Update documentation

## Support

For issues or questions:
1. Check browser console for errors
2. Review CloudWatch logs for backend issues
3. Verify AWS configuration
4. Consult DEPLOYMENT.md

## License

See main project LICENSE file.
