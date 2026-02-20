# FastAPI Production Template

A production-ready FastAPI template with best practices for building AI-powered APIs.

## Features

- FastAPI with async support
- CORS middleware configured
- Pydantic models for request/response validation
- LLM service integration (Anthropic Claude)
- Health check endpoint
- Error handling middleware
- Environment variable configuration
- Docker support
- Basic testing setup

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
```

Edit `.env`:
```
ANTHROPIC_API_KEY=your-api-key-here
ENVIRONMENT=development
```

### 3. Run Locally

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --port 8000

# Or use Python directly
python -m app.main
```

Visit:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

### 4. Run with Docker

```bash
# Build image
docker build -t fastapi-app .

# Run container
docker run -p 8000:8000 --env-file .env fastapi-app
```

## Project Structure

```
fastapi-template/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app setup
│   ├── routers/
│   │   ├── __init__.py
│   │   └── api.py           # API endpoints
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py       # Pydantic models
│   └── services/
│       ├── __init__.py
│       └── llm_service.py   # LLM integration
├── tests/
│   └── test_api.py          # API tests
├── requirements.txt         # Python dependencies
├── .env.example            # Environment template
├── Dockerfile              # Container config
└── README.md               # This file
```

## API Endpoints

### Health Check
```bash
GET /health
```

Returns service status.

### Chat Completion
```bash
POST /api/chat
Content-Type: application/json

{
  "message": "Hello, how are you?",
  "max_tokens": 1024
}
```

Returns AI-generated response.

### Example Usage

```python
import requests

# Chat with AI
response = requests.post(
    "http://localhost:8000/api/chat",
    json={"message": "Explain FastAPI in one sentence"}
)
print(response.json())
```

## Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=app tests/
```

## Production Deployment

### Environment Variables

Set these in production:
- `ANTHROPIC_API_KEY`: Your Anthropic API key
- `ENVIRONMENT`: Set to "production"
- `CORS_ORIGINS`: Configure allowed origins
- `LOG_LEVEL`: Set to "INFO" or "WARNING"

### Docker Deployment

The included Dockerfile is production-ready with:
- Health checks
- Non-root user
- Optimized image size
- Security best practices

### Cloud Platforms

This template works with:
- Railway
- Render
- Google Cloud Run
- AWS ECS/Fargate
- Azure Container Apps

## Development Tips

### Adding New Routes

1. Create route in `app/routers/api.py`
2. Define Pydantic models in `app/models/schemas.py`
3. Add business logic in `app/services/`

### Error Handling

The template includes global error handlers that:
- Catch HTTP exceptions
- Handle validation errors
- Log errors properly
- Return consistent JSON responses

### CORS Configuration

Update `app/main.py` to configure CORS for your domain:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Production origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Anthropic API Docs](https://docs.anthropic.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

## License

MIT - Use freely for your projects
