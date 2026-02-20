"""
API Routes

Example endpoints demonstrating:
- Request/response validation with Pydantic
- LLM service integration
- Error handling
- Async operations
"""
import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.services.llm_service import LLMService
from app.models.schemas import ChatRequest, ChatResponse, Message

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Initialize LLM service (singleton)
llm_service = LLMService()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Chat with AI using Claude.

    Args:
        request: Chat request with message and optional parameters

    Returns:
        ChatResponse: AI-generated response with metadata

    Raises:
        HTTPException: If LLM service fails
    """
    try:
        logger.info(f"Processing chat request: {request.message[:50]}...")

        # Call LLM service
        response = await llm_service.chat(
            message=request.message,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )

        return ChatResponse(
            message=response["content"],
            model=response["model"],
            tokens_used=response["tokens"],
            finish_reason=response.get("stop_reason", "end_turn")
        )

    except Exception as e:
        logger.error(f"Chat error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat request: {str(e)}"
        )


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Stream chat responses (placeholder for streaming implementation).

    Note: Implement with FastAPI's StreamingResponse for production use.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Streaming not yet implemented"
    )


@router.get("/models")
async def list_models():
    """
    List available AI models.

    Returns:
        dict: Available models and their capabilities
    """
    return {
        "models": [
            {
                "id": "claude-3-5-sonnet-20241022",
                "name": "Claude 3.5 Sonnet",
                "description": "Most intelligent model for complex tasks",
                "context_window": 200000
            },
            {
                "id": "claude-3-5-haiku-20241022",
                "name": "Claude 3.5 Haiku",
                "description": "Fastest model for quick responses",
                "context_window": 200000
            }
        ]
    }


@router.get("/status")
async def get_status():
    """
    Get API status and configuration.

    Returns:
        dict: Current API status
    """
    return {
        "status": "operational",
        "llm_service": "anthropic",
        "endpoints": {
            "chat": "/api/chat",
            "models": "/api/models",
            "status": "/api/status"
        }
    }
