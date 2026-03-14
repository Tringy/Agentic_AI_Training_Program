"""Vector Store implementation using ChromaDB with OpenAI embeddings."""

import os
from typing import Any, Dict, List, Optional

import chromadb
from chromadb import Documents, EmbeddingFunction, Embeddings
from openai import OpenAI


class OpenAIEmbeddingFunction(EmbeddingFunction):
    """Custom embedding function using the OpenAI client directly.

    ChromaDB's built-in OpenAIEmbeddingFunction targets the legacy openai<1.0
    request format and throws '$.input is invalid' against openai>=1.0.
    This wrapper calls the SDK directly and is always compatible.
    """

    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        self._client = OpenAI(api_key=api_key)
        self._model = model

    def __call__(self, input: Documents) -> Embeddings:  # noqa: A002
        # OpenAI rejects empty strings — replace with a single space so the
        # index position is preserved (ChromaDB matches embeddings by position).
        safe = [doc if doc and doc.strip() else " " for doc in input]

        from .cache import EMBEDDING_CACHE_ENABLED, embedding_cache

        if not EMBEDDING_CACHE_ENABLED:
            response = self._client.embeddings.create(model=self._model, input=safe)
            return [item.embedding for item in response.data]

        result: List[Optional[List[float]]] = [None] * len(safe)
        uncached_indices: List[int] = []
        uncached_texts: List[str] = []

        for i, text in enumerate(safe):
            cached = embedding_cache.get(f"{self._model}:{text}")
            if cached is not None:
                result[i] = cached
            else:
                uncached_indices.append(i)
                uncached_texts.append(text)

        if uncached_texts:
            response = self._client.embeddings.create(model=self._model, input=uncached_texts)
            for idx, item in zip(uncached_indices, response.data):
                embedding_cache.set(f"{self._model}:{safe[idx]}", item.embedding)
                result[idx] = item.embedding

        return result  # type: ignore[return-value]


class CodebaseVectorStore:
    """Vector store for code embeddings using ChromaDB + OpenAI."""

    def __init__(self, collection_name: str = "codebase", persist_directory: str | None = None):
        # Prefer explicit arg, then env var, then local fallback
        if persist_directory is None:
            persist_directory = os.getenv("CHROMA_DB_PATH", "./chroma_db")
        # Initialize ChromaDB with persistence
        self.client = chromadb.PersistentClient(path=persist_directory)

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

        self.embedding_fn = OpenAIEmbeddingFunction(api_key=api_key)

        self.collection = self.client.get_or_create_collection(
            name=collection_name, embedding_function=self.embedding_fn, metadata={"hnsw:space": "cosine"}
        )

    def add_documents(self, documents: List[str], metadatas: List[Dict[str, Any]], ids: List[str]) -> None:
        """Add documents to the vector store, skipping empty chunks."""
        filtered = [(doc, meta, id_) for doc, meta, id_ in zip(documents, metadatas, ids) if doc and doc.strip()]
        if not filtered:
            return
        docs, metas, id_list = zip(*filtered)
        self.collection.upsert(documents=list(docs), metadatas=list(metas), ids=list(id_list))

    def query(self, query: str, n_results: int = 5, where: Optional[Dict] = None) -> List[Dict]:
        """Query the vector store."""
        results = self.collection.query(query_texts=[query], n_results=n_results, where=where)

        formatted = []
        for i in range(len(results["documents"][0])):
            formatted.append(
                {
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i],
                    "id": results["ids"][0][i],
                }
            )

        return formatted

    def get_stats(self) -> Dict:
        """Get collection statistics."""
        return {"count": self.collection.count(), "name": self.collection.name}

    def clear(self) -> None:
        """Clear all documents from the collection."""
        self.client.delete_collection(self.collection.name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection.name, embedding_function=self.embedding_fn, metadata={"hnsw:space": "cosine"}
        )
