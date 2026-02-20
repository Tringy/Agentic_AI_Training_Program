"""Migration Workflow Agent - FastAPI Application."""
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any
from dotenv import load_dotenv

from agent import MigrationAgent
from state import MigrationState

# Load environment variables
load_dotenv()

# Import LLM client from lab02 or create locally
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lab02-code-analyzer-agent/python'))
from llm_client import get_llm_client

app = FastAPI(
    title="Migration Workflow Agent",
    description="Multi-step agent for code migration between frameworks",
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


class MigrationRequest(BaseModel):
    """Request body for migration."""
    source_framework: str
    target_framework: str
    files: Dict[str, str]  # filename -> content


class StepResult(BaseModel):
    """Result of a migration step."""
    id: int
    description: str
    status: str


class MigrationResponse(BaseModel):
    """Response from migration."""
    success: bool
    migrated_files: Dict[str, str]
    plan_executed: List[StepResult]
    verification: Dict[str, Any]
    errors: List[str]


# Initialize LLM client
provider = os.getenv("LLM_PROVIDER", "anthropic")
llm = get_llm_client(provider)


@app.post("/migrate", response_model=MigrationResponse)
async def migrate(request: MigrationRequest):
    """Run migration workflow."""
    agent = MigrationAgent(llm)

    state = MigrationState(
        source_framework=request.source_framework,
        target_framework=request.target_framework,
        source_files=request.files
    )

    try:
        result = agent.run(state)

        return MigrationResponse(
            success=len(result.errors) == 0,
            migrated_files=result.migrated_files,
            plan_executed=[
                StepResult(id=s.id, description=s.description, status=s.status)
                for s in result.plan
            ],
            verification=result.verification_result or {},
            errors=result.errors
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "provider": provider}


@app.get("/frameworks")
async def list_frameworks():
    """List supported frameworks."""
    return {
        "supported": [
            {"name": "express", "language": "javascript"},
            {"name": "fastapi", "language": "python"},
            {"name": "flask", "language": "python"},
            {"name": "django", "language": "python"},
            {"name": "nestjs", "language": "typescript"},
            {"name": "hono", "language": "typescript"},
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
