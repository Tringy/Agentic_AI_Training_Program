"""
API Tests

Basic tests for API endpoints.
Run with: pytest tests/
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "docs" in data


def test_list_models():
    """Test models endpoint."""
    response = client.get("/api/models")
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    assert len(data["models"]) > 0


def test_api_status():
    """Test API status endpoint."""
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "operational"
    assert "endpoints" in data


def test_chat_validation():
    """Test chat endpoint input validation."""
    # Missing required field
    response = client.post("/api/chat", json={})
    assert response.status_code == 422

    # Invalid max_tokens
    response = client.post(
        "/api/chat",
        json={"message": "Hello", "max_tokens": -1}
    )
    assert response.status_code == 422

    # Invalid temperature
    response = client.post(
        "/api/chat",
        json={"message": "Hello", "temperature": 3.0}
    )
    assert response.status_code == 422


@pytest.mark.skipif(
    not pytest.config.getoption("--run-integration"),
    reason="Requires ANTHROPIC_API_KEY"
)
def test_chat_integration():
    """
    Integration test for chat endpoint.

    Run with: pytest --run-integration
    Requires ANTHROPIC_API_KEY in environment
    """
    response = client.post(
        "/api/chat",
        json={
            "message": "Say hello in one word",
            "max_tokens": 50
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "model" in data
    assert "tokens_used" in data
    assert len(data["message"]) > 0


def pytest_addoption(parser):
    """Add custom pytest options."""
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="Run integration tests that require API keys"
    )
