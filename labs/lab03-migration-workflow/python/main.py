"""Migration Workflow Agent - FastAPI Application."""

import asyncio
import os
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import db
from agent import MigrationAgent
from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from profiles import FrameworkProfile, detect_framework, get_profile, register_profile
from pydantic import BaseModel
from state import MigrationState, Phase, RollbackRecord, Snapshot

# Load environment variables
load_dotenv()

from llm_client import get_llm_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()
    job_store.update(db.load_all_jobs())
    yield


app = FastAPI(
    title="Migration Workflow Agent",
    description="Multi-step agent for code migration between frameworks",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job store and timeout tasks
job_store: Dict[str, MigrationState] = {}
timeout_tasks: Dict[str, asyncio.Task] = {}

APPROVAL_TIMEOUT_SECONDS = int(os.getenv("APPROVAL_TIMEOUT_SECONDS", "3600"))


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------


class MigrationRequest(BaseModel):
    source_framework: str
    target_framework: str
    files: Dict[str, str]  # filename -> content
    execution_mode: str = "parallel"  # "parallel" | "sequential"


class StepResult(BaseModel):
    id: int
    description: str
    status: str
    wave_index: int = 0
    dependencies: List[int] = []


class ApprovalPlanResponse(BaseModel):
    """Returned immediately after POST /migrate (HTTP 202)."""

    job_id: str
    status: str  # "awaiting_approval"
    plan: List[StepResult]
    analysis: Optional[Dict[str, Any]] = None


class ApproveRequest(BaseModel):
    updated_plan: Optional[List[Dict[str, Any]]] = None  # optional step-level overrides


class ApproveResponse(BaseModel):
    job_id: str
    status: str  # "executing"


class RejectResponse(BaseModel):
    job_id: str
    status: str  # "rejected"


class JobStatusResponse(BaseModel):
    job_id: str
    status: str  # awaiting_approval | executing | completed | failed | rejected | timed_out
    phase: str
    plan_executed: List[StepResult]
    migrated_files: Dict[str, str]
    verification: Dict[str, Any]
    errors: List[str]


class WaveStep(BaseModel):
    id: int
    description: str
    status: str


class WaveProgress(BaseModel):
    wave_index: int
    steps: List[WaveStep]


class ProgressResponse(BaseModel):
    job_id: str
    phase: str
    execution_mode: str
    waves: List[WaveProgress]


class FrameworkProfileModel(BaseModel):
    name: str
    language: str
    file_extensions: List[str]
    description: str
    migration_notes: List[str]
    idiomatic_patterns: List[str]
    independent_file_types: List[str]


class DetectFrameworkRequest(BaseModel):
    filenames: List[str]
    snippets: Optional[List[str]] = None


class DetectFrameworkResponse(BaseModel):
    detected_source: Optional[str]
    confidence: str
    alternatives: List[str]
    evidence: List[str]


class SnapshotEntry(BaseModel):
    step_index: int
    step_description: str
    timestamp: str
    files_count: int


class SnapshotsResponse(BaseModel):
    job_id: str
    snapshots: List[SnapshotEntry]


class RollbackRequest(BaseModel):
    to_step: int


class RollbackResponse(BaseModel):
    success: bool
    rolled_back_to_step: int
    migrated_files_count: int
    migrated_files: Dict[str, str]
    plan_executed: List[StepResult]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _state_to_status(state: MigrationState) -> str:
    if state.timed_out:
        return "timed_out"
    if state.rejected_at:
        return "rejected"
    if state.phase == Phase.AWAITING_APPROVAL:
        return "awaiting_approval"
    if state.phase == Phase.COMPLETE:
        return "completed" if not state.errors else "failed"
    return "executing"


def _state_to_job_status(state: MigrationState) -> JobStatusResponse:
    return JobStatusResponse(
        job_id=state.job_id or "",
        status=_state_to_status(state),
        phase=state.phase.value,
        plan_executed=[
            StepResult(id=s.id, description=s.description, status=s.status, wave_index=s.wave_index, dependencies=s.dependencies) for s in state.plan
        ],
        migrated_files=state.migrated_files,
        verification=state.verification_result or {},
        errors=state.errors,
    )


async def _timeout_job(job_id: str) -> None:
    await asyncio.sleep(APPROVAL_TIMEOUT_SECONDS)
    state = job_store.get(job_id)
    if state and state.phase == Phase.AWAITING_APPROVAL:
        state.timed_out = True
        state.phase = Phase.COMPLETE
        db.save_job(state)


async def _run_resume(job_id: str, llm_client) -> None:
    state = job_store.get(job_id)
    if not state:
        return
    # Cancel timeout if still pending
    task = timeout_tasks.pop(job_id, None)
    if task:
        task.cancel()
    agent = MigrationAgent(llm_client)
    if state.execution_mode == "parallel":
        updated = await agent.resume_async(state)
    else:
        updated = await asyncio.to_thread(agent.resume, state)
    job_store[job_id] = updated
    db.save_job(updated)


# ---------------------------------------------------------------------------
# Initialize LLM client
# ---------------------------------------------------------------------------

provider = os.getenv("LLM_PROVIDER", "anthropic")
llm = get_llm_client(provider)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.post("/migrate", response_model=ApprovalPlanResponse, status_code=202)
async def migrate(request: MigrationRequest):
    """
    Start a migration job. Runs the Analysis and Planning phases, then stops
    and returns the plan for human review. Returns HTTP 202 Accepted.
    """
    job_id = str(uuid.uuid4())
    state = MigrationState(
        source_framework=request.source_framework,
        target_framework=request.target_framework,
        source_files=request.files,
        job_id=job_id,
        execution_mode=request.execution_mode,
    )

    try:
        agent = MigrationAgent(llm)
        # run() stops at AWAITING_APPROVAL after the planning phase
        result = await asyncio.to_thread(agent.run, state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    if result.errors:
        raise HTTPException(status_code=500, detail="; ".join(result.errors))

    job_store[job_id] = result
    db.save_job(result)

    # Schedule timeout — job is auto-rejected if not approved in time
    loop = asyncio.get_event_loop()
    timeout_tasks[job_id] = loop.create_task(_timeout_job(job_id))

    return ApprovalPlanResponse(
        job_id=job_id,
        status="awaiting_approval",
        plan=[
            StepResult(id=s.id, description=s.description, status=s.status, wave_index=s.wave_index, dependencies=s.dependencies) for s in result.plan
        ],
        analysis=result.analysis,
    )


@app.get("/migrate/{job_id}/plan", response_model=ApprovalPlanResponse)
async def get_plan(job_id: str):
    """Return the current plan for a job that is awaiting approval."""
    state = job_store.get(job_id)
    if not state:
        raise HTTPException(status_code=404, detail="Job not found")
    if state.phase not in (Phase.AWAITING_APPROVAL,):
        raise HTTPException(status_code=409, detail=f"Job is not awaiting approval (phase: {state.phase.value})")
    return ApprovalPlanResponse(
        job_id=job_id,
        status="awaiting_approval",
        plan=[
            StepResult(id=s.id, description=s.description, status=s.status, wave_index=s.wave_index, dependencies=s.dependencies) for s in state.plan
        ],
        analysis=state.analysis,
    )


@app.post("/migrate/{job_id}/approve", response_model=ApproveResponse)
async def approve_plan(job_id: str, body: ApproveRequest, background_tasks: BackgroundTasks):
    """
    Approve the migration plan and start execution. Optionally supply an
    updated_plan list (same structure as plan) to change step descriptions
    before execution begins.
    """
    state = job_store.get(job_id)
    if not state:
        raise HTTPException(status_code=404, detail="Job not found")
    if state.phase != Phase.AWAITING_APPROVAL:
        raise HTTPException(status_code=409, detail=f"Job is not awaiting approval (phase: {state.phase.value})")

    # Apply any plan overrides supplied by the reviewer
    if body.updated_plan:
        step_by_id = {s.id: s for s in state.plan}
        for override in body.updated_plan:
            sid = override.get("id")
            if sid is not None and sid in step_by_id:
                if "description" in override:
                    step_by_id[sid].description = override["description"]

    state.approved_at = datetime.now(timezone.utc).isoformat()
    db.save_job(state)
    background_tasks.add_task(_run_resume, job_id, llm)  # llm is module-level client

    return ApproveResponse(job_id=job_id, status="executing")


@app.post("/migrate/{job_id}/reject", response_model=RejectResponse)
async def reject_plan(job_id: str):
    """Reject the migration plan and discard the job."""
    state = job_store.get(job_id)
    if not state:
        raise HTTPException(status_code=404, detail="Job not found")
    if state.phase != Phase.AWAITING_APPROVAL:
        raise HTTPException(status_code=409, detail=f"Job is not awaiting approval (phase: {state.phase.value})")

    task = timeout_tasks.pop(job_id, None)
    if task:
        task.cancel()

    state.rejected_at = datetime.now(timezone.utc).isoformat()
    state.phase = Phase.COMPLETE  # mark as terminal
    job_store.pop(job_id, None)  # clean up
    db.delete_job(job_id)

    return RejectResponse(job_id=job_id, status="rejected")


@app.get("/migrate/{job_id}/status", response_model=JobStatusResponse)
async def get_status(job_id: str):
    """Poll the status of a migration job."""
    state = job_store.get(job_id)
    if not state:
        raise HTTPException(status_code=404, detail="Job not found")
    return _state_to_job_status(state)


@app.get("/migrate/{job_id}/progress", response_model=ProgressResponse)
async def get_progress(job_id: str):
    """Real-time wave / step progress during execution."""
    state = job_store.get(job_id)
    if not state:
        raise HTTPException(status_code=404, detail="Job not found")

    # Build a wave_index -> steps map from the plan
    wave_map: Dict[int, List[WaveStep]] = {}
    for step in state.plan:
        wave_map.setdefault(step.wave_index, []).append(WaveStep(id=step.id, description=step.description, status=step.status))

    waves = [WaveProgress(wave_index=wi, steps=steps) for wi, steps in sorted(wave_map.items())]

    return ProgressResponse(
        job_id=job_id,
        phase=state.phase.value,
        execution_mode=state.execution_mode,
        waves=waves,
    )


@app.get("/health")
async def health():
    return {"status": "healthy", "provider": provider}


def _profile_to_dict(p) -> dict:
    return {
        "name": p.name,
        "language": p.language,
        "description": p.description,
        "migration_notes": p.migration_notes,
        "file_extensions": p.file_extensions,
        "independent_file_types": p.independent_file_types,
        "idiomatic_patterns": p.idiomatic_patterns,
    }


@app.get("/frameworks")
async def list_frameworks():
    from profiles import PROFILES

    return {"supported": [_profile_to_dict(p) for p in PROFILES.values()]}


@app.post("/frameworks", status_code=201)
async def create_framework(body: FrameworkProfileModel):
    profile = FrameworkProfile(
        name=body.name,
        language=body.language,
        file_extensions=body.file_extensions,
        description=body.description,
        migration_notes=body.migration_notes,
        idiomatic_patterns=body.idiomatic_patterns,
        independent_file_types=body.independent_file_types,
    )
    try:
        register_profile(profile)
    except ValueError as exc:
        msg = str(exc)
        if "already exists" in msg:
            raise HTTPException(status_code=409, detail=f"Profile '{body.name}' already exists") from exc
        raise HTTPException(status_code=422, detail=msg) from exc
    return _profile_to_dict(profile)


@app.post("/detect-framework", response_model=DetectFrameworkResponse)
async def detect_framework_endpoint(body: DetectFrameworkRequest):
    detected, confidence, alternatives, evidence = detect_framework(
        filenames=body.filenames,
        snippets=body.snippets,
    )
    return DetectFrameworkResponse(
        detected_source=detected,
        confidence=confidence,
        alternatives=alternatives,
        evidence=evidence,
    )


@app.get("/migrate/{job_id}/snapshots", response_model=SnapshotsResponse)
async def list_snapshots(job_id: str):
    """Return all recorded snapshots for a job, ordered by step_index ascending."""
    state = job_store.get(job_id)
    if not state:
        raise HTTPException(status_code=404, detail="Job not found")
    entries = [
        SnapshotEntry(
            step_index=s.step_index,
            step_description=s.step_description,
            timestamp=s.timestamp,
            files_count=len(s.migrated_files),
        )
        for s in sorted(state.snapshots, key=lambda x: x.step_index)
    ]
    return SnapshotsResponse(job_id=job_id, snapshots=entries)


@app.post("/migrate/{job_id}/rollback", response_model=RollbackResponse)
async def rollback_job(job_id: str, body: RollbackRequest):
    """Manually roll back a job to the snapshot taken before the given step."""
    state = job_store.get(job_id)
    if not state:
        raise HTTPException(status_code=404, detail="Job not found")

    snapshot = next((s for s in reversed(state.snapshots) if s.step_index == body.to_step), None)
    if snapshot is None:
        raise HTTPException(status_code=404, detail=f"No snapshot found for step {body.to_step}")

    import copy
    from datetime import datetime, timezone

    from state import RollbackRecord

    from_step = state.current_step
    state.rollback_history.append(
        RollbackRecord(
            timestamp=datetime.now(timezone.utc).isoformat(),
            from_step=from_step,
            to_step=body.to_step,
            reason="manual",
        )
    )
    state.migrated_files = copy.deepcopy(snapshot.migrated_files)
    state.current_step = body.to_step
    # Reset statuses of steps at or after the rollback target back to pending
    for s in state.plan:
        if s.id >= body.to_step:
            s.status = "pending"
    db.save_job(state)

    return RollbackResponse(
        success=True,
        rolled_back_to_step=body.to_step,
        migrated_files_count=len(state.migrated_files),
        migrated_files=state.migrated_files,
        plan_executed=[
            StepResult(
                id=s.id,
                description=s.description,
                status=s.status,
                wave_index=s.wave_index,
                dependencies=s.dependencies,
            )
            for s in state.plan
        ],
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
