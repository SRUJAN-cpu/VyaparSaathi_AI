#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { VyaparSaathiStack } from '../lib/vyapar-saathi-stack';

const app = new cdk.App();

// Create the VyaparSaathi stack
new VyaparSaathiStack(app, 'VyaparSaathiStack', {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION || 'us-east-1',
  },
  description: 'VyaparSaathi - Festival Demand & Inventory Risk Forecasting Platform',
  tags: {
    Project: 'VyaparSaathi',
    Environment: 'Production',
    ManagedBy: 'CDK',
  },
});

app.synth();
