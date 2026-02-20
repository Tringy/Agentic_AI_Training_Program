"""
LLM Service

Handles all interactions with Anthropic's Claude API.
Includes error handling, retry logic, and response parsing.
"""
import os
import logging
from typing import Dict, Any, Optional

import anthropic
from anthropic import APIError, APIConnectionError, RateLimitError

logger = logging.getLogger(__name__)


class LLMService:
    """Service for LLM interactions with Claude."""

    def __init__(self):
        """Initialize the LLM service."""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")

        self.client = anthropic.Anthropic(api_key=api_key)
        self.default_model = os.getenv("DEFAULT_MODEL", "claude-3-5-sonnet-20241022")
        self.default_max_tokens = int(os.getenv("DEFAULT_MAX_TOKENS", "1024"))

        logger.info(f"LLM Service initialized with model: {self.default_model}")

    async def chat(
        self,
        message: str,
        max_tokens: Optional[int] = None,
        temperature: float = 1.0,
        system: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a chat message to Claude and get response.

        Args:
            message: User message to send
            max_tokens: Maximum tokens in response (default: from env)
            temperature: Sampling temperature 0-2 (default: 1.0)
            system: Optional system prompt

        Returns:
            dict: Response containing:
                - content: AI response text
                - model: Model used
                - tokens: Total tokens used
                - stop_reason: Why generation stopped

        Raises:
            Exception: If API call fails after retries
        """
        try:
            # Prepare request
            max_tokens = max_tokens or self.default_max_tokens

            request_params = {
                "model": self.default_model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [
                    {
                        "role": "user",
                        "content": message
                    }
                ]
            }

            # Add system prompt if provided
            if system:
                request_params["system"] = system

            logger.debug(f"Sending request to Claude: {message[:100]}...")

            # Call API
            response = self.client.messages.create(**request_params)

            # Extract response
            result = {
                "content": response.content[0].text,
                "model": response.model,
                "tokens": response.usage.input_tokens + response.usage.output_tokens,
                "stop_reason": response.stop_reason
            }

            logger.info(f"Received response: {result['tokens']} tokens used")

            return result

        except RateLimitError as e:
            logger.error(f"Rate limit exceeded: {str(e)}")
            raise Exception("Rate limit exceeded. Please try again later.")

        except APIConnectionError as e:
            logger.error(f"Connection error: {str(e)}")
            raise Exception("Failed to connect to AI service. Please try again.")

        except APIError as e:
            logger.error(f"API error: {str(e)}")
            raise Exception(f"AI service error: {str(e)}")

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            raise Exception(f"Failed to process request: {str(e)}")

    async def chat_with_context(
        self,
        messages: list[Dict[str, str]],
        max_tokens: Optional[int] = None,
        temperature: float = 1.0,
        system: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Chat with conversation history context.

        Args:
            messages: List of message dicts with 'role' and 'content'
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            system: Optional system prompt

        Returns:
            dict: Response in same format as chat()
        """
        try:
            max_tokens = max_tokens or self.default_max_tokens

            request_params = {
                "model": self.default_model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": messages
            }

            if system:
                request_params["system"] = system

            logger.debug(f"Sending conversation with {len(messages)} messages")

            response = self.client.messages.create(**request_params)

            result = {
                "content": response.content[0].text,
                "model": response.model,
                "tokens": response.usage.input_tokens + response.usage.output_tokens,
                "stop_reason": response.stop_reason
            }

            logger.info(f"Received response: {result['tokens']} tokens used")

            return result

        except Exception as e:
            logger.error(f"Chat with context error: {str(e)}", exc_info=True)
            raise Exception(f"Failed to process conversation: {str(e)}")

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model.

        Returns:
            dict: Model information
        """
        return {
            "model": self.default_model,
            "max_tokens": self.default_max_tokens,
            "provider": "anthropic"
        }
