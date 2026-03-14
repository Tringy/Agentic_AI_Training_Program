"""SQLite-backed memory store for the multi-agent system."""

import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import List

DATABASE_PATH = os.getenv("DATABASE_PATH", "/data")
MEMORY_MAX_ENTRIES = int(os.getenv("MEMORY_MAX_ENTRIES", "20"))
MEMORY_TOP_K = int(os.getenv("MEMORY_TOP_K", "3"))

_DB_FILE = os.path.join(DATABASE_PATH, "memory.db")


def _db_path() -> str:
    return os.path.join(os.getenv("DATABASE_PATH", DATABASE_PATH), "memory.db")


@contextmanager
def _get_conn():
    conn = sqlite3.connect(_db_path())
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    """Create the memory table if it doesn't exist."""
    os.makedirs(os.path.dirname(_db_path()), exist_ok=True)
    with _get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS memory (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                task       TEXT    NOT NULL,
                summary    TEXT    NOT NULL,
                created_at TEXT    NOT NULL DEFAULT (datetime('now'))
            )
            """
        )


def save_memory(task: str, summary: str) -> None:
    """Insert a memory entry and prune oldest rows if over the limit."""
    now = datetime.now(timezone.utc).isoformat()
    with _get_conn() as conn:
        conn.execute(
            "INSERT INTO memory (task, summary, created_at) VALUES (?, ?, ?)",
            (task, summary, now),
        )
        # Prune oldest rows exceeding the max
        conn.execute(
            """
            DELETE FROM memory
            WHERE id IN (
                SELECT id FROM memory ORDER BY created_at ASC
                LIMIT MAX(0, (SELECT COUNT(*) FROM memory) - ?)
            )
            """,
            (MEMORY_MAX_ENTRIES,),
        )


def load_memory(top_k: int = MEMORY_TOP_K) -> List[dict]:
    """Return the top_k most recent memory entries."""
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT id, task, summary, created_at FROM memory ORDER BY created_at DESC LIMIT ?",
            (top_k,),
        ).fetchall()
    return [dict(r) for r in rows]


def list_memory() -> List[dict]:
    """Return all memory entries, most recent first."""
    with _get_conn() as conn:
        rows = conn.execute("SELECT id, task, summary, created_at FROM memory ORDER BY created_at DESC").fetchall()
    return [dict(r) for r in rows]


def delete_all_memory() -> int:
    """Delete all memory entries. Returns the count deleted."""
    with _get_conn() as conn:
        cursor = conn.execute("DELETE FROM memory")
        return cursor.rowcount
