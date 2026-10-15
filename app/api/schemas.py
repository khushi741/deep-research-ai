from typing import Optional, List
from pydantic import BaseModel, Field
from app.models.research import ResearchSessionState, SourceEvaluation, ResearchReport


class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str
    gemini_api_configured: bool
    tavily_api_configured: bool


class ResearchResponse(BaseModel):
    id: str
    question: str
    mode: str
    status: str
    current_stage: str
    sources_count: int
    findings_count: int
    duration_seconds: float
    created_at: str
    report: Optional[ResearchReport] = None
    error_message: Optional[str] = None


class SourcesResponse(BaseModel):
    session_id: str
    count: int
    sources: List[SourceEvaluation]


class ErrorResponse(BaseModel):
    error: str
    detail: str
