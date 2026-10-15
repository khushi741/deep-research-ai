import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import type { ResearchSessionState } from '../types/research';
import { SourcesView } from './SourcesView';
import { FindingsView } from './FindingsView';
import { getExportUrl } from '../services/api';
import { FileText, Download, Globe, ShieldCheck, Clock, CheckCircle2, RotateCcw, ExternalLink } from 'lucide-react';

interface ReportViewerProps {
  session: ResearchSessionState;
  onNewResearch: () => void;
}

export const ReportViewer: React.FC<ReportViewerProps> = ({ session, onNewResearch }) => {
  const [activeTab, setActiveTab] = useState<'report' | 'sources' | 'findings' | 'references'>('report');

  const report = session.report;

  return (
    <div style={{ maxWidth: '1100px', margin: '2.5rem auto', padding: '0 1.5rem' }}>
      {/* Header Banner */}
      <div className="glass-card" style={{ padding: '2rem', marginBottom: '2rem' }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: '1rem', marginBottom: '1rem' }}>
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.4rem',
            padding: '0.3rem 0.75rem',
            borderRadius: '20px',
            background: 'rgba(16, 185, 129, 0.15)',
            color: '#34D399',
            fontSize: '0.8rem',
            fontWeight: 700
          }}>
            <CheckCircle2 size={14} />
            <span>Autonomous Synthesis Complete</span>
          </div>

          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <button
              onClick={onNewResearch}
              style={{
                padding: '0.55rem 1rem',
                borderRadius: '8px',
                background: 'rgba(255, 255, 255, 0.06)',
                border: '1px solid var(--border-color)',
                color: '#FFFFFF',
                fontSize: '0.85rem',
                fontWeight: 600,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '0.4rem'
              }}
            >
              <RotateCcw size={14} />
              New Research
            </button>

            {/* Download Buttons */}
            <a
              href={getExportUrl(session.id, 'markdown')}
              download={`research_report_${session.id}.md`}
              style={{
                padding: '0.55rem 1rem',
                borderRadius: '8px',
                background: 'rgba(59, 130, 246, 0.15)',
                border: '1px solid rgba(59, 130, 246, 0.3)',
                color: '#60A5FA',
                fontSize: '0.85rem',
                fontWeight: 600,
                textDecoration: 'none',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.4rem'
              }}
            >
              <Download size={14} />
              Export Markdown
            </a>

            <a
              href={getExportUrl(session.id, 'pdf')}
              download={`research_report_${session.id}.pdf`}
              style={{
                padding: '0.55rem 1rem',
                borderRadius: '8px',
                background: 'var(--gradient-brand)',
                border: 'none',
                color: '#FFFFFF',
                fontSize: '0.85rem',
                fontWeight: 700,
                textDecoration: 'none',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.4rem',
                boxShadow: '0 4px 12px rgba(59, 130, 246, 0.3)'
              }}
            >
              <Download size={14} />
              Download PDF
            </a>
          </div>
        </div>

        <h2 style={{ fontSize: '2rem', fontWeight: 800, color: '#FFFFFF', lineHeight: 1.3, marginBottom: '1.25rem' }}>
          {report?.title || session.question}
        </h2>

        {/* Executive Stats Bar */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
          gap: '1rem',
          background: 'rgba(15, 23, 42, 0.8)',
          padding: '1rem 1.25rem',
          borderRadius: '12px',
          border: '1px solid var(--border-color)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <Globe size={20} color="#60A5FA" />
            <div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Evaluated Sources</div>
              <div style={{ fontSize: '1.1rem', fontWeight: 800, color: '#FFFFFF' }}>{session.sources_count} Web Pages</div>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <ShieldCheck size={20} color="#C084FC" />
            <div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Extracted Evidence</div>
              <div style={{ fontSize: '1.1rem', fontWeight: 800, color: '#FFFFFF' }}>{session.findings_count} Claims</div>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <Clock size={20} color="#34D399" />
            <div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Duration</div>
              <div style={{ fontSize: '1.1rem', fontWeight: 800, color: '#FFFFFF' }}>{session.duration_seconds.toFixed(1)}s</div>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs Navigation */}
      <div style={{
        display: 'flex',
        gap: '0.5rem',
        marginBottom: '1.5rem',
        borderBottom: '1px solid var(--border-color)',
        paddingBottom: '0.5rem'
      }}>
        {[
          { id: 'report', label: 'Full Research Report', icon: FileText },
          { id: 'sources', label: `Sources (${session.sources_count})`, icon: Globe },
          { id: 'findings', label: `Evidence & Claims (${session.findings_count})`, icon: ShieldCheck },
          { id: 'references', label: `References (${report?.references?.length || 0})`, icon: ExternalLink },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              style={{
                padding: '0.65rem 1.25rem',
                borderRadius: '8px',
                border: 'none',
                background: isActive ? 'rgba(59, 130, 246, 0.15)' : 'transparent',
                color: isActive ? '#FFFFFF' : 'var(--text-muted)',
                fontSize: '0.9rem',
                fontWeight: isActive ? 700 : 500,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                transition: 'all 0.2s',
                borderBottom: isActive ? '2px solid var(--accent-primary)' : '2px solid transparent'
              }}
            >
              <Icon size={16} color={isActive ? '#60A5FA' : 'var(--text-muted)'} />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Tab Content */}
      <div>
        {activeTab === 'report' && (
          <div className="glass-card" style={{ padding: '2.5rem' }}>
            <div className="markdown-body">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {report?.full_markdown || 'No report content generated.'}
              </ReactMarkdown>
            </div>
          </div>
        )}

        {activeTab === 'sources' && (
          <SourcesView sources={session.sources} />
        )}

        {activeTab === 'findings' && (
          <FindingsView findings={session.findings} />
        )}

        {activeTab === 'references' && (
          <div className="glass-card" style={{ padding: '2rem' }}>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#FFFFFF', marginBottom: '1.25rem' }}>
              Verified Source References
            </h3>
            {report?.references && report.references.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
                {report.references.map((ref) => (
                  <div
                    key={ref.id}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '0.85rem 1.25rem',
                      borderRadius: '8px',
                      background: 'rgba(15, 23, 42, 0.6)',
                      border: '1px solid var(--border-color)'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                      <span style={{
                        fontSize: '0.8rem',
                        fontWeight: 700,
                        color: '#60A5FA',
                        fontFamily: 'var(--font-mono)',
                        background: 'rgba(59, 130, 246, 0.1)',
                        padding: '0.2rem 0.5rem',
                        borderRadius: '4px'
                      }}>
                        [{ref.id}]
                      </span>

                      <div>
                        <div style={{ fontSize: '0.95rem', fontWeight: 600, color: '#FFFFFF' }}>
                          {ref.title}
                        </div>
                        <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                          {ref.domain} {ref.published_date ? `• ${ref.published_date}` : ''}
                        </div>
                      </div>
                    </div>

                    <a
                      href={ref.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '0.3rem',
                        fontSize: '0.8rem',
                        color: '#60A5FA',
                        textDecoration: 'none'
                      }}
                    >
                      <span>Open Link</span>
                      <ExternalLink size={12} />
                    </a>
                  </div>
                ))}
              </div>
            ) : (
              <p style={{ color: 'var(--text-muted)' }}>No explicit citations listed.</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
