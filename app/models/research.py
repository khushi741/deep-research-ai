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


class Finding(BaseModel):
    id: str
    claim: str
    evidence_excerpt: str
    source_urls: List[str]
    subquestion_id: str
    confidence_level: str = Field(default="Medium", description="High, Medium, or Low")
    confidence_explanation: str
    relevant_dates: Optional[str] = None


class Citation(BaseModel):
    id: int
    url: str
    title: str
    domain: str
    published_date: Optional[str] = None


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


class ResearchRequest(BaseModel):
    question: str = Field(min_length=5, max_length=500)
    mode: str = Field(default="quick", description="quick or deep")
    category: Optional[str] = None
    date_scope: Optional[str] = None


class ResearchSessionState(BaseModel):
    id: str
    question: str
    mode: str
    status: str  # pending, planning, searching, extracting, evaluating, synthesizing, completed, failed
    current_stage: str
    plan: Optional[ResearchPlan] = None
    sources_count: int = 0
    findings_count: int = 0
    sources: List[SourceEvaluation] = Field(default_factory=list)
    findings: List[Finding] = Field(default_factory=list)
    report: Optional[ResearchReport] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    duration_seconds: float = 0.0
    error_message: Optional[str] = None
