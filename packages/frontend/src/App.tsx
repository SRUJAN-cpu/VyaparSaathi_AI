/**
 * Main App Component
 * Configures AWS Amplify and routing
 */

import { useEffect, useState } from 'react';
import { Amplify } from 'aws-amplify';
import { Authenticator } from '@aws-amplify/ui-react';
import { RouterProvider } from 'react-router-dom';
import { amplifyConfig, validateAmplifyConfig } from './config/amplify';
import { router } from './routes';
import '@aws-amplify/ui-react/styles.css';

// Configure Amplify
Amplify.configure(amplifyConfig);

function App() {
  const [configValid, setConfigValid] = useState(true);

  useEffect(() => {
    const isValid = validateAmplifyConfig();
    setConfigValid(isValid);
  }, []);

  if (!configValid) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        padding: '2rem',
        backgroundColor: '#f5f5f5',
      }}>
        <div style={{
          maxWidth: '600px',
          padding: '2rem',
          backgroundColor: 'white',
          borderRadius: '8px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        }}>
          <h1 style={{ color: '#c62828', marginBottom: '1rem' }}>⚠️ Configuration Error</h1>
          <p style={{ marginBottom: '1rem' }}>
            VyaparSaathi requires AWS configuration to run. Please set up your environment variables:
          </p>
          <ol style={{ marginBottom: '1rem', paddingLeft: '1.5rem' }}>
            <li>Copy <code>.env.example</code> to <code>.env</code></li>
            <li>Fill in your AWS Cognito and API Gateway details</li>
            <li>Restart the development server</li>
          </ol>
          <p style={{ fontSize: '0.9rem', color: '#666' }}>
            See <code>packages/frontend/.env.example</code> for required variables.
          </p>
        </div>
      </div>
    );
  }

  return (
    <Authenticator>
      {({ signOut, user }) => (
        <RouterProvider router={router} />
      )}
    </Authenticator>
  );
}

export default App;
