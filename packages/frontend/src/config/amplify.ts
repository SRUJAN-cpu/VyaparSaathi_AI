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

/**
 * Validate Amplify configuration
 * Logs warnings if required environment variables are missing
 */
export function validateAmplifyConfig(): boolean {
  const requiredVars = [
    'VITE_USER_POOL_ID',
    'VITE_USER_POOL_CLIENT_ID',
    'VITE_API_ENDPOINT',
  ];

  const missing = requiredVars.filter(varName => !import.meta.env[varName]);

  if (missing.length > 0) {
    console.warn(
      'Missing required environment variables:',
      missing.join(', '),
      '\nPlease create a .env file based on .env.example'
    );
    return false;
  }

  return true;
}
