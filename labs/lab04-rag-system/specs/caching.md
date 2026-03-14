# Feature: Caching

## Overview
Every `/query` call currently embeds the query string via OpenAI and searches ChromaDB,
even when the same question has been asked moments before. This feature adds a
**two-level cache**: a fast in-memory LRU cache for query results, and an optional
embedding cache that avoids redundant OpenAI API calls for repeated query strings. Both
caches are keyed on a normalized (lowercased, whitespace-collapsed) version of the
query plus all request parameters that affect the result.

> **Relationship to other specs**
> - **Hybrid Search** (`hybrid-search.md`): the `search_mode` parameter must be part of
>   the cache key so that `"vector"` and `"hybrid"` queries for the same question are
>   cached independently.
> - **Reranking** (`reranking.md`): the `enable_reranking` flag must be part of the
>   cache key. A cached reranked result must not be returned for a non-reranking request
>   (the ordering differs). When caching is enabled, reranked results should be cached
>   after the reranker has already run so that the cached entry reflects the final order.

---

## Functional Requirements

1. Add a `QueryCache` class in `rag/cache.py` that:
   - Implements an in-memory LRU cache with a configurable maximum size
     (`CACHE_MAX_SIZE`, default `200` entries).
   - Implements a configurable TTL (`CACHE_TTL_SECONDS`, default `300` — 5 minutes)
     per entry; stale entries are evicted on read (lazy expiry).
   - Exposes `get(key: str) -> Dict | None`, `set(key: str, value: Dict) -> None`,
     and `clear() -> None`.
   - Tracks hit/miss counters (`hits`, `misses`) for the lifetime of the process.
   - Is **not** persisted to disk; the cache is lost on restart by design.
2. Add an `EmbeddingCache` class in `rag/cache.py` that:
   - Caches `(model_name, text) → List[float]` embeddings in memory.
   - Has the same `CACHE_MAX_SIZE` limit (shared with `QueryCache` by default is fine;
     separate size config is preferred).
   - Is consulted by `OpenAIEmbeddingFunction.__call__` before calling the OpenAI API;
     only uncached texts are sent in the batch request.
3. `CodebaseRAG.query()` checks the `QueryCache` before running retrieval or generation:
   - Cache hit → return cached result immediately (add `"cache_hit": true` to response).
   - Cache miss → run the full pipeline, store result, return with `"cache_hit": false`.
4. Cache key derivation:
   ```
   key = sha256(json.dumps({
       "q": question.lower().split(),   # normalized tokens
       "n": n_results,
       "lang": filter_language,
       "repo": filter_repository,
       "mode": search_mode,
       "rerank": enable_reranking,
   }, sort_keys=True))
   ```
5. Expose `GET /cache/stats` returning `{hits, misses, size, max_size, ttl_seconds}`.
6. Expose `DELETE /cache` to clear the query cache (does not affect the vector index
   or BM25 index). Returns `{cleared: true, previous_size: N}`.
7. Clearing the vector index via `DELETE /index` must also clear the query cache and
   embedding cache (stale results are invalid after re-indexing).
8. Environment variables that control cache behaviour:

   | Variable | Default | Description |
   |----------|---------|-------------|
   | `CACHE_ENABLED` | `"true"` | Set to `"false"` to disable query caching entirely |
   | `CACHE_MAX_SIZE` | `200` | Max LRU entries in the query cache |
   | `CACHE_TTL_SECONDS` | `300` | Seconds before an entry is considered stale |
   | `EMBEDDING_CACHE_ENABLED` | `"true"` | Set to `"false"` to disable embedding caching |

---

## Acceptance Criteria

```
GIVEN POST /query is called twice with identical parameters
WHEN CACHE_ENABLED is "true"
THEN the second response must return in < 50 ms (no embedding or LLM call)
AND the second response must include "cache_hit": true
AND GET /cache/stats must show hits: 1, misses: 1

GIVEN POST /query with search_mode "hybrid" is cached
WHEN POST /query with the same question but search_mode "vector" is called
THEN the second call must be a cache miss (different key)
AND the second call must return results from the vector-only path

GIVEN POST /query with enable_reranking true is cached
WHEN POST /query with enable_reranking false (same question) is called
THEN the second call must be a cache miss
AND sources must be in vector-distance order (no rerank_score present)

GIVEN DELETE /index is called
THEN the query cache is cleared
AND GET /cache/stats shows size: 0
AND the next POST /query for a previously cached question is a cache miss

GIVEN DELETE /cache is called
THEN the response includes previous_size equal to the count before clearing
AND GET /cache/stats shows size: 0, hits and misses are reset to 0

GIVEN CACHE_ENABLED is "false"
THEN POST /query never reads or writes the cache
AND every response includes "cache_hit": false

GIVEN the embedding cache is enabled and the same query text is used twice
THEN the OpenAI embeddings API is called only once across both queries
(second call served entirely from the embedding cache)
```

