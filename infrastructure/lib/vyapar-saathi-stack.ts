import * as cdk from 'aws-cdk-lib';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as cognito from 'aws-cdk-lib/aws-cognito';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as logs from 'aws-cdk-lib/aws-logs';
import { Construct } from 'constructs';

export class VyaparSaathiStack extends cdk.Stack {
  public readonly userProfileTable: dynamodb.Table;
  public readonly forecastsTable: dynamodb.Table;
  public readonly festivalCalendarTable: dynamodb.Table;
  public readonly rawDataBucket: s3.Bucket;
  public readonly processedDataBucket: s3.Bucket;
  public readonly api: apigateway.RestApi;
  public readonly userPool: cognito.UserPool;
  public readonly userPoolClient: cognito.UserPoolClient;

  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // ===== DynamoDB Tables (Task 2.1) =====
    
    // UserProfile Table with GSI for location queries
    this.userProfileTable = new dynamodb.Table(this, 'UserProfileTable', {
      tableName: 'VyaparSaathi-UserProfiles',
      partitionKey: {
        name: 'userId',
        type: dynamodb.AttributeType.STRING,
      },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST, // On-demand billing
      encryption: dynamodb.TableEncryption.AWS_MANAGED,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
      pointInTimeRecovery: true,
    });

    // GSI for location-based queries
    this.userProfileTable.addGlobalSecondaryIndex({
      indexName: 'LocationIndex',
      partitionKey: {
        name: 'region',
        type: dynamodb.AttributeType.STRING,
      },
      sortKey: {
        name: 'city',
        type: dynamodb.AttributeType.STRING,
      },
      projectionType: dynamodb.ProjectionType.ALL,
    });

    // Forecasts Table with TTL and GSI for date queries
    this.forecastsTable = new dynamodb.Table(this, 'ForecastsTable', {
      tableName: 'VyaparSaathi-Forecasts',
      partitionKey: {
        name: 'userId',
        type: dynamodb.AttributeType.STRING,
      },
      sortKey: {
        name: 'sku',
        type: dynamodb.AttributeType.STRING,
      },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST, // On-demand billing
      encryption: dynamodb.TableEncryption.AWS_MANAGED,
      timeToLiveAttribute: 'ttl', // TTL attribute for automatic expiration
      removalPolicy: cdk.RemovalPolicy.RETAIN,
      pointInTimeRecovery: true,
    });

    // GSI for date-based queries
    this.forecastsTable.addGlobalSecondaryIndex({
      indexName: 'DateIndex',
      partitionKey: {
        name: 'userId',
        type: dynamodb.AttributeType.STRING,
      },
      sortKey: {
        name: 'forecastDate',
        type: dynamodb.AttributeType.STRING,
      },
      projectionType: dynamodb.ProjectionType.ALL,
    });

    // FestivalCalendar Table with GSI for region and date queries
    this.festivalCalendarTable = new dynamodb.Table(this, 'FestivalCalendarTable', {
      tableName: 'VyaparSaathi-FestivalCalendar',
      partitionKey: {
        name: 'festivalId',
        type: dynamodb.AttributeType.STRING,
      },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST, // On-demand billing
      encryption: dynamodb.TableEncryption.AWS_MANAGED,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
      pointInTimeRecovery: true,
    });

    // GSI for region-based queries
    this.festivalCalendarTable.addGlobalSecondaryIndex({
      indexName: 'RegionIndex',
      partitionKey: {
        name: 'region',
        type: dynamodb.AttributeType.STRING,
      },
      sortKey: {
        name: 'date',
        type: dynamodb.AttributeType.STRING,
      },
      projectionType: dynamodb.ProjectionType.ALL,
    });

    // GSI for date-based queries across all regions
    this.festivalCalendarTable.addGlobalSecondaryIndex({
      indexName: 'DateIndex',
      partitionKey: {
        name: 'date',
        type: dynamodb.AttributeType.STRING,
      },
      projectionType: dynamodb.ProjectionType.ALL,
    });

