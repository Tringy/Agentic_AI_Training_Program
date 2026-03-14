# Parallel Workers

## Overview
When the supervisor delegates multiple independent tasks (e.g., Researcher and a
secondary Fact-Checker that do not depend on each other), executing them sequentially
wastes time. This feature allows the supervisor to issue a `PARALLEL_DELEGATE` block
listing multiple agents, and the system runs them concurrently via `asyncio.gather`,
feeding all results back to the supervisor in a single message.

## Related Specs
| Relationship | Spec file | Why |
|---|---|---|
| required by | `specs/human-approval.md` | Human approval should display which agents ran in parallel before the user reviews |
| required by | `specs/memory.md` | Per-task memory entries are written after each worker completes; parallel runs write concurrently |

## API Contract

No new endpoints. The existing `POST /run` endpoint drives the workflow.
The `TaskResponse` gains an optional `agent_trace` field:

**Success response (`200`):**
```json
{
  "result": "string — final synthesized output",
  "steps_taken": 3,
  "agent_trace": [
    { "agent": "Researcher", "parallel_group": 0, "duration_ms": 1240 },
    { "agent": "Fact-Checker", "parallel_group": 0, "duration_ms": 980 },
    { "agent": "Writer", "parallel_group": 1, "duration_ms": 1100 }
  ]
}
```

## Data Model Changes
No persistence changes. `agent_trace` is computed in-memory during the run and
returned in the response only.

```python
# agents.py — new dataclass
@dataclass
class AgentTraceEntry:
    agent: str
    parallel_group: int
    duration_ms: int
```

## Configuration
| Env var | Default | Purpose |
|---------|---------|---------|
| `MAX_PARALLEL_WORKERS` | `4` | Cap on concurrent worker calls per parallel group |

## Behaviour

1. The supervisor prompt is extended to support a second delegation syntax for
   parallel work:
   ```
   PARALLEL_DELEGATE: Researcher, Fact-Checker
   TASK_Researcher: Gather key facts about vector databases
   TASK_Fact-Checker: Verify the following claims: ...
   ```
2. The supervisor parser detects `PARALLEL_DELEGATE:` and extracts the comma-separated
   agent names and their individual `TASK_{AgentName}:` lines.
3. All named agents are invoked concurrently using `asyncio.gather` with a semaphore
   capped at `MAX_PARALLEL_WORKERS`.
4. Each agent receives the current shared context (all previous results) plus its own
   task string.
5. All results are stored in `self.results` keyed `{AgentName}_{iteration}` and
   combined into a single message fed back to the supervisor:
   ```
   Results from parallel group {n}:
   --- Researcher ---
   {result}
   --- Fact-Checker ---
   {result}
   ```
6. The original single `DELEGATE:` syntax continues to work unchanged.
7. Duration for each agent is measured with `time.monotonic` and included in
   `agent_trace`.

## Acceptance Criteria

```
GIVEN a task where research and fact-checking are independent
WHEN the supervisor issues a PARALLEL_DELEGATE for Researcher and Fact-Checker
THEN both agents must be called concurrently
AND total wall-clock time < time(Researcher) + time(Fact-Checker)
AND both results must appear in the context fed back to the supervisor

GIVEN a PARALLEL_DELEGATE with three agents
WHEN MAX_PARALLEL_WORKERS is set to 2
THEN at most 2 agents run concurrently at any point
AND all 3 complete successfully before the supervisor's next turn

GIVEN a single-agent DELEGATE (the original syntax)
WHEN the supervisor issues DELEGATE: Writer
THEN no parallel behaviour is triggered
AND the response is identical to the current implementation

GIVEN an agent in a parallel group raises an exception
WHEN asyncio.gather runs
THEN the error is caught, stored as the agent's result with an error prefix
AND the supervisor is notified so it can decide whether to retry or proceed

GIVEN a completed run
WHEN the POST /run response is returned
THEN agent_trace lists every agent called with its parallel_group index and duration_ms
```

## Out of Scope
- Dynamic worker pool scaling
- Streaming partial results to the client during execution
- Cancelling in-flight parallel workers if the supervisor later decides they are unneeded
