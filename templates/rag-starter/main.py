"""
RAG Starter - FastAPI Application
A minimal RAG system for learning and prototyping.
"""
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from openai import OpenAI

from simple_rag import SimpleRAG

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="RAG Starter",
    description="Minimal RAG system for learning",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class Document(BaseModel):
    """A document to be indexed."""
    id: str
    content: str
    metadata: Optional[Dict[str, Any]] = {}


class IndexRequest(BaseModel):
    """Request to index documents."""
    documents: List[Document]


class QueryRequest(BaseModel):
    """Request to query the RAG system."""
    question: str
    top_k: int = 3


class QueryResponse(BaseModel):
    """Response from query."""
    answer: str
    sources: List[Dict[str, Any]]
    context_used: str


# Initialize RAG system
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
rag = SimpleRAG(
    openai_client=openai_client,
    model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    embedding_model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
    chunk_size=int(os.getenv("CHUNK_SIZE", "500")),
    chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "50"))
)


@app.post("/index")
async def index_documents(request: IndexRequest):
    """
    Index documents for later retrieval.

    Documents are split into chunks, embedded, and stored in memory.
    """
    try:
        total_chunks = 0

        for doc in request.documents:
            chunks = rag.index_document(
                doc_id=doc.id,
                content=doc.content,
                metadata=doc.metadata
            )
            total_chunks += chunks

        return {
            "indexed_count": len(request.documents),
            "total_chunks": total_chunks,
            "status": "success"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    """
    Query the RAG system with a question.

    Retrieves relevant chunks and generates an answer using LLM.
    """
    try:
        result = rag.query(
            question=request.question,
            top_k=request.top_k
        )

        return QueryResponse(**result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """
    Health check endpoint.

    Returns status and number of indexed chunks.
    """
    return {
        "status": "healthy",
        "indexed_chunks": rag.get_chunk_count()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
