/**
 * Layout Component
 * Main layout wrapper with mobile-responsive navigation
 */

import React, { useState } from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { useAuthenticator } from '@aws-amplify/ui-react';

const Layout: React.FC = () => {
  const location = useLocation();
  const { user, signOut } = useAuthenticator((context) => [context.user]);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const isActive = (path: string) => location.pathname === path;

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <header style={{
        backgroundColor: '#1a73e8',
        color: 'white',
        padding: '1rem',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
      }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h1 style={{ margin: 0, fontSize: 'clamp(1.25rem, 4vw, 1.5rem)' }}>VyaparSaathi</h1>
          {user && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                style={{
                  display: 'none',
                  backgroundColor: 'transparent',
                  border: '1px solid white',
                  color: 'white',
                  padding: '0.5rem',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontSize: '1.25rem',
                }}
                className="show-mobile"
              >
                ☰
              </button>
              <button
                onClick={signOut}
                style={{
                  backgroundColor: 'transparent',
                  border: '1px solid white',
                  color: 'white',
                  padding: '0.5rem 1rem',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontSize: 'clamp(0.875rem, 2vw, 1rem)',
                }}
              >
                Sign Out
              </button>
            </div>
          )}
        </div>
      </header>

      {/* Navigation */}
      {user && (
        <nav style={{
          backgroundColor: '#f5f5f5',
          borderBottom: '1px solid #ddd',
          padding: '0 1rem',
          overflowX: 'auto',
          WebkitOverflowScrolling: 'touch',
        }}>
          <div style={{
            maxWidth: '1200px',
            margin: '0 auto',
            display: 'flex',
            gap: 'clamp(1rem, 3vw, 2rem)',
          }}>
            <Link
              to="/"
              style={{
                padding: '1rem 0',
                textDecoration: 'none',
                color: isActive('/') ? '#1a73e8' : '#333',
                borderBottom: isActive('/') ? '2px solid #1a73e8' : '2px solid transparent',
                fontWeight: isActive('/') ? 'bold' : 'normal',
                whiteSpace: 'nowrap',
                fontSize: 'clamp(0.875rem, 2vw, 1rem)',
              }}
            >
              Home
            </Link>
            <Link
              to="/input"
              style={{
                padding: '1rem 0',
                textDecoration: 'none',
                color: isActive('/input') ? '#1a73e8' : '#333',
                borderBottom: isActive('/input') ? '2px solid #1a73e8' : '2px solid transparent',
                fontWeight: isActive('/input') ? 'bold' : 'normal',
                whiteSpace: 'nowrap',
                fontSize: 'clamp(0.875rem, 2vw, 1rem)',
              }}
            >
              Data Input
            </Link>
            <Link
              to="/dashboard"
              style={{
                padding: '1rem 0',
                textDecoration: 'none',
                color: isActive('/dashboard') ? '#1a73e8' : '#333',
                borderBottom: isActive('/dashboard') ? '2px solid #1a73e8' : '2px solid transparent',
                fontWeight: isActive('/dashboard') ? 'bold' : 'normal',
                whiteSpace: 'nowrap',
                fontSize: 'clamp(0.875rem, 2vw, 1rem)',
              }}
            >
              Dashboard
            </Link>
            <Link
              to="/copilot"
              style={{
                padding: '1rem 0',
                textDecoration: 'none',
                color: isActive('/copilot') ? '#1a73e8' : '#333',
                borderBottom: isActive('/copilot') ? '2px solid #1a73e8' : '2px solid transparent',
                fontWeight: isActive('/copilot') ? 'bold' : 'normal',
                whiteSpace: 'nowrap',
                fontSize: 'clamp(0.875rem, 2vw, 1rem)',
              }}
            >
              AI Copilot
            </Link>
          </div>
        </nav>
      )}

      {/* Main Content */}
      <main style={{
        flex: 1,
        padding: 'clamp(1rem, 3vw, 2rem)',
        backgroundColor: '#fafafa',
      }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
          <Outlet />
        </div>
      </main>

      {/* Footer */}
      <footer style={{
        backgroundColor: '#333',
        color: 'white',
        padding: '1rem',
        textAlign: 'center',
      }}>
        <p style={{ margin: 0, fontSize: 'clamp(0.75rem, 2vw, 1rem)' }}>
          © 2024 VyaparSaathi - Festival Demand Forecasting Platform
        </p>
      </footer>
    </div>
  );
};

export default Layout;
