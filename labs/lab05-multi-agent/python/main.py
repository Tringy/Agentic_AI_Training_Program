"""Multi-agent API."""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supervisor import SupervisorAgent
from llm_client import get_llm_client

app = FastAPI(title="Multi-Agent System")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize
provider = os.getenv("LLM_PROVIDER", "anthropic")
llm = get_llm_client(provider)
supervisor = SupervisorAgent(llm)


class TaskRequest(BaseModel):
    task: str
    max_iterations: int = 5


class TaskResponse(BaseModel):
    result: str
    steps_taken: int


@app.post("/run", response_model=TaskResponse)
async def run_task(request: TaskRequest):
    """Run a multi-agent task."""
    # Reset for new task
    supervisor.results = {}

    result = supervisor.run(request.task, request.max_iterations)

    return TaskResponse(
        result=result,
        steps_taken=len(supervisor.results)
    )


@app.get("/health")
async def health():
    return {"status": "healthy", "provider": provider}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
