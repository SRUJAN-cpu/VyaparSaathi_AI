/**
 * AWS Amplify Configuration
 * Configure authentication and API endpoints
 */

export const amplifyConfig = {
  Auth: {
    Cognito: {
      userPoolId: import.meta.env.VITE_USER_POOL_ID || '',
      userPoolClientId: import.meta.env.VITE_USER_POOL_CLIENT_ID || '',
      identityPoolId: import.meta.env.VITE_IDENTITY_POOL_ID || '',
      loginWith: {
        email: true,
      },
      signUpVerificationMethod: 'code' as const,
      userAttributes: {
        email: {
          required: true,
        },
      },
      passwordFormat: {
        minLength: 8,
        requireLowercase: true,
        requireUppercase: true,
        requireNumbers: true,
        requireSpecialCharacters: true,
      },
    },
  },
  API: {
    REST: {
      VyaparSaathiAPI: {
        endpoint: import.meta.env.VITE_API_ENDPOINT || '',
        region: import.meta.env.VITE_AWS_REGION || 'us-east-1',
      },
    },
  },
};
