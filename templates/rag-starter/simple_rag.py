"""
Simple RAG Implementation
A minimal in-memory RAG system using OpenAI embeddings and numpy.
"""
from typing import List, Dict, Any, Optional
import numpy as np
from embeddings import get_embedding, cosine_similarity


class SimpleRAG:
    """
    A simple in-memory RAG system.

    Uses:
    - Fixed-size text chunking
    - OpenAI embeddings
    - Numpy-based cosine similarity
    - In-memory storage (no database)
    """

    def __init__(
        self,
        openai_client,
        model: str = "gpt-4o-mini",
        embedding_model: str = "text-embedding-3-small",
        chunk_size: int = 500,
        chunk_overlap: int = 50
    ):
        """
        Initialize the RAG system.

        Args:
            openai_client: OpenAI client instance
            model: LLM model for answer generation
            embedding_model: Model for embeddings
            chunk_size: Size of text chunks in characters
            chunk_overlap: Overlap between chunks in characters
        """
        self.openai_client = openai_client
        self.model = model
        self.embedding_model = embedding_model
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # In-memory storage
        self.chunks = []  # List of chunk dictionaries
        self.embeddings = None  # Numpy array of embeddings

    def _chunk_text(self, text: str) -> List[str]:
        """
        Split text into fixed-size chunks with overlap.

        Args:
            text: Text to chunk

        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + self.chunk_size
            chunk = text[start:end]

            if chunk.strip():
                chunks.append(chunk)

            start += self.chunk_size - self.chunk_overlap

        return chunks

    def index_document(
        self,
        doc_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Index a document by chunking and embedding it.

        Args:
            doc_id: Unique document identifier
            content: Document content
            metadata: Optional metadata

        Returns:
            Number of chunks created
        """
        if metadata is None:
            metadata = {}

        # Chunk the document
        text_chunks = self._chunk_text(content)

        # Create embeddings for each chunk
        chunk_count = 0
        for i, chunk_text in enumerate(text_chunks):
            # Get embedding
            embedding = get_embedding(
                self.openai_client,
                chunk_text,
                self.embedding_model
            )

            # Store chunk with metadata
            chunk = {
                "id": f"{doc_id}_chunk_{i}",
                "doc_id": doc_id,
                "content": chunk_text,
                "metadata": metadata,
                "chunk_index": i
            }
            self.chunks.append(chunk)

            # Add embedding to array
            if self.embeddings is None:
                self.embeddings = np.array([embedding])
            else:
                self.embeddings = np.vstack([self.embeddings, embedding])

            chunk_count += 1

        return chunk_count

    def query(
        self,
        question: str,
        top_k: int = 3
    ) -> Dict[str, Any]:
        """
        Query the RAG system.

        Args:
            question: User question
            top_k: Number of chunks to retrieve

        Returns:
            Dictionary with answer, sources, and context
        """
        if not self.chunks:
            return {
                "answer": "No documents have been indexed yet.",
                "sources": [],
                "context_used": ""
            }

        # Get question embedding
        question_embedding = get_embedding(
            self.openai_client,
            question,
            self.embedding_model
        )

        # Calculate similarities
        similarities = []
        for i, chunk_embedding in enumerate(self.embeddings):
            similarity = cosine_similarity(question_embedding, chunk_embedding)
            similarities.append((i, similarity))

        # Sort by similarity (highest first)
        similarities.sort(key=lambda x: x[1], reverse=True)

        # Get top-k chunks
        top_chunks = []
        for i, similarity in similarities[:top_k]:
            chunk = self.chunks[i].copy()
            chunk["similarity"] = round(similarity, 3)
            top_chunks.append(chunk)

        # Build context for LLM
        context = self._build_context(top_chunks)

        # Generate answer using LLM
        answer = self._generate_answer(question, context)

        return {
            "answer": answer,
            "sources": [
                {
                    "id": chunk["id"],
                    "content": chunk["content"][:200] + "...",  # Truncate for response
                    "similarity": chunk["similarity"],
                    "metadata": chunk["metadata"]
                }
                for chunk in top_chunks
            ],
            "context_used": context
        }

    def _build_context(self, chunks: List[Dict]) -> str:
        """
        Build context string from retrieved chunks.

        Args:
            chunks: List of chunk dictionaries

        Returns:
            Formatted context string
        """
        context_parts = []

        for chunk in chunks:
            header = f"[Document: {chunk['doc_id']}, Chunk: {chunk['chunk_index']}]"
            if chunk["metadata"]:
                metadata_str = ", ".join(f"{k}: {v}" for k, v in chunk["metadata"].items())
                header += f" ({metadata_str})"

            context_parts.append(f"{header}\n{chunk['content']}")

        return "\n\n---\n\n".join(context_parts)

    def _generate_answer(self, question: str, context: str) -> str:
        """
        Generate answer using LLM with retrieved context.

        Args:
            question: User question
            context: Retrieved context

        Returns:
            Generated answer
        """
        system_prompt = """You are a helpful assistant that answers questions based on provided context.
Always base your answers on the context provided. If the context doesn't contain enough information
to answer the question, say so clearly."""

        user_prompt = f"""Context:
{context}

Question: {question}

Please provide a clear, accurate answer based on the context above."""

        response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )

        return response.choices[0].message.content

    def get_chunk_count(self) -> int:
        """Get the number of indexed chunks."""
        return len(self.chunks)
