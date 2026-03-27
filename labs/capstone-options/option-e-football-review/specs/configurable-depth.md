# Configurable Parameters

## Overview
Add optional `depth` and `max_iterations` query parameters to `POST /games/{game_id}/review`. `depth` controls agent output verbosity and token limits; `max_iterations` controls how many specialist agents run before synthesis. The frontend includes selectors in the game form so users can configure both before review generation.

## Related Specs
| Relationship | Spec file | Why |
|---|---|---|
| extends | `specs/conversation-history-and-metrics.md` | Depth affects truncation of agent content in trace |
| required by | `specs/report-formats.md` | Format presets use depth values |

---

## Backend: API Contract

### `POST /games/{game_id}/review?depth=brief|standard|detailed&max_iterations=1..4`

**Query parameters:**
| Param | Values | Default |
|---|---|---|
| `depth` | `brief`, `standard`, `detailed` | `standard` |
| `max_iterations` | `1`, `2`, `3`, `4` | `4` |

**Success response — metadata addition (200):**
```json
{
  "metadata": {
    "depth": "standard",
    "max_iterations": 4,
    "game_date": "...",
    "home_team": "...",
    ...additional fields
  }
}
```

**Error responses:**
| Status | Condition |
|--------|-----------|
| 422 | `depth` not one of `brief`, `standard`, `detailed` |
| 422 | `max_iterations` outside `1..4` |

---

## Backend: Implementation

### Token Configuration
| Depth | Agent max_tokens | Synthesis max_tokens | Notes |
|-------|------------------|---------------------|-------|
| `brief` | 128 | 256 | Fast responses, minimal detail |
| `standard` | 256 | 512 | Default, balanced |
| `detailed` | 512 | 1024 | Long-form, comprehensive |

### `python/main.py`
1. Import `Literal` from `typing`
2. At endpoint signature:
   ```python
   async def create_game_review(
       game_id: str,
     depth: Literal["brief", "standard", "detailed"] = Query("standard"),
     max_iterations: int = Query(4, ge=1, le=4)
   ):
   ```
3. Map depth to token limits:
   ```python
   depth_config = {
       "brief": {"agent": 128, "synthesis": 256},
       "standard": {"agent": 256, "synthesis": 512},
       "detailed": {"agent": 512, "synthesis": 1024},
   }
   agent_tokens = depth_config[depth]["agent"]
   synthesis_tokens = depth_config[depth]["synthesis"]
   ```
4. Pass to supervisor:
   ```python
   result = await supervisor.orchestrate(
       context,
     agent_tokens=agent_tokens,
     synthesis_tokens=synthesis_tokens,
     max_iterations=max_iterations,
   )
   ```
5. Include both `"depth"` and `"max_iterations"` in metadata.

### `python/supervisor.py`
1. Update `orchestrate()` signature:
   ```python
   async def orchestrate(
       self,
       game_context: str,
       agent_tokens: int = 256,
     synthesis_tokens: int = 512,
     max_iterations: int = 4,
   ) -> str:
   ```
2. Cap the specialist sequence to the first `max_iterations` agents.
3. Pass `max_tokens=agent_tokens` to each specialist call.
4. Pass `max_tokens=synthesis_tokens` to `self.llm.chat_json()` call.

### `python/llm_client.py`
Already updated to accept `max_tokens` in `chat_json()`.

---

## Frontend: Components

### `frontend/components/GameForm.tsx`
Add depth and max-iterations selectors:
```tsx
const [depth, setDepth] = useState<"brief" | "standard" | "detailed">("standard");
const [maxIterations, setMaxIterations] = useState<1 | 2 | 3 | 4>(4);

// In form JSX:
<div className="flex flex-col gap-2">
  <label htmlFor="depth" className="text-sm font-semibold text-goal-accent">
    Analysis Depth
  </label>
  <select
    id="depth"
    value={depth}
    onChange={(e) => setDepth(e.target.value as any)}
    className="px-3 py-2 bg-gray-800 border border-gray-600 rounded text-gray-100"
  >
    <option value="brief">Brief (fast)</option>
    <option value="standard">Standard (balanced)</option>
    <option value="detailed">Detailed (comprehensive)</option>
  </select>
</div>

// In fetch call:
const response = await fetch(
  `${process.env.NEXT_PUBLIC_API_URL}/games/${game.id}/review?depth=${depth}&max_iterations=${maxIterations}`,
  ...
);
```

### `frontend/types.ts`
Update `GameMetadata` type:
```typescript
export type GameMetadata = {
  game_date: string;
  home_team: string;
  away_team: string;
  final_score: string;
  competition?: string;
  stadium?: string;
  depth?: "brief" | "standard" | "detailed";
  max_iterations?: number;
  iterations?: number;
  agents_used?: string[];
  duration_seconds?: number;
};
```

---

## Behaviour
1. User selects depth and max iterations before clicking "Review"
2. Frontend sends both query params to backend
3. Backend validates enum/range, maps depth to token budgets, passes both to supervisor
4. Supervisor runs only the configured number of specialist steps before synthesis
5. Response includes both fields in metadata
6. Frontend can display the configured and actual iteration counts on result

---

## Acceptance Criteria

GIVEN user selects `depth=brief` in dropdown
WHEN form is submitted
THEN `POST /games/game_0/review?depth=brief` is sent
AND response time is < 50% of `depth=detailed` request

GIVEN user selects `max_iterations=2`
WHEN form is submitted
THEN only the first two specialist agents run before synthesis
AND `metadata.max_iterations == 2`

GIVEN `POST /games/game_0/review?depth=invalid`
WHEN request is made
THEN HTTP 422 is returned

GIVEN `POST /games/game_0/review?max_iterations=9`
WHEN request is made
THEN HTTP 422 is returned

GIVEN `POST /games/game_0/review` (no depth param)
WHEN response arrives
THEN `metadata.depth == "standard"`

GIVEN `POST /games/game_0/review` (no max_iterations param)
WHEN response arrives
THEN `metadata.max_iterations == 4`

GIVEN the depth selector component
WHEN rendered
THEN 3 options are visible: Brief, Standard, Detailed
AND 4 max-iteration options are visible: 1, 2, 3, 4

---

## Out of Scope
- Saving depth preference per user
- Per-agent depth differentiation
- Dynamic token limit based on game complexity
