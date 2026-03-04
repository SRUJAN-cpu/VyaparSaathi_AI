/**
 * Data Input Page
 * CSV upload and questionnaire interface
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import CSVUpload from '../components/CSVUpload';
import Questionnaire from '../components/Questionnaire';

type InputMode = 'csv' | 'questionnaire';

const DataInputPage: React.FC = () => {
  const navigate = useNavigate();
  const [mode, setMode] = useState<InputMode | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleUploadSuccess = () => {
    setSuccess('Data uploaded successfully! Redirecting to dashboard...');
    setError(null);
    setTimeout(() => navigate('/dashboard'), 2000);
  };

  const handleUploadError = (errorMsg: string) => {
    setError(errorMsg);
    setSuccess(null);
  };

  const handleQuestionnaireSuccess = () => {
    setSuccess('Questionnaire submitted successfully! Redirecting to dashboard...');
    setError(null);
    setTimeout(() => navigate('/dashboard'), 2000);
  };

  const handleQuestionnaireError = (errorMsg: string) => {
    setError(errorMsg);
    setSuccess(null);
  };

  return (
    <div>
      <h1 style={{ marginBottom: '1rem' }}>Data Input</h1>
      <p style={{ color: '#666', marginBottom: '2rem' }}>
        Choose how you want to provide your sales data
      </p>

      {/* Mode Selection */}
      {!mode && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
          <div
            onClick={() => setMode('csv')}
            style={{
              backgroundColor: 'white',
              padding: '2rem',
              borderRadius: '8px',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
              cursor: 'pointer',
              transition: 'transform 0.2s',
            }}
            onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-4px)'}
            onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}
          >
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📊</div>
            <h3 style={{ marginBottom: '0.5rem' }}>Upload CSV File</h3>
            <p style={{ color: '#666' }}>
              I have historical sales data in CSV format
            </p>
          </div>

          <div
            onClick={() => setMode('questionnaire')}
            style={{
              backgroundColor: 'white',
              padding: '2rem',
              borderRadius: '8px',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
              cursor: 'pointer',
              transition: 'transform 0.2s',
            }}
            onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-4px)'}
            onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}
          >
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📝</div>
            <h3 style={{ marginBottom: '0.5rem' }}>Answer Questionnaire</h3>
            <p style={{ color: '#666' }}>
              I don't have detailed sales records
            </p>
          </div>
        </div>
      )}

      {/* CSV Upload Mode */}
      {mode === 'csv' && (
        <div style={{ backgroundColor: 'white', padding: '2rem', borderRadius: '8px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
            <h2>Upload Sales Data</h2>
            <button
              onClick={() => setMode(null)}
              style={{
                padding: '0.5rem 1rem',
                backgroundColor: '#f5f5f5',
                border: '1px solid #ccc',
                borderRadius: '4px',
                cursor: 'pointer',
              }}
            >
              Back
            </button>
          </div>
          <CSVUpload onUploadSuccess={handleUploadSuccess} onUploadError={handleUploadError} />
        </div>
      )}

      {/* Questionnaire Mode */}
      {mode === 'questionnaire' && (
        <div style={{ backgroundColor: 'white', padding: '2rem', borderRadius: '8px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
            <h2>Business Questionnaire</h2>
            <button
              onClick={() => setMode(null)}
              style={{
                padding: '0.5rem 1rem',
                backgroundColor: '#f5f5f5',
                border: '1px solid #ccc',
                borderRadius: '4px',
                cursor: 'pointer',
              }}
            >
              Back
            </button>
          </div>
          <Questionnaire onSubmitSuccess={handleQuestionnaireSuccess} onSubmitError={handleQuestionnaireError} />
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div style={{
          marginTop: '1rem',
          padding: '1rem',
          backgroundColor: '#ffebee',
          color: '#c62828',
          borderRadius: '4px',
          border: '1px solid #ef5350',
        }}>
          {error}
        </div>
      )}

      {/* Success Message */}
      {success && (
        <div style={{
          marginTop: '1rem',
          padding: '1rem',
          backgroundColor: '#e8f5e9',
          color: '#2e7d32',
          borderRadius: '4px',
          border: '1px solid #66bb6a',
        }}>
          {success}
        </div>
      )}
    </div>
  );
};

export default DataInputPage;
