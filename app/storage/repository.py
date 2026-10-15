import json
from typing import Optional, List
from app.models.research import ResearchSessionState
from app.storage.database import get_db_connection
from app.utils.logging import get_logger

logger = get_logger("repository")


class ResearchRepository:
    """Repository for persisting and retrieving research session history in SQLite."""

    def save_session(self, state: ResearchSessionState):
        """Saves or updates a research session state."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        json_data = state.model_dump_json()

        cursor.execute("""
            INSERT OR REPLACE INTO research_sessions (
                id, question, mode, status, current_stage, 
                sources_count, findings_count, session_data, 
                created_at, duration_seconds, error_message
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            state.id,
            state.question,
            state.mode,
            state.status,
            state.current_stage,
            state.sources_count,
            state.findings_count,
            json_data,
            state.created_at,
            state.duration_seconds,
            state.error_message
        ))

        conn.commit()
        conn.close()

    def get_session(self, session_id: str) -> Optional[ResearchSessionState]:
        """Retrieves a research session by ID."""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT session_data FROM research_sessions WHERE id = ?", (session_id,))
        row = cursor.fetchone()
        conn.close()

        if row and row["session_data"]:
            data = json.loads(row["session_data"])
            return ResearchSessionState.model_validate(data)
        return None

    def list_sessions(self, limit: int = 50) -> List[ResearchSessionState]:
        """Lists recent research sessions."""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT session_data FROM research_sessions ORDER BY created_at DESC LIMIT ?", 
            (limit,)
        )
        rows = cursor.fetchall()
        conn.close()

        sessions = []
        for row in rows:
            if row["session_data"]:
                data = json.loads(row["session_data"])
                sessions.append(ResearchSessionState.model_validate(data))
        return sessions

    def delete_session(self, session_id: str) -> bool:
        """Deletes a research session by ID."""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM research_sessions WHERE id = ?", (session_id,))
        affected = cursor.rowcount
        conn.commit()
        conn.close()

        return affected > 0
