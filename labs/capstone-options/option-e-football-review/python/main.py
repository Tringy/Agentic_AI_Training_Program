"""Football Game Review Assistant API."""

import asyncio
import json
import os
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, List, Literal, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from llm_client import LLMClient
from prompts import SYNTHESIS_PROMPTS
from pydantic import BaseModel, Field
from supervisor import SupervisorAgent

load_dotenv()

AGENT_TIMEOUT_SECONDS = int(os.getenv("AGENT_TIMEOUT_SECONDS", "60"))
SYNTHESIS_TIMEOUT_SECONDS = int(os.getenv("SYNTHESIS_TIMEOUT_SECONDS", "60"))
RETRY_ATTEMPTS = int(os.getenv("RETRY_ATTEMPTS", "1"))


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Startup and shutdown logic."""
    # Startup
    yield
    # Shutdown


app = FastAPI(title="Football Game Review Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class APIError(BaseModel):
    """Standard error envelope."""

    detail: str
    error_code: str
    retryable: bool
    request_id: str


def _make_api_error(detail: str, error_code: str, retryable: bool, request_id: str) -> dict:
    return APIError(
        detail=detail,
        error_code=error_code,
        retryable=retryable,
        request_id=request_id,
    ).model_dump()


def _api_http_exception(status_code: int, detail: str, error_code: str, retryable: bool, request_id: str) -> HTTPException:
    return HTTPException(
        status_code=status_code,
        detail=_make_api_error(detail, error_code, retryable, request_id),
    )


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, _exc: RequestValidationError):
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    return JSONResponse(
        status_code=422,
        content=_make_api_error("Validation failed", "VALIDATION_ERROR", False, request_id),
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if isinstance(exc.detail, dict) and "error_code" in exc.detail:
        return JSONResponse(status_code=exc.status_code, content=exc.detail)

    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    default_code = "HTTP_ERROR"
    if exc.status_code == 404:
        default_code = "NOT_FOUND"
    elif exc.status_code == 400:
        default_code = "BAD_REQUEST"
    elif exc.status_code == 422:
        default_code = "VALIDATION_ERROR"

    return JSONResponse(
        status_code=exc.status_code,
        content=_make_api_error(str(exc.detail), default_code, exc.status_code >= 500, request_id),
    )


# Initialize LLM client
try:
    llm_client = LLMClient()
except (ImportError, OSError, RuntimeError, ValueError):
    # Allow API import/test startup even if local Python or SDK setup cannot load
    # the LLM backend. Endpoints that require the model will fail at runtime.
    llm_client = None

# Sample games catalog - in production, pull from database/external API
SAMPLE_GAMES = [
    {
        "game_date": "2026-03-21",
        "home_team": "Manchester United",
        "away_team": "Liverpool",
        "home_score": 2,
        "away_score": 1,
        "final_score": "2-1",
        "competition": "Premier League",
        "stadium": "Old Trafford",
        "events": [
            {"minute": 14, "type": "goal", "team": "Liverpool", "player": "Mohamed Salah", "assist": "Trent Alexander-Arnold"},
            {"minute": 37, "type": "yellow_card", "team": "Manchester United", "player": "Bruno Fernandes"},
            {"minute": 52, "type": "goal", "team": "Manchester United", "player": "Marcus Rashford", "assist": "Kobbie Mainoo"},
            {"minute": 68, "type": "yellow_card", "team": "Liverpool", "player": "Alexis Mac Allister"},
            {"minute": 79, "type": "goal", "team": "Manchester United", "player": "Rasmus Højlund", "assist": "Marcus Rashford"},
            {"minute": 85, "type": "red_card", "team": "Liverpool", "player": "Virgil van Dijk"},
        ],
        "stats": {
            "home": {
                "possession": 44,
                "shots": 12,
                "shots_on_target": 5,
                "xG": 1.42,
                "passes": 387,
                "pass_accuracy": 82,
                "corners": 4,
                "fouls": 11,
            },
            "away": {
                "possession": 56,
                "shots": 18,
                "shots_on_target": 7,
                "xG": 2.31,
                "passes": 512,
                "pass_accuracy": 89,
                "corners": 7,
                "fouls": 14,
            },
        },
        "top_performers": [
            {"player": "Marcus Rashford", "team": "Manchester United", "rating": 8.7, "note": "1 goal, 1 assist, 4 key passes"},
            {"player": "Mohamed Salah", "team": "Liverpool", "rating": 7.9, "note": "1 goal, 4 shots, xG 0.84"},
            {"player": "Rasmus Højlund", "team": "Manchester United", "rating": 8.2, "note": "1 goal, 3 shots on target"},
        ],
    },
    {
        "game_date": "2026-03-20",
        "home_team": "Real Madrid",
        "away_team": "Barcelona",
        "home_score": 3,
        "away_score": 2,
        "final_score": "3-2",
        "competition": "La Liga",
        "stadium": "Santiago Bernabéu",
        "events": [
            {"minute": 8, "type": "goal", "team": "Real Madrid", "player": "Vinícius Jr.", "assist": "Jude Bellingham"},
            {"minute": 23, "type": "goal", "team": "Barcelona", "player": "Pedri", "assist": "Lamine Yamal"},
            {"minute": 41, "type": "yellow_card", "team": "Real Madrid", "player": "Federico Valverde"},
            {"minute": 45, "type": "goal", "team": "Real Madrid", "player": "Kylian Mbappé", "assist": "Vinícius Jr."},
            {"minute": 61, "type": "goal", "team": "Barcelona", "player": "Robert Lewandowski", "assist": "Pedri", "note": "penalty"},
            {"minute": 74, "type": "yellow_card", "team": "Barcelona", "player": "Frenkie de Jong"},
            {"minute": 88, "type": "goal", "team": "Real Madrid", "player": "Jude Bellingham", "assist": "Rodrygo"},
        ],
        "stats": {
            "home": {
                "possession": 48,
                "shots": 16,
                "shots_on_target": 8,
                "xG": 2.87,
                "passes": 441,
                "pass_accuracy": 86,
                "corners": 5,
                "fouls": 10,
            },
            "away": {
                "possession": 52,
                "shots": 14,
                "shots_on_target": 6,
                "xG": 1.93,
                "passes": 479,
                "pass_accuracy": 88,
                "corners": 6,
                "fouls": 12,
            },
        },
        "top_performers": [
            {"player": "Jude Bellingham", "team": "Real Madrid", "rating": 9.1, "note": "1 goal, 1 assist, man of the match"},
            {"player": "Kylian Mbappé", "team": "Real Madrid", "rating": 8.4, "note": "1 goal, xG 1.12, 5 shots"},
            {"player": "Pedri", "team": "Barcelona", "rating": 8.0, "note": "1 goal, 1 assist, 91 passes completed"},
        ],
    },
    {
        "game_date": "2026-03-22",
        "home_team": "Paris Saint-Germain",
        "away_team": "Lyon",
        "home_score": 1,
        "away_score": 0,
        "final_score": "1-0",
        "competition": "Ligue 1",
        "stadium": "Parc des Princes",
        "events": [
            {"minute": 33, "type": "yellow_card", "team": "Lyon", "player": "Corentin Tolisso"},
            {"minute": 57, "type": "goal", "team": "Paris Saint-Germain", "player": "Ousmane Dembélé", "assist": "Fabian Ruiz"},
            {"minute": 72, "type": "yellow_card", "team": "Paris Saint-Germain", "player": "Marquinhos"},
            {"minute": 89, "type": "yellow_card", "team": "Lyon", "player": "Nicolas Tagliafico"},
        ],
        "stats": {
            "home": {
                "possession": 63,
                "shots": 19,
                "shots_on_target": 6,
                "xG": 1.74,
                "passes": 601,
                "pass_accuracy": 91,
                "corners": 8,
                "fouls": 9,
            },
            "away": {
                "possession": 37,
                "shots": 7,
                "shots_on_target": 2,
                "xG": 0.41,
                "passes": 352,
                "pass_accuracy": 78,
                "corners": 2,
                "fouls": 13,
            },
        },
        "top_performers": [
            {"player": "Ousmane Dembélé", "team": "Paris Saint-Germain", "rating": 8.3, "note": "1 goal, 3 key passes, 7 dribbles"},
            {"player": "Lucas Chevalier", "team": "Lyon", "rating": 8.0, "note": "4 saves, kept Lyon in the game until late"},
        ],
    },
    {
        "game_date": "2026-03-19",
        "home_team": "Bayern Munich",
        "away_team": "Borussia Dortmund",
        "home_score": 2,
        "away_score": 2,
        "final_score": "2-2",
        "competition": "Bundesliga",
        "stadium": "Allianz Arena",
        "events": [
            {"minute": 11, "type": "goal", "team": "Bayern Munich", "player": "Harry Kane", "assist": "Leroy Sané"},
            {"minute": 29, "type": "yellow_card", "team": "Borussia Dortmund", "player": "Emre Can"},
            {"minute": 38, "type": "goal", "team": "Borussia Dortmund", "player": "Serhou Guirassy", "assist": "Julian Brandt"},
            {"minute": 55, "type": "goal", "team": "Bayern Munich", "player": "Harry Kane", "assist": "Thomas Müller", "note": "penalty"},
            {"minute": 67, "type": "yellow_card", "team": "Bayern Munich", "player": "Joshua Kimmich"},
            {"minute": 83, "type": "goal", "team": "Borussia Dortmund", "player": "Jamie Gittens", "assist": "Ramy Bensebaini"},
            {"minute": 90, "type": "yellow_card", "team": "Borussia Dortmund", "player": "Marcel Sabitzer"},
        ],
        "stats": {
            "home": {
                "possession": 58,
                "shots": 21,
                "shots_on_target": 9,
                "xG": 2.65,
                "passes": 534,
                "pass_accuracy": 88,
                "corners": 9,
                "fouls": 8,
            },
            "away": {
                "possession": 42,
                "shots": 13,
                "shots_on_target": 5,
                "xG": 1.58,
                "passes": 387,
                "pass_accuracy": 81,
                "corners": 4,
                "fouls": 11,
            },
        },
        "top_performers": [
            {"player": "Harry Kane", "team": "Bayern Munich", "rating": 8.9, "note": "2 goals (1 pen), xG 1.43, 6 shots"},
            {"player": "Jamie Gittens", "team": "Borussia Dortmund", "rating": 8.5, "note": "1 goal, equalizer in 83', 5 dribbles"},
            {"player": "Julian Brandt", "team": "Borussia Dortmund", "rating": 7.8, "note": "1 assist, 3 key passes, 88 touches"},
        ],
    },
]

# In-memory game store for conversation context
games_store: Dict[str, dict] = {}


# ---------------------------------------------------------------------------
# Request/Response Models
# ---------------------------------------------------------------------------


class GameInfoRequest(BaseModel):
    """Request with basic game information."""

    game_date: str = Field(min_length=8, description="Game date (YYYY-MM-DD)")
    home_team: str = Field(min_length=2, description="Home team name")
    away_team: str = Field(min_length=2, description="Away team name")
    home_score: int = Field(ge=0, description="Home team score")
    away_score: int = Field(ge=0, description="Away team score")
    final_score: str = Field(description="Final score string (e.g., '2-1')")
    context: Optional[str] = Field(
        default=None,
        description="Additional context about the game",
    )


class FollowUpQuestion(BaseModel):
    """Follow-up question about a game."""

    question: str = Field(
        min_length=10,
        description="Question to ask about the game",
    )


class GameReview(BaseModel):
    """Game review from all specialist perspectives."""

    summary: str
    key_moments: List[str]
    tactical_analysis: str
    performance_insights: str
    fan_perspective: str
    final_verdict: str


class ConversationEntry(BaseModel):
    """Entry in agent conversation history."""

    iteration: int
    agent: str
    action: str
    content: Optional[str] = None
    duration_ms: int = 0


class ProgressInfo(BaseModel):
    """Progress summary for a completed workflow."""

    status: str
    total_steps: int
    completed_steps: int
    percent_complete: int
    current_step: str
    planned_steps: List[str]
    completed_steps_labels: List[str]
    max_iterations: int


class AgentMetric(BaseModel):
    """Performance metrics for a single agent."""

    duration_ms: int
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class MetricsSummary(BaseModel):
    """Aggregated metrics for all agents."""

    agent_metrics: Dict[str, AgentMetric]
    total_tokens: int
    total_prompt_tokens: int
    total_completion_tokens: int


class GameReviewResponse(BaseModel):
    """Complete game review response."""

    game_id: str
    game_review: GameReview
    specialist_perspectives: dict
    conversation_history: List[ConversationEntry]
    progress: ProgressInfo
    metadata: dict


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/games")
async def list_games():
    """List available games to review."""
    games = []
    for i, game in enumerate(SAMPLE_GAMES):
        goals = [e for e in game.get("events", []) if e["type"] == "goal"]
        games.append(
            {
                "id": f"game_{i}",
                "date": game["game_date"],
                "home_team": game["home_team"],
                "away_team": game["away_team"],
                "final_score": game["final_score"],
                "competition": game.get("competition", ""),
                "stadium": game.get("stadium", ""),
                "scorers": [{"minute": g["minute"], "player": g["player"], "team": g["team"]} for g in goals],
            }
        )
    return {"games": games}


class ReviewRequest(BaseModel):
    """Request body for POST /review (game catalog-based)."""

    game_id: str = Field(description="Game ID from GET /games (e.g., 'game_0')")


@app.post("/review")
async def review_by_id(http_request: Request, request: ReviewRequest):
    """POST /review — accepts game_id and delegates to the game-specific review endpoint."""
    return await create_game_review(http_request, request.game_id)


@app.post("/games/{game_id}/review")
async def create_game_review(
    request: Request,
    game_id: str,
    depth: Literal["brief", "standard", "detailed"] = Query("standard"),
    report_format: Literal["brief", "standard", "technical"] = Query("standard", alias="format"),
    max_iterations: int = Query(4, ge=1, le=4),
):
    """Create a review session for a game."""
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    try:
        depth_config = {
            "brief": {"agent": 128, "synthesis": 256},
            "standard": {"agent": 256, "synthesis": 512},
            "detailed": {"agent": 512, "synthesis": 1024},
        }
        # Depth controls specialist verbosity/tokens; format controls synthesis style.
        effective_depth = depth
        agent_tokens = depth_config[effective_depth]["agent"]
        synthesis_tokens = depth_config[effective_depth]["synthesis"]

        game_index = int(game_id.split("_")[1])
        if game_index < 0 or game_index >= len(SAMPLE_GAMES):
            raise _api_http_exception(404, "Game not found", "GAME_NOT_FOUND", False, request_id)

        game = SAMPLE_GAMES[game_index]

        # Store game context for this session
        session_id = str(uuid.uuid4())
        games_store[session_id] = {
            "game_id": game_id,
            "game_data": game,
            "created_at": datetime.now().isoformat(),
            "settings": {
                "depth": effective_depth,
                "format": report_format,
                "max_iterations": max_iterations,
            },
            "reviews": [],
            "follow_ups": [],
        }

        # Run automatic review with game context
        if llm_client is None:
            raise _api_http_exception(500, "LLM backend not available", "FOLLOWUP_FAILED", True, request_id)
        supervisor = SupervisorAgent(llm_client)

        # Build rich context prompt with all match details
        events = game.get("events", [])
        stats = game.get("stats", {})
        performers = game.get("top_performers", [])

        goals = [e for e in events if e["type"] == "goal"]
        yellows = [e for e in events if e["type"] == "yellow_card"]
        reds = [e for e in events if e["type"] == "red_card"]

        goal_lines = "\n".join(
            f"  {e['minute']}' {e['player']} ({e['team']})"
            + (f" — assist: {e['assist']}" if "assist" in e else "")
            + (f" [{e['note']}]" if "note" in e else "")
            for e in goals
        )
        yellow_lines = ", ".join(f"{e['player']} ({e['team']}, {e['minute']}')" for e in yellows) or "None"
        red_lines = ", ".join(f"{e['player']} ({e['team']}, {e['minute']}')" for e in reds) or "None"

        h = stats.get("home", {})
        a = stats.get("away", {})

        performer_lines = "\n".join(f"  {p['player']} ({p['team']}): rated {p['rating']}/10 — {p['note']}" for p in performers)

        context = f"""MATCH REPORT
