"""
Shared Utilities for AI Training Program
=========================================

Consolidated utilities eliminating code duplication across labs, templates, and exercises.

Quick Start:
    from shared_utils import UnifiedLLMClient, extract_json

    # Create LLM client (auto-selects free provider)
    client = UnifiedLLMClient()

    # Chat
    response = client.chat([{"role": "user", "content": "Hello!"}])

    # Parse JSON from response
    data = extract_json(response)

Modules:
    - llm_client: Unified LLM client supporting 5 providers
    - parsing: JSON and code extraction utilities
    - (more modules to be added: caching, retry, rate_limit, etc.)

Examples:
    >>> from shared_utils import get_llm_client, extract_code_block
    >>>
    >>> # Use specific provider
    >>> client = get_llm_client("google")
    >>> response = client.chat([{"role": "user", "content": "Write hello world in Python"}])
    >>> code = extract_code_block(response, language="python")
    >>> print(code)
    print("Hello, world!")
"""

# LLM Client exports
from .llm_client import (
    LLMClient,
    UnifiedLLMClient,
    get_llm_client,
    get_free_llm_client,
    auto_select_client,
    GoogleAIClient,
    GroqClient,
    OllamaClient,
    AnthropicClient,
    OpenAIClient,
)

# Parsing utilities
from .parsing import (
    extract_json,
    extract_json_array,
    extract_code_block,
    extract_all_code_blocks,
    clean_response,
    validate_json_schema,
)

__version__ = "1.0.0"

# Define public API
__all__ = [
    # LLM Clients
    "LLMClient",
    "UnifiedLLMClient",
    "get_llm_client",
    "get_free_llm_client",
    "auto_select_client",
    "GoogleAIClient",
    "GroqClient",
    "OllamaClient",
    "AnthropicClient",
    "OpenAIClient",
    # Parsing
    "extract_json",
    "extract_json_array",
    "extract_code_block",
    "extract_all_code_blocks",
    "clean_response",
    "validate_json_schema",
]
