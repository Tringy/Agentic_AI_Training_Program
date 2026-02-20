# URL Shortener - Deployment Guide

Complete guide for deploying the URL Shortener to Fly.io with Docker and GitHub Actions CI/CD.

## Architecture

```
GitHub Repo
    ↓
    ├─ Push to main → GitHub Actions → Fly.io
    │
    ├─ Backend (Python FastAPI)
    │  ├─ Docker: python:3.11-slim
    │  ├─ Port: 8000
    │  ├─ Volume: /data (SQLite database)
    │  └─ URL: https://url-shortener-api.fly.dev
    │
    └─ Frontend (Next.js 14)
       ├─ Docker: node:20-alpine
       ├─ Port: 3000
       └─ URL: https://url-shortener-web.fly.dev
```

## 5-Minute Quick Start

### Prerequisites
```bash
# Install and authenticate with Fly.io
curl -L https://fly.io/install.sh | sh
flyctl auth login
```

### Deploy Backend
```bash
cd backend

# Create app
flyctl apps create --name tringo-ai-lab01-url-shortener-api

# Create SQLite volume
flyctl volumes create url_db_volume --size 10 --app tringo-ai-lab01-url-shortener-api

# Deploy
flyctl deploy

cd ..
```

### Deploy Frontend
```bash
cd frontend

# Create app
flyctl apps create --name tringo-ai-lab01-url-shortener-web

# Deploy
flyctl deploy

cd ..
```

### Setup GitHub Actions
1. Get your API token:
   ```bash
   flyctl auth token
   ```

2. Go to your GitHub repo → **Settings → Secrets and variables → Actions**

3. Add two separate secrets:
   - Name: `LAB01_URL_SHORTENER_FLY_API_TOKEN` | Value: (paste token)
   - Name: `LAB01_URL_SHORTENER_WEB_FLY_API_TOKEN` | Value: (paste token)

**Done!** Future pushes to `main` auto-deploy.

---

## Detailed Setup

### Backend Deployment

```bash
cd backend

# Create the app
flyctl apps create --name tringo-ai-lab01-url-shortener-api

# Create persistent volume for SQLite
flyctl volumes create url_db_volume --size 1 --app tringo-ai-lab01-url-shortener-api

# Deploy
flyctl deploy --app tringo-ai-lab01-url-shortener-api

# Verify
curl https://tringo-ai-lab01-url-shortener-api.fly.dev/health
```

### Frontend Deployment

```bash
cd frontend

# Create the app
flyctl apps create --name tringo-ai-lab01-url-shortener-web

# Deploy
flyctl deploy --app tringo-ai-lab01-url-shortener-web

# Verify
curl https://tringo-ai-lab01-url-shortener-web.fly.dev
```

### GitHub Actions Auto-Deploy

Workflows trigger automatically on push to `main`:

- **Backend**: Deploys when changes in `backend/**`
- **Frontend**: Deploys when changes in `frontend/**`

No manual deployment needed after setup!

---

## Database & Volume

The backend uses a persistent volume for SQLite at `/data`:

```bash
# List volumes
flyctl volumes list --app tringo-ai-lab01-url-shortener-api

# Connect to database
flyctl ssh console --app tringo-ai-lab01-url-shortener-api
sqlite3 /data/urls.db ".tables"
exit
```

**Important**: The volume persists across deployments and restarts.

---

## Common Fly Commands

### Manage Apps
```bash
# View info
flyctl info --app tringo-ai-lab01-url-shortener-api

# View logs
flyctl logs --app tringo-ai-lab01-url-shortener-api
flyctl logs --follow --app tringo-ai-lab01-url-shortener-api  # Real-time

# SSH into app
flyctl ssh console --app tringo-ai-lab01-url-shortener-api

# Restart app
flyctl restart --app tringo-ai-lab01-url-shortener-api

# Redeploy current code
cd backend && flyctl deploy
```

### Scaling
```bash
# Scale to multiple instances
flyctl scale count 3 --app tringo-ai-lab01-url-shortener-api

# Check current allocation
flyctl status --app tringo-ai-lab01-url-shortener-api
```

### Clean Up
```bash
# Delete app (keeps volumes)
flyctl apps destroy tringo-ai-lab01-url-shortener-api

# Delete volume
flyctl volumes delete url_db_volume --app tringo-ai-lab01-url-shortener-api
```

