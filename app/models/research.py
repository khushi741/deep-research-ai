from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class SubQuestion(BaseModel):
    id: str = Field(description="Unique ID for subquestion, e.g., sq_1")
    question: str = Field(description="The subquestion text")
    search_queries: List[str] = Field(default_factory=list, description="Targeted web search queries")


class ResearchPlan(BaseModel):
    refined_question: str = Field(description="Refined and unambiguous version of user query")
    main_objectives: List[str] = Field(default_factory=list, description="Core objectives of research")
    subquestions: List[SubQuestion] = Field(default_factory=list, description="3 to 6 focused subquestions")
    time_scope: Optional[str] = Field(default=None, description="Time boundary if applicable")
    geographic_scope: Optional[str] = Field(default=None, description="Geographic focus if applicable")


class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str
    published_date: Optional[str] = None
    source_metadata: Dict[str, Any] = Field(default_factory=dict)


class ExtractedContent(BaseModel):
    url: str
    title: str
    content: str
    domain: str
    published_date: Optional[str] = None
    retrieved_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    error: Optional[str] = None


class SourceEvaluation(BaseModel):
    url: str
    title: str
    domain: str
    relevance_score: float = Field(ge=0.0, le=1.0, description="Relevance from 0 to 1")
    authority_score: float = Field(ge=0.0, le=1.0, description="Assessable publisher authority")
    source_type: str = Field(default="Secondary", description="Primary, Secondary, Opinion, Academic, etc.")
    credibility_signals: List[str] = Field(default_factory=list)
    reasoning: str = Field(description="Transparent evaluation rationale")
    published_date: Optional[str] = None
    is_included: bool = Field(default=True, description="Whether source passed relevance threshold")
    exclusion_reason: Optional[str] = Field(default=None, description="Detailed reason if excluded")
    corroborating_claims: List[str] = Field(default_factory=list, description="IDs of claims supported")


class Finding(BaseModel):
    id: str
    claim: str
    evidence_excerpt: str
    source_urls: List[str]
    subquestion_id: str
    confidence_level: str = Field(default="Medium", description="High, Medium, or Low")
    confidence_explanation: str
    relevant_dates: Optional[str] = None
    corroboration_count: int = Field(default=1, description="Number of distinct corroborating sources")
    verification_status: str = Field(default="Verified", description="Verified, Disputed, or Uncorroborated")


class Citation(BaseModel):
    id: int
    url: str
    title: str
    domain: str
    published_date: Optional[str] = None
    relevance_score: Optional[float] = None
    authority_score: Optional[float] = None
    source_type: Optional[str] = None


class ResearchReport(BaseModel):
    title: str
    executive_summary: str
    methodology: str
    key_findings: List[str]
    detailed_analysis: str
    evidence_and_citations: str
    conflicting_evidence_and_limitations: str
    unanswered_questions: str
    conclusion: str
    references: List[Citation]
    full_markdown: str
    verification_badge: str = Field(default="Partial Evidence", description="Verified, Partial Evidence, or Unverified Claims")
    verification_explanation: str = Field(default="", description="Truthful explanation of evidence support and coverage")
    total_claims_count: int = 0
    verified_claims_count: int = 0
    rejected_sources_count: int = 0


class ResearchRequest(BaseModel):
    question: str = Field(min_length=5, max_length=500)
    mode: str = Field(default="quick", description="quick or deep")
    category: Optional[str] = None
    date_scope: Optional[str] = None
    min_relevance: float = Field(default=0.45, ge=0.0, le=1.0)
    source_types: Optional[List[str]] = None
    domains_whitelist: Optional[List[str]] = None


class FollowupRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)
    allow_new_search: bool = Field(default=True)


class FollowupResponse(BaseModel):
    question: str
    answer: str
    cited_references: List[Citation] = Field(default_factory=list)
    new_searches_conducted: bool = False
    evidence_source: str = Field(default="Existing Report Evidence")  # Existing vs Newly Retrieved


class ResearchSessionState(BaseModel):
    id: str
    question: str
    mode: str
    status: str  # pending, planning, searching, extracting, evaluating, synthesizing, completed, failed, cancelled
    current_stage: str
    progress_percent: int = 0
    plan: Optional[ResearchPlan] = None
    sources_count: int = 0
    findings_count: int = 0
    completed_queries_count: int = 0
    total_queries_count: int = 0
    rejected_sources_count: int = 0
    completed_stages: List[str] = Field(default_factory=list)
    sources: List[SourceEvaluation] = Field(default_factory=list)
    findings: List[Finding] = Field(default_factory=list)
    report: Optional[ResearchReport] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    duration_seconds: float = 0.0
    error_message: Optional[str] = None
    is_cancelled: bool = False
    followup_history: List[Dict[str, Any]] = Field(default_factory=list)