============
Competition : {game.get('competition', 'Unknown')}
Date        : {game['game_date']}
Venue       : {game.get('stadium', 'Unknown')}
Result      : {game['home_team']} {game['home_score']}–{game['away_score']} {game['away_team']}

GOAL TIMELINE
{goal_lines}

DISCIPLINARY
Yellow cards : {yellow_lines}
Red cards    : {red_lines}

MATCH STATISTICS
                         {game['home_team']:<25} {game['away_team']}
  Possession             {str(h.get('possession', '?')) + '%':<25} {a.get('possession', '?')}%
  Shots (on target)      {str(h.get('shots', '?')) + ' (' + str(h.get('shots_on_target', '?')) + ')':<25} {a.get('shots', '?')} ({a.get('shots_on_target', '?')})
  xG                     {str(h.get('xG', '?')):<25} {a.get('xG', '?')}
  Passes (accuracy)      {str(h.get('passes', '?')) + ' (' + str(h.get('pass_accuracy', '?')) + '%)':<25} {a.get('passes', '?')} ({a.get('pass_accuracy', '?')}%)
  Corners                {str(h.get('corners', '?')):<25} {a.get('corners', '?')}
  Fouls                  {str(h.get('fouls', '?')):<25} {a.get('fouls', '?')}

TOP PERFORMERS
{performer_lines}
"""

        # Run supervisor to generate multi-perspective review
        result = await supervisor.orchestrate(
            context,
            agent_tokens=agent_tokens,
            synthesis_tokens=synthesis_tokens,
            synthesis_prompt=SYNTHESIS_PROMPTS[report_format],
            depth=effective_depth,
            report_format=report_format,
            max_iterations=max_iterations,
            agent_timeout_seconds=AGENT_TIMEOUT_SECONDS,
            synthesis_timeout_seconds=SYNTHESIS_TIMEOUT_SECONDS,
        )

        # Parse and structure the review
        try:
            review_data = json.loads(result)
        except json.JSONDecodeError:
            review_data = {"raw": result}

        game_review = GameReview(
            summary=review_data.get("summary", ""),
            key_moments=review_data.get("key_moments", []),
            tactical_analysis=review_data.get("tactical_analysis", ""),
            performance_insights=review_data.get("performance_insights", ""),
            fan_perspective=review_data.get("fan_perspective", ""),
            final_verdict=review_data.get("final_verdict", ""),
        )

        # Store review
        games_store[session_id]["reviews"].append(
            {
                "timestamp": datetime.now().isoformat(),
                "review": game_review.dict(),
            }
        )

        response = GameReviewResponse(
            game_id=session_id,
            game_review=game_review,
            specialist_perspectives=review_data.get("specialist_perspectives", {}),
            conversation_history=review_data.get("conversation_history", []),
            progress=review_data.get(
                "progress",
                {
                    "status": "complete",
                    "total_steps": review_data.get("iterations", max_iterations) + 1,
                    "completed_steps": review_data.get("iterations", max_iterations) + 1,
                    "percent_complete": 100,
                    "current_step": "complete",
                    "planned_steps": review_data.get("agents_used", []) + ["Synthesis"],
                    "completed_steps_labels": review_data.get("agents_used", []) + ["Synthesis"],
                    "max_iterations": max_iterations,
                },
            ),
            metadata={
                "game_date": game["game_date"],
                "home_team": game["home_team"],
                "away_team": game["away_team"],
                "final_score": game["final_score"],
                "competition": game.get("competition", ""),
                "stadium": game.get("stadium", ""),
                "iterations": review_data.get("iterations", 4),
                "max_iterations": review_data.get("max_iterations", max_iterations),
                "agents_used": review_data.get("agents_used", ["Journalist", "Coach", "AssistantCoach", "Fan"]),
                "duration_seconds": review_data.get("duration_seconds", 0),
                "agent_timings": review_data.get("agent_timings", {}),
                "agent_metrics": review_data.get("agent_metrics", {}),
                "total_tokens": review_data.get("total_tokens", 0),
                "total_prompt_tokens": review_data.get("total_prompt_tokens", 0),
                "total_completion_tokens": review_data.get("total_completion_tokens", 0),
                "depth": effective_depth,
                "format": report_format,
            },
        )

        return response

    except ValueError as exc:
        msg = str(exc)
        if "AGENT_TIMEOUT" in msg:
            raise _api_http_exception(504, "Agent execution timed out", "AGENT_TIMEOUT", True, request_id) from exc
        if "invalid json" in msg.lower():
            raise _api_http_exception(500, "LLM returned invalid JSON", "LLM_INVALID_JSON", True, request_id) from exc
        raise _api_http_exception(400, "Invalid game ID format", "INVALID_GAME_ID", False, request_id) from exc
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise _api_http_exception(500, f"Review failed: {str(e)}", "FOLLOWUP_FAILED", True, request_id) from e


@app.post("/games/{game_id}/review/stream")
async def stream_game_review(
    request: Request,
    game_id: str,
    depth: Literal["brief", "standard", "detailed"] = Query("standard"),
    report_format: Literal["brief", "standard", "technical"] = Query("standard", alias="format"),
    max_iterations: int = Query(4, ge=1, le=4),
):
    """Stream game review progress via Server-Sent Events."""
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    try:
        depth_config = {
            "brief": {"agent": 128, "synthesis": 256},
            "standard": {"agent": 256, "synthesis": 512},
            "detailed": {"agent": 512, "synthesis": 1024},
        }
        effective_depth = depth
        agent_tokens = depth_config[effective_depth]["agent"]
        synthesis_tokens = depth_config[effective_depth]["synthesis"]

        game_index = int(game_id.split("_")[1])
        if game_index < 0 or game_index >= len(SAMPLE_GAMES):
            raise _api_http_exception(404, "Game not found", "GAME_NOT_FOUND", False, request_id)

        game = SAMPLE_GAMES[game_index]
        session_id = str(uuid.uuid4())
        games_store[session_id] = {
            "game_id": game_id,
            "game_data": game,
            "created_at": datetime.now().isoformat(),
            "settings": {
                "depth": effective_depth,
                "format": report_format,
                "max_iterations": max_iterations,
            },
            "reviews": [],
            "follow_ups": [],
        }

        # Build rich context prompt with all match details
        events = game.get("events", [])
        stats = game.get("stats", {})
        performers = game.get("top_performers", [])

        goals = [e for e in events if e["type"] == "goal"]
        yellows = [e for e in events if e["type"] == "yellow_card"]
        reds = [e for e in events if e["type"] == "red_card"]

        goal_lines = "\n".join(
            f"  {e['minute']}' {e['player']} ({e['team']})"
            + (f" — assist: {e['assist']}" if "assist" in e else "")
            + (f" [{e['note']}]" if "note" in e else "")
            for e in goals
        )
        yellow_lines = ", ".join(f"{e['player']} ({e['team']}, {e['minute']}')" for e in yellows) or "None"
        red_lines = ", ".join(f"{e['player']} ({e['team']}, {e['minute']}')" for e in reds) or "None"

        h = stats.get("home", {})
        a = stats.get("away", {})

        performer_lines = "\n".join(f"  {p['player']} ({p['team']}): rated {p['rating']}/10 — {p['note']}" for p in performers)

        context = f"""MATCH REPORT
