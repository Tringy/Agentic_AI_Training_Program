---
applyTo: "**/rag/**,**/vector_store*,**/bm25*,**/chunker*,**/reranker*,**/evaluation*,**/pipeline*"
---

# RAG System Skill

You are working on a Retrieval-Augmented Generation (RAG) pipeline. Follow these patterns exactly.

## Overall Pipeline Architecture

```
Index phase:  file/directory/GitHub → CodeChunker → VectorStore (ChromaDB) + BM25Index
Query phase:  question → [vector_store.query + bm25.query] → rrf_merge → [Reranker] → LLM → answer
Eval  phase:  examples → retrieve → precision@k / recall@k / MRR + LLM-as-judge relevance/accuracy
```

## CodeChunker — Language Detection & Chunking

Map file extensions to language strings using this table:

| Extensions | Language |
|------------|----------|
| `.py` | python |
| `.ts`, `.tsx` | typescript |
| `.js`, `.jsx` | javascript |
| `.java` | java |
| `.go` | go |
| `.rs` | rust |
| `.cs` | csharp |
| `.rb` | ruby |
| `.php` | php |
| `.cpp`, `.cc`, `.cxx` | cpp |
| `.c` | c |
| `.sql` | sql |
| `.yaml`, `.yml` | yaml |
| `.md` | markdown |
| `.tf`, `.hcl` | terraform |

Chunking strategies by language:
- **Python**: regex split on `def`, `class`, `async def` boundaries; header (imports/module-level) is a separate chunk
- **JS/TS**: regex split on `function`, `class`, arrow functions
- **Everything else**: size-based (1000 chars) with 100-char overlap

Each `CodeChunk` carries:
```python
@dataclass
class CodeChunk:
    content: str
    chunk_id: str          # "{filename}:{function_name}" or "{filename}:block_{n}"
    metadata: Dict         # filename, language, type, name, line_start, [line_end], [repository]
```

## VectorStore (ChromaDB) Pattern

```python
import chromadb
from chromadb import PersistentClient

class CodebaseVectorStore:
    def __init__(self, collection_name: str, persist_directory: str):
        self.client = PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},   # cosine distance
        )

    def add_documents(self, chunks: List[CodeChunk]):
        if not chunks:
            return
        self.collection.upsert(               # upsert = idempotent re-indexing
            ids=[c.chunk_id for c in chunks],
            documents=[c.content for c in chunks],
            metadatas=[c.metadata for c in chunks],
        )

    def query(self, query: str, n_results: int, where: dict = None):
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where or None,   # ChromaDB $and filter for language/repository
        )
        # Flatten and return list of dicts with content, metadata, distance, id
```

### ChromaDB metadata filters

```python
# Single filter
where = {"language": {"$eq": "python"}}

# Combined filter
where = {"$and": [{"language": {"$eq": "python"}}, {"repository": {"$eq": "my-repo"}}]}
```

### Custom embedding function

