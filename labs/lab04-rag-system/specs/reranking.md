# Feature: Reranking

## Overview
Initial retrieval (vector search or hybrid) optimizes for recall: it returns the top-N
chunks that are *roughly* relevant. A **reranker** applies a more expensive, precise
scoring model to that small candidate set to re-order it by true relevance before the
answer is generated. This feature adds an optional reranking step to the query pipeline
using the **existing LLM client** (Anthropic or OpenAI, whichever is already configured)
as an LLM-as-reranker: a single prompt scores all candidates in one call. No new
dependencies, no model weights, and no extra API keys are required, keeping the Docker
image and infrastructure footprint unchanged for Fly.io deployment.

> **Relationship to other specs**
> - **Hybrid Search** (`hybrid-search.md`): reranking works on whatever set of candidates
>   retrieval produces. When hybrid search is enabled, the RRF-merged list is the input to
>   the reranker. This ordering — retrieve widely, then rerank precisely — is the
>   recommended production pattern.
> - **Caching** (`caching.md`): the cache is checked **before** the over-fetch and
>   reranking call, so a cache hit avoids both the extra retrieval and the LLM scoring
>   call entirely. The `enable_reranking` flag and `search_mode` are both encoded in the
>   cache key, so reranked and non-reranked results for the same question are stored and
>   served independently.

---

## Functional Requirements

1. Add a `Reranker` class in `rag/reranker.py` that:
   - Accepts the existing `llm_client` instance; no new API keys or packages needed.
   - Exposes `rerank(query: str, candidates: List[Dict], top_n: int) -> List[Dict]`
     which sends a single LLM prompt listing all candidates, parses the returned JSON
     score array, attaches a `rerank_score: float` field, and returns the list sorted
     descending by score (truncated to `top_n`).
   - Truncates each candidate's `content` to 400 characters in the prompt to stay within
     reasonable token budgets.
2. `CodebaseRAG.query()` accepts `enable_reranking: bool = False`. When `True`:
   - Retrieve `n_results * 2` candidates from the underlying store (over-fetch to give
     the reranker sufficient candidates).
   - Pass candidates to `Reranker.rerank(query, candidates, top_n=n_results)`.
   - Return the reranked list (length = `n_results`).
3. `POST /query` must accept and pass through `enable_reranking` from `QueryRequest`.
4. Each source in the response must include `rerank_score: float | null` — present and
   non-null when reranking was applied, `null` otherwise.
5. `GET /stats` response must include `reranker_enabled: bool` — `true` once at
   least one reranking call has been made during the current process lifetime.
6. No model weights are downloaded; scoring is done via the already-configured LLM API.

---

## Acceptance Criteria

```
GIVEN POST /query with enable_reranking false (or omitted)
THEN Reranker.rerank() is never called
AND no extra LLM call is made beyond normal answer generation
AND response sources have rerank_score: null
AND retrieval fetches exactly n_results candidates

GIVEN POST /query with enable_reranking true and search_mode "vector"
THEN retrieval fetches n_results * 2 candidates from ChromaDB
AND Reranker.rerank() is called once with those candidates
AND the response contains exactly n_results sources
AND each source has rerank_score as a non-null float
AND sources are sorted descending by rerank_score

GIVEN POST /query with enable_reranking true and search_mode "hybrid"
THEN retrieval fetches n_results * 2 candidates via RRF-merged hybrid results
AND Reranker.rerank() is called on the merged list
AND the final response is sorted by rerank_score (overrides RRF order)

GIVEN the same request is made twice with enable_reranking true
WHEN caching is enabled (CACHE_ENABLED=true)
THEN the second response is returned from cache (cache_hit: true)
AND no LLM reranking call is made on the second request

GIVEN POST /query with enable_reranking true
AND POST /query with same question but enable_reranking false
THEN both are cache misses on their respective first calls
AND the cached reranked result is NOT returned for the non-reranking request

GIVEN a query where the top vector result is irrelevant and a
highly relevant result sits at position 4 in the retrieval list
WHEN enable_reranking true and search_mode "hybrid"
THEN the reranked response places the highly relevant result in position 1 or 2
```

---

