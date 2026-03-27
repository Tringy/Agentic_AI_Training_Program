# Multiple Report Formats

## Overview
Add a `format` query parameter (`brief|standard|technical`) to `POST /games/{game_id}/review` that selects between three synthesis styles, each with different output structure and emphasis. The frontend includes a selector to let users choose format before generation.

## Related Specs
| Relationship | Spec file | Why |
|---|---|---|
| depends on | `specs/configurable-depth.md` | Format presets map to depth token settings |
| extends | `specs/conversation-history-and-metrics.md` | Format recorded in metadata |

---

## Backend: API Contract

### `POST /games/{game_id}/review?format=brief|standard|technical`

**Query parameter:**
| Param | Values | Default |
|---|---|---|
| `format` | `brief`, `standard`, `technical` | `standard` |

**Success response — metadata addition (200):**
```json
{
  "metadata": {
    "format": "technical",
    ...other fields
  }
}
```

**Error responses:**
| Status | Condition |
|--------|-----------|
| 422 | `format` not one of `brief`, `standard`, `technical` |

---

## Backend: Implementation

### Format Token Mappings
| Format | Depth used | Summary | key_moments | tactical_analysis | performance_insights | fan_perspective | final_verdict |
|--------|-----------|---------|-------------|-------------------|---------------------|-----------------|---------------|
| `brief` | brief | 1 sent. | 2 bullets | 1 sent. | 1 sent. | omitted | 1 sent. |
| `standard` | standard | 2 sent. | 3 bullets | 2 sent. | 2 sent. | 1 sent. | 1 sent. |
| `technical` | detailed | 3 sent. | 5 bullets + stats | 3 sent. (xG/poss) | 3 sent. (ratings) | 1 sent. | 2 sent. |

### `python/prompts.py`
Update to import `SYNTHESIS_PROMPTS` dict and three format-specific prompts:
```python
SYNTHESIS_PROMPT_BRIEF = """You are synthesizing...
Rules:
- summary: 1 sentence only
- key_moments: exactly 2 bullet strings, each under 12 words
...(brief version of standard prompt)
"""

SYNTHESIS_PROMPT_TECHNICAL = """You are synthesizing into a technical report.
Rules:
- summary: 3 sentences covering narrative, tactical context, and outcome
- key_moments: exactly 5 bullets; each includes minute and stat (xG, pass %, shots, rating)
- tactical_analysis: 3 sentences; must reference xG and possession %
- performance_insights: 3 sentences; must include player ratings
...(detailed version)
"""

SYNTHESIS_PROMPTS = {
    "brief": SYNTHESIS_PROMPT_BRIEF,
    "standard": SYNTHESIS_PROMPT,
    "technical": SYNTHESIS_PROMPT_TECHNICAL,
}
```

### `python/main.py`
1. Import `Literal` and add to endpoint:
   ```python
   async def create_game_review(
       game_id: str,
       depth: Literal["brief", "standard", "detailed"] = Query("standard"),
       format: Literal["brief", "standard", "technical"] = Query("standard")
   ):
   ```
2. Map format to synthesis prompt and depth:
   ```python
   format_config = {
       "brief": {"depth": "brief", "prompt": "BRIEF"},
       "standard": {"depth": "standard", "prompt": "STANDARD"},
       "technical": {"depth": "detailed", "prompt": "TECHNICAL"},
   }
   # If format is specified, it overrides depth
   format_info = format_config[format]
   effective_depth = format_info["depth"]
   synthesis_prompt_key = format_info["prompt"]
   ```
3. Pass to supervisor:
   ```python
   from prompts import SYNTHESIS_PROMPTS
   result = await supervisor.orchestrate(
       context,
       agent_tokens=depth_config[effective_depth]["agent"],
       synthesis_tokens=depth_config[effective_depth]["synthesis"],
       synthesis_prompt=SYNTHESIS_PROMPTS[format]
   )
   ```
4. Include in metadata: `metadata["format"] = format`

### `python/supervisor.py`
Update `orchestrate()` signature:
```python
async def orchestrate(
    self,
    game_context: str,
    agent_tokens: int = 256,
    synthesis_tokens: int = 512,
    synthesis_prompt: str = None  # defaults to SYNTHESIS_PROMPT in imports
) -> str:
```

Pass `synthesis_prompt` (or default) to `self.llm.chat_json()` call.

---

## Frontend: Components

### `frontend/components/GameForm.tsx`
Add format selector alongside depth:
```tsx
const [format, setFormat] = useState<"brief" | "standard" | "technical">("standard");

// In form JSX:
<div className="flex flex-col gap-2">
  <label htmlFor="format" className="text-sm font-semibold text-goal-accent">
    Report Format
  </label>
  <select
    id="format"
    value={format}
    onChange={(e) => setFormat(e.target.value as any)}
    className="px-3 py-2 bg-gray-800 border border-gray-600 rounded text-gray-100"
  >
    <option value="brief">Brief (summary)</option>
    <option value="standard">Standard (balanced)</option>
    <option value="technical">Technical (detailed stats)</option>
  </select>
</div>

// In fetch call:
const response = await fetch(
  `${process.env.NEXT_PUBLIC_API_URL}/games/${game.id}/review?depth=${depth}&format=${format}`,
  ...
);
```

### `frontend/components/ReviewResult.tsx`
Add badge showing selected format:
```tsx
<div className="pitch-gradient rounded-lg p-6 text-white shadow-lg">
  <div className="flex justify-between items-start">
    <div>
      <p className="text-goal-yellow font-semibold text-sm">
        {metadata.competition && `${metadata.competition} · `}{metadata.game_date}
      </p>
      {metadata.format && (
        <p className="text-xs text-gray-300 mt-1">
          Report: <span className="text-goal-accent font-semibold">{metadata.format}</span>
        </p>
      )}
      ...existing content
    </div>
    ...
  </div>
</div>
```

### `frontend/types.ts`
Update `GameMetadata`:
```typescript
export type GameMetadata = {
  game_date: string;
  home_team: string;
  away_team: string;
  final_score: string;
  competition?: string;
  stadium?: string;
  depth?: "brief" | "standard" | "detailed";
  format?: "brief" | "standard" | "technical";
  iterations?: number;
  agents_used?: string[];
  duration_seconds?: number;
};
```

---

## Behaviour
1. User selects format in dropdown (triggers depth change if format chosen)
2. Frontend sends both `?depth=X&format=Y` (or just `?format=Z` which sets depth)
3. Backend validates both, effective depth = format's mapped depth
4. Supervisor gets correct synthesis prompt and token limits
5. Response includes both `depth` and `format` in metadata
6. Frontend shows format badge on result header

---

## Acceptance Criteria

GIVEN `POST /games/game_0/review?format=brief`
WHEN response arrives
THEN `metadata.format == "brief"`
AND `game_review.key_moments.length == 2`

GIVEN `POST /games/game_0/review?format=technical`
WHEN response arrives
THEN `game_review.key_moments.length == 5`
AND at least one key moment includes a number (xG, %, rating)

GIVEN user selects "Technical" in dropdown
WHEN form is submitted
THEN URL includes `format=technical`
AND result badge shows "Technical"

GIVEN `POST /games/game_0/review?format=invalid`
WHEN request made
THEN HTTP 422 returned

GIVEN `POST /games/game_0/review` (no format)
WHEN response arrives
THEN `metadata.format == "standard"`

---

## Out of Scope
- Custom user-defined formats
- Format-specific UI layouts (all use same component structure)
- Exporting formats to PDF/Word
