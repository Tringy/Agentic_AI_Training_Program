# Exercise 09: Multi-Provider API Wrapper

## Description
Create a unified abstraction over multiple LLM APIs (OpenAI, Anthropic, Google) with a consistent interface.

## Objectives
- Unified API for all providers
- Automatic failover between providers
- Load balancing
- Rate limiting per provider
- Unified streaming

## Core Interface

```python
from abc import ABC, abstractmethod

class LLMProvider(ABC):
    @abstractmethod
    async def complete(
        self,
        messages: List[Message],
        **kwargs
    ) -> Response:
        pass

    @abstractmethod
    async def stream(self, messages: List[Message]) -> AsyncIterator[str]:
        pass

class UnifiedLLMClient:
    def __init__(self, providers: List[LLMProvider]):
        self.providers = providers
        self.current_provider = 0

    async def complete(self, messages: List[Message], **kwargs):
        for attempt in range(len(self.providers)):
            provider = self.providers[self.current_provider]
            try:
                response = await provider.complete(messages, **kwargs)
                return response
            except Exception as e:
                print(f"Provider {provider.name} failed: {e}")
                self.current_provider = (self.current_provider + 1) % len(self.providers)

        raise Exception("All providers failed")
```

## Provider Implementations

```python
class AnthropicProvider(LLMProvider):
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)

    async def complete(self, messages, **kwargs):
        response = self.client.messages.create(
            model=kwargs.get('model', 'claude-sonnet-4'),
            messages=messages,
            max_tokens=kwargs.get('max_tokens', 1024)
        )
        return self.normalize_response(response)

class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)

    async def complete(self, messages, **kwargs):
        response = self.client.chat.completions.create(
            model=kwargs.get('model', 'gpt-4'),
            messages=messages,
        )
        return self.normalize_response(response)
```

## Features
- [ ] Unified message format
- [ ] Response normalization
- [ ] Automatic retry with exponential backoff
- [ ] Cost tracking per provider
- [ ] Smart routing based on task type

## Advanced Features

```python
class SmartRouter:
    """Route requests to best provider based on criteria"""

    def select_provider(self, messages: List[Message], criteria: str):
        if criteria == "cost":
            return self.cheapest_provider()
        elif criteria == "quality":
            return self.best_quality_provider()
        elif criteria == "speed":
            return self.fastest_provider()

class RateLimiter:
    """Per-provider rate limiting"""

    async def acquire(self, provider: str):
        # Implement token bucket algorithm
        pass
```

## Testing

```python
async def test_failover():
    # Mock provider that always fails
    failing = MockProvider(always_fail=True)
    working = MockProvider(always_fail=False)

    client = UnifiedLLMClient([failing, working])
    response = await client.complete([{"role": "user", "content": "test"}])

    assert response.provider == "working"

async def test_streaming():
    client = UnifiedLLMClient([AnthropicProvider(key)])

    chunks = []
    async for chunk in client.stream(messages):
        chunks.append(chunk)

    assert len(chunks) > 0
```

## Challenges
1. Cache layer with semantic deduplication
2. Request batching
3. A/B testing between providers
4. Cost optimization router

**Time**: 5-6h
