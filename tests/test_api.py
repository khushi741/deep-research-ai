from fastapi.testclient import TestClient
from app.main import app
from app.storage.database import init_db

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
