#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { VyaparSaathiStack } from '../lib/vyapar-saathi-stack';

const app = new cdk.App();

new VyaparSaathiStack(app, 'VyaparSaathiStack', {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION,
  },
  description: 'VyaparSaathi - Festival Demand Forecasting Platform',
});