    // Output table names
    new cdk.CfnOutput(this, 'UserProfileTableName', {
      value: this.userProfileTable.tableName,
      description: 'DynamoDB UserProfile table name',
    });

    new cdk.CfnOutput(this, 'ForecastsTableName', {
      value: this.forecastsTable.tableName,
      description: 'DynamoDB Forecasts table name',
    });

    new cdk.CfnOutput(this, 'FestivalCalendarTableName', {
      value: this.festivalCalendarTable.tableName,
      description: 'DynamoDB FestivalCalendar table name',
    });

    // ===== S3 Buckets (Task 2.2) =====
    
    // Raw Data Bucket with encryption and lifecycle policies
    this.rawDataBucket = new s3.Bucket(this, 'RawDataBucket', {
      bucketName: `vyapar-saathi-raw-data-${this.account}`,
      encryption: s3.BucketEncryption.S3_MANAGED, // SSE-S3
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      versioned: true,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
      lifecycleRules: [
        {
          id: 'TransitionToGlacier',
          enabled: true,
          transitions: [
            {
              storageClass: s3.StorageClass.GLACIER,
              transitionAfter: cdk.Duration.days(90),
            },
          ],
        },
        {
          id: 'DeleteOldData',
          enabled: true,
          expiration: cdk.Duration.days(365),
        },
      ],
      cors: [
        {
          allowedMethods: [
            s3.HttpMethods.GET,
            s3.HttpMethods.PUT,
            s3.HttpMethods.POST,
          ],
          allowedOrigins: ['*'], // Should be restricted to frontend domain in production
          allowedHeaders: ['*'],
          maxAge: 3000,
        },
      ],
    });

    // Processed Data Bucket with encryption and lifecycle policies
    this.processedDataBucket = new s3.Bucket(this, 'ProcessedDataBucket', {
      bucketName: `vyapar-saathi-processed-data-${this.account}`,
      encryption: s3.BucketEncryption.S3_MANAGED, // SSE-S3
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      versioned: true,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
      lifecycleRules: [
        {
          id: 'TransitionToGlacier',
          enabled: true,
          transitions: [
            {
              storageClass: s3.StorageClass.GLACIER,
              transitionAfter: cdk.Duration.days(90),
            },
          ],
        },
        {
          id: 'DeleteOldData',
          enabled: true,
          expiration: cdk.Duration.days(365),
        },
      ],
    });

