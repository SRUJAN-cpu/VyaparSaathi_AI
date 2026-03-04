/**
 * Home Page
 * Landing page with overview and quick actions
 */

import React from 'react';
import { Link } from 'react-router-dom';

const HomePage: React.FC = () => {
  return (
    <div>
      <h1>Welcome to VyaparSaathi</h1>
      <p style={{ fontSize: '1.1rem', color: '#666', marginBottom: '2rem' }}>
        Festival demand and inventory risk forecasting platform for MSME retailers
      </p>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem', marginTop: '2rem' }}>
        <div style={{
          backgroundColor: 'white',
          padding: '1.5rem',
          borderRadius: '8px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        }}>
          <h3>📊 Data Input</h3>
          <p>Upload sales data or answer a quick questionnaire to get started</p>
          <Link to="/input" style={{
            display: 'inline-block',
            marginTop: '1rem',
            padding: '0.5rem 1rem',
            backgroundColor: '#1a73e8',
            color: 'white',
            textDecoration: 'none',
            borderRadius: '4px',
          }}>
            Get Started
          </Link>
        </div>

        <div style={{
          backgroundColor: 'white',
          padding: '1.5rem',
          borderRadius: '8px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        }}>
          <h3>📈 Dashboard</h3>
          <p>View demand forecasts and inventory risk assessments</p>
          <Link to="/dashboard" style={{
            display: 'inline-block',
            marginTop: '1rem',
            padding: '0.5rem 1rem',
            backgroundColor: '#1a73e8',
            color: 'white',
            textDecoration: 'none',
            borderRadius: '4px',
          }}>
            View Dashboard
          </Link>
        </div>

        <div style={{
          backgroundColor: 'white',
          padding: '1.5rem',
          borderRadius: '8px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        }}>
          <h3>🤖 AI Copilot</h3>
          <p>Ask questions and get explanations about your forecasts</p>
          <Link to="/copilot" style={{
            display: 'inline-block',
            marginTop: '1rem',
            padding: '0.5rem 1rem',
            backgroundColor: '#1a73e8',
            color: 'white',
            textDecoration: 'none',
            borderRadius: '4px',
          }}>
            Ask AI
          </Link>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
