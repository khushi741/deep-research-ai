import { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { ResearchInput } from './components/ResearchInput';
import { ResearchProgress } from './components/ResearchProgress';
import { ReportViewer } from './components/ReportViewer';
import { HistoryModal } from './components/HistoryModal';
import type { HealthResponse, ResearchSessionState } from './types/research';
import { checkHealth, startResearch, getResearchStatus, cancelResearch } from './services/api';
import { AlertCircle } from 'lucide-react';

export function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [session, setSession] = useState<ResearchSessionState | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);

  // Poll backend health status on mount
  useEffect(() => {
    checkHealth().then(setHealth);
  }, []);

  // Poll active research session status every 1.5 seconds
  useEffect(() => {
    if (!session || session.id === 'init' || session.status === 'completed' || session.status === 'failed' || session.status === 'cancelled') {
      return;
    }

    const interval = setInterval(async () => {
      try {
        const updated = await getResearchStatus(session.id);
        setSession(updated);

        if (updated.status === 'completed' || updated.status === 'failed' || updated.status === 'cancelled') {
          setLoading(false);
          if (updated.status === 'failed') {
            setError(updated.error_message || 'Research run failed.');
          }
        }
      } catch (err) {
        console.error('Error polling session status:', err);
      }
    }, 1500);

    return () => clearInterval(interval);
  }, [session]);

  const handleStartResearch = async (
    question: string,
    mode: string,
    category?: string,
    dateScope?: string,
    minRelevance?: number
  ) => {
    setLoading(true);
    setError(null);

    // Instant optimistic session transition
    const optimisticSession: ResearchSessionState = {
      id: 'init',
      question,
      mode,
      status: 'planning',
      current_stage: 'Stage 1/6: Formulating Research Plan & Search Vectors',
      progress_percent: 5,
      sources_count: 0,
      findings_count: 0,
      completed_queries_count: 0,
      total_queries_count: mode === 'deep' ? 12 : 4,
      rejected_sources_count: 0,
      sources: [],
      findings: [],
      created_at: new Date().toISOString(),
      duration_seconds: 0.1,
    };
    setSession(optimisticSession);

    try {
      const initialState = await startResearch(question, mode, category, dateScope, minRelevance);
      setSession(initialState);
    } catch (err: any) {
      console.error('Failed to start research:', err);
      setError(err.message || 'Failed to submit research request.');
      setLoading(false);
      setSession(null);
    }
  };

  const handleCancelResearch = async () => {
    if (!session || session.id === 'init') return;
    try {
      await cancelResearch(session.id);
      const updated = await getResearchStatus(session.id);
      setSession(updated);
      setLoading(false);
    } catch (err: any) {
      console.error('Failed to cancel research:', err);
    }
  };

  const handleReset = () => {
    setSession(null);
    setLoading(false);
    setError(null);
  };

  const handleSelectHistorySession = (selected: ResearchSessionState) => {
    setSession(selected);
    setError(null);
    setLoading(false);
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Top Navigation */}
      <Navbar 
        health={health} 
        onReset={handleReset} 
        onOpenHistory={() => setIsHistoryOpen(true)} 
      />

      {/* Main Page Area */}
      <main style={{ flex: 1, paddingBottom: '4rem' }}>
        {/* Error Banner */}
        {error && (
          <div className="page-container" style={{ marginTop: '1rem', marginBottom: '0.5rem' }}>
            <div style={{
              padding: '0.85rem 1.15rem',
              borderRadius: '12px',
              background: 'rgba(239, 68, 68, 0.12)',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              color: '#F87171',
              display: 'flex',
              alignItems: 'center',
              gap: '0.75rem',
              fontSize: '0.85rem'
            }}>
              <AlertCircle size={18} style={{ flexShrink: 0 }} />
              <div style={{ wordBreak: 'break-word' }}>
                <strong>Research Error:</strong> {error}
              </div>
            </div>
          </div>
        )}

        {/* State 1: Input Form */}
        {!session && (
          <ResearchInput
            onStartResearch={handleStartResearch}
            isLoading={loading}
            apiKeyMissing={health !== null && !health.gemini_api_configured}
          />
        )}

        {/* State 2: Active Pipeline Progress or Cancelled */}
        {session && session.status !== 'completed' && !session.report && (
          <ResearchProgress 
            session={session} 
            onCancel={handleCancelResearch} 
          />
        )}

        {/* State 3: Completed Report */}
        {session && (session.status === 'completed' || session.report) && (
          <ReportViewer 
            session={session} 
            onNewResearch={handleReset} 
          />
        )}
      </main>

      {/* History Modal */}
      <HistoryModal
        isOpen={isHistoryOpen}
        onClose={() => setIsHistoryOpen(false)}
        onSelectSession={handleSelectHistorySession}
      />

      {/* Footer */}
      <footer style={{
        borderTop: '1px solid var(--border-color)',
        padding: '1.25rem 1rem',
        textAlign: 'center',
        fontSize: '0.75rem',
        lineHeight: 1.5,
        color: 'var(--text-muted)'
      }}>
        Deep Research AI Agent • Real Autonomous Multi-Vector Engine • Powered by FastAPI, Google Gemini, Tavily & React
      </footer>
    </div>
  );
}

export default App;
