"""Tests for agent performance metrics spec."""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestAgentMetrics:
    """Test suite for agent performance metrics feature."""

    def test_review_response_includes_agent_metrics(self):
        """GIVEN a successful POST /games/game_0/review
        WHEN the response arrives
        THEN metadata.agent_metrics exists
        AND it includes one entry per executed agent plus Synthesis."""
        response = client.post("/games/game_0/review?depth=standard&format=standard&max_iterations=4")
        assert response.status_code == 200

        data = response.json()
        assert "metadata" in data
        assert "agent_metrics" in data["metadata"]

        metrics = data["metadata"]["agent_metrics"]
        assert len(metrics) > 0
        # Should have Journalist, Coach, AssistantCoach, Fan, and Synthesis for max_iterations=4
        assert "Synthesis" in metrics
        assert "Journalist" in metrics

    def test_agent_metric_has_required_fields(self):
        """GIVEN metadata.agent_metrics.Journalist
        WHEN inspected
        THEN it has duration_ms, prompt_tokens, completion_tokens, and total_tokens
        AND total_tokens == prompt_tokens + completion_tokens."""
        response = client.post("/games/game_0/review?depth=standard&format=standard")
        assert response.status_code == 200

        data = response.json()
        journalist_metric = data["metadata"]["agent_metrics"]["Journalist"]

        assert "duration_ms" in journalist_metric
        assert "prompt_tokens" in journalist_metric
        assert "completion_tokens" in journalist_metric
        assert "total_tokens" in journalist_metric

        # Verify total equals sum
        assert journalist_metric["total_tokens"] == journalist_metric["prompt_tokens"] + journalist_metric["completion_tokens"]

    def test_total_tokens_equals_sum_of_agent_metrics(self):
        """GIVEN a successful review response
        WHEN metadata.total_tokens is inspected
        THEN it equals the sum of all agent_metrics[*].total_tokens values."""
        response = client.post("/games/game_0/review?depth=standard&format=standard")
        assert response.status_code == 200

        data = response.json()
        metadata = data["metadata"]
        metrics = metadata["agent_metrics"]

        computed_total = sum(m["total_tokens"] for m in metrics.values())
        assert metadata["total_tokens"] == computed_total

    def test_max_iterations_affects_agent_metrics(self):
        """GIVEN max_iterations=2
        WHEN a review is created
        THEN metadata.agent_metrics contains Journalist, Coach, and Synthesis
        AND does not contain AssistantCoach or Fan."""
        response = client.post("/games/game_0/review?depth=standard&format=standard&max_iterations=2")
        assert response.status_code == 200

        data = response.json()
        metrics = data["metadata"]["agent_metrics"]

        # With max_iterations=2, only Journalist and Coach should run
        assert "Journalist" in metrics
        assert "Coach" in metrics
        assert "Synthesis" in metrics

        # These should not be present
        assert "AssistantCoach" not in metrics
        assert "Fan" not in metrics

    def test_follow_up_response_includes_metrics(self):
        """GIVEN a successful POST /games/{session_id}/ask
        WHEN the response arrives
        THEN a top-level metrics block is present
        AND it contains aggregate token totals and per-agent metrics."""
        # First create a review to get a session_id
        review_response = client.post("/games/game_0/review")
        assert review_response.status_code == 200
        session_id = review_response.json()["game_id"]

        # Now ask a follow-up question
        followup_response = client.post(
            f"/games/{session_id}/ask",
            json={"question": "What was the most significant tactical decision?"},
        )
        assert followup_response.status_code == 200

        data = followup_response.json()
        assert "metrics" in data
        assert "agent_metrics" in data["metrics"]
        assert "total_tokens" in data["metrics"]
        assert "total_prompt_tokens" in data["metrics"]
        assert "total_completion_tokens" in data["metrics"]

    def test_prompt_completion_token_sum(self):
        """GIVEN any agent metric
        WHEN inspected
        THEN prompt_tokens + completion_tokens == total_tokens."""
        response = client.post("/games/game_0/review")
        assert response.status_code == 200

        data = response.json()
        metrics = data["metadata"]["agent_metrics"]

        for agent_name, metric in metrics.items():
            expected_total = metric["prompt_tokens"] + metric["completion_tokens"]
            assert metric["total_tokens"] == expected_total, (
                f"{agent_name}: {metric['prompt_tokens']} + {metric['completion_tokens']} " f"!= {metric['total_tokens']}"
            )

    def test_token_counts_are_positive(self):
        """GIVEN any agent metric
        WHEN inspected
        THEN all token counts are non-negative integers."""
        response = client.post("/games/game_0/review")
        assert response.status_code == 200

        data = response.json()
        metrics = data["metadata"]["agent_metrics"]

        for _, metric in metrics.items():
            assert isinstance(metric["prompt_tokens"], int) and metric["prompt_tokens"] >= 0
            assert isinstance(metric["completion_tokens"], int) and metric["completion_tokens"] >= 0
            assert isinstance(metric["total_tokens"], int) and metric["total_tokens"] >= 0

    def test_duration_ms_present_for_all_agents(self):
        """GIVEN a complete review response
        WHEN agent_metrics are inspected
        THEN every agent has a duration_ms field."""
        response = client.post("/games/game_0/review")
        assert response.status_code == 200

        data = response.json()
        metrics = data["metadata"]["agent_metrics"]

        for _, metric in metrics.items():
            assert "duration_ms" in metric
            assert isinstance(metric["duration_ms"], int)
            assert metric["duration_ms"] >= 0

    def test_multiple_depth_levels_have_different_metrics(self):
        """GIVEN reviews at different depth levels
        WHEN compared
        THEN they have different token usage patterns."""
        brief_response = client.post("/games/game_0/review?depth=brief")
        detailed_response = client.post("/games/game_0/review?depth=detailed")

        assert brief_response.status_code == 200
        assert detailed_response.status_code == 200

        brief_tokens = brief_response.json()["metadata"]["total_tokens"]
        detailed_tokens = detailed_response.json()["metadata"]["total_tokens"]

        # Detailed should generally use more tokens than brief
        assert detailed_tokens > brief_tokens

    def test_health_check_still_works(self):
        """GIVEN GET /health
        WHEN called
        THEN returns 200 with {status: 'ok'}."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
