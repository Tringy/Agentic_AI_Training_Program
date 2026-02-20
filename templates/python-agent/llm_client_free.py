"""
Free-Tier LLM Client
====================

LLM client supporting 100% free providers:
- Google AI Studio (Gemini) - Most generous free tier
- Groq - Fastest inference
- Ollama - Completely local/offline

Usage:
    from llm_client_free import get_llm_client

    # Using Google AI Studio (recommended)
    client = get_llm_client("google")

    # Using Groq (fast)
    client = get_llm_client("groq")

    # Using Ollama (local)
    client = get_llm_client("ollama")

    response = client.chat([
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ])
"""

import os
from abc import ABC, abstractmethod
from typing import List, Dict, Optional


class LLMClient(ABC):
    """Abstract base class for LLM clients."""

    @abstractmethod
    def chat(self, messages: List[Dict]) -> str:
        """Send messages and get response."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Get the model name."""
        pass


class GoogleAIClient(LLMClient):
    """
    Google AI Studio client - BEST FREE OPTION.

    Free tier: 15 RPM, 1M TPM for Gemini 1.5 Flash
    Signup: https://aistudio.google.com/
    """

    def __init__(self, model: str = "gemini-1.5-flash"):
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError("Install google-generativeai: pip install google-generativeai")

        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
        self._model_name = model

    @property
    def model_name(self) -> str:
        return self._model_name

    def chat(self, messages: List[Dict]) -> str:
        """Convert messages to Gemini format and get response."""
        # Gemini uses a different message format
        # Combine system message with first user message
        system_content = ""
        chat_messages = []

        for msg in messages:
            if msg["role"] == "system":
                system_content = msg["content"] + "\n\n"
            elif msg["role"] == "user":
                content = system_content + msg["content"] if system_content else msg["content"]
                chat_messages.append({"role": "user", "parts": [content]})
                system_content = ""  # Only prepend to first user message
            elif msg["role"] == "assistant":
                chat_messages.append({"role": "model", "parts": [msg["content"]]})

        # Use generate_content for simple cases
        if len(chat_messages) == 1:
            response = self.model.generate_content(chat_messages[0]["parts"][0])
        else:
            # Use chat for multi-turn conversations
            chat = self.model.start_chat(history=chat_messages[:-1])
            response = chat.send_message(chat_messages[-1]["parts"][0])

        return response.text


class GroqClient(LLMClient):
    """
    Groq client - FASTEST FREE INFERENCE.

    Free tier: 30 RPM for Llama 3.1 70B
    Signup: https://console.groq.com/
    """

    def __init__(self, model: str = "llama-3.1-70b-versatile"):
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("Install openai: pip install openai")

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1"
        )
        self._model_name = model

    @property
    def model_name(self) -> str:
        return self._model_name

    def chat(self, messages: List[Dict]) -> str:
        """Send messages using OpenAI-compatible API."""
        response = self.client.chat.completions.create(
            model=self._model_name,
            messages=messages,
            max_tokens=4096
        )
        return response.choices[0].message.content


class OllamaClient(LLMClient):
    """
    Ollama client - COMPLETELY FREE/LOCAL.

    No API key needed, runs on your machine.
    Install: https://ollama.ai/
    Then: ollama pull llama3.1:8b
    """

    def __init__(self, model: str = "llama3.1:8b", base_url: str = "http://localhost:11434/v1"):
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("Install openai: pip install openai")

        self.client = OpenAI(
            api_key="ollama",  # Required but not used
            base_url=base_url
        )
        self._model_name = model

    @property
    def model_name(self) -> str:
        return self._model_name

    def chat(self, messages: List[Dict]) -> str:
        """Send messages to local Ollama server."""
        response = self.client.chat.completions.create(
            model=self._model_name,
            messages=messages
        )
        return response.choices[0].message.content