---

## Implementation Notes

### New file: `rag/cache.py`

```python
import hashlib
import json
import os
import time
from collections import OrderedDict
from typing import Any, Dict, List, Optional, Tuple


class _LRUCache:
    """Generic LRU cache with TTL eviction."""

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
    payload = {
        "q": question.lower().split(),
        "n": n_results,
        "lang": filter_language,
        "repo": filter_repository,
        "mode": search_mode,
        "rerank": enable_reranking,
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
```

### Changes to `rag/vector_store.py` — `OpenAIEmbeddingFunction`

```python
def __call__(self, input: Documents) -> Embeddings:
    from rag.cache import embedding_cache, EMBEDDING_CACHE_ENABLED
    safe = [doc if doc and doc.strip() else " " for doc in input]
    if not EMBEDDING_CACHE_ENABLED:
        # original path
        response = self._client.embeddings.create(model=self._model, input=safe)
        return [item.embedding for item in response.data]

    result: List[Optional[List[float]]] = [None] * len(safe)
    uncached_indices, uncached_texts = [], []
    for i, text in enumerate(safe):
        cached = embedding_cache.get(f"{self._model}:{text}")
        if cached is not None:
            result[i] = cached
        else:
            uncached_indices.append(i)
            uncached_texts.append(text)

    if uncached_texts:
        response = self._client.embeddings.create(model=self._model, input=uncached_texts)
        for idx, item in zip(uncached_indices, response.data):
            embedding_cache.set(f"{self._model}:{safe[idx]}", item.embedding)
            result[idx] = item.embedding

    return result   # type: ignore[return-value]
```

### Changes to `rag/pipeline.py`

```python
from .cache import query_cache, make_query_key, CACHE_ENABLED

def query(self, question, n_results=5, filter_language=None, filter_repository=None,
          search_mode="hybrid", enable_reranking=False):
    cache_key = make_query_key(question, n_results, filter_language,
                               filter_repository, search_mode, enable_reranking)
    if CACHE_ENABLED:
        cached = query_cache.get(cache_key)
        if cached is not None:
            return {**cached, "cache_hit": True}

    result = self._run_query(...)  # existing logic
    result["cache_hit"] = False

    if CACHE_ENABLED:
        query_cache.set(cache_key, result)
    return result
```

In `clear_index()`:
```python
from .cache import query_cache, embedding_cache
query_cache.clear()
embedding_cache.clear()
```

### Changes to `main.py`

```python
from rag.cache import query_cache, CACHE_ENABLED

@app.get("/cache/stats")
async def cache_stats():
    return {
        "enabled": CACHE_ENABLED,
        "hits": query_cache.hits,
        "misses": query_cache.misses,
        "size": query_cache.size,
        "max_size": query_cache.max_size,
        "ttl_seconds": int(query_cache.ttl),
    }

@app.delete("/cache")
async def clear_cache():
    previous = query_cache.clear()
    return {"cleared": True, "previous_size": previous}
```

Add `"cache_hit": bool` to `QueryResponse`:
```python
class QueryResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    context_used: str
    cache_hit: bool = False              # NEW
```

---

## Frontend Changes

### `components/QueryPanel.tsx`

1. Read `cache_hit` from the query response and display a small pill badge beside the
   response header:
   - Cache hit → green pill **"Cached"** with a lightning bolt icon.
   - Cache miss → no badge (or a subtle grey **"Live"** badge).
2. Add a **Cache** section to the stats bar (or a separate collapsible panel) that:
   - Fetches `GET /cache/stats` on page load and after every query.
   - Displays: *Hits: N  ·  Misses: N  ·  Entries: N / MAX  ·  TTL: Ns*.
3. Add a **Clear Cache** button in the stats bar (alongside the existing **Clear Index**
   button) that calls `DELETE /cache` and refreshes the stats.
4. Do not expose `CACHE_ENABLED` or TTL as user-editable fields in the UI; they are
   server-side configuration.

### UI copy

| Element | Text |
|---------|------|
| Cache hit badge | ⚡ Cached |
| Stats row | Cache — Hits: {hits} · Misses: {misses} · {size}/{max_size} entries |
| Clear button | Clear Cache |
| Confirm dialog | Clear the query cache? Indexed documents are not affected. |
