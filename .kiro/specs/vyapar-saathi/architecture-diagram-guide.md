# VyaparSaathi Architecture Diagram Guide for draw.io

## Quick Start
1. Go to https://app.diagrams.net/
2. Create a new diagram
3. Enable AWS icon library:
   - Click "More Shapes" (bottom left, or + icon in the shapes panel)
   - In the search box, type "AWS"
   - Check the box for **"AWS 2026"** (recommended - latest version)
     - Or use "AWS 18" or "AWS 17" if 2026 isn't available
   - Click "Apply"
4. The AWS shapes will now appear in your left sidebar
5. Use the search box in the shapes panel to find specific services
6. Follow the structure below

## Diagram Layout (Top to Bottom)

### Layer 1: Users & Frontend
**Components:**
- User icon (Search in shapes for "user" or use General category)
- Web Application box (AWS → Mobile → Amplify, or AWS → Compute → Lambda)
- Mobile Interface box (AWS → Mobile → Amplify)

**Alternative if Amplify not found:**
- Use generic rectangles with AWS orange color (#FF9900)
- Add text labels manually

**Labels:**
- "MSME Retailers" for user
- "Web Application" and "Mobile Interface"

**Connections:**
- User → Web Application
- User → Mobile Interface

---

### Layer 2: API Gateway & Authentication
**Components:**
- API Gateway (AWS → Network → API Gateway, or search "API Gateway")
- Cognito User Pool (AWS → Security → Cognito, or search "Cognito")

**How to find icons:**
- In the AWS shapes panel on the left, expand categories
- Or use the search box at the top of the shapes panel
- Type the service name (e.g., "API Gateway", "Cognito")

**Labels:**
- "API Gateway"
- "User Authentication"

**Connections:**
- Web Application → API Gateway
- Mobile Interface → API Gateway
- API Gateway → Cognito (bidirectional)

---

### Layer 3: Core Processing Layer (Lambda Functions)
**Create a container/group labeled "Core Processing Layer"**

**Components (5 Lambda functions):**
- Search for "Lambda" in the AWS shapes panel
- Drag 5 Lambda icons into your diagram
- Lambda icons typically look like orange/yellow function symbols

**Label each Lambda:**
1. "Orchestrator"
2. "Data Processor"
3. "Forecast Engine"
4. "Risk Assessor"
5. "AI Explainer"

**Connections:**
- API Gateway → Orchestrator
- Orchestrator → Data Processor
- Orchestrator → Forecast Engine
- Orchestrator → Risk Assessor
- Orchestrator → AI Explainer

---

### Layer 4: AI & ML Services
**Create a container/group labeled "AI & ML Services"**

**Components:**
- Amazon Bedrock (Search "Bedrock" in AWS shapes)
  - Label: "Amazon Bedrock\n(AI Explanations)"
  - If not found, use a purple rectangle with AWS ML icon
- Amazon Forecast (Search "Forecast" in AWS shapes)
  - Label: "Amazon Forecast\n(Demand Prediction)"
  - If not found, use a purple rectangle with chart icon

**Tip:** ML/AI services are usually in purple/pink colors in AWS icons

**Connections:**
- AI Explainer → Bedrock
- Forecast Engine → Amazon Forecast

---

### Layer 5: Data Storage Layer
**Create a container/group labeled "Data Storage"**

**Components:**
- S3: Raw Data (Search "S3" - green bucket icon)
  - Label: "Raw Sales Data"
- S3: Processed Data (Use another S3 icon)
  - Label: "Processed Data"
- DynamoDB: User Data (Search "DynamoDB" - blue database icon)
  - Label: "User Profiles"
- DynamoDB: Forecasts (Use another DynamoDB icon)
  - Label: "Forecast Results"
- DynamoDB: Festivals (Use another DynamoDB icon)
  - Label: "Festival Calendar"

**Tip:** 
- S3 icons are typically green with a bucket symbol
- DynamoDB icons are typically blue with database/table symbols

**Connections:**
- Data Processor → S3 Raw Data
- Data Processor → S3 Processed Data
- Data Processor → DynamoDB User Data
- Forecast Engine → DynamoDB Forecasts
- Forecast Engine → DynamoDB Festivals
- Risk Assessor → DynamoDB Forecasts
- Risk Assessor → DynamoDB User Data

---

### Layer 6: External Data Sources
**Create a container/group labeled "External Data"**

**Components:**
- Festival Calendar API (Use API Gateway icon or generic cloud icon)
- Synthetic Data Generator (Use Lambda icon)

**Connections:**
- Festival Calendar API → DynamoDB Festivals
- Synthetic Data Generator → S3 Processed Data

---

## Finding AWS Icons - Troubleshooting

If you can't find specific AWS icons:

1. **Search Method (BEST):**
   - Use the search box at the top of the shapes panel (left sidebar)
   - Type the service name (Lambda, S3, DynamoDB, Bedrock, etc.)
   - Icons should appear immediately
   - Drag and drop into your canvas

2. **Browse by Category:**
   - After enabling AWS 2026, expand the AWS categories in the left panel
   - Categories: Compute, Storage, Database, ML, Network, Security, etc.
   - Scroll through to find your service

3. **Alternative Libraries:**
   - AWS 2026 is the newest (recommended)
   - AWS 18 has most modern services
   - AWS 17 is older but still comprehensive

4. **Manual Icon Method:**
   - Download official AWS icons from: https://aws.amazon.com/architecture/icons/
   - In draw.io: File → Import → Select downloaded SVG files
   - Drag imported icons into your diagram

5. **Generic Shapes Fallback:**
   - Use colored rectangles with text labels
   - AWS color scheme:
     - Orange (#FF9900) for compute/Lambda
     - Green (#3F8624) for storage/S3
     - Blue (#527FFF) for database/DynamoDB
     - Purple (#B07FD6) for AI/ML services

---

## Styling Tips

### Colors
- **Frontend Layer**: Light blue background (#E3F2FD)
- **API & Auth**: Light green background (#E8F5E9)
- **Processing Layer**: Light orange background (#FFF3E0)
- **AI/ML Services**: Light purple background (#F3E5F5)
- **Data Storage**: Light yellow background (#FFFDE7)
- **External Data**: Light gray background (#F5F5F5)

### Arrows
- Use solid arrows for primary data flow
- Use dashed arrows for external/async operations
- Add labels on arrows for important flows:
  - "Upload CSV" (User → Web)
  - "Authenticate" (API Gateway → Cognito)
  - "Process Request" (API Gateway → Orchestrator)
  - "Generate Explanation" (AI Explainer → Bedrock)

### Container Styling
- Use rounded rectangles for containers
- Add drop shadows for depth
- Use bold text for container titles

---

## Alternative: Using AWS Architecture Icons

If you prefer official AWS styling:

1. Download AWS Architecture Icons: https://aws.amazon.com/architecture/icons/
2. Use PowerPoint, Visio, or draw.io
3. Follow the same structure above
4. Use official AWS colors and styling guidelines

---

## Key Data Flows to Highlight

### Flow 1: Data Upload (Structured Mode)
User → Web App → API Gateway → Orchestrator → Data Processor → S3 Raw → S3 Processed → DynamoDB

### Flow 2: Forecast Generation
Orchestrator → Forecast Engine → Amazon Forecast → DynamoDB Forecasts

### Flow 3: Low-Data Mode
User → Questionnaire → Data Processor → Synthetic Data Generator → S3 Processed → Forecast Engine

### Flow 4: Risk Assessment
Forecast Engine → DynamoDB Forecasts → Risk Assessor → DynamoDB User Data

### Flow 5: AI Explanation
Risk Assessor → AI Explainer → Amazon Bedrock → User (via API Gateway)

---

## Quick Reference: AWS Service Icons Needed

| Service | Search Term | Icon Color | Description |
|---------|-------------|------------|-------------|
| User | "user" | Red/Orange | Person icon |
| Amplify | "amplify" | Orange | Mobile/web hosting |
| API Gateway | "api gateway" | Purple | API management |
| Cognito | "cognito" | Pink/Red | Authentication |
| Lambda | "lambda" | Orange | Serverless compute |
| Bedrock | "bedrock" | Purple | AI/ML service |
| Forecast | "forecast" | Purple | ML forecasting |
| S3 | "s3" | Green | Object storage |
| DynamoDB | "dynamodb" | Blue | NoSQL database |

**Pro Tip:** If an icon doesn't exist (like Bedrock in older libraries), use a similar ML service icon or a generic purple rectangle.

---

## Pro Tips

1. **Alignment**: Use draw.io's alignment tools (Arrange → Align) to keep everything neat
2. **Spacing**: Maintain consistent spacing between layers (50-80px)
3. **Labels**: Keep labels concise but descriptive
4. **Legend**: Add a legend explaining arrow types if using multiple styles
5. **Export**: Export as PNG (high resolution) or SVG for documentation

---

## Estimated Time
- Basic structure: 15-20 minutes
- With styling and labels: 30-40 minutes
- Professional polish: 45-60 minutes
