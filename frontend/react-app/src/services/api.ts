import type { HealthResponse, ResearchSessionState, FollowupResponse } from '../types/research';

const API_BASE_URL =
  import.meta.env.VITE_API_URL ||
  (typeof window !== 'undefined' && window.location.hostname === 'localhost' && window.location.port === '5173'
    ? 'http://localhost:8000'
    : '');

export async function checkHealth(): Promise<HealthResponse> {
  try {
    const res = await fetch(`${API_BASE_URL}/health`);
    if (!res.ok) throw new Error('Backend health check failed');
    return await res.json();
  } catch (err) {
    console.error('Health check error:', err);
    return {
      status: 'offline',
      app_name: 'Deep Research AI',
      version: '1.0.0',
      gemini_api_configured: false,
      tavily_api_configured: false,
    };
  }
}

export async function startResearch(
  question: string,
  mode: string = 'quick',
  category?: string,
  dateScope?: string,
  minRelevance: number = 0.45
): Promise<ResearchSessionState> {
  const res = await fetch(`${API_BASE_URL}/api/v1/research`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      question,
      mode,
      category: category || undefined,
      date_scope: dateScope || undefined,
      min_relevance: minRelevance,
    }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: 'Failed to start research' }));
    throw new Error(errorData.detail || 'Research request failed');
  }

  return await res.json();
}

export async function getResearchStatus(sessionId: string): Promise<ResearchSessionState> {
  const res = await fetch(`${API_BASE_URL}/api/v1/research/${sessionId}`);
  if (!res.ok) {
    throw new Error(`Failed to fetch session ${sessionId}`);
  }
  return await res.json();
}

export async function cancelResearch(sessionId: string): Promise<void> {
  const res = await fetch(`${API_BASE_URL}/api/v1/research/${sessionId}/cancel`, {
    method: 'POST',
  });
  if (!res.ok) {
    throw new Error(`Failed to cancel research session ${sessionId}`);
  }
}

export async function submitFollowup(
  sessionId: string,
  question: string,
  allowNewSearch: boolean = true
): Promise<FollowupResponse> {
  const res = await fetch(`${API_BASE_URL}/api/v1/research/${sessionId}/followup`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      question,
      allow_new_search: allowNewSearch,
    }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Follow-up query failed' }));
    throw new Error(err.detail || 'Failed to submit follow-up');
  }

  return await res.json();
}

export async function listResearchSessions(
  limit: number = 20,
  query?: string,
  mode?: string
): Promise<ResearchSessionState[]> {
  const params = new URLSearchParams();
  params.append('limit', limit.toString());
  if (query) params.append('q', query);
  if (mode) params.append('mode', mode);

  const res = await fetch(`${API_BASE_URL}/api/v1/research?${params.toString()}`);
  if (!res.ok) {
    throw new Error('Failed to list research sessions');
  }
  return await res.json();
}

export async function deleteResearchSession(sessionId: string): Promise<void> {
  const res = await fetch(`${API_BASE_URL}/api/v1/research/${sessionId}`, {
    method: 'DELETE',
  });
  if (!res.ok) {
    throw new Error(`Failed to delete session ${sessionId}`);
  }
}

export function getExportUrl(sessionId: string, format: 'markdown' | 'pdf'): string {
  return `${API_BASE_URL}/api/v1/research/${sessionId}/report?format=${format}`;
}
