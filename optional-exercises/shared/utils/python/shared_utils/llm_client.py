"""
Unified LLM Client for AI Training Program
===========================================

Consolidated LLM client supporting all major providers with a unified interface.

This module consolidates 9+ duplicated LLM client implementations across labs and templates
into a single, reusable, well-tested utility.

Supported Providers:
    FREE:
        - Google AI Studio (Gemini) - Most generous free tier, 60 RPM
        - Groq - Fastest inference, unlimited free tier
        - Ollama - Completely local/offline, no API key needed

    PAID:
        - Anthropic (Claude) - Best for long context and reasoning
        - OpenAI (GPT) - Broad capabilities and function calling

Usage:
    from shared_utils.llm_client import get_llm_client

    # Use free provider (recommended for learning)
    client = get_llm_client("google")

    # Or paid provider
    client = get_llm_client("anthropic")

    # Send messages
    response = client.chat([
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ])

    print(response)  # "Hello! How can I help you today?"
"""

import os
from abc import ABC, abstractmethod
from typing import List, Dict, Optional


class LLMClient(ABC):
    """Abstract base class for all LLM clients."""

    @abstractmethod
    def chat(self, messages: List[Dict[str, str]]) -> str:
        """Send messages and get response content.

        Args:
            messages: List of message dicts with 'role' and 'content'
                     Roles: 'system', 'user', 'assistant'

        Returns:
            Response text from LLM
        """
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Get the current model name."""
        pass


# ==============================================================================
# FREE PROVIDERS
# ==============================================================================

class GoogleAIClient(LLMClient):
    """
    Google AI Studio client - BEST FREE OPTION.

    Free tier: 15 RPM, 1M TPM for Gemini 1.5 Flash
    Signup: https://aistudio.google.com/

    Get API key:
        1. Go to https://aistudio.google.com/app/apikey
        2. Create API key
        3. Set GOOGLE_API_KEY environment variable
    """

    def __init__(self, model: str = "gemini-1.5-flash"):
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError(
                "Install google-generativeai: pip install google-generativeai"
            )

        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError(
                "GOOGLE_API_KEY environment variable not set. "
                "Get one at https://aistudio.google.com/app/apikey"
            )

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

    Free tier: 30 RPM for Llama 3.1 70B, unlimited usage
    Signup: https://console.groq.com/

    Get API key:
        1. Go to https://console.groq.com/
        2. Sign up (free)
        3. Create API key
        4. Set GROQ_API_KEY environment variable
    """

    def __init__(self, model: str = "llama-3.1-70b-versatile"):
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("Install openai: pip install openai")

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY environment variable not set. "
                "Get one at https://console.groq.com/"
            )

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
    Ollama client - COMPLETELY FREE AND LOCAL.

    No API key needed, runs entirely on your machine.
    Perfect for privacy, offline work, and zero cost.

    Setup:
        1. Install from https://ollama.ai/
        2. Pull a model: ollama pull llama3.1:8b
        3. Model runs automatically when called

    Available models:
        - llama3.1:8b (fast, 8GB RAM)
        - llama3.1:70b (best quality, 40GB RAM)
        - mistral (balanced)
        - codellama (code-focused)
    """

    def __init__(self, model: str = "llama3.1:8b", base_url: str = "http://localhost:11434/v1"):
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("Install openai: pip install openai")

        self.client = OpenAI(
            api_key="ollama",  # Required by API but not used
            base_url=base_url
        )
        self._model_name = model

    @property
    def model_name(self) -> str:
        return self._model_name

    def chat(self, messages: List[Dict]) -> str:
        """Send messages to local Ollama server."""
        try:
            response = self.client.chat.completions.create(
                model=self._model_name,
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            raise ConnectionError(
                f"Could not connect to Ollama at {self.client.base_url}. "
                f"Make sure Ollama is running and model '{self._model_name}' is pulled. "
                f"Error: {e}"
            )


# ==============================================================================
# PAID PROVIDERS
# ==============================================================================

class AnthropicClient(LLMClient):
    """
    Anthropic Claude client (PAID).

    Best for: Long context (200K tokens), complex reasoning, safety
    Cost: $3-15 per million tokens depending on model

    Get API key:
        1. Go to https://console.anthropic.com/
        2. Create account
        3. Add credits
        4. Create API key
        5. Set ANTHROPIC_API_KEY environment variable
    """

    def __init__(self, model: str = "claude-3-5-sonnet-20241022"):
        try:
            from anthropic import Anthropic
        except ImportError:
            raise ImportError("Install anthropic: pip install anthropic")

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable not set. "
                "Get one at https://console.anthropic.com/"
            )

        self.client = Anthropic(api_key=api_key)
        self._model_name = model

    @property
    def model_name(self) -> str:
        return self._model_name

    def chat(self, messages: List[Dict]) -> str:
        """Send messages to Claude API.

        Note: Anthropic requires system prompts separate from messages.
        """
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
    """
    OpenAI client (PAID).

    Best for: Function calling, broad capabilities, multimodal
    Cost: $2.50-30 per million tokens depending on model

    Get API key:
        1. Go to https://platform.openai.com/
        2. Create account
        3. Add credits
        4. Create API key
        5. Set OPENAI_API_KEY environment variable
    """

    def __init__(self, model: str = "gpt-4o"):
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("Install openai: pip install openai")

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable not set. "
                "Get one at https://platform.openai.com/"
            )

        self.client = OpenAI(api_key=api_key)
        self._model_name = model

    @property
    def model_name(self) -> str:
        return self._model_name

    def chat(self, messages: List[Dict]) -> str:
        """Send messages to OpenAI API."""
        response = self.client.chat.completions.create(
            model=self._model_name,
            messages=messages
        )
        return response.choices[0].message.content


# ==============================================================================
# FACTORY FUNCTIONS
# ==============================================================================

def get_llm_client(provider: str = "google", model: Optional[str] = None) -> LLMClient:
    """
    Get an LLM client for the specified provider.

    This is the main entry point for creating LLM clients. It automatically
    detects available API keys and creates the appropriate client.

    FREE PROVIDERS (recommended for learning):
        - "google": Google AI Studio (Gemini) - Most generous free tier, 60 RPM
        - "groq": Groq - Fastest inference (300+ tok/sec), unlimited free
        - "ollama": Ollama - Completely local/offline, no cost ever

    PAID PROVIDERS:
        - "anthropic": Anthropic Claude - Best reasoning and long context
        - "openai": OpenAI GPT - Broad capabilities and function calling

    Args:
        provider: Provider name (default: "google" for free tier)
        model: Optional model override (uses provider default if None)

    Returns:
        LLMClient instance ready to use

    Raises:
        ValueError: If provider is unknown or API key is missing
        ImportError: If required SDK is not installed

    Examples:
        >>> # Use free Google AI
        >>> client = get_llm_client("google")
        >>> response = client.chat([{"role": "user", "content": "Hi!"}])

        >>> # Use specific model
        >>> client = get_llm_client("anthropic", model="claude-3-opus-20240229")

        >>> # Auto-detect from environment
        >>> client = get_llm_client()  # Defaults to Google
    """
    providers = {
        # FREE (recommended)
        "google": (GoogleAIClient, "gemini-1.5-flash"),
        "groq": (GroqClient, "llama-3.1-70b-versatile"),
        "ollama": (OllamaClient, "llama3.1:8b"),

        # PAID
        "anthropic": (AnthropicClient, "claude-3-5-sonnet-20241022"),
        "openai": (OpenAIClient, "gpt-4o"),
    }

    if provider not in providers:
        available = ", ".join(providers.keys())
        raise ValueError(
            f"Unknown provider: {provider}. "
            f"Available providers: {available}"
        )

    client_class, default_model = providers[provider]
    return client_class(model=model or default_model)


def get_free_llm_client(provider: str = "google") -> LLMClient:
    """
    Get a FREE LLM client.

    Convenience wrapper that only allows free providers to prevent accidental costs.

    Args:
        provider: One of "google", "groq", "ollama" (default: "google")

    Returns:
        LLMClient instance for free provider

    Raises:
        ValueError: If provider is not free

    Examples:
        >>> # Recommended: Google AI (most generous free tier)
        >>> client = get_free_llm_client("google")

        >>> # Fastest: Groq
        >>> client = get_free_llm_client("groq")

        >>> # Local: Ollama (completely offline)
        >>> client = get_free_llm_client("ollama")
    """
    free_providers = ["google", "groq", "ollama"]

    if provider not in free_providers:
        raise ValueError(
            f"Provider '{provider}' is not free. "
            f"Use one of: {', '.join(free_providers)}"
        )

    return get_llm_client(provider)


def auto_select_client(prefer_free: bool = True) -> LLMClient:
    """
    Automatically select best available client based on environment.

    Checks for API keys in this order:
        FREE (if prefer_free=True):
            1. GOOGLE_API_KEY
            2. GROQ_API_KEY
            3. Ollama (always available if running)

        PAID (if no free keys or prefer_free=False):
            1. ANTHROPIC_API_KEY
            2. OPENAI_API_KEY

    Args:
        prefer_free: Try free providers first (default: True)

    Returns:
        LLMClient instance for first available provider

    Raises:
        RuntimeError: If no providers are available

    Examples:
        >>> # Auto-select (prefers free)
        >>> client = auto_select_client()
        >>> print(f"Using: {client.model_name}")

        >>> # Prefer paid providers
        >>> client = auto_select_client(prefer_free=False)
    """
    if prefer_free:
        # Try free providers first
        if os.getenv("GOOGLE_API_KEY"):
            return get_llm_client("google")
        if os.getenv("GROQ_API_KEY"):
            return get_llm_client("groq")

        # Try Ollama (doesn't need key)
        try:
            return get_llm_client("ollama")
        except:
            pass

    # Try paid providers
    if os.getenv("ANTHROPIC_API_KEY"):
        return get_llm_client("anthropic")
    if os.getenv("OPENAI_API_KEY"):
        return get_llm_client("openai")

    # If prefer_free=False and no paid keys, try free
    if not prefer_free:
        if os.getenv("GOOGLE_API_KEY"):
            return get_llm_client("google")
        if os.getenv("GROQ_API_KEY"):
            return get_llm_client("groq")

    raise RuntimeError(
        "No LLM provider available. Set one of these environment variables:\n"
        "  - GOOGLE_API_KEY (free, recommended)\n"
        "  - GROQ_API_KEY (free, fast)\n"
        "  - ANTHROPIC_API_KEY (paid)\n"
        "  - OPENAI_API_KEY (paid)\n"
        "Or install and run Ollama for local inference."
    )


# ==============================================================================
# CONVENIENCE WRAPPER
# ==============================================================================

class UnifiedLLMClient:
    """
    Unified LLM client with simplified interface.

    This is a convenience wrapper that auto-selects the best available provider
    and provides helper methods for common tasks.

    Usage:
        from shared_utils.llm_client import UnifiedLLMClient

        # Auto-select provider (prefers free)
        client = UnifiedLLMClient()

        # Simple chat
        response = client.chat([{"role": "user", "content": "Hi!"}])

        # With system prompt
        response = client.chat([
            {"role": "system", "content": "You are an expert."},
            {"role": "user", "content": "Explain LLMs"}
        ])
    """

    def __init__(self, provider: Optional[str] = None, model: Optional[str] = None):
        """Initialize unified client.

        Args:
            provider: Optional provider name (auto-select if None)
            model: Optional model override

        Examples:
            >>> # Auto-select
            >>> client = UnifiedLLMClient()

            >>> # Specific provider
            >>> client = UnifiedLLMClient(provider="google")

            >>> # Specific model
            >>> client = UnifiedLLMClient(provider="anthropic", model="claude-3-opus-20240229")
        """
        if provider:
            self.client = get_llm_client(provider, model)
        else:
            self.client = auto_select_client()

    def chat(self, messages: List[Dict[str, str]]) -> str:
        """Send messages and get response.

        Args:
            messages: List of message dicts

        Returns:
            Response text
        """
        return self.client.chat(messages)

    @property
    def model_name(self) -> str:
        """Get current model name."""
        return self.client.model_name


# ==============================================================================
# QUICK TEST
# ==============================================================================

if __name__ == "__main__":
    import sys

    print("Testing Unified LLM Client")
    print("=" * 60)
    print("")

    # Test auto-select
    print("1. Testing auto-select...")
    try:
        client = UnifiedLLMClient()
        print(f"   Selected: {client.model_name}")

        response = client.chat([
            {"role": "user", "content": "Say 'Hello from AI Training!' in exactly those words."}
        ])
        print(f"   Response: {response[:100]}")
        print("   ✅ Auto-select working!")
    except Exception as e:
        print(f"   ❌ Auto-select failed: {e}")

    print("")

    # Test each provider if API key available
    test_providers = []

    if os.getenv("GOOGLE_API_KEY"):
        test_providers.append("google")
    if os.getenv("GROQ_API_KEY"):
        test_providers.append("groq")
    if os.getenv("ANTHROPIC_API_KEY"):
        test_providers.append("anthropic")
    if os.getenv("OPENAI_API_KEY"):
        test_providers.append("openai")

    # Always try Ollama
    test_providers.append("ollama")

    for i, provider in enumerate(test_providers, 2):
        print(f"{i}. Testing {provider}...")
        try:
            client = get_llm_client(provider)
            response = client.chat([
                {"role": "user", "content": f"Say 'Working!' in one word."}
            ])
            print(f"   Model: {client.model_name}")
            print(f"   Response: {response[:50]}")
            print(f"   ✅ {provider} working!")
        except Exception as e:
            print(f"   ❌ {provider} not available: {e}")

        print("")

    print("=" * 60)
    print("Test complete!")
    print("")
    print("Recommendations:")
    print("  - Use Google AI for learning (free, generous limits)")
    print("  - Use Groq for speed (300+ tokens/second)")
    print("  - Use Ollama for privacy (100% local)")
    print("  - Use Claude for production (best quality)")
