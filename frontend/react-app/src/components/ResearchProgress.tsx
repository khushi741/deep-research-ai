import React, { useState, useEffect } from 'react';
import type { ResearchSessionState } from '../types/research';
import { Loader2, CheckCircle2, AlertCircle, FileText, Globe, ShieldCheck, Cpu, XCircle, Search, CheckSquare } from 'lucide-react';

interface ResearchProgressProps {
  session: ResearchSessionState;
  onCancel?: () => void;
}

const STAGES = [
  { id: 'planning', label: '1. Research Planning', icon: Cpu, desc: 'Decomposing query into subquestions & search queries' },
  { id: 'searching', label: '2. Multi-Vector Web Search', icon: Search, desc: 'Querying search engines across distinct topic angles' },
  { id: 'fetching', label: '3. Safe Content Extraction', icon: Globe, desc: 'Fetching HTML pages, SSRF validation & cleaning text' },
  { id: 'evaluating', label: '4. Semantic Source Evaluation', icon: ShieldCheck, desc: 'Scoring relevance, authority & rejecting homonyms' },
  { id: 'extracting', label: '5. Evidence Extraction', icon: CheckSquare, desc: 'Extracting atomic claims & cross-source corroboration' },
  { id: 'synthesizing', label: '6. Grounded Report Synthesis', icon: FileText, desc: 'Assembling executive report with verifiable citations' },
];

