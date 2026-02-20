"""
Tests for ProductionAgent class.

Tests agent query processing, confidence calculation, reasoning extraction,
error handling, and integration with supporting components.
"""
import pytest
from unittest.mock import Mock, patch
from anthropic import APIError, RateLimitError
import time


class TestProductionAgent:
    """Test suite for ProductionAgent."""

    @pytest.mark.asyncio
    async def test_process_basic_query(self, production_agent, sample_query):
        """Test basic query processing."""
        result = await production_agent.process(query=sample_query)

        assert "response" in result
        assert isinstance(result["response"], str)
        assert len(result["response"]) > 0
        assert result["confidence"] >= 0 and result["confidence"] <= 1
        assert "reasoning" in result
        assert "cost" in result
        assert result["cost"] >= 0
        assert "latency_ms" in result

    @pytest.mark.asyncio
    async def test_process_with_context(self, production_agent, sample_query, sample_context):
        """Test query processing with context."""
        result = await production_agent.process(
            query=sample_query,
            context=sample_context
        )

        assert "response" in result
        assert result["response"] is not None
        # Verify context was included in the request
        agent_client = production_agent.client
        assert agent_client.messages.create.called

    @pytest.mark.asyncio
    async def test_process_with_user_id(self, production_agent, sample_query):
        """Test query processing with user ID."""
        user_id = "test_user_456"

        result = await production_agent.process(
            query=sample_query,
            user_id=user_id
        )

        assert result is not None
        assert "audit_id" in result

    @pytest.mark.asyncio
    async def test_confidence_calculation(self, production_agent):
        """Test confidence score calculation."""
        result = await production_agent.process(
            query="What is 2+2?"
        )

        # Confidence should be a float between 0 and 1
        assert isinstance(result["confidence"], float)
        assert 0.0 <= result["confidence"] <= 1.0

    @pytest.mark.asyncio
    async def test_reasoning_extraction(self, production_agent):
        """Test reasoning extraction from response."""
        result = await production_agent.process(
            query="Explain why the sky is blue."
        )

        assert "reasoning" in result
        assert isinstance(result["reasoning"], str)

    @pytest.mark.asyncio
    async def test_cost_calculation(self, production_agent):
        """Test cost calculation from token usage."""
        result = await production_agent.process(
            query="Short query"
        )

        assert "cost" in result
        assert result["cost"] > 0
        # Cost should be reasonable (input + output)
        # For ~100 input tokens and ~50 output tokens:
        # (100/1M * $3) + (50/1M * $15) = $0.0003 + $0.00075 = $0.00105
        assert result["cost"] < 0.1  # Sanity check

    @pytest.mark.asyncio
    async def test_latency_tracking(self, production_agent):
        """Test latency measurement."""
        start = time.time()
        result = await production_agent.process(
            query="Test query"
        )
        end = time.time()

        elapsed_ms = (end - start) * 1000

        assert "latency_ms" in result
        # Latency should be positive and reasonable
        assert result["latency_ms"] > 0
        assert result["latency_ms"] < elapsed_ms + 100  # Allow some overhead

    @pytest.mark.asyncio
    async def test_bias_detection_integration(self, production_agent, bias_detector):
        """Test integration with bias detector."""
        # Mock bias detector to return positive result
        bias_detector.detect_bias = Mock(return_value={
            "has_bias": True,
            "score": 0.75,
            "bias_types": ["gender"]
        })

        production_agent.bias_detector = bias_detector

        result = await production_agent.process(
            query="Test query with potential bias"
        )

        assert "bias_detected" in result
        assert "bias_score" in result

    @pytest.mark.asyncio
    async def test_bias_detection_disabled(self, mock_anthropic_client):
        """Test agent without bias detection."""
        from src.agent import ProductionAgent

        agent = ProductionAgent(
            api_key="test_key",
            bias_detector=None  # Disabled
        )
        agent.client = mock_anthropic_client

        result = await agent.process(query="Test query")

        assert result["bias_detected"] is False
        assert result["bias_score"] == 0.0

    @pytest.mark.asyncio
    async def test_audit_trail_logging(self, production_agent, mock_audit_trail):
        """Test audit trail logging."""
        result = await production_agent.process(
            query="Test audit logging",
            user_id="audit_user"
        )

        # Verify audit trail was called
        assert mock_audit_trail.log_decision.called
        call_args = mock_audit_trail.log_decision.call_args

        assert call_args[1]["action_type"] == "agent_query"
        assert "query" in call_args[1]["input_data"]
        assert call_args[1]["actor"] == "audit_user"

        assert result["audit_id"] == "audit_test_123"

    @pytest.mark.asyncio
    async def test_audit_trail_disabled(self, mock_anthropic_client):
        """Test agent without audit trail."""
        from src.agent import ProductionAgent

        agent = ProductionAgent(
            api_key="test_key",
            audit_trail=None  # Disabled
        )
        agent.client = mock_anthropic_client

        result = await agent.process(query="Test query")

        assert result["audit_id"] is None

    @pytest.mark.asyncio
    async def test_error_handling_api_error(self, mock_anthropic_client):
        """Test error handling for API errors."""
        from src.agent import ProductionAgent

        # Configure client to raise error
        mock_anthropic_client.messages.create.side_effect = APIError(
            message="API Error",
            request=Mock(),
            body={}
        )

        agent = ProductionAgent(api_key="test_key")
        agent.client = mock_anthropic_client

        with pytest.raises(APIError):
            await agent.process(query="Test query")

    @pytest.mark.asyncio
    async def test_error_handling_rate_limit(self, mock_anthropic_client):
        """Test error handling for rate limit errors."""
        from src.agent import ProductionAgent

        # Configure client to raise rate limit error
        mock_anthropic_client.messages.create.side_effect = RateLimitError(
            message="Rate limit exceeded",
            response=Mock(status_code=429),
            body={}
        )

        agent = ProductionAgent(api_key="test_key")
        agent.client = mock_anthropic_client

        with pytest.raises(RateLimitError):
            await agent.process(query="Test query")

    @pytest.mark.asyncio
    async def test_empty_query_handling(self, production_agent):
        """Test handling of empty queries."""
        # This should be validated before reaching the agent
        # But test agent behavior if it receives empty query
        result = await production_agent.process(query="")

        # Agent should still process (API will handle validation)
        assert "response" in result

    @pytest.mark.asyncio
    async def test_long_query_handling(self, production_agent):
        """Test handling of very long queries."""
        long_query = "What is the meaning of life? " * 500  # ~3500 chars

        result = await production_agent.process(query=long_query)

        assert "response" in result
        assert result["cost"] > 0  # Should cost more due to tokens

    @pytest.mark.asyncio
    async def test_special_characters_in_query(self, production_agent):
        """Test handling of special characters."""
        special_query = "What about émojis 😀 and symbols: @#$%^&*()?!"

        result = await production_agent.process(query=special_query)

        assert "response" in result
        assert len(result["response"]) > 0

    @pytest.mark.asyncio
    async def test_calculate_cost_accuracy(self, production_agent):
        """Test cost calculation accuracy."""
        # Create mock usage
        mock_usage = Mock()
        mock_usage.input_tokens = 1000
        mock_usage.output_tokens = 500

        cost = production_agent._calculate_cost(mock_usage)

        # Expected: (1000/1M * $3) + (500/1M * $15)
        # = $0.003 + $0.0075 = $0.0105
        expected_cost = 0.0105
        assert abs(cost - expected_cost) < 0.0001

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, production_agent):
        """Test handling of concurrent requests."""
        import asyncio

        queries = [
            "Query 1",
            "Query 2",
            "Query 3",
        ]

        # Process queries concurrently
        results = await asyncio.gather(*[
            production_agent.process(query=q)
            for q in queries
        ])

        assert len(results) == 3
        for result in results:
            assert "response" in result
            assert result["response"] is not None
