---
description: Add a new feature to an existing lab. Guides through backend model, endpoint, LLM prompt changes, frontend wiring, and tests.
---

I want to add a new feature to one of the labs. Help me implement it end-to-end following the project conventions.

## What I'm adding

- **Lab**: (which lab — 01 / 02 / 03 / 04)
- **Feature description**: (describe the feature)
- **API endpoint(s) needed**: (e.g. `POST /analyze/security`, `GET /stats`)

---

## Implementation Steps

### 1. Backend — Pydantic models

First, define the request and response models in the appropriate file (usually `main.py` or a models module):

```python
class MyRequest(BaseModel):
    field: str
    optional_field: Optional[str] = None

class MyResponse(BaseModel):
    result: str
    score: float
```

Rules:
- Use `Optional[X] = None` for optional fields (Pydantic v2)
- Use `HttpUrl` for URL inputs; call `str(url)` before storing
- Add `@field_validator` with `@classmethod` for custom validation
- Use reserved-word blocklists for any user-supplied slug or code field

### 2. Backend — FastAPI endpoint

Add to `main.py` with the correct HTTP status code:

```python
@app.post("/my-endpoint", status_code=201)
async def my_endpoint(request: MyRequest, response: Response):
    # Check cache first (if applicable)
    cached = cache.get(...)
    if cached:
        response.headers["X-Cache"] = "HIT"
        return cached

    # Core logic
    result = do_work(request)

    # Store in cache (if applicable)
    cache.set(...)
    response.headers["X-Cache"] = "MISS"
    return MyResponse(result=result)
```

HTTP status reference:
- `201` — created
- `202` — accepted (async job started)
- `404` — not found
- `409` — conflict / duplicate
- `422` — validation error (automatic from Pydantic)
- `429` — rate limited

### 3. LLM prompt (if feature involves the LLM)

Add to `prompts.py`. Always instruct the model to return only valid JSON with an explicit schema:

```python
MY_FEATURE_PROMPT = """You are an expert at X. Analyze the provided input and return ONLY valid JSON.

Return this exact schema:
{
  "field_a": "string",
  "field_b": ["array", "of", "strings"],
  "score": 0.0
}"""
```

Then in the business logic, call the LLM and parse defensively:

```python
def my_llm_call(self, input: str) -> MyResponse:
    messages = [
        {"role": "system", "content": MY_FEATURE_PROMPT},
        {"role": "user", "content": f"Input:\n{input}"},
    ]
    raw = self.llm.chat(messages)
    data = self._parse_json(raw)
    return MyResponse(**data)
```

### 4. Caching the LLM result (SHA-256 + TTL pattern)

If the feature is deterministic (same input → same output), add caching:

```python
def my_feature(self, code: str, language: str) -> MyResponse:
    cached = cache.get("my_feature", language, code)
    if cached:
        return cached
    result = self._run_llm(code, language)
    cache.set("my_feature", language, code, result)
    return result
```

### 5. Frontend component

Create `components/MyFeature.tsx`:

```tsx
'use client'
import { useState } from 'react'
import type { MyResponse } from '@/types'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function MyFeature() {
  const [input, setInput] = useState('')
  const [result, setResult] = useState<MyResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit() {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch(`${API_BASE}/my-endpoint`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ field: input }),
      })
      if (!res.ok) throw new Error((await res.json()).detail || 'Request failed')
      setResult(await res.json())
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-8 space-y-4">
      {/* ... */}
    </div>
  )
}
```

Add the new type to `types.ts`.

### 6. Wire into a page

Import and render the component in `app/page.tsx` or a new `app/my-feature/page.tsx`:

```tsx
import MyFeature from '@/components/MyFeature'

export default function MyFeaturePage() {
  return (
    <main className="max-w-4xl mx-auto px-4 py-8">
      <MyFeature />
    </main>
  )
}
```

Add the route to `Navigation.tsx` if it's a top-level page.

### 7. Tests

Add to `test_api.py`:

```python
def test_my_endpoint(client):
    response = client.post("/my-endpoint", json={"field": "test input"})
    assert response.status_code == 201
    data = response.json()
    assert "result" in data
    assert "score" in data

def test_my_endpoint_validation(client):
    response = client.post("/my-endpoint", json={})  # missing required field
    assert response.status_code == 422

def test_my_endpoint_cache(client):
    r1 = client.post("/my-endpoint", json={"field": "test"})
    r2 = client.post("/my-endpoint", json={"field": "test"})
    assert r1.headers.get("X-Cache") == "MISS"
    assert r2.headers.get("X-Cache") == "HIT"
```

### 8. Update fly.toml (if new env vars)

If the feature introduces a new configuration value:

```toml
[env]
  MY_NEW_VAR = "default_value"
```

Secrets (API keys, tokens) go via `fly secrets set`, not in `fly.toml`.

---

## Checklist

- [ ] Request and response Pydantic models defined
- [ ] Endpoint added to `main.py` with correct status code
- [ ] `prompts.py` updated if LLM behaviour changes
- [ ] JSON schema in prompt matches Pydantic response model
- [ ] Cache key includes new feature type if applicable
- [ ] `X-Cache` header set on cached responses
- [ ] Frontend component created with `API_BASE` env var
- [ ] Type added to `types.ts`
- [ ] Navigation updated if new page added
- [ ] Tests added to `test_api.py`
- [ ] `fly.toml` updated if new env vars introduced
- [ ] `pytest -v` passes