export const ResearchProgress: React.FC<ResearchProgressProps> = ({ session, onCancel }) => {
  const [elapsed, setElapsed] = useState<number>(() => {
    if (session.created_at) {
      const start = new Date(session.created_at).getTime();
      const diff = Math.floor((Date.now() - start) / 1000);
      return diff > 0 ? diff : 0;
    }
    return 0;
  });

  const [cancelling, setCancelling] = useState(false);

  useEffect(() => {
    const timer = setInterval(() => {
      setElapsed((prev) => prev + 1);
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const handleCancelClick = async () => {
    if (onCancel) {
      setCancelling(true);
      try {
        await onCancel();
      } finally {
        setCancelling(false);
      }
    }
  };

  const getStageStatus = (stageId: string) => {
    if (session.status === 'failed') return 'error';
    if (session.status === 'cancelled') return 'cancelled';
    if (session.status === 'completed') return 'completed';

    const completedStages = session.completed_stages || [];
    if (completedStages.includes(stageId)) return 'completed';

    if (session.status === stageId) return 'active';
    if (session.status === 'searching' && (stageId === 'searching' || stageId === 'fetching')) {
      return stageId === 'searching' ? 'active' : 'pending';
    }
    return 'pending';
  };

  const progressPercent = session.progress_percent ?? (
    session.status === 'completed' ? 100 :
    session.status === 'synthesizing' ? 90 :
    session.status === 'extracting' ? 70 :
    session.status === 'evaluating' ? 55 :
    session.status === 'searching' ? 30 :
    session.status === 'planning' ? 10 : 5
  );

  return (
    <div className="page-container">
      <div className="glass-card card-padding-lg">
        {/* Header */}
        <div className="progress-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.25rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '0.3rem' }}>
              {session.status === 'cancelled' ? (
                <XCircle size={14} color="#EF4444" />
              ) : session.status === 'failed' ? (
                <AlertCircle size={14} color="#EF4444" />
              ) : (
                <span className="radar-dot" />
              )}
              <span style={{
                fontSize: '0.75rem',
                fontWeight: 700,
                textTransform: 'uppercase',
                color: session.status === 'cancelled' ? '#EF4444' : 'var(--accent-cyan)',
                letterSpacing: '0.06em'
              }}>
                {session.status === 'cancelled' ? 'Research Cancelled' : 'Autonomous Pipeline Active'}
              </span>
            </div>
            <h3 style={{ fontSize: 'clamp(1.1rem, 3.5vw, 1.35rem)', fontWeight: 700, color: '#FFFFFF', marginTop: '0.2rem', lineHeight: 1.35 }}>
              "{session.question}"
            </h3>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              padding: '0.35rem 0.85rem',
              borderRadius: '20px',
              background: 'rgba(139, 92, 246, 0.15)',
              border: '1px solid rgba(139, 92, 246, 0.3)',
              color: '#C084FC',
              fontSize: '0.8rem',
              fontWeight: 700,
              textTransform: 'capitalize',
            }}>
              <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#C084FC' }} />
              {session.mode} Mode
            </div>

            {onCancel && session.status !== 'completed' && session.status !== 'failed' && session.status !== 'cancelled' && (
              <button
                onClick={handleCancelClick}
                disabled={cancelling}
                style={{
                  padding: '0.4rem 0.85rem',
                  borderRadius: '8px',
                  background: 'rgba(239, 68, 68, 0.15)',
                  border: '1px solid rgba(239, 68, 68, 0.35)',
                  color: '#F87171',
                  fontSize: '0.78rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.35rem',
                  transition: 'background 0.2s',
                }}
              >
                {cancelling ? <Loader2 size={12} className="animate-spin" /> : <XCircle size={12} />}
                <span>{cancelling ? 'Cancelling...' : 'Cancel Job'}</span>
              </button>
            )}
          </div>
        </div>

        {/* Real Progress Bar */}
        <div style={{ marginBottom: '1.75rem' }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            fontSize: '0.82rem',
            color: 'var(--text-secondary)',
            marginBottom: '0.5rem',
            flexWrap: 'wrap',
            gap: '0.35rem'
          }}>
            <span>Current Stage: <strong style={{ color: '#FFFFFF' }}>{session.current_stage || session.status}</strong></span>
            <span style={{ fontWeight: 700, color: 'var(--accent-cyan)' }}>{progressPercent}% Complete</span>
          </div>

          <div style={{
            height: '8px',
            width: '100%',
            background: 'rgba(255, 255, 255, 0.08)',
            borderRadius: '4px',
            overflow: 'hidden'
          }}>
            <div
              className="progress-bar-animated"
              style={{
                height: '100%',
                width: `${progressPercent}%`,
                borderRadius: '4px',
                transition: 'width 0.5s ease-in-out',
                boxShadow: '0 0 16px rgba(59, 130, 246, 0.6)'
              }}
            />
          </div>
        </div>

        {/* Real Event Live Terminal Strip */}
        <div className="terminal-strip" style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem',
          padding: '0.75rem 1rem',
          background: 'rgba(15, 23, 42, 0.9)',
          borderRadius: '8px',
          border: '1px solid var(--border-color)',
          marginBottom: '1.75rem'
        }}>
          {session.status !== 'completed' && session.status !== 'failed' && session.status !== 'cancelled' ? (
            <Loader2 size={16} className="animate-spin" color="#06B6D4" style={{ flexShrink: 0 }} />
          ) : session.status === 'completed' ? (
            <CheckCircle2 size={16} color="#10B981" style={{ flexShrink: 0 }} />
          ) : (
            <AlertCircle size={16} color="#EF4444" style={{ flexShrink: 0 }} />
          )}

          <div style={{ flex: 1, fontSize: '0.82rem', color: '#E2E8F0', fontFamily: 'var(--font-mono)', wordBreak: 'break-word' }}>
            <span style={{ color: '#06B6D4', fontWeight: 700 }}>[ACTUAL STATUS] </span>
            {session.current_stage}
          </div>

          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            fontSize: '0.75rem',
            color: '#94A3B8',
            fontFamily: 'var(--font-mono)',
            flexShrink: 0
          }}>
            <span>Elapsed: {elapsed}s</span>
          </div>
        </div>

        {/* Real Metrics Grid */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))',
          gap: '0.75rem',
          marginBottom: '2rem'
        }}>
          <div style={{ padding: '0.85rem', background: 'rgba(255, 255, 255, 0.03)', borderRadius: '8px', border: '1px solid var(--border-color)', textAlign: 'center' }}>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: '0.2rem' }}>Queries Completed</div>
            <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#60A5FA' }}>
              {session.completed_queries_count ?? 0} <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>/ {session.total_queries_count || '-'}</span>
            </div>
          </div>

          <div style={{ padding: '0.85rem', background: 'rgba(255, 255, 255, 0.03)', borderRadius: '8px', border: '1px solid var(--border-color)', textAlign: 'center' }}>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: '0.2rem' }}>Sources Evaluated</div>
            <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#34D399' }}>
              {session.sources_count}
            </div>
          </div>

          <div style={{ padding: '0.85rem', background: 'rgba(255, 255, 255, 0.03)', borderRadius: '8px', border: '1px solid var(--border-color)', textAlign: 'center' }}>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: '0.2rem' }}>Irrelevant Rejected</div>
            <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#F87171' }}>
              {session.rejected_sources_count ?? 0}
            </div>
          </div>

          <div style={{ padding: '0.85rem', background: 'rgba(255, 255, 255, 0.03)', borderRadius: '8px', border: '1px solid var(--border-color)', textAlign: 'center' }}>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: '0.2rem' }}>Evidence Claims</div>
            <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#C084FC' }}>
              {session.findings_count}
            </div>
          </div>
        </div>

        {/* Pipeline Stage Cards */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '0.85rem' }}>
          {STAGES.map((stg) => {
            const status = getStageStatus(stg.id);
            const Icon = stg.icon;

            return (
              <div
                key={stg.id}
                style={{
                  padding: '1rem',
                  borderRadius: '10px',
                  background: status === 'active'
                    ? 'rgba(59, 130, 246, 0.12)'
                    : status === 'completed'
                    ? 'rgba(16, 185, 129, 0.08)'
                    : 'rgba(255, 255, 255, 0.02)',
                  border: status === 'active'
                    ? '1px solid rgba(59, 130, 246, 0.4)'
                    : status === 'completed'
                    ? '1px solid rgba(16, 185, 129, 0.25)'
                    : '1px solid var(--border-color)',
                  transition: 'all 0.3s ease',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.4rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <Icon size={16} color={status === 'active' ? '#60A5FA' : status === 'completed' ? '#34D399' : '#64748B'} />
                    <span style={{ fontSize: '0.85rem', fontWeight: 700, color: status === 'active' ? '#FFFFFF' : status === 'completed' ? '#E2E8F0' : '#94A3B8' }}>
                      {stg.label}
                    </span>
                  </div>

                  {status === 'active' && <Loader2 size={14} className="animate-spin" color="#60A5FA" />}
                  {status === 'completed' && <CheckCircle2 size={14} color="#34D399" />}
                </div>

                <p style={{ fontSize: '0.74rem', color: 'var(--text-muted)', lineHeight: 1.4, margin: 0 }}>
                  {stg.desc}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
