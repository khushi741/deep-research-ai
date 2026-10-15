import sqlite3
import os
from typing import Optional
from app.config import settings
from app.utils.logging import get_logger

logger = get_logger("database")

DB_PATH = settings.DATABASE_URL.replace("sqlite:///", "")


def get_db_connection() -> sqlite3.Connection:
    """Creates a connection to SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes SQLite database tables."""
    logger.info(f"Initializing database schema at '{DB_PATH}'")
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS research_sessions (
            id TEXT PRIMARY KEY,
            question TEXT NOT NULL,
            mode TEXT NOT NULL,
            status TEXT NOT NULL,
            current_stage TEXT NOT NULL,
            sources_count INTEGER DEFAULT 0,
            findings_count INTEGER DEFAULT 0,
            session_data JSON NOT NULL,
            created_at TEXT NOT NULL,
            duration_seconds REAL DEFAULT 0.0,
            error_message TEXT
        )
    """)

    conn.commit()
    conn.close()
