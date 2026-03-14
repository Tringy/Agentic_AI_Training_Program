# Agent Memory

## Overview
Currently each call to `POST /run` starts with a blank context — the supervisor and
workers have no knowledge of previous tasks. This feature adds a **persistent memory
store** (SQLite) that saves a summary of each completed task. Before starting a new
run, the supervisor is given the most relevant past results as additional context,
enabling continuity across conversations (e.g., "continue the article you started
earlier").

## Related Specs
| Relationship | Spec file | Why |
|---|---|---|
| depends on | `specs/human-approval.md` | Memory entries are only written after a job reaches "completed" status; do not persist rejected or timed-out jobs |
| extends | `specs/parallel-workers.md` | When parallel workers are active, all agent results from a parallel group are summarised together into a single memory entry |

## API Contract

### `POST /run`
No change to the request shape. Memory context is injected automatically.

**Success response (`200`) — extended:**
```json
{
  "result": "string",
  "steps_taken": 2,
  "memory_context_used": true
}
```

### `GET /memory`
List stored memory entries (most recent first).

**Response (`200`):**
```json
{
  "entries": [
    {
      "id": 1,
      "task": "string — original task prompt",
      "summary": "string — one-paragraph summary of the result",
      "created_at": "ISO-8601 datetime"
    }
  ],
  "total": 1
}
```

### `DELETE /memory`
Clear all memory entries.

**Response (`200`):**
```json
{ "deleted": 3 }
```

**Error responses:**
| Status | Condition |
|--------|-----------|
| 422 | Validation failed |

## Data Model Changes

New SQLite table, stored at `DATABASE_PATH/memory.db`.

```sql
CREATE TABLE IF NOT EXISTS memory (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    task      TEXT    NOT NULL,
    summary   TEXT    NOT NULL,
    created_at TEXT   NOT NULL DEFAULT (datetime('now'))
);
```

`init_db()` creates the file and runs the DDL at startup via FastAPI `lifespan`.

## Configuration
| Env var | Default | Purpose |
|---------|---------|---------|
| `DATABASE_PATH` | `/data` | Directory for `memory.db` |
| `MEMORY_MAX_ENTRIES` | `20` | Maximum entries kept; oldest are pruned when exceeded |
| `MEMORY_TOP_K` | `3` | Number of most-recent entries injected into the supervisor context |

## Behaviour

### Writing memory
1. On successful run completion (`result` returned from `supervisor.run`), call
   `save_memory(task, result)`.
2. `save_memory` asks the LLM to produce a one-paragraph summary of the result (a
   lightweight summariser call — no multi-agent orchestration).
3. Insert `(task, summary, now())` into the `memory` table.
4. If the row count exceeds `MEMORY_MAX_ENTRIES`, delete the oldest rows to stay
   within the limit.

### Reading memory
1. At the start of `supervisor.run`, call `load_memory(top_k=MEMORY_TOP_K)` to fetch
   the `top_k` most recent entries ordered by `created_at DESC`.
2. If entries exist, prepend a `MEMORY CONTEXT` block to the supervisor's first user
   message:
   ```
   MEMORY CONTEXT (previous tasks — use if relevant):
   [1] Task: "..."
       Summary: "..."
   [2] ...

   Current task: {task}
   ```
3. If `load_memory` returns zero entries, the message is unchanged (no `MEMORY
   CONTEXT` block).
4. Set `memory_context_used = len(entries) > 0` in the response.

## LLM Output Schema (summariser call)

```json
{ "summary": "string — one paragraph, max 120 words" }
```

## Parsing Fallback
Strip markdown fences before `json.loads`.
On `JSONDecodeError` or `ValidationError` → store the raw result text truncated to
500 chars instead of failing the whole request.

## Acceptance Criteria

```
GIVEN no previous tasks exist in memory
WHEN POST /run is called
THEN memory_context_used is false
AND the supervisor receives no MEMORY CONTEXT block

GIVEN one completed task exists in memory
WHEN POST /run is called with a related task
THEN memory_context_used is true
AND the supervisor's first message contains a "MEMORY CONTEXT" block with the prior summary

GIVEN MEMORY_TOP_K = 2 and 5 entries exist
WHEN POST /run is called
THEN only the 2 most recent entries appear in the MEMORY CONTEXT block

GIVEN MEMORY_MAX_ENTRIES = 3 and 3 entries already exist
WHEN a new task completes
THEN the oldest entry is deleted
AND the table contains exactly 3 rows

GIVEN GET /memory is called
THEN it returns all entries ordered by most recent first
AND each entry has id, task, summary, and created_at fields

GIVEN DELETE /memory is called
WHEN GET /memory is called afterwards
THEN entries is an empty list and total is 0

GIVEN the summariser LLM call returns malformed JSON
WHEN a task completes
THEN the raw result (truncated to 500 chars) is stored as the summary
AND the POST /run response still returns 200 with the correct result
```

## Out of Scope
- Semantic / vector similarity search over memory (retrieve by relevance, not recency)
- Per-user or per-session memory isolation
- Memory entry editing via the API
- Embedding-based memory pruning (removes least relevant rather than oldest)