============
Competition : {game.get('competition', 'Unknown')}
Date        : {game['game_date']}
Venue       : {game.get('stadium', 'Unknown')}
Result      : {game['home_team']} {game['home_score']}–{game['away_score']} {game['away_team']}

GOAL TIMELINE
{goal_lines}

DISCIPLINARY
Yellow cards : {yellow_lines}
Red cards    : {red_lines}

MATCH STATISTICS
                         {game['home_team']:<25} {game['away_team']}
  Possession             {str(h.get('possession', '?')) + '%':<25} {a.get('possession', '?')}%
  Shots (on target)      {str(h.get('shots', '?')) + ' (' + str(h.get('shots_on_target', '?')) + ')':<25} {a.get('shots', '?')} ({a.get('shots_on_target', '?')})
  xG                     {str(h.get('xG', '?')):<25} {a.get('xG', '?')}
  Passes (accuracy)      {str(h.get('passes', '?')) + ' (' + str(h.get('pass_accuracy', '?')) + '%)':<25} {a.get('passes', '?')} ({a.get('pass_accuracy', '?')}%)
  Corners                {str(h.get('corners', '?')):<25} {a.get('corners', '?')}
  Fouls                  {str(h.get('fouls', '?')):<25} {a.get('fouls', '?')}

TOP PERFORMERS
{performer_lines}
"""

        async def event_generator():
            if llm_client is None:
                yield f'data: {json.dumps({"type": "error", "detail": "LLM backend not available"})}\n\n'
                return

            supervisor = SupervisorAgent(llm_client)

            # Use a queue to collect streaming events
            stream_queue: asyncio.Queue = asyncio.Queue()

            async def stream_callback(event: dict):
                """Collect streaming events into queue."""
                await stream_queue.put(event)

            # Emit initial event
            yield f"data: {json.dumps({'state': 'agent_thinking', 'message': 'Initializing analysis...'})}\n\n"

            try:
                # Start supervisor task
                orchestrate_task = asyncio.create_task(
                    supervisor.orchestrate(
                        context,
                        agent_tokens=agent_tokens,
                        synthesis_tokens=synthesis_tokens,
                        synthesis_prompt=SYNTHESIS_PROMPTS[report_format],
                        depth=effective_depth,
                        report_format=report_format,
                        max_iterations=max_iterations,
                        agent_timeout_seconds=AGENT_TIMEOUT_SECONDS,
                        synthesis_timeout_seconds=SYNTHESIS_TIMEOUT_SECONDS,
                        stream_callback=stream_callback,
                    )
                )

                # Yield streaming events as they arrive
                while not orchestrate_task.done():
                    try:
                        # Wait for events with timeout
                        event = await asyncio.wait_for(stream_queue.get(), timeout=0.1)
                        yield f"data: {json.dumps(event)}\n\n"
                    except asyncio.TimeoutError:
                        # No event yet, check if task is done
                        if orchestrate_task.done():
                            break
                        await asyncio.sleep(0.05)

                # Get the final result
                result = await orchestrate_task

                # Parse and structure the complete review
                try:
                    review_data = json.loads(result)
                except json.JSONDecodeError:
                    review_data = {"raw": result}

                game_review = GameReview(
                    summary=review_data.get("summary", ""),
                    key_moments=review_data.get("key_moments", []),
                    tactical_analysis=review_data.get("tactical_analysis", ""),
                    performance_insights=review_data.get("performance_insights", ""),
                    fan_perspective=review_data.get("fan_perspective", ""),
                    final_verdict=review_data.get("final_verdict", ""),
                )

                response = GameReviewResponse(
                    game_id=session_id,
                    game_review=game_review,
                    specialist_perspectives=review_data.get("specialist_perspectives", {}),
                    conversation_history=review_data.get("conversation_history", []),
                    progress=review_data.get(
                        "progress",
                        {
                            "status": "complete",
                            "total_steps": review_data.get("iterations", max_iterations) + 1,
                            "completed_steps": review_data.get("iterations", max_iterations) + 1,
                            "percent_complete": 100,
                            "current_step": "complete",
                            "planned_steps": review_data.get("agents_used", []) + ["Synthesis"],
                            "completed_steps_labels": review_data.get("agents_used", []) + ["Synthesis"],
                            "max_iterations": max_iterations,
                        },
                    ),
                    metadata={
                        "game_date": game["game_date"],
                        "home_team": game["home_team"],
                        "away_team": game["away_team"],
                        "final_score": game["final_score"],
                        "competition": game.get("competition", ""),
                        "stadium": game.get("stadium", ""),
                        "iterations": review_data.get("iterations", 4),
                        "max_iterations": review_data.get("max_iterations", max_iterations),
                        "agents_used": review_data.get("agents_used", ["Journalist", "Coach", "AssistantCoach", "Fan"]),
                        "duration_seconds": review_data.get("duration_seconds", 0),
                        "agent_timings": review_data.get("agent_timings", {}),
                        "agent_metrics": review_data.get("agent_metrics", {}),
                        "total_tokens": review_data.get("total_tokens", 0),
                        "total_prompt_tokens": review_data.get("total_prompt_tokens", 0),
                        "total_completion_tokens": review_data.get("total_completion_tokens", 0),
                        "depth": effective_depth,
                        "format": report_format,
                    },
                )

                # Store review
                games_store[session_id]["reviews"].append(
                    {
                        "timestamp": datetime.now().isoformat(),
                        "review": game_review.dict(),
                    }
                )

                # Emit complete event
                yield f'data: {json.dumps({"state": "complete", "review": response.dict()})}\n\n'

            except ValueError as exc:
                msg = str(exc)
                if "AGENT_TIMEOUT" in msg:
                    yield f'data: {json.dumps({"state": "error", "detail": "Agent execution timed out"})}\n\n'
                elif "invalid json" in msg.lower():
                    yield f'data: {json.dumps({"state": "error", "detail": "LLM returned invalid JSON"})}\n\n'
                else:
                    yield f'data: {json.dumps({"state": "error", "detail": str(exc)})}\n\n'
            except Exception as e:
                yield f'data: {json.dumps({"state": "error", "detail": f"Streaming error: {str(e)}"})}\n\n'

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            },
        )

    except ValueError:
        raise _api_http_exception(400, "Invalid game ID format", "INVALID_GAME_ID", False, request_id)
    except HTTPException:
        raise
    except Exception as e:
        raise _api_http_exception(500, f"Streaming failed: {str(e)}", "STREAMING_FAILED", True, request_id) from e


@app.post("/games/{session_id}/ask")
async def ask_follow_up(request: Request, session_id: str, question: FollowUpQuestion):
    """Ask a follow-up question about a previously reviewed game."""
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    if session_id not in games_store:
        raise _api_http_exception(404, "Game session not found", "SESSION_NOT_FOUND", False, request_id)

    try:
        game_info = games_store[session_id]
        game_data = game_info["game_data"]
        settings = game_info.get("settings", {})
        depth = settings.get("depth", "standard")
        report_format = settings.get("format", "standard")
        max_iterations = settings.get("max_iterations", 4)
        depth_config = {
            "brief": {"agent": 128, "synthesis": 256},
            "standard": {"agent": 256, "synthesis": 512},
            "detailed": {"agent": 512, "synthesis": 1024},
        }
        agent_tokens = depth_config[depth]["agent"]
        synthesis_tokens = depth_config[depth]["synthesis"]

        # Rebuild the same rich match report for context
        events = game_data.get("events", [])
        stats = game_data.get("stats", {})
        performers = game_data.get("top_performers", [])

        goals = [e for e in events if e["type"] == "goal"]
        yellows = [e for e in events if e["type"] == "yellow_card"]
        reds = [e for e in events if e["type"] == "red_card"]

        goal_lines = "\n".join(
            f"  {e['minute']}' {e['player']} ({e['team']})"
            + (f" — assist: {e['assist']}" if "assist" in e else "")
            + (f" [{e['note']}]" if "note" in e else "")
            for e in goals
        )
        yellow_lines = ", ".join(f"{e['player']} ({e['team']}, {e['minute']}')" for e in yellows) or "None"
        red_lines = ", ".join(f"{e['player']} ({e['team']}, {e['minute']}')" for e in reds) or "None"

        h = stats.get("home", {})
        a = stats.get("away", {})

        performer_lines = "\n".join(f"  {p['player']} ({p['team']}): rated {p['rating']}/10 — {p['note']}" for p in performers)

        context = f"""MATCH REPORT
