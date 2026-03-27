# Streaming Responses (Server-Sent Events)

## Overview
Add a `POST /games/{game_id}/review/stream` endpoint that streams agent progress via Server-Sent Events (SSE). As each agent completes, a `progress` event fires immediately, letting the frontend display real-time progress without waiting for all four agents to finish. Final `complete` event includes the full synthesized review.

## Related Specs
| Relationship | Spec file | Why |
|---|---|---|
| depends on | `specs/conversation-history-and-metrics.md` | Reuses same trace-entry JSON structure |
| depends on | `specs/configurable-depth.md` | Accepts same `depth` query param |
| depends on | `specs/report-formats.md` | Accepts same `format` query param |

---

## Backend: API Contract

### `POST /games/{game_id}/review/stream?depth=standard&format=standard`

**Request:** No body (game ID from catalog)

**Query parameters:**
| Param | Values | Default |
|---|---|---|
| `depth` | `brief`, `standard`, `detailed` | `standard` |
| `format` | `brief`, `standard`, `technical` | `standard` |

**Response:** `Content-Type: text/event-stream`

Each SSE event formatted as `data: {json}\n\n` where `{json}` is:

**Progress event** (after each agent completes):
```json
{
  "type": "progress",
  "iteration": 1,
  "agent": "Journalist",
  "action": "RESULT",
  "duration_ms": 1820,
  "content": "Manchester United defeated Liverpool 2-1..."
}
```

**Complete event** (when synthesis finishes):
```json
{
  "type": "complete",
  "review": {
    "game_id": "session-uuid",
    "game_review": { /* full GameReview object */ },
    "specialist_perspectives": { /* full dict */ },
    "metadata": { /* full metadata with depth, format, timings */ },
    "conversation_history": [ /* full array */ ]
  }
}
```

**Error event** (on exception):
```json
{
  "type": "error",
  "detail": "Journalist agent timed out after 60 seconds"
}
```

**Error responses (pre-streaming):**
| Status | Condition |
|--------|-----------|
| 404 | Game ID not found |
| 422 | Invalid `depth` or `format` param |

---

## Backend: Implementation

### `python/main.py`
1. Import `StreamingResponse` from FastAPI
2. Create new endpoint:
```python
@app.post("/games/{game_id}/review/stream")
async def stream_game_review(
    game_id: str,
    depth: Literal["brief", "standard", "detailed"] = Query("standard"),
    format: Literal["brief", "standard", "technical"] = Query("standard")
):
    """Stream game review progress via Server-Sent Events."""
    try:
        # Validate game exists (same as create_game_review)
        game_index = int(game_id.split("_")[1])
        if game_index < 0 or game_index >= len(SAMPLE_GAMES):
            raise HTTPException(status_code=404, detail="Game not found")
        
        game = SAMPLE_GAMES[game_index]
        session_id = str(uuid.uuid4())
        games_store[session_id] = {...}  # Same as create_game_review
        
        async def event_generator():
            supervisor = SupervisorAgent(llm_client)
            
            # Build context (same as create_game_review)
            context = f"""..."""
            
            try:
                # Run orchestrate with streaming callback
                result = await supervisor.orchestrate(
                    context,
                    agent_tokens=depth_config[effective_depth]["agent"],
                    synthesis_tokens=depth_config[effective_depth]["synthesis"],
                    synthesis_prompt=SYNTHESIS_PROMPTS[format],
                    stream_callback=lambda event: event_generator_emit(event)
                )
                
                # Parse complete result
                review_data = json.loads(result)
                
                # Build GameReviewResponse
                game_review = GameReview(...)
                response = GameReviewResponse(...)
                
                # Emit complete event
                yield f'data: {json.dumps({"type": "complete", "review": response.dict()})}\n\n'
                
            except Exception as e:
                yield f'data: {json.dumps({"type": "error", "detail": str(e)})}\n\n'
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            }
        )
    
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid game ID format")
```

### `python/supervisor.py`
Update `orchestrate()` to support streaming callback:
```python
async def orchestrate(
    self,
    game_context: str,
    agent_tokens: int = 256,
    synthesis_tokens: int = 512,
    synthesis_prompt: str = None,
    stream_callback = None  # Optional async callable(event_dict)
) -> str:
    ...
    # After journalist completes:
    if stream_callback:
        await stream_callback({
            "type": "progress",
            "iteration": 1,
            "agent": "Journalist",
            "action": "RESULT",
            "duration_ms": duration_ms,
            "content": journalist_result[:100] + "..."
        })
    
    # After each subsequent agent, similar calls
    # After synthesis:
    if stream_callback:
        await stream_callback({
            "type": "progress",
            "iteration": 5,
            "agent": "Supervisor",
            "action": "SYNTHESIS",
            "duration_ms": synthesis_duration,
            "content": "Complete"
        })
```

---

## Frontend: Components

