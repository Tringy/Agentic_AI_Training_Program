# Exercise 11: Multi-Provider Router with Optimization

## Description
Intelligent router that selects the best LLM provider based on cost, quality, latency, and availability.

## Objectives
- Dynamic routing based on multiple criteria
- Performance tracking per provider
- Automatic failover
- Cost optimization
- Quality scoring

## Architecture

```typescript
interface RoutingStrategy {
  name: string;
  selectProvider(
    request: LLMRequest,
    providers: Provider[]
  ): Provider;
}

class CostOptimizedRouter implements RoutingStrategy {
  selectProvider(request, providers) {
    // Select cheapest provider that meets quality threshold
    return providers
      .filter(p => p.qualityScore >= 0.8)
      .sort((a, b) => a.cost - b.cost)[0];
  }
}

class LatencyOptimizedRouter implements RoutingStrategy {
  selectProvider(request, providers) {
    // Select fastest provider
    return providers
      .sort((a, b) => a.avgLatency - b.avgLatency)[0];
  }
}

class QualityOptimizedRouter implements RoutingStrategy {
  selectProvider(request, providers) {
    // Select highest quality, regardless of cost
    return providers
      .sort((a, b) => b.qualityScore - a.qualityScore)[0];
  }
}
```

## Core Implementation

```python
from dataclasses import dataclass
from enum import Enum

class RoutingStrategy(Enum):
    COST = "cost"
    QUALITY = "quality"
    LATENCY = "latency"
    BALANCED = "balanced"

@dataclass
class ProviderMetrics:
    provider: str
    avg_latency: float
    quality_score: float
    cost_per_1k_tokens: float
    availability: float  # 0-1
    current_load: float  # 0-1

class IntelligentRouter:
    def __init__(self, strategy: RoutingStrategy = RoutingStrategy.BALANCED):
        self.strategy = strategy
        self.metrics: Dict[str, ProviderMetrics] = {}
        self.providers = self._initialize_providers()

    def route(self, request: LLMRequest) -> Provider:
        # Get current metrics for all providers
        available_providers = [
            p for p in self.providers
            if self.metrics[p.name].availability > 0.95
        ]

        if not available_providers:
            raise NoProvidersAvailable()

        # Select based on strategy
        if self.strategy == RoutingStrategy.COST:
            return self._select_cheapest(available_providers, request)
        elif self.strategy == RoutingStrategy.QUALITY:
            return self._select_highest_quality(available_providers, request)
        elif self.strategy == RoutingStrategy.LATENCY:
            return self._select_fastest(available_providers, request)
        else:
            return self._select_balanced(available_providers, request)

    def _select_balanced(self, providers, request) -> Provider:
        """Balanced scoring: quality * (1 / cost) * (1 / latency)"""
        scores = []

        for provider in providers:
            metrics = self.metrics[provider.name]

            # Normalize metrics to 0-1 scale
            quality_norm = metrics.quality_score
            cost_norm = 1 / (1 + metrics.cost_per_1k_tokens)
            latency_norm = 1 / (1 + metrics.avg_latency)

            # Weighted score
            score = (
                quality_norm * 0.4 +
                cost_norm * 0.3 +
                latency_norm * 0.3
            )

            scores.append((score, provider))

        return max(scores, key=lambda x: x[0])[1]

    async def update_metrics(self, provider: str, response: Response):
        """Update provider metrics based on actual performance"""
        metrics = self.metrics[provider]

        # Update latency (moving average)
        metrics.avg_latency = (
            0.9 * metrics.avg_latency +
            0.1 * response.latency
        )

        # Update quality score
        if response.quality_score:
            metrics.quality_score = (
                0.9 * metrics.quality_score +
                0.1 * response.quality_score
            )

        # Update availability
        if response.error:
            metrics.availability *= 0.95
        else:
            metrics.availability = min(1.0, metrics.availability * 1.01)
```

## Task-Based Routing