Use the custom `OpenAIEmbeddingFunction` wrapper (not ChromaDB's built-in) to support `openai>=1.0`:

```python
class OpenAIEmbeddingFunction(EmbeddingFunction):
    def __call__(self, input: Documents) -> Embeddings:
        # Replace empty strings with " " — OpenAI rejects empty
        texts = [t if t.strip() else " " for t in input]
        # Check embedding cache first; only call API for uncached texts
        uncached = [t for t in texts if not embedding_cache.get(t)]
        if uncached:
            response = client.embeddings.create(model="text-embedding-3-small", input=uncached)
            for text, emb in zip(uncached, response.data):
                embedding_cache.set(text, emb.embedding)
        return [embedding_cache.get(t) for t in texts]
```

## BM25 Index Pattern

```python
from rank_bm25 import BM25Okapi
import re

def _tokenize(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z0-9_]+", text.lower())

class BM25Index:
    _ids: List[str] = []
    _docs: List[str] = []
    _metas: List[dict] = []
    _bm25: BM25Okapi | None = None

    def add_documents(self, ids, docs, metas):
        self._ids.extend(ids)
        self._docs.extend(docs)
        self._metas.extend(metas)
        self._bm25 = BM25Okapi([_tokenize(d) for d in self._docs])  # rebuild from scratch

    def query(self, query_text: str, n_results: int):
        if not self._bm25:
            return []
        scores = self._bm25.get_scores(_tokenize(query_text))
        top_idx = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:n_results]
        return [
            {"id": self._ids[i], "content": self._docs[i],
             "metadata": self._metas[i], "bm25_score": scores[i]}
            for i in top_idx if scores[i] > 0
        ]
```

## Hybrid Search — RRF Merge

Reciprocal Rank Fusion with k=60 (standard default):

```python
def rrf_merge(vector_results, bm25_results, k=60, n=5):
    """Merge two ranked lists via Reciprocal Rank Fusion."""
    scores = {}
    meta_map = {}

    for rank, doc in enumerate(vector_results):
        did = doc["id"]
        scores[did] = scores.get(did, 0) + 1 / (k + rank + 1)
        meta_map[did] = doc

    for rank, doc in enumerate(bm25_results):
        did = doc["id"]
        scores[did] = scores.get(did, 0) + 1 / (k + rank + 1)
        meta_map.setdefault(did, doc)

    sorted_ids = sorted(scores, key=lambda x: scores[x], reverse=True)[:n]
    return [
        {**meta_map[did], "rrf_score": scores[did], "search_mode": "hybrid"}
        for did in sorted_ids
    ]
```

Choose retrieval strategy based on `search_mode`:
- `"vector"` → `vector_store.query()` only
- `"keyword"` → `bm25.query()` only
- `"hybrid"` → both + `rrf_merge()` (default)

## LLM-as-Reranker Pattern

Over-fetch (`n_results * 2`), then rerank to `n_results`:

```python
class Reranker:
    def rerank(self, query: str, candidates: list, top_n: int) -> list:
        numbered = "\n".join(
            f"{i+1}. {c['content'][:400]}" for i, c in enumerate(candidates)
        )
        prompt = (
            f"Query: {query}\n\nCandidates:\n{numbered}\n\n"
            "Rate each candidate's relevance to the query on a scale of 0.0 to 1.0. "
            "Return ONLY a JSON array of numbers, one per candidate, e.g. [0.9, 0.3, 0.7]"
        )
        raw = self.llm.chat([{"role": "user", "content": prompt}])
        match = re.search(r"\[.*?\]", raw, re.DOTALL)
        if not match:
            return candidates[:top_n]  # graceful fallback
        scores = json.loads(match.group())
        # Pad or truncate to match candidate count
        while len(scores) < len(candidates):
            scores.append(0.0)
        for c, score in zip(candidates, scores):
            c["rerank_score"] = float(score)
        return sorted(candidates, key=lambda x: x["rerank_score"], reverse=True)[:top_n]
```

## Two-Level Caching

```python
CACHE_TTL_SECONDS       = 300     # 5 min for query results
EMBEDDING_CACHE_TTL     = 86400   # 24h for embeddings

query_cache     = _LRUCache(max_size=200, ttl=CACHE_TTL_SECONDS)
embedding_cache = _LRUCache(max_size=2000, ttl=EMBEDDING_CACHE_TTL)

def make_query_key(question, n_results, filter_language, filter_repository,
                   search_mode, enable_reranking) -> str:
    params = {"q": question.lower().split(), "n": n_results,
              "lang": filter_language, "repo": filter_repository,
              "mode": search_mode, "rerank": enable_reranking}
    return hashlib.sha256(json.dumps(params, sort_keys=True).encode()).hexdigest()
```

Cache hit/miss is surfaced in the query response as `cache_hit: bool`.

## Evaluation Metrics

```python
def precision_at_k(retrieved: list, relevant: set, k: int) -> float:
    return len(set(retrieved[:k]) & relevant) / k

def recall_at_k(retrieved: list, relevant: set, k: int) -> float:
    if not relevant:
        return 0.0
    return len(set(retrieved[:k]) & relevant) / len(relevant)

def mrr(retrieved: list, relevant: set) -> float:
    for rank, item in enumerate(retrieved, start=1):
        if item in relevant:
            return 1.0 / rank
    return 0.0
```

LLM-as-judge generation eval: score relevance and accuracy on 1–5 scale, then normalize by dividing by 5.

## Index Exclusion List

When indexing a directory, skip these paths:
```python
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv",
             "dist", "build", ".next", ".idea", ".vscode", "coverage",
             ".pytest_cache", "chroma_db"}
```

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `CHROMA_DB_PATH` | `./chroma_db` | ChromaDB persistence path |
| `CACHE_ENABLED` | `true` | Toggle query result caching |
| `EMBEDDING_CACHE_ENABLED` | `true` | Toggle embedding caching |
| `LLM_PROVIDER` | `anthropic` | LLM for generation + reranking |

## Fly.io VM Sizing

Any backend using ChromaDB requires **512 MB RAM** (not the standard 256 MB) because ChromaDB loads its HNSW index into memory. Always set:

```toml
[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 512
```
