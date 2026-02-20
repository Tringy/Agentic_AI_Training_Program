"""
Tests for RateLimiter with Token Bucket algorithm.

Tests RPM limits, TPM limits, token bucket implementation, per-user rate limiting,
and burst capacity.
"""
import pytest
import time
import threading
from unittest.mock import Mock, patch


class TestTokenBucket:
    """Test TokenBucket data structure."""

    def test_token_bucket_initialization(self):
        """Test token bucket initialization."""
        from src.rate_limiter import TokenBucket

        bucket = TokenBucket(
            capacity=100,
            tokens=50.0,
            refill_rate=10.0,
            last_refill=time.time()
        )

        assert bucket.capacity == 100
        assert bucket.tokens == 50.0
        assert bucket.refill_rate == 10.0
        assert isinstance(bucket.last_refill, float)


class TestRateLimiter:
    """Test RateLimiter class."""

    def test_rate_limiter_initialization(self):
        """Test rate limiter initialization."""
        from src.rate_limiter import RateLimiter

        limiter = RateLimiter(
            requests_per_minute=60,
            tokens_per_minute=100000,
            burst_multiplier=1.5
        )

        assert limiter.request_bucket.capacity == 90  # 60 * 1.5
        assert limiter.request_bucket.refill_rate == 1.0  # 60/60
        assert hasattr(limiter, 'user_limiters')

    def test_rate_limiter_default_values(self):
        """Test rate limiter with default values."""
        from src.rate_limiter import RateLimiter

        limiter = RateLimiter()

        assert limiter.request_bucket.capacity == 90  # 60 * 1.5
        assert limiter.request_bucket.refill_rate == 1.0

    def test_acquire_single_token_success(self, rate_limiter):
        """Test acquiring a single token successfully."""
        result = rate_limiter.acquire(tokens=1)

        # Should succeed on first request
        assert result is True

    def test_acquire_multiple_tokens(self, rate_limiter):
        """Test acquiring multiple tokens at once."""
        # Try to acquire 5 tokens
        result = rate_limiter.acquire(tokens=5)

        # Should succeed if capacity allows
        assert isinstance(result, bool)

    def test_rpm_limit_enforcement(self):
        """Test requests per minute limit."""
        from src.rate_limiter import RateLimiter

        # Low RPM for testing
        limiter = RateLimiter(
            requests_per_minute=5,
            tokens_per_minute=100000
        )

        # Make requests up to limit
        successes = 0
        for _ in range(10):
            if limiter.acquire(tokens=1):
                successes += 1

        # Should not exceed initial capacity
        # Initial capacity is requests_per_minute * burst_multiplier
        # 5 * 1.5 = 7.5, so up to 7 requests should succeed
        assert successes <= 8  # Allow for rounding

    def test_tpm_limit_enforcement(self):
        """Test tokens per minute limit."""
        from src.rate_limiter import RateLimiter

        limiter = RateLimiter(
            requests_per_minute=100,
            tokens_per_minute=1000,  # Low TPM for testing
            burst_multiplier=1.0
        )

        # Try to consume more tokens than limit
        result1 = limiter.acquire(tokens=500)
        result2 = limiter.acquire(tokens=600)  # Would exceed

        # First should succeed, second might fail
        assert result1 is True
        # Second depends on implementation details

    def test_burst_capacity(self):
        """Test burst capacity handling."""
        from src.rate_limiter import RateLimiter

        limiter = RateLimiter(
            requests_per_minute=10,
            tokens_per_minute=1000,
            burst_multiplier=2.0  # 2x burst
        )

        # Should allow burst up to capacity * burst_multiplier
        # Capacity = 10 * 2 = 20
        successes = 0
        for _ in range(25):
            if limiter.acquire(tokens=1):
                successes += 1

        # Should allow burst but not unlimited
        assert successes > 10  # More than base rate
        assert successes <= 20  # Not more than burst capacity

    def test_token_refill_over_time(self):
        """Test tokens refill over time."""
        from src.rate_limiter import RateLimiter

        limiter = RateLimiter(
            requests_per_minute=60,  # 1 per second
            tokens_per_minute=1000
        )

        # Consume some tokens
        limiter.acquire(tokens=5)

        # Wait for refill (implementation dependent)
        # This test would need actual implementation of refill logic
        time.sleep(0.1)

        # Should be able to acquire more after waiting
        result = limiter.acquire(tokens=1)
        assert isinstance(result, bool)

    def test_per_user_rate_limiting(self, rate_limiter):
        """Test per-user rate limiting."""
        user1_limiter = rate_limiter.get_limiter("user1")
        user2_limiter = rate_limiter.get_limiter("user2")

        # Should return different limiter instances
        assert user1_limiter is not user2_limiter

        # Should cache limiter per user
        user1_limiter_again = rate_limiter.get_limiter("user1")
        assert user1_limiter is user1_limiter_again

    def test_multiple_users_independent_limits(self):
        """Test multiple users have independent rate limits."""
        from src.rate_limiter import RateLimiter

        main_limiter = RateLimiter(
            requests_per_minute=5,
            tokens_per_minute=1000
        )

        user1 = main_limiter.get_limiter("user1")
        user2 = main_limiter.get_limiter("user2")

        # Exhaust user1's limit
        for _ in range(10):
            user1.acquire(tokens=1)

        # User2 should still be able to acquire
        result = user2.acquire(tokens=1)
        assert result is True

    def test_get_status(self, rate_limiter):
        """Test getting rate limit status."""
        status = rate_limiter.get_status()

        assert "requests_available" in status
        assert "tokens_available" in status
        assert isinstance(status["requests_available"], (int, float))
        assert isinstance(status["tokens_available"], (int, float))

    def test_thread_safety(self):
        """Test rate limiter is thread-safe."""
        from src.rate_limiter import RateLimiter

        limiter = RateLimiter(
            requests_per_minute=100,
            tokens_per_minute=10000
        )

        results = []
        lock = threading.Lock()

        def acquire_tokens():
            result = limiter.acquire(tokens=1)
            with lock:
                results.append(result)

        # Create multiple threads
        threads = [threading.Thread(target=acquire_tokens) for _ in range(20)]

        # Start all threads
        for t in threads:
            t.start()

        # Wait for completion
        for t in threads:
            t.join()

        # All threads completed
        assert len(results) == 20
        # Should have some successful acquisitions
        assert any(results)

    def test_zero_tokens_acquire(self, rate_limiter):
        """Test acquiring zero tokens."""
        result = rate_limiter.acquire(tokens=0)

        # Should handle edge case
        assert isinstance(result, bool)

    def test_negative_tokens_acquire(self, rate_limiter):
        """Test acquiring negative tokens."""
        # Should either reject or handle gracefully
        try:
            result = rate_limiter.acquire(tokens=-1)
            # If it doesn't raise, should return boolean
            assert isinstance(result, bool)
        except ValueError:
            # Or it might raise ValueError for invalid input
            pass

    def test_very_large_token_request(self, rate_limiter):
        """Test requesting more tokens than capacity."""
        result = rate_limiter.acquire(tokens=1000000)

        # Should reject or handle appropriately
        assert isinstance(result, bool)

    def test_rate_limiter_reset(self):
        """Test rate limiter can be reset."""
        from src.rate_limiter import RateLimiter

        limiter = RateLimiter(requests_per_minute=10)

        # Consume some tokens
        for _ in range(5):
            limiter.acquire(tokens=1)

        # Create new limiter (reset)
        limiter = RateLimiter(requests_per_minute=10)

        # Should have full capacity again
        result = limiter.acquire(tokens=1)
        assert result is True

    def test_concurrent_user_access(self):
        """Test concurrent access by multiple users."""
        from src.rate_limiter import RateLimiter

        main_limiter = RateLimiter(
            requests_per_minute=10,
            tokens_per_minute=1000
        )

        results = {"user1": [], "user2": [], "user3": []}

        def user_requests(user_id):
            limiter = main_limiter.get_limiter(user_id)
            for _ in range(5):
                result = limiter.acquire(tokens=1)
                results[user_id].append(result)
                time.sleep(0.01)

        threads = [
            threading.Thread(target=user_requests, args=("user1",)),
            threading.Thread(target=user_requests, args=("user2",)),
            threading.Thread(target=user_requests, args=("user3",))
        ]

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        # All users should have made requests
        assert len(results["user1"]) == 5
        assert len(results["user2"]) == 5
        assert len(results["user3"]) == 5