============
Competition : {game_data.get('competition', 'Unknown')}
Date        : {game_data['game_date']}
Venue       : {game_data.get('stadium', 'Unknown')}
Result      : {game_data['home_team']} {game_data['home_score']}–{game_data['away_score']} {game_data['away_team']}

GOAL TIMELINE
{goal_lines}

DISCIPLINARY
Yellow cards : {yellow_lines}
Red cards    : {red_lines}

MATCH STATISTICS
                         {game_data['home_team']:<25} {game_data['away_team']}
  Possession             {str(h.get('possession', '?')) + '%':<25} {a.get('possession', '?')}%
  Shots (on target)      {str(h.get('shots', '?')) + ' (' + str(h.get('shots_on_target', '?')) + ')':<25} {a.get('shots', '?')} ({a.get('shots_on_target', '?')})
  xG                     {str(h.get('xG', '?')):<25} {a.get('xG', '?')}
  Passes (accuracy)      {str(h.get('passes', '?')) + ' (' + str(h.get('pass_accuracy', '?')) + '%)':<25} {a.get('passes', '?')} ({a.get('pass_accuracy', '?')}%)
  Corners                {str(h.get('corners', '?')):<25} {a.get('corners', '?')}
  Fouls                  {str(h.get('fouls', '?')):<25} {a.get('fouls', '?')}

