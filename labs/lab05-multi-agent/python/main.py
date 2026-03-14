"""Multi-agent API."""

import asyncio
import json
import os
import re
from contextlib import asynccontextmanager
from typing import Dict, List, Optional

from agent_registry import AgentDefinition, init_agents_table, registry
from agents import RESEARCHER_PROMPT, REVIEWER_PROMPT, WRITER_PROMPT
from agents import AgentTraceEntry as _AgentTraceEntry
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from job_store import Job, job_store
from llm_client import get_llm_client
from memory_store import MEMORY_TOP_K, delete_all_memory, init_db, list_memory, load_memory, save_memory
from prompts import build_summariser_message
from pydantic import BaseModel, Field
from supervisor import SupervisorAgent

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    init_agents_table()
    # Register built-in agents
    registry.register(
        AgentDefinition(
            name="Researcher",
            system_prompt=RESEARCHER_PROMPT,
            description="Finds and summarizes information on a topic",
            builtin=True,
        )
    )
    registry.register(
        AgentDefinition(
            name="Writer",
            system_prompt=WRITER_PROMPT,
            description="Creates polished content from research",
            builtin=True,
        )
    )
    registry.register(
        AgentDefinition(
            name="Reviewer",
            system_prompt=REVIEWER_PROMPT,
            description="Reviews content for quality and accuracy",
            builtin=True,
        )
    )
    # Restore any previously saved custom agents
    registry.load_persisted()
    yield


app = FastAPI(title="Multi-Agent System", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

provider = os.getenv("LLM_PROVIDER", "google")
APPROVAL_TIMEOUT = int(os.getenv("APPROVAL_TIMEOUT_SECONDS", "3600"))
REQUIRE_APPROVAL_GLOBAL = os.getenv("REQUIRE_APPROVAL", "false").lower() == "true"

try:
    llm = get_llm_client(provider)
except Exception as e:
    raise RuntimeError(f"Failed to initialize LLM provider '{provider}': {e}") from e


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------


class TaskRequest(BaseModel):
    task: str = Field(min_length=1)
    max_iterations: int = Field(default=5, ge=1, le=10)
    require_approval: bool = False


class TaskResponse(BaseModel):
    result: str
    steps_taken: int
    memory_context_used: bool = False
    workers_used: List[str] = []
    agent_trace: List["AgentTraceResponse"] = []


class AgentTraceResponse(BaseModel):
    agent: str
    parallel_group: int
    duration_ms: int


class MemoryEntry(BaseModel):
    id: int
    task: str
    summary: str
    created_at: str


class MemoryListResponse(BaseModel):
    entries: List[MemoryEntry]
    total: int


class MemoryDeleteResponse(BaseModel):
    deleted: int


class AgentOut(BaseModel):
    name: str
    description: str
    builtin: bool


class AgentsListResponse(BaseModel):
    agents: List[AgentOut]


_AGENT_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9-]{0,31}$")


class AgentCreateRequest(BaseModel):
    name: str = Field(pattern=r"^[A-Za-z][A-Za-z0-9-]{0,31}$")
    system_prompt: str = Field(min_length=1)
    description: str = Field(min_length=1)


class AgentDeleteResponse(BaseModel):
    name: str
    deleted: bool


class JobStartResponse(BaseModel):
    job_id: str
    status: str
    intermediate: Dict[str, str]


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    intermediate: Dict[str, str]
    result: Optional[str] = None
    steps_taken: int
    workers_used: List[str] = []
    agent_trace: List[AgentTraceResponse] = []


class ApproveRequest(BaseModel):
    override_task: Optional[str] = None


class ApproveResponse(BaseModel):
    job_id: str
    status: str


class RejectResponse(BaseModel):
    job_id: str
    status: str


# ---------------------------------------------------------------------------
# Background helpers
# ---------------------------------------------------------------------------


async def _run_with_timeout(
    job: Job,
    agent: SupervisorAgent,
    task: str,
    max_iterations: int,
    memory_entries: Optional[List[dict]] = None,
) -> None:
    """Run supervisor with optional approval gate and a timeout watchdog."""

    async def _watchdog():
        await asyncio.sleep(APPROVAL_TIMEOUT)
        if job.status == "awaiting_approval":
            job.status = "timed_out"
            # Cancel the supervisor task so it unblocks
            if job._supervisor_task:
                job._supervisor_task.cancel()

    watchdog = asyncio.create_task(_watchdog())
    try:
        result = await agent.run_async(
            task,
            max_iterations=max_iterations,
            job=job,
            require_approval=True,
            memory_entries=memory_entries or [],
        )
        if job.status not in ("rejected", "timed_out"):
            job.result = result
            job.steps_taken = len(agent.results)
            job.intermediate = dict(agent.results)
            job.workers_used = sorted({k.rsplit("_", 1)[0] for k in agent.results})
            job.agent_trace = agent.agent_trace
            job.status = "completed"
            # Persist a summary so future tasks can use this as memory context
            asyncio.create_task(asyncio.to_thread(_summarise_and_save, task, result))
    except asyncio.CancelledError:
        pass  # rejected — status already set
    finally:
        watchdog.cancel()


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/run", response_model=TaskResponse)
async def run_task(request: TaskRequest):
    """Run a multi-agent task (fully autonomous, no approval gate)."""
    # Load memory context
    mem_entries = await asyncio.to_thread(load_memory, MEMORY_TOP_K)
    memory_context_used = len(mem_entries) > 0

    agent = SupervisorAgent(llm, registry)
    result = await agent.run_async(
        request.task,
        request.max_iterations,
        memory_entries=mem_entries,
    )

    # Persist a summary of the completed task
    await asyncio.to_thread(_summarise_and_save, request.task, result)

    workers_used = list({k.rsplit("_", 1)[0] for k in agent.results})
    trace = [AgentTraceResponse(agent=e.agent, parallel_group=e.parallel_group, duration_ms=e.duration_ms) for e in agent.agent_trace]
    return TaskResponse(
        result=result,
        steps_taken=len(agent.results),
        memory_context_used=memory_context_used,
        workers_used=sorted(workers_used),
        agent_trace=trace,
    )


