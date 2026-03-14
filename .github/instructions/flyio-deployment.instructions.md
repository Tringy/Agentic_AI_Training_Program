Note: The tool simplified the command to ` cat > "c:\Users\tringo\Desktop\taller_technologies\AI\Agentic_AI_Training_Program\.github\instructions\flyio-deployment.instructions.md" << 'EOF'
---
applyTo: "**/fly.toml,**/Dockerfile,**/.dockerignore,**/.github/workflows/**"
---

# Fly.io — Configuration & GitHub Actions

Deployment is handled by GitHub Actions workflows in `.github/workflows/`. The agent's job is to configure `fly.toml`, Dockerfiles, and workflow YAML correctly — not to run `fly` CLI commands.

---

## `fly.toml` — Backend

```toml
app = "{username}-ai-{project-slug}-api"
primary_region = "iad"

[build]
  dockerfile = "Dockerfile"

[env]
  LLM_PROVIDER = "google"       # anthropic | openai | google
  # DATABASE_PATH = "/data"     # uncomment for SQLite
  # CHROMA_DB_PATH = "/data/chroma_db"  # uncomment for ChromaDB

# [[services]] — TCP-level entry point. auto_start_machines = false here
# prevents the Fly proxy from waking the machine on inbound TCP connections.
[[services]]
  internal_port = 8000
  processes = ["app"]
  protocol = "tcp"
  auto_start_machines = false

# [http_service] — HTTP routing layer. auto_start_machines = false here
# prevents the HTTP router from waking the machine on inbound HTTP requests.
[http_service]
  internal_port = 8000
  auto_start_machines = false

[[http_service.checks]]
  grace_period = "5s"
  interval = "30s"
  method = "GET"
  path = "/health"
  protocol = "http"
  timeout = "10s"
  type = "http"

[checks.http_service]
  grace_period = "5s"
  interval = "30s"
  method = "GET"
  path = "/health"
  protocol = "http"
  timeout = "10s"
  type = "http"

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 256   # use 512 for ChromaDB / large in-memory indexes
```

Add `[[mounts]]` only when the backend writes durable data:

```toml
[[mounts]]
  source      = "{unique_volume_name}"   # unique per app, e.g. url_db_volume
  destination = "/data"
```

Stateless backends (no SQLite, no ChromaDB) → omit `[[mounts]]`.

---

## `fly.toml` — Frontend

```toml
app = "{username}-ai-{project-slug}-web"
primary_region = "iad"

[build]
  dockerfile = "Dockerfile"
  [build.args]
    NEXT_PUBLIC_API_URL = "https://{username}-ai-{project-slug}-api.fly.dev"

[env]
  NEXT_PUBLIC_API_URL = "https://{username}-ai-{project-slug}-api.fly.dev"

# [[services]] — TCP-level entry point. auto_start_machines = false prevents
# the Fly proxy from waking the machine on inbound TCP connections.
[[services]]
  internal_port = 3000
  processes = ["app"]
  protocol = "tcp"
  auto_start_machines = false

# [http_service] — HTTP routing layer. auto_start_machines = false prevents
# the HTTP router from waking the machine on inbound HTTP requests.
[http_service]
  internal_port = 3000
  auto_start_machines = false

[[http_service.checks]]
  grace_period = "5s"
  interval = "30s"
  method = "GET"
  path = "/"
  protocol = "http"
  timeout = "10s"
  type = "http"

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 256
```

`NEXT_PUBLIC_API_URL` **must appear in both** `[build.args]` (baked into the JS bundle) and `[env]` (covers server-side rendering). Missing either makes one rendering path use an empty URL.

---

## Secrets vs `[env]`

| Value | Where |
|-------|-------|
| API keys, tokens | GitHub Actions secrets → passed as `FLY_API_TOKEN` / set via `fly secrets set` in workflow |
| Provider names, paths, flags | `[env]` in `fly.toml` (safe to commit) |

Never put API keys in `fly.toml` or source code.

---

## VM Sizing

| Workload | `memory_mb` |
|----------|-------------|
| CRUD / simple LLM calls | 256 |
| ChromaDB / in-memory vector index | 512 |
| Large embedding or multi-agent workloads | 1024 |

---

## GitHub Actions Workflow Pattern

Each lab has one workflow per service. Copy this pattern for any new lab or capstone:

```yaml
name: Deploy {Lab} {Service} to Fly.io

on:
  workflow_dispatch:
  push:
    branches: [main]
    paths:
      - 'labs/{lab-dir}/{service}/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: superfly/flyctl-actions/setup-flyctl@master
      - name: Deploy
        env:
          FLY_API_TOKEN: ${{ secrets.{LAB}_FLY_API_TOKEN }}
        run: flyctl deploy --remote-only --config fly.toml
        working-directory: ./labs/{lab-dir}/{service}
```

When adding a workflow for a new lab:
1. Update `name:`, `paths:`, `working-directory:` for the new service folder
2. Create a matching `FLY_API_TOKEN` secret in GitHub → Settings → Secrets and variables → Actions
3. `--remote-only` builds the Docker image on Fly.io's builders, not the runner

---

## Dockerfile — Backend

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Dockerfile — Frontend (Production)

```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
RUN npm run build

FROM node:18-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
EXPOSE 3000
CMD ["node", "server.js"]
```

## `.dockerignore` (Backend)

```
__pycache__/
*.pyc
.env
.git
*.db
chroma_db/
.venv/
```
EOF`, and this is the output of running that command instead:
$  cat > "c:\Users\tringo\Desktop\taller_technologies\AI\Agentic_AI_Training_Pro
gram\.github\instructions\flyio-deployment.instructions.md" << 'EOF'
> ---
> applyTo: "**/fly.toml,**/Dockerfile,**/.dockerignore,**/.github/workflows/**" 
> ---
>
> # Fly.io — Configuration & GitHub Actions
>
> Deployment is handled by GitHub Actions workflows in `.github/workflows/`. The
 agent's job is to configure `fly.toml`, Dockerfiles, and workflow YAML correctl