---

## GitHub Actions Setup

### Required Secrets

Go to **Settings → Secrets and variables → Actions** and add:

| Name | Value |
|------|-------|
| `LAB01_URL_SHORTENER_FLY_API_TOKEN` | Output of `flyctl auth token` |
| `LAB01_URL_SHORTENER_WEB_FLY_API_TOKEN` | Output of `flyctl auth token` |

### Workflow Files

Located in `.github/workflows/`:

- **deploy-backend.yml** - Triggers on backend changes
- **deploy-frontend.yml** - Triggers on frontend changes

Both use the Fly CLI to build and deploy automatically.

---

## Troubleshooting

### Backend won't start
```bash
# Check logs
flyctl logs --app tringo-ai-lab01-url-shortener-api

# Verify volume exists
flyctl volumes list --app tringo-ai-lab01-url-shortener-api

# Restart
flyctl restart --app tringo-ai-lab01-url-shortener-api
```

### Frontend can't connect to backend
1. Verify backend is running:
   ```bash
   curl https://tringo-ai-lab01-url-shortener-api.fly.dev/health
   ```
2. Check frontend logs:
   ```bash
   flyctl logs --app tringo-ai-lab01-url-shortener-web
   ```
3. Verify `NEXT_PUBLIC_API_URL` in `frontend/fly.toml` matches backend URL
4. Check browser console for CORS errors

### Database errors
```bash
# Connect to database
flyctl ssh console --app tringo-ai-lab01-url-shortener-api

# Check database
sqlite3 /data/urls.db ".tables"
sqlite3 /data/urls.db "SELECT COUNT(*) FROM urls;"

exit
```

### 502 Bad Gateway
- Check backend logs: `flyctl logs --app tringo-ai-lab01-url-shortener-api`
- Restart: `flyctl restart --app tringo-ai-lab01-url-shortener-api`

---

## Testing

### Test Backend
```bash
# Health check
curl https://tringo-ai-lab01-url-shortener-api.fly.dev/health

# Shorten a URL
curl -X POST https://tringo-ai-lab01-url-shortener-api.fly.dev/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com"}'

# Response:
# {"short_code":"abc123","short_url":"https://tringo-ai-lab01-url-shortener-api.fly.dev/abc123"}
```

### Test Frontend
1. Open https://tringo-ai-lab01-url-shortener-web.fly.dev
2. Enter a long URL
3. Click "Shorten"
4. Verify short URL works

---

## Local Development

### Using Docker Compose
```bash
# From project root (where docker-compose.yml is located)
docker-compose up --build

# Frontend: http://localhost:3000
# Backend: http://localhost:8000

# Tear down
docker-compose down
```

### Without Docker

**Terminal 1 - Backend:**
```bash
cd backend
pip install -r requirements.txt
export DATABASE_PATH=./data
export BASE_URL=http://localhost:8000
uvicorn main:app --reload
# Runs at http://localhost:8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install
npm run dev
# Runs at http://localhost:3000
```

---

## Next Steps

| Task | Command |
|------|---------|
| View backend logs | `flyctl logs --app tringo-ai-lab01-url-shortener-api` |
| View frontend logs | `flyctl logs --app tringo-ai-lab01-url-shortener-web` |
| Connect to DB | `flyctl ssh console --app tringo-ai-lab01-url-shortener-api` |
| Check app status | `flyctl status --app tringo-ai-lab01-url-shortener-api` |
| Redeploy backend | `cd backend && flyctl deploy` |
| Redeploy frontend | `cd frontend && flyctl deploy` |
| Scale backend | `flyctl scale count 3 --app tringo-ai-lab01-url-shortener-api` |
| Get app URL | `flyctl info --app tringo-ai-lab01-url-shortener-api` |

---

## Next Steps

1. **Deploy both apps** (follow Quick Start above)
2. **Test end-to-end** (use Testing section)
3. **Monitor logs** (setup alerts in Fly.io dashboard)
4. **Custom domain** (optional - Fly.io docs)
5. **Scale as needed** (use Scale commands)

---

## Support

- **Fly.io Docs**: https://fly.io/docs/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Next.js Docs**: https://nextjs.org/docs/
