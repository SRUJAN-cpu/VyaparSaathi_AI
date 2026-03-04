/**
 * AI Copilot Page
 * AI-powered explanations and conversational interface
 */

import React from 'react';
import ChatInterface from '../components/ChatInterface';
import HelpTooltip from '../components/HelpTooltip';

const CopilotPage: React.FC = () => {
  const suggestedQuestions = [
    'Why is my stockout risk high for DIYA-001?',
    'What factors are driving the demand forecast?',
    'How confident should I be in these predictions?',
    'What happens if I don\'t reorder the recommended quantity?',
    'Can you explain the festival multiplier effect?',
  ];

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
          <h1 style={{ margin: 0 }}>AI Copilot</h1>
          <HelpTooltip
            title="AI Copilot"
            content="Ask questions about your forecasts, risk assessments, and recommendations. I'll provide clear explanations in simple language."
          />
        </div>
        <p style={{ color: '#666' }}>
          Get AI-powered explanations about your forecasts and recommendations
        </p>
      </div>

      {/* Suggested Questions */}
      <div style={{
        backgroundColor: 'white',
        padding: '1.5rem',
        borderRadius: '8px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        marginBottom: '1.5rem',
      }}>
        <h3 style={{ marginBottom: '1rem' }}>💡 Suggested Questions</h3>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem' }}>
          {suggestedQuestions.map((question, index) => (
            <button
              key={index}
              style={{
                padding: '0.5rem 1rem',
                backgroundColor: '#e8f0fe',
                color: '#1a73e8',
                border: '1px solid #1a73e8',
                borderRadius: '20px',
                cursor: 'pointer',
                fontSize: '0.9rem',
                transition: 'all 0.2s',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#1a73e8';
                e.currentTarget.style.color = 'white';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = '#e8f0fe';
                e.currentTarget.style.color = '#1a73e8';
              }}
            >
              {question}
            </button>
          ))}
        </div>
      </div>

      {/* Chat Interface */}
      <ChatInterface />

      {/* Help Section */}
      <div style={{
        marginTop: '1.5rem',
        padding: '1rem',
        backgroundColor: '#e8f5e9',
        borderRadius: '4px',
        border: '1px solid #66bb6a',
      }}>
        <p style={{ margin: 0, fontSize: '0.9rem', color: '#2e7d32' }}>
          <strong>💡 Tip:</strong> You can ask about specific products, festivals, or general inventory strategies. 
          The AI will provide explanations based on your actual forecast and risk data.
        </p>
      </div>
    </div>
  );
};

export default CopilotPage;
