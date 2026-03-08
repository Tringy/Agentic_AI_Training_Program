"""SQLite persistence for migration jobs."""

import dataclasses
import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

from state import MigrationState, MigrationStep, Phase, RollbackRecord, Snapshot

DB_PATH = Path(os.getenv("DB_PATH", "/data/jobs.db"))


def _ensure_dir() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def init_db() -> None:
    """Create the jobs table if it doesn't exist."""
    _ensure_dir()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                job_id   TEXT PRIMARY KEY,
                state_json TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def _to_json(state: MigrationState) -> str:
    d = dataclasses.asdict(state)
    d["phase"] = state.phase.value  # enum -> string
    return json.dumps(d)


def _from_json(s: str) -> MigrationState:
    d = json.loads(s)
    plan = [MigrationStep(**step) for step in d.pop("plan", [])]
    snapshots = [Snapshot(**snap) for snap in d.pop("snapshots", [])]
    rollback_history = [RollbackRecord(**rec) for rec in d.pop("rollback_history", [])]
    d["phase"] = Phase(d["phase"])
    d["plan"] = plan
    d["snapshots"] = snapshots
    d["rollback_history"] = rollback_history
    return MigrationState(**d)


def save_job(state: MigrationState) -> None:
    """Upsert a job's state to the database."""
    now = datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT OR REPLACE INTO jobs (job_id, state_json, updated_at) VALUES (?, ?, ?)",
            (state.job_id, _to_json(state), now),
        )
        conn.commit()


def delete_job(job_id: str) -> None:
    """Remove a job from the database."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM jobs WHERE job_id = ?", (job_id,))
        conn.commit()


def load_all_jobs() -> Dict[str, MigrationState]:
    """Load all persisted jobs; returns empty dict if DB doesn't exist yet."""
    if not DB_PATH.exists():
        return {}
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute("SELECT job_id, state_json FROM jobs").fetchall()
    jobs: Dict[str, MigrationState] = {}
    for job_id, state_json in rows:
        try:
            jobs[job_id] = _from_json(state_json)
        except Exception:
            pass  # skip corrupted rows
    return jobs
