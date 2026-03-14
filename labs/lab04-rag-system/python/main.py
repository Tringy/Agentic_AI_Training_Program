"""RAG System - FastAPI Application."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Load environment variables
load_dotenv()

from llm_client import get_llm_client
from rag import CodebaseRAG, RAGEvaluator, create_eval_dataset

app = FastAPI(title="Codebase RAG System", description="RAG system for querying codebases with evaluation", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Repo registry — persisted to disk so it survives container restarts on
# fly.io (as long as the volume is mounted at CHROMA_DB_PATH/../).
# ---------------------------------------------------------------------------
_REGISTRY_PATH = Path(os.getenv("CHROMA_DB_PATH", "./chroma_db")) / "repos.json"


def _load_registry() -> Dict[str, Any]:
    try:
        if _REGISTRY_PATH.exists():
            return json.loads(_REGISTRY_PATH.read_text())
    except Exception:
        pass
    return {}


def _save_registry(registry: Dict[str, Any]) -> None:
    try:
        _REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
        _REGISTRY_PATH.write_text(json.dumps(registry, indent=2))
    except Exception as exc:
        print(f"Warning: could not persist repo registry: {exc}")


_repo_registry: Dict[str, Any] = _load_registry()


def _register_repo(name: str, url: str, chunks: int) -> None:
    _repo_registry[name] = {
        "name": name,
        "url": url,
        "chunks": _repo_registry.get(name, {}).get("chunks", 0) + chunks,
        "indexed_at": datetime.now(timezone.utc).isoformat(),
    }
    _save_registry(_repo_registry)


class QueryRequest(BaseModel):
    """Request for querying the codebase."""

    question: str
    n_results: int = 5
    filter_language: Optional[str] = None
    filter_repository: Optional[str] = None
    search_mode: str = "hybrid"
    enable_reranking: bool = False


class IndexDirectoryRequest(BaseModel):
    """Request to index a directory."""

    directory: str
    extensions: Optional[List[str]] = None


class IndexGithubRequest(BaseModel):
    """Request to index a GitHub repository."""

    url: str
    branch: Optional[str] = None
    extensions: Optional[List[str]] = None


class IndexFilesRequest(BaseModel):
    """Request to index files directly."""

    files: Dict[str, str]  # filename -> content
    repository: Optional[str] = None  # logical name for this set of files


class EvalRequest(BaseModel):
    """Request for evaluation."""

    examples: List[Dict[str, Any]]


class QueryResponse(BaseModel):
    """Response from query."""

    answer: str
    sources: List[Dict[str, Any]]
    context_used: str
    cache_hit: bool = False


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


@app.post("/index/github")
async def index_github(request: IndexGithubRequest):
    """Clone a GitHub repository and index it."""
    import shutil
    import subprocess
    import tempfile

    # Basic validation to prevent command injection
    url = request.url.strip()
    if not url.startswith(("https://github.com/", "https://gitlab.com/", "https://bitbucket.org/")):
        raise HTTPException(status_code=400, detail="Only https:// URLs from GitHub, GitLab, or Bitbucket are allowed.")

    tmpdir = tempfile.mkdtemp(prefix="rag_repo_")
    try:
        cmd = ["git", "clone", "--depth", "1"]
        if request.branch:
            cmd += ["--branch", request.branch]
        cmd += [url, tmpdir]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            raise HTTPException(status_code=422, detail=f"git clone failed: {result.stderr.strip()}")

        # Derive a display name from the URL (last path segment, strip .git)
        repo_name = url.rstrip("/").split("/")[-1].removesuffix(".git")
        count = rag.index_directory(tmpdir, request.extensions, repository=repo_name)
        _register_repo(repo_name, url, count)
        return {"indexed_chunks": count, "repository": repo_name, "url": url}
    except HTTPException:
        raise
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="git clone timed out (120s).")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


@app.post("/index/files")
async def index_files(request: IndexFilesRequest):
    """Index files from request body."""
    try:
        count = rag.index_files(request.files, repository=request.repository)
        if request.repository:
            _register_repo(request.repository, "", count)
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
            request.filter_language,
            request.filter_repository,
            request.search_mode,
            request.enable_reranking,
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

        return {"retrieval": retrieval_metrics, "generation": generation_metrics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/repos")
async def list_repos():
    """List all indexed repositories."""
    return {"repos": list(_repo_registry.values())}


@app.get("/stats")
async def get_stats():
    """Get index statistics."""
    return rag.get_stats()


@app.get("/cache/stats")
async def cache_stats():
    """Get query cache statistics."""
    from rag.cache import CACHE_ENABLED, query_cache

    return {
        "enabled": CACHE_ENABLED,
        "hits": query_cache.hits,
        "misses": query_cache.misses,
        "size": query_cache.size,
        "max_size": query_cache.max_size,
        "ttl_seconds": int(query_cache.ttl),
    }


@app.delete("/cache")
async def clear_cache():
    """Clear the query cache without affecting the index."""
    from rag.cache import query_cache

    previous = query_cache.clear()
    return {"cleared": True, "previous_size": previous}


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