# Also include paid clients for flexibility
class AnthropicClient(LLMClient):
    """Anthropic Claude client (PAID)."""

    def __init__(self, model: str = "claude-3-5-sonnet-20241022"):
        try:
            from anthropic import Anthropic
        except ImportError:
            raise ImportError("Install anthropic: pip install anthropic")

        self.client = Anthropic()
        self._model_name = model

    @property
    def model_name(self) -> str:
        return self._model_name

    def chat(self, messages: List[Dict]) -> str:
        system = None
        filtered = []
        for m in messages:
            if m["role"] == "system":
                system = m["content"]
            else:
                filtered.append(m)

        response = self.client.messages.create(
            model=self._model_name,
            max_tokens=4096,
            system=system,
            messages=filtered
        )
        return response.content[0].text


class OpenAIClient(LLMClient):
    """OpenAI client (PAID)."""

    def __init__(self, model: str = "gpt-4o"):
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("Install openai: pip install openai")

        self.client = OpenAI()
        self._model_name = model

    @property
    def model_name(self) -> str:
        return self._model_name

    def chat(self, messages: List[Dict]) -> str:
        response = self.client.chat.completions.create(
            model=self._model_name,
            messages=messages
        )
        return response.choices[0].message.content


def get_llm_client(provider: str = "google", model: Optional[str] = None) -> LLMClient:
    """
    Get an LLM client for the specified provider.

    FREE PROVIDERS (recommended):
        - "google": Google AI Studio (Gemini) - Most generous free tier
        - "groq": Groq - Fastest inference
        - "ollama": Ollama - Completely local/offline

    PAID PROVIDERS:
        - "anthropic": Anthropic Claude
        - "openai": OpenAI GPT

    Args:
        provider: Provider name
        model: Optional model override

    Returns:
        LLMClient instance
    """
    providers = {
        # FREE
        "google": (GoogleAIClient, "gemini-1.5-flash"),
        "groq": (GroqClient, "llama-3.1-70b-versatile"),
        "ollama": (OllamaClient, "llama3.1:8b"),
        # PAID
        "anthropic": (AnthropicClient, "claude-3-5-sonnet-20241022"),
        "openai": (OpenAIClient, "gpt-4o"),
    }

    if provider not in providers:
        available = ", ".join(providers.keys())
        raise ValueError(f"Unknown provider: {provider}. Available: {available}")

    client_class, default_model = providers[provider]
    return client_class(model=model or default_model)


def get_free_llm_client(provider: str = "google") -> LLMClient:
    """
    Get a FREE LLM client. Convenience wrapper that only allows free providers.

    Args:
        provider: One of "google", "groq", "ollama"

    Returns:
        LLMClient instance
    """
    free_providers = ["google", "groq", "ollama"]
    if provider not in free_providers:
        raise ValueError(f"Provider '{provider}' is not free. Use one of: {free_providers}")
    return get_llm_client(provider)


# ============================================================================
# Quick Test
# ============================================================================

if __name__ == "__main__":
    import sys

    print("Testing FREE LLM clients...")
    print("=" * 50)

    # Test based on what's configured
    test_providers = []

    if os.getenv("GOOGLE_API_KEY"):
        test_providers.append("google")
    if os.getenv("GROQ_API_KEY"):
        test_providers.append("groq")

    # Ollama doesn't need API key, try it
    test_providers.append("ollama")

    if not test_providers:
        print("No API keys found! Set one of:")
        print("  - GOOGLE_API_KEY (recommended)")
        print("  - GROQ_API_KEY")
        print("Or install Ollama for local testing")
        sys.exit(1)

    for provider in test_providers:
        print(f"\nTesting {provider}...")
        try:
            client = get_free_llm_client(provider)
            response = client.chat([
                {"role": "user", "content": "Say 'Hello from " + provider + "!' in exactly those words."}
            ])
            print(f"  Model: {client.model_name}")
            print(f"  Response: {response[:100]}...")
            print(f"  ✅ {provider} working!")
        except Exception as e:
            print(f"  ❌ {provider} failed: {e}")

    print("\n" + "=" * 50)
    print("Done!")
