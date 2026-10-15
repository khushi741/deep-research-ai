import React from 'react';
import type { SourceEvaluation } from '../types/research';
import { ExternalLink, Check } from 'lucide-react';

interface SourcesViewProps {
  sources: SourceEvaluation[];
}

export const SourcesView: React.FC<SourcesViewProps> = ({ sources }) => {
  if (!sources || sources.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
        No web sources evaluated yet.
      </div>
    );
  }

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))', gap: '1.25rem' }}>
      {sources.map((src, idx) => (
        <div
          key={idx}
          className="glass-card"
          style={{
            padding: '1.25rem',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between'
          }}
        >
          <div>
            {/* Header / Domain & Type */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '0.75rem'
            }}>
              <span style={{
                fontSize: '0.8rem',
                fontWeight: 700,
                color: '#60A5FA',
                fontFamily: 'var(--font-mono)'
              }}>
                {src.domain}
              </span>

              <span style={{
                fontSize: '0.7rem',
                fontWeight: 600,
                padding: '0.2rem 0.6rem',
                borderRadius: '12px',
                background: src.source_type === 'Academic' ? 'rgba(139, 92, 246, 0.2)' : 'rgba(255, 255, 255, 0.08)',
                color: src.source_type === 'Academic' ? '#C084FC' : 'var(--text-secondary)',
                border: '1px solid rgba(255, 255, 255, 0.1)'
              }}>
                {src.source_type}
              </span>
            </div>

            {/* Title */}
            <h4 style={{
              fontSize: '1rem',
              fontWeight: 700,
              color: '#FFFFFF',
              lineHeight: 1.4,
              marginBottom: '0.75rem'
            }}>
              {src.title}
            </h4>

            {/* Reasoning Excerpt */}
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
                {src.credibility_signals.map((sig, sIdx) => (
                  <span
                    key={sIdx}
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '0.25rem',
                      fontSize: '0.7rem',
                      color: '#34D399',
                      background: 'rgba(16, 185, 129, 0.1)',
                      border: '1px solid rgba(16, 185, 129, 0.2)',
                      padding: '0.15rem 0.45rem',
                      borderRadius: '6px'
                    }}
                  >
                    <Check size={10} />
                    {sig}
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Footer Metrics & Link */}
          <div style={{
            borderTop: '1px solid var(--border-color)',
            paddingTop: '0.85rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}>
            <div style={{ display: 'flex', gap: '1rem' }}>
              <div>
                <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)', display: 'block' }}>Relevance</span>
                <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#34D399' }}>
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
                fontSize: '0.8rem',
                fontWeight: 600,
                color: '#60A5FA',
                textDecoration: 'none',
                padding: '0.35rem 0.75rem',
                borderRadius: '8px',
                background: 'rgba(59, 130, 246, 0.1)'
              }}
            >
              <span>Visit Source</span>
              <ExternalLink size={12} />
            </a>
          </div>
        </div>
      ))}
    </div>
  );
};
