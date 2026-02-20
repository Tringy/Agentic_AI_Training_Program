"""RAG Pipeline implementation."""
from typing import List, Dict, Any, Optional
from .vector_store import CodebaseVectorStore
from .chunker import CodeChunker
import os


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

    def __init__(
        self,
        llm_client,
        collection_name: str = "codebase",
        persist_directory: str = "./chroma_db"
    ):
        self.llm = llm_client
        self.vector_store = CodebaseVectorStore(
            collection_name,
            persist_directory
        )
        self.chunker = CodeChunker()

    def index_directory(
        self,
        directory: str,
        extensions: Optional[List[str]] = None
    ) -> int:
        """Index all code files in a directory."""
        if extensions is None:
            extensions = ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go']

        documents = []
        metadatas = []
        ids = []

        for root, dirs, files in os.walk(directory):
            # Skip common non-code directories
            dirs[:] = [d for d in dirs if d not in [
                '.git', 'node_modules', '__pycache__', '.venv',
                'venv', 'dist', 'build', '.next'
            ]]

            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    filepath = os.path.join(root, file)
                    relative_path = os.path.relpath(filepath, directory)

                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()

                        chunks = self.chunker.chunk_file(content, relative_path)

                        for chunk in chunks:
                            documents.append(chunk.content)
                            metadatas.append(chunk.metadata)
                            ids.append(chunk.chunk_id)

                    except Exception as e:
                        print(f"Error processing {filepath}: {e}")

        if documents:
            self.vector_store.add_documents(documents, metadatas, ids)
            print(f"Indexed {len(documents)} chunks from {directory}")

        return len(documents)

    def index_files(
        self,
        files: Dict[str, str]
    ) -> int:
        """Index code from a dictionary of files."""
        documents = []
        metadatas = []
        ids = []

        for filename, content in files.items():
            chunks = self.chunker.chunk_file(content, filename)

            for chunk in chunks:
                documents.append(chunk.content)
                metadatas.append(chunk.metadata)
                ids.append(chunk.chunk_id)

        if documents:
            self.vector_store.add_documents(documents, metadatas, ids)

        return len(documents)

    def query(
        self,
        question: str,
        n_results: int = 5,
        filter_language: Optional[str] = None
    ) -> Dict[str, Any]:
        """Query the codebase and generate an answer."""
        # Build filter
        where = {"language": filter_language} if filter_language else None

        # Retrieve relevant chunks
        results = self.vector_store.query(question, n_results, where)

        if not results:
            return {
                "answer": "No relevant code found for this question.",
                "sources": [],
                "context_used": ""
            }

        # Build context
        context = self._build_context(results)

        # Generate answer
        prompt = RAG_USER_PROMPT.format(context=context, question=question)

        response = self.llm.chat([
            {"role": "system", "content": RAG_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ])

        return {
            "answer": response,
            "sources": [
                {
                    "file": r['metadata']['filename'],
                    "type": r['metadata'].get('type'),
                    "name": r['metadata'].get('name'),
                    "line": r['metadata'].get('line_start'),
                    "relevance": round(1 - r['distance'], 3)
                }
                for r in results
            ],
            "context_used": context
        }

    def _build_context(self, results: List[Dict]) -> str:
        """Build context string from retrieved results."""
        context_parts = []

        for r in results:
            metadata = r['metadata']
            header = f"File: {metadata['filename']}"
            if metadata.get('name'):
                header += f" | {metadata.get('type', 'block')}: {metadata['name']}"
            if metadata.get('line_start'):
                header += f" | Line: {metadata['line_start']}"

            context_parts.append(f"--- {header} ---\n{r['content']}")

        return "\n\n".join(context_parts)

    def get_stats(self) -> Dict:
        """Get index statistics."""
        return self.vector_store.get_stats()

    def clear_index(self) -> None:
        """Clear the index."""
        self.vector_store.clear()
