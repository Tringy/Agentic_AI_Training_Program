"""LLM client abstraction for Code Analyzer."""
import os
from abc import ABC, abstractmethod
from typing import List, Dict


class LLMClient(ABC):
    """Abstract base class for LLM clients."""

    @abstractmethod
    def chat(self, messages: List[Dict[str, str]]) -> str:
        """Send messages and return response content."""
        pass


class AnthropicClient(LLMClient):
    """Anthropic Claude client."""

    def __init__(self, model: str = "claude-3-5-sonnet-20241022"):
        from anthropic import Anthropic
        self.client = Anthropic()
        self.model = model

    def chat(self, messages: List[Dict[str, str]]) -> str:
        system = None
        filtered = []
        for m in messages:
            if m["role"] == "system":
                system = m["content"]
            else:
                filtered.append(m)

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system,
            messages=filtered
        )
        return response.content[0].text


class OpenAIClient(LLMClient):
    """OpenAI client."""

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


class GoogleClient(LLMClient):
    """Google Generative AI client (Gemini)."""

    def __init__(self, model: str = "gemini-1.5-flash"):
        import google.generativeai as genai
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)

    def chat(self, messages: List[Dict[str, str]]) -> str:
        # Extract system and build prompt
        system = ""
        history = []
        user_message = ""

        for m in messages:
            if m["role"] == "system":
                system = m["content"]
            elif m["role"] == "user":
                user_message = m["content"]
            elif m["role"] == "assistant":
                history.append({"role": "model", "parts": [m["content"]]})

        prompt = f"{system}\n\n{user_message}" if system else user_message
        response = self.model.generate_content(prompt)
        return response.text


def get_llm_client(provider: str = "anthropic") -> LLMClient:
    """Factory function to create LLM client."""
    providers = {
        "anthropic": AnthropicClient,
        "openai": OpenAIClient,
        "google": GoogleClient,
    }

    if provider not in providers:
        raise ValueError(f"Unknown provider: {provider}. Available: {list(providers.keys())}")

    return providers[provider]()
