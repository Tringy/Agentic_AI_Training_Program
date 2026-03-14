# Human Approval

## Overview
After the supervisor has gathered research and produced a draft, execution pauses and
the caller is returned a `job_id` plus the current agent results. A human reviewer
inspects the intermediate work, optionally edits the task passed to the next agent,
then either approves (workflow resumes with the next delegation) or rejects (job is
discarded). This converts the fully-autonomous pipeline into a **human-in-the-loop**
workflow for high-stakes outputs.

## Related Specs
| Relationship | Spec file | Why |
|---|---|---|
| depends on | `specs/parallel-workers.md` | When parallel workers are enabled, the approval payload must include the full agent_trace so the reviewer sees what ran in parallel |
| required by | `specs/memory.md` | Memory entries for a job should only be persisted after the job is approved and completed |

## API Contract

### `POST /run`
Unchanged request shape. When the task includes the phrase `"review before writing"`
(or `require_approval=true` is passed), the job pauses after the Researcher phase.

**Response when paused (`202`):**
```json
{
  "job_id": "string — UUID4",
  "status": "awaiting_approval",
  "intermediate": {
    "Researcher_0": "string — researcher output"
  }
}
```

### `GET /jobs/{job_id}`
Returns current job state at any time.

**Response (`200`):**
```json
{
  "job_id": "string",
  "status": "awaiting_approval | executing | completed | rejected | timed_out",
  "intermediate": { "AgentName_step": "result" },
  "result": "string — present only when status is completed",
  "steps_taken": 0
}
```

### `POST /jobs/{job_id}/approve`
Resumes execution. Optionally overrides the next task.

**Request:**
```json
{
  "override_task": "string — optional; replaces the Writer's task if provided"
}
```

**Response (`200`):**
```json
{ "job_id": "string", "status": "executing" }
```

### `POST /jobs/{job_id}/reject`
Discards the job.

**Response (`200`):**
```json
{ "job_id": "string", "status": "rejected" }
```

**Error responses:**
| Status | Condition |
|--------|-----------|
| 404 | `job_id` not found |
| 409 | Job is not in `awaiting_approval` state |
| 422 | Validation failed |

## Data Model Changes

In-memory job store (dict keyed by `job_id`). No SQLite — jobs are ephemeral.

```python
# job_store.py
from dataclasses import dataclass, field
from typing import Dict, Optional
import uuid, asyncio

@dataclass
class Job:
    job_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: str = "awaiting_approval"   # awaiting_approval | executing | completed | rejected | timed_out
    intermediate: Dict[str, str] = field(default_factory=dict)
    result: Optional[str] = None
    steps_taken: int = 0
    resume_event: asyncio.Event = field(default_factory=asyncio.Event)
    approved_override: Optional[str] = None

job_store: Dict[str, Job] = {}
```

## Configuration
| Env var | Default | Purpose |
|---------|---------|---------|
| `APPROVAL_TIMEOUT_SECONDS` | `3600` | Jobs not approved/rejected within this window are auto-rejected |
| `REQUIRE_APPROVAL` | `false` | Global flag; when `true`, all jobs pause for approval |

## Behaviour

1. `POST /run` creates a `Job`, stores it in `job_store`, and starts the supervisor
   in a background `asyncio.Task`.
2. The supervisor runs normally until it has at least one result (Researcher phase
   complete). It then checks `require_approval`; if `true`, it sets
   `job.status = "awaiting_approval"` and awaits `job.resume_event`.
3. The background task's `await` unblocks only when `POST /jobs/{job_id}/approve`
   is called, which sets `job.resume_event`.
4. If `override_task` is provided in the approve body, it is injected as the Writer's
   task on resume.
5. A background timeout task runs alongside the supervisor; if
   `APPROVAL_TIMEOUT_SECONDS` elapses without an event, status is set to `"timed_out"`
   and the resume event is never set.
6. `POST /jobs/{job_id}/reject` sets status to `"rejected"` and cancels the background
   supervisor task.
7. On completion, `job.result`, `job.steps_taken`, and `job.status = "completed"` are
   updated; `GET /jobs/{job_id}` reflects this.

## Acceptance Criteria

```
GIVEN POST /run is called with require_approval=true
WHEN the Researcher phase completes
THEN the response must be 202 with status "awaiting_approval" and intermediate results
AND execution must NOT have proceeded to the Writer

GIVEN a job in "awaiting_approval" status
WHEN GET /jobs/{job_id} is called
THEN status is "awaiting_approval" and intermediate contains at least one entry

GIVEN POST /jobs/{job_id}/approve is called without override_task
WHEN the supervisor resumes
THEN the Writer receives the supervisor's original planned task
AND GET /jobs/{job_id} eventually returns status "completed" with a non-empty result

GIVEN POST /jobs/{job_id}/approve is called with override_task = "Write a formal summary"
WHEN the Writer executes
THEN the Writer's task is "Write a formal summary" not the supervisor's original plan

GIVEN POST /jobs/{job_id}/reject is called
THEN GET /jobs/{job_id} returns status "rejected"
AND no further LLM calls are made for that job

GIVEN APPROVAL_TIMEOUT_SECONDS = 5 (test override)
WHEN no approve or reject is called within 5 seconds
THEN GET /jobs/{job_id} returns status "timed_out"

GIVEN a job_id that does not exist
WHEN POST /jobs/{job_id}/approve is called
THEN the response is 404
```

## Out of Scope
- Persistent job storage across server restarts
- Email / webhook notifications when a job awaits approval
- Multiple approval gates within a single run
- Frontend UI for the approval flow (consumed via the API directly)
