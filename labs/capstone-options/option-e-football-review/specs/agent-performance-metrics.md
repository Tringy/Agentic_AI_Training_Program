# Agent Performance Metrics

## Overview
Add explicit per-agent performance metrics to review and follow-up responses so the system reports both time taken and token usage for each specialist and for synthesis. The backend captures these metrics during orchestration, and the frontend displays them in a compact metrics panel so users can compare cost and runtime across agents, formats, and depth settings.

## Related Specs
| Relationship | Spec file | Why |
|---|---|---|
| extends | `specs/conversation-history-and-metrics.md` | Reuses the existing trace/timing structure and adds richer per-agent metrics |
| depends on | `specs/configurable-depth.md` | Depth and max_iterations change token budgets and which agents execute |
| extends | `specs/report-formats.md` | Format selection affects synthesis token usage and should be reflected in metrics |

## API Contract

### `POST /games/{game_id}/review`

**Success response (200) — additions only:**
```json
{
  "metadata": {
    "iterations": 4,
    "max_iterations": 4,
    "duration_seconds": 8.91,
    "agent_timings": {
      "Journalist": 1412,
      "Coach": 1364,
      "AssistantCoach": 1498,
      "Fan": 1180,
      "Synthesis": 2107
    },
    "agent_metrics": {
      "Journalist": {
        "duration_ms": 1412,
        "prompt_tokens": 620,
        "completion_tokens": 124,
        "total_tokens": 744
      },
      "Coach": {
        "duration_ms": 1364,
        "prompt_tokens": 771,
        "completion_tokens": 117,
        "total_tokens": 888
      },
      "AssistantCoach": {
        "duration_ms": 1498,
        "prompt_tokens": 943,
        "completion_tokens": 131,
        "total_tokens": 1074
      },
      "Fan": {
        "duration_ms": 1180,
        "prompt_tokens": 1108,
        "completion_tokens": 82,
        "total_tokens": 1190
      },
      "Synthesis": {
        "duration_ms": 2107,
        "prompt_tokens": 1682,
        "completion_tokens": 166,
        "total_tokens": 1848
      }
    },
    "total_tokens": 5744,
    "total_prompt_tokens": 5124,
    "total_completion_tokens": 620
  }
}
```

### `POST /games/{session_id}/ask`

**Success response (200) — additions only:**
```json
{
  "answer": {
    "summary": "..."
  },
  "metrics": {
    "agent_metrics": {
      "Journalist": {
        "duration_ms": 1290,
        "prompt_tokens": 702,
        "completion_tokens": 118,
        "total_tokens": 820
      },
      "Synthesis": {
        "duration_ms": 1944,
        "prompt_tokens": 1544,
        "completion_tokens": 141,
        "total_tokens": 1685
      }
    },
    "total_tokens": 4460,
    "total_prompt_tokens": 3948,
    "total_completion_tokens": 512
  }
}
```

**Error responses:**
Shared error behaviour remains defined by `specs/error-handling-and-timeout-protection.md`.

## Data Model Changes

### Backend Pydantic
Add reusable models in `python/main.py`:
```python
class AgentMetric(BaseModel):
    duration_ms: int
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class MetricsSummary(BaseModel):
    agent_metrics: Dict[str, AgentMetric]
    total_tokens: int
    total_prompt_tokens: int
    total_completion_tokens: int
```

Update `GameReviewResponse.metadata` to include:
- `agent_metrics`
- `total_tokens`
- `total_prompt_tokens`
- `total_completion_tokens`

### Frontend TypeScript
Add shared types in `frontend/types.ts`:
```ts
export type AgentMetric = {
  duration_ms: number;
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
};

export type MetricsSummary = {
  agent_metrics: Record<string, AgentMetric>;
  total_tokens: number;
  total_prompt_tokens: number;
  total_completion_tokens: number;
};
```

## Configuration
| Env var | Default | Purpose |
|---------|---------|---------|
| `TOKEN_ESTIMATION_CHARS_PER_TOKEN` | `4` | Fallback heuristic when provider usage metadata is unavailable |

## Behaviour
1. During each specialist and synthesis LLM call, the backend records start/end time as already defined in `specs/conversation-history-and-metrics.md`.
2. For each LLM call, the backend captures token usage from provider metadata when available.
3. If provider metadata is unavailable, the backend estimates tokens using a deterministic fallback:
   - `prompt_tokens = ceil(len(prompt_text) / TOKEN_ESTIMATION_CHARS_PER_TOKEN)`
   - `completion_tokens = ceil(len(response_text) / TOKEN_ESTIMATION_CHARS_PER_TOKEN)`
   - `total_tokens = prompt_tokens + completion_tokens`
4. The supervisor stores one metrics record per executed agent plus one for synthesis.
5. `metadata.agent_timings` remains for backward compatibility, but `metadata.agent_metrics` becomes the canonical detailed metrics structure.
6. Aggregate totals are computed by summing per-agent values for prompt, completion, and total tokens.
7. Follow-up responses include a top-level `metrics` block because follow-up responses do not currently reuse the same `metadata` envelope as review creation.
8. The frontend renders:
   - total token summary cards,
   - a per-agent metrics table or grid,
   - duration and token counts for each executed agent only.
9. If `max_iterations` is less than 4, omitted agents do not appear in `agent_metrics` and are not counted in totals.

## Acceptance Criteria
GIVEN a successful `POST /games/game_0/review`
WHEN the response arrives
THEN `metadata.agent_metrics` exists
AND it includes one entry per executed agent plus `Synthesis`.

GIVEN `metadata.agent_metrics.Journalist`
WHEN inspected
THEN it has `duration_ms`, `prompt_tokens`, `completion_tokens`, and `total_tokens`
AND `total_tokens == prompt_tokens + completion_tokens`.

GIVEN a successful review response
WHEN `metadata.total_tokens` is inspected
THEN it equals the sum of all `agent_metrics[*].total_tokens` values.

GIVEN `max_iterations=2`
WHEN a review is created
THEN `metadata.agent_metrics` contains `Journalist`, `Coach`, and `Synthesis`
AND does not contain `AssistantCoach` or `Fan`.

GIVEN a successful `POST /games/{session_id}/ask`
WHEN the response arrives
THEN a top-level `metrics` block is present
AND it contains aggregate token totals and per-agent metrics.

GIVEN the review result screen
WHEN it renders a completed review
THEN it shows total token usage and total duration summary cards
AND it shows a per-agent metrics breakdown including duration and token counts.

## Out of Scope
- Billing or currency cost estimation per provider
- Persisting metrics to a database for historical analytics
- Cross-request dashboards or trend charts
- Exact tokenizer parity across all model providers when usage metadata is unavailable