## Implementation Notes

### New file: `rag/reranker.py`

```python
import json
import re
from typing import Dict, List, Optional


class Reranker:
    """LLM-as-reranker — no new dependencies, no model weights, no extra API keys.

    Uses the same llm_client already wired into CodebaseRAG to score
    all candidates in a single prompt call.
    """

    def __init__(self, llm_client):
        self._llm = llm_client
        self._call_count: int = 0

    def rerank(self, query: str, candidates: List[Dict], top_n: int) -> List[Dict]:
        if not candidates:
            return candidates

        numbered = "\n\n".join(
            f"[{i}] {c['content'][:400]}" for i, c in enumerate(candidates)
        )
        prompt = (
            f"Rate each code snippet's relevance to the following query on a scale "
            f"of 0.0 to 1.0.\n"
            f"Query: {query}\n\n"
            f"{numbered}\n\n"
            f"Reply with a JSON array of {len(candidates)} numbers only, "
            f"e.g. [0.9, 0.3, 0.7, ...]. No explanation."
        )
        raw = self._llm.chat([
            {
                "role": "system",
                "content": "You are a relevance scoring assistant. Reply with a JSON array of numbers only.",
            },
            {"role": "user", "content": prompt},
        ])

        match = re.search(r"\[.*?\]", raw, re.DOTALL)
        if not match:
            # Parsing failed — return candidates unchanged with null scores
            return [{**c, "rerank_score": None} for c in candidates[:top_n]]

        scores = [float(s) for s in json.loads(match.group())]
        # Guard against mismatched array length
        scores = (scores + [0.0] * len(candidates))[: len(candidates)]

        ranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)[:top_n]
        self._call_count += 1
        return [{**doc, "rerank_score": float(score)} for doc, score in ranked]

    @property
    def enabled(self) -> bool:
        return self._call_count > 0
```

### Changes to `rag/pipeline.py`

- Import `Reranker` from `.reranker`.
- Add `self.reranker = Reranker(llm_client=self.llm)` in `__init__`.
- Update `query()` to accept `search_mode` (from hybrid-search spec) and
  `enable_reranking`; check the cache **first** (before over-fetching), then:
  ```python
  fetch_n = n_results * 2 if enable_reranking else n_results  # 2× keeps cost low
  # _retrieve dispatches to vector / keyword / hybrid based on search_mode
  results = self._retrieve(question, fetch_n, filter_language, filter_repository, search_mode)
  if enable_reranking:
      results = self.reranker.rerank(question, results, top_n=n_results)
  else:
      for r in results:
          r["rerank_score"] = None
  ```

### Changes to `main.py`

```python
class QueryRequest(BaseModel):
    question: str
    n_results: int = 5
    filter_language: Optional[str] = None
    filter_repository: Optional[str] = None
    search_mode: str = "hybrid"
    enable_reranking: bool = False       # NEW
```

Pass `enable_reranking` to `rag.query(...)`.

In `GET /stats`, include:
```python
"reranker_enabled": rag.reranker.enabled,   # True once any reranking call has run
```

### Required package

None. `Reranker` uses only the `llm_client` already present in `CodebaseRAG`.

---

## Frontend Changes

### `components/QueryPanel.tsx`

1. Add an `enableReranking` boolean state (default `false`).
2. Render a labelled toggle switch — **Rerank results** — in the query options row,
   beside the search mode selector.
3. Include `enable_reranking: enableReranking` in the POST body alongside `search_mode`
   (added by the hybrid-search spec).
4. When a source has a non-null `rerank_score`, display it as a secondary amber badge
   (e.g. `↑ 0.94`) next to the existing vector distance badge.
5. When reranking is enabled and the response returns, show a small note beneath the
   sources heading:
   - `cache_hit: false` → *"Results reranked by LLM"*
   - `cache_hit: true`  → *"Results reranked by LLM (cached)"*

### UI copy

| State | Label |
|-------|-------|
| Toggle off | Rerank results |
| Toggle on  | Reranking ON |
| Score badge | ↑ {score.toFixed(2)} |
| Note (live) | Results reranked by LLM |
| Note (cached) | Results reranked by LLM (cached) |
