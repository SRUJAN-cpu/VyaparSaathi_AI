# VyaparSaathi Project Structure

```
vyapar-saathi/
├── packages/
│   ├── frontend/                    # React + TypeScript (Tasks 13.x)
│   │   ├── src/
│   │   │   ├── components/          # UI components (13.2, 13.3, 13.4)
│   │   │   ├── pages/               # Page components (13.1)
│   │   │   ├── services/            # API calls (14.1)
│   │   │   └── types/               # TypeScript interfaces (1.3)
│   │   └── package.json
│   │
│   ├── backend/                     # Python Lambda functions
│   │   ├── src/
│   │   │   ├── orchestrator/        # Main orchestrator (14.2)
│   │   │   ├── data_processor/      # Data upload & validation (3.x)
│   │   │   ├── forecast_engine/     # Forecasting logic (7.x)
│   │   │   ├── risk_assessor/       # Risk calculations (8.x)
│   │   │   ├── ai_explainer/        # Bedrock integration (10.x)
│   │   │   ├── festival_calendar/   # Festival queries (4.x)
│   │   │   └── synthetic_data/      # Demo data generator (5.x)
│   │   ├── tests/                   # Pytest + Hypothesis tests
│   │   └── requirements.txt
│   │
│   └── infrastructure/              # AWS CDK (Tasks 2.x, 10.x)
│       ├── lib/
│       │   ├── stacks/
│       │   │   ├── database-stack.ts      # DynamoDB tables (2.1, 10.1)
│       │   │   ├── storage-stack.ts       # S3 buckets (2.2, 10.2)
│       │   │   ├── api-stack.ts           # API Gateway (2.3, 10.3)
│       │   │   └── auth-stack.ts          # Cognito (2.4, 10.4)
│       │   └── app.ts
│       └── package.json
│
├── .eslintrc.json                   # Linting config (1.1)
├── .prettierrc                      # Formatting config (1.1)
├── package.json                     # Root workspace config (1.1)
└── tsconfig.json                    # Shared TypeScript config (1.1)
```

## Task to Folder Mapping

**Task 1.x** - Project setup (DONE)
- Root configs, package.json, tsconfig

**Task 2.x & 10.x** - Infrastructure
- `packages/infrastructure/lib/stacks/`

**Task 3.x** - Data processing
- `packages/backend/src/data_processor/`

**Task 4.x** - Festival calendar
- `packages/backend/src/festival_calendar/`

**Task 5.x** - Synthetic data
- `packages/backend/src/synthetic_data/`

**Task 7.x** - Forecasting
- `packages/backend/src/forecast_engine/`

**Task 8.x** - Risk assessment
- `packages/backend/src/risk_assessor/`

**Task 10.x** - AI explanations
- `packages/backend/src/ai_explainer/`

**Task 11.x** - Performance & errors
- Across all Lambda functions

**Task 13.x** - Frontend
- `packages/frontend/src/`

**Task 14.x** - Integration
- `packages/backend/src/orchestrator/` + frontend services
