/**
 * Chat Interface Component
 * Chat-style interface for AI copilot
 */

import React, { useState, useRef, useEffect } from 'react';
import { askCopilot } from '../services/api';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  insights?: string[];
  assumptions?: string[];
}

const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'Hello! I\'m your VyaparSaathi AI assistant. I can help you understand your forecasts, risk assessments, and inventory recommendations. What would you like to know?',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    const result = await askCopilot(input);
    setIsLoading(false);

    if (result.success) {
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: result.data.explanation || result.data.response || 'I apologize, but I couldn\'t generate a response.',
        timestamp: new Date(),
        insights: result.data.keyInsights,
        assumptions: result.data.assumptions,
      };
      setMessages(prev => [...prev, assistantMessage]);
    } else {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `I'm sorry, I encountered an error: ${result.error}. Please try again.`,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: 'clamp(400px, 70vh, 600px)',
      backgroundColor: 'white',
      borderRadius: '8px',
      boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
      overflow: 'hidden',
    }}>
      {/* Messages Container */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: 'clamp(1rem, 3vw, 1.5rem)',
        display: 'flex',
        flexDirection: 'column',
        gap: '1rem',
      }}>
        {messages.map((message) => (
          <div
            key={message.id}
            style={{
              display: 'flex',
              justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start',
            }}
          >
            <div style={{
              maxWidth: 'min(70%, 500px)',
              padding: 'clamp(0.75rem, 2vw, 1rem)',
              borderRadius: '8px',
              backgroundColor: message.role === 'user' ? '#1a73e8' : '#f5f5f5',
              color: message.role === 'user' ? 'white' : '#333',
              fontSize: 'clamp(0.875rem, 2vw, 1rem)',
            }}>
              <p style={{ margin: 0, whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>{message.content}</p>
              
              {/* Key Insights */}
              {message.insights && message.insights.length > 0 && (
                <div style={{
                  marginTop: '1rem',
                  padding: '0.75rem',
                  backgroundColor: 'rgba(26, 115, 232, 0.1)',
                  borderRadius: '4px',
                  borderLeft: '3px solid #1a73e8',
                }}>
                  <p style={{ margin: 0, marginBottom: '0.5rem', fontWeight: 'bold', fontSize: '0.9rem' }}>
                    💡 Key Insights:
                  </p>
                  <ul style={{ margin: 0, paddingLeft: '1.5rem', fontSize: '0.9rem' }}>
                    {message.insights.map((insight, idx) => (
                      <li key={idx}>{insight}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Assumptions */}
              {message.assumptions && message.assumptions.length > 0 && (
                <div style={{
                  marginTop: '0.75rem',
                  padding: '0.75rem',
                  backgroundColor: 'rgba(255, 152, 0, 0.1)',
                  borderRadius: '4px',
                  borderLeft: '3px solid #ff9800',
                }}>
                  <p style={{ margin: 0, marginBottom: '0.5rem', fontWeight: 'bold', fontSize: '0.9rem' }}>
                    ℹ️ Assumptions:
                  </p>
                  <ul style={{ margin: 0, paddingLeft: '1.5rem', fontSize: '0.9rem' }}>
                    {message.assumptions.map((assumption, idx) => (
                      <li key={idx}>{assumption}</li>
                    ))}
                  </ul>
                </div>
              )}

              <p style={{
                margin: 0,
                marginTop: '0.5rem',
                fontSize: '0.75rem',
                opacity: 0.7,
              }}>
                {message.timestamp.toLocaleTimeString()}
              </p>
            </div>
          </div>
        ))}

        {isLoading && (
          <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
            <div style={{
              padding: '1rem',
              borderRadius: '8px',
              backgroundColor: '#f5f5f5',
            }}>
              <p style={{ margin: 0 }}>Thinking...</p>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div style={{
        padding: 'clamp(0.75rem, 2vw, 1rem)',
        borderTop: '1px solid #e0e0e0',
        backgroundColor: '#fafafa',
      }}>
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me anything..."
            disabled={isLoading}
            style={{
              flex: '1 1 200px',
              padding: '0.75rem',
              border: '1px solid #ccc',
              borderRadius: '4px',
              fontSize: '16px',
              minWidth: 0,
            }}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            style={{
              padding: '0.75rem 1.5rem',
              backgroundColor: (!input.trim() || isLoading) ? '#ccc' : '#1a73e8',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: (!input.trim() || isLoading) ? 'not-allowed' : 'pointer',
              fontSize: '1rem',
              minHeight: '44px',
              flex: '0 0 auto',
            }}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
