"""LLM-as-reranker — no new dependencies, no model weights, no extra API keys."""

import json
import re
from typing import Dict, List, Optional


class Reranker:
    """Re-scores retrieval candidates using the existing LLM client.

    Sends a single prompt with all candidates and parses a JSON score array.
    Works with any LLM provider already configured in the project.
    """

    def __init__(self, llm_client) -> None:
        self._llm = llm_client
        self._call_count: int = 0

    def rerank(self, query: str, candidates: List[Dict], top_n: int) -> List[Dict]:
        """Re-order candidates by relevance. Returns at most top_n results."""
        if not candidates:
            return candidates

        numbered = "\n\n".join(f"[{i}] {c['content'][:400]}" for i, c in enumerate(candidates))
        prompt = (
            f"Rate each code snippet's relevance to the following query on a scale "
            f"of 0.0 to 1.0.\n"
            f"Query: {query}\n\n"
            f"{numbered}\n\n"
            f"Reply with a JSON array of {len(candidates)} numbers only, "
            f"e.g. [0.9, 0.3, 0.7, ...]. No explanation."
        )
        raw = self._llm.chat(
            [
                {
                    "role": "system",
                    "content": "You are a relevance scoring assistant. Reply with a JSON array of numbers only.",
                },
                {"role": "user", "content": prompt},
            ]
        )

        match = re.search(r"\[.*?\]", raw, re.DOTALL)
        if not match:
            # Parsing failed — return candidates unchanged with null scores
            return [{**c, "rerank_score": None} for c in candidates[:top_n]]

        scores = [float(s) for s in json.loads(match.group())]
        # Guard against mismatched array length from the LLM
        scores = (scores + [0.0] * len(candidates))[: len(candidates)]

        ranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)[:top_n]
        self._call_count += 1
        return [{**doc, "rerank_score": float(score)} for doc, score in ranked]

    @property
    def enabled(self) -> bool:
        """True once at least one reranking call has been made this process lifetime."""
        return self._call_count > 0
