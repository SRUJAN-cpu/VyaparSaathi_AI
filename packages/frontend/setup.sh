#!/bin/bash

# VyaparSaathi Frontend Setup Script
# This script helps configure the frontend environment

set -e

echo "🚀 VyaparSaathi Frontend Setup"
echo "================================"
echo ""

# Check if .env already exists
if [ -f .env ]; then
    echo "⚠️  .env file already exists!"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup cancelled. Existing .env file preserved."
        exit 0
    fi
fi

# Copy .env.example to .env
if [ ! -f .env.example ]; then
    echo "❌ Error: .env.example not found!"
    exit 1
fi

cp .env.example .env
echo "✅ Created .env file from .env.example"
echo ""

# Check if infrastructure outputs exist
INFRA_DIR="../../infrastructure"
OUTPUTS_FILE="$INFRA_DIR/outputs.json"

if [ -f "$OUTPUTS_FILE" ]; then
    echo "📦 Found infrastructure outputs file"
    echo "Attempting to auto-configure from CDK outputs..."
    echo ""
    
    # Extract values using jq if available
    if command -v jq &> /dev/null; then
        USER_POOL_ID=$(jq -r '.VyaparSaathiStack.UserPoolId // empty' "$OUTPUTS_FILE")
        USER_POOL_CLIENT_ID=$(jq -r '.VyaparSaathiStack.UserPoolClientId // empty' "$OUTPUTS_FILE")
        API_ENDPOINT=$(jq -r '.VyaparSaathiStack.ApiEndpoint // empty' "$OUTPUTS_FILE")
        
        if [ -n "$USER_POOL_ID" ]; then
            sed -i.bak "s|VITE_USER_POOL_ID=.*|VITE_USER_POOL_ID=$USER_POOL_ID|" .env
            echo "✅ Set VITE_USER_POOL_ID=$USER_POOL_ID"
        fi
        
        if [ -n "$USER_POOL_CLIENT_ID" ]; then
            sed -i.bak "s|VITE_USER_POOL_CLIENT_ID=.*|VITE_USER_POOL_CLIENT_ID=$USER_POOL_CLIENT_ID|" .env
            echo "✅ Set VITE_USER_POOL_CLIENT_ID=$USER_POOL_CLIENT_ID"
        fi
        
        if [ -n "$API_ENDPOINT" ]; then
            sed -i.bak "s|VITE_API_ENDPOINT=.*|VITE_API_ENDPOINT=$API_ENDPOINT|" .env
            echo "✅ Set VITE_API_ENDPOINT=$API_ENDPOINT"
        fi
        
        rm -f .env.bak
        echo ""
        echo "✅ Auto-configuration complete!"
    else
        echo "⚠️  jq not installed. Skipping auto-configuration."
        echo "Install jq for automatic configuration: brew install jq (macOS) or apt-get install jq (Linux)"
    fi
else
    echo "⚠️  Infrastructure outputs not found at $OUTPUTS_FILE"
    echo "Please deploy infrastructure first or manually configure .env"
fi

echo ""
echo "📝 Configuration Summary"
echo "========================"
echo ""
echo "Please verify your .env file contains:"
echo "  - VITE_USER_POOL_ID (from Cognito User Pool)"
echo "  - VITE_USER_POOL_CLIENT_ID (from Cognito App Client)"
echo "  - VITE_API_ENDPOINT (from API Gateway)"
echo "  - VITE_AWS_REGION (default: us-east-1)"
echo ""

# Prompt for manual configuration if needed
read -p "Do you want to manually enter configuration values now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Enter configuration values (press Enter to skip):"
    echo ""
    
    read -p "User Pool ID: " USER_POOL_ID
    if [ -n "$USER_POOL_ID" ]; then
        sed -i.bak "s|VITE_USER_POOL_ID=.*|VITE_USER_POOL_ID=$USER_POOL_ID|" .env
    fi
    
    read -p "User Pool Client ID: " USER_POOL_CLIENT_ID
    if [ -n "$USER_POOL_CLIENT_ID" ]; then
        sed -i.bak "s|VITE_USER_POOL_CLIENT_ID=.*|VITE_USER_POOL_CLIENT_ID=$USER_POOL_CLIENT_ID|" .env
    fi
    
    read -p "API Endpoint: " API_ENDPOINT
    if [ -n "$API_ENDPOINT" ]; then
        sed -i.bak "s|VITE_API_ENDPOINT=.*|VITE_API_ENDPOINT=$API_ENDPOINT|" .env
    fi
    
    read -p "AWS Region (default: us-east-1): " AWS_REGION
    if [ -n "$AWS_REGION" ]; then
        sed -i.bak "s|VITE_AWS_REGION=.*|VITE_AWS_REGION=$AWS_REGION|" .env
    fi
    
    rm -f .env.bak
    echo ""
    echo "✅ Manual configuration complete!"
fi

echo ""
echo "🎉 Setup Complete!"
echo ""
echo "Next steps:"
echo "  1. Review .env file: cat .env"
echo "  2. Install dependencies: npm install"
echo "  3. Start development server: npm run dev"
echo ""
echo "For more information, see DEPLOYMENT.md"
