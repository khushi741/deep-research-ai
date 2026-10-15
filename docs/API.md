# Deep Research AI — API Reference

The FastAPI backend exposes RESTful endpoints for initiating, monitoring, and retrieving deep research runs.

Base URL: `http://localhost:8000`

---

## Endpoints

### 1. Health Check
`GET /health`

Returns application health status and API configuration state.

**Response:**
```json
{
  "status": "healthy",
  "app_name": "Deep Research AI",
  "version": "1.0.0",
  "gemini_api_configured": true,
  "tavily_api_configured": true
}
```

---

### 2. Initiate Research Run
`POST /api/v1/research`

**Request Body:**
```json
{
  "question": "How is generative AI changing software engineering jobs in India in 2026?",
  "mode": "deep",
  "category": "Technology & AI",
  "date_scope": "Past Year (Recent)"
}
```

**Response:**
Returns `ResearchSessionState` object containing initial stage status and session ID.

---

### 3. Get Research Status & Results
`GET /api/v1/research/{session_id}`

Retrieves the complete state of a research session including decomposed plan, extracted findings, and report.

---

### 4. Get Evaluated Sources
`GET /api/v1/research/{session_id}/sources`

Returns list of evaluated web sources with authority scores and credibility signals.

---

### 5. Download Research Report
`GET /api/v1/research/{session_id}/report?format=markdown|pdf|json`

**Parameters:**
- `format` (optional): `json` (default), `markdown`, or `pdf`.

---

### 6. Delete Research Session
`DELETE /api/v1/research/{session_id}`

Deletes a research session from SQLite storage.
