import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import type { ResearchSessionState, FollowupItem } from '../types/research';
import { SourcesView } from './SourcesView';
import { FindingsView } from './FindingsView';
import { getExportUrl, submitFollowup } from '../services/api';
import { 
  FileText, Download, Globe, ShieldCheck, CheckCircle2, 
  RotateCcw, ExternalLink, AlertCircle, MessageSquare, Send, Loader2, Sparkles 
} from 'lucide-react';

interface ReportViewerProps {
  session: ResearchSessionState;
  onNewResearch: () => void;
}

export const ReportViewer: React.FC<ReportViewerProps> = ({ session, onNewResearch }) => {
  const [activeTab, setActiveTab] = useState<'report' | 'sources' | 'findings' | 'references' | 'followup'>('report');
  const [followupQuery, setFollowupQuery] = useState('');
  const [allowNewSearch, setAllowNewSearch] = useState(true);
  const [followupLoading, setFollowupLoading] = useState(false);
  const [followupList, setFollowupList] = useState<FollowupItem[]>(session.followup_history || []);
  const [followupError, setFollowupError] = useState<string | null>(null);

  const report = session.report;
  const badge = report?.verification_badge || 'Partial Evidence';
  const isVerified = badge.toLowerCase() === 'verified';
  const isPartial = badge.toLowerCase().includes('partial');

  const handleFollowupSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!followupQuery.trim() || followupLoading) return;

    setFollowupLoading(true);
    setFollowupError(null);

    try {
      const res = await submitFollowup(session.id, followupQuery.trim(), allowNewSearch);
      setFollowupList((prev) => [
        ...prev,
        {
          question: res.question,
          answer: res.answer,
          evidence_source: res.evidence_source,
          new_searches_conducted: res.new_searches_conducted,
          timestamp: Date.now()
        }
      ]);
      setFollowupQuery('');
    } catch (err: any) {
      setFollowupError(err.message || 'Failed to answer follow-up.');
    } finally {
      setFollowupLoading(false);
    }
  };

  return (
    <div className="report-container">
      {/* Header Banner */}
      <div className="glass-card card-padding-lg" style={{ marginBottom: '1.75rem' }}>
        <div className="report-header-row" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          {/* Truthful Verification Badge */}
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.45rem',
            padding: '0.35rem 0.85rem',
            borderRadius: '20px',
            background: isVerified ? 'rgba(16, 185, 129, 0.15)' : isPartial ? 'rgba(245, 158, 11, 0.15)' : 'rgba(239, 68, 68, 0.15)',
            color: isVerified ? '#34D399' : isPartial ? '#FBBF24' : '#F87171',
            border: `1px solid ${isVerified ? 'rgba(16, 185, 129, 0.3)' : isPartial ? 'rgba(245, 158, 11, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
            fontSize: '0.8rem',
            fontWeight: 700
          }}>
            {isVerified ? <CheckCircle2 size={15} /> : <AlertCircle size={15} />}
            <span>STATUS: {badge.toUpperCase()}</span>
          </div>

          <div className="report-buttons-row" style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            <button
              onClick={onNewResearch}
              style={{
                padding: '0.55rem 0.95rem',
                borderRadius: '8px',
                background: 'rgba(255, 255, 255, 0.06)',
                border: '1px solid var(--border-color)',
                color: '#FFFFFF',
                fontSize: '0.82rem',
                fontWeight: 600,
                cursor: 'pointer',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.4rem'
              }}
            >
              <RotateCcw size={14} />
              <span>New Research</span>
            </button>

            {/* Download Buttons */}
            <a
              href={getExportUrl(session.id, 'markdown')}
              download={`research_report_${session.id}.md`}
              style={{
                padding: '0.55rem 0.95rem',
                borderRadius: '8px',
                background: 'rgba(59, 130, 246, 0.15)',
                border: '1px solid rgba(59, 130, 246, 0.3)',
                color: '#60A5FA',
                fontSize: '0.82rem',
                fontWeight: 600,
                textDecoration: 'none',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.4rem'
              }}
            >
              <Download size={14} />
              <span>Export Markdown</span>
            </a>

            <a
              href={getExportUrl(session.id, 'pdf')}
              download={`research_report_${session.id}.pdf`}
              style={{
                padding: '0.55rem 0.95rem',
                borderRadius: '8px',
                background: 'var(--gradient-brand)',
                border: 'none',
                color: '#FFFFFF',
                fontSize: '0.82rem',
                fontWeight: 700,
                textDecoration: 'none',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.4rem',
                boxShadow: '0 4px 12px rgba(59, 130, 246, 0.3)'
              }}
            >
              <Download size={14} />
              <span>Export Verified PDF</span>
            </a>
          </div>
        </div>

        {/* Verification Explanation Callout */}
        {report?.verification_explanation && (
          <div style={{
            marginTop: '1rem',
            padding: '0.65rem 0.95rem',
            borderRadius: '8px',
            background: 'rgba(255, 255, 255, 0.03)',
            border: '1px solid var(--border-color)',
            fontSize: '0.8rem',
            color: 'var(--text-secondary)',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem'
          }}>
            <ShieldCheck size={16} color={isVerified ? '#34D399' : '#FBBF24'} style={{ flexShrink: 0 }} />
            <div>
              <strong style={{ color: '#FFFFFF' }}>Verification Summary:</strong> {report.verification_explanation}
            </div>
          </div>
        )}

        {/* Metadata stats pill row */}
        <div style={{
          marginTop: '1.25rem',
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))',
          gap: '0.75rem'
        }}>
          <div style={{ padding: '0.6rem', background: 'rgba(255, 255, 255, 0.02)', borderRadius: '6px', textAlign: 'center' }}>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Verified Citations</div>
            <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#60A5FA' }}>
              {report?.references ? report.references.length : 0}
            </div>
          </div>

          <div style={{ padding: '0.6rem', background: 'rgba(255, 255, 255, 0.02)', borderRadius: '6px', textAlign: 'center' }}>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Claims Corroborated</div>
            <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#34D399' }}>
              {report?.verified_claims_count ?? session.findings.length}
            </div>
          </div>

          <div style={{ padding: '0.6rem', background: 'rgba(255, 255, 255, 0.02)', borderRadius: '6px', textAlign: 'center' }}>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Irrelevant Excluded</div>
            <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#F87171' }}>
              {session.rejected_sources_count ?? 0}
            </div>
          </div>

          <div style={{ padding: '0.6rem', background: 'rgba(255, 255, 255, 0.02)', borderRadius: '6px', textAlign: 'center' }}>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Investigation Time</div>
            <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#C084FC' }}>
              {session.duration_seconds}s
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div style={{
          display: 'flex',
          borderBottom: '1px solid var(--border-color)',
          marginTop: '1.5rem',
          gap: '0.5rem',
          overflowX: 'auto'
        }}>
          <button
            onClick={() => setActiveTab('report')}
            style={{
              padding: '0.65rem 1rem',
              background: 'none',
              border: 'none',
              borderBottom: activeTab === 'report' ? '2px solid #3B82F6' : '2px solid transparent',
              color: activeTab === 'report' ? '#60A5FA' : 'var(--text-secondary)',
              fontSize: '0.85rem',
              fontWeight: 700,
              cursor: 'pointer',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.4rem',
              whiteSpace: 'nowrap'
            }}
          >
            <FileText size={15} />
            <span>Research Report</span>
          </button>

          <button
            onClick={() => setActiveTab('findings')}
            style={{
              padding: '0.65rem 1rem',
              background: 'none',
              border: 'none',
              borderBottom: activeTab === 'findings' ? '2px solid #3B82F6' : '2px solid transparent',
              color: activeTab === 'findings' ? '#60A5FA' : 'var(--text-secondary)',
              fontSize: '0.85rem',
              fontWeight: 700,
              cursor: 'pointer',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.4rem',
              whiteSpace: 'nowrap'
            }}
          >
            <ShieldCheck size={15} />
            <span>Evidence & Claims ({session.findings.length})</span>
          </button>

          <button
            onClick={() => setActiveTab('sources')}
            style={{
              padding: '0.65rem 1rem',
              background: 'none',
              border: 'none',
              borderBottom: activeTab === 'sources' ? '2px solid #3B82F6' : '2px solid transparent',
              color: activeTab === 'sources' ? '#60A5FA' : 'var(--text-secondary)',
              fontSize: '0.85rem',
              fontWeight: 700,
              cursor: 'pointer',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.4rem',
              whiteSpace: 'nowrap'
            }}
          >
            <Globe size={15} />
            <span>Sources Audit ({session.sources.length})</span>
          </button>

          <button
            onClick={() => setActiveTab('references')}
            style={{
              padding: '0.65rem 1rem',
              background: 'none',
              border: 'none',
              borderBottom: activeTab === 'references' ? '2px solid #3B82F6' : '2px solid transparent',
              color: activeTab === 'references' ? '#60A5FA' : 'var(--text-secondary)',
              fontSize: '0.85rem',
              fontWeight: 700,
              cursor: 'pointer',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.4rem',
              whiteSpace: 'nowrap'
            }}
          >
            <ExternalLink size={15} />
            <span>References ({report?.references?.length || 0})</span>
          </button>

          <button
            onClick={() => setActiveTab('followup')}
            style={{
              padding: '0.65rem 1rem',
              background: 'none',
              border: 'none',
              borderBottom: activeTab === 'followup' ? '2px solid #8B5CF6' : '2px solid transparent',
              color: activeTab === 'followup' ? '#C084FC' : 'var(--text-secondary)',
              fontSize: '0.85rem',
              fontWeight: 700,
              cursor: 'pointer',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.4rem',
              whiteSpace: 'nowrap'
            }}
          >
            <MessageSquare size={15} />
            <span>Interactive Follow-ups</span>
          </button>
        </div>
      </div>

      {/* Tab Content */}
      {activeTab === 'report' && report && (
        <div className="glass-card card-padding-lg markdown-body" style={{ lineHeight: 1.7, fontSize: '0.95rem' }}>
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {report.full_markdown}
          </ReactMarkdown>
        </div>
      )}

      {activeTab === 'findings' && (
        <FindingsView findings={session.findings} />
      )}

      {activeTab === 'sources' && (
        <SourcesView sources={session.sources} />
      )}

      {activeTab === 'references' && report?.references && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
          {report.references.map((ref) => (
            <div
              key={ref.id}
              className="glass-card"
              style={{
                padding: '1.1rem',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                flexWrap: 'wrap',
                gap: '0.75rem'
              }}
            >
              <div style={{ flex: 1, minWidth: '240px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.35rem' }}>
                  <span style={{
                    fontSize: '0.75rem',
                    fontWeight: 700,
                    color: '#60A5FA',
                    fontFamily: 'var(--font-mono)'
                  }}>
                    [{ref.id}]
                  </span>
                  <span style={{
                    fontSize: '0.72rem',
                    color: 'var(--text-muted)',
                    background: 'rgba(255, 255, 255, 0.05)',
                    padding: '0.15rem 0.5rem',
                    borderRadius: '4px'
                  }}>
                    {ref.domain}
                  </span>
                  {ref.source_type && (
                    <span style={{
                      fontSize: '0.72rem',
                      color: '#34D399',
                      background: 'rgba(16, 185, 129, 0.1)',
                      padding: '0.15rem 0.5rem',
                      borderRadius: '4px'
                    }}>
                      {ref.source_type}
                    </span>
                  )}
                </div>
                <h4 style={{ fontSize: '0.95rem', fontWeight: 600, color: '#FFFFFF', margin: 0 }}>
                  {ref.title}
                </h4>
              </div>

              <a
                href={ref.url}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.35rem',
                  fontSize: '0.8rem',
                  fontWeight: 600,
                  color: '#60A5FA',
                  textDecoration: 'none',
                  padding: '0.4rem 0.85rem',
                  borderRadius: '6px',
                  background: 'rgba(59, 130, 246, 0.1)',
                  border: '1px solid rgba(59, 130, 246, 0.25)'
                }}
              >
                <span>Visit Reference</span>
                <ExternalLink size={12} />
              </a>
            </div>
          ))}
        </div>
      )}

      {/* Tab 5: Interactive Follow-Up Q&A */}
      {activeTab === 'followup' && (
        <div className="glass-card card-padding-lg">
          <div style={{ marginBottom: '1.5rem' }}>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#FFFFFF', marginBottom: '0.4rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Sparkles size={18} color="#C084FC" />
              <span>Ask Follow-Up Questions About This Research</span>
            </h3>
            <p style={{ fontSize: '0.84rem', color: 'var(--text-secondary)', margin: 0 }}>
              Queries are answered strictly using the report's gathered evidence. When necessary, targeted supplementary web search is executed and explicitly labeled.
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleFollowupSubmit} style={{ marginBottom: '2rem' }}>
            <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '0.75rem' }}>
              <input
                type="text"
                value={followupQuery}
                onChange={(e) => setFollowupQuery(e.target.value)}
                placeholder="Ask a clarifying question (e.g. Which specific OEM aims to commercialize by 2027?)"
                style={{
                  flex: 1,
                  padding: '0.75rem 1rem',
                  borderRadius: '10px',
                  background: 'rgba(15, 23, 42, 0.8)',
                  border: '1px solid var(--border-color)',
                  color: '#FFFFFF',
                  fontSize: '0.9rem'
                }}
              />
              <button
                type="submit"
                disabled={followupLoading || !followupQuery.trim()}
                style={{
                  padding: '0.75rem 1.25rem',
                  borderRadius: '10px',
                  background: 'var(--gradient-brand)',
                  border: 'none',
                  color: '#FFFFFF',
                  fontSize: '0.85rem',
                  fontWeight: 700,
                  cursor: 'pointer',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.4rem',
                  opacity: followupLoading || !followupQuery.trim() ? 0.6 : 1
                }}
              >
                {followupLoading ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}
                <span>{followupLoading ? 'Analyzing...' : 'Ask'}</span>
              </button>
            </div>

            <label style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.78rem', color: 'var(--text-muted)', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={allowNewSearch}
                onChange={(e) => setAllowNewSearch(e.target.checked)}
              />
              <span>Allow automated supplementary web search if existing evidence has gaps</span>
            </label>
          </form>

          {followupError && (
            <div style={{ padding: '0.75rem', borderRadius: '8px', background: 'rgba(239, 68, 68, 0.1)', color: '#F87171', fontSize: '0.82rem', marginBottom: '1.25rem' }}>
              {followupError}
            </div>
          )}

          {/* History */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            {followupList.map((item, idx) => (
              <div
                key={idx}
                style={{
                  padding: '1.25rem',
                  borderRadius: '10px',
                  background: 'rgba(255, 255, 255, 0.02)',
                  border: '1px solid var(--border-color)'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.6rem', gap: '0.5rem' }}>
                  <h4 style={{ fontSize: '0.98rem', fontWeight: 700, color: '#60A5FA', margin: 0 }}>
                    Q: "{item.question}"
                  </h4>
                  <span style={{
                    fontSize: '0.7rem',
                    fontWeight: 600,
                    padding: '0.2rem 0.5rem',
                    borderRadius: '6px',
                    background: item.new_searches_conducted ? 'rgba(139, 92, 246, 0.15)' : 'rgba(16, 185, 129, 0.15)',
                    color: item.new_searches_conducted ? '#C084FC' : '#34D399',
                    border: `1px solid ${item.new_searches_conducted ? 'rgba(139, 92, 246, 0.3)' : 'rgba(16, 185, 129, 0.3)'}`,
                    flexShrink: 0
                  }}>
                    {item.evidence_source}
                  </span>
                </div>

                <div style={{ fontSize: '0.88rem', color: '#E2E8F0', lineHeight: 1.6, whiteSpace: 'pre-wrap' }}>
                  {item.answer}
                </div>
              </div>
            ))}

            {followupList.length === 0 && !followupLoading && (
              <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                No follow-up questions asked yet. Ask any question above to interrogate the report's evidence.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
