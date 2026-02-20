# Deployment Guide

Complete deployment guide for the Code Review Agent.

## Prerequisites

- Python 3.11+
- GitHub account with personal access token
- Anthropic API key
- (Optional) Docker for containerized deployment

## Local Development

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your credentials
```

Required environment variables:
- `GITHUB_TOKEN`: GitHub personal access token with `repo` scope
- `ANTHROPIC_API_KEY`: Anthropic API key
- `GITHUB_WEBHOOK_SECRET`: Random secret for webhook verification

### 3. Run Locally

```bash
# Start webhook server
python -m src.webhook_server

# Or use uvicorn directly
uvicorn src.webhook_server:app --reload --port 8000
```

### 4. Test with ngrok

For local webhook testing:

```bash
# Install ngrok
brew install ngrok  # macOS
# or download from https://ngrok.com

# Create tunnel
ngrok http 8000

# Use the HTTPS URL for GitHub webhook
# Example: https://abc123.ngrok.io/webhooks/github
```

## Production Deployment

### Option 1: Docker

```bash
# Build image
docker build -t code-review-agent .

# Run container
docker run -d \
  --name code-review-agent \
  -p 8000:8000 \
  --env-file .env \
  code-review-agent

# Or use docker-compose
docker-compose up -d
```

### Option 2: Railway

1. Install Railway CLI:
```bash
npm i -g @railway/cli
```

2. Initialize and deploy:
```bash
railway login
railway init
railway up
```

3. Add environment variables in Railway dashboard

### Option 3: Render

1. Create `render.yaml`:
```yaml
services:
  - type: web
    name: code-review-agent
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python -m src.webhook_server
    envVars:
      - key: GITHUB_TOKEN
        sync: false
      - key: ANTHROPIC_API_KEY
        sync: false
      - key: GITHUB_WEBHOOK_SECRET
        sync: false
```

2. Connect GitHub repo to Render
3. Configure environment variables
4. Deploy

### Option 4: Heroku

```bash
# Install Heroku CLI
brew install heroku/brew/heroku

# Login and create app
heroku login
heroku create your-app-name

# Set environment variables
heroku config:set GITHUB_TOKEN=your_token
heroku config:set ANTHROPIC_API_KEY=your_key
heroku config:set GITHUB_WEBHOOK_SECRET=your_secret

# Deploy
git push heroku main
```

### Option 5: DigitalOcean App Platform

1. Create `app.yaml`:
```yaml
name: code-review-agent
services:
  - name: web
    github:
      repo: your-username/your-repo
      branch: main
    build_command: pip install -r requirements.txt
    run_command: python -m src.webhook_server
    environment_slug: python
    instance_count: 1
    instance_size_slug: basic-xxs
    envs:
      - key: GITHUB_TOKEN
        scope: RUN_TIME
        type: SECRET
      - key: ANTHROPIC_API_KEY
        scope: RUN_TIME
        type: SECRET
```

2. Deploy via DigitalOcean dashboard

## GitHub Webhook Setup

### 1. Go to Repository Settings

Navigate to: `https://github.com/owner/repo/settings/hooks`

### 2. Add Webhook

Click "Add webhook" and configure:

- **Payload URL**: `https://your-domain.com/webhooks/github`
- **Content type**: `application/json`
- **Secret**: Same value as `GITHUB_WEBHOOK_SECRET` in .env
- **Events**: Select "Pull requests"
- **Active**: ✓ Checked

### 3. Test Webhook

Create a test PR to verify the webhook is working. Check:
- GitHub webhook delivery logs
- Your application logs
- PR comments

## Monitoring

### Health Check

```bash
curl https://your-domain.com/health
```

Response:
```json
{
  "status": "healthy",
  "uptime_seconds": 3600,
  "reviews_completed": 10,
  "reviews_failed": 0
}
```

### Metrics

```bash
curl https://your-domain.com/metrics
```

Response:
```json
{
  "webhooks_received": 15,
  "reviews_completed": 10,
  "reviews_failed": 0,
  "total_cost_usd": 0.45,
  "average_cost_usd": 0.045,
  "uptime_seconds": 3600
}
```

### Logs

Monitor application logs for errors and performance:

```bash
# Docker
docker logs -f code-review-agent

# Railway
railway logs

# Heroku
heroku logs --tail

# Local
# Logs written to stdout
```

## Cost Management

### Monitor Costs

Check `/metrics` endpoint regularly:
```bash
curl https://your-domain.com/metrics | jq '.total_cost_usd'
```

### Set Cost Limits

In `.env`:
```bash
MAX_COST_PER_REVIEW=0.50  # Maximum $0.50 per review
```

### Typical Costs

Based on Claude 3.5 Sonnet pricing:
- Small PR (1-5 files): $0.01-0.05
- Medium PR (6-15 files): $0.05-0.15
- Large PR (16+ files): $0.15-0.50

## Security Best Practices

### 1. Secure Secrets

- Never commit `.env` file
- Use secret management (Railway, Heroku Config Vars, etc.)
- Rotate tokens regularly

### 2. Webhook Signature Verification

Always enabled by default. Verifies:
- HMAC-SHA256 signature
- GitHub origin

### 3. Rate Limiting

Configured per repository:
```bash
RATE_LIMIT_REQUESTS_PER_MINUTE=60
```

### 4. Input Validation

All PR data is validated before processing.

## Troubleshooting

### Webhook Not Firing

1. Check GitHub webhook delivery logs
2. Verify webhook URL is publicly accessible
3. Check signature verification in logs
4. Ensure webhook is active

### Reviews Not Posting

1. Check GitHub token permissions (needs `repo` scope)
2. Verify `AUTO_COMMENT=true` in .env
3. Check application logs for errors
4. Test GitHub API connection

### High Costs

1. Reduce `MAX_FILES_PER_PR`
2. Enable caching: `ENABLE_CACHING=true`
3. Increase `SEVERITY_THRESHOLD` to reduce comment size
4. Set `MAX_COST_PER_REVIEW` limit

### Rate Limits

1. Adjust `RATE_LIMIT_REQUESTS_PER_MINUTE`
2. Check GitHub API rate limits: `/rate_limit` endpoint
3. Use caching to reduce API calls

## Scaling

### Horizontal Scaling

Deploy multiple instances with load balancer:
- Use Redis for shared rate limiting
- Use PostgreSQL for audit logging
- Implement message queue (RabbitMQ, SQS)

### Performance Optimization

1. Enable caching
2. Limit files per review
3. Use async processing
4. Implement request queuing

## Support

For issues or questions:
1. Check application logs
2. Review GitHub webhook deliveries
3. Test with manual trigger: `POST /review/trigger`
4. Monitor `/metrics` and `/health` endpoints