def _summarise_and_save(task: str, result: str) -> None:
    """Call the LLM to summarise the result then store it in memory."""
    try:
        messages = build_summariser_message(task, result)
        raw = llm.chat(messages)
        # Strip markdown fences
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
        data = json.loads(cleaned)
        summary = data["summary"]
    except Exception:
        # Fallback: store raw result truncated to 500 chars
        summary = result[:500]
    save_memory(task, summary)


@app.get("/memory", response_model=MemoryListResponse)
async def get_memory():
    """List all memory entries, most recent first."""
    entries = await asyncio.to_thread(list_memory)
    return MemoryListResponse(
        entries=[MemoryEntry(**e) for e in entries],
        total=len(entries),
    )


@app.delete("/memory", response_model=MemoryDeleteResponse)
async def clear_memory():
    """Delete all memory entries."""
    deleted = await asyncio.to_thread(delete_all_memory)
    return MemoryDeleteResponse(deleted=deleted)


@app.post("/run-with-approval", status_code=202, response_model=JobStartResponse)
async def run_task_with_approval(request: TaskRequest):
    """Start a task that pauses after the Researcher phase for human review."""
    job = Job(status="executing")
    job_store[job.job_id] = job

    # Load memory context so the approval path benefits from past tasks too
    mem_entries = await asyncio.to_thread(load_memory, MEMORY_TOP_K)
    agent = SupervisorAgent(llm, registry)

    task = asyncio.create_task(_run_with_timeout(job, agent, request.task, request.max_iterations, mem_entries))
    job._supervisor_task = task

    # Wait until the job either pauses for approval or completes quickly
    for _ in range(60):  # poll up to 3 seconds
        await asyncio.sleep(0.05)
        if job.status in ("awaiting_approval", "completed", "rejected", "timed_out"):
            break

    return JobStartResponse(
        job_id=job.job_id,
        status=job.status,
        intermediate=job.intermediate,
    )


@app.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job(job_id: str):
    """Return current state of a job."""
    job = job_store.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobStatusResponse(
        job_id=job.job_id,
        status=job.status,
        intermediate=job.intermediate,
        result=job.result,
        steps_taken=job.steps_taken,
        workers_used=job.workers_used,
        agent_trace=[AgentTraceResponse(agent=e.agent, parallel_group=e.parallel_group, duration_ms=e.duration_ms) for e in job.agent_trace],
    )


@app.post("/jobs/{job_id}/approve", response_model=ApproveResponse)
async def approve_job(job_id: str, body: ApproveRequest = ApproveRequest()):
    """Resume a paused job, optionally overriding the Writer's task."""
    job = job_store.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != "awaiting_approval":
        raise HTTPException(status_code=409, detail=f"Job is not awaiting approval (status: {job.status})")

    job.approved_override = body.override_task
    job.status = "executing"
    job.resume_event.set()
    return ApproveResponse(job_id=job.job_id, status="executing")


@app.post("/jobs/{job_id}/reject", response_model=RejectResponse)
async def reject_job(job_id: str):
    """Discard a paused job."""
    job = job_store.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != "awaiting_approval":
        raise HTTPException(status_code=409, detail=f"Job is not awaiting approval (status: {job.status})")

    job.status = "rejected"
    if job._supervisor_task:
        job._supervisor_task.cancel()
    return RejectResponse(job_id=job.job_id, status="rejected")


# ---------------------------------------------------------------------------
# Agent registry endpoints
# ---------------------------------------------------------------------------


@app.get("/agents", response_model=AgentsListResponse)
async def list_agents():
    """List all registered agents."""
    return AgentsListResponse(agents=[AgentOut(name=d.name, description=d.description, builtin=d.builtin) for d in registry.list()])


@app.post("/agents", status_code=201, response_model=AgentOut)
async def create_agent(body: AgentCreateRequest):
    """Register a new custom agent."""
    # Case-insensitive duplicate check
    if registry.get_case_insensitive(body.name) is not None:
        raise HTTPException(status_code=409, detail=f"Agent '{body.name}' already exists")
    defn = AgentDefinition(
        name=body.name,
        system_prompt=body.system_prompt,
        description=body.description,
        builtin=False,
    )
    registry.register(defn, persist=True)
    return AgentOut(name=defn.name, description=defn.description, builtin=defn.builtin)


@app.delete("/agents/{name}", response_model=AgentDeleteResponse)
async def delete_agent(name: str):
    """Remove a custom agent. Built-in agents cannot be deleted."""
    try:
        deleted = registry.delete(name)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Agent '{name}' not found")
    if not deleted:
        raise HTTPException(status_code=403, detail=f"Cannot delete built-in agent '{name}'")
    return AgentDeleteResponse(name=name, deleted=True)


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
