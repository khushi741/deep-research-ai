import React from 'react';
import { Search, Sparkles, CheckCircle, AlertTriangle, Database } from 'lucide-react';
import type { HealthResponse } from '../types/research';

interface NavbarProps {
  health: HealthResponse | null;
  onReset: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ health, onReset }) => {
  return (
    <header style={{
      position: 'sticky',
      top: 0,
      zIndex: 50,
      background: 'rgba(11, 15, 25, 0.8)',
      backdropFilter: 'blur(12px)',
      borderBottom: '1px solid var(--border-color)',
      padding: '0.85rem 2rem',
    }}>
      <div style={{
        maxWidth: '1280px',
        margin: '0 auto',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        {/* Logo Brand */}
        <div 
          onClick={onReset}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
            cursor: 'pointer'
          }}
        >
          <div style={{
            width: '40px',
            height: '40px',
            borderRadius: '12px',
            background: 'var(--gradient-brand)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 4px 14px rgba(59, 130, 246, 0.4)'
          }}>
            <Search size={22} color="#FFFFFF" />
          </div>
          <div>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}>
              <h1 style={{
                fontSize: '1.25rem',
                fontWeight: 800,
                letterSpacing: '-0.02em',
                color: '#FFFFFF'
              }}>
                Deep Research <span className="text-gradient">AI</span>
              </h1>
              <span style={{
                fontSize: '0.65rem',
                fontWeight: 700,
                padding: '0.15rem 0.45rem',
                borderRadius: '6px',
                background: 'rgba(139, 92, 246, 0.2)',
                color: '#C084FC',
                border: '1px solid rgba(139, 92, 246, 0.3)',
                textTransform: 'uppercase'
              }}>
                v{health?.version || '1.0'}
              </span>
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', margin: 0 }}>
              Autonomous Multi-Step AI Research Agent
            </p>
          </div>
        </div>

        {/* System Status Badges */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.8rem' }}>
          {/* Gemini API Badge */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
            padding: '0.35rem 0.75rem',
            borderRadius: '20px',
            fontSize: '0.75rem',
            fontWeight: 600,
            background: health?.gemini_api_configured 
              ? 'rgba(16, 185, 129, 0.1)' 
              : 'rgba(245, 158, 11, 0.1)',
            border: `1px solid ${health?.gemini_api_configured 
              ? 'rgba(16, 185, 129, 0.25)' 
              : 'rgba(245, 158, 11, 0.25)'}`,
            color: health?.gemini_api_configured ? '#34D399' : '#FBBF24',
          }}>
            {health?.gemini_api_configured ? <CheckCircle size={14} /> : <AlertTriangle size={14} />}
            <span>Gemini LLM: {health?.gemini_api_configured ? 'Ready' : 'API Key Missing'}</span>
          </div>

          {/* Search Provider Badge */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
            padding: '0.35rem 0.75rem',
            borderRadius: '20px',
            fontSize: '0.75rem',
            fontWeight: 600,
            background: 'rgba(59, 130, 246, 0.1)',
            border: '1px solid rgba(59, 130, 246, 0.25)',
            color: '#60A5FA',
          }}>
            <Sparkles size={14} />
            <span>Search: {health?.tavily_api_configured ? 'Tavily API' : 'DuckDuckGo Fallback'}</span>
          </div>

          {/* Backend Status */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
            padding: '0.35rem 0.75rem',
            borderRadius: '20px',
            fontSize: '0.75rem',
            fontWeight: 600,
            background: health?.status === 'healthy' ? 'rgba(16, 185, 129, 0.08)' : 'rgba(239, 68, 68, 0.1)',
            color: health?.status === 'healthy' ? '#10B981' : '#EF4444',
            border: '1px solid rgba(255, 255, 255, 0.08)'
          }}>
            <Database size={14} />
            <span>API {health?.status === 'healthy' ? ':8000' : 'Offline'}</span>
          </div>
        </div>
      </div>
    </header>
  );
};