### `frontend/components/StreamingReviewProgress.tsx` (new)
Display real-time stream of progress events:
```typescript
interface StreamingReviewProgressProps {
  gameId: string;
  depth?: "brief" | "standard" | "detailed";
  format?: "brief" | "standard" | "technical";
  onComplete: (review: GameReviewResponse) => void;
  onError: (error: string) => void;
}

export default function StreamingReviewProgress({
  gameId,
  depth = "standard",
  format = "standard",
  onComplete,
  onError,
}: StreamingReviewProgressProps) {
  const [events, setEvents] = useState<
    Array<{ type: string; agent?: string; duration_ms?: number; detail?: string }>
  >([]);

  useEffect(() => {
    const eventSource = new EventSource(
      `${process.env.NEXT_PUBLIC_API_URL}/games/${gameId}/review/stream?depth=${depth}&format=${format}`
    );

    eventSource.addEventListener("message", (event) => {
      const data = JSON.parse(event.data);

      if (data.type === "progress") {
        setEvents((prev) => [...prev, data]);
      } else if (data.type === "complete") {
        setEvents((prev) => [...prev, { type: "complete" }]);
        onComplete(data.review);
        eventSource.close();
      } else if (data.type === "error") {
        onError(data.detail);
        eventSource.close();
      }
    });

    eventSource.onerror = () => {
      onError("Connection lost");
      eventSource.close();
    };

    return () => eventSource.close();
  }, [gameId, depth, format, onComplete, onError]);

  return (
    <div className="space-y-3">
      {events.map((event, i) => (
        <div
          key={i}
          className="flex items-center gap-3 px-4 py-3 bg-gray-900 border border-gray-700 rounded"
        >
          {event.type === "progress" && (
            <>
              <div className="w-2 h-2 bg-goal-accent rounded-full animate-pulse" />
              <span className="text-sm font-semibold text-goal-accent">
                {event.agent}
              </span>
              <span className="text-xs text-gray-400">
                {event.duration_ms}ms
              </span>
            </>
          )}
          {event.type === "complete" && (
            <>
              <div className="w-2 h-2 bg-green-500 rounded-full" />
              <span className="text-sm font-semibold text-green-400">
                Analysis Complete
              </span>
            </>
          )}
        </div>
      ))}
    </div>
  );
}
```

### `frontend/app/page.tsx`
Add conditional view for streaming:
```tsx
const [streamingMode, setStreamingMode] = useState(false);

// In render:
{!reviewResult && (
  <>
    {streamingMode ? (
      <>
        <button
          onClick={() => setStreamingMode(false)}
          className="mb-6 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded text-sm"
        >
          ← Back to Classic Mode
        </button>
        <StreamingReviewProgress
          gameId={selectedGame!}
          depth={depth}
          format={format}
          onComplete={(result) => {
            setReviewResult(result);
            setCurrentSessionId(result.game_id);
          }}
          onError={(err) => setFollowUpError(err)}
        />
      </>
    ) : (
      <>
        <button
          onClick={() => setStreamingMode(true)}
          className="mb-6 px-4 py-2 bg-goal-accent/20 border border-goal-accent rounded text-sm text-goal-accent"
        >
          🚀 Use Streaming Mode
        </button>
        <GameForm
          onGameSelected={handleGameSelected}
          depth={depth}
          format={format}
        />
      </>
    )}
  </>
)}
```

---

## Behaviour
1. Client calls `POST /games/{game_id}/review/stream?depth=X&format=Y`
2. Backend opens ServerResponse stream, begins supervisor orchestration
3. After Journalist completes: send `{type: "progress", agent: "Journalist", duration_ms: N}`
4. After Coach, AssistantCoach, Fan: send similar progress events
5. After Synthesis: send `{type: "progress", agent: "Supervisor", action: "SYNTHESIS"}`
6. After full response built: send `{type: "complete", review: {...}}`
7. Frontend renders events one by one as they arrive, shows live progress
8. Final review auto-displays when `complete` event received

---

## Acceptance Criteria

GIVEN `POST /games/game_0/review/stream` is called
WHEN stream opens
THEN `Content-Type: text/event-stream` header present
AND connection stays open (no premature close)

GIVEN stream is running
WHEN Journalist agent completes
THEN a `progress` event with `"agent": "Journalist"` is received
AND event arrives before any Coach event

GIVEN all agents complete
WHEN `complete` event is received
THEN `event.review.game_review.summary` is non-empty string
AND `event.review.conversation_history` has 6 entries

GIVEN an invalid game ID
WHEN stream endpoint called
THEN HTTP 404 JSON response (stream never starts)

GIVEN the StreamingReviewProgress component
WHEN events arrive
THEN DOM displays a new progress line for each event
AND final line shows "Analysis Complete"

GIVEN frontend receives `error` event
WHEN parsed
THEN `onError` callback fires with error detail
AND EventSource closes

---

## Out of Scope
- Token-by-token synthesis streaming (only agent-by-agent)
- WebSocket upgrade from SSE
- Client reconnect / resumption logic
- Event ID / retry logic
