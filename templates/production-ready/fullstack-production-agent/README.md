# Fullstack Production Agent Template

Complete production-ready AI agent with all patterns pre-integrated.

## Features

✅ **Production Patterns**
- Rate limiting (token bucket algorithm)
- Caching (exact + semantic)
- Retry and fallback logic
- Circuit breaker
- Graceful degradation

✅ **Security**
- Input validation (Pydantic)
- Prompt injection detection
- Output sanitization
- API key management
- CORS configuration

✅ **Observability**
- Structured logging (JSON)
- Request tracing
- Performance metrics
- Cost tracking
- Health checks

✅ **Responsible AI**
- Bias detection
- Audit trails
- Human-in-the-loop
- Confidence-based escalation
- Explainability

✅ **Deployment Ready**
- Railway configuration
- Render configuration
- Docker support
- Environment management
- Database migrations

## Quick Start

```bash
# Clone template
cp -r templates/production-ready/fullstack-production-agent my-agent
cd my-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Initialize database (if using audit trails)
python -m alembic upgrade head

# Run development server
uvicorn src.main:app --reload

# Test endpoint
curl http://localhost:8000/health
```

## Project Structure

```
fullstack-production-agent/
├── src/
│   ├── main.py              # FastAPI application
│   ├── agent.py             # Core agent logic
│   ├── rate_limiter.py      # Rate limiting
│   ├── cache.py             # Caching layer
│   ├── security.py          # Security utilities
│   ├── governance.py        # Responsible AI
│   └── llm_client.py        # LLM wrapper
├── config/
│   └── settings.py          # Configuration
├── tests/
│   ├── test_agent.py        # Unit tests
│   └── test_integration.py  # Integration tests
├── requirements.txt         # Dependencies
├── railway.toml            # Railway config
├── render.yaml             # Render config
├── Dockerfile              # Docker config
└── .env.example            # Environment template
```

## Configuration

### Environment Variables

```bash
# Required
ANTHROPIC_API_KEY=your-key-here

# Optional (with defaults)
ENVIRONMENT=development
DEBUG=false
LOG_LEVEL=INFO

# Rate Limiting
RATE_LIMIT_RPM=60
RATE_LIMIT_TPM=100000

# Caching
CACHE_TTL_SECONDS=3600
SEMANTIC_CACHE_THRESHOLD=0.95

# Responsible AI
ENABLE_BIAS_DETECTION=true
ENABLE_AUDIT_TRAIL=true
HUMAN_APPROVAL_THRESHOLD=0.7

# Database (for audit trails)
DATABASE_URL=postgresql://localhost/agent_db
```

## API Endpoints

### Health Check
```bash
GET /health

Response:
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime": 3600
}
```

### Agent Query
```bash
POST /agent/query

Request:
{
  "query": "Analyze this code for security issues",
  "context": {...},
  "user_id": "user_123"
}

Response:
{
  "response": "...",
  "confidence": 0.89,
  "reasoning": "...",
  "audit_id": "audit_abc123",
  "cost": 0.002
}
```

### Metrics
```bash
GET /metrics

Response:
{
  "requests_total": 1000,
  "cache_hit_rate": 0.65,
  "average_latency_ms": 1200,
  "cost_total_usd": 5.23
}
```

## Deployment

### Deploy to Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Set environment variables
railway variables set ANTHROPIC_API_KEY=your-key

# Deploy
railway up
```

### Deploy to Render

```bash
# Connect your GitHub repo to Render
# Render will automatically deploy using render.yaml
```

### Deploy with Docker

```bash
# Build image
docker build -t production-agent .

# Run container
docker run -p 8000:8000 --env-file .env production-agent
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test
pytest tests/test_agent.py::test_agent_query

# Load testing
locust -f tests/load_test.py
```

## Monitoring

### Logs

Structured JSON logs:
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "message": "Agent query completed",
  "user_id": "user_123",
  "request_id": "req_abc123",
  "latency_ms": 1200,
  "cost_usd": 0.002,
  "confidence": 0.89
}
```

### Metrics Dashboard

Access metrics at: `GET /metrics`

Key metrics:
- Requests per minute
- Cache hit rate
- Average latency (P50, P95, P99)
- Error rate
- Cost per hour

## Responsible AI

### Bias Detection

Automatically scans all outputs:
```python
{
  "has_bias": false,
  "bias_types": [],
  "score": 0.15
}
```

### Audit Trail

Every decision is logged:
```python
{
  "audit_id": "audit_abc123",
  "action": "code_review",
  "input_hash": "a1b2c3...",
  "output_hash": "d4e5f6...",
  "model": "claude-3-5-sonnet",
  "confidence": 0.89,
  "approved_by": "user_123",
  "cost": 0.002
}
```

### Human-in-the-Loop

Low confidence queries escalate to human:
```python
if confidence < 0.7:
    await request_human_approval(query, reasoning)
```

## Customization

### Add New Tool

```python
# src/tools.py
class CustomTool(Tool):
    name = "custom_tool"
    description = "Does something custom"

    def execute(self, **params):
        # Implementation
        return result

# src/agent.py
agent = Agent(tools=[CustomTool()])
```

### Adjust Rate Limits

```python
# config/settings.py
rate_limit_rpm: int = 100  # Increase to 100 RPM
rate_limit_tpm: int = 200000  # Increase token limit
```

### Add Custom Metrics

```python
# src/metrics.py
from prometheus_client import Counter

custom_metric = Counter('custom_events', 'Description')
custom_metric.inc()
```

## Troubleshooting

### "Rate limit exceeded"
- Increase `RATE_LIMIT_RPM` in .env
- Check per-user limits
- Consider adding request queuing

### "Cache not working"
- Verify semantic cache threshold
- Check cache TTL settings
- Review cache hit rate in metrics

### "High latency"
- Enable semantic caching
- Use model routing (Haiku for simple queries)
- Increase cache TTL if appropriate

### "Bias detected"
- Review training prompts
- Add explicit bias mitigation to system prompt
- Consider human review for sensitive outputs

## Production Checklist

Before going live:

- [ ] Environment variables configured
- [ ] Rate limits set appropriately
- [ ] Caching strategy reviewed
- [ ] Security review completed
- [ ] Monitoring/alerting configured
- [ ] Error tracking set up (Sentry)
- [ ] Audit trail database configured
- [ ] Load testing completed
- [ ] Documentation updated
- [ ] Backup plan in place

## Support

- **Issues**: Report bugs in main repository
- **Questions**: Ask in Discord/Slack
- **Documentation**: See main training materials

---

**Ready to deploy? Follow the Quick Start guide above! 🚀**
