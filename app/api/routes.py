import os
import asyncio
import json
from typing import Optional, List
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query, Response
from fastapi.responses import Response, JSONResponse, StreamingResponse
from app.config import settings
from app.api.schemas import HealthResponse, ResearchResponse, SourcesResponse, ErrorResponse
from app.models.research import (
    ResearchRequest, 
    ResearchSessionState, 
    FollowupRequest, 
    FollowupResponse
)
from app.services.research_orchestrator import ResearchOrchestrator
from app.services.export_service import ExportService
from app.storage.repository import ResearchRepository
from app.utils.logging import get_logger

logger = get_logger("routes")

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
        gemini_api_configured=bool(gemini_key and not gemini_key.startswith("your_")),
        tavily_api_configured=bool(tavily_key and not tavily_key.startswith("your_"))
    )


@router.post("/api/v1/research", response_model=ResearchSessionState, tags=["Research"])
async def start_research(request: ResearchRequest, background_tasks: BackgroundTasks):
    """Initiates an autonomous research run asynchronously with live progress tracking."""
    if len(request.question.strip()) < 5:
        raise HTTPException(status_code=400, detail="Research question must be at least 5 characters long.")
    if len(request.question) > settings.MAX_QUERY_LENGTH:
        raise HTTPException(
            status_code=400, 
            detail=f"Research question exceeds maximum allowed length of {settings.MAX_QUERY_LENGTH} chars."
        )

    import uuid
    session_id = str(uuid.uuid4())
    initial_state = ResearchSessionState(
        id=session_id,
        question=request.question,
        mode=request.mode,
        status="planning",
        current_stage="Stage 1/6: Formulating Research Plan & Search Vectors",
        progress_percent=5
    )
    repository.save_session(initial_state)

    async def execute_pipeline(sid: str, req: ResearchRequest):
        def save_cb(st: ResearchSessionState):
            repository.save_session(st)
        try:
            final_st = await orchestrator.run_research(req, session_id=sid, progress_callback=save_cb)
            repository.save_session(final_st)
        except Exception as e:
            logger.error(f"Async pipeline execution failed for {sid}: {str(e)}", exc_info=True)
            err_state = repository.get_session(sid) or initial_state
            err_state.status = "failed"
            err_state.error_message = str(e)
            repository.save_session(err_state)

    background_tasks.add_task(execute_pipeline, session_id, request)
    return initial_state


@router.get("/api/v1/research", response_model=List[ResearchSessionState], tags=["Research"])
async def list_research_sessions(
    limit: int = Query(50, ge=1, le=100),
    q: Optional[str] = Query(None, description="Search previous queries"),
    mode: Optional[str] = Query(None, enum=["quick", "deep"])
):
    """Lists saved research reports with search filtering."""
    sessions = repository.list_sessions(limit=limit)
    if q:
        query_lower = q.lower()
        sessions = [s for s in sessions if query_lower in s.question.lower()]
    if mode:
        sessions = [s for s in sessions if s.mode == mode]
    return sessions


@router.get("/api/v1/research/{session_id}", response_model=ResearchSessionState, tags=["Research"])
async def get_research_status(session_id: str):
    """Retrieves status and full result of a research session."""
    session = repository.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Research session '{session_id}' not found.")
    return session


@router.post("/api/v1/research/{session_id}/cancel", tags=["Research"])
async def cancel_research(session_id: str):
    """Cancels an ongoing research run."""
    session = repository.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Research session '{session_id}' not found.")
    
    orchestrator.cancel_research(session_id)
    session.status = "cancelled"
    session.is_cancelled = True
    session.current_stage = "Research Cancelled by User"
    repository.save_session(session)
    return {"status": "cancelled", "session_id": session_id}


@router.post("/api/v1/research/{session_id}/followup", response_model=FollowupResponse, tags=["Research"])
async def research_followup(session_id: str, request: FollowupRequest):
    """Answers follow-up questions grounded in the completed report's evidence."""
    session = repository.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Research session '{session_id}' not found.")
    if session.status != "completed" or not session.report:
        raise HTTPException(
            status_code=400, 
            detail="Research report must be fully completed before asking follow-up questions."
        )

    try:
        response = await orchestrator.answer_followup(session, request)
        # Store in session followup history
        session.followup_history.append({
            "question": response.question,
            "answer": response.answer,
            "evidence_source": response.evidence_source,
            "new_searches_conducted": response.new_searches_conducted,
            "timestamp": asyncio.get_event_loop().time()
        })
        repository.save_session(session)
        return response
    except Exception as e:
        logger.error(f"Followup answering failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate follow-up answer: {str(e)}")


@router.get("/api/v1/research/{session_id}/events", tags=["Research"])
async def stream_research_events(session_id: str):
    """Streams live Server-Sent Events (SSE) for research session progress."""
    async def event_generator():
        last_stage = None
        last_progress = -1

        for _ in range(240):  # Stream for up to 120 seconds (0.5s intervals)
            session = repository.get_session(session_id)
            if not session:
                yield f"data: {json.dumps({'error': 'Session not found'})}\n\n"
                break

            # Yield event if stage or progress changed, or if terminal state reached
            if session.current_stage != last_stage or session.progress_percent != last_progress or session.status in {"completed", "failed", "cancelled"}:
                last_stage = session.current_stage
                last_progress = session.progress_percent
                payload = {
                    "id": session.id,
                    "status": session.status,
                    "stage": session.current_stage,
                    "progress": session.progress_percent,
                    "sources_count": session.sources_count,
                    "findings_count": session.findings_count,
                    "completed_queries": session.completed_queries_count,
                    "total_queries": session.total_queries_count,
                    "rejected_sources": session.rejected_sources_count,
                    "duration_seconds": session.duration_seconds
                }
                yield f"data: {json.dumps(payload)}\n\n"

            if session.status in {"completed", "failed", "cancelled"}:
                break

            await asyncio.sleep(0.5)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/api/v1/research/{session_id}/sources", response_model=SourcesResponse, tags=["Research"])
async def get_research_sources(session_id: str):
    """Retrieves list of evaluated sources (both accepted and excluded) with full reasoning."""
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
    """Retrieves generated report in JSON, Markdown, or PDF format with honest verification badge."""
    session = repository.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Research session '{session_id}' not found.")
    if not session.report:
        raise HTTPException(status_code=400, detail="Report generation is not complete or failed for this session.")

    if format == "markdown":
        md_bytes = ExportService.generate_markdown_bytes(session.report)
        return Response(
            content=md_bytes,
            media_type="text/markdown; charset=utf-8",
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
