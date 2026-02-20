# Quick Start Guide

Get the Code Review Agent running in 5 minutes.

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your keys
nano .env
```

Required keys:
```bash
GITHUB_TOKEN=ghp_your_token_here
ANTHROPIC_API_KEY=sk-ant-your_key_here
GITHUB_WEBHOOK_SECRET=your_random_secret_here
```

### Get GitHub Token

1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes: `repo` (full repository access)
4. Generate and copy token

### Get Anthropic API Key

1. Go to https://console.anthropic.com/
2. Navigate to API Keys
3. Create new key
4. Copy key

### Generate Webhook Secret

```bash
# Generate random secret
python -c "import secrets; print(secrets.token_hex(32))"
```

## Step 3: Test Locally

```bash
# Run the server
python -m src.webhook_server

# Server will start on http://localhost:8000
```

Visit http://localhost:8000/health to verify it's running.

## Step 4: Test Static Analysis (No API Keys)

```bash
# Run static analysis example
python example_usage.py static
```

This will analyze example code without making API calls.

## Step 5: Setup ngrok (for GitHub webhooks)

```bash
# Install ngrok (macOS)
brew install ngrok

# Or download from https://ngrok.com

# Start tunnel
ngrok http 8000
```

Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

## Step 6: Configure GitHub Webhook

1. Go to your repository on GitHub
2. Click Settings → Webhooks → Add webhook
3. Configure:
   - **Payload URL**: `https://abc123.ngrok.io/webhooks/github`
   - **Content type**: `application/json`
   - **Secret**: Your `GITHUB_WEBHOOK_SECRET` from .env
   - **Events**: Select "Pull requests"
4. Click "Add webhook"

## Step 7: Test with a PR

1. Create a test pull request in your repository
2. Watch the webhook server logs
3. The agent will automatically review the PR
4. Check the PR for a comment with the review

## Example Test PR

Create a file with intentional issues:

```python
# test.py
def get_user(user_id):
    # SQL injection vulnerability
    query = f"SELECT * FROM users WHERE id={user_id}"
    cursor.execute(query)

    # Hardcoded secret
    api_key = "sk-1234567890abcdef"

    return result
```

The agent should detect:
- SQL injection vulnerability (High severity)
- Hardcoded secret (High severity)
- Missing error handling (Medium severity)

## Verify It's Working

### Check Health

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "uptime_seconds": 120.5,
  "reviews_completed": 1,
  "reviews_failed": 0
}
```

### Check Metrics

```bash
curl http://localhost:8000/metrics
```

Expected response:
```json
{
  "webhooks_received": 1,
  "reviews_completed": 1,
  "reviews_failed": 0,
  "total_cost_usd": 0.045,
  "average_cost_usd": 0.045,
  "uptime_seconds": 180.2
}
```

### Manual Trigger

Test the agent without a webhook:

```bash
curl -X POST "http://localhost:8000/review/trigger?owner=your-username&repo=your-repo&pr_number=1"
```

## Troubleshooting

### "Module not found" error

```bash
# Make sure you're in the project directory
cd /path/to/code-review-agent

# Install dependencies
pip install -r requirements.txt
```

### Webhook not receiving events

1. Check ngrok is running: `http://127.0.0.1:4040` (ngrok inspector)
2. Verify webhook URL in GitHub settings
3. Check webhook secret matches .env file
4. Look at GitHub webhook "Recent Deliveries" for errors

### "Invalid signature" error

- Make sure `GITHUB_WEBHOOK_SECRET` in .env matches GitHub webhook secret
- Check webhook server logs for signature verification details

### Review not posting

1. Verify `AUTO_COMMENT=true` in .env
2. Check GitHub token has `repo` scope
3. Look at application logs for errors
4. Test GitHub API connection:
   ```bash
   curl -H "Authorization: Bearer $GITHUB_TOKEN" https://api.github.com/user
   ```

### API rate limits

1. Check rate limits:
   ```bash
   curl -H "Authorization: Bearer $GITHUB_TOKEN" https://api.github.com/rate_limit
   ```
2. Adjust `RATE_LIMIT_REQUESTS_PER_MINUTE` in .env

## Next Steps

1. **Deploy to production**: See [DEPLOYMENT.md](DEPLOYMENT.md)
2. **Customize prompts**: Edit `src/prompts.py`
3. **Add custom rules**: Extend `src/code_analyzer.py`
4. **Run tests**: `pytest tests/`
5. **Monitor costs**: Check `/metrics` endpoint regularly

## Quick Reference

### Endpoints

- `GET /` - Service info
- `GET /health` - Health check
- `GET /metrics` - Application metrics
- `POST /webhooks/github` - GitHub webhook receiver
- `POST /review/trigger` - Manual review trigger

### Environment Variables

See `.env.example` for all available options.

### Cost Estimates

Typical costs per review (Claude 3.5 Sonnet):
- Small PR (1-5 files): $0.01-0.05
- Medium PR (6-15 files): $0.05-0.15
- Large PR (16+ files): $0.15-0.50

### Support

If you encounter issues:
1. Check logs: Application will print detailed error messages
2. Review GitHub webhook deliveries
3. Test with `python example_usage.py static` (no API keys needed)
4. Check `/health` and `/metrics` endpoints
