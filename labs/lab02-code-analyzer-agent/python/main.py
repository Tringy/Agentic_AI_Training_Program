"""Code Analyzer Agent - FastAPI Application."""

import json
import os
from typing import Annotated, List

from analyzer import AnalysisResult, CodeAnalyzer, DetectionResult, DiffResult, FileInput, MultiFileResult
from cache import AnalysisCache
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from llm_client import get_llm_client
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

app = FastAPI(title="Code Analyzer Agent", description="LLM-powered code analysis API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    """Request body for code analysis."""

    code: str
    language: str = "python"


class MultiAnalyzeRequest(BaseModel):
    """Request body for multi-file code analysis (2–10 files)."""

    files: Annotated[List[FileInput], Field(min_length=2, max_length=10)]


class DiffAnalyzeRequest(BaseModel):
    """Request body for diff analysis between two code versions."""

    before: str
    after: str
    language: str = "python"


class DetectRequest(BaseModel):
    """Request body for language detection."""

    code: str


# Initialize analyzer with configured provider
provider = os.getenv("LLM_PROVIDER", "google")

try:
    llm = get_llm_client(provider)
    analyzer = CodeAnalyzer(llm)
except Exception as e:
    raise RuntimeError(f"Failed to initialize LLM provider '{provider}': {str(e)}") from e

# Module-level cache instance
cache = AnalysisCache()


@app.post("/detect-language", response_model=DetectionResult)
async def detect_language(request: DetectRequest):
    """Detect the programming language of the submitted code."""
    try:
        result = analyzer.detect_language(request.code)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/analyze", response_model=AnalysisResult)
async def analyze_code(request: AnalyzeRequest, response: Response):
    """Analyze code and return structured feedback."""
    try:
        language = request.language
        if language == "auto":
            detected = analyzer.detect_language(request.code)
            language = detected.language
        cached = cache.get("general", language, request.code)
        if cached is not None:
            response.headers["X-Cache"] = "HIT"
            return cached
        result = analyzer.analyze(request.code, language)
        cache.set("general", language, request.code, result.model_dump())
        response.headers["X-Cache"] = "MISS"
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/analyze/security", response_model=AnalysisResult)
async def analyze_security(request: AnalyzeRequest, response: Response):
    """Security-focused code analysis."""
    try:
        language = request.language
        if language == "auto":
            detected = analyzer.detect_language(request.code)
            language = detected.language
        cached = cache.get("security", language, request.code)
        if cached is not None:
            response.headers["X-Cache"] = "HIT"
            return cached
        result = analyzer.analyze_security(request.code, language)
        cache.set("security", language, request.code, result.model_dump())
        response.headers["X-Cache"] = "MISS"
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/analyze/performance", response_model=AnalysisResult)
async def analyze_performance(request: AnalyzeRequest, response: Response):
    """Performance-focused code analysis."""
    try:
        language = request.language
        if language == "auto":
            detected = analyzer.detect_language(request.code)
            language = detected.language
        cached = cache.get("performance", language, request.code)
        if cached is not None:
            response.headers["X-Cache"] = "HIT"
            return cached
        result = analyzer.analyze_performance(request.code, language)
        cache.set("performance", language, request.code, result.model_dump())
        response.headers["X-Cache"] = "MISS"
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/analyze/multi", response_model=MultiFileResult)
async def analyze_multi(request: MultiAnalyzeRequest, response: Response):
    """Analyze 2–10 files and return per-file results plus cross-file relationships."""
    try:
        # Build a stable, order-preserving payload for cache keying
        payload = json.dumps(
            [f.model_dump() for f in request.files],
            sort_keys=True,
        )
        cached = cache.get_multi(payload)
        if cached is not None:
            response.headers["X-Cache"] = "HIT"
            return cached
        result = analyzer.analyze_multi(request.files)
        cache.set_multi(payload, result.model_dump())
        response.headers["X-Cache"] = "MISS"
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/analyze/diff", response_model=DiffResult)
async def analyze_diff(request: DiffAnalyzeRequest):
    """Compare two code versions and return introduced/resolved issues and regression risks."""
    try:
        language = request.language
        if language == "auto":
            detected = analyzer.detect_language(request.before)
            language = detected.language
        result = analyzer.analyze_diff(request.before, request.after, language)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/cache/stats")
async def cache_stats():
    """Return cache statistics: total, alive, and expired entry counts."""
    return cache.stats()


@app.delete("/cache")
async def clear_cache():
    """Clear all cached entries and return the number removed."""
    cleared = cache.clear()
    return {"cleared": cleared}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "provider": provider}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
