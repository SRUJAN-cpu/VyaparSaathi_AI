# @vyapar-saathi/shared-types

Comprehensive TypeScript interfaces and types for the VyaparSaathi festival demand and inventory risk forecasting platform.

## Overview

This package provides shared type definitions used across all components of the VyaparSaathi system:
- Frontend React application
- Backend Lambda functions
- Infrastructure CDK code
- Testing utilities

## Installation

```bash
npm install @vyapar-saathi/shared-types
```

## Usage

```typescript
import { 
  SalesRecord, 
  ForecastRequest, 
  RiskAssessment, 
  UserProfile 
} from '@vyapar-saathi/shared-types';

// Use the types in your code
const salesData: SalesRecord[] = [
  {
    date: '2024-01-15',
    sku: 'PROD-001',
    quantity: 25,
    category: 'electronics',
    price: 1500
  }
];
```

## Type Categories

### Core Data Types (`data.ts`)
- `SalesRecord` - Individual sales transaction
- `DataUpload` - File upload with validation
- `ValidationResult` - Data validation results
- `QuestionnaireResponse` - Low-data mode questionnaire
- `InventoryEstimate` - Inventory estimates

### Forecasting Types (`forecasting.ts`)
- `ForecastRequest` - Demand forecast request
- `ForecastResult` - Generated forecast results
- `DailyPrediction` - Daily demand predictions
- `ForecastSummary` - Forecast summary statistics

### Risk Assessment Types (`risk.ts`)
- `RiskAssessment` - Inventory risk analysis
- `ReorderRecommendation` - Reorder suggestions
- `RiskAlert` - Risk-based alerts
- `RiskDashboard` - Risk dashboard summary

### AI Explanation Types (`explanation.ts`)
- `ExplanationRequest` - AI explanation request
- `ExplanationResponse` - Generated explanations
- `ConversationContext` - Chat conversation context
- `ConversationTurn` - Individual chat turns

### User Profile Types (`user.ts`)
- `UserProfile` - Complete user profile
- `BusinessType` - Business type enumeration
- `NotificationSettings` - User notification preferences
- `DashboardPreferences` - Dashboard customization

### Festival Types (`festival.ts`)
- `FestivalEvent` - Festival definition
- `FestivalCalendar` - Regional festival calendar
- `FestivalImpact` - Festival impact analysis
- `FestivalCategory` - Festival categorization

### Synthetic Data Types (`synthetic.ts`)
- `SyntheticPattern` - Data generation patterns
- `SyntheticDataConfig` - Generation configuration
- `SyntheticDataset` - Generated synthetic data
- `DemoScenario` - Demo scenario definitions

### Common Utilities (`common.ts`)
- `ApiResponse<T>` - Generic API response wrapper
- `PaginatedResponse<T>` - Paginated response wrapper
- `TimeRange` - Time period specification
- `Location` - Geographic location
- `MoneyAmount` - Currency amounts

### API Types (`api.ts`)
- Namespace-organized API request/response types
- `DataUploadAPI` - Data upload endpoints
- `ForecastingAPI` - Forecasting endpoints
- `RiskAssessmentAPI` - Risk assessment endpoints
- `ExplanationAPI` - AI explanation endpoints
- `UserProfileAPI` - User profile endpoints
- `FestivalAPI` - Festival calendar endpoints
- `AnalyticsAPI` - Analytics endpoints
- `SystemAPI` - System status endpoints

## Development

### Building

```bash
npm run build
```

### Type Checking

```bash
npm run type-check
```

### Development Mode

```bash
npm run dev
```

## Design Principles

1. **Comprehensive Coverage** - All data structures used across the system
2. **Type Safety** - Strict typing with proper null/undefined handling
3. **Documentation** - Extensive JSDoc comments for all interfaces
4. **Modularity** - Organized into logical modules by domain
5. **Extensibility** - Designed for easy extension and modification
6. **Cross-Platform** - Compatible with frontend, backend, and infrastructure code

## Requirements Mapping

This package implements type definitions that support all system requirements:

- **Requirement 1**: Data input flexibility (data.ts)
- **Requirement 2**: Festival-aware forecasting (forecasting.ts, festival.ts)
- **Requirement 3**: Inventory risk assessment (risk.ts)
- **Requirement 4**: AI-powered explanations (explanation.ts)
- **Requirement 5**: User interface support (user.ts, api.ts)
- **Requirement 6**: System performance (common.ts, api.ts)
- **Requirement 7**: Data security (user.ts, common.ts)
- **Requirement 8**: Synthetic data support (synthetic.ts)

## Contributing

When adding new types:

1. Place them in the appropriate module file
2. Add comprehensive JSDoc documentation
3. Export from the main index.ts file
4. Update this README if adding new modules
5. Ensure backward compatibility

## License

Private - VyaparSaathi Project