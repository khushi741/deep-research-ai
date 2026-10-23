import React, { useState } from 'react';
import { Zap, Compass, Filter, ArrowRight, ShieldAlert, Loader2 } from 'lucide-react';

interface ResearchInputProps {
  onStartResearch: (question: string, mode: string, category?: string, dateScope?: string, minRelevance?: number) => void;
  isLoading: boolean;
  apiKeyMissing?: boolean;
}

const EXAMPLE_QUERIES = [
  "How is generative AI changing software engineering jobs in India in 2026?",
  "What are the current breakthroughs and challenges in solid-state battery commercialization?",
  "What is the economic impact of global remote work policies post-2025?",
  "Quantum computing advancements in cryptography and security 2026"
];

export const ResearchInput: React.FC<ResearchInputProps> = ({
  onStartResearch,
  isLoading,
  apiKeyMissing
}) => {
  const [question, setQuestion] = useState('');
  const [mode, setMode] = useState<'quick' | 'deep'>('quick');
  const [category, setCategory] = useState('');
  const [dateScope, setDateScope] = useState('');
  const [minRelevance, setMinRelevance] = useState(45);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (question.trim().length >= 5 && !isLoading) {
      onStartResearch(question.trim(), mode, category, dateScope, minRelevance / 100);
    }
  };

  return (
    <div className="page-container">
      {/* Hero Header */}
      <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
        <div style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '0.45rem',
          padding: '0.35rem 0.9rem',
          borderRadius: '30px',
          background: 'rgba(59, 130, 246, 0.1)',
          border: '1px solid rgba(59, 130, 246, 0.25)',
          fontSize: '0.8rem',
          fontWeight: 600,
          color: '#60A5FA',
          marginBottom: '1rem'
        }}>
          <Zap size={14} />
          <span>Autonomous AI Research & Verification Agent</span>
        </div>
        <h2 className="hero-title-responsive">
          Research Smarter. <span className="text-gradient">Verify Sources.</span> Discover Insights.
        </h2>
        <p className="hero-subtitle-responsive">
          Deep Research AI autonomously executes multi-step web queries, checks publisher credibility, extracts evidence, and synthesizes cited reports.
        </p>
      </div>

      {apiKeyMissing && (
        <div style={{
          padding: '0.85rem 1.15rem',
          borderRadius: '12px',
          background: 'rgba(245, 158, 11, 0.1)',
          border: '1px solid rgba(245, 158, 11, 0.25)',
          color: '#FBBF24',
          fontSize: '0.85rem',
          marginBottom: '1.25rem',
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem'
        }}>
          <ShieldAlert size={18} style={{ flexShrink: 0 }} />
          <div>
            <strong>Notice:</strong> <code>GEMINI_API_KEY</code> is not configured. The agent will run with the local heuristic evaluation and fallback synthesis pipeline.
          </div>
        </div>
      )}

      {/* Main Form Box */}
      <div className="glass-card card-padding-lg" style={{ position: 'relative' }}>
        <form onSubmit={handleSubmit}>
          {/* Query Text Area */}
          <div style={{ position: 'relative', marginBottom: '1.25rem' }}>
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="What topic would you like to investigate deeply? (e.g. Current breakthroughs and challenges in solid-state battery commercialization)"
              rows={3}
              style={{
                width: '100%',
                background: 'rgba(15, 23, 42, 0.8)',
                border: '1px solid var(--border-color)',
                borderRadius: '12px',
                padding: '0.9rem 1.1rem',
                color: '#FFFFFF',
                fontSize: '1rem',
                fontFamily: 'inherit',
                resize: 'none',
                outline: 'none',
                lineHeight: 1.5
              }}
            />
          </div>

          {/* Action Row */}
          <div className="form-action-row" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.75rem' }}>
            {/* Mode Selector */}
            <div style={{ display: 'flex', background: 'rgba(15, 23, 42, 0.8)', padding: '4px', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
              <button
                type="button"
                onClick={() => setMode('quick')}
                style={{
                  padding: '0.45rem 0.85rem',
                  borderRadius: '8px',
                  border: 'none',
                  fontSize: '0.82rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.4rem',
                  background: mode === 'quick' ? 'var(--gradient-brand)' : 'transparent',
                  color: mode === 'quick' ? '#FFFFFF' : 'var(--text-muted)',
                  transition: 'all 0.2s'
                }}
              >
                <Zap size={14} />
                Quick (2 SubQ, 6 Pages)
              </button>
              <button
                type="button"
                onClick={() => setMode('deep')}
                style={{
                  padding: '0.45rem 0.85rem',
                  borderRadius: '8px',
                  border: 'none',
                  fontSize: '0.82rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.4rem',
                  background: mode === 'deep' ? 'var(--gradient-brand)' : 'transparent',
                  color: mode === 'deep' ? '#FFFFFF' : 'var(--text-muted)',
                  transition: 'all 0.2s'
                }}
              >
                <Compass size={14} />
                Deep (5 SubQ, 18 Pages, Gap Filling)
              </button>
            </div>

            {/* Filter Toggle & Submit Button */}
            <div className="action-buttons-group" style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
              <button
                type="button"
                onClick={() => setShowAdvanced(!showAdvanced)}
                style={{
                  padding: '0.55rem 0.85rem',
                  borderRadius: '10px',
                  background: showAdvanced ? 'rgba(59, 130, 246, 0.15)' : 'rgba(255, 255, 255, 0.05)',
                  border: '1px solid var(--border-color)',
                  color: showAdvanced ? '#60A5FA' : 'var(--text-secondary)',
                  fontSize: '0.82rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.4rem'
                }}
              >
                <Filter size={14} />
                Filters
              </button>

              <button
                type="submit"
                disabled={question.trim().length < 5 || isLoading}
                style={{
                  padding: '0.65rem 1.4rem',
                  borderRadius: '10px',
                  background: question.trim().length >= 5 && !isLoading
                    ? 'var(--gradient-brand)'
                    : 'rgba(59, 130, 246, 0.25)',
                  color: '#FFFFFF',
                  border: 'none',
                  fontSize: '0.9rem',
                  fontWeight: 700,
                  cursor: question.trim().length >= 5 && !isLoading ? 'pointer' : 'not-allowed',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  boxShadow: question.trim().length >= 5 && !isLoading
                    ? '0 4px 15px rgba(59, 130, 246, 0.4)'
                    : 'none',
                  transition: 'all 0.2s'
                }}
              >
                {isLoading ? (
                  <>
                    <Loader2 size={16} className="animate-spin" />
                    <span>Launching...</span>
                  </>
                ) : (
                  <>
                    <span>Start Research</span>
                    <ArrowRight size={16} />
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Advanced Filter Accordion */}
          {showAdvanced && (
            <div style={{
              marginTop: '1.25rem',
              paddingTop: '1.25rem',
              borderTop: '1px solid var(--border-color)',
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
              gap: '1rem'
            }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>
                  Category Focus
                </label>
                <input
                  type="text"
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  placeholder="e.g. Science, Energy, Technology, Finance"
                  style={{
                    width: '100%',
                    padding: '0.5rem 0.75rem',
                    borderRadius: '8px',
                    background: 'rgba(15, 23, 42, 0.6)',
                    border: '1px solid var(--border-color)',
                    color: '#FFFFFF',
                    fontSize: '0.82rem'
                  }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>
                  Temporal Scope
                </label>
                <input
                  type="text"
                  value={dateScope}
                  onChange={(e) => setDateScope(e.target.value)}
                  placeholder="e.g. 2025-2026, Recent, Historical"
                  style={{
                    width: '100%',
                    padding: '0.5rem 0.75rem',
                    borderRadius: '8px',
                    background: 'rgba(15, 23, 42, 0.6)',
                    border: '1px solid var(--border-color)',
                    color: '#FFFFFF',
                    fontSize: '0.82rem'
                  }}
                />
              </div>

              <div>
                <label style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>
                  <span>Min Relevance Threshold</span>
                  <span style={{ color: '#60A5FA' }}>{minRelevance}%</span>
                </label>
                <input
                  type="range"
                  min="25"
                  max="80"
                  step="5"
                  value={minRelevance}
                  onChange={(e) => setMinRelevance(Number(e.target.value))}
                  style={{ width: '100%', accentColor: '#3B82F6' }}
                />
                <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                  Filters out homonyms & unrelated web hits.
                </span>
              </div>
            </div>
          )}
        </form>
      </div>

      {/* Example Suggestions */}
      <div style={{ marginTop: '2rem' }}>
        <div style={{ fontSize: '0.78rem', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          Suggested Research Questions
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '0.75rem' }}>
          {EXAMPLE_QUERIES.map((eq, idx) => (
            <div
              key={idx}
              onClick={() => setQuestion(eq)}
              style={{
                padding: '0.85rem 1rem',
                borderRadius: '10px',
                background: 'rgba(255, 255, 255, 0.02)',
                border: '1px solid var(--border-color)',
                fontSize: '0.82rem',
                color: 'var(--text-secondary)',
                cursor: 'pointer',
                transition: 'all 0.2s',
                lineHeight: 1.4
              }}
              onMouseEnter={(e) => (e.currentTarget.style.borderColor = 'rgba(59, 130, 246, 0.5)')}
              onMouseLeave={(e) => (e.currentTarget.style.borderColor = 'var(--border-color)')}
            >
              "{eq}"
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
