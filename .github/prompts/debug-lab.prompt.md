---
description: Debug a failing lab. Provides systematic diagnosis steps for the most common failure modes across all 4 labs.
---

I have an issue with one of the labs. Help me debug it systematically.

## Tell me about the problem

- **Lab**: (01 / 02 / 03 / 04)
- **Component**: backend / frontend / Docker Compose / Fly.io deployment
- **Symptom**: (what you see — error message, wrong output, crash, etc.)
- **What you expected**: (what should have happened)

---

## Diagnostic Decision Tree

### 1. Is the backend reachable?

```bash
curl http://localhost:8000/health
```

Expected: `{"status": "ok"}` with HTTP 200.

**If it returns 404 or connection refused:**
- Check if container is running: `docker compose ps`
- Check logs: `docker compose logs backend`
- Verify `GET /health` endpoint exists in `main.py`

**If it hangs:**
- Check if the port is bound: `netstat -an | grep 8000`
- Restart: `docker compose restart backend`

---

### 2. LLM / JSON parsing errors (Labs 02, 03, 04)

**Symptom**: `json.JSONDecodeError`, `ValidationError`, or `500` from `/analyze` / `/migrate` / `/query`

Checklist:
- [ ] `_parse_json` strips markdown code fences before `json.loads`
- [ ] The prompt explicitly says "return ONLY valid JSON — no markdown, no explanation"
- [ ] The JSON schema in the prompt matches the Pydantic model field names exactly
- [ ] Pydantic model is called immediately after `_parse_json`: `MyModel(**data)`

Test by printing the raw LLM response:
```python
raw = self.llm.chat(messages)
print("RAW LLM RESPONSE:", repr(raw))   # add this temporarily
data = self._parse_json(raw)
```

---

### 3. Database errors (Labs 01, 03)

**Symptom**: `sqlite3.OperationalError: no such table`

- Verify `init_db()` is called at startup (`@app.on_event("startup")` or in `lifespan`)
- Check `DATABASE_PATH` / `DB_PATH` env var points to a writable directory
- In Docker: confirm the volume is mounted at the expected path

**Symptom**: `sqlite3.IntegrityError: UNIQUE constraint failed`

- For short codes: `code_exists()` should be checked before insert
- For custom codes: return `HTTP 409` with a descriptive message, not a 500

---

### 4. Frontend not calling the correct backend (all labs)

**Symptom**: Network errors in browser, requests going to wrong URL

- Check `NEXT_PUBLIC_API_URL` in the browser console: `window.next?.version` or the network tab
- For Docker Compose: must be `http://localhost:8000` (not `http://backend:8000`)
- For Fly.io: must be in **both** `[build.args]` and `[env]` in `frontend/fly.toml`
- After changing the env var on Fly.io, redeploy the frontend (it's baked at build time)

---

### 5. Hot-reload not working in Docker (all labs)

**Symptom**: Code changes don't reflect without manual restart

Backend:
- Confirm `command: uvicorn main:app --reload --reload-dir /app`
- Confirm the source directory is bind-mounted: `- ./python:/app`

Frontend:
- Confirm `WATCHPACK_POLLING: "true"` and `CHOKIDAR_USEPOLLING: "true"` are set
- Confirm the named `node_modules` volume exists (`frontend_node_modules:/app/node_modules`)

---

### 6. ChromaDB errors (Lab 04)

**Symptom**: `chromadb.errors.NotEnoughElementsException` or empty results

- Verify data was indexed first: `GET /stats` should show `count > 0`
- Check `CHROMA_DB_PATH` points to a persisted volume in production
- Confirm the `where` filter is `None` (not `{}`) when no filter is applied — ChromaDB rejects empty `where` dicts

**Symptom**: OOM crash in production

- Set `memory_mb = 512` in `fly.toml` — the default 256 MB is not enough for ChromaDB's HNSW index

---

### 7. Human approval timeout (Lab 03)

**Symptom**: Job auto-rejects before you can approve

- Check `APPROVAL_TIMEOUT_SECONDS` — default is `3600` (1 hour)
- In tests, set it to a large value so the job doesn't time out mid-test
- Verify the `asyncio.Task` for the timeout is being cancelled on `POST /approve` or `POST /reject`

---

### 8. Rate limit false positives (Lab 01)

**Symptom**: Legitimate requests getting `429 Too Many Requests`

- Check `RATE_LIMIT_REQUESTS` and `RATE_LIMIT_WINDOW` env vars
- The rate limiter uses client IP — if running behind a proxy, ensure `request.client.host` returns the real IP
- In tests, use different IP addresses per test or reset the `_ip_requests` dict between tests

---

## Collecting Diagnostic Info

```bash
# Backend logs
docker compose logs --tail=50 backend

# Frontend logs
docker compose logs --tail=50 frontend

# Running containers
docker compose ps

# Fly.io logs
fly logs --app {app-name}

# Run backend tests
cd labs/{lab-dir}/python && pytest -v

# Manual API test
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"code": "def hello(): pass", "language": "python"}'
```
