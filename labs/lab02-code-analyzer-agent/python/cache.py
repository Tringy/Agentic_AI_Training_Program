"""In-memory LLM analysis cache with TTL expiry."""

import hashlib
import os
import time
from typing import Any


class AnalysisCache:
    """Thread-safe in-memory cache for LLM analysis results."""

    def __init__(self) -> None:
        self._store: dict[str, dict[str, Any]] = {}
        self._ttl: int = int(os.getenv("CACHE_TTL", "3600"))

    # ------------------------------------------------------------------
    # Key helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _make_key(analysis_type: str, language: str, code: str) -> str:
        """Return a SHA-256 hex digest key for the given inputs."""
        raw = f"{analysis_type}:{language}:{code}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def _get(self, key: str) -> dict | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        if time.monotonic() > entry["expires_at"]:
            return None
        return entry["result"]

    def _set(self, key: str, result: dict) -> None:
        self._store[key] = {
            "result": result,
            "expires_at": time.monotonic() + self._ttl,
        }

    def get(self, analysis_type: str, language: str, code: str) -> dict | None:
        """Return the cached result if it exists and has not expired, else None."""
        return self._get(self._make_key(analysis_type, language, code))

    def set(self, analysis_type: str, language: str, code: str, result: dict) -> None:
        """Store a result under the derived key with a fresh TTL."""
        self._set(self._make_key(analysis_type, language, code), result)

    def get_multi(self, files_payload: str) -> dict | None:
        """Return cached multi-file result keyed by a JSON payload string."""
        key = hashlib.sha256(f"multi:{files_payload}".encode("utf-8")).hexdigest()
        return self._get(key)

    def set_multi(self, files_payload: str, result: dict) -> None:
        """Store a multi-file result keyed by a JSON payload string."""
        key = hashlib.sha256(f"multi:{files_payload}".encode("utf-8")).hexdigest()
        self._set(key, result)

    def clear(self) -> int:
        """Remove all entries and return how many were removed."""
        count = len(self._store)
        self._store.clear()
        return count

    def stats(self) -> dict[str, int]:
        """Return total, alive, and expired entry counts."""
        now = time.monotonic()
        total = len(self._store)
        expired = sum(1 for e in self._store.values() if now > e["expires_at"])
        return {
            "total_entries": total,
            "alive": total - expired,
            "expired": expired,
        }
