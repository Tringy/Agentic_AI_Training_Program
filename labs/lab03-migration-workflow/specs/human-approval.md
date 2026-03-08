# Feature: Human Approval

## Overview
After the agent finishes the **planning phase**, execution pauses and the API returns
a job ID plus the full migration plan. A human reviewer can inspect each step,
optionally edit step descriptions or reorder steps, then either approve (execution
resumes) or reject (job is discarded). This turns the agent from fully autonomous
into a **human-in-the-loop** workflow.

> **Relationship to other specs**
> - **Rollback Support** (`rollback-support.md`): approval is a pre-execution gate;
>   rollback is a post-execution safety net. Both can coexist — approval prevents bad
>   plans from running, rollback recovers from steps that fail after a plan is approved.
> - **Parallel Execution** (`parallel-execution.md`): if parallel execution is enabled,
>   the approval UI should display the computed wave groupings so the reviewer
>   understands which steps will run simultaneously before approving.
> - **Framework Profiles** (`framework-profiles.md`): profile metadata (descriptions,
>   known migration caveats) can be surfaced in the approval UI as contextual hints
>   beside each step, helping non-expert reviewers make informed decisions.

---

## Functional Requirements

1. `POST /migrate` stops after the planning phase and returns
   `{ job_id, status: "awaiting_approval", plan }` instead of running to completion.
2. `GET /migrate/{job_id}/plan` returns the current plan and job status at any time.
3. `POST /migrate/{job_id}/approve` accepts an optional `updated_plan` body; if
   provided, replaces the agent's plan before resuming execution.
4. `POST /migrate/{job_id}/reject` discards the job and frees its resources; returns
   `{ job_id, status: "rejected" }`.
5. Approved jobs resume execution asynchronously in a background task; the caller
   polls `GET /migrate/{job_id}/status` for completion.
6. Jobs not acted upon within a configurable `APPROVAL_TIMEOUT_SECONDS` (default 3600)
   are automatically rejected and marked `"timed_out"`.
7. An approved job that later encounters an error keeps its `job_id` so the caller can
   call rollback (if that feature is enabled).

---

## Acceptance Criteria

```
GIVEN POST /migrate is called with a valid request
WHEN the planning phase completes
THEN the response must:
  - Have status code 202
  - Return job_id (UUID4), status "awaiting_approval", and the plan list
  - NOT have started execution

GIVEN GET /migrate/{job_id}/plan is called for a waiting job
THEN the response must:
  - Return status "awaiting_approval"
  - Return the full plan with all step fields

GIVEN POST /migrate/{job_id}/approve is called without a body
THEN:
  - Execution must start in a background task
  - Response must return { "job_id": "...", "status": "executing" }

GIVEN POST /migrate/{job_id}/approve is called with an updated_plan body
THEN:
  - The agent must use the updated plan (not the LLM-generated one)
  - Execution must start in a background task

GIVEN POST /migrate/{job_id}/reject is called
THEN:
  - Job must be removed from the store
  - Response must return { "job_id": "...", "status": "rejected" }

GIVEN APPROVAL_TIMEOUT_SECONDS has elapsed since planning completed
WHEN no approve or reject has been called
THEN the job status must change to "timed_out"
```

---

## Job Status Flow

```
POST /migrate
     │
     ▼
  [analysis]──►[planning]──► awaiting_approval
                                   │          │
                              approve        reject
                                 │              │
                                 ▼              ▼
                           [executing]      rejected
                                 │
                        success ─┤─ error
                                 ▼
                            completed / failed
```

---

## Response Schema — `POST /migrate` (202)

```json
{
  "job_id": "uuid",
  "status": "awaiting_approval",
  "plan": [ ...StepResult ]
}
```

## Response Schema — `GET /migrate/{job_id}/status`

```json
{
  "job_id": "uuid",
  "status": "awaiting_approval | executing | completed | failed | rejected | timed_out",
  "phase": "planning | execution | verification | complete",
  "plan_executed": [ ...StepResult ],
  "migrated_files": {},
  "verification": {},
  "errors": []
}
```

---

## State Changes

```python
# state.py additions

class Phase(Enum):
    ...
    AWAITING_APPROVAL = "awaiting_approval"   # new phase between PLANNING and EXECUTION

# Add to MigrationState:
job_id: Optional[str] = None
approved_at: Optional[str] = None    # ISO-8601 timestamp
rejected_at: Optional[str] = None
timed_out: bool = False
```

---

## Files to Add / Update

| File | Change |
|---|---|
| `python/state.py` | Add `AWAITING_APPROVAL` to `Phase`; add `job_id`, `approved_at`, `rejected_at`, `timed_out` to `MigrationState` |
| `python/agent.py` | In `_step()`, after `_plan()` sets `phase = PLANNING → EXECUTION`, intercept and set `phase = AWAITING_APPROVAL` instead; add `resume()` method that sets `phase = EXECUTION` and continues the loop |
| `python/main.py` | Change `POST /migrate` to run analysis + planning only then return 202; add `job_store`; add background task runner; add `GET /migrate/{job_id}/plan`; add `POST /migrate/{job_id}/approve`; add `POST /migrate/{job_id}/reject`; add `GET /migrate/{job_id}/status`; add timeout cleanup via `asyncio` |
| `frontend/app/page.tsx` | After receiving 202, switch to a plan-review view; poll `/migrate/{job_id}/status` every 3 s when status is `executing` |
| `frontend/components/PlanReview.tsx` | NEW – renders each step with description, input files, complexity badge; "Edit" inline for description; drag-to-reorder; "Approve" and "Reject" buttons |
| `frontend/components/MigrationResult.tsx` | Accept `job_id` prop; show `job_id` in the result header for cross-referencing with rollback |
| `frontend/components/types.ts` | Add `ApprovalResponse`, `JobStatusResponse`, `PlanReviewStep` interfaces; add `"awaiting_approval"` to `Phase` union |

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `APPROVAL_TIMEOUT_SECONDS` | `3600` | Seconds before a waiting job is auto-rejected |

---

## Implementation Notes

- Use FastAPI `BackgroundTasks` to run `agent.resume(state)` after approval — this
  keeps the `/approve` response fast while execution continues asynchronously.
- Store the full `MigrationState` in `job_store` (in-memory dict keyed by `job_id`).
  If `rollback-support.md` is also implemented, this is the same store.
- The `updated_plan` body in `/approve` should be a list of `MigrationStep`-compatible
  dicts; validate that all `id` values match the original plan to prevent injection
  of unexpected steps.
- `PlanReview` drag-to-reorder only changes step order, not dependencies — warn the
  user if they move a step before one of its declared dependencies.
- For the timeout, schedule a `asyncio.create_task` when the job enters
  `AWAITING_APPROVAL`, cancelling it on approve/reject.
