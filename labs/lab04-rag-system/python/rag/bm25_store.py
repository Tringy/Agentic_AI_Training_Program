"""BM25 keyword index and RRF merge utilities."""

import re
from typing import Dict, List, Optional

from rank_bm25 import BM25Okapi


def _tokenize(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z0-9_]+", text.lower())


class BM25Index:
    """In-memory BM25 index over indexed code chunks."""

    def __init__(self) -> None:
        self._ids: List[str] = []
        self._docs: List[str] = []
        self._metas: List[Dict] = []
        self._bm25: Optional[BM25Okapi] = None

    def add_documents(self, ids: List[str], documents: List[str], metadatas: List[Dict]) -> None:
        """Append documents and rebuild the BM25 index."""
        self._ids.extend(ids)
        self._docs.extend(documents)
        self._metas.extend(metadatas)
        self._bm25 = BM25Okapi([_tokenize(d) for d in self._docs])

    def query(self, query_text: str, n_results: int = 5) -> List[Dict]:
        """Return top-n results ordered by BM25 score descending."""
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
    """Merge two ranked lists using Reciprocal Rank Fusion."""
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
