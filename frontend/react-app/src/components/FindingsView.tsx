import React from 'react';
import type { Finding } from '../types/research';
import { ExternalLink, Quote } from 'lucide-react';

interface FindingsViewProps {
  findings: Finding[];
}

export const FindingsView: React.FC<FindingsViewProps> = ({ findings }) => {
  if (!findings || findings.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
        No structured findings extracted yet.
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      {findings.map((f) => (
        <div key={f.id} className="glass-card" style={{ padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span style={{
                fontSize: '0.75rem',
                fontWeight: 700,
                fontFamily: 'var(--font-mono)',
                color: '#60A5FA',
                background: 'rgba(59, 130, 246, 0.1)',
                padding: '0.2rem 0.5rem',
                borderRadius: '6px'
              }}>
                {f.id.toUpperCase()}
              </span>

              <span style={{
                fontSize: '0.75rem',
                fontWeight: 700,
                padding: '0.2rem 0.6rem',
                borderRadius: '12px',
                background: f.confidence_level === 'High' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(245, 158, 11, 0.15)',
                color: f.confidence_level === 'High' ? '#34D399' : '#FBBF24',
                border: `1px solid ${f.confidence_level === 'High' ? 'rgba(16, 185, 129, 0.3)' : 'rgba(245, 158, 11, 0.3)'}`
              }}>
                {f.confidence_level} Confidence
              </span>
            </div>

            {f.relevant_dates && (
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                Scope: {f.relevant_dates}
              </span>
            )}
          </div>

          {/* Claim */}
          <h4 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#FFFFFF', marginBottom: '0.75rem' }}>
            {f.claim}
          </h4>

          {/* Evidence Excerpt */}
          <div style={{
            background: 'rgba(15, 23, 42, 0.7)',
            borderLeft: '3px solid var(--accent-primary)',
            padding: '0.75rem 1rem',
            borderRadius: '0 8px 8px 0',
            fontSize: '0.85rem',
            color: 'var(--text-secondary)',
            fontStyle: 'italic',
            marginBottom: '0.85rem'
          }}>
            <Quote size={14} style={{ display: 'inline', marginRight: '0.35rem', color: '#60A5FA' }} />
            "{f.evidence_excerpt}"
          </div>

          {/* Explanation & Source Links */}
          <div style={{
            display: 'flex',
            flexWrap: 'wrap',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '0.75rem',
            fontSize: '0.8rem',
            color: 'var(--text-muted)'
          }}>
            <span>Reason: {f.confidence_explanation}</span>

            {f.source_urls && f.source_urls.length > 0 && (
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                {f.source_urls.map((url, uIdx) => (
                  <a
                    key={uIdx}
                    href={url}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{
                      color: '#60A5FA',
                      textDecoration: 'none',
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '0.25rem'
                    }}
                  >
                    <span>Source [{uIdx + 1}]</span>
                    <ExternalLink size={10} />
                  </a>
                ))}
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};
