# Full Stack AI Application

This directory contains a complete Docker Compose orchestration for a full-stack AI application with the following services:

- **Frontend**: Next.js web application
- **Backend**: FastAPI REST API
- **PostgreSQL**: Relational database with audit trails
- **Redis**: Caching and session management
- **Qdrant**: Vector database for embeddings

## Architecture

```
┌─────────────┐
│   Frontend  │ (Next.js :3000)
│   (React)   │
└──────┬──────┘
       │
       ↓
┌─────────────┐
│   Backend   │ (FastAPI :8000)
│   (Python)  │
└──────┬──────┘
       │
       ├─────→ PostgreSQL :5432 (Relational Data)
       ├─────→ Redis :6379 (Cache/Sessions)
       └─────→ Qdrant :6333 (Vector Search)
```

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- At least 4GB RAM available
- Ports 3000, 6333, 6334, 6379, 8000, 5432 available

### Initial Setup

1. **Copy environment configuration**:
   ```bash
   cp .env.example .env
   ```

2. **Update environment variables** (edit `.env`):
   - Change default passwords
   - Add API keys if needed
   - Configure application settings

3. **Create backend and frontend placeholder directories** (see below)

4. **Start all services**:
   ```bash
   docker-compose up -d
   ```

5. **Check service health**:
   ```bash
   docker-compose ps
   ```

## Service Endpoints

Once all services are running:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
  - API Docs: http://localhost:8000/docs
  - Health: http://localhost:8000/health
- **Qdrant Dashboard**: http://localhost:6333/dashboard
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

## Creating Backend Service

Create a `backend` directory with the following structure:

### backend/Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

### backend/requirements.txt

```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
pydantic-settings==2.1.0
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
redis==5.0.1
qdrant-client==1.7.0
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
httpx==0.26.0
```

### backend/main.py

```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import redis
from qdrant_client import QdrantClient
from sqlalchemy import create_engine, text

app = FastAPI(
    title="AI Training API",
    description="Full-stack AI application backend",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connections (lazy initialization)
_db_engine = None
_redis_client = None
_qdrant_client = None

def get_db_engine():
    global _db_engine
    if _db_engine is None:
        database_url = os.getenv("DATABASE_URL")
        _db_engine = create_engine(database_url)
    return _db_engine

def get_redis_client():
    global _redis_client
    if _redis_client is None:
        redis_url = os.getenv("REDIS_URL")
        _redis_client = redis.from_url(redis_url)
    return _redis_client

def get_qdrant_client():
    global _qdrant_client
    if _qdrant_client is None:
        qdrant_host = os.getenv("QDRANT_HOST", "localhost")
        qdrant_port = int(os.getenv("QDRANT_PORT", 6333))
        _qdrant_client = QdrantClient(host=qdrant_host, port=qdrant_port)
    return _qdrant_client

@app.get("/")
async def root():
    return {
        "message": "AI Training API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for Docker"""
    health = {
        "status": "healthy",
        "services": {}
    }

    # Check PostgreSQL
    try:
        engine = get_db_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        health["services"]["postgres"] = "connected"
    except Exception as e:
        health["services"]["postgres"] = f"error: {str(e)}"
        health["status"] = "unhealthy"

    # Check Redis
    try:
        r = get_redis_client()
        r.ping()
        health["services"]["redis"] = "connected"
    except Exception as e:
        health["services"]["redis"] = f"error: {str(e)}"
        health["status"] = "unhealthy"

    # Check Qdrant
    try:
        q = get_qdrant_client()
        q.get_collections()
        health["services"]["qdrant"] = "connected"
    except Exception as e:
        health["services"]["qdrant"] = f"error: {str(e)}"
        health["status"] = "unhealthy"

    if health["status"] != "healthy":
        raise HTTPException(status_code=503, detail=health)

    return health

class PredictRequest(BaseModel):
    text: str

@app.post("/api/predict")
async def predict(request: PredictRequest):
    """Example prediction endpoint"""
    return {
        "input": request.text,
        "prediction": "positive",
        "confidence": 0.95
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Creating Frontend Service

Create a `frontend` directory with the following structure:

### frontend/Dockerfile

```dockerfile
FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application
COPY . .

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD node healthcheck.js || exit 1

