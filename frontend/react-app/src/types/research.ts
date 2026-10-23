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
  is_included?: boolean;
  exclusion_reason?: string;
  corroborating_claims?: string[];
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
  corroboration_count?: number;
  verification_status?: 'Verified' | 'Disputed' | 'Uncorroborated';
}

export interface Citation {
  id: number;
  url: string;
  title: string;
  domain: string;
  published_date?: string;
  relevance_score?: number;
  authority_score?: number;
  source_type?: string;
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
  verification_badge?: string;
  verification_explanation?: string;
  total_claims_count?: number;
  verified_claims_count?: number;
  rejected_sources_count?: number;
}

export interface FollowupItem {
  question: string;
  answer: string;
  evidence_source: string;
  new_searches_conducted: boolean;
  timestamp?: number;
}

export interface FollowupResponse {
  question: string;
  answer: string;
  cited_references: Citation[];
  new_searches_conducted: boolean;
  evidence_source: string;
}

export interface ResearchSessionState {
  id: string;
  question: string;
  mode: string;
  status: 'pending' | 'planning' | 'searching' | 'extracting' | 'evaluating' | 'synthesizing' | 'completed' | 'failed' | 'cancelled';
  current_stage: string;
  progress_percent?: number;
  plan?: ResearchPlan;
  sources_count: number;
  findings_count: number;
  completed_queries_count?: number;
  total_queries_count?: number;
  rejected_sources_count?: number;
  completed_stages?: string[];
  sources: SourceEvaluation[];
  findings: Finding[];
  report?: ResearchReport;
  created_at: string;
  duration_seconds: number;
  error_message?: string;
  is_cancelled?: boolean;
  followup_history?: FollowupItem[];
}

export interface HealthResponse {
  status: string;
  app_name: string;
  version: string;
  gemini_api_configured: boolean;
  tavily_api_configured: boolean;
}
