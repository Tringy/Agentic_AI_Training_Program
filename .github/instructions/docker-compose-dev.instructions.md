---
applyTo: "**/docker-compose.yml"
---

# Docker Compose Dev Conventions

Docker Compose is used for local development only. Production runs on Fly.io. Every service follows the same structural patterns regardless of which lab or capstone project you are working on.

---

## Core Principles

1. **Bind-mount source code** into the container so file edits reflect immediately without rebuilding
2. **Use named volumes for dependencies** (`node_modules`) to prevent the host directory from shadowing the container-installed packages
3. **Use named volumes for persistent data** (SQLite files, ChromaDB) so the data survives container restarts
4. **Always define a health check** on the backend so frontend `depends_on` can gate correctly
5. **All environment values are strings** — quote numbers: `"1000"`, `"true"`, `"3600"`

---

## Backend Service Template

```yaml
services:
  backend:
    build: ./python            # adjust path if source is elsewhere (e.g. ./backend, ./typescript)
    ports:
      - "8000:8000"
    environment:
      LLM_PROVIDER: google     # anthropic | openai | google
      # Add all non-secret config here as key: value
    env_file:
      - ./python/.env          # holds API keys (ANTHROPIC_API_KEY, OPENAI_API_KEY, GOOGLE_API_KEY)
    volumes:
      - ./python:/app          # bind-mount for hot-reload
    command: uvicorn main:app --reload --reload-dir /app
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 10s
```

**`--reload-dir /app`** is required — using bare `--reload` watches the entire filesystem and causes spurious reloads inside Docker.

---

## Frontend Service Template (Next.js)

```yaml
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000   # always localhost — browser can't resolve container names
      WATCHPACK_POLLING: "true"                    # required on Windows/WSL for hot-reload
      CHOKIDAR_USEPOLLING: "true"                  # required on Windows/WSL for hot-reload
    volumes:
      - ./frontend:/app
      - frontend_node_modules:/app/node_modules   # named volume prevents host override
    depends_on:
      backend:
        condition: service_healthy
```

`NEXT_PUBLIC_API_URL` **must be `http://localhost:8000`**, not `http://backend:8000`. The browser fetches from the host machine, not from inside the Docker network.

---

## Volumes

### Named volumes for persistent data

Use named volumes whenever a service writes data that must survive container restarts or rebuilds. Declare them in the top-level `volumes:` section so Docker manages their lifecycle.

```yaml
volumes:
  frontend_node_modules:   # isolates container node_modules from host directory
  db_data:                 # for SQLite — mount at /data in the backend
  chroma_data:             # for ChromaDB — mount at /app/chroma_db or /data
  redis_data:              # for Redis — mount at /data
```

Mount a named volume inside a service:

```yaml
    volumes:
      - ./python:/app          # bind-mount (source code, hot-reload)
      - db_data:/data          # named volume (persistent data)
```

### When to use bind-mounts vs named volumes

| Use case | Type | Example |
|----------|------|---------|
| Source code (need live edits) | Bind-mount | `./python:/app` |
| Database / vector store files | Named volume | `db_data:/data` |
| `node_modules` | Named volume | `frontend_node_modules:/app/node_modules` |
| Config files (read-only) | Bind-mount with `:ro` | `./config.yaml:/app/config.yaml:ro` |

### Services without persistent storage

If a service uses only in-memory caching (no files to persist), omit the data volume entirely — just bind-mount the source:

```yaml
    volumes:
      - ./python:/app    # source code only, no data volume needed
```

---

## Environment Variable Conventions

**12-factor rule**: all configuration comes from environment variables, never hardcoded in source.

```yaml
environment:
  # Non-secret config — safe to commit in docker-compose.yml
  LLM_PROVIDER: google
  CACHE_TTL: "3600"
  DATABASE_PATH: /data

env_file:
  - ./python/.env        # secrets — git-ignored, never committed
```

The `.env` file holds only secrets:

```dotenv
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AIza...
```

**Naming convention for env vars**:
- All caps, underscore-separated: `DATABASE_PATH`, `CACHE_TTL`, `LLM_PROVIDER`
- Booleans as strings: `"true"` / `"false"`
- Integers as strings: `"1000"`, `"3600"`
- Paths always absolute inside the container: `/data`, `/app/chroma_db`

---

## Networks

Add a named network when services need to call each other by hostname (e.g. a background worker calling the API):

```yaml
networks:
  app-network:
    driver: bridge

services:
  backend:
    networks:
      - app-network
  worker:
    networks:
      - app-network
```

For simple two-service stacks (backend + frontend) Compose's default network is sufficient and the explicit declaration can be omitted.

---

## Health Checks

Every backend service must define a health check. This enables `depends_on: condition: service_healthy` on the frontend and gives Docker Compose visibility into readiness.

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 10s
  timeout: 5s
  retries: 3
  start_period: 10s   # grace period while the process initialises
```

The backend **must** expose `GET /health → {"status": "ok"}` with HTTP 200.

---

## Frontend `Dockerfile.dev`

The dev Dockerfile skips the multi-stage production build — it just installs and runs `npm run dev`:

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["npm", "run", "dev"]
```

---

## Patterns by Storage Type

### No persistent storage (in-memory only)
```yaml
services:
  backend:
    volumes:
      - ./python:/app
    # No data volume needed
volumes: {}
```

### SQLite
```yaml
services:
  backend:
    environment:
      DATABASE_PATH: /data
    volumes:
      - ./python:/app
      - db_data:/data
volumes:
  db_data:
```

### ChromaDB (vector store)
```yaml
services:
  backend:
    environment:
      CHROMA_DB_PATH: /data/chroma_db
    volumes:
      - ./python:/app
      - chroma_data:/data
volumes:
  chroma_data:
```

### Multiple services (e.g. multi-agent with worker)
```yaml
services:
  api:
    build: ./python
    ports: ["8000:8000"]
    volumes:
      - ./python:/app
      - shared_data:/data
    healthcheck: ...

  worker:
    build: ./python
    command: python worker.py
    volumes:
      - ./python:/app
      - shared_data:/data
    depends_on:
      api:
        condition: service_healthy

volumes:
  shared_data:
```

---

## Verification Commands

```bash
# Start full stack (rebuilds images)
docker compose up --build

# Start in background
docker compose up -d --build

# Check service health
curl http://localhost:8000/health

# Stream logs for one service
docker compose logs -f backend

# Restart a single service without rebuilding
docker compose restart backend

# Tear down (keeps named volumes)
docker compose down

# Tear down and delete all volumes (destructive — deletes DB data)
docker compose down -v
```
