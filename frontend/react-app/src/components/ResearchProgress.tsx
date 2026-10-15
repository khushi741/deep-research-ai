import React from 'react';
import type { ResearchSessionState } from '../types/research';
import { Loader2, CheckCircle2, AlertCircle, FileText, Globe, ShieldCheck, Cpu } from 'lucide-react';

interface ResearchProgressProps {
  session: ResearchSessionState;
  onCancel?: () => void;
}

const STAGES = [
  { id: 'planning', label: 'Stage A: Research Planner', icon: Cpu, desc: 'Decomposing query into subquestions & vectors' },
  { id: 'searching', label: 'Stage B & C: Web Researcher', icon: Globe, desc: 'Querying search engines & fetching HTML content' },
  { id: 'evaluating', label: 'Stage D: Source Evaluator', icon: ShieldCheck, desc: 'Rating publisher authority, relevance & recency' },
  { id: 'synthesizing', label: 'Stage E & F: Synthesizer', icon: FileText, desc: 'Extracting evidence & building cited report' },
];

export const ResearchProgress: React.FC<ResearchProgressProps> = ({ session }) => {
  const getStageStatus = (stageId: string) => {
    const stageOrder = ['pending', 'planning', 'searching', 'extracting', 'evaluating', 'synthesizing', 'completed'];
    const currentIndex = stageOrder.indexOf(session.status);
    const targetIndex = stageOrder.indexOf(stageId);

    if (session.status === 'failed') return 'error';
    if (session.status === 'completed') return 'completed';
    if (currentIndex > targetIndex) return 'completed';
    if (currentIndex === targetIndex) return 'active';
    return 'pending';
  };

  const getProgressPercentage = () => {
    switch (session.status) {
      case 'planning': return 20;
      case 'searching': return 40;
      case 'extracting': return 60;
      case 'evaluating': return 75;
      case 'synthesizing': return 90;
      case 'completed': return 100;
      case 'failed': return 100;
      default: return 10;
    }
  };

  return (
    <div style={{ maxWidth: '900px', margin: '3rem auto 0', padding: '0 1.5rem' }}>
      <div className="glass-card" style={{ padding: '2.5rem' }}>
        {/* Header */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '1.5rem',
          borderBottom: '1px solid var(--border-color)',
          paddingBottom: '1rem'
        }}>
          <div>
            <span style={{
              fontSize: '0.75rem',
              fontWeight: 700,
              textTransform: 'uppercase',
              color: 'var(--accent-cyan)',
              letterSpacing: '0.05em'
            }}>
              Autonomous Pipeline Active
            </span>
            <h3 style={{ fontSize: '1.35rem', fontWeight: 700, color: '#FFFFFF', marginTop: '0.2rem' }}>
              Investigating: "{session.question}"
            </h3>
          </div>

          {/* Mode Pill */}
          <div style={{
            padding: '0.35rem 0.8rem',
            borderRadius: '20px',
            background: 'rgba(139, 92, 246, 0.15)',
            border: '1px solid rgba(139, 92, 246, 0.3)',
            color: '#C084FC',
            fontSize: '0.8rem',
            fontWeight: 700,
            textTransform: 'capitalize'
          }}>
            {session.mode} Mode
          </div>
        </div>

        {/* Progress Bar */}
        <div style={{ marginBottom: '2rem' }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            fontSize: '0.85rem',
            color: 'var(--text-secondary)',
            marginBottom: '0.5rem'
          }}>
            <span>Current Stage: <strong style={{ color: '#FFFFFF' }}>{session.current_stage || session.status}</strong></span>
            <span>{getProgressPercentage()}% Complete</span>
          </div>

          <div style={{
            height: '8px',
            width: '100%',
            background: 'rgba(255, 255, 255, 0.08)',
            borderRadius: '4px',
            overflow: 'hidden'
          }}>
            <div style={{
              height: '100%',
              width: `${getProgressPercentage()}%`,
              background: session.status === 'failed' ? '#EF4444' : 'var(--gradient-brand)',
              borderRadius: '4px',
              transition: 'width 0.5s ease-in-out',
              boxShadow: '0 0 12px rgba(59, 130, 246, 0.5)'
            }} />
          </div>
        </div>

        {/* Pipeline Stage Cards */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '2rem' }}>
          {STAGES.map((s) => {
            const status = getStageStatus(s.id);
            const Icon = s.icon;

            let cardBg = 'rgba(15, 23, 42, 0.4)';
            let borderColor = 'var(--border-color)';
            let iconColor = 'var(--text-muted)';

            if (status === 'active') {
              cardBg = 'rgba(59, 130, 246, 0.12)';
              borderColor = 'rgba(59, 130, 246, 0.5)';
              iconColor = '#60A5FA';
            } else if (status === 'completed') {
              cardBg = 'rgba(16, 185, 129, 0.08)';
              borderColor = 'rgba(16, 185, 129, 0.25)';
              iconColor = '#34D399';
            } else if (status === 'error') {
              cardBg = 'rgba(239, 68, 68, 0.1)';
              borderColor = 'rgba(239, 68, 68, 0.3)';
              iconColor = '#F87171';
            }

            return (
              <div
                key={s.id}
                style={{
                  padding: '1rem 1.25rem',
                  borderRadius: '12px',
                  background: cardBg,
                  border: `1px solid ${borderColor}`,
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '0.85rem',
                  transition: 'all 0.3s'
                }}
              >
                <div style={{ marginTop: '0.1rem', flexShrink: 0 }}>
                  {status === 'active' ? (
                    <Loader2 size={20} className="animate-spin" color={iconColor} />
                  ) : status === 'completed' ? (
                    <CheckCircle2 size={20} color={iconColor} />
                  ) : status === 'error' ? (
                    <AlertCircle size={20} color={iconColor} />
                  ) : (
                    <Icon size={20} color={iconColor} />
                  )}
                </div>

                <div>
                  <h4 style={{
                    fontSize: '0.9rem',
                    fontWeight: 700,
                    color: status === 'active' ? '#FFFFFF' : status === 'completed' ? '#D1D5DB' : 'var(--text-muted)'
                  }}>
                    {s.label}
                  </h4>
                  <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                    {s.desc}
                  </p>
                </div>
              </div>
            );
          })}
        </div>

        {/* Live Metrics Row */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(3, 1fr)',
          gap: '1rem',
          background: 'rgba(15, 23, 42, 0.8)',
          padding: '1rem 1.5rem',
          borderRadius: '12px',
          border: '1px solid var(--border-color)',
          textAlign: 'center'
        }}>
          <div>
            <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#60A5FA' }}>
              {session.sources_count || 0}
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
              Web Sources Evaluated
            </div>
          </div>

          <div>
            <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#C084FC' }}>
              {session.findings_count || 0}
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
              Verifiable Claims
            </div>
          </div>

          <div>
            <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#34D399' }}>
              {session.duration_seconds ? `${session.duration_seconds.toFixed(1)}s` : 'Processing...'}
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
              Elapsed Time
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
