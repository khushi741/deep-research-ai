import { Search, Sparkles, CheckCircle, AlertTriangle, Database, History } from 'lucide-react';
import type { HealthResponse } from '../types/research';

interface NavbarProps {
  health: HealthResponse | null;
  onReset: () => void;
  onOpenHistory?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ health, onReset, onOpenHistory }) => {
  return (
    <header className="navbar-header-root">
      <div className="navbar-inner">
        {/* Logo Brand */}
        <div className="navbar-brand-row">
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
              width: '38px',
              height: '38px',
              borderRadius: '10px',
              background: 'var(--gradient-brand)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 4px 14px rgba(59, 130, 246, 0.4)',
              flexShrink: 0
            }}>
              <Search size={20} color="#FFFFFF" />
            </div>
            <div>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.45rem'
              }}>
                <h1 style={{
                  fontSize: 'clamp(1.05rem, 3.5vw, 1.25rem)',
                  fontWeight: 800,
                  letterSpacing: '-0.02em',
                  color: '#FFFFFF',
                  margin: 0
                }}>
                  Deep Research <span className="text-gradient">AI</span>
                </h1>
                <span style={{
                  fontSize: '0.65rem',
                  fontWeight: 700,
                  padding: '0.12rem 0.45rem',
                  borderRadius: '6px',
                  background: 'rgba(139, 92, 246, 0.2)',
                  color: '#C084FC',
                  border: '1px solid rgba(139, 92, 246, 0.3)',
                  textTransform: 'uppercase'
                }}>
                  v{health?.version || '1.0'}
                </span>
              </div>
              <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', margin: 0 }}>
                Autonomous Multi-Step AI Agent
              </p>
            </div>
          </div>
        </div>

        {/* System Status Badges */}
        <div className="navbar-badges-wrap">
          {/* Gemini API Badge */}
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.35rem',
            padding: '0.3rem 0.65rem',
            borderRadius: '20px',
            fontSize: '0.72rem',
            fontWeight: 600,
            whiteSpace: 'nowrap',
            flexShrink: 0,
            background: health?.gemini_api_configured 
              ? 'rgba(16, 185, 129, 0.1)' 
              : 'rgba(245, 158, 11, 0.1)',
            border: `1px solid ${health?.gemini_api_configured 
              ? 'rgba(16, 185, 129, 0.25)' 
              : 'rgba(245, 158, 11, 0.25)'}`,
            color: health?.gemini_api_configured ? '#34D399' : '#FBBF24',
          }}>
            {health?.gemini_api_configured ? <CheckCircle size={13} /> : <AlertTriangle size={13} />}
            <span>Gemini: {health?.gemini_api_configured ? 'Ready' : 'No Key'}</span>
          </div>

          {/* Search Provider Badge */}
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.35rem',
            padding: '0.3rem 0.65rem',
            borderRadius: '20px',
            fontSize: '0.72rem',
            fontWeight: 600,
            whiteSpace: 'nowrap',
            flexShrink: 0,
            background: 'rgba(59, 130, 246, 0.1)',
            border: '1px solid rgba(59, 130, 246, 0.25)',
            color: '#60A5FA',
          }}>
            <Sparkles size={13} />
            <span>Search: {health?.tavily_api_configured ? 'Tavily' : 'DuckDuckGo'}</span>
          </div>

          {/* Backend Status */}
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.35rem',
            padding: '0.3rem 0.65rem',
            borderRadius: '20px',
            fontSize: '0.72rem',
            fontWeight: 600,
            whiteSpace: 'nowrap',
            flexShrink: 0,
            background: health?.status === 'healthy' ? 'rgba(16, 185, 129, 0.08)' : 'rgba(239, 68, 68, 0.1)',
            color: health?.status === 'healthy' ? '#10B981' : '#EF4444',
            border: '1px solid rgba(255, 255, 255, 0.08)'
          }}>
            <Database size={13} />
            <span>API {health?.status === 'healthy' ? ':8000' : 'Offline'}</span>
          </div>

          {/* History Button */}
          {onOpenHistory && (
            <button
              onClick={onOpenHistory}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.35rem',
                padding: '0.3rem 0.75rem',
                borderRadius: '20px',
                fontSize: '0.74rem',
                fontWeight: 600,
                background: 'rgba(255, 255, 255, 0.06)',
                border: '1px solid var(--border-color)',
                color: '#FFFFFF',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
            >
              <History size={13} color="#60A5FA" />
              <span>History</span>
            </button>
          )}
        </div>
      </div>
    </header>
  );
};
