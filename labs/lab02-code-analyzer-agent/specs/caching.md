# Feature: Caching

## Functional Requirements
1. Cache LLM analysis results using a deterministic key derived from `(code, language, analysis_type)`
2. Return cached results immediately, bypassing the LLM call entirely
3. Expire cache entries after a configurable TTL (default 3600 seconds)
4. Apply caching to all three analyze endpoints: `/analyze`, `/analyze/security`, `/analyze/performance`
5. Expose a stats endpoint showing total entries, alive entries, and expired entries
6. Expose a clear endpoint for manual cache invalidation
7. Signal cache hits to the frontend via a response header

---

## Acceptance Criteria

```
GIVEN the same code, language, and analysis type are submitted twice
WHEN POST /analyze is called the second time
THEN response must:
  - Return identical JSON to the first response
  - Include header X-Cache: HIT
  - Complete significantly faster than the first (LLM-backed) call

GIVEN a cached entry whose TTL has expired
WHEN POST /analyze is called
THEN the cache must:
  - Treat the entry as a miss
  - Call the LLM and store a fresh result
  - Return header X-Cache: MISS

GIVEN GET /cache/stats is called
THEN response must:
  - Return total_entries, alive, and expired counts
  - Have status code 200

GIVEN DELETE /cache is called
WHEN the cache has N entries
THEN response must:
  - Return { "cleared": N }
  - Leave the cache empty
```

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `CACHE_TTL` | `3600` | Cache entry TTL in seconds |

---

## Files to Add / Update

| File | Change |
|---|---|
| `python/cache.py` | NEW – `AnalysisCache` class with `get`, `set`, `clear`, `stats`; SHA-256 key hashing; TTL expiry |
| `python/main.py` | Instantiate cache at module level; wrap all three analyze endpoints with cache check/store; add `GET /cache/stats` and `DELETE /cache`; set `X-Cache` response header |
| `frontend/components/CacheStatsBar.tsx` | NEW – banner showing alive entry count; fetches `/cache/stats` on mount and after each analysis; "Clear Cache" button calls `DELETE /cache` |
| `frontend/components/CodeAnalyzer.tsx` | Read `X-Cache` response header; show `"Served from cache"` badge when value is `HIT` |
| `frontend/app/page.tsx` | Render `CacheStatsBar` above the analyzer |
| `frontend/types.ts` | Add `CacheStats` interface |

---

## Implementation Notes

- Cache key must be a SHA-256 hash of `"{analysis_type}:{language}:{code}"` to produce a stable, fixed-length key.
- Store entries as `{ result: dict, expires_at: float }` in a plain in-memory dict — no external dependencies required.
- All three analyze endpoints (`general`, `security`, `performance`) must pass the corresponding `analysis_type` string to `cache.get()` and `cache.set()`.
- The `FastAPI` `Response` object must be injected as a parameter in each endpoint to allow setting `response.headers["X-Cache"]`.
- `CacheStatsBar` should re-fetch stats after every successful analysis so the count stays current without a page reload.
