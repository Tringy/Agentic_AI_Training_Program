# Feature: Hybrid Search

## Overview
The current retrieval pipeline is purely vector-based: every query is embedded with
OpenAI `text-embedding-3-small` and scored by cosine distance in ChromaDB. Keyword
search (BM25) excels at exact-match terms — function names, error codes, import
paths — where semantic similarity is weak. This feature adds a **BM25 index** that
runs in parallel with the vector search; the two ranked lists are merged via
**Reciprocal Rank Fusion (RRF)** to produce a single, stronger result set.

> **Relationship to other specs**
> - **Reranking** (`reranking.md`): hybrid retrieval and reranking are complementary.
>   Hybrid search widens the recall of the candidate pool; reranking then re-scores those
>   candidates to improve precision. When both are enabled, hybrid results are the input
>   to the reranker.
> - **Caching** (`caching.md`): BM25 results for a query can be cached separately from
>   vector results; the merged RRF result set should also be eligible for caching. The
>   cache key must encode the `search_mode` so that `"hybrid"` and `"vector"` queries
>   are cached independently.

---

## Functional Requirements

1. Add a `BM25Index` class in `rag/bm25_store.py` that:
   - Maintains an in-memory BM25 index (using `rank_bm25.BM25Okapi`) over all indexed
     chunks, tokenized by whitespace + punctuation.
   - Exposes `add_documents(ids, documents)` and `query(query_text, n_results) -> List[Dict]`
     returning `{id, content, metadata, bm25_score}` in descending score order.
   - Rebuilds from scratch when `add_documents` is called (append-and-rebuild is
     acceptable at lab scale; no incremental update required).
2. `CodebaseVectorStore` keeps its existing interface unchanged; no BM25 logic lives
   inside the vector store.
3. Add an `rrf_merge(vector_results, bm25_results, k=60) -> List[Dict]` utility in
   `rag/bm25_store.py` that implements standard RRF scoring:
   `score(d) = Σ 1 / (k + rank(d))` over both result lists, then sorts descending.
4. `CodebaseRAG` accepts a `search_mode: str = "hybrid"` constructor/query parameter
   (`"vector"`, `"keyword"`, `"hybrid"`).
5. When `search_mode` is `"hybrid"` or `"keyword"`, `index_files`, `index_directory`,
   and `index_github` paths must also populate the BM25 index.
6. `POST /query` must pass the new `search_mode` field from `QueryRequest` to
   `CodebaseRAG.query()`.
7. Each source object in the query response must include a `search_mode` field
   indicating which index(es) contributed that result (`"vector"`, `"keyword"`, or
   `"hybrid"`).
8. `GET /stats` response must include `bm25_doc_count` when BM25 is active.

---

## Acceptance Criteria

```
GIVEN POST /query with search_mode "vector"
THEN only ChromaDB is consulted; BM25 index is not queried
AND response sources lack a bm25_score field

GIVEN POST /query with search_mode "keyword"
THEN only BM25 is consulted; no embedding API call is made for retrieval
AND sources are ordered by bm25_score descending

GIVEN POST /query with search_mode "hybrid"
THEN both ChromaDB and BM25 are queried with the same query text
AND results are merged using RRF (k=60 default)
AND the merged list length equals min(n_results, combined unique results)
AND each source carries a "search_mode": "hybrid" field

GIVEN a query for an exact function name (e.g. "def authenticate_user")
WHEN search_mode is "hybrid"
THEN the file containing that exact function name ranks in top-3
  (hybrid must outperform or match pure vector on exact-match queries)

GIVEN the index is cleared via DELETE /index
THEN the BM25 index is also cleared
AND GET /stats returns bm25_doc_count: 0
```

---

## Implementation Notes

### New file: `rag/bm25_store.py`

```python
from dataclasses import dataclass, field
from typing import Dict, List
import re

from rank_bm25 import BM25Okapi


def _tokenize(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z0-9_]+", text.lower())


class BM25Index:
    def __init__(self):
        self._ids: List[str] = []
        self._docs: List[str] = []
        self._metas: List[Dict] = []
        self._bm25: BM25Okapi | None = None

    def add_documents(self, ids: List[str], documents: List[str], metadatas: List[Dict]) -> None:
        self._ids.extend(ids)
        self._docs.extend(documents)
        self._metas.extend(metadatas)
        self._bm25 = BM25Okapi([_tokenize(d) for d in self._docs])

    def query(self, query_text: str, n_results: int = 5) -> List[Dict]:
        if self._bm25 is None:
            return []
        tokens = _tokenize(query_text)
        scores = self._bm25.get_scores(tokens)
        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:n_results]
        return [
            {
                "id": self._ids[i],
                "content": self._docs[i],
                "metadata": self._metas[i],
                "bm25_score": float(score),
            }
            for i, score in ranked
            if score > 0
        ]

    def clear(self) -> None:
        self._ids, self._docs, self._metas, self._bm25 = [], [], [], None

    @property
    def doc_count(self) -> int:
        return len(self._ids)


def rrf_merge(
    vector_results: List[Dict],
    bm25_results: List[Dict],
    k: int = 60,
    n: int = 5,
) -> List[Dict]:
    scores: Dict[str, float] = {}
    meta_map: Dict[str, Dict] = {}

    for rank, doc in enumerate(vector_results):
        doc_id = doc["id"]
        scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank + 1)
        meta_map[doc_id] = doc

    for rank, doc in enumerate(bm25_results):
        doc_id = doc["id"]
        scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank + 1)
        if doc_id not in meta_map:
            meta_map[doc_id] = doc

    ranked_ids = sorted(scores, key=lambda x: scores[x], reverse=True)[:n]
    return [{**meta_map[doc_id], "rrf_score": scores[doc_id], "search_mode": "hybrid"} for doc_id in ranked_ids]
```

### Changes to `rag/pipeline.py`

- Import `BM25Index`, `rrf_merge` from `.bm25_store`.
- Add `self.bm25 = BM25Index()` in `__init__`.
- In `index_files` / `index_directory`: after `vector_store.add_documents(...)` also
  call `self.bm25.add_documents(ids, documents, metadatas)`.
- In `query(...)`:
  - `"vector"` → existing path (unchanged).
  - `"keyword"` → `return self.bm25.query(question, n_results)`.
  - `"hybrid"` → run both, call `rrf_merge(vector_results, bm25_results, n=n_results)`.
- In `clear_index()`: call `self.bm25.clear()`.

### Changes to `main.py`

```python
class QueryRequest(BaseModel):
    question: str
    n_results: int = 5
    filter_language: Optional[str] = None
    filter_repository: Optional[str] = None
    search_mode: str = "hybrid"          # NEW
```

Pass `search_mode` to `rag.query(...)`.

### Required package

Add `rank-bm25>=0.2.2` to `python/requirements.txt`.

---

## Frontend Changes

### `components/QueryPanel.tsx`

1. Add a `searchMode` state variable (default `"hybrid"`).
2. Render a segmented control / select with three options: **Vector**, **Keyword**,
   **Hybrid** (default). Place it beside the *n_results* selector.
3. Include `search_mode: searchMode` in the POST body sent to `/query`.
4. In the sources list, display a small badge per source showing `Vector`, `Keyword`,
   or `Hybrid` based on the `search_mode` field in each source object (fall back to
   `"Vector"` if the field is absent for backward compatibility).

### UI copy

| Mode | Label | Tooltip |
|------|-------|---------|
| `vector` | Vector | Semantic similarity search |
| `keyword` | Keyword | Exact keyword match (BM25) |
| `hybrid` | Hybrid ✦ | Best of both (recommended) |
