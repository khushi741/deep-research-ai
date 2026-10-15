export interface SubQuestion {
  id: string;
  question: string;
  search_queries: string[];
}

export interface ResearchPlan {
  refined_question: string;
  main_objectives: string[];
  subquestions: SubQuestion[];
  time_scope?: string;
  geographic_scope?: string;
}

export interface SourceEvaluation {
  url: string;
  title: string;
  domain: string;
  relevance_score: number;
  authority_score: number;
  source_type: string;
  credibility_signals: string[];
  reasoning: string;
  published_date?: string;
}

export interface Finding {
  id: string;
  claim: string;
  evidence_excerpt: string;
  source_urls: string[];
  subquestion_id: string;
  confidence_level: 'High' | 'Medium' | 'Low';
  confidence_explanation: string;
  relevant_dates?: string;
}

export interface Citation {
  id: number;
  url: string;
  title: string;
  domain: string;
  published_date?: string;
}

export interface ResearchReport {
  title: string;
  executive_summary: string;
  methodology: string;
  key_findings: string[];
  detailed_analysis: string;
  evidence_and_citations: string;
  conflicting_evidence_and_limitations: string;
  unanswered_questions: string;
  conclusion: string;
  references: Citation[];
  full_markdown: string;
}

export interface ResearchSessionState {
  id: string;
  question: string;
  mode: string;
  status: 'pending' | 'planning' | 'searching' | 'extracting' | 'evaluating' | 'synthesizing' | 'completed' | 'failed';
  current_stage: string;
  plan?: ResearchPlan;
  sources_count: number;
  findings_count: number;
  sources: SourceEvaluation[];
  findings: Finding[];
  report?: ResearchReport;
  created_at: string;
  duration_seconds: number;
  error_message?: string;
}

export interface HealthResponse {
  status: string;
  app_name: string;
  version: string;
  gemini_api_configured: boolean;
  tavily_api_configured: boolean;
}
