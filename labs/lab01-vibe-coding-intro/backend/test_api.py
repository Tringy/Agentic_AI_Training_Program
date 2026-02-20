"""
Basic integration tests for URL Shortener API.

To run these tests:
  pip install pytest
  pytest tests/test_api.py -v
"""

import os
import sqlite3
import sys
import tempfile
from pathlib import Path

import pytest

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

# Set test database path
test_db_dir = tempfile.mkdtemp()
os.environ["DATABASE_PATH"] = test_db_dir

from fastapi.testclient import TestClient
from main import app, cache, init_db

client = TestClient(app)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Initialize test database before running tests."""
    init_db()
    yield
    # Cleanup is optional - temp directory will be removed by system


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear cache before each test."""
    cache.clear()
    yield


class TestBasicEndpoints:
    """Test basic API endpoints."""

    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_shorten_valid_url(self):
        """Test shortening a valid URL."""
        response = client.post("/shorten", json={"url": "https://example.com/test"})
        assert response.status_code == 201
        data = response.json()
        assert "short_code" in data
        assert "short_url" in data
        assert len(data["short_code"]) == 6

    def test_shorten_invalid_url(self):
        """Test that invalid URLs are rejected."""
        response = client.post("/shorten", json={"url": "not-a-url"})
        assert response.status_code == 422

    def test_redirect_to_shortened_url(self):
        """Test redirecting to original URL."""
        # Create shortened URL
        create_response = client.post("/shorten", json={"url": "https://example.com/redirect-test"})
        code = create_response.json()["short_code"]

        # Redirect
        response = client.get(f"/{code}", follow_redirects=False)
        assert response.status_code == 307
        assert "example.com/redirect-test" in response.headers["location"]

    def test_redirect_nonexistent(self):
        """Test that redirecting to nonexistent code returns 404."""
        response = client.get("/nonexistent404")
        assert response.status_code == 404

    def test_get_url_info(self):
        """Test GET /info/{code} endpoint."""
        # Create shortened URL
        create_response = client.post("/shorten", json={"url": "https://example.com/info-test"})
        code = create_response.json()["short_code"]

        # Get info
        response = client.get(f"/info/{code}")
        assert response.status_code == 200
        data = response.json()
        assert data["short_code"] == code
        assert "example.com/info-test" in data["original_url"]


class TestCaching:
    """Test LRU caching functionality."""

    def test_cache_stats(self):
        """Test cache statistics endpoint."""
        response = client.get("/api/cache-stats")
        assert response.status_code == 200
        stats = response.json()
        assert "hits" in stats
        assert "misses" in stats
        assert "hit_rate" in stats

    def test_cache_hit_improves_performance(self):
        """Test that multiple accesses to the same URL work correctly."""
        # Create a URL
        response = client.post("/shorten", json={"url": "https://example.com/cache-test"})
        assert response.status_code == 201
        code = response.json()["short_code"]

        # First access
        response1 = client.get(f"/{code}", follow_redirects=False)
        assert response1.status_code == 307

        # Second access (cached)
        response2 = client.get(f"/{code}", follow_redirects=False)
        assert response2.status_code == 307

        # Both should redirect to the same location
        assert response1.headers["location"] == response2.headers["location"]

    def test_cache_clear(self):
        """Test cache clearing."""
        response = client.post("/api/cache-clear")
        assert response.status_code == 200
        assert "message" in response.json()


class TestAnalytics:
    """Test analytics functionality."""

    def test_analytics_endpoint(self):
        """Test GET /api/analytics endpoint."""
        response = client.get("/api/analytics?page=1&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert "total_urls" in data
        assert "total_clicks" in data
        assert "urls" in data

    def test_analytics_for_specific_code(self):
        """Test GET /api/analytics/{code} endpoint."""
        # Create URL
        response = client.post("/shorten", json={"url": "https://example.com/analytics-test"})
        code = response.json()["short_code"]

        # Get analytics
        response = client.get(f"/api/analytics/{code}")
        assert response.status_code == 200
        data = response.json()
        assert data["short_code"] == code
        assert data["click_count"] == 0

    def test_click_tracking(self):
        """Test that clicks are tracked."""
        # Create URL
        response = client.post("/shorten", json={"url": "https://example.com/click-test"})
        code = response.json()["short_code"]

        # Access the URL (should record a click)
        client.get(f"/{code}", follow_redirects=False)

        # Check analytics
        response = client.get(f"/api/analytics/{code}")
        assert response.status_code == 200
        assert response.json()["click_count"] >= 1


class TestCustomCodes:
    """Test custom code functionality."""

    def test_custom_code_valid(self):
        """Test shortening with a valid custom code."""
        response = client.post("/shorten", json={"url": "https://example.com/custom-test", "custom_code": "mycode"})
        assert response.status_code == 201
        data = response.json()
        assert data["short_code"] == "mycode"

    def test_custom_code_duplicate(self):
        """Test that duplicate custom codes are rejected."""
        # First URL
        client.post("/shorten", json={"url": "https://example.com/first", "custom_code": "taken"})

        # Second URL with same custom code
        response = client.post("/shorten", json={"url": "https://example.com/second", "custom_code": "taken"})
        assert response.status_code == 409

    def test_custom_code_invalid_format(self):
        """Test that invalid custom codes are rejected."""
        response = client.post("/shorten", json={"url": "https://example.com/invalid", "custom_code": "12"})  # Too short
        assert response.status_code == 422

    def test_custom_code_reserved(self):
        """Test that reserved words are rejected."""
        response = client.post("/shorten", json={"url": "https://example.com/reserved", "custom_code": "api"})
        assert response.status_code == 422


class TestDeletion:
    """Test URL deletion functionality."""

    def test_delete_url(self):
        """Test DELETE /{code} endpoint."""
        # Create URL
        response = client.post("/shorten", json={"url": "https://example.com/delete-test"})
        code = response.json()["short_code"]

        # Delete
        response = client.delete(f"/{code}")
        assert response.status_code == 200
        assert "Successfully deleted" in response.json()["message"]

        # Verify it's deleted
        response = client.get(f"/{code}")
        assert response.status_code == 404


class TestQRCode:
    """Test QR code generation."""

    def test_qrcode_generation(self):
        """Test QR code generation endpoint."""
        # Create URL
        response = client.post("/shorten", json={"url": "https://example.com/qr-test"})
        code = response.json()["short_code"]

        # Get QR code
        response = client.get(f"/api/qrcode/{code}")
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/png"

    def test_qrcode_nonexistent(self):
        """Test QR code for nonexistent code."""
        response = client.get("/api/qrcode/nonexistent")
        assert response.status_code == 404


class TestRateLimiting:
    """Test rate limiting functionality."""

    def test_rate_limit_stats(self):
        """Test rate limit statistics endpoint."""
        response = client.get("/api/rate-limit-stats")
        assert response.status_code == 200
        data = response.json()
        assert "rate_limit_requests" in data
        assert "rate_limit_window_seconds" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
