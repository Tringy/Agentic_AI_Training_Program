"""RAG System - FastAPI Application."""
import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lab02-code-analyzer-agent/python'))
from llm_client import get_llm_client

from rag import CodebaseRAG, RAGEvaluator, create_eval_dataset

app = FastAPI(
    title="Codebase RAG System",
    description="RAG system for querying codebases with evaluation",
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


class QueryRequest(BaseModel):
    """Request for querying the codebase."""
    question: str
    n_results: int = 5
    filter_language: Optional[str] = None


class IndexDirectoryRequest(BaseModel):
    """Request to index a directory."""
    directory: str
    extensions: Optional[List[str]] = None


class IndexFilesRequest(BaseModel):
    """Request to index files directly."""
    files: Dict[str, str]  # filename -> content


class EvalRequest(BaseModel):
    """Request for evaluation."""
    examples: List[Dict[str, Any]]


class QueryResponse(BaseModel):
    """Response from query."""
    answer: str
    sources: List[Dict[str, Any]]
    context_used: str


# Initialize RAG
provider = os.getenv("LLM_PROVIDER", "anthropic")
llm = get_llm_client(provider)
rag = CodebaseRAG(llm)


@app.post("/index/directory")
async def index_directory(request: IndexDirectoryRequest):
    """Index a codebase directory."""
    try:
        count = rag.index_directory(request.directory, request.extensions)
        return {"indexed_chunks": count, "directory": request.directory}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/index/files")
async def index_files(request: IndexFilesRequest):
    """Index files from request body."""
    try:
        count = rag.index_files(request.files)
        return {"indexed_chunks": count, "files": list(request.files.keys())}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query", response_model=QueryResponse)
async def query_codebase(request: QueryRequest):
    """Query the codebase."""
    try:
        result = rag.query(
            request.question,
            request.n_results,
            request.filter_language
        )
        return QueryResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/evaluate")
async def evaluate_rag(request: EvalRequest):
    """Evaluate RAG performance."""
    try:
        examples = create_eval_dataset(request.examples)
        evaluator = RAGEvaluator(rag, llm)

        retrieval_metrics = evaluator.evaluate_retrieval(examples)
        generation_metrics = evaluator.evaluate_generation(examples)

        return {
            "retrieval": retrieval_metrics,
            "generation": generation_metrics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats():
    """Get index statistics."""
    return rag.get_stats()


@app.delete("/index")
async def clear_index():
    """Clear the index."""
    rag.clear_index()
    return {"status": "cleared"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "provider": provider}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
