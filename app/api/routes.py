import os
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query, Response
from fastapi.responses import Response, JSONResponse
from app.config import settings
from app.api.schemas import HealthResponse, ResearchResponse, SourcesResponse, ErrorResponse
from app.models.research import ResearchRequest, ResearchSessionState
from app.services.research_orchestrator import ResearchOrchestrator
from app.services.export_service import ExportService
from app.storage.repository import ResearchRepository
from app.providers.gemini_provider import GeminiLLMProvider

router = APIRouter()
repository = ResearchRepository()
orchestrator = ResearchOrchestrator()


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Returns application health status and API key configuration state."""
    gemini_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
    tavily_key = settings.TAVILY_API_KEY or os.getenv("TAVILY_API_KEY")

    return HealthResponse(
        status="healthy",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        gemini_api_configured=bool(gemini_key),
        tavily_api_configured=bool(tavily_key)
    )


@router.post("/api/v1/research", response_model=ResearchSessionState, tags=["Research"])
async def start_research(request: ResearchRequest, background_tasks: BackgroundTasks):
    """Initiates a new research run."""
    if len(request.question.strip()) < 5:
        raise HTTPException(status_code=400, detail="Research question must be at least 5 characters long.")
    if len(request.question) > settings.MAX_QUERY_LENGTH:
        raise HTTPException(status_code=400, detail=f"Research question exceeds maximum allowed length of {settings.MAX_QUERY_LENGTH} chars.")

    # Execute research run
    def save_cb(state: ResearchSessionState):
        repository.save_session(state)

    state = await orchestrator.run_research(request, progress_callback=save_cb)
    repository.save_session(state)
    return state


@router.get("/api/v1/research/{session_id}", response_model=ResearchSessionState, tags=["Research"])
async def get_research_status(session_id: str):
    """Retrieves status and full result of a research session."""
    session = repository.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Research session '{session_id}' not found.")
    return session


@router.get("/api/v1/research/{session_id}/sources", response_model=SourcesResponse, tags=["Research"])
async def get_research_sources(session_id: str):
    """Retrieves list of evaluated sources for a research session."""
    session = repository.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Research session '{session_id}' not found.")
    
    return SourcesResponse(
        session_id=session.id,
        count=len(session.sources),
        sources=session.sources
    )


@router.get("/api/v1/research/{session_id}/report", tags=["Research"])
async def get_research_report(session_id: str, format: str = Query("json", enum=["json", "markdown", "pdf"])):
    """Retrieves generated report in JSON, Markdown, or PDF format."""
    session = repository.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Research session '{session_id}' not found.")
    if not session.report:
        raise HTTPException(status_code=400, detail="Report generation is not complete or failed for this session.")

    if format == "markdown":
        md_bytes = ExportService.generate_markdown_bytes(session.report)
        return Response(
            content=md_bytes,
            media_type="text/markdown",
            headers={"Content-Disposition": f"attachment; filename=research_report_{session_id}.md"}
        )
    elif format == "pdf":
        pdf_bytes = ExportService.generate_pdf_bytes(session.report)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=research_report_{session_id}.pdf"}
        )

    return session.report


@router.delete("/api/v1/research/{session_id}", tags=["Research"])
async def delete_research_session(session_id: str):
    """Deletes a research session from history."""
    deleted = repository.delete_session(session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Research session '{session_id}' not found.")
    return {"status": "deleted", "session_id": session_id}
