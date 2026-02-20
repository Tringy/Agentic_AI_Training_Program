# Exercise 16: Custom LLM Router with ML

## Description
Advanced router with ML that learns which provider to use based on historical performance.

## Objectives
- Train ML model for routing decisions
- Collect performance data
- Optimize cost vs quality tradeoff
- A/B testing framework
- Real-time adaptation

## ML-Based Router Architecture

```python
from sklearn.ensemble import RandomForestClassifier
import pandas as pd

class MLRouter:
    def __init__(self):
        self.model = RandomForestClassifier()
        self.performance_db = PerformanceDB()
        self.is_trained = False

    async def route(self, request: LLMRequest) -> Provider:
        if not self.is_trained:
            # Fallback to rule-based
            return self._fallback_routing(request)

        # Extract features
        features = self._extract_features(request)

        # Predict best provider
        provider_id = self.model.predict([features])[0]

        return self.providers[provider_id]

    def _extract_features(self, request: LLMRequest) -> List[float]:
        """Extract features for ML model"""
        return [
            len(request.prompt),  # prompt length
            request.estimated_complexity,  # 0-1
            request.requires_reasoning,  # boolean
            request.time_of_day,  # hour
            request.user_tier,  # premium vs free
            self._get_provider_load("gpt-4"),
            self._get_provider_load("claude"),
        ]

    async def train(self):
        """Train model on historical data"""
        # Get past requests and their outcomes
        data = await self.performance_db.get_training_data()

        X = [self._extract_features(req) for req in data['requests']]
        y = data['best_provider']  # Determined by cost/quality

        self.model.fit(X, y)
        self.is_trained = True

        # Evaluate
        score = self.model.score(X_test, y_test)
        print(f"Model accuracy: {score:.2%}")
```

## Online Learning

```python
class OnlineMLRouter(MLRouter):
    """Continuously learn from new data"""

    async def route_and_learn(self, request: LLMRequest):
        # Route request
        provider = await self.route(request)

        # Execute
        result = await provider.complete(request)

        # Calculate quality score
        quality = await self._evaluate_quality(result)

        # Store for retraining
        await self._store_outcome(request, provider, quality)

        # Retrain periodically
        if self._should_retrain():
            await self.train()

        return result
```

## Multi-Armed Bandit

```python
class BanditRouter:
    """Explore-exploit tradeoff"""

    def __init__(self, epsilon=0.1):
        self.epsilon = epsilon  # Exploration rate
        self.provider_stats = {}

    def select_provider(self, request):
        if random.random() < self.epsilon:
            # Explore: random provider
            return random.choice(self.providers)
        else:
            # Exploit: best known provider
            return self._best_provider(request)

    def _best_provider(self, request):
        # Thompson sampling
        scores = {
            p: self._thompson_sample(self.provider_stats[p])
            for p in self.providers
        }
        return max(scores, key=scores.get)
```

## Cost-Quality Pareto Optimization

```python
def find_pareto_optimal(providers, request):
    """Find providers on Pareto frontier"""

    pareto = []

    for p1 in providers:
        is_dominated = False

        for p2 in providers:
            if p1 == p2:
                continue

            # Check if p2 dominates p1
            if (p2.cost <= p1.cost and p2.quality >= p1.quality and
                (p2.cost < p1.cost or p2.quality > p1.quality)):
                is_dominated = True
                break

        if not is_dominated:
            pareto.append(p1)

    return pareto
```

**Time**: 10-15h
**Resources**: [Multi-Armed Bandits](https://lilianweng.github.io/posts/2018-01-23-multi-armed-bandit/)
