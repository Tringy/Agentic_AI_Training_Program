"""
GitHub Webhook Server with FastAPI

Receives GitHub webhook events for pull requests and triggers code reviews.

Features:
- Webhook signature verification (HMAC-SHA256)
- Rate limiting per repository
- Async processing
- Health checks and metrics
"""
import hashlib
import hmac
import json
import time
import logging
from typing import Dict, Any, Optional
from collections import defaultdict
from datetime import datetime, timedelta

from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .config import get_settings
from .github_client import GitHubClient
from .review_agent import ReviewAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Code Review Agent",
    description="GitHub-integrated AI code review agent",
    version="1.0.0"
)

# Global state (use Redis/database in production)
settings = get_settings()
review_queue: Dict[str, list] = defaultdict(list)
rate_limits: Dict[str, list] = defaultdict(list)  # repo -> list of timestamps
metrics = {
    "webhooks_received": 0,
    "reviews_completed": 0,
    "reviews_failed": 0,
    "total_cost": 0.0,
    "start_time": time.time()
}

# Initialize clients
github_client = GitHubClient(token=settings.github_token)
review_agent = ReviewAgent(
    github_client=github_client,
    anthropic_api_key=settings.anthropic_api_key
)


class WebhookPayload(BaseModel):
    """GitHub webhook payload model (simplified)."""
    action: str
    number: int
    pull_request: Dict[str, Any]
    repository: Dict[str, Any]


def verify_github_signature(payload_body: bytes, signature_header: str) -> bool:
    """
    Verify GitHub webhook signature using HMAC-SHA256.

    Args:
        payload_body: Raw request body
        signature_header: X-Hub-Signature-256 header value

    Returns:
        True if signature is valid
    """
    if not signature_header:
        logger.warning("Missing signature header")
        return False

    # Parse signature
    try:
        hash_algorithm, signature = signature_header.split('=')
    except ValueError:
        logger.warning("Invalid signature format")
        return False

    if hash_algorithm != 'sha256':
        logger.warning(f"Unsupported hash algorithm: {hash_algorithm}")
        return False

    # Calculate expected signature
    expected_signature = hmac.new(
        key=settings.github_webhook_secret.encode(),
        msg=payload_body,
        digestmod=hashlib.sha256
    ).hexdigest()

    # Compare signatures
    is_valid = hmac.compare_digest(expected_signature, signature)

    if not is_valid:
        logger.warning("Signature verification failed")

    return is_valid


def check_rate_limit(repo_full_name: str) -> bool:
    """
    Check if repository has exceeded rate limit.

    Args:
        repo_full_name: Full repository name (owner/repo)

    Returns:
        True if within rate limit
    """
    now = time.time()
    window_start = now - 60  # 1 minute window

    # Clean old timestamps
    rate_limits[repo_full_name] = [
        ts for ts in rate_limits[repo_full_name]
        if ts > window_start
    ]

    # Check limit
    current_count = len(rate_limits[repo_full_name])

    if current_count >= settings.rate_limit_requests_per_minute:
        logger.warning(
            f"Rate limit exceeded for {repo_full_name}: "
            f"{current_count} requests in last minute"
        )
        return False

    # Add timestamp
    rate_limits[repo_full_name].append(now)
    return True


async def process_pull_request_review(
    owner: str,
    repo: str,
    pr_number: int,
    action: str
):
    """
    Process pull request review asynchronously.

    Args:
        owner: Repository owner
        repo: Repository name
        pr_number: Pull request number
        action: PR action (opened, synchronize, etc.)
    """
    try:
        logger.info(f"Processing PR {owner}/{repo}#{pr_number} (action: {action})")

        # Perform review
        result = review_agent.review_pull_request(owner, repo, pr_number)

        # Update metrics
        if result["status"] == "completed":
            metrics["reviews_completed"] += 1
            metrics["total_cost"] += result.get("cost", 0.0)
            logger.info(
                f"Review completed for {owner}/{repo}#{pr_number}. "
                f"Cost: ${result.get('cost', 0):.4f}"
            )
        else:
            metrics["reviews_failed"] += 1
            logger.error(f"Review failed for {owner}/{repo}#{pr_number}: {result.get('error')}")

    except Exception as e:
        metrics["reviews_failed"] += 1
        logger.error(f"Failed to process PR review: {str(e)}", exc_info=True)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Code Review Agent",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "uptime_seconds": time.time() - metrics["start_time"],
        "reviews_completed": metrics["reviews_completed"],
        "reviews_failed": metrics["reviews_failed"]
    }


