import React, { useState, useEffect } from 'react';
import type { ResearchSessionState } from '../types/research';
import { listResearchSessions, deleteResearchSession } from '../services/api';
import { History, X, Search, Trash2, ArrowUpRight } from 'lucide-react';

interface HistoryModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectSession: (session: ResearchSessionState) => void;
}

export const HistoryModal: React.FC<HistoryModalProps> = ({ isOpen, onClose, onSelectSession }) => {
  const [sessions, setSessions] = useState<ResearchSessionState[]>([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [error, setError] = useState<string | null>(null);

  const loadHistory = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await listResearchSessions(30, search.trim() || undefined);
      setSessions(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load history');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      loadHistory();
    }
  }, [isOpen, search]);

  const handleDelete = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    if (!window.confirm('Delete this research session from history?')) return;
    try {
      await deleteResearchSession(id);
      setSessions((prev) => prev.filter((s) => s.id !== id));
    } catch (err: any) {
      alert(`Error deleting: ${err.message}`);
    }
  };

  if (!isOpen) return null;

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0, 0, 0, 0.75)',
      backdropFilter: 'blur(8px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      padding: '1rem'
    }}>
      <div className="glass-card" style={{
        width: '100%',
        maxWidth: '750px',
        maxHeight: '85vh',
        display: 'flex',
        flexDirection: 'column',
        borderRadius: '16px',
        border: '1px solid var(--border-color)',
        boxShadow: '0 20px 50px rgba(0, 0, 0, 0.5)',
        overflow: 'hidden'
      }}>
        {/* Header */}
        <div style={{
          padding: '1.25rem 1.5rem',
          borderBottom: '1px solid var(--border-color)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <History size={20} color="#60A5FA" />
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#FFFFFF', margin: 0 }}>
              Saved Research Reports
            </h3>
          </div>
          <button
            onClick={onClose}
            style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Search */}
        <div style={{ padding: '1rem 1.5rem', borderBottom: '1px solid var(--border-color)' }}>
          <div style={{ position: 'relative' }}>
            <Search size={15} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search past research topics..."
              style={{
                width: '100%',
                padding: '0.55rem 0.85rem 0.55rem 2.2rem',
                borderRadius: '8px',
                background: 'rgba(15, 23, 42, 0.8)',
                border: '1px solid var(--border-color)',
                color: '#FFFFFF',
                fontSize: '0.85rem'
              }}
            />
          </div>
        </div>

        {/* List */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '1rem 1.5rem' }}>
          {error && (
            <div style={{ padding: '0.65rem', borderRadius: '6px', background: 'rgba(239, 68, 68, 0.15)', color: '#F87171', fontSize: '0.8rem', marginBottom: '1rem' }}>
              {error}
            </div>
          )}

          {loading && (
            <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
              Loading research history...
            </div>
          )}

          {!loading && sessions.length === 0 && (
            <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
              No research sessions found. Complete a research run to view it here.
            </div>
          )}

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {sessions.map((s) => {
              const isCompleted = s.status === 'completed';
              const badge = s.report?.verification_badge || 'Completed';

              return (
                <div
                  key={s.id}
                  onClick={() => {
                    onSelectSession(s);
                    onClose();
                  }}
                  style={{
                    padding: '1rem',
                    borderRadius: '10px',
                    background: 'rgba(255, 255, 255, 0.02)',
                    border: '1px solid var(--border-color)',
                    cursor: 'pointer',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    gap: '1rem',
                    transition: 'all 0.2s'
                  }}
                  onMouseEnter={(e) => (e.currentTarget.style.borderColor = 'rgba(59, 130, 246, 0.5)')}
                  onMouseLeave={(e) => (e.currentTarget.style.borderColor = 'var(--border-color)')}
                >
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.35rem' }}>
                      <span style={{
                        fontSize: '0.68rem',
                        fontWeight: 700,
                        textTransform: 'uppercase',
                        padding: '0.15rem 0.5rem',
                        borderRadius: '4px',
                        background: isCompleted ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)',
                        color: isCompleted ? '#34D399' : '#F87171'
                      }}>
                        {badge}
                      </span>
                      <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                        {new Date(s.created_at).toLocaleDateString()}
                      </span>
                      <span style={{ fontSize: '0.72rem', color: '#60A5FA', textTransform: 'capitalize' }}>
                        {s.mode} mode
                      </span>
                    </div>

                    <h4 style={{
                      fontSize: '0.95rem',
                      fontWeight: 600,
                      color: '#FFFFFF',
                      margin: 0,
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap'
                    }}>
                      "{s.question}"
                    </h4>

                    <div style={{ display: 'flex', gap: '0.85rem', marginTop: '0.35rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      <span>{s.sources_count} sources</span>
                      <span>{s.findings_count} claims</span>
                      <span>{s.duration_seconds}s</span>
                    </div>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <button
                      onClick={(e) => handleDelete(e, s.id)}
                      title="Delete session"
                      style={{
                        padding: '0.45rem',
                        borderRadius: '6px',
                        background: 'transparent',
                        border: '1px solid transparent',
                        color: 'var(--text-muted)',
                        cursor: 'pointer'
                      }}
                      onMouseEnter={(e) => (e.currentTarget.style.color = '#F87171')}
                      onMouseLeave={(e) => (e.currentTarget.style.color = 'var(--text-muted)')}
                    >
                      <Trash2 size={16} />
                    </button>
                    <ArrowUpRight size={18} color="#60A5FA" />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};