```python
class TaskBasedRouter(IntelligentRouter):
    """Route based on task type"""

    TASK_PREFERENCES = {
        "code_generation": ["claude-sonnet", "gpt-4"],
        "summarization": ["gpt-3.5", "claude-haiku"],
        "creative_writing": ["claude-opus", "gpt-4"],
        "translation": ["gpt-4", "gemini-pro"],
        "data_extraction": ["gpt-3.5", "claude-haiku"],
    }

    def route(self, request: LLMRequest) -> Provider:
        task_type = self._detect_task_type(request)
        preferred_models = self.TASK_PREFERENCES.get(
            task_type,
            ["gpt-4"]  # default
        )

        # Filter providers by preferred models
        candidates = [
            p for p in self.providers
            if p.model in preferred_models
        ]

        # Apply standard routing logic
        return super().route_from_candidates(candidates, request)
```

## Circuit Breaker Pattern

```python
from datetime import datetime, timedelta

class CircuitBreaker:
    """Prevent calling failing providers"""

    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures: Dict[str, int] = {}
        self.opened_at: Dict[str, datetime] = {}

    def is_available(self, provider: str) -> bool:
        # Check if circuit is open
        if provider in self.opened_at:
            if datetime.now() - self.opened_at[provider] > timedelta(seconds=self.timeout):
                # Timeout passed, try again (half-open)
                del self.opened_at[provider]
                self.failures[provider] = 0
                return True
            return False

        return True

    def record_failure(self, provider: str):
        self.failures[provider] = self.failures.get(provider, 0) + 1

        if self.failures[provider] >= self.failure_threshold:
            # Open circuit
            self.opened_at[provider] = datetime.now()
            print(f"🔴 Circuit breaker opened for {provider}")

    def record_success(self, provider: str):
        self.failures[provider] = 0
        if provider in self.opened_at:
            del self.opened_at[provider]
```

## Analytics & Monitoring

```python
class RouterAnalytics:
    def __init__(self):
        self.requests_by_provider = {}
        self.total_cost = {}
        self.latencies = {}

    def track_request(self, provider: str, cost: float, latency: float):
        self.requests_by_provider[provider] = \
            self.requests_by_provider.get(provider, 0) + 1

        self.total_cost[provider] = \
            self.total_cost.get(provider, 0.0) + cost

        if provider not in self.latencies:
            self.latencies[provider] = []
        self.latencies[provider].append(latency)

    def generate_report(self):
        print("\n📊 Router Performance Report")
        print("=" * 50)

        for provider in self.requests_by_provider:
            requests = self.requests_by_provider[provider]
            cost = self.total_cost[provider]
            avg_latency = sum(self.latencies[provider]) / len(self.latencies[provider])

            print(f"\n{provider}:")
            print(f"  Requests: {requests}")
            print(f"  Total Cost: ${cost:.2f}")
            print(f"  Avg Latency: {avg_latency:.0f}ms")
            print(f"  Cost/Request: ${cost/requests:.4f}")
```

## Testing

```python
async def test_cost_routing():
    router = IntelligentRouter(strategy=RoutingStrategy.COST)

    # Mock providers with different costs
    router.metrics = {
        "gpt-4": ProviderMetrics("gpt-4", 200, 0.95, 0.03, 1.0, 0.5),
        "gpt-3.5": ProviderMetrics("gpt-3.5", 150, 0.85, 0.002, 1.0, 0.3),
    }

    provider = router.route(LLMRequest("simple task"))

    # Should select cheaper option
    assert provider.name == "gpt-3.5"

async def test_quality_routing():
    router = IntelligentRouter(strategy=RoutingStrategy.QUALITY)

    provider = router.route(LLMRequest("complex reasoning"))

    # Should select higher quality
    assert provider.name == "gpt-4"

async def test_circuit_breaker():
    breaker = CircuitBreaker(failure_threshold=3)

    # Simulate failures
    for _ in range(3):
        breaker.record_failure("failing-provider")

    assert not breaker.is_available("failing-provider")

    # After timeout, should be available again
    time.sleep(61)
    assert breaker.is_available("failing-provider")
```

## Extra Challenges

1. **ML-Based Routing**: Train model to predict best provider
2. **A/B Testing**: Randomly test providers to gather data
3. **Multi-Region**: Route based on geographic location
4. **Budget Caps**: Enforce spending limits per provider

## Resources
- [Load Balancing Algorithms](https://www.nginx.com/blog/choosing-nginx-plus-load-balancing-techniques/)
- [Circuit Breaker Pattern](https://martinfowler.com/bliki/CircuitBreaker.html)

**Time**: 6-8h
