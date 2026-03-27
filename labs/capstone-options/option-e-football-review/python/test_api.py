"""Tests for the Football Game Review API."""

import json
import os
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

os.environ.setdefault("GOOGLE_API_KEY", "test-key")

from main import app


@pytest.mark.asyncio
async def test_health_endpoint():
    """Test health check endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_list_games():
    """Test listing available games."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/games")
        assert response.status_code == 200
        data = response.json()
        assert "games" in data
        assert len(data["games"]) == 4

        # Verify game structure
        game = data["games"][0]
        assert "id" in game
        assert "date" in game
        assert "home_team" in game
        assert "away_team" in game
        assert "final_score" in game
        assert "competition" in game
        assert "stadium" in game


@pytest.mark.asyncio
async def test_create_game_review_success():
    """Test successful game review creation."""
    mock_response = {
        "summary": "Manchester United dominated the match",
        "key_moments": ["United goal", "Liverpool equalizer", "Winning goal"],
        "tactical_analysis": "United controlled midfield",
        "performance_insights": "Strong defensive performance",
        "fan_perspective": "Exciting match!",
        "final_verdict": "United deserved the win",
    }

    with patch("main.SupervisorAgent") as mock_supervisor_class:
        mock_supervisor = AsyncMock()
        mock_supervisor.orchestrate = AsyncMock(return_value=json.dumps(mock_response))
        mock_supervisor_class.return_value = mock_supervisor

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/games/game_0/review")

        assert response.status_code == 200
        data = response.json()
        assert "game_id" in data
        assert "game_review" in data
        assert data["game_review"]["summary"] == "Manchester United dominated the match"
        assert "specialist_perspectives" in data
        assert "metadata" in data
        assert data["metadata"]["home_team"] == "Manchester United"


@pytest.mark.asyncio
async def test_game_not_found():
    """Test request for non-existent game."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/games/game_999/review")
        assert response.status_code == 404
        assert "Game not found" in response.text


@pytest.mark.asyncio
async def test_invalid_game_id_format():
    """Test invalid game ID format."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/games/invalid/review")
        assert response.status_code == 400


@pytest.mark.asyncio
async def test_ask_follow_up_success():
    """Test successful follow-up question."""
    # First create a review
    mock_review_response = {
        "summary": "Manchester United dominated",
        "key_moments": ["Goal"],
        "tactical_analysis": "Good tactics",
        "performance_insights": "Good performance",
        "fan_perspective": "Great match!",
        "final_verdict": "Well deserved",
    }

    with patch("main.SupervisorAgent") as mock_supervisor_class:
        mock_supervisor = AsyncMock()
        mock_supervisor.orchestrate = AsyncMock(return_value=json.dumps(mock_review_response))
        mock_supervisor_class.return_value = mock_supervisor

        async with AsyncClient(app=app, base_url="http://test") as client:
            # Create review
            response = await client.post("/games/game_0/review")
            data = response.json()
            session_id = data["game_id"]

            # Ask follow-up question
            mock_answer = {"answer": "The defense was excellent in the second half"}
            mock_supervisor.orchestrate = AsyncMock(return_value=json.dumps(mock_answer))

            response = await client.post(f"/games/{session_id}/ask", json={"question": "How was the defense?"})

        assert response.status_code == 200
        data = response.json()
        assert data["question"] == "How was the defense?"
        assert "answer" in data


@pytest.mark.asyncio
async def test_ask_follow_up_session_not_found():
    """Test follow-up on non-existent session."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/games/invalid_session/ask", json={"question": "What happened?"})
        assert response.status_code == 404
        assert "Game session not found" in response.text


@pytest.mark.asyncio
async def test_review_game_timeout():
    """Test timeout handling during review."""
    with patch("main.SupervisorAgent") as mock_supervisor_class:
        mock_supervisor = AsyncMock()
        mock_supervisor.orchestrate = AsyncMock(side_effect=TimeoutError())
        mock_supervisor_class.return_value = mock_supervisor

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/games/game_0/review")

        assert response.status_code == 500


async def test_review_game_with_optional_context():
    """Test review with optional context field."""
    request_data = {
        "game_date": "2024-03-24",
        "home_team": "Liverpool",
        "away_team": "Chelsea",
        "home_score": 1,
        "away_score": 1,
        "final_score": "1-1",
        "review_question": "How well did Liverpool defend the title?",
        # context is optional, omit it
    }

    mock_response = {
        "game_review": {
            "summary": "Liverpool draw with Chelsea",
            "key_moments": ["No decisive moment"],
            "tactical_analysis": "Balanced match",
            "performance_insights": "Both teams fought hard",
            "fan_perspective": "Disappointing draw",
            "final_verdict": "Fair result",
        },
        "specialist_perspectives": {
            "journalist": "Evenly matched...",
            "coach": "Neither team dominated...",
            "assistant_coach": "Solid performances...",
            "fan": "Expected more...",
        },
        "conversation_history": [],
        "metadata": {
            "iterations": 2,
            "agents_used": ["Journalist", "Coach", "AssistantCoach", "Fan"],
            "game_info": ["Liverpool", "Chelsea", "1-1"],
            "duration_seconds": 32.1,
        },
    }

    with patch("main.SupervisorAgent") as mock_supervisor_class:
        mock_supervisor = AsyncMock()
        mock_supervisor.run = AsyncMock(return_value=mock_response)
        mock_supervisor_class.return_value = mock_supervisor

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/review", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["game_review"]["summary"] == "Liverpool draw with Chelsea"
