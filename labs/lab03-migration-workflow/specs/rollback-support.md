# Feature: Rollback Support

## Overview
Before executing each migration step, the agent takes a snapshot of the current
`migrated_files` and `plan` state. If a step fails — or the user explicitly requests
it — the agent can restore any previous snapshot, returning the project to a known-good
state without re-running the full migration.

> **Relationship to other specs**
> - When **Parallel Execution** (`parallel-execution.md`) is implemented, rollback must
>   restore all files written during the entire parallel wave, not just a single step.
>   The snapshot strategy described here already supports this — take one snapshot per
>   wave rather than per step.
> - When **Human Approval** (`human-approval.md`) is implemented, rollback provides a
>   complementary safety net: the user approves the plan before execution starts, and
>   rollback handles failures after execution has begun.

---

## Functional Requirements

1. Before executing each `MigrationStep`, save a snapshot of `migrated_files` (deep
   copy) and the step index into `MigrationState.snapshots`.
2. If a step fails (status `"failed"` or an unhandled exception), automatically roll
   back to the snapshot taken immediately before that step.
3. Expose `POST /migrate/{job_id}/rollback` to let callers manually roll back to any
   previously recorded snapshot by step index.
4. Expose `GET /migrate/{job_id}/snapshots` to list available snapshots with their
   step index, step description, and timestamp.
5. Record each rollback action in a `rollback_history` list on the state (timestamp,
   from step, to step, reason).
6. After a successful automatic rollback the `phase` must remain `EXECUTION` so the
   caller can retry or abort.
7. Never roll back past step 0 (the initial empty state is always available as
   snapshot index `0`).

---

## Acceptance Criteria

```
GIVEN a migration is in progress and step N fails
WHEN automatic rollback triggers
THEN the state must:
  - Restore migrated_files to the snapshot taken before step N
  - Set step N status to "failed"
  - Append an entry to rollback_history
  - Keep phase as EXECUTION (not COMPLETE or ERROR)
  - NOT remove snapshots for steps 0..N-1

GIVEN GET /migrate/{job_id}/snapshots is called
THEN the response must:
  - Return a list ordered by step_index ascending
  - Each entry has: step_index, step_description, timestamp, files_count

GIVEN POST /migrate/{job_id}/rollback with body { "to_step": 2 }
WHEN the job has a snapshot for step 2
THEN the state must:
  - Restore migrated_files to the step-2 snapshot
  - Set current_step to 2
  - Append an entry to rollback_history with reason "manual"
  - Return the updated plan_executed list

GIVEN POST /migrate/{job_id}/rollback with body { "to_step": 99 }
WHEN no snapshot exists for step 99
THEN the response must:
  - Have status code 404
  - Return { "detail": "No snapshot found for step 99" }
```

---

## State Changes

```python
# state.py additions

@dataclass
class Snapshot:
    step_index: int
    step_description: str
    timestamp: str          # ISO-8601
    migrated_files: Dict[str, str]  # deep copy at time of snapshot

@dataclass
class RollbackRecord:
    timestamp: str
    from_step: int
    to_step: int
    reason: str             # "automatic" | "manual"

# Add to MigrationState:
snapshots: List[Snapshot] = field(default_factory=list)
rollback_history: List[RollbackRecord] = field(default_factory=list)
```

---

## Response Schema — `POST /migrate/{job_id}/rollback`

```json
{
  "success": true,
  "rolled_back_to_step": 2,
  "migrated_files_count": 3,
  "plan_executed": [ ...StepResult ]
}
```

---

## Files to Add / Update

| File | Change |
|---|---|
| `python/state.py` | Add `Snapshot` and `RollbackRecord` dataclasses; add `snapshots` and `rollback_history` fields to `MigrationState` |
| `python/agent.py` | In `_execute()`, call `_take_snapshot()` before each step; call `_rollback()` on step failure; add private `_take_snapshot()` and `_rollback()` helper methods |
| `python/main.py` | Add in-memory `job_store: Dict[str, MigrationState]`; store result after `/migrate`; add `GET /migrate/{job_id}/snapshots`; add `POST /migrate/{job_id}/rollback` |
| `frontend/components/MigrationResult.tsx` | Add "Rollback to step N" button beside each completed step; calls `POST /migrate/{job_id}/rollback` and refreshes result |
| `frontend/components/types.ts` | Add `Snapshot`, `RollbackRecord`, `RollbackResponse` interfaces |
| `frontend/app/page.tsx` | Thread `job_id` returned from `/migrate` through to `MigrationResult` |

---

## Implementation Notes

- `_take_snapshot()` must perform a **deep copy** of `migrated_files` — a shallow
  reference will be mutated by subsequent steps.
- The `job_store` in `main.py` is an in-memory dict keyed by `job_id` (UUID4). Add
  `job_id: Optional[str]` to `MigrationResponse` so the frontend can reference it.
- For automatic rollback, catch exceptions inside the per-step loop in `_execute()`
  rather than letting them propagate; set `step.status = "failed"`, call `_rollback()`,
  append to `errors`, and break the loop.
- Keep snapshot storage lightweight: store only `migrated_files`, not the full
  `MigrationState`, to avoid unbounded memory growth on large migrations.
