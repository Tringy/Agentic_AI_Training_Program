# Feature: Parallel Execution

## Overview
The migration planner already asks the LLM to record `dependencies` per step. This
feature uses those dependency declarations to group steps into **execution waves** —
sets of steps that share no dependencies — and runs each wave concurrently using
`asyncio.gather`. Steps that depend on earlier steps still execute in order, but
within a wave every step runs at the same time.

> **Relationship to other specs**
> - **Rollback Support** (`rollback-support.md`): when both features are active, take
>   one snapshot per wave (before the wave starts) rather than per step. Rolling back
>   restores the state to before that wave; all steps in the wave revert together.
> - **Human Approval** (`human-approval.md`): when both are active, the user reviews and
>   approves the plan (including the computed wave groupings) before the first wave
>   executes. Display the wave layout in the approval UI so the user understands which
>   steps will run simultaneously.
> - **Framework Profiles** (`framework-profiles.md`): profiles that declare file-type
>   independence hints (e.g., "route files never depend on middleware files") can be
>   used to pre-populate the dependency graph before the LLM planning call, reducing
>   the chance of unnecessary serialisation.

---

## Functional Requirements

1. After the planning phase, build a **dependency graph** from
   `MigrationStep.dependencies` (list of step IDs that must complete first).
2. Partition the plan into ordered waves using a topological sort; steps with no
   unfulfilled dependencies form wave 1, then wave 2, and so on.
3. Execute all steps within a wave concurrently via `asyncio.gather`.
4. A step may only start when every step it depends on has status `"completed"`.
5. If any step in a wave fails, abort the remaining steps in that wave and stop
   execution (do not proceed to subsequent waves).
6. Record `wave_index` on each `MigrationStep` so the frontend can group and display
   them.
7. Add `execution_mode: "sequential" | "parallel"` to the migration request so callers
   can opt out of parallelism (default `"parallel"`).
8. Expose `GET /migrate/{job_id}/progress` with real-time step statuses so the
   frontend can poll during execution.

---

## Acceptance Criteria

```
GIVEN a plan where steps 1 and 2 have no dependencies and step 3 depends on both
WHEN POST /migrate is called with execution_mode "parallel"
THEN:
  - Steps 1 and 2 must execute concurrently (wave 1)
  - Step 3 must start only after both steps 1 and 2 are "completed" (wave 2)
  - Total wall-clock time < time(step 1) + time(step 2) + time(step 3)

GIVEN a plan where all steps depend sequentially on the previous
WHEN POST /migrate is called with execution_mode "parallel"
THEN:
  - Each step runs in its own wave (effective sequential behaviour)
  - No concurrency errors occur

GIVEN execution_mode is "sequential"
WHEN POST /migrate is called
THEN:
  - Steps execute one at a time in plan order
  - wave_index is set to the step's position index

GIVEN step 2 fails during wave execution
WHEN POST /migrate is called
THEN:
  - Steps in the same wave that have not yet started are cancelled
  - Subsequent waves do not execute
  - Response errors list contains the failure reason
```

---

## State Changes

```python
# state.py additions

# Add to MigrationStep:
dependencies: List[int] = field(default_factory=list)  # step IDs that must finish first
wave_index: int = 0  # set during execution planning

# Add to MigrationState:
execution_mode: str = "parallel"      # "parallel" | "sequential"
waves: List[List[int]] = field(default_factory=list)   # [[step_ids], ...] per wave
```

---

## Response Schema — `GET /migrate/{job_id}/progress`

```json
{
  "job_id": "uuid",
  "phase": "execution",
  "waves": [
    {
      "wave_index": 0,
      "steps": [
        { "id": 1, "description": "...", "status": "completed" },
        { "id": 2, "description": "...", "status": "completed" }
      ]
    },
    {
      "wave_index": 1,
      "steps": [
        { "id": 3, "description": "...", "status": "in_progress" }
      ]
    }
  ]
}
```

---

## Files to Add / Update

| File | Change |
|---|---|
| `python/state.py` | Add `dependencies` and `wave_index` fields to `MigrationStep`; add `execution_mode` and `waves` to `MigrationState` |
| `python/agent.py` | Add `_build_waves()` (topological sort); replace serial loop in `_execute()` with `_execute_parallel()` that calls `asyncio.gather` per wave; convert `_execute_step()` to an `async` coroutine |
| `python/prompts.py` | Update `PLANNING_PROMPT` to require `"dependencies": [step_ids]` in each step object (already partially present); add instruction to minimise unnecessary dependencies |
| `python/main.py` | Add `execution_mode` field to `MigrationRequest`; add `GET /migrate/{job_id}/progress` endpoint that reads from `job_store` |
| `frontend/components/MigrationResult.tsx` | Group plan steps by `wave_index`; label each group "Wave N (parallel)"; poll `GET /migrate/{job_id}/progress` every 2 s while phase is `execution` |
| `frontend/components/types.ts` | Add `wave_index` to `StepResult`; add `WaveProgress` and `ProgressResponse` interfaces |

---

## Implementation Notes

- `_build_waves()` implements **Kahn's algorithm**: start with steps whose
  `dependencies` list is empty, add them to wave 0, remove their IDs from all
  remaining dependency lists, repeat until the queue is empty. Raise `ValueError`
  if a cycle is detected.
- `_execute_parallel()` should convert each step coroutine via
  `asyncio.ensure_future` and collect results with `asyncio.gather(return_exceptions=True)`.
  Inspect results for exceptions before writing to `migrated_files`.
- The LLM migration call inside `_execute_step()` is I/O-bound and benefits from
  `async` even when the underlying HTTP client is synchronous — wrap it with
  `asyncio.to_thread()` if the client is blocking.
- When `execution_mode` is `"sequential"`, set every step's `wave_index` to its
  position in the plan and run the existing serial loop unchanged.
- The `job_store` introduced in `rollback-support.md` can be reused here; if that
  spec is not implemented, add a minimal version of `job_store` locally.