@app.get("/metrics")
async def get_metrics():
    """Get application metrics."""
    uptime = time.time() - metrics["start_time"]
    agent_stats = review_agent.get_stats()

    return {
        "webhooks_received": metrics["webhooks_received"],
        "reviews_completed": metrics["reviews_completed"],
        "reviews_failed": metrics["reviews_failed"],
        "total_cost_usd": round(metrics["total_cost"], 4),
        "average_cost_usd": agent_stats["average_cost"],
        "uptime_seconds": round(uptime, 1),
        "uptime_hours": round(uptime / 3600, 2)
    }


@app.post("/webhooks/github")
async def github_webhook(
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    GitHub webhook endpoint.

    Receives pull request events and triggers code reviews.
    """
    try:
        # Get raw body and signature
        body = await request.body()
        signature = request.headers.get("X-Hub-Signature-256", "")

        # Verify signature
        if not verify_github_signature(body, signature):
            raise HTTPException(status_code=401, detail="Invalid signature")

        # Parse payload
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON payload")

        # Update metrics
        metrics["webhooks_received"] += 1

        # Get event type
        event_type = request.headers.get("X-GitHub-Event", "")

        logger.info(f"Received webhook: {event_type}")

        # Only process pull request events
        if event_type != "pull_request":
            return {"status": "ignored", "reason": f"Event type '{event_type}' not supported"}

        # Extract PR info
        action = payload.get("action", "")
        pr_data = payload.get("pull_request", {})
        repo_data = payload.get("repository", {})

        pr_number = pr_data.get("number")
        repo_full_name = repo_data.get("full_name", "")
        owner, repo = repo_full_name.split('/') if '/' in repo_full_name else ("", "")

        if not all([pr_number, owner, repo]):
            raise HTTPException(status_code=400, detail="Missing required PR information")

        # Only review on opened or synchronize (new commits)
        if action not in ["opened", "synchronize"]:
            return {
                "status": "ignored",
                "reason": f"Action '{action}' does not trigger review"
            }

        # Check rate limit
        if not check_rate_limit(repo_full_name):
            return {
                "status": "rate_limited",
                "message": f"Rate limit exceeded for {repo_full_name}"
            }

        # Queue review in background
        background_tasks.add_task(
            process_pull_request_review,
            owner=owner,
            repo=repo,
            pr_number=pr_number,
            action=action
        )

        logger.info(f"Queued review for {owner}/{repo}#{pr_number}")

        return {
            "status": "queued",
            "pr_number": pr_number,
            "repository": repo_full_name,
            "action": action
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook processing error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/review/trigger")
async def trigger_review_manually(
    owner: str,
    repo: str,
    pr_number: int,
    background_tasks: BackgroundTasks
):
    """
    Manually trigger a code review.

    Useful for testing or re-reviewing PRs.

    Args:
        owner: Repository owner
        repo: Repository name
        pr_number: Pull request number
    """
    try:
        repo_full_name = f"{owner}/{repo}"

        # Check rate limit
        if not check_rate_limit(repo_full_name):
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded for {repo_full_name}"
            )

        # Queue review
        background_tasks.add_task(
            process_pull_request_review,
            owner=owner,
            repo=repo,
            pr_number=pr_number,
            action="manual"
        )

        logger.info(f"Manually triggered review for {owner}/{repo}#{pr_number}")

        return {
            "status": "queued",
            "pr_number": pr_number,
            "repository": repo_full_name
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Manual trigger error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.debug else "An error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting Code Review Agent on {settings.host}:{settings.port}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Auto-comment: {settings.auto_comment}")

    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower()
    )
