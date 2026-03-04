# VyaparSaathi Frontend Setup Script (PowerShell)
# This script helps configure the frontend environment

$ErrorActionPreference = "Stop"

Write-Host "🚀 VyaparSaathi Frontend Setup" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env already exists
if (Test-Path .env) {
    Write-Host "⚠️  .env file already exists!" -ForegroundColor Yellow
    $overwrite = Read-Host "Do you want to overwrite it? (y/N)"
    if ($overwrite -ne "y" -and $overwrite -ne "Y") {
        Write-Host "Setup cancelled. Existing .env file preserved." -ForegroundColor Yellow
        exit 0
    }
}

# Copy .env.example to .env
if (-not (Test-Path .env.example)) {
    Write-Host "❌ Error: .env.example not found!" -ForegroundColor Red
    exit 1
}

Copy-Item .env.example .env
Write-Host "✅ Created .env file from .env.example" -ForegroundColor Green
Write-Host ""

# Check if infrastructure outputs exist
$infraDir = "..\..\infrastructure"
$outputsFile = "$infraDir\outputs.json"

if (Test-Path $outputsFile) {
    Write-Host "📦 Found infrastructure outputs file" -ForegroundColor Cyan
    Write-Host "Attempting to auto-configure from CDK outputs..." -ForegroundColor Cyan
    Write-Host ""
    
    try {
        $outputs = Get-Content $outputsFile | ConvertFrom-Json
        $stack = $outputs.VyaparSaathiStack
        
        if ($stack.UserPoolId) {
            (Get-Content .env) -replace 'VITE_USER_POOL_ID=.*', "VITE_USER_POOL_ID=$($stack.UserPoolId)" | Set-Content .env
            Write-Host "✅ Set VITE_USER_POOL_ID=$($stack.UserPoolId)" -ForegroundColor Green
        }
        
        if ($stack.UserPoolClientId) {
            (Get-Content .env) -replace 'VITE_USER_POOL_CLIENT_ID=.*', "VITE_USER_POOL_CLIENT_ID=$($stack.UserPoolClientId)" | Set-Content .env
            Write-Host "✅ Set VITE_USER_POOL_CLIENT_ID=$($stack.UserPoolClientId)" -ForegroundColor Green
        }
        
        if ($stack.ApiEndpoint) {
            (Get-Content .env) -replace 'VITE_API_ENDPOINT=.*', "VITE_API_ENDPOINT=$($stack.ApiEndpoint)" | Set-Content .env
            Write-Host "✅ Set VITE_API_ENDPOINT=$($stack.ApiEndpoint)" -ForegroundColor Green
        }
        
        Write-Host ""
        Write-Host "✅ Auto-configuration complete!" -ForegroundColor Green
    }
    catch {
        Write-Host "⚠️  Failed to parse outputs.json. Skipping auto-configuration." -ForegroundColor Yellow
    }
}
else {
    Write-Host "⚠️  Infrastructure outputs not found at $outputsFile" -ForegroundColor Yellow
    Write-Host "Please deploy infrastructure first or manually configure .env" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📝 Configuration Summary" -ForegroundColor Cyan
Write-Host "========================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Please verify your .env file contains:"
Write-Host "  - VITE_USER_POOL_ID (from Cognito User Pool)"
Write-Host "  - VITE_USER_POOL_CLIENT_ID (from Cognito App Client)"
Write-Host "  - VITE_API_ENDPOINT (from API Gateway)"
Write-Host "  - VITE_AWS_REGION (default: us-east-1)"
Write-Host ""

# Prompt for manual configuration if needed
$manualConfig = Read-Host "Do you want to manually enter configuration values now? (y/N)"
if ($manualConfig -eq "y" -or $manualConfig -eq "Y") {
    Write-Host ""
    Write-Host "Enter configuration values (press Enter to skip):"
    Write-Host ""
    
    $userPoolId = Read-Host "User Pool ID"
    if ($userPoolId) {
        (Get-Content .env) -replace 'VITE_USER_POOL_ID=.*', "VITE_USER_POOL_ID=$userPoolId" | Set-Content .env
    }
    
    $userPoolClientId = Read-Host "User Pool Client ID"
    if ($userPoolClientId) {
        (Get-Content .env) -replace 'VITE_USER_POOL_CLIENT_ID=.*', "VITE_USER_POOL_CLIENT_ID=$userPoolClientId" | Set-Content .env
    }
    
    $apiEndpoint = Read-Host "API Endpoint"
    if ($apiEndpoint) {
        (Get-Content .env) -replace 'VITE_API_ENDPOINT=.*', "VITE_API_ENDPOINT=$apiEndpoint" | Set-Content .env
    }
    
    $awsRegion = Read-Host "AWS Region (default: us-east-1)"
    if ($awsRegion) {
        (Get-Content .env) -replace 'VITE_AWS_REGION=.*', "VITE_AWS_REGION=$awsRegion" | Set-Content .env
    }
    
    Write-Host ""
    Write-Host "✅ Manual configuration complete!" -ForegroundColor Green
}

Write-Host ""
Write-Host "🎉 Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Review .env file: Get-Content .env"
Write-Host "  2. Install dependencies: npm install"
Write-Host "  3. Start development server: npm run dev"
Write-Host ""
Write-Host "For more information, see DEPLOYMENT.md"
