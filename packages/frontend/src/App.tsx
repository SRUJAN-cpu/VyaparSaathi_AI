/**
 * Main App Component
 * Configures AWS Amplify and routing
 */

import { Amplify } from 'aws-amplify';
import { Authenticator } from '@aws-amplify/ui-react';
import { RouterProvider } from 'react-router-dom';
import { amplifyConfig } from './config/amplify';
import { router } from './routes';
import '@aws-amplify/ui-react/styles.css';

// Configure Amplify
Amplify.configure(amplifyConfig);

function App() {
  return (
    <Authenticator>
      <RouterProvider router={router} />
    </Authenticator>
  );
}

export default App;
