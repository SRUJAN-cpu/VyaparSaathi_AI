# Orchestrator Lambda

The orchestrator Lambda is the main entry point for the VyaparSaathi system, coordinating workflow between data processing, forecasting, risk assessment, and AI explanation components.

## Overview

The orchestrator implements the following key responsibilities:

1. **Data Source Prioritization** (Requirement 1.4): Determines data availability and routes to appropriate forecasting method (structured vs low-data mode)
2. **Workflow Coordination**: Orchestrates the flow between forecast generation and risk assessment
3. **Parallel Processing** (Requirement 6.1): Executes forecast and risk calculations in parallel to meet 30-second performance target
4. **Result Aggregation**: Combines results from multiple components into unified response
5. **Error Handling**: Gracefully handles component failures and provides clear error messages

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Orchestrator Lambda                       │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  1. Determine Data Mode                            │    │
│  │     - Check user profile                           │    │
│  │     - Assess data quality                          │    │
│  │     - Select data source (structured vs low-data)  │    │
│  └────────────────────────────────────────────────────┘    │
│                          │                                   │
│                          ▼                                   │
│  ┌────────────────────────────────────────────────────┐    │
│  │  2. Generate Forecast                              │    │
│  │     - Route to ML or pattern-based forecaster      │    │
│  │     - Incorporate festival calendar data           │    │
│  │     - Store forecast results                       │    │
│  └────────────────────────────────────────────────────┘    │
│                          │                                   │
│                          ▼                                   │
│  ┌────────────────────────────────────────────────────┐    │
│  │  3. Assess Risks (Parallel)                        │    │
│  │     - Calculate stockout/overstock risks           │    │
│  │     - Generate reorder recommendations             │    │
│  │     - Create alerts for high-urgency items         │    │
│  └────────────────────────────────────────────────────┘    │
│                          │                                   │
│                          ▼                                   │
│  ┌────────────────────────────────────────────────────┐    │
│  │  4. Generate Explanations (Optional)               │    │
│  │     - Create forecast explanations                 │    │
│  │     - Create risk explanations                     │    │
│  │     - Use Amazon Bedrock for natural language      │    │
│  └────────────────────────────────────────────────────┘    │
│                          │                                   │
│                          ▼                                   │
│  ┌────────────────────────────────────────────────────┐    │
│  │  5. Aggregate Results                              │    │
│  │     - Combine forecast, risk, and explanation data │    │
│  │     - Add performance metadata                     │    │
│  │     - Return unified response                      │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## API Actions

The orchestrator supports three main actions:

### 1. forecast_and_risk

Generates demand forecasts and risk assessments for inventory items.

**Request:**
```json
{
  "action": "forecast_and_risk",
  "userId": "user123",
  "forecastHorizon": 14,
  "targetFestivals": ["Diwali", "Dhanteras"],
  "inventoryItems": [
    {
      "sku": "SKU001",
      "category": "sweets",
      "currentStock": 100,
      "safetyStock": 20,
      "unitCost": 10.0,
      "leadTimeDays": 7
    }
  ],
  "includeExplanations": true,
  "parallelExecution": true
}
```

**Response:**
```json
{
  "success": true,
  "userId": "user123",
  "dataMode": {
    "mode": "structured",
    "hasStructuredData": true,
    "quality": "good",
    "score": 0.9
  },
  "forecast": {
    "forecasts": [...],
    "metadata": {...}
  },
  "risks": {
    "results": [...],
    "successCount": 1
  },
  "explanations": {
    "forecast": {...},
    "risk": {...}
  },
  "metadata": {
    "processingTime": 12.5,
    "timestamp": "2024-01-15T10:00:00Z",
    "parallelExecution": true,
    "forecastHorizon": 14,
    "performanceTarget": 30.0,
    "meetsPerformanceTarget": true
  }
}
```

### 2. data_upload

Processes data uploads (CSV files or questionnaires).

**Request:**
```json
{
  "action": "data_upload",
  "userId": "user123",
  "dataType": "csv",
  "dataPayload": {
    "fileContent": "date,sku,quantity\n2024-01-01,SKU001,100",
    "fileName": "sales.csv"
  }
}
```

**Response:**
```json
{
  "success": true,
  "recordsProcessed": 100,
  "validationErrors": []
}
```

### 3. explanation

Generates AI-powered explanations for forecasts, risks, or conversational queries.

**Request:**
```json
{
  "action": "explanation",
  "userId": "user123",
  "context": "forecast",
  "sku": "SKU001"
}
```

