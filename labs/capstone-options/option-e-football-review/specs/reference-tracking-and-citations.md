# Reference Tracking and Citations

## Overview
Add source reference tracking so generated reviews include transparent evidence links to match facts (events, stats, and top performers). Backend returns normalized citations; frontend renders clickable citation chips and expandable source details per section.

## Related Specs
| Relationship | Spec file | Why |
|---|---|---|
| depends on | `specs/report-formats.md` | Technical format requires stronger evidence density |
| extends | `specs/conversation-history-and-metrics.md` | References are attached to synthesis and trace metadata |
| depends on | `specs/streaming.md` | Streaming complete event includes citation payload |

## API Contract

### `POST /games/{game_id}/review`

**Success response additions (200):**
```json
{
  "game_review": {
    "summary": "...",
    "key_moments": ["..."],
    "tactical_analysis": "...",
    "performance_insights": "...",
    "fan_perspective": "...",
    "final_verdict": "..."
  },
  "citations": [
    {
      "id": "ref_1",
      "type": "event",
      "label": "79' Hojlund goal",
      "value": "Rasmus Hojlund scored assisted by Rashford",
      "source": "SAMPLE_GAMES.game_0.events[4]"
    },
    {
      "id": "ref_2",
      "type": "stat",
      "label": "xG",
      "value": "MU 1.42 vs LIV 2.31",
      "source": "SAMPLE_GAMES.game_0.stats"
    }
  ],
  "section_citations": {
    "summary": ["ref_1", "ref_2"],
    "key_moments": ["ref_1"],
    "tactical_analysis": ["ref_2"],
    "performance_insights": ["ref_3"],
    "fan_perspective": [],
    "final_verdict": ["ref_2"]
  }
}
```

### `POST /games/{session_id}/ask`

Follow-up response should include same `citations` + `section_citations` shape in `answer` payload.

**Error responses:**
| Status | Condition |
|---|---|
| 500 | Citation parsing failed and fallback unavailable |

## Data Model Changes

### Backend (`python/main.py`)
```python
class Citation(BaseModel):
    id: str
    type: Literal["event", "stat", "performer", "discipline", "derived"]
    label: str
    value: str
    source: str

class GameReviewResponse(BaseModel):
    ...
    citations: List[Citation] = []
    section_citations: Dict[str, List[str]] = {}
```

### Frontend (`frontend/types.ts`)
```ts
export type Citation = {
  id: string;
  type: "event" | "stat" | "performer" | "discipline" | "derived";
  label: string;
  value: string;
  source: string;
};

export type GameReviewResponse = {
  ...
  citations?: Citation[];
  section_citations?: Record<string, string[]>;
};
```

## LLM Output Schema

Update synthesis prompt output schema to include citation wiring:
```json
{
  "summary": "string",
  "key_moments": ["string"],
  "tactical_analysis": "string",
  "performance_insights": "string",
  "fan_perspective": "string",
  "final_verdict": "string",
  "section_citations": {
    "summary": ["ref_1"],
    "key_moments": ["ref_1", "ref_2"],
    "tactical_analysis": ["ref_3"],
    "performance_insights": ["ref_4"],
    "fan_perspective": [],
    "final_verdict": ["ref_2"]
  }
}
```

## Parsing Fallback
- Strip markdown fences before `json.loads`.
- On `JSONDecodeError` or invalid citation IDs:
  - keep existing text fields,
  - set `section_citations` to empty arrays,
  - continue with HTTP 200 and `metadata.citation_status = "fallback"`.
- Only return HTTP 500 when both synthesis and fallback citation generation fail.

## Behaviour
1. Build deterministic citation catalog from game context before LLM call:
   - goals/cards/events,
   - stats (xG, possession, shots, passes),
   - top performers.
2. Assign stable IDs (`ref_1..ref_n`) and include citation catalog in synthesis context.
3. Prompt synthesis model to reference only provided citation IDs.
4. Validate all returned IDs exist in catalog.
5. Return:
   - `citations` (catalog entries),
   - `section_citations` (section-to-id mapping).
6. For `technical` format, enforce at least one citation per section except `fan_perspective`.

## Frontend Behaviour

### `frontend/components/ReviewResult.tsx`
1. Add citation chips below each rendered section:
```tsx
<CitationChips ids={section_citations.summary} citations={citations} />
```
2. Chips show `label` and open expandable detail panel with `value` + `source`.
3. Empty state: "No citations" for sections with none.

### New component: `frontend/components/CitationChips.tsx`
Props:
```ts
type CitationChipsProps = {
  ids?: string[];
  citations?: Citation[];
};
```
Behavior:
- Resolve ids to citation objects,
- render compact chips,
- clicking chip toggles source details.

## Acceptance Criteria
GIVEN `POST /games/game_0/review`
WHEN response is returned
THEN `citations` array exists and has at least 3 items
AND each citation has `id`, `type`, `label`, `value`, `source`.

GIVEN section citations in response
WHEN `section_citations.tactical_analysis` is read
THEN each id exists in `citations`.

GIVEN technical format review
WHEN response is returned
THEN `summary`, `key_moments`, `tactical_analysis`, `performance_insights`, and `final_verdict` each have at least one citation id.

GIVEN frontend renders review result
WHEN user clicks a citation chip
THEN source detail panel expands showing `value` and `source`.

## Out of Scope
- External web URLs as sources
- PDF/academic citation styles (APA/MLA)
- Cross-game citation graphing
