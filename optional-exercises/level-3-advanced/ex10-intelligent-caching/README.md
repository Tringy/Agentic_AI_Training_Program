# Exercise 10: Intelligent Caching System

## Description
Semantic cache system for LLM calls that can save 60-80% of costs by identifying similar queries.

## Objectives
- Semantic cache using embeddings
- Cache hit detection with similarity threshold
- TTL and invalidation strategies
- Cost savings analytics

## Architecture

```
User Query → Embed → Search Cache → Hit? → Return cached
                                  → Miss? → Call LLM → Store → Return
```

## Core Implementation

```python
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import hashlib

class SemanticCache:
    def __init__(self, similarity_threshold=0.95):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.qdrant = QdrantClient(":memory:")
        self.threshold = similarity_threshold

        # Create collection
        self.qdrant.create_collection(
            collection_name="llm_cache",
            vectors_config={"size": 384, "distance": "Cosine"}
        )

    async def get(self, query: str) -> str | None:
        # 1. Generate embedding
        query_vector = self.model.encode(query)

        # 2. Search for similar queries
        results = self.qdrant.search(
            collection_name="llm_cache",
            query_vector=query_vector.tolist(),
            limit=1
        )

        # 3. Check similarity threshold
        if results and results[0].score >= self.threshold:
            print(f"🎯 Cache HIT (similarity: {results[0].score:.3f})")
            return results[0].payload['response']

        print("❌ Cache MISS")
        return None

    async def set(self, query: str, response: str, ttl: int = 3600):
        query_vector = self.model.encode(query)

        self.qdrant.upsert(
            collection_name="llm_cache",
            points=[{
                "id": hashlib.md5(query.encode()).hexdigest(),
                "vector": query_vector.tolist(),
                "payload": {
                    "query": query,
                    "response": response,
                    "created_at": time.time(),
                    "ttl": ttl
                }
            }]
        )
```

## Usage Example

```python
cache = SemanticCache(similarity_threshold=0.95)

async def cached_completion(prompt: str):
    # Check cache
    cached_response = await cache.get(prompt)
    if cached_response:
        return cached_response

    # Cache miss - call LLM
    response = await llm_client.complete(prompt)

    # Store in cache
    await cache.set(prompt, response)

    return response

# Example queries that should hit cache
await cached_completion("What is Python?")
await cached_completion("What's Python?")  # Similar! Should hit cache
await cached_completion("Tell me about Python")  # Also similar!
```

## Advanced Features

### 1. Tiered Caching
```python
class TieredCache:
    """In-memory (fast) + Vector DB (semantic) + Disk (persistent)"""

    def __init__(self):
        self.l1_cache = {}  # Exact match (dict)
        self.l2_cache = SemanticCache()  # Semantic (vector)
        self.l3_cache = RedisCache()  # Distributed

    async def get(self, query: str):
        # L1: Exact match
        if query in self.l1_cache:
            return self.l1_cache[query]

        # L2: Semantic similarity
        result = await self.l2_cache.get(query)
        if result:
            self.l1_cache[query] = result  # Promote to L1
            return result

        # L3: Distributed cache
        return await self.l3_cache.get(query)
```

### 2. Cache Analytics

```python
class CacheAnalytics:
    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.cost_saved = 0.0

    def record_hit(self, query: str):
        self.hits += 1
        # Estimate cost saved
        tokens = len(query.split()) * 1.3  # Rough estimate
        self.cost_saved += self.calculate_cost(tokens)

    def get_stats(self):
        total = self.hits + self.misses
        hit_rate = self.hits / total if total > 0 else 0

        return {
            "hit_rate": f"{hit_rate:.1%}",
            "total_requests": total,
            "cost_saved": f"${self.cost_saved:.2f}"
        }
```

### 3. Smart Invalidation

```python
class SmartInvalidation:
    """Invalidate cache based on relevance decay"""

    def should_invalidate(self, cache_entry) -> bool:
        # Time-based decay
        age_hours = (time.time() - cache_entry['created_at']) / 3600

        # Fact-checking queries expire faster
        if 'fact' in cache_entry['query'].lower():
            return age_hours > 6

        # Code generation can be cached longer
        if 'code' in cache_entry['query'].lower():
            return age_hours > 24

        return age_hours > 12  # Default
```

## Testing

```python
async def test_semantic_cache():
    cache = SemanticCache(similarity_threshold=0.95)

    # Store original
    await cache.set("What is the capital of France?", "Paris")

    # Similar query should hit
    result = await cache.get("What's France's capital?")
    assert result == "Paris"

    # Different query should miss
    result = await cache.get("What is the capital of Spain?")
    assert result is None

async def test_cost_savings():
    cache = SemanticCache()
    analytics = CacheAnalytics()

    queries = ["What is Python?"] * 100

    for query in queries:
        cached = await cache.get(query)
        if cached:
            analytics.record_hit(query)
        else:
            response = await llm_call(query)
            await cache.set(query, response)
            analytics.record_miss()

    stats = analytics.get_stats()
    assert float(stats['hit_rate'].rstrip('%')) > 90  # 99% hit rate expected
```

## Performance Benchmarks

Target metrics:
- Cache lookup: < 10ms
- Similarity search: < 50ms
- Hit rate: > 60% after warmup
- Cost reduction: 60-80%

## Extra Challenges

1. **Distributed Caching**: Redis cluster with consistent hashing
2. **Adaptive Thresholds**: ML model to optimize similarity threshold
3. **Context-Aware Caching**: Consider conversation context
4. **Compression**: Compress cached responses

## Resources
- [Qdrant Semantic Search](https://qdrant.tech)
- [Sentence Transformers](https://sbert.net)
- [GPTCache Paper](https://arxiv.org/abs/2305.04676)

**Estimated time**: 6-7h

---

**Intelligent cache = 💰 big savings**
