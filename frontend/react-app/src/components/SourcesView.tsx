import React, { useState } from 'react';
import type { SourceEvaluation } from '../types/research';
import { ExternalLink, Check, ShieldCheck, Search, XCircle } from 'lucide-react';

interface SourcesViewProps {
  sources: SourceEvaluation[];
}

export const SourcesView: React.FC<SourcesViewProps> = ({ sources }) => {
  const [filter, setFilter] = useState<'all' | 'included' | 'excluded'>('all');
  const [searchTerm, setSearchTerm] = useState('');

  if (!sources || sources.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
        No web sources evaluated yet.
      </div>
    );
  }

  const includedCount = sources.filter((s) => s.is_included !== false).length;
  const excludedCount = sources.filter((s) => s.is_included === false).length;

  const filteredSources = sources.filter((src) => {
    const isInc = src.is_included !== false;
    if (filter === 'included' && !isInc) return false;
    if (filter === 'excluded' && isInc) return false;
    if (searchTerm.trim()) {
      const q = searchTerm.toLowerCase();
      return (
        src.title.toLowerCase().includes(q) ||
        src.domain.toLowerCase().includes(q) ||
        src.reasoning.toLowerCase().includes(q) ||
        (src.exclusion_reason && src.exclusion_reason.toLowerCase().includes(q))
      );
    }
    return true;
  });

  return (
    <div>
      {/* Filter and Search Bar */}
      <div style={{
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '0.85rem',
        marginBottom: '1.5rem',
        padding: '0.85rem 1rem',
        background: 'rgba(255, 255, 255, 0.02)',
        borderRadius: '10px',
        border: '1px solid var(--border-color)'
      }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
          <button
            onClick={() => setFilter('all')}
            style={{
              padding: '0.35rem 0.75rem',
              borderRadius: '8px',
              fontSize: '0.78rem',
              fontWeight: 600,
              cursor: 'pointer',
              border: filter === 'all' ? '1px solid #3B82F6' : '1px solid var(--border-color)',
              background: filter === 'all' ? 'rgba(59, 130, 246, 0.2)' : 'transparent',
              color: filter === 'all' ? '#60A5FA' : 'var(--text-secondary)'
            }}
          >
            All Evaluated ({sources.length})
          </button>

          <button
            onClick={() => setFilter('included')}
            style={{
              padding: '0.35rem 0.75rem',
              borderRadius: '8px',
              fontSize: '0.78rem',
              fontWeight: 600,
              cursor: 'pointer',
              border: filter === 'included' ? '1px solid #10B981' : '1px solid var(--border-color)',
              background: filter === 'included' ? 'rgba(16, 185, 129, 0.15)' : 'transparent',
              color: filter === 'included' ? '#34D399' : 'var(--text-secondary)',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px'
            }}
          >
            <ShieldCheck size={12} />
            <span>Approved & Cited ({includedCount})</span>
          </button>

          <button
            onClick={() => setFilter('excluded')}
            style={{
              padding: '0.35rem 0.75rem',
              borderRadius: '8px',
              fontSize: '0.78rem',
              fontWeight: 600,
              cursor: 'pointer',
              border: filter === 'excluded' ? '1px solid #EF4444' : '1px solid var(--border-color)',
              background: filter === 'excluded' ? 'rgba(239, 68, 68, 0.15)' : 'transparent',
              color: filter === 'excluded' ? '#F87171' : 'var(--text-secondary)',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px'
            }}
          >
            <XCircle size={12} />
            <span>Excluded / Irrelevant ({excludedCount})</span>
          </button>
        </div>

        {/* Search input */}
        <div style={{ position: 'relative', minWidth: '220px' }}>
          <Search size={14} style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Filter by title, domain, or reason..."
            style={{
              width: '100%',
              padding: '0.4rem 0.75rem 0.4rem 2rem',
              borderRadius: '6px',
              background: 'rgba(15, 23, 42, 0.6)',
              border: '1px solid var(--border-color)',
              color: '#FFFFFF',
              fontSize: '0.78rem'
            }}
          />
        </div>
      </div>

      {/* Grid of Sources */}
      <div className="sources-grid">
        {filteredSources.map((src, idx) => {
          const isApproved = src.is_included !== false;

          return (
            <div
              key={idx}
              className="glass-card"
              style={{
                padding: '1.25rem',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                borderColor: isApproved ? 'var(--border-color)' : 'rgba(239, 68, 68, 0.25)',
                background: isApproved ? 'rgba(17, 24, 39, 0.7)' : 'rgba(30, 20, 25, 0.5)'
              }}
            >
              <div>
                {/* Header / Domain & Status Pill */}
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  marginBottom: '0.75rem',
                  gap: '0.5rem'
                }}>
                  <span style={{
                    fontSize: '0.8rem',
                    fontWeight: 700,
                    color: isApproved ? '#60A5FA' : '#F87171',
                    fontFamily: 'var(--font-mono)',
                    wordBreak: 'break-all'
                  }}>
                    {src.domain}
                  </span>

                  <span style={{
                    fontSize: '0.7rem',
                    fontWeight: 700,
                    padding: '0.2rem 0.6rem',
                    borderRadius: '12px',
                    background: isApproved ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)',
                    color: isApproved ? '#34D399' : '#F87171',
                    border: `1px solid ${isApproved ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
                    flexShrink: 0,
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '4px'
                  }}>
                    {isApproved ? <ShieldCheck size={10} /> : <XCircle size={10} />}
                    {isApproved ? 'Approved' : 'Excluded'}
                  </span>
                </div>

                {/* Title */}
                <h4 style={{
                  fontSize: '0.98rem',
                  fontWeight: 700,
                  color: '#FFFFFF',
                  lineHeight: 1.4,
                  marginBottom: '0.75rem',
                  wordBreak: 'break-word'
                }}>
                  {src.title}
                </h4>

                {/* Exclusion Reason Callout Box */}
                {!isApproved && src.exclusion_reason && (
                  <div style={{
                    background: 'rgba(239, 68, 68, 0.1)',
                    border: '1px solid rgba(239, 68, 68, 0.25)',
                    borderRadius: '6px',
                    padding: '0.6rem 0.8rem',
                    marginBottom: '0.85rem',
                    fontSize: '0.78rem',
                    color: '#FCA5A5',
                    lineHeight: 1.45
                  }}>
                    <strong>Rejection Rationale:</strong> {src.exclusion_reason}
                  </div>
                )}

                {/* Reasoning */}
                <p style={{
                  fontSize: '0.82rem',
                  color: 'var(--text-secondary)',
                  lineHeight: 1.5,
                  marginBottom: '1rem'
                }}>
                  {src.reasoning}
                </p>

                {/* Credibility Signals */}
                {src.credibility_signals && src.credibility_signals.length > 0 && (
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem', marginBottom: '1rem' }}>
                    {src.credibility_signals.map((sig, sIdx) => {
                      const isNegative = sig.toLowerCase().includes('excluded') || sig.toLowerCase().includes('low');
                      return (
                        <span
                          key={sIdx}
                          style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '0.25rem',
                            fontSize: '0.7rem',
                            color: isNegative ? '#F87171' : '#34D399',
                            background: isNegative ? 'rgba(239, 68, 68, 0.1)' : 'rgba(16, 185, 129, 0.1)',
                            border: `1px solid ${isNegative ? 'rgba(239, 68, 68, 0.25)' : 'rgba(16, 185, 129, 0.2)'}`,
                            padding: '0.15rem 0.45rem',
                            borderRadius: '6px'
                          }}
                        >
                          {isNegative ? <XCircle size={10} /> : <Check size={10} />}
                          {sig}
                        </span>
                      );
                    })}
                  </div>
                )}
              </div>

              {/* Footer Metrics & Link */}
              <div style={{
                borderTop: '1px solid var(--border-color)',
                paddingTop: '0.85rem',
                display: 'flex',
                flexWrap: 'wrap',
                gap: '0.75rem',
                alignItems: 'center',
                justifyContent: 'space-between'
              }}>
                <div style={{ display: 'flex', gap: '1rem' }}>
                  <div>
                    <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)', display: 'block' }}>Relevance</span>
                    <span style={{
                      fontSize: '0.85rem',
                      fontWeight: 700,
                      color: src.relevance_score >= 0.5 ? '#34D399' : src.relevance_score >= 0.3 ? '#FBBF24' : '#F87171'
                    }}>
                      {Math.round(src.relevance_score * 100)}%
                    </span>
                  </div>
                  <div>
                    <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)', display: 'block' }}>Authority</span>
                    <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#60A5FA' }}>
                      {Math.round(src.authority_score * 100)}%
                    </span>
                  </div>
                </div>

                <a
                  href={src.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '0.35rem',
                    fontSize: '0.78rem',
                    fontWeight: 600,
                    color: '#60A5FA',
                    textDecoration: 'none',
                    padding: '0.35rem 0.75rem',
                    borderRadius: '8px',
                    background: 'rgba(59, 130, 246, 0.1)',
                    flexShrink: 0
                  }}
                >
                  <span>Visit Source</span>
                  <ExternalLink size={12} />
                </a>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
