# Agentic AI Training Program

Five-lab, five-day program for building and deploying LLM agents. All projects share a Python/FastAPI backend, Next.js frontend, `LLMClient` abstraction, Docker Compose dev environment, and Fly.io production deployment.

## Project Map

```
labs/
  lab01-vibe-coding-intro/    # URL shortener — FastAPI + SQLite, no LLM
  lab02-code-analyzer-agent/  # Single-call LLM agent, structured JSON output
  lab03-migration-workflow/   # Stateful multi-step agent, human approval
  lab04-rag-system/           # RAG — ChromaDB + BM25 hybrid search
  lab05-multi-agent/          # Supervisor/worker multi-agent orchestration
  capstone-options/           # code-review, documenter, tech-debt, research-assistant
curriculum/                   # Day-by-day lesson plans
templates/                    # Reusable starters (python-agent, rag-starter, typescript-agent)
```

## Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11, FastAPI, Pydantic v2, `python-dotenv` |
| Frontend | Next.js 14+ (App Router), TypeScript, Tailwind CSS |
| LLM | `LLMClient` ABC — Anthropic / OpenAI / Google, via `LLM_PROVIDER` env var |
| Dev | Docker Compose, bind-mount hot-reload |
| Production | Fly.io (`fly.toml` per service) |

## Non-Negotiable Rules

- Every backend: `GET /health → {"status": "ok"}`
- LLM output: always request JSON-only; strip markdown fences; validate with Pydantic immediately
- No `shell=True` in subprocess; never log or commit API keys
- Secrets via `fly secrets set` — never in `fly.toml`
- `NEXT_PUBLIC_API_URL` in both `[build.args]` and `[env]` in frontend `fly.toml`
- ChromaDB backends need 512 MB RAM; all others 256 MB
- Rate-limit all public-facing write endpoints; validate all external input with Pydantic

## Common Env Vars

```
LLM_PROVIDER=google          # anthropic | openai | google
DATABASE_PATH=/data
CACHE_TTL=3600
RATE_LIMIT_REQUESTS=60
RATE_LIMIT_WINDOW=60
CHROMA_DB_PATH=./chroma_db
DB_PATH=/data/jobs.db
APPROVAL_TIMEOUT_SECONDS=3600
```

## Detailed Patterns

Specific code patterns auto-activate via `.github/instructions/` by file type:

- **`python-fastapi-backend`** — FastAPI, Pydantic, caching, rate limiting, SQLite
- **`nextjs-frontend`** — App Router components, API wiring, env vars
- **`docker-compose-dev`** — bind mounts, named volumes, hot-reload, health checks
- **`flyio-deployment`** — `fly.toml` config, Dockerfiles, GitHub Actions workflow pattern
- **`llm-agent-patterns`** — LLMClient, prompts, state machines, supervisor/worker
- **`rag-system`** — ChromaDB, BM25, hybrid retrieval, evaluation

## Skills (on-demand slash commands)

Type `/` in chat to invoke:
- **`/implement-lab`** — implement a lab's core required features end-to-end (backend → frontend → tests)
- **`/implement-spec`** — implement a feature from an existing `specs/{feature}.md`, respecting spec dependencies
- **`/write-spec`** — generate a `specs/{feature}.md` before implementing extension challenges or capstone features
