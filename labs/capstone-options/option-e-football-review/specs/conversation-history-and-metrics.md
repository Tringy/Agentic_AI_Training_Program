# Conversation History & Agent Metrics

## Overview
Expose the supervisor's internal execution trace as `conversation_history` in every `POST /games/{id}/review` response, add per-agent timing to the `metadata` block, and return an explicit `progress` object summarizing workflow completion. The frontend displays the trace as a timeline and the progress object as a compact review-status summary.

## Related Specs
| Relationship | Spec file | Why |
|---|---|---|
| required by | `specs/streaming.md` | Streaming reuses the same trace event structure |
| required by | `specs/configurable-depth.md` | Depth controls how many tokens emit in trace content |

---

## Backend: API Contract

### `POST /games/{game_id}/review` — response changes only

**Success response (200):**
```json
{
  "game_id": "session-uuid",
  "game_review": { /* existing fields */ },
  "specialist_perspectives": { /* existing fields */ },
  "progress": {
    "status": "complete",
    "total_steps": 5,
    "completed_steps": 5,
    "percent_complete": 100,
    "current_step": "complete",
    "planned_steps": ["Journalist", "Coach", "AssistantCoach", "Fan", "Synthesis"],
    "completed_steps_labels": ["Journalist", "Coach", "AssistantCoach", "Fan", "Synthesis"],
    "max_iterations": 4
  },
  "metadata": {
    "game_date": "2026-03-21",
    "home_team": "Manchester United",
    "away_team": "Liverpool",
    "final_score": "2-1",
    "competition": "Premier League",
    "stadium": "Old Trafford",
    "iterations": 4,
    "agents_used": ["Journalist", "Coach", "AssistantCoach", "Fan"],
    "duration_seconds": 9.42,
    "agent_timings": {
      "Journalist": 1820,
      "Coach": 1650,
      "AssistantCoach": 1540,
      "Fan": 1310,
      "Synthesis": 2100
    }
  },
  "conversation_history": [
    {
      "iteration": 0,
      "agent": "Supervisor",
      "action": "DELEGATE",
      "content": "Starting sequential iterative workflow...",
      "duration_ms": 0
    },
    {
      "iteration": 1,
      "agent": "Journalist",
      "action": "RESULT",
      "content": "Manchester United defeated Liverpool 2-1 in a thrilling...",
      "duration_ms": 1820
    },
    {
      "iteration": 2,
      "agent": "Coach",
      "action": "RESULT",
      "content": "United's 4-3-3 formation pressed aggressively...",
      "duration_ms": 1650
    },
    {
      "iteration": 3,
      "agent": "AssistantCoach",
      "action": "RESULT",
      "content": "Rashford's 8.7 rating led the field with direct...",
      "duration_ms": 1540
    },
    {
      "iteration": 4,
      "agent": "Fan",
      "action": "RESULT",
      "content": "What a game! The comeback was incredible, Højlund...",
      "duration_ms": 1310
    },
    {
      "iteration": 5,
      "agent": "Supervisor",
      "action": "SYNTHESIS",
      "content": "Final review synthesized from all specialist perspectives.",
      "duration_ms": 2100
    }
  ]
}
```

---

## Backend: Implementation

### `python/supervisor.py`
1. Import `time` module.
2. In `orchestrate()`:
   - Before each agent call: `t0 = time.time()`
   - After agent returns: `duration_ms = round((time.time() - t0) * 1000)`
   - Append trace entry with `duration_ms` field
3. At end of `orchestrate()`, before return:
   - Build `agent_timings` dict by extracting `duration_ms` from trace for each agent
   - Include in returned JSON: `"conversation_history": self.trace, "agent_timings": {...}`

### `python/main.py`
1. Update `ConversationEntry` Pydantic model:
   ```python
   class ConversationEntry(BaseModel):
       iteration: int
       agent: str
       action: str
       content: Optional[str] = None
       duration_ms: int = 0
   ```
2. In `create_game_review()`:
   - Parse `review_data.get("conversation_history", [])`
   - Pass to `GameReviewResponse(conversation_history=...)`
  - Add `progress=review_data.get("progress", ...)`
   - Extract `agent_timings` from `review_data` and add to `metadata`

### `frontend/types.ts`
Update the shared types:
```typescript
export type ConversationEntry = {
  iteration: number;
  agent: string;
  action: string;
  content?: string;
  duration_ms: number;
};

export type ProgressInfo = {
  status: string;
  total_steps: number;
  completed_steps: number;
  percent_complete: number;
  current_step: string;
  planned_steps: string[];
  completed_steps_labels: string[];
  max_iterations: number;
};
```

---

## Frontend: Components

### `frontend/components/AgentTimeline.tsx` (new)
Display the conversation history as a vertical timeline:
- Left side: agent name + iteration
- Center: vertical line connector
- Right side: action badge + content preview + duration badge
- Styling: use pitch theme, goal-accent for active agents

Props:
```typescript
interface AgentTimelineProps {
  history: ConversationEntry[];
}
```

### `frontend/app/page.tsx`
After `<ReviewResult>` component, add:
```tsx
{reviewResult && (
  <div className="mt-8 pt-8 border-t border-gray-700">
    <h3 className="text-2xl font-bold text-goal-yellow mb-6">
      Agent Workflow Timeline
    </h3>
    <AgentTimeline history={reviewResult.conversation_history} />
  </div>
)}
```

### `frontend/types.ts`
Already has `ConversationEntry`, just ensure `duration_ms` field is present.

### `frontend/components/ReviewResult.tsx`
Add a compact progress summary above the detailed review sections:
- percent complete
- completed steps vs total steps
- actual iterations vs configured max iterations
- number of agents used

---

## Behaviour

### Tracing in supervisor
- Every specialist step is timed in milliseconds
- Trace entries are recorded for delegation, each specialist result, and synthesis
- The `progress` object is derived from the planned specialist sequence plus synthesis
- Synthesis timing includes the LLM JSON parsing

---

## Acceptance Criteria

GIVEN a valid `POST /games/game_0/review`
WHEN the response arrives
THEN `conversation_history` array has exactly 6 entries

GIVEN `conversation_history[1]` (Journalist result)
WHEN inspected
THEN `iteration == 1 && agent == "Journalist" && action == "RESULT" && duration_ms > 0`

GIVEN `metadata.agent_timings`
WHEN inspected
THEN keys are exactly `["Journalist", "Coach", "AssistantCoach", "Fan", "Synthesis"]`
AND all values are integers > 0

GIVEN `progress`
WHEN inspected
THEN `status == "complete"`
AND `completed_steps == total_steps`
AND `percent_complete == 100`

GIVEN the AgentTimeline component
WHEN rendered with 6 conversation entries
THEN 6 timeline nodes are visible
AND each node shows agent name and duration in milliseconds

GIVEN the ReviewResult component
WHEN rendered with a completed response
THEN it shows a progress summary card with completion %, step count, and iteration count

---

## Out of Scope
- Storing conversation history in database across sessions
- Replaying or resuming from middle of conversation
- Full LLM output text in history (truncated to ~100 chars for brevity)
