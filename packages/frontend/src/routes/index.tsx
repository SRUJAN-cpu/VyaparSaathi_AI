/**
 * Application Routes
 * Defines all routes and navigation structure
 */

import { createBrowserRouter, Navigate } from 'react-router-dom';
import Layout from '../components/Layout';
import HomePage from '../pages/HomePage';
import DataInputPage from '../pages/DataInputPage';
import DashboardPage from '../pages/DashboardPage';
import CopilotPage from '../pages/CopilotPage';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      {
        index: true,
        element: <HomePage />,
      },
      {
        path: 'input',
        element: <DataInputPage />,
      },
      {
        path: 'dashboard',
        element: <DashboardPage />,
      },
      {
        path: 'copilot',
        element: <CopilotPage />,
      },
      {
        path: '*',
        element: <Navigate to="/" replace />,
      },
    ],
  },
]);
