from fastapi.testclient import TestClient
from app.main import app
from app.storage.database import init_db
from app.models.research import ResearchSessionState, ResearchReport, Citation

# Initialize database schema for test environment
init_db()

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "app_name" in data
    assert "gemini_api_configured" in data


def test_invalid_query_validation():
    # Query too short (< 5 chars) triggers Pydantic schema validation error (HTTP 422)
    response = client.post("/api/v1/research", json={"question": "tiny"})
    assert response.status_code == 422


def test_nonexistent_session_404():
    response = client.get("/api/v1/research/nonexistent-id-12345")
    assert response.status_code == 404


def test_list_research_sessions():
    response = client.get("/api/v1/research")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


from unittest.mock import patch, AsyncMock
from app.api.routes import orchestrator


def test_cancel_research_session():
    # Mock background task so it doesn't execute live search in unit tests
    with patch.object(orchestrator, "run_research", new_callable=AsyncMock):
        create_res = client.post("/api/v1/research", json={"question": "What is solid-state battery commercialization timeline?", "mode": "quick"})
        assert create_res.status_code == 200
        sid = create_res.json()["id"]

        cancel_res = client.post(f"/api/v1/research/{sid}/cancel")
        assert cancel_res.status_code == 200
        assert cancel_res.json()["status"] == "cancelled"

        # Status check
        st_res = client.get(f"/api/v1/research/{sid}")
        assert st_res.status_code == 200
        assert st_res.json()["status"] == "cancelled"


def test_report_export_endpoints():
    from app.storage.repository import ResearchRepository
    repo = ResearchRepository()
    test_session = ResearchSessionState(
        id="test-export-sid-999",
        question="What is the future of EV battery chemistry?",
        mode="quick",
        status="completed",
        current_stage="Research Completed Successfully",
        report=ResearchReport(
            title="Future of EV Battery Chemistry",
            executive_summary="Summary of EV battery advances.",
            methodology="Autonomous search and extraction.",
            key_findings=["Finding 1: High energy density", "Finding 2: Sulfide electrolytes"],
            detailed_analysis="Comprehensive analysis [1].",
            evidence_and_citations="Evaluated evidence.",
            conflicting_evidence_and_limitations="High production costs.",
            unanswered_questions="Recycling yields.",
            conclusion="Outlook remains robust.",
            references=[
                Citation(id=1, url="https://example.com/paper", title="Battery Paper", domain="example.com")
            ],
            full_markdown="# Future of EV Battery Chemistry\n\nExecutive summary...",
            verification_badge="Verified",
            verification_explanation="Corroborated across primary sources."
        )
    )
    repo.save_session(test_session)

    # Test Markdown export
    md_res = client.get("/api/v1/research/test-export-sid-999/report?format=markdown")
    assert md_res.status_code == 200
    assert "text/markdown" in md_res.headers["content-type"]
    assert len(md_res.content) > 0

    # Test PDF export
    pdf_res = client.get("/api/v1/research/test-export-sid-999/report?format=pdf")
    assert pdf_res.status_code == 200
    assert "application/pdf" in pdf_res.headers["content-type"]
    assert pdf_res.content.startswith(b"%PDF")
