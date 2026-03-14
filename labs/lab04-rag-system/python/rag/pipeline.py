"""RAG Pipeline implementation."""

import os
from typing import Any, Dict, List, Optional

from .bm25_store import BM25Index, rrf_merge
from .chunker import CodeChunker
from .reranker import Reranker
from .vector_store import CodebaseVectorStore

RAG_SYSTEM_PROMPT = """You are a helpful assistant that answers questions about code.
Use the provided code context to answer questions accurately.
If the context doesn't contain enough information, say so.
Always reference specific files and line numbers when possible."""

RAG_USER_PROMPT = """Based on the following code context, answer the question.

Context:
{context}

Question: {question}

Provide a clear, accurate answer based on the code context above."""


class CodebaseRAG:
    """Complete RAG pipeline for codebase Q&A."""

    def __init__(self, llm_client, collection_name: str = "codebase", persist_directory: str | None = None):
        self.llm = llm_client
        self.vector_store = CodebaseVectorStore(collection_name, persist_directory)  # None → vector_store reads CHROMA_DB_PATH env var
        self.chunker = CodeChunker()
        self.bm25 = BM25Index()
        self.reranker = Reranker(llm_client=self.llm)

    def index_directory(self, directory: str, extensions: Optional[List[str]] = None, repository: Optional[str] = None) -> int:
        """Index all code files in a directory."""
        if extensions is None:
            extensions = [
                # Web / JS ecosystem
                ".js",
                ".ts",
                ".jsx",
                ".tsx",
                ".mjs",
                ".cjs",
                # Python
                ".py",
                # .NET
                ".cs",
                ".fs",
                ".vb",
                ".csproj",
                ".fsproj",
                ".sln",
                # JVM
                ".java",
                ".kt",
                ".kts",
                ".scala",
                ".groovy",
                # Go
                ".go",
                # Rust
                ".rs",
                # Ruby
                ".rb",
                # PHP
                ".php",
                # Swift / ObjC
                ".swift",
                ".m",
                ".h",
                # C / C++
                ".c",
                ".cpp",
                ".cc",
                ".cxx",
                ".hpp",
                # Shell
                ".sh",
                ".bash",
                ".zsh",
                ".ps1",
                # Config / data
                ".json",
                ".yaml",
                ".yml",
                ".toml",
                ".xml",
                ".env",
                # Docs
                ".md",
                ".mdx",
                ".rst",
                ".txt",
                # SQL
                ".sql",
                # Other
                ".dockerfile",
                ".tf",
                ".hcl",
            ]

        documents = []
        metadatas = []
        ids = []

        for root, dirs, files in os.walk(directory):
            # Skip common non-code directories
            dirs[:] = [
                d
                for d in dirs
                if d
                not in [
                    ".git",
                    ".github",
                    ".svn",
                    "node_modules",
                    ".pnpm-store",
                    "__pycache__",
                    ".venv",
                    "venv",
                    ".env",
                    "dist",
                    "build",
                    "out",
                    "bin",
                    "obj",
                    ".next",
                    ".nuxt",
                    ".output",
                    "coverage",
                    ".nyc_output",
                    ".idea",
                    ".vscode",
                    "packages",  # NuGet cache
                ]
            ]

            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    filepath = os.path.join(root, file)
                    relative_path = os.path.relpath(filepath, directory)

                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            content = f.read()

                        chunks = self.chunker.chunk_file(content, relative_path)

                        for chunk in chunks:
                            if repository:
                                chunk.metadata["repository"] = repository
                            documents.append(chunk.content)
                            metadatas.append(chunk.metadata)
                            ids.append(chunk.chunk_id)

                    except Exception as e:
                        print(f"Error processing {filepath}: {e}")

        if documents:
            self.vector_store.add_documents(documents, metadatas, ids)
            self.bm25.add_documents(ids, documents, metadatas)
            print(f"Indexed {len(documents)} chunks from {directory}")

        return len(documents)

    def index_files(self, files: Dict[str, str], repository: Optional[str] = None) -> int:
        """Index code from a dictionary of files."""
        documents = []
        metadatas = []
        ids = []

        for filename, content in files.items():
            chunks = self.chunker.chunk_file(content, filename)

            for chunk in chunks:
                if repository:
                    chunk.metadata["repository"] = repository
                documents.append(chunk.content)
                metadatas.append(chunk.metadata)
                ids.append(chunk.chunk_id)

        if documents:
            self.vector_store.add_documents(documents, metadatas, ids)
            self.bm25.add_documents(ids, documents, metadatas)

        return len(documents)

    def query(
        self,
        question: str,
        n_results: int = 5,
        filter_language: Optional[str] = None,
        filter_repository: Optional[str] = None,
        search_mode: str = "hybrid",
        enable_reranking: bool = False,
    ) -> Dict[str, Any]:
        """Query the codebase and generate an answer."""
        from .cache import CACHE_ENABLED, make_query_key, query_cache

        # Check cache before doing any work
        cache_key = make_query_key(question, n_results, filter_language, filter_repository, search_mode, enable_reranking)
        if CACHE_ENABLED:
            cached = query_cache.get(cache_key)
            if cached is not None:
                return {**cached, "cache_hit": True}

        # Build ChromaDB where filter
        conditions = []
        if filter_language:
            conditions.append({"language": filter_language})
        if filter_repository:
            conditions.append({"repository": filter_repository})

        if len(conditions) == 0:
            where = None
        elif len(conditions) == 1:
            where = conditions[0]
        else:
            where = {"$and": conditions}

        # Over-fetch when reranking so the reranker has candidates to reorder
        fetch_n = n_results * 2 if enable_reranking else n_results

        results = self._retrieve(question, fetch_n, where, search_mode)

        if not results:
            return {"answer": "No relevant code found for this question.", "sources": [], "context_used": "", "cache_hit": False}

        if enable_reranking:
            results = self.reranker.rerank(question, results, top_n=n_results)
        else:
            for r in results:
                r["rerank_score"] = None

        context = self._build_context(results)
        prompt = RAG_USER_PROMPT.format(context=context, question=question)
        response = self.llm.chat([{"role": "system", "content": RAG_SYSTEM_PROMPT}, {"role": "user", "content": prompt}])

        result: Dict[str, Any] = {
            "answer": response,
            "sources": [self._format_source(r) for r in results],
            "context_used": context,
            "cache_hit": False,
        }

        if CACHE_ENABLED:
            query_cache.set(cache_key, result)

        return result

    def _retrieve(self, question: str, n_results: int, where: Optional[Dict], search_mode: str) -> List[Dict]:
        """Dispatch retrieval to vector, keyword, or hybrid backend."""
        if search_mode == "keyword":
            results = self.bm25.query(question, n_results)
            for r in results:
                r["search_mode"] = "keyword"
            return results
        elif search_mode == "hybrid" and self.bm25.doc_count > 0:
            vector_results = self.vector_store.query(question, n_results, where)
            bm25_results = self.bm25.query(question, n_results)
            return rrf_merge(vector_results, bm25_results, n=n_results)
        else:  # "vector" or hybrid fallback when BM25 is empty
            results = self.vector_store.query(question, n_results, where)
            for r in results:
                r["search_mode"] = "vector"
            return results

    def _format_source(self, r: Dict) -> Dict:
        """Format a retrieval result into the API source shape."""
        meta = r.get("metadata", {})
        if "distance" in r:
            relevance: Optional[float] = round(1 - r["distance"], 3)
        elif "rrf_score" in r:
            relevance = round(min(r["rrf_score"] * 500, 1.0), 3)
        elif "bm25_score" in r:
            relevance = round(min(r["bm25_score"] / 10.0, 1.0), 3)
        else:
            relevance = None
        return {
            "file": meta.get("filename", r.get("id", "unknown")),
            "type": meta.get("type"),
            "name": meta.get("name"),
            "line": meta.get("line_start"),
            "relevance": relevance,
            "search_mode": r.get("search_mode", "vector"),
            "rerank_score": r.get("rerank_score"),
        }

    def _build_context(self, results: List[Dict]) -> str:
        """Build context string from retrieved results."""
        context_parts = []

        for r in results:
            metadata = r["metadata"]
            header = f"File: {metadata['filename']}"
            if metadata.get("name"):
                header += f" | {metadata.get('type', 'block')}: {metadata['name']}"
            if metadata.get("line_start"):
                header += f" | Line: {metadata['line_start']}"

            context_parts.append(f"--- {header} ---\n{r['content']}")

        return "\n\n".join(context_parts)

    def get_stats(self) -> Dict:
        """Get index statistics."""
        stats = self.vector_store.get_stats()
        stats["bm25_doc_count"] = self.bm25.doc_count
        stats["reranker_enabled"] = self.reranker.enabled
        return stats

    def clear_index(self) -> None:
        """Clear the vector index, BM25 index, and query/embedding caches."""
        from .cache import embedding_cache, query_cache

        self.vector_store.clear()
        self.bm25.clear()
        query_cache.clear()
        embedding_cache.clear()