**Response:**
```json
{
  "success": true,
  "explanation": {
    "explanation": "Based on historical data...",
    "keyInsights": [...],
    "assumptions": [...],
    "limitations": [...],
    "confidence": "High",
    "nextSteps": [...]
  }
}
```

## Performance Optimization

The orchestrator implements several strategies to meet the 30-second performance requirement (Requirement 6.1):

1. **Parallel Execution**: Forecast and risk assessments run concurrently using ThreadPoolExecutor
2. **Early Data Routing**: Data mode determination happens once at the start
3. **Conditional Processing**: Explanations are optional and only generated when requested
4. **Performance Monitoring**: Processing time is tracked and logged
5. **Performance Warnings**: Logs warnings when processing exceeds 30-second target

## Data Source Prioritization

The orchestrator implements Requirement 1.4 by prioritizing structured data over manual estimates:

```python
def determine_data_mode(user_id: str) -> Dict[str, Any]:
    """
    Determine data availability and quality for routing decisions.
    
    Returns:
        - mode: 'structured' or 'low-data'
        - hasStructuredData: boolean
        - quality: 'poor', 'fair', or 'good'
        - score: 0.0 to 1.0
    """
```

The data mode determination:
1. Checks user profile for historical data availability
2. Assesses data quality using the data prioritization module
3. Selects structured data when quality score >= 0.6
4. Falls back to low-data mode for poor quality or missing data

## Error Handling

The orchestrator implements graceful error handling:

- **Component Failures**: Individual component failures don't stop the entire workflow
- **Partial Results**: Returns partial results when some components succeed
- **Clear Error Messages**: Provides specific error information for debugging
- **CORS Support**: All responses include CORS headers for frontend integration

## Integration with Other Components

### Data Processor
- `process_csv_upload()`: Handles CSV file uploads
- `process_questionnaire()`: Processes low-data mode questionnaires
- `select_data_source()`: Determines data source priority

### Forecast Engine
- `generate_forecast()`: Generates demand predictions
- `get_latest_forecast_for_sku()`: Retrieves stored forecasts

### Risk Assessor
- `assess_multiple_skus()`: Calculates risks for multiple items
- `get_latest_risk_for_sku()`: Retrieves stored risk assessments

### AI Explainer
- `generate_explanation()`: Creates natural language explanations
- `generate_conversational_response()`: Handles conversational queries

## Testing

The orchestrator has comprehensive unit test coverage (77%):

- Data mode determination tests
- Workflow orchestration tests
- Parallel processing tests
- Error handling tests
- Lambda handler tests
- CORS header tests

Run tests:
```bash
pytest tests/test_orchestrator.py -v
```

## Deployment

The orchestrator Lambda is deployed via AWS CDK as part of the VyaparSaathi stack:

```typescript
const orchestratorLambda = new lambda.Function(this, 'OrchestratorFunction', {
  functionName: 'VyaparSaathi-Orchestrator',
  runtime: lambda.Runtime.PYTHON_3_11,
  handler: 'orchestrator_handler.lambda_handler',
  timeout: cdk.Duration.seconds(30),
  memorySize: 2048,
  environment: {
    USER_PROFILE_TABLE: userProfileTable.tableName,
    FORECASTS_TABLE: forecastsTable.tableName,
    // ... other environment variables
  }
});
```

## Environment Variables

Required environment variables:

- `USER_PROFILE_TABLE`: DynamoDB table for user profiles
- `FORECASTS_TABLE`: DynamoDB table for forecast results
- `PROCESSED_DATA_BUCKET`: S3 bucket for processed data
- `FESTIVAL_CALENDAR_TABLE`: DynamoDB table for festival data

## Monitoring

Key metrics to monitor:

- **Processing Time**: Should be < 30 seconds (Requirement 6.1)
- **Success Rate**: Percentage of successful orchestrations
- **Component Failures**: Track which components fail most often
- **Data Mode Distribution**: Ratio of structured vs low-data mode usage

CloudWatch alarms are configured for:
- Processing time exceeding 25 seconds (buffer before 30s limit)
- Error rate exceeding threshold
- Throttling events

## Future Enhancements

Potential improvements:

1. **Caching**: Cache forecast results for frequently accessed SKUs
2. **Batch Processing**: Support batch operations for multiple users
3. **Async Processing**: Use Step Functions for long-running workflows
4. **Circuit Breaker**: Implement circuit breaker pattern for component failures
5. **Rate Limiting**: Add per-user rate limiting for API protection
