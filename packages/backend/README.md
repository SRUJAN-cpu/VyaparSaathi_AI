# VyaparSaathi Backend

Python Lambda functions for the VyaparSaathi festival demand forecasting platform.

## Setup

Create and activate virtual environment:

```bash
make setup
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

## Development

### Running Tests

```bash
make test
```

### Linting

```bash
make lint
```

### Formatting

```bash
make format
```

## Project Structure

```
src/
  ├── orchestrator/       # Main orchestration Lambda
  ├── data_processor/     # Data validation and processing
  ├── forecast_engine/    # Demand forecasting logic
  ├── risk_assessor/      # Risk calculation
  └── ai_explainer/       # AI-powered explanations
```
