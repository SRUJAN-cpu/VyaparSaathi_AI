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

## Technology Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **React Router 6** - Client-side routing
- **AWS Amplify 6** - Authentication and API integration
- **Recharts** - Data visualization
- **Vite** - Build tool and dev server
- **Vitest** - Testing framework

## Getting Started

### Prerequisites
- Node.js >= 18.0.0
- npm >= 9.0.0

### Installation
```bash
npm install
```

### Environment Variables
Copy `.env.example` to `.env` and configure:
```
VITE_USER_POOL_ID=your-user-pool-id
VITE_USER_POOL_CLIENT_ID=your-user-pool-client-id
VITE_IDENTITY_POOL_ID=your-identity-pool-id
VITE_API_ENDPOINT=https://your-api-gateway-endpoint
VITE_AWS_REGION=us-east-1
```

### Development
```bash
npm run dev
```

### Build
```bash
npm run build
```

### Testing
```bash
npm run test
```

### Type Checking
```bash
npm run type-check
```

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
├── config/             # AWS Amplify config
├── styles/             # Global styles
└── test/               # Test utilities
```

## Key Features

- **Authentication**: AWS Cognito integration with Amplify Authenticator
- **Data Input**: Dual-mode (CSV upload or questionnaire)
- **Visualization**: Interactive charts with Recharts
- **AI Copilot**: Chat interface for explanations
- **Mobile-First**: Responsive design for all screen sizes
- **Type-Safe**: Full TypeScript coverage

## Next Steps

- Connect to actual backend APIs (Task 13.1)
- Add loading states and error boundaries
- Implement offline support
- Add analytics and monitoring
