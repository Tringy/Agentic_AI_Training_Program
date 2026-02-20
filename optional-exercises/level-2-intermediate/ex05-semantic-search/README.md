# Exercise 05: Semantic Search Engine

## Description
Build a semantic search engine over technical documentation using embeddings and vector databases.

## Objectives
- Implement indexing with embeddings
- Vector search with Qdrant/Pinecone
- Hybrid search (vector + keyword)
- Reranking to improve relevance

## Stack
```bash
Backend: FastAPI + Qdrant + sentence-transformers
Frontend: Next.js + TailwindCSS
```

## Core Implementation

### 1. Document Indexing
```python
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

class DocumentIndexer:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.qdrant = QdrantClient("localhost", port=6333)

    async def index_document(self, doc: Document):
        # 1. Chunk document
        chunks = self.chunk_document(doc, chunk_size=500)

        # 2. Generate embeddings
        embeddings = self.model.encode(chunks)

        # 3. Store in Qdrant
        self.qdrant.upsert(
            collection_name="docs",
            points=[
                {
                    "id": f"{doc.id}_{i}",
                    "vector": emb.tolist(),
                    "payload": {"text": chunk, "metadata": doc.metadata}
                }
                for i, (chunk, emb) in enumerate(zip(chunks, embeddings))
            ]
        )
```

### 2. Semantic Search
```python
async def search(query: str, top_k: int = 10):
    # 1. Encode query
    query_vector = model.encode(query)

    # 2. Vector search
    results = qdrant.search(
        collection_name="docs",
        query_vector=query_vector,
        limit=top_k
    )

    # 3. Rerank with cross-encoder (optional)
    reranked = rerank(query, results)

    return reranked
```

### 3. Hybrid Search
```python
def hybrid_search(query: str):
    # Combine vector + BM25 keyword search
    vector_results = semantic_search(query)
    keyword_results = bm25_search(query)

    # Reciprocal Rank Fusion
    combined = reciprocal_rank_fusion(
        [vector_results, keyword_results]
    )

    return combined
```

## Features
- [ ] Document upload & indexing
- [ ] Real-time search with < 100ms latency
- [ ] Filters (date, author, category)
- [ ] Query suggestions
- [ ] Search analytics

## Challenges
1. Implement query expansion
2. Add multilingual support
3. Personalized search
4. Search result explanations

## Resources
- [Qdrant Tutorial](https://qdrant.tech/documentation/)
- [Sentence Transformers](https://www.sbert.net/)

**Time**: 4-5h
