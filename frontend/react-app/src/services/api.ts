import type { HealthResponse, ResearchSessionState } from '../types/research';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

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
  dateScope?: string
): Promise<ResearchSessionState> {
  const res = await fetch(`${API_BASE_URL}/api/v1/research`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      question,
      mode,
      category: category || undefined,
      date_scope: dateScope || undefined,
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

export function getExportUrl(sessionId: string, format: 'markdown' | 'pdf'): string {
  return `${API_BASE_URL}/api/v1/research/${sessionId}/report?format=${format}`;
}