TOP PERFORMERS
{performer_lines}

FOLLOW-UP QUESTION: {question.question}
"""

        if llm_client is None:
            raise _api_http_exception(500, "LLM backend not available", "FOLLOWUP_FAILED", True, request_id)

        supervisor = SupervisorAgent(llm_client)
        result = await supervisor.orchestrate(
            context,
            agent_tokens=agent_tokens,
            synthesis_tokens=synthesis_tokens,
            synthesis_prompt=SYNTHESIS_PROMPTS[report_format],
            depth=depth,
            report_format=report_format,
            max_iterations=max_iterations,
            agent_timeout_seconds=AGENT_TIMEOUT_SECONDS,
            synthesis_timeout_seconds=SYNTHESIS_TIMEOUT_SECONDS,
            focus_question=question.question,
        )

        try:
            answer_data = json.loads(result)
        except json.JSONDecodeError:
            answer_data = {"raw": result}

        # Store follow-up
        games_store[session_id]["follow_ups"].append(
            {
                "timestamp": datetime.now().isoformat(),
                "question": question.question,
                "answer": answer_data,
            }
        )

        # Extract metrics from answer_data
        metrics_response = {
            "agent_metrics": answer_data.get("agent_metrics", {}),
            "total_tokens": answer_data.get("total_tokens", 0),
            "total_prompt_tokens": answer_data.get("total_prompt_tokens", 0),
            "total_completion_tokens": answer_data.get("total_completion_tokens", 0),
        }

        return {
            "session_id": session_id,
            "question": question.question,
            "answer": {
                "summary": answer_data.get("summary", ""),
            },
            "metrics": metrics_response,
            "metadata": {
                "game_date": game_data["game_date"],
                "home_team": game_data["home_team"],
                "away_team": game_data["away_team"],
                "final_score": game_data["final_score"],
                "depth": depth,
                "format": report_format,
                "max_iterations": max_iterations,
            },
        }

    except ValueError as exc:
        if "AGENT_TIMEOUT" in str(exc):
            raise _api_http_exception(504, "Follow-up timed out", "AGENT_TIMEOUT", True, request_id) from exc
        raise _api_http_exception(500, f"Follow-up failed: {str(exc)}", "FOLLOWUP_FAILED", True, request_id) from exc
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise _api_http_exception(500, f"Follow-up failed: {str(e)}", "FOLLOWUP_FAILED", True, request_id) from e


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
