"""LLM Client abstraction."""
import os
from typing import List, Dict, Optional
from abc import ABC, abstractmethod


class LLMClient(ABC):
    """Abstract base class for LLM clients."""

    @abstractmethod
    def chat(self, messages: List[Dict[str, str]]) -> str:
        """Send messages and get a response."""
        pass


class AnthropicClient(LLMClient):
    """Anthropic Claude client."""

    def __init__(self, model: str = "claude-3-5-sonnet-20241022"):
        from anthropic import Anthropic
        self.client = Anthropic()
        self.model = model

    def chat(self, messages: List[Dict[str, str]]) -> str:
        # Extract system message
        system = None
        filtered = []
        for msg in messages:
            if msg["role"] == "system":
                system = msg["content"]
            else:
                filtered.append(msg)

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system,
            messages=filtered
        )

        return response.content[0].text


class OpenAIClient(LLMClient):
    """OpenAI GPT client."""

    def __init__(self, model: str = "gpt-4o"):
        from openai import OpenAI
        self.client = OpenAI()
        self.model = model

    def chat(self, messages: List[Dict[str, str]]) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages
        )
        return response.choices[0].message.content


def get_llm_client(provider: str = "anthropic") -> LLMClient:
    """Get an LLM client by provider name."""
    if provider == "anthropic":
        return AnthropicClient()
    elif provider == "openai":
        return OpenAIClient()
    else:
        raise ValueError(f"Unknown provider: {provider}")
