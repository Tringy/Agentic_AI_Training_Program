"""Dynamic agent registry for the multi-agent system."""

import os
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Dict, List, Optional

_DATABASE_PATH = os.getenv("DATABASE_PATH", "/data")


def _db_path() -> str:
    return os.path.join(os.getenv("DATABASE_PATH", _DATABASE_PATH), "memory.db")


@contextmanager
def _get_conn():
    conn = sqlite3.connect(_db_path())
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_agents_table() -> None:
    """Create the agents table if it doesn't exist."""
    os.makedirs(os.path.dirname(_db_path()), exist_ok=True)
    with _get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS agents (
                name          TEXT PRIMARY KEY,
                system_prompt TEXT NOT NULL,
                description   TEXT NOT NULL
            )
            """
        )


@dataclass
class AgentDefinition:
    name: str
    system_prompt: str
    description: str
    builtin: bool = False


class AgentRegistry:
    def __init__(self):
        self._agents: Dict[str, AgentDefinition] = {}

    # ------------------------------------------------------------------
    # In-memory operations (always used)
    # ------------------------------------------------------------------

    def register(self, defn: AgentDefinition, persist: bool = False) -> None:
        """Add an agent to the registry. Pass persist=True for custom agents."""
        self._agents[defn.name] = defn
        if persist and not defn.builtin:
            with _get_conn() as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO agents (name, system_prompt, description) VALUES (?, ?, ?)",
                    (defn.name, defn.system_prompt, defn.description),
                )

    def get(self, name: str) -> Optional[AgentDefinition]:
        return self._agents.get(name)

    def get_case_insensitive(self, name: str) -> Optional[AgentDefinition]:
        lower = name.lower()
        for k, v in self._agents.items():
            if k.lower() == lower:
                return v
        return None

    def list(self) -> List[AgentDefinition]:
        return list(self._agents.values())

    def delete(self, name: str) -> bool:
        """Delete a custom agent. Returns False if builtin, raises KeyError if not found."""
        defn = self._agents.get(name)
        if defn is None:
            raise KeyError(name)
        if defn.builtin:
            return False
        del self._agents[name]
        with _get_conn() as conn:
            conn.execute("DELETE FROM agents WHERE name = ?", (name,))
        return True

    def names(self) -> List[str]:
        return list(self._agents.keys())

    def load_persisted(self) -> None:
        """Load previously saved custom agents from SQLite (called at startup)."""
        try:
            with _get_conn() as conn:
                rows = conn.execute("SELECT name, system_prompt, description FROM agents").fetchall()
            for row in rows:
                defn = AgentDefinition(
                    name=row["name"],
                    system_prompt=row["system_prompt"],
                    description=row["description"],
                    builtin=False,
                )
                self._agents[defn.name] = defn
        except Exception:
            pass  # table may not exist yet; init_agents_table() creates it


# ---------------------------------------------------------------------------
# Module-level singleton populated at startup in main.py lifespan
# ---------------------------------------------------------------------------

registry = AgentRegistry()