    // Bucket policies for least-privilege access
    const rawDataBucketPolicy = new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      principals: [new iam.ServicePrincipal('lambda.amazonaws.com')],
      actions: ['s3:GetObject', 's3:PutObject'],
      resources: [`${this.rawDataBucket.bucketArn}/*`],
    });

    const processedDataBucketPolicy = new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      principals: [new iam.ServicePrincipal('lambda.amazonaws.com')],
      actions: ['s3:GetObject', 's3:PutObject'],
      resources: [`${this.processedDataBucket.bucketArn}/*`],
    });

    this.rawDataBucket.addToResourcePolicy(rawDataBucketPolicy);
    this.processedDataBucket.addToResourcePolicy(processedDataBucketPolicy);

    // Output bucket names
    new cdk.CfnOutput(this, 'RawDataBucketName', {
      value: this.rawDataBucket.bucketName,
      description: 'S3 Raw Data bucket name',
    });

    new cdk.CfnOutput(this, 'ProcessedDataBucketName', {
      value: this.processedDataBucket.bucketName,
      description: 'S3 Processed Data bucket name',
    });

    // ===== Lambda Functions (Placeholder for Task 2.3) =====
    
    // Create placeholder Lambda functions for API Gateway integrations
    // These will be implemented in later tasks
    
    const dataUploadLambda = new lambda.Function(this, 'DataUploadFunction', {
      functionName: 'VyaparSaathi-DataUpload',
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: 'index.handler',
      code: lambda.Code.fromInline(`
def handler(event, context):
    return {
        'statusCode': 200,
        'body': '{"message": "Data upload endpoint - to be implemented"}'
    }
      `),
      timeout: cdk.Duration.seconds(30),
      memorySize: 1024, // Increased for CSV processing
      environment: {
        USER_PROFILE_TABLE: this.userProfileTable.tableName,
        RAW_DATA_BUCKET: this.rawDataBucket.bucketName,
        PROCESSED_DATA_BUCKET: this.processedDataBucket.bucketName,
      },
    });

    const forecastLambda = new lambda.Function(this, 'ForecastFunction', {
      functionName: 'VyaparSaathi-Forecast',
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: 'index.handler',
      code: lambda.Code.fromInline(`
def handler(event, context):
    return {
        'statusCode': 200,
        'body': '{"message": "Forecast endpoint - to be implemented"}'
    }
      `),
      timeout: cdk.Duration.seconds(30),
      memorySize: 2048, // Increased for ML forecasting
      environment: {
        FORECASTS_TABLE: this.forecastsTable.tableName,
        FESTIVAL_CALENDAR_TABLE: this.festivalCalendarTable.tableName,
        PROCESSED_DATA_BUCKET: this.processedDataBucket.bucketName,
      },
    });

    const riskAssessmentLambda = new lambda.Function(this, 'RiskAssessmentFunction', {
      functionName: 'VyaparSaathi-RiskAssessment',
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: 'index.handler',
      code: lambda.Code.fromInline(`
def handler(event, context):
    return {
        'statusCode': 200,
        'body': '{"message": "Risk assessment endpoint - to be implemented"}'
    }
      `),
      timeout: cdk.Duration.seconds(30),
      memorySize: 1024, // Increased for risk calculations
      environment: {
        FORECASTS_TABLE: this.forecastsTable.tableName,
        USER_PROFILE_TABLE: this.userProfileTable.tableName,
      },
    });

    const explanationLambda = new lambda.Function(this, 'ExplanationFunction', {
      functionName: 'VyaparSaathi-Explanation',
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: 'index.handler',
      code: lambda.Code.fromInline(`
def handler(event, context):
    return {
        'statusCode': 200,
        'body': '{"message": "AI explanation endpoint - to be implemented"}'
    }
      `),
      timeout: cdk.Duration.seconds(30),
      memorySize: 1536, // Increased for Bedrock API calls
      environment: {
        FORECASTS_TABLE: this.forecastsTable.tableName,
      },
    });

    // Grant Lambda functions permissions to access DynamoDB tables and S3 buckets
    this.userProfileTable.grantReadWriteData(dataUploadLambda);
    this.userProfileTable.grantReadData(riskAssessmentLambda);
    this.forecastsTable.grantReadWriteData(forecastLambda);
    this.forecastsTable.grantReadData(riskAssessmentLambda);
    this.forecastsTable.grantReadData(explanationLambda);
    this.festivalCalendarTable.grantReadData(forecastLambda);
    this.rawDataBucket.grantReadWrite(dataUploadLambda);
    this.processedDataBucket.grantReadWrite(dataUploadLambda);
    this.processedDataBucket.grantRead(forecastLambda);

    // Grant Bedrock permissions to explanation Lambda
    explanationLambda.addToRolePolicy(
      new iam.PolicyStatement({
        effect: iam.Effect.ALLOW,
        actions: ['bedrock:InvokeModel'],
        resources: ['*'],
      })
    );

    // Grant CloudWatch permissions to all Lambda functions for custom metrics
    const cloudwatchPolicy = new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: ['cloudwatch:PutMetricData'],
      resources: ['*'],
    });

    dataUploadLambda.addToRolePolicy(cloudwatchPolicy);
    forecastLambda.addToRolePolicy(cloudwatchPolicy);
    riskAssessmentLambda.addToRolePolicy(cloudwatchPolicy);
    explanationLambda.addToRolePolicy(cloudwatchPolicy);

    // ===== CloudWatch Alarms for Performance Monitoring =====
    
    // Create alarms for Lambda execution time (30 second requirement)
    const forecastAlarm = forecastLambda.metricDuration().createAlarm(this, 'ForecastDurationAlarm', {
      alarmName: 'VyaparSaathi-Forecast-Duration-Alarm',
      alarmDescription: 'Alert when forecast generation exceeds 25 seconds',
      threshold: 25000, // 25 seconds (buffer before 30s limit)
      evaluationPeriods: 2,
      datapointsToAlarm: 2,
      treatMissingData: cdk.aws_cloudwatch.TreatMissingData.NOT_BREACHING,
    });

    const riskAlarm = riskAssessmentLambda.metricDuration().createAlarm(this, 'RiskDurationAlarm', {
      alarmName: 'VyaparSaathi-Risk-Duration-Alarm',
      alarmDescription: 'Alert when risk assessment exceeds 20 seconds',
      threshold: 20000, // 20 seconds
      evaluationPeriods: 2,
      datapointsToAlarm: 2,
      treatMissingData: cdk.aws_cloudwatch.TreatMissingData.NOT_BREACHING,
    });

    // Create alarms for Lambda errors
    const forecastErrorAlarm = forecastLambda.metricErrors().createAlarm(this, 'ForecastErrorAlarm', {
      alarmName: 'VyaparSaathi-Forecast-Error-Alarm',
      alarmDescription: 'Alert when forecast Lambda has errors',
      threshold: 5,
      evaluationPeriods: 1,
      treatMissingData: cdk.aws_cloudwatch.TreatMissingData.NOT_BREACHING,
    });

    // Output alarm ARNs
    new cdk.CfnOutput(this, 'ForecastDurationAlarmArn', {
      value: forecastAlarm.alarmArn,
      description: 'Forecast duration alarm ARN',
    });

    new cdk.CfnOutput(this, 'ForecastErrorAlarmArn', {
      value: forecastErrorAlarm.alarmArn,
      description: 'Forecast error alarm ARN',
    });

    // ===== API Gateway (Task 2.3) =====
    
    // Create CloudWatch Log Group for API Gateway
    const apiLogGroup = new logs.LogGroup(this, 'ApiGatewayLogGroup', {
      logGroupName: '/aws/apigateway/vyapar-saathi',
      retention: logs.RetentionDays.ONE_MONTH,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    // Create REST API
    this.api = new apigateway.RestApi(this, 'VyaparSaathiApi', {
      restApiName: 'VyaparSaathi API',
      description: 'API for VyaparSaathi festival demand forecasting platform',
      deployOptions: {
        stageName: 'prod',
        throttlingRateLimit: 100, // 100 requests per second
        throttlingBurstLimit: 200,
        loggingLevel: apigateway.MethodLoggingLevel.INFO,
        dataTraceEnabled: true,
        accessLogDestination: new apigateway.LogGroupLogDestination(apiLogGroup),
        accessLogFormat: apigateway.AccessLogFormat.jsonWithStandardFields(),
      },
      defaultCorsPreflightOptions: {
        allowOrigins: apigateway.Cors.ALL_ORIGINS, // Should be restricted in production
        allowMethods: apigateway.Cors.ALL_METHODS,
        allowHeaders: [
          'Content-Type',
          'X-Amz-Date',
          'Authorization',
          'X-Api-Key',
          'X-Amz-Security-Token',
        ],
      },
    });

    // Create request validators
    const requestValidator = new apigateway.RequestValidator(this, 'RequestValidator', {
      restApi: this.api,
      requestValidatorName: 'request-validator',
      validateRequestBody: true,
      validateRequestParameters: true,
    });

    // Create API resources
    const dataResource = this.api.root.addResource('data');
    const uploadResource = dataResource.addResource('upload');
    
    const forecastResource = this.api.root.addResource('forecast');
    
    const riskResource = this.api.root.addResource('risk');
    
    const explanationResource = this.api.root.addResource('explanation');

    // Create request/response models for validation
    const uploadRequestModel = this.api.addModel('UploadRequestModel', {
      contentType: 'application/json',
      modelName: 'UploadRequest',
      schema: {
        type: apigateway.JsonSchemaType.OBJECT,
        properties: {
          userId: { type: apigateway.JsonSchemaType.STRING },
          dataType: { 
            type: apigateway.JsonSchemaType.STRING,
            enum: ['csv', 'questionnaire'],
          },
        },
        required: ['userId', 'dataType'],
      },
    });

    const forecastRequestModel = this.api.addModel('ForecastRequestModel', {
      contentType: 'application/json',
      modelName: 'ForecastRequest',
      schema: {
        type: apigateway.JsonSchemaType.OBJECT,
        properties: {
          userId: { type: apigateway.JsonSchemaType.STRING },
          forecastHorizon: { type: apigateway.JsonSchemaType.INTEGER },
          targetFestivals: {
            type: apigateway.JsonSchemaType.ARRAY,
            items: { type: apigateway.JsonSchemaType.STRING },
          },
        },
        required: ['userId', 'forecastHorizon'],
      },
    });

    // Add Lambda integrations with request validation
    uploadResource.addMethod(
      'POST',
      new apigateway.LambdaIntegration(dataUploadLambda),
      {
        requestValidator,
        requestModels: {
          'application/json': uploadRequestModel,
        },
      }
    );

    forecastResource.addMethod(
      'POST',
      new apigateway.LambdaIntegration(forecastLambda),
      {
        requestValidator,
        requestModels: {
          'application/json': forecastRequestModel,
        },
      }
    );

    riskResource.addMethod(
      'POST',
      new apigateway.LambdaIntegration(riskAssessmentLambda)
    );

    explanationResource.addMethod(
      'POST',
      new apigateway.LambdaIntegration(explanationLambda)
    );

    // Add usage plan for rate limiting per user
    const usagePlan = this.api.addUsagePlan('UsagePlan', {
      name: 'VyaparSaathi-UsagePlan',
      throttle: {
        rateLimit: 100, // 100 requests per minute per user
        burstLimit: 200,
      },
      quota: {
        limit: 10000,
        period: apigateway.Period.MONTH,
      },
    });

    usagePlan.addApiStage({
      stage: this.api.deploymentStage,
    });

    // Output API Gateway endpoint
    new cdk.CfnOutput(this, 'ApiEndpoint', {
      value: this.api.url,
      description: 'API Gateway endpoint URL',
    });

    // ===== Amazon Cognito (Task 2.4) =====
    
    // Create Cognito User Pool
    this.userPool = new cognito.UserPool(this, 'UserPool', {
      userPoolName: 'VyaparSaathi-UserPool',
      selfSignUpEnabled: true,
      signInAliases: {
        email: true,
        username: false,
      },
      autoVerify: {
        email: true,
      },
      passwordPolicy: {
        minLength: 8,
        requireLowercase: true,
        requireUppercase: true,
        requireDigits: true,
        requireSymbols: true,
      },
      accountRecovery: cognito.AccountRecovery.EMAIL_ONLY,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
      mfa: cognito.Mfa.OPTIONAL,
      mfaSecondFactor: {
        sms: true,
        otp: true,
      },
      standardAttributes: {
        email: {
          required: true,
          mutable: true,
        },
        givenName: {
          required: false,
          mutable: true,
        },
        familyName: {
          required: false,
          mutable: true,
        },
      },
      customAttributes: {
        businessName: new cognito.StringAttribute({ mutable: true }),
        businessType: new cognito.StringAttribute({ mutable: true }),
        region: new cognito.StringAttribute({ mutable: true }),
      },
    });

    // Create User Pool Client
    this.userPoolClient = new cognito.UserPoolClient(this, 'UserPoolClient', {
      userPool: this.userPool,
      userPoolClientName: 'VyaparSaathi-WebClient',
      authFlows: {
        userPassword: true,
        userSrp: true,
        custom: true,
      },
      oAuth: {
        flows: {
          authorizationCodeGrant: true,
          implicitCodeGrant: true,
        },
        scopes: [
          cognito.OAuthScope.EMAIL,
          cognito.OAuthScope.OPENID,
          cognito.OAuthScope.PROFILE,
        ],
        callbackUrls: [
          'http://localhost:3000/callback', // Development
          'https://vyaparsaathi.example.com/callback', // Production - update with actual domain
        ],
        logoutUrls: [
          'http://localhost:3000', // Development
          'https://vyaparsaathi.example.com', // Production - update with actual domain
        ],
      },
      preventUserExistenceErrors: true,
      generateSecret: false, // For web/mobile apps
    });

    // Add Google Identity Provider (placeholder - requires Google OAuth credentials)
    const googleProvider = new cognito.UserPoolIdentityProviderGoogle(this, 'GoogleProvider', {
      userPool: this.userPool,
      clientId: 'GOOGLE_CLIENT_ID_PLACEHOLDER', // Replace with actual Google OAuth client ID
      clientSecret: 'GOOGLE_CLIENT_SECRET_PLACEHOLDER', // Replace with actual Google OAuth client secret
      scopes: ['profile', 'email', 'openid'],
      attributeMapping: {
        email: cognito.ProviderAttribute.GOOGLE_EMAIL,
        givenName: cognito.ProviderAttribute.GOOGLE_GIVEN_NAME,
        familyName: cognito.ProviderAttribute.GOOGLE_FAMILY_NAME,
      },
    });

    // Add Facebook Identity Provider (placeholder - requires Facebook App credentials)
    const facebookProvider = new cognito.UserPoolIdentityProviderFacebook(this, 'FacebookProvider', {
      userPool: this.userPool,
      clientId: 'FACEBOOK_APP_ID_PLACEHOLDER', // Replace with actual Facebook App ID
      clientSecret: 'FACEBOOK_APP_SECRET_PLACEHOLDER', // Replace with actual Facebook App Secret
      scopes: ['public_profile', 'email'],
      attributeMapping: {
        email: cognito.ProviderAttribute.FACEBOOK_EMAIL,
        givenName: cognito.ProviderAttribute.FACEBOOK_NAME,
      },
    });

    // Ensure client depends on providers
    this.userPoolClient.node.addDependency(googleProvider);
    this.userPoolClient.node.addDependency(facebookProvider);

    // Create Cognito Authorizer for API Gateway
    const authorizer = new apigateway.CognitoUserPoolsAuthorizer(this, 'ApiAuthorizer', {
      cognitoUserPools: [this.userPool],
      authorizerName: 'VyaparSaathi-Authorizer',
      identitySource: 'method.request.header.Authorization',
    });

    // Note: The authorizer is created and can be applied to API methods
    // The existing API resources (dataResource, uploadResource, forecastResource, 
    // riskResource, explanationResource) already have methods configured above
    // In production, you would add the authorizer parameter when creating methods:
    // resource.addMethod('POST', integration, { authorizer })

    // Create User Pool Domain for hosted UI
    const userPoolDomain = this.userPool.addDomain('UserPoolDomain', {
      cognitoDomain: {
        domainPrefix: `vyapar-saathi-${this.account}`, // Must be globally unique
      },
    });

    // Output Cognito details
    new cdk.CfnOutput(this, 'UserPoolId', {
      value: this.userPool.userPoolId,
      description: 'Cognito User Pool ID',
    });

    new cdk.CfnOutput(this, 'UserPoolClientId', {
      value: this.userPoolClient.userPoolClientId,
      description: 'Cognito User Pool Client ID',
    });

    new cdk.CfnOutput(this, 'UserPoolDomain', {
      value: userPoolDomain.domainName,
      description: 'Cognito User Pool Domain',
    });
  }
}
