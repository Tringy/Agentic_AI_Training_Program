---
name: implement-lab
description: 'Implement a lab from scratch or resume an incomplete lab — backend, frontend, and tests. Use when: starting a new lab, filling in TODO stubs, implementing the core required features (not extensions). Covers FastAPI backend, LLMClient wiring, Docker Compose, and Next.js frontend.'
argument-hint: 'Which lab to implement (e.g. "lab02 code analyzer" or "lab04 RAG system")'
---

# Implement a Lab

## When to Use

- Starting a new lab from the provided README or skeleton
- Filling in TODO/placeholder stubs in an existing lab
- Implementing the **core required features only** — not extension challenges (use `/implement-spec` for those)

## Procedure

1. **Read the lab README** — understand the required deliverables and any skeleton code provided

2. **Read existing code** — check `main.py`, `llm_client.py`, `prompts.py`/`agent.py`, `docker-compose.yml`, and any starter files before writing anything

3. **Implement backend** in this order:
   - Pydantic request/response models
   - `init_db()` or storage setup called at FastAPI startup
   - `GET /health → {"status": "ok"}` endpoint (must always be present)
   - Core endpoints with correct HTTP status codes
   - LLM prompt in `prompts.py` if the lab calls an LLM — always request JSON-only output
   - Caching if the lab spec calls for it (SHA-256 + TTL for LLM results; LRU for key lookups)
   - Rate limiting on public-facing write endpoints

4. **Implement frontend** — components in `components/`, types in `types.ts`, always use `process.env.NEXT_PUBLIC_API_URL` as base URL

5. **Write tests** — `test_api.py` using `pytest` + `httpx.AsyncClient`; cover happy path and at least one error case per endpoint

6. **Verify** — `cd python && pytest -v`, then `docker compose up` and smoke-test manually

## Rules

- Never implement extension challenges here — stop at the core lab requirements
- JSON schema in prompts must exactly match Pydantic response model field names
- Never use `shell=True` in subprocess calls
- `GET /health` must return `{"status": "ok"}` with HTTP 200 at all times
