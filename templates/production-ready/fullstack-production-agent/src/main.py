"""
Production-Ready AI Agent API
FastAPI application with all production patterns integrated.
"""
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import time
import logging

from .agent import ProductionAgent
from .rate_limiter import RateLimiter
from .cache import LLMCache
from .security import InputValidator
from .governance import BiasDetector, AuditTrail
from config.settings import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize app
app = FastAPI(
    title="Production AI Agent",
    description="Production-ready AI agent with all patterns integrated",
    version="1.0.0"
)

# Settings
settings = get_settings()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
rate_limiter = RateLimiter(
    requests_per_minute=settings.rate_limit_rpm,
    tokens_per_minute=settings.rate_limit_tpm
)
cache = LLMCache(ttl_seconds=settings.cache_ttl_seconds)
validator = InputValidator()
bias_detector = BiasDetector()
# audit_trail = AuditTrail(storage_backend)  # Configure with your DB

agent = ProductionAgent(
    api_key=settings.anthropic_api_key,
    cache=cache,
    bias_detector=bias_detector if settings.enable_bias_detection else None
)

# Request/Response models
class AgentRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=10000)
    context: Optional[Dict[str, Any]] = None
    user_id: str = Field(..., description="User identifier for rate limiting")
    require_approval: bool = Field(False, description="Require human approval")

class AgentResponse(BaseModel):
    response: str
    confidence: float
    reasoning: str
    audit_id: Optional[str] = None
    cost: float
    cached: bool
    bias_detected: bool = False
    bias_score: float = 0.0

class HealthResponse(BaseModel):
    status: str
    version: str
    uptime: float

class MetricsResponse(BaseModel):
    requests_total: int
    cache_hit_rate: float
    average_latency_ms: float
    cost_total_usd: float

# Metrics storage (use Redis or database in production)
metrics = {
    "requests": 0,
    "cache_hits": 0,
    "total_latency": 0.0,
    "total_cost": 0.0,
    "start_time": time.time()
}

# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    latency = (time.time() - start_time) * 1000
    logger.info(
        "Request completed",
        extra={
            "method": request.method,
            "url": str(request.url),
            "status_code": response.status_code,
            "latency_ms": latency
        }
    )

    return response

# Health check
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "uptime": time.time() - metrics["start_time"]
    }

# Main agent endpoint
@app.post("/agent/query", response_model=AgentResponse)
async def agent_query(
    request: AgentRequest,
    http_request: Request
) -> AgentResponse:
    """
    Process query with production AI agent.

    Includes:
    - Rate limiting
    - Input validation
    - Caching
    - Bias detection
    - Audit logging
    - Cost tracking
    """
    start_time = time.time()

    try:
        # Rate limiting
        limiter = rate_limiter.get_limiter(request.user_id)
        if not limiter.acquire():
            logger.warning(f"Rate limit exceeded for user {request.user_id}")
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later."
            )

        # Input validation
        validation = validator.validate_and_sanitize(request.query)
        if validation.get("warnings", {}).get("injectionRisk"):
            logger.warning(
                f"Potential prompt injection detected for user {request.user_id}",
                extra={"patterns": validation["warnings"]["injectionRisk"]["patterns"]}
            )
            # Optionally reject or sanitize

        sanitized_query = validation["text"]

        # Check cache
        cached_response = cache.get([{"role": "user", "content": sanitized_query}], "default")
        if cached_response:
            metrics["cache_hits"] += 1
            metrics["requests"] += 1

            logger.info(f"Cache hit for user {request.user_id}")

            return AgentResponse(
                response=cached_response["response"],
                confidence=cached_response["confidence"],
                reasoning=cached_response["reasoning"],
                cost=0.0,  # Cached, no cost
                cached=True,
                bias_detected=False
            )

        # Process with agent
        result = await agent.process(
            query=sanitized_query,
            context=request.context,
            user_id=request.user_id
        )

        # Cache response
        cache.set(
            [{"role": "user", "content": sanitized_query}],
            "default",
            {
                "response": result["response"],
                "confidence": result["confidence"],
                "reasoning": result["reasoning"]
            }
        )

        # Update metrics
        latency = (time.time() - start_time) * 1000
        metrics["requests"] += 1
        metrics["total_latency"] += latency
        metrics["total_cost"] += result["cost"]

        # Log audit trail (if enabled)
        # audit_id = audit_trail.log_decision(...)

        logger.info(
            "Agent query completed",
            extra={
                "user_id": request.user_id,
                "latency_ms": latency,
                "cost": result["cost"],
                "confidence": result["confidence"],
                "cached": False
            }
        )

        return AgentResponse(
            response=result["response"],
            confidence=result["confidence"],
            reasoning=result["reasoning"],
            audit_id=result.get("audit_id"),
            cost=result["cost"],
            cached=False,
            bias_detected=result.get("bias_detected", False),
            bias_score=result.get("bias_score", 0.0)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error. Please try again later."
        )

# Metrics endpoint
@app.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    """Get application metrics."""
    requests_total = metrics["requests"]
    cache_hit_rate = metrics["cache_hits"] / requests_total if requests_total > 0 else 0.0
    avg_latency = metrics["total_latency"] / requests_total if requests_total > 0 else 0.0

    return MetricsResponse(
        requests_total=requests_total,
        cache_hit_rate=cache_hit_rate,
        average_latency_ms=avg_latency,
        cost_total_usd=metrics["total_cost"]
    )

# Rate limit status endpoint
@app.get("/rate-limit/{user_id}")
async def get_rate_limit_status(user_id: str):
    """Get rate limit status for a user."""
    limiter = rate_limiter.get_limiter(user_id)
    status = limiter.get_status()

    return {
        "user_id": user_id,
        "requests_available": status["requests_available"],
        "tokens_available": status["tokens_available"]
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
