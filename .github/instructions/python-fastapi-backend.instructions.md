---
applyTo: "**/python/**,**/backend/**"
---

# Python FastAPI Backend Conventions

All backend services in this program (labs and capstone projects) are FastAPI applications running Python 3.11. Follow these patterns consistently across every project you work on.

## FastAPI Application Structure

Every `main.py` follows this standard structure:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Your Project Name")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok"}
```

Always include CORS middleware with `allow_origins=["*"]` for dev compatibility. Always include `GET /health` returning `{"status": "ok"}`.

## Pydantic v2 Models

Use Pydantic v2 syntax throughout:

```python
from pydantic import BaseModel, field_validator, HttpUrl
from typing import Optional, List

class URLRequest(BaseModel):
    url: HttpUrl
    custom_code: Optional[str] = None

    @field_validator("custom_code")
    @classmethod
    def validate_custom_code(cls, v):
        if v is not None:
            if not v.isalnum():
                raise ValueError("Only alphanumeric characters allowed")
            if v.lower() in {"api", "health", "shorten", "analytics"}:
                raise ValueError("Reserved word")
        return v
```

- Use `@field_validator` (not `@validator`) for Pydantic v2
- Decorate validators with `@classmethod`
- `HttpUrl` for URL validation; call `str(url)` when storing to DB

## Environment Variable Convention

All configuration comes from environment variables (12-factor). Read at module level with sensible defaults:

```python
# Common across all backend services
LLM_PROVIDER  = os.getenv("LLM_PROVIDER", "google")

# For services with SQLite storage
DATABASE_PATH = os.getenv("DATABASE_PATH", "/data")

# For services with rate limiting
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "60"))
RATE_LIMIT_WINDOW   = int(os.getenv("RATE_LIMIT_WINDOW", "60"))

# For services with LRU caching
CACHE_SIZE = int(os.getenv("CACHE_SIZE", "1000"))
CACHE_TTL  = int(os.getenv("CACHE_TTL", "3600"))
```

Never hardcode configuration values. If a value is non-sensitive (paths, provider names, feature flags), add it to `fly.toml [env]`. If it is a secret (API key, token), it goes in `fly secrets set` and the local `.env` file only.

## SQLite Database Pattern

```python
import sqlite3
import os

DB_PATH = os.path.join(os.getenv("DATABASE_PATH", "/data"), "urls.db")

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS my_table (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        )""")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_my_table_key ON my_table(key)")
        conn.commit()
```

- Always create the directory before connecting (`os.makedirs(..., exist_ok=True)`)
- Call `init_db()` in a FastAPI `lifespan` or `@app.on_event("startup")` handler
- Use `CREATE TABLE IF NOT EXISTS` and `CREATE INDEX IF NOT EXISTS` — safe to run on every startup
- Use parameterized queries exclusively — never format SQL strings with user data

## LRU Caching — Size-Bounded (cachetools)

```python
from cachetools import LRUCache

_cache = LRUCache(maxsize=CACHE_SIZE)
NOT_FOUND_SENTINEL = "__NOT_FOUND__"

def get_from_cache(key: str):
    return _cache.get(key)  # returns None on miss

def set_in_cache(key: str, value: str):
    _cache[key] = value
```

Cache negative results too using `NOT_FOUND_SENTINEL` to avoid repeated DB lookups on keys that don't exist.

Use this pattern when cache keys are short identifiers (slugs, IDs) and the cache should never grow past a fixed size.

## SHA-256 Cache with TTL — Deterministic Results

```python
import hashlib, json, time

class AnalysisCache:
    def __init__(self, ttl: int = 3600):
        self._store: dict = {}
        self.ttl = ttl

    def _make_key(self, analysis_type: str, language: str, code: str) -> str:
        raw = f"{analysis_type}:{language}:{code}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def get(self, analysis_type, language, code):
        key = self._make_key(analysis_type, language, code)
        entry = self._store.get(key)
        if entry and time.time() < entry["expires_at"]:
            return entry["result"]
        return None

    def set(self, analysis_type, language, code, result):
        key = self._make_key(analysis_type, language, code)
        self._store[key] = {"result": result, "expires_at": time.time() + self.ttl}
```

Use this pattern when the cache key encodes multiple inputs (e.g. request type + language + code content). The SHA-256 hash keeps keys short and collision-resistant.

## Sliding-Window Rate Limiting

Use for any public-facing endpoint that could be abused:

```python
from collections import defaultdict
import time

_ip_requests: dict = defaultdict(list)

def check_rate_limit(ip: str) -> bool:
    """Returns True if the request is allowed, False if the limit is exceeded."""
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW
    # Prune timestamps outside the window
    _ip_requests[ip] = [t for t in _ip_requests[ip] if t > window_start]
    if len(_ip_requests[ip]) >= RATE_LIMIT_REQUESTS:
        return False
    _ip_requests[ip].append(now)
    return True
```

In endpoints, raise `HTTPException(status_code=429)` when the limit is exceeded. Expose `RATE_LIMIT_REQUESTS` and `RATE_LIMIT_WINDOW` as env vars so operators can tune without rebuilding.

## HTTP Status Codes

| Scenario                  | Status |
|---------------------------|--------|
| Successful creation       | 201    |
| Accepted (async started)  | 202    |
| Validation failure        | 422    |
| Not found                 | 404    |
| Rate limited              | 429    |
| Duplicate resource        | 409    |
| Redirect                  | 307    |

## Response Headers (caching)

Always add `X-Cache` header to indicate cache hit/miss:

```python
from fastapi import Response

@app.post("/analyze")
async def analyze(request: AnalyzeRequest, response: Response):
    cached = cache.get(...)
    if cached:
        response.headers["X-Cache"] = "HIT"
        return cached
    result = analyzer.analyze(...)
    cache.set(...)
    response.headers["X-Cache"] = "MISS"
    return result
```

## Security Checklist

- Never use `shell=True` in `subprocess` calls
- Validate URLs against an allowlist before passing to external tools
- Sanitize all user inputs via Pydantic validators
- Use reserved-word blocklists for user-supplied ID fields
- Never log API keys or secrets
- Use parameterized SQLite queries
