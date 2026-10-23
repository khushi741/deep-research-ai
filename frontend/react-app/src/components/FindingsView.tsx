import React, { useState } from 'react';
import type { Finding } from '../types/research';
import { ExternalLink, Quote, ShieldCheck, AlertCircle, ChevronDown, ChevronUp } from 'lucide-react';

interface FindingsViewProps {
  findings: Finding[];
}

export const FindingsView: React.FC<FindingsViewProps> = ({ findings }) => {
  const [filter, setFilter] = useState<'all' | 'verified' | 'uncorroborated'>('all');
  const [expandedId, setExpandedId] = useState<string | null>(null);

  if (!findings || findings.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
        No structured findings extracted yet.
      </div>
    );
  }

  const verifiedCount = findings.filter((f) => f.verification_status === 'Verified' || (f.corroboration_count && f.corroboration_count >= 2)).length;
  const uncorroboratedCount = findings.length - verifiedCount;

  const filtered = findings.filter((f) => {
    const isVer = f.verification_status === 'Verified' || (f.corroboration_count && f.corroboration_count >= 2);
    if (filter === 'verified' && !isVer) return false;
    if (filter === 'uncorroborated' && isVer) return false;
    return true;
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      {/* Filter Tabs */}
      <div style={{
        display: 'flex',
        flexWrap: 'wrap',
        gap: '0.5rem',
        padding: '0.65rem 0.85rem',
        background: 'rgba(255, 255, 255, 0.02)',
        borderRadius: '8px',
        border: '1px solid var(--border-color)',
        alignItems: 'center'
      }}>
        <button
          onClick={() => setFilter('all')}
          style={{
            padding: '0.3rem 0.75rem',
            borderRadius: '6px',
            fontSize: '0.78rem',
            fontWeight: 600,
            cursor: 'pointer',
            border: filter === 'all' ? '1px solid #3B82F6' : '1px solid var(--border-color)',
            background: filter === 'all' ? 'rgba(59, 130, 246, 0.2)' : 'transparent',
            color: filter === 'all' ? '#60A5FA' : 'var(--text-secondary)'
          }}
        >
          All Claims ({findings.length})
        </button>

        <button
          onClick={() => setFilter('verified')}
          style={{
            padding: '0.3rem 0.75rem',
            borderRadius: '6px',
            fontSize: '0.78rem',
            fontWeight: 600,
            cursor: 'pointer',
            border: filter === 'verified' ? '1px solid #10B981' : '1px solid var(--border-color)',
            background: filter === 'verified' ? 'rgba(16, 185, 129, 0.15)' : 'transparent',
            color: filter === 'verified' ? '#34D399' : 'var(--text-secondary)',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '4px'
          }}
        >
          <ShieldCheck size={12} />
          <span>Multi-Source Verified ({verifiedCount})</span>
        </button>

        <button
          onClick={() => setFilter('uncorroborated')}
          style={{
            padding: '0.3rem 0.75rem',
            borderRadius: '6px',
            fontSize: '0.78rem',
            fontWeight: 600,
            cursor: 'pointer',
            border: filter === 'uncorroborated' ? '1px solid #F59E0B' : '1px solid var(--border-color)',
            background: filter === 'uncorroborated' ? 'rgba(245, 158, 11, 0.15)' : 'transparent',
            color: filter === 'uncorroborated' ? '#FBBF24' : 'var(--text-secondary)',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '4px'
          }}
        >
          <AlertCircle size={12} />
          <span>Single-Source Provisional ({uncorroboratedCount})</span>
        </button>
      </div>

      {filtered.map((f) => {
        const isVerified = f.verification_status === 'Verified' || (f.corroboration_count && f.corroboration_count >= 2);
        const isExpanded = expandedId === f.id;

        return (
          <div key={f.id} className="glass-card" style={{ padding: '1.25rem' }}>
            <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: '0.5rem', marginBottom: '0.75rem' }}>
              <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: '0.5rem' }}>
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
                  background: isVerified ? 'rgba(16, 185, 129, 0.15)' : 'rgba(245, 158, 11, 0.15)',
                  color: isVerified ? '#34D399' : '#FBBF24',
                  border: `1px solid ${isVerified ? 'rgba(16, 185, 129, 0.3)' : 'rgba(245, 158, 11, 0.3)'}`,
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '4px'
                }}>
                  {isVerified ? <ShieldCheck size={10} /> : <AlertCircle size={10} />}
                  {isVerified ? 'Corroborated' : 'Provisional (Single Source)'}
                </span>

                {f.corroboration_count && f.corroboration_count > 1 && (
                  <span style={{ fontSize: '0.75rem', color: '#34D399', fontWeight: 600 }}>
                    {f.corroboration_count} independent sources
                  </span>
                )}
              </div>

              {f.relevant_dates && (
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  Timeline: {f.relevant_dates}
                </span>
              )}
            </div>

            {/* Claim */}
            <h4
              onClick={() => setExpandedId(isExpanded ? null : f.id)}
              style={{
                fontSize: '1.05rem',
                fontWeight: 700,
                color: '#FFFFFF',
                marginBottom: '0.75rem',
                wordBreak: 'break-word',
                lineHeight: 1.35,
                cursor: 'pointer',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}
            >
              <span>{f.claim}</span>
              {isExpanded ? <ChevronUp size={16} color="var(--text-muted)" /> : <ChevronDown size={16} color="var(--text-muted)" />}
            </h4>

            {/* Evidence Excerpt */}
            <div style={{
              background: 'rgba(15, 23, 42, 0.7)',
              borderLeft: `3px solid ${isVerified ? '#10B981' : '#F59E0B'}`,
              padding: '0.75rem 0.95rem',
              borderRadius: '0 8px 8px 0',
              fontSize: '0.84rem',
              color: 'var(--text-secondary)',
              fontStyle: 'italic',
              marginBottom: '0.85rem',
              wordBreak: 'break-word'
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
              gap: '0.65rem',
              fontSize: '0.8rem',
              color: 'var(--text-muted)'
            }}>
              <span style={{ wordBreak: 'break-word' }}>Validation: {f.confidence_explanation}</span>

              {f.source_urls && f.source_urls.length > 0 && (
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
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
                        gap: '0.25rem',
                        fontSize: '0.78rem'
                      }}
                    >
                      <span>Supporting Source [{uIdx + 1}]</span>
                      <ExternalLink size={10} />
                    </a>
                  ))}
                </div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
};