y — not to run `fly` CLI commands.
>
> ---
>
> ## `fly.toml` — Backend
>
> ```toml
> app = "{username}-ai-{project-slug}-api"
> primary_region = "iad"
>
> [env]
>   LLM_PROVIDER = "google"       # anthropic | openai | google
>   # DATABASE_PATH = "/data"     # uncomment for SQLite
>   # CHROMA_DB_PATH = "/data/chroma_db"  # uncomment for ChromaDB
>
> [http_service]
>   internal_port = 8000
>   force_https = true
>   auto_start_machines = true
>   min_machines_running = 0
>
>   [[http_service.checks]]
>     grace_period = "10s"
>     interval = "30s"
>     method = "GET"
>     path = "/health"
>     timeout = "5s"
>
> [[vm]]
>   cpu_kind = "shared"
>   cpus = 1
>   memory_mb = 256   # use 512 for ChromaDB / large in-memory indexes
> ```
>
> Add `[[mounts]]` only when the backend writes durable data:
>
> ```toml
> [[mounts]]
>   source      = "{unique_volume_name}"   # unique per app, e.g. url_db_volume 
>   destination = "/data"
> ```
>
> Stateless backends (no SQLite, no ChromaDB) → omit `[[mounts]]`.
>
> ---
> 
> ## `fly.toml` — Frontend
>
> ```toml
> app = "{username}-ai-{project-slug}-web"
> primary_region = "iad"
>
> [build]
>   [build.args]
>     NEXT_PUBLIC_API_URL = "https://{username}-ai-{project-slug}-api.fly.dev"  
>
> [env]
>   NEXT_PUBLIC_API_URL = "https://{username}-ai-{project-slug}-api.fly.dev"
>
> [http_service]
>   internal_port = 3000
>   force_https = true
>   auto_start_machines = true
>   min_machines_running = 0
>
> [[vm]]
>   cpu_kind = "shared"
>   cpus = 1
>   memory_mb = 256
> ```
>
> `NEXT_PUBLIC_API_URL` **must appear in both** `[build.args]` (baked into the J
S bundle) and `[env]` (covers server-side rendering). Missing either makes one r
endering path use an empty URL.
> 
> ---
>
> ## Secrets vs `[env]`
>
> | Value | Where |
> |-------|-------|
> | API keys, tokens | GitHub Actions secrets → passed as `FLY_API_TOKEN` / set 
via `fly secrets set` in workflow |
> | Provider names, paths, flags | `[env]` in `fly.toml` (safe to commit) |     
>
> Never put API keys in `fly.toml` or source code.
>
> ---
>
> ## VM Sizing
>
> | Workload | `memory_mb` |
> |----------|-------------|
> | CRUD / simple LLM calls | 256 |
> | ChromaDB / in-memory vector index | 512 |
> | Large embedding or multi-agent workloads | 1024 |
>
> ---
>
> ## GitHub Actions Workflow Pattern
>
> Each lab has one workflow per service. Copy this pattern for any new lab or ca
pstone:
>
> ```yaml
> name: Deploy {Lab} {Service} to Fly.io
>
> on:
>   workflow_dispatch:
>   push:
>     branches: [main]
>     paths:
>       - 'labs/{lab-dir}/{service}/**'
>
> jobs:
>   deploy:
>     runs-on: ubuntu-latest
>     steps:
>       - uses: actions/checkout@v4
>       - uses: superfly/flyctl-actions/setup-flyctl@master
>       - name: Deploy
>         env:
>           FLY_API_TOKEN: ${{ secrets.{LAB}_FLY_API_TOKEN }}
>         run: flyctl deploy --remote-only --config fly.toml
>         working-directory: ./labs/{lab-dir}/{service}
> ```
>
> When adding a workflow for a new lab:
> 1. Update `name:`, `paths:`, `working-directory:` for the new service folder  
> 2. Create a matching `FLY_API_TOKEN` secret in GitHub → Settings → Secrets and
 variables → Actions
> 3. `--remote-only` builds the Docker image on Fly.io's builders, not the runne
r
> 
> ---
>
> ## Dockerfile — Backend
>
> ```dockerfile
> FROM python:3.11-slim
> WORKDIR /app
> COPY requirements.txt .
> RUN pip install --no-cache-dir -r requirements.txt
> COPY . .
> EXPOSE 8000
> CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
> ```
>
> ## Dockerfile — Frontend (Production)
>
> ```dockerfile
> FROM node:18-alpine AS builder
> WORKDIR /app
> COPY package*.json ./
> RUN npm ci
> COPY . .
> ARG NEXT_PUBLIC_API_URL
> ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
> RUN npm run build
>
> FROM node:18-alpine AS runner
> WORKDIR /app
> ENV NODE_ENV=production
> COPY --from=builder /app/public ./public
> COPY --from=builder /app/.next/standalone ./
> COPY --from=builder /app/.next/static ./.next/static
> EXPOSE 3000
> CMD ["node", "server.js"]
> ```
>
> ## `.dockerignore` (Backend)
>
> ```
> __pycache__/
> *.pyc
> .env
> .git
> *.db
> chroma_db/
> .venv/
> ```
> EOF
data[i]>0:\\n            result.append(data[i]*2)\\n    return result", "languag
e": "python" }';89b4db27-d62d-45f1-88bd-8af83f80736b