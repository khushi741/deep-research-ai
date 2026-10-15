import React, { useState } from 'react';
import { Zap, Compass, Filter, ArrowRight, Lightbulb, ShieldAlert } from 'lucide-react';

interface ResearchInputProps {
  onStartResearch: (question: string, mode: string, category?: string, dateScope?: string) => void;
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
  const [showAdvanced, setShowAdvanced] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (question.trim().length >= 5 && !isLoading) {
      onStartResearch(question.trim(), mode, category, dateScope);
    }
  };

  return (
    <div style={{ maxWidth: '900px', margin: '3rem auto 0', padding: '0 1.5rem' }}>
      {/* Hero Header */}
      <div style={{ textAlign: 'center', marginBottom: '2.5rem' }}>
        <div style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '0.5rem',
          padding: '0.4rem 1rem',
          borderRadius: '30px',
          background: 'rgba(59, 130, 246, 0.1)',
          border: '1px solid rgba(59, 130, 246, 0.2)',
          fontSize: '0.85rem',
          fontWeight: 600,
          color: '#60A5FA',
          marginBottom: '1.2rem'
        }}>
          <Zap size={14} />
          <span>Autonomous AI Research & Verification Agent</span>
        </div>
        <h2 style={{
          fontSize: '2.75rem',
          fontWeight: 800,
          letterSpacing: '-0.03em',
          lineHeight: 1.2,
          marginBottom: '1rem'
        }}>
          Research Smarter. <span className="text-gradient">Verify Sources.</span> Discover Insights.
        </h2>
        <p style={{
          fontSize: '1.1rem',
          color: 'var(--text-secondary)',
          maxWidth: '680px',
          margin: '0 auto'
        }}>
          Deep Research AI autonomously executes multi-step web queries, checks publisher credibility, extracts evidence, and synthesizes cited reports.
        </p>
      </div>

      {apiKeyMissing && (
        <div style={{
          padding: '1rem 1.25rem',
          borderRadius: '12px',
          background: 'rgba(245, 158, 11, 0.1)',
          border: '1px solid rgba(245, 158, 11, 0.25)',
          color: '#FBBF24',
          fontSize: '0.88rem',
          marginBottom: '1.5rem',
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem'
        }}>
          <ShieldAlert size={20} style={{ flexShrink: 0 }} />
          <div>
            <strong>Notice:</strong> <code>GEMINI_API_KEY</code> is not configured in <code>.env</code>. You can set it in your environment or <code>.env</code> file to run real Gemini synthesis.
          </div>
        </div>
      )}

      {/* Main Form Box */}
      <div className="glass-card" style={{ padding: '2rem', position: 'relative' }}>
        <form onSubmit={handleSubmit}>
          {/* Query Text Area */}
          <div style={{ position: 'relative', marginBottom: '1.5rem' }}>
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="What topic would you like to investigate deeply? (e.g. Current state of nuclear fusion energy in 2026)"
              rows={3}
              style={{
                width: '100%',
                background: 'rgba(15, 23, 42, 0.8)',
                border: '1px solid var(--border-color)',
                borderRadius: '12px',
                padding: '1rem 1.25rem',
                color: '#FFFFFF',
                fontSize: '1.05rem',
                fontFamily: 'inherit',
                resize: 'vertical',
                outline: 'none',
                transition: 'border-color 0.2s',
              }}
              onFocus={(e) => e.target.style.borderColor = 'var(--accent-primary)'}
              onBlur={(e) => e.target.style.borderColor = 'var(--border-color)'}
            />
          </div>

          {/* Controls Bar */}
          <div style={{
            display: 'flex',
            flexWrap: 'wrap',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '1rem',
            paddingTop: '0.5rem'
          }}>
            {/* Research Mode Selector */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              background: 'rgba(15, 23, 42, 0.6)',
              padding: '0.25rem',
              borderRadius: '10px',
              border: '1px solid var(--border-color)'
            }}>
              <button
                type="button"
                onClick={() => setMode('quick')}
                style={{
                  padding: '0.45rem 0.9rem',
                  borderRadius: '8px',
                  border: 'none',
                  fontSize: '0.85rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.4rem',
                  background: mode === 'quick' ? 'var(--accent-primary)' : 'transparent',
                  color: mode === 'quick' ? '#FFFFFF' : 'var(--text-muted)',
                  transition: 'all 0.2s'
                }}
              >
                <Zap size={14} />
                Quick (3-5 Pages)
              </button>

              <button
                type="button"
                onClick={() => setMode('deep')}
                style={{
                  padding: '0.45rem 0.9rem',
                  borderRadius: '8px',
                  border: 'none',
                  fontSize: '0.85rem',
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
                Deep Analysis (10+ Pages)
              </button>
            </div>

            {/* Filter Toggle & Submit Button */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <button
                type="button"
                onClick={() => setShowAdvanced(!showAdvanced)}
                style={{
                  padding: '0.55rem 0.85rem',
                  borderRadius: '10px',
                  background: showAdvanced ? 'rgba(59, 130, 246, 0.15)' : 'rgba(255, 255, 255, 0.05)',
                  border: '1px solid var(--border-color)',
                  color: showAdvanced ? '#60A5FA' : 'var(--text-secondary)',
                  fontSize: '0.85rem',
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
                  padding: '0.65rem 1.6rem',
                  borderRadius: '10px',
                  background: question.trim().length >= 5 && !isLoading
                    ? 'var(--gradient-brand)'
                    : 'rgba(255, 255, 255, 0.1)',
                  color: question.trim().length >= 5 && !isLoading ? '#FFFFFF' : 'var(--text-muted)',
                  border: 'none',
                  fontSize: '0.95rem',
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
                  <span>Running Research...</span>
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
              gridTemplateColumns: '1fr 1fr',
              gap: '1rem'
            }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.35rem' }}>
                  Domain Category (Optional)
                </label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  style={{
                    width: '100%',
                    background: '#0F172A',
                    border: '1px solid var(--border-color)',
                    borderRadius: '8px',
                    padding: '0.5rem',
                    color: '#FFFFFF',
                    fontSize: '0.85rem'
                  }}
                >
                  <option value="">All Domains & Industries</option>
                  <option value="Technology & AI">Technology & AI</option>
                  <option value="Science & Energy">Science & Energy</option>
                  <option value="Economics & Finance">Economics & Finance</option>
                  <option value="Healthcare & Medicine">Healthcare & Medicine</option>
                </select>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.35rem' }}>
                  Time Boundary (Optional)
                </label>
                <input
                  type="text"
                  value={dateScope}
                  onChange={(e) => setDateScope(e.target.value)}
                  placeholder="e.g. 2024-2026, Recent 6 months"
                  style={{
                    width: '100%',
                    background: '#0F172A',
                    border: '1px solid var(--border-color)',
                    borderRadius: '8px',
                    padding: '0.5rem',
                    color: '#FFFFFF',
                    fontSize: '0.85rem'
                  }}
                />
              </div>
            </div>
          )}
        </form>
      </div>

      {/* Example Topics */}
      <div style={{ marginTop: '2rem' }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          fontSize: '0.85rem',
          color: 'var(--text-muted)',
          marginBottom: '0.8rem'
        }}>
          <Lightbulb size={14} color="#FBBF24" />
          <span>Suggested Research Questions:</span>
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.6rem' }}>
          {EXAMPLE_QUERIES.map((q, idx) => (
            <button
              key={idx}
              onClick={() => setQuestion(q)}
              style={{
                background: 'rgba(255, 255, 255, 0.04)',
                border: '1px solid var(--border-color)',
                borderRadius: '20px',
                padding: '0.4rem 0.85rem',
                color: 'var(--text-secondary)',
                fontSize: '0.8rem',
                cursor: 'pointer',
                textAlign: 'left',
                transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = 'rgba(59, 130, 246, 0.4)';
                e.currentTarget.style.color = '#FFFFFF';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = 'var(--border-color)';
                e.currentTarget.style.color = 'var(--text-secondary)';
              }}
            >
              {q}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
