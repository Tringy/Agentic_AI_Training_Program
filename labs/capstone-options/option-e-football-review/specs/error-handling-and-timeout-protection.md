# Error Handling and Timeout Protection

## Overview
Add consistent error handling and timeout safeguards across review endpoints so failures are predictable, debuggable, and user-friendly. This includes per-agent timeout handling, synthesis fallback behavior, standard error payloads, and frontend error-state rendering.

## Related Specs
| Relationship | Spec file | Why |
|---|---|---|
| extends | `specs/conversation-history-and-metrics.md` | Error events are added to conversation/progress history |
| depends on | `specs/streaming.md` | Stream endpoint must emit structured error events |
| depends on | `specs/configurable-depth.md` | Timeout limits vary by depth and token budget |

## API Contract

### Standard Error Envelope
All non-2xx API responses must use:
```json
{
  "detail": "Human-readable message",
  "error_code": "STRING_CODE",
  "retryable": false,
  "request_id": "uuid"
}
```

### `POST /games/{game_id}/review`

**Error responses:**
| Status | Condition | `error_code` | retryable |
|---|---|---|---|
| 400 | Invalid game id format (`game_X`) | `INVALID_GAME_ID` | false |
| 404 | Game id not found in catalog | `GAME_NOT_FOUND` | false |
| 422 | Invalid query params (`depth`, `format`) | `VALIDATION_ERROR` | false |
| 500 | LLM returned invalid JSON and fallback also failed | `LLM_INVALID_JSON` | true |
| 504 | Any specialist or synthesis exceeded timeout | `AGENT_TIMEOUT` | true |

### `POST /games/{session_id}/ask`

**Error responses:**
| Status | Condition | `error_code` | retryable |
|---|---|---|---|
| 404 | Session not found | `SESSION_NOT_FOUND` | false |
| 422 | Question too short/invalid | `VALIDATION_ERROR` | false |
| 500 | Unexpected failure | `FOLLOWUP_FAILED` | true |
| 504 | Follow-up orchestration timeout | `AGENT_TIMEOUT` | true |

### `POST /games/{game_id}/review/stream`

Pre-stream validation errors return JSON with the standard envelope (same status table as `/review`).
If failure occurs mid-stream, emit:
```json
{ "type": "error", "detail": "Coach agent timed out after 60 seconds", "error_code": "AGENT_TIMEOUT", "retryable": true }
```
then close stream.

## Data Model Changes

### Backend Pydantic
Add reusable model in `python/main.py`:
```python
class APIError(BaseModel):
    detail: str
    error_code: str
    retryable: bool
    request_id: str
```

### Frontend TypeScript
Add in `frontend/types.ts`:
```ts
export type APIError = {
  detail: string;
  error_code: string;
  retryable: boolean;
  request_id: string;
};
```

## Configuration
| Env var | Default | Purpose |
|---|---|---|
| `AGENT_TIMEOUT_SECONDS` | `60` | Timeout for each specialist call |
| `SYNTHESIS_TIMEOUT_SECONDS` | `60` | Timeout for synthesis call |
| `RETRY_ATTEMPTS` | `1` | Number of automatic retries for retryable errors |

## Behaviour
1. Generate `request_id = str(uuid.uuid4())` at the start of each request.
2. Wrap orchestration in structured `try/except` blocks.
3. Convert known errors to mapped HTTP status + `error_code`.
4. Use `raise HTTPException(... ) from exc` for all wrapped exceptions.
5. For timeout failures, return status 504 and include `retryable=true`.
6. For LLM JSON parsing failure:
   - attempt existing fallback synthesis payload,
   - if fallback fails, return `500` with `LLM_INVALID_JSON`.
7. In streaming mode, emit SSE error event and close connection.
8. Add an error trace event in `conversation_history` when failure occurs before response.

## Frontend Behaviour
1. Centralize API error parsing helper:
```ts
function parseApiError(responseBody: unknown): APIError
```
2. `GameForm.tsx` and follow-up form should display:
   - main message (`detail`),
   - small metadata line (`Code: AGENT_TIMEOUT · Request: <id>`),
   - retry hint if `retryable=true`.
3. Add retry button for retryable failures that replays the last request params.
4. For streaming mode, show non-blocking toast + persistent inline error card.

## Acceptance Criteria
GIVEN `POST /games/invalid/review`
WHEN called
THEN response status is 400
AND JSON body includes `error_code="INVALID_GAME_ID"` and `request_id`.

GIVEN a specialist exceeds timeout
WHEN `/games/{id}/review` is called
THEN status is 504
AND `error_code="AGENT_TIMEOUT"`
AND `retryable=true`.

GIVEN streaming review fails mid-run
WHEN Coach times out
THEN stream emits one `type="error"` event with `error_code="AGENT_TIMEOUT"`
AND stream closes gracefully.

GIVEN frontend receives retryable API error
WHEN error card is shown
THEN retry button is visible
AND clicking retry re-sends the previous request.

## Out of Scope
- Circuit breaker across distributed services
- Persistent error analytics backend
- Automatic exponential backoff beyond one retry
