"""In-memory LRU caches for query results and embeddings."""

import hashlib
import json
import os
import time
from collections import OrderedDict
from typing import Any, Dict, List, Optional, Tuple


class _LRUCache:
    """Generic LRU cache with lazy TTL eviction."""

    def __init__(self, max_size: int, ttl: float):
        self.max_size = max_size
        self.ttl = ttl
        self._store: OrderedDict[str, Tuple[Any, float]] = OrderedDict()
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Optional[Any]:
        if key not in self._store:
            self.misses += 1
            return None
        value, ts = self._store[key]
        if time.monotonic() - ts > self.ttl:
            del self._store[key]
            self.misses += 1
            return None
        self._store.move_to_end(key)
        self.hits += 1
        return value

    def set(self, key: str, value: Any) -> None:
        self._store[key] = (value, time.monotonic())
        self._store.move_to_end(key)
        if len(self._store) > self.max_size:
            self._store.popitem(last=False)

    def clear(self) -> int:
        n = len(self._store)
        self._store.clear()
        self.hits = 0
        self.misses = 0
        return n

    @property
    def size(self) -> int:
        return len(self._store)


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


_CACHE_MAX_SIZE = _env_int("CACHE_MAX_SIZE", 200)
_CACHE_TTL = _env_int("CACHE_TTL_SECONDS", 300)

query_cache = _LRUCache(max_size=_CACHE_MAX_SIZE, ttl=float(_CACHE_TTL))
embedding_cache = _LRUCache(max_size=_env_int("EMBEDDING_CACHE_SIZE", 2000), ttl=86400.0)

CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() != "false"
EMBEDDING_CACHE_ENABLED = os.getenv("EMBEDDING_CACHE_ENABLED", "true").lower() != "false"


def make_query_key(
    question: str,
    n_results: int,
    filter_language: Optional[str],
    filter_repository: Optional[str],
    search_mode: str = "hybrid",
    enable_reranking: bool = False,
) -> str:
    """Create a deterministic SHA-256 cache key from all query parameters."""
    payload = {
        "q": question.lower().split(),
        "n": n_results,
        "lang": filter_language,
        "repo": filter_repository,
        "mode": search_mode,
        "rerank": enable_reranking,
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
