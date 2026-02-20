"""Code Analyzer Agent - FastAPI Application."""
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from analyzer import CodeAnalyzer, AnalysisResult
from llm_client import get_llm_client

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Code Analyzer Agent",
    description="LLM-powered code analysis API",
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


class AnalyzeRequest(BaseModel):
    """Request body for code analysis."""
    code: str
    language: str = "python"


# Initialize analyzer with configured provider
provider = os.getenv("LLM_PROVIDER", "anthropic")
llm = get_llm_client(provider)
analyzer = CodeAnalyzer(llm)


@app.post("/analyze", response_model=AnalysisResult)
async def analyze_code(request: AnalyzeRequest):
    """Analyze code and return structured feedback."""
    try:
        result = analyzer.analyze(request.code, request.language)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/security", response_model=AnalysisResult)
async def analyze_security(request: AnalyzeRequest):
    """Security-focused code analysis."""
    try:
        result = analyzer.analyze_security(request.code, request.language)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/performance", response_model=AnalysisResult)
async def analyze_performance(request: AnalyzeRequest):
    """Performance-focused code analysis."""
    try:
        result = analyzer.analyze_performance(request.code, request.language)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "provider": provider}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
