import { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { ResearchInput } from './components/ResearchInput';
import { ResearchProgress } from './components/ResearchProgress';
import { ReportViewer } from './components/ReportViewer';
import type { HealthResponse, ResearchSessionState } from './types/research';
import { checkHealth, startResearch, getResearchStatus } from './services/api';
import { AlertCircle } from 'lucide-react';

export function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [session, setSession] = useState<ResearchSessionState | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Poll backend health status on mount
  useEffect(() => {
    checkHealth().then(setHealth);
  }, []);

  // Poll active research session status every 1.5 seconds
  useEffect(() => {
    if (!session || session.id === 'init' || session.status === 'completed' || session.status === 'failed') {
      return;
    }

    const interval = setInterval(async () => {
      try {
        const updated = await getResearchStatus(session.id);
        setSession(updated);

        if (updated.status === 'completed' || updated.status === 'failed') {
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
    dateScope?: string
  ) => {
    setLoading(true);
    setError(null);

    // Instant optimistic session transition so UI never freezes on form
    const optimisticSession: ResearchSessionState = {
      id: 'init',
      question,
      mode,
      status: 'planning',
      current_stage: 'Stage A: Decomposing Research Objectives & Generating Search Vectors',
      sources_count: 0,
      findings_count: 0,
      sources: [],
      findings: [],
      created_at: new Date().toISOString(),
      duration_seconds: 0.1,
    };
    setSession(optimisticSession);

    try {
      const initialState = await startResearch(question, mode, category, dateScope);
      setSession(initialState);
    } catch (err: any) {
      console.error('Failed to start research:', err);
      setError(err.message || 'Failed to submit research request.');
      setLoading(false);
      setSession(null);
    }
  };

  const handleReset = () => {
    setSession(null);
    setLoading(false);
    setError(null);
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Top Navigation */}
      <Navbar health={health} onReset={handleReset} />

      {/* Main Page Area */}
      <main style={{ flex: 1, paddingBottom: '4rem' }}>
        {/* Error Banner */}
        {error && (
          <div style={{ maxWidth: '900px', margin: '1.5rem auto 0', padding: '0 1.5rem' }}>
            <div style={{
              padding: '1rem 1.25rem',
              borderRadius: '12px',
              background: 'rgba(239, 68, 68, 0.12)',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              color: '#F87171',
              display: 'flex',
              alignItems: 'center',
              gap: '0.75rem',
              fontSize: '0.9rem'
            }}>
              <AlertCircle size={20} style={{ flexShrink: 0 }} />
              <div>
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

        {/* State 2: Active Pipeline Progress */}
        {session && session.status !== 'completed' && session.status !== 'failed' && (
          <ResearchProgress session={session} />
        )}

        {/* State 3: Completed Report */}
        {session && (session.status === 'completed' || session.report) && (
          <ReportViewer session={session} onNewResearch={handleReset} />
        )}
      </main>

      {/* Footer */}
      <footer style={{
        borderTop: '1px solid var(--border-color)',
        padding: '1.5rem',
        textAlign: 'center',
        fontSize: '0.8rem',
        color: 'var(--text-muted)'
      }}>
        Deep Research AI Agent • Powered by FastAPI, Google Gemini, Tavily API & React Vite
      </footer>
    </div>
  );
}

export default App;