# Run in development mode
CMD ["npm", "run", "dev"]
```

### frontend/package.json

```json
{
  "name": "ai-training-frontend",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "14.1.0",
    "react": "18.2.0",
    "react-dom": "18.2.0"
  },
  "devDependencies": {
    "@types/node": "20.11.5",
    "@types/react": "18.2.48",
    "@types/react-dom": "18.2.18",
    "typescript": "5.3.3"
  }
}
```

### frontend/healthcheck.js

```javascript
const http = require('http');

const options = {
  host: 'localhost',
  port: 3000,
  path: '/api/health',
  timeout: 2000
};

const request = http.request(options, (res) => {
  if (res.statusCode === 200) {
    process.exit(0);
  } else {
    process.exit(1);
  }
});

request.on('error', () => {
  process.exit(1);
});

request.end();
```

### frontend/pages/api/health.js

```javascript
export default function handler(req, res) {
  res.status(200).json({ status: 'healthy' });
}
```

### frontend/pages/index.js

```javascript
import { useState } from 'react';

export default function Home() {
  const [text, setText] = useState('');
  const [result, setResult] = useState(null);

  const handlePredict = async () => {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });
    const data = await response.json();
    setResult(data);
  };

  return (
    <div style={{ padding: '50px' }}>
      <h1>AI Training Application</h1>
      <input
        type="text"
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Enter text..."
        style={{ width: '300px', padding: '10px' }}
      />
      <button onClick={handlePredict} style={{ marginLeft: '10px', padding: '10px' }}>
        Predict
      </button>
      {result && (
        <div style={{ marginTop: '20px' }}>
          <h2>Result:</h2>
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
```

### frontend/next.config.js

```javascript
module.exports = {
  reactStrictMode: true,
}
```

## Management Commands

### Start all services

```bash
docker-compose up -d
```

### Stop all services

```bash
docker-compose down
```

### View logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Rebuild services

```bash
docker-compose up -d --build
```

### Check service status

```bash
docker-compose ps
```

### Scale services

```bash
docker-compose up -d --scale backend=3
```

## Database Management

### Access PostgreSQL

```bash
docker-compose exec postgres psql -U postgres -d ai_training
```

### Run migrations

```bash
docker-compose exec backend alembic upgrade head
```

### Backup database

```bash
docker-compose exec postgres pg_dump -U postgres ai_training > backup.sql
```

## Development Workflow

### Hot Reloading

Both backend and frontend support hot reloading:
- **Backend**: Uvicorn auto-reloads on file changes
- **Frontend**: Next.js Fast Refresh enabled

### Adding Dependencies

**Backend**:
```bash
# Add to requirements.txt, then:
docker-compose exec backend pip install <package>
# Or rebuild:
docker-compose up -d --build backend
```

**Frontend**:
```bash
# Add to package.json, then:
docker-compose exec frontend npm install
# Or rebuild:
docker-compose up -d --build frontend
```

## Production Deployment

### Pre-deployment Checklist

1. **Update `.env` file**:
   - Set `APP_ENV=production`
   - Use strong passwords
   - Configure proper CORS origins
   - Add production API keys

2. **Security**:
   - Change all default passwords
   - Use secrets management (Docker Secrets, Vault)
   - Enable HTTPS/TLS
   - Configure firewall rules

3. **Performance**:
   - Adjust memory limits in docker-compose.yml
   - Configure connection pools
   - Enable caching strategies
   - Set up CDN for static assets

4. **Monitoring**:
   - Add logging aggregation (ELK, Grafana Loki)
   - Set up metrics (Prometheus, Grafana)
   - Configure alerts
   - Enable health checks

### Production Build

```bash
# Build optimized images
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Troubleshooting

### Services not starting

```bash
# Check logs
docker-compose logs

# Check individual service
docker-compose logs backend
```

### Database connection issues

```bash
# Check PostgreSQL is ready
docker-compose exec postgres pg_isready

# Check connection string
docker-compose exec backend env | grep DATABASE_URL
```

### Port conflicts

```bash
# Change ports in .env file
FRONTEND_PORT=3001
BACKEND_PORT=8001
```

### Reset everything

```bash
docker-compose down -v
docker-compose up -d --build
```

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/documentation)
- [Qdrant Documentation](https://qdrant.tech/documentation/)

## License

This configuration is part of the AI Training course materials.
