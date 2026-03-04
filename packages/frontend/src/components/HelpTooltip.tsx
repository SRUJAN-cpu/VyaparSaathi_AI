/**
 * Help Tooltip Component
 * Contextual help tooltips for key concepts
 */

import React, { useState } from 'react';

interface HelpTooltipProps {
  content: string;
  title?: string;
}

const HelpTooltip: React.FC<HelpTooltipProps> = ({ content, title }) => {
  const [isVisible, setIsVisible] = useState(false);

  return (
    <div style={{ position: 'relative', display: 'inline-block' }}>
      <button
        onMouseEnter={() => setIsVisible(true)}
        onMouseLeave={() => setIsVisible(false)}
        onClick={() => setIsVisible(!isVisible)}
        style={{
          width: '20px',
          height: '20px',
          borderRadius: '50%',
          backgroundColor: '#1a73e8',
          color: 'white',
          border: 'none',
          cursor: 'pointer',
          fontSize: '0.75rem',
          fontWeight: 'bold',
          display: 'inline-flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        ?
      </button>

      {isVisible && (
        <div style={{
          position: 'absolute',
          bottom: '100%',
          left: '50%',
          transform: 'translateX(-50%)',
          marginBottom: '0.5rem',
          padding: '0.75rem',
          backgroundColor: '#333',
          color: 'white',
          borderRadius: '4px',
          fontSize: '0.85rem',
          width: '250px',
          zIndex: 1000,
          boxShadow: '0 2px 8px rgba(0,0,0,0.2)',
        }}>
          {title && (
            <p style={{ margin: 0, marginBottom: '0.5rem', fontWeight: 'bold' }}>
              {title}
            </p>
          )}
          <p style={{ margin: 0 }}>{content}</p>
          <div style={{
            position: 'absolute',
            top: '100%',
            left: '50%',
            transform: 'translateX(-50%)',
            width: 0,
            height: 0,
            borderLeft: '6px solid transparent',
            borderRight: '6px solid transparent',
            borderTop: '6px solid #333',
          }} />
        </div>
      )}
    </div>
  );
};

export default HelpTooltip;
