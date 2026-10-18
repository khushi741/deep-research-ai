import React, { useState, useEffect } from 'react';
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

const STAGE_ACTIVITIES: Record<string, string[]> = {
  planning: [
    'Parsing research intent & scoping key investigative vectors...',
    'Generating targeted multi-vector search queries...',
    'Setting temporal and technical scope boundaries...',
  ],
  searching: [
    'Querying DuckDuckGo across multiple subquestion vectors...',
    'Traversing web results & fetching live HTML article payloads...',
    'Extracting clean text & stripping advertisement noise...',
    'Cross-indexing domain authority & publisher metadata...',
  ],
  evaluating: [
    'Assessing publisher authority & domain credibility...',
    'Scoring source relevance against research intent...',
    'Triangulating cross-source corroboration...',
  ],
  extracting: [
    'Extracting factual evidence & technical claims...',
    'Isolating numerical metrics, dates & direct quotes...',
    'Mapping evidence excerpts to research subquestions...',
  ],
  synthesizing: [
    'Structuring multi-section executive technical whitepaper...',
    'Embedding verified inline citations [1], [2]...',
    'Compiling conflicting evidence & key strategic findings...',
    'Formatting high-resolution publication PDF export...',
  ],
};

export const ResearchProgress: React.FC<ResearchProgressProps> = ({ session }) => {
  // Live elapsed seconds counter that ticks every 1 second
  const [elapsed, setElapsed] = useState<number>(() => {
    if (session.created_at) {
      const start = new Date(session.created_at).getTime();
      const diff = Math.floor((Date.now() - start) / 1000);
      return diff > 0 ? diff : 0;
    }
    return 0;
  });

  // Dynamic rotating micro-activity status
  const [activityIndex, setActivityIndex] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setElapsed((prev) => prev + 1);
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    const activityTimer = setInterval(() => {
      setActivityIndex((prev) => prev + 1);
    }, 2800);

    return () => clearInterval(activityTimer);
  }, []);

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
      case 'planning': return 25;
      case 'searching': return 50;
      case 'extracting': return 65;
      case 'evaluating': return 80;
      case 'synthesizing': return 92;
      case 'completed': return 100;
      case 'failed': return 100;
      default: return 15;
    }
  };

  const currentActivities = STAGE_ACTIVITIES[session.status] || STAGE_ACTIVITIES.searching;
  const currentAction = currentActivities[activityIndex % currentActivities.length];

  return (
    <div style={{ maxWidth: '900px', margin: '3rem auto 0', padding: '0 1.5rem' }}>
      <div className="glass-card" style={{ padding: '2.5rem' }}>
        {/* Header with live pulsing radar indicator */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '1.5rem',
          borderBottom: '1px solid var(--border-color)',
          paddingBottom: '1rem'
        }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '0.2rem' }}>
              <span className="radar-dot" />
              <span style={{
                fontSize: '0.75rem',
                fontWeight: 700,
                textTransform: 'uppercase',
                color: 'var(--accent-cyan)',
                letterSpacing: '0.06em'
              }}>
                Autonomous Pipeline Live & Active
              </span>
            </div>
            <h3 style={{ fontSize: '1.35rem', fontWeight: 700, color: '#FFFFFF', marginTop: '0.2rem', lineHeight: 1.4 }}>
              Investigating: "{session.question}"
            </h3>
          </div>

          {/* Mode Pill */}
          <div style={{
            display: 'flex',
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
            flexShrink: 0
          }}>
            <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#C084FC' }} />
            {session.mode} Mode
          </div>
        </div>

        {/* Progress Bar with Moving Shimmer */}
        <div style={{ marginBottom: '1.75rem' }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            fontSize: '0.85rem',
            color: 'var(--text-secondary)',
            marginBottom: '0.5rem'
          }}>
            <span>Current Stage: <strong style={{ color: '#FFFFFF' }}>{session.current_stage || session.status}</strong></span>
            <span style={{ fontWeight: 700, color: 'var(--accent-cyan)' }}>{getProgressPercentage()}% Complete</span>
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
                width: `${getProgressPercentage()}%`,
                borderRadius: '4px',
                transition: 'width 0.6s ease-in-out',
                boxShadow: '0 0 16px rgba(59, 130, 246, 0.6)'
              }}
            />
          </div>
        </div>

        {/* Live Terminal / Micro-Activity Action Strip */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem',
          background: 'rgba(15, 23, 42, 0.7)',
          border: '1px solid rgba(59, 130, 246, 0.25)',
          borderRadius: '10px',
          padding: '0.65rem 1rem',
          marginBottom: '1.75rem'
        }}>
          <Loader2 size={16} className="animate-spin" color="#06B6D4" style={{ flexShrink: 0 }} />
          <div style={{ flex: 1, fontSize: '0.82rem', color: '#E2E8F0', fontFamily: 'var(--font-mono)' }}>
            <span style={{ color: '#06B6D4', fontWeight: 700 }}>[AGENT ACTIVE] </span>
            {currentAction}
          </div>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            fontSize: '0.72rem',
            color: '#34D399',
            fontWeight: 700,
            textTransform: 'uppercase',
            letterSpacing: '0.05em'
          }}>
            <span className="radar-dot" style={{ width: '6px', height: '6px' }} />
            Processing
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
            let cardClass = '';

            if (status === 'active') {
              cardBg = 'rgba(59, 130, 246, 0.12)';
              borderColor = 'rgba(59, 130, 246, 0.6)';
              iconColor = '#60A5FA';
              cardClass = 'stage-card-active';
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
                className={cardClass}
                style={{
                  padding: '1.1rem 1.25rem',
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

                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <h4 style={{
                      fontSize: '0.9rem',
                      fontWeight: 700,
                      color: status === 'active' ? '#FFFFFF' : status === 'completed' ? '#D1D5DB' : 'var(--text-muted)'
                    }}>
                      {s.label}
                    </h4>

                    {/* Active audio visualizer equalizer bars */}
                    {status === 'active' && (
                      <div style={{ display: 'flex', alignItems: 'center', gap: '2.5px', height: '16px' }}>
                        <div className="soundwave-bar" />
                        <div className="soundwave-bar" />
                        <div className="soundwave-bar" />
                        <div className="soundwave-bar" />
                      </div>
                    )}
                  </div>

                  <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                    {s.desc}
                  </p>
                </div>
              </div>
            );
          })}
        </div>

        {/* Live Metrics Row with Live Ticking Elapsed Timer */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(3, 1fr)',
          gap: '1rem',
          background: 'rgba(15, 23, 42, 0.85)',
          padding: '1.25rem 1.5rem',
          borderRadius: '12px',
          border: '1px solid var(--border-color)',
          textAlign: 'center'
        }}>
          <div>
            <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#60A5FA' }}>
              {session.sources_count || 0}
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginTop: '0.15rem' }}>
              {session.sources_count > 0 ? 'Web Sources Evaluated' : 'Scanning Web Sources'}
            </div>
          </div>

          <div>
            <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#C084FC' }}>
              {session.findings_count || 0}
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginTop: '0.15rem' }}>
              {session.findings_count > 0 ? 'Verifiable Claims Found' : 'Extracting Evidence Claims'}
            </div>
          </div>

          <div>
            <div style={{
              fontSize: '1.5rem',
              fontWeight: 800,
              color: '#34D399',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '6px'
            }}>
              <span>
                {session.duration_seconds && (session.status === 'completed' || session.status === 'failed')
                  ? `${session.duration_seconds.toFixed(1)}s`
                  : `${elapsed}s`}
              </span>
            </div>
            <div style={{
              fontSize: '0.75rem',
              color: '#10B981',
              fontWeight: 700,
              textTransform: 'uppercase',
              marginTop: '0.15rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '5px'
            }}>
              <span className="radar-dot" style={{ width: '5px', height: '5px' }} />
              Live Elapsed Timer
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
