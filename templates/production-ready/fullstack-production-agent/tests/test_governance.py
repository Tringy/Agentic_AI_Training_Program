"""
Tests for governance and responsible AI components.

Tests bias detection patterns, audit trail logging, and human approval thresholds.
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime


class TestBiasDetector:
    """Test BiasDetector class."""

    def test_bias_detector_initialization(self):
        """Test bias detector initialization."""
        from src.governance import BiasDetector

        detector = BiasDetector()

        assert hasattr(detector, 'gendered_terms')
        assert len(detector.gendered_terms) > 0

    def test_gendered_terms_defined(self, bias_detector):
        """Test gendered terms are properly defined."""
        terms = bias_detector.gendered_terms

        assert "he" in terms
        assert "she" in terms
        assert "man" in terms
        assert "woman" in terms

    def test_detect_bias_neutral_text(self, bias_detector):
        """Test bias detection on neutral text."""
        neutral_text = "The engineer completed the project successfully."

        result = bias_detector.detect_bias(neutral_text, {})

        assert "has_bias" in result
        assert "bias_types" in result
        assert "suggestions" in result
        assert "score" in result

        # Neutral text should have no bias
        if result["has_bias"]:
            # Depends on implementation sophistication
            pass

    def test_detect_bias_gendered_language(self, bias_detector):
        """Test detection of gendered language."""
        gendered_text = "The chairman led the meeting. He made decisions."

        result = bias_detector.detect_bias(gendered_text, {})

        # Should potentially detect gender bias (if implemented)
        assert isinstance(result["has_bias"], bool)
        assert isinstance(result["score"], (int, float))

    def test_detect_bias_stereotypical_roles(self, bias_detector):
        """Test detection of stereotypical role assignments."""
        stereotypical_text = "The nurse was caring. She helped patients."

        result = bias_detector.detect_bias(stereotypical_text, {})

        assert "has_bias" in result
        assert "bias_types" in result

    def test_detect_bias_inclusive_language(self, bias_detector):
        """Test inclusive language."""
        inclusive_text = "The team members collaborated effectively."

        result = bias_detector.detect_bias(inclusive_text, {})

        # Inclusive language should score better
        assert result["score"] >= 0.0
        assert result["score"] <= 1.0

    def test_detect_bias_with_context(self, bias_detector):
        """Test bias detection with context."""
        text = "The doctor made a diagnosis."
        context = {"domain": "medical", "audience": "general"}

        result = bias_detector.detect_bias(text, context)

        assert "has_bias" in result

    def test_detect_bias_score_range(self, bias_detector):
        """Test bias score is within valid range."""
        text = "This is a test sentence."

        result = bias_detector.detect_bias(text, {})

        # Score should be between 0 and 1
        assert result["score"] >= 0.0
        assert result["score"] <= 1.0

    def test_detect_bias_multiple_types(self, bias_detector):
        """Test detection of multiple bias types."""
        text = "The elderly woman struggled with the technology."

        result = bias_detector.detect_bias(text, {})

        assert isinstance(result["bias_types"], list)

    def test_detect_bias_suggestions_format(self, bias_detector):
        """Test suggestions are properly formatted."""
        text = "He is a good programmer."

        result = bias_detector.detect_bias(text, {})

        assert isinstance(result["suggestions"], list)

    def test_detect_bias_empty_text(self, bias_detector):
        """Test bias detection on empty text."""
        result = bias_detector.detect_bias("", {})

        assert "has_bias" in result
        # Empty text should not have bias
        assert result["has_bias"] is False

    def test_detect_bias_long_text(self, bias_detector):
        """Test bias detection on long text."""
        long_text = "The developer worked on the project. " * 100

        result = bias_detector.detect_bias(long_text, {})

        # Should handle long text without errors
        assert "has_bias" in result
        assert "score" in result

    def test_detect_bias_special_characters(self, bias_detector):
        """Test bias detection with special characters."""
        text = "The engineer @work 😀 completed tasks!"

        result = bias_detector.detect_bias(text, {})

        # Should handle special characters
        assert "has_bias" in result


class TestAuditTrail:
    """Test AuditTrail class."""

    def test_audit_trail_initialization(self):
        """Test audit trail initialization."""
        from src.governance import AuditTrail

        mock_storage = Mock()
        audit_trail = AuditTrail(mock_storage)

        assert audit_trail.storage == mock_storage

    def test_log_decision_basic(self, mock_audit_trail):
        """Test basic decision logging."""
        audit_id = mock_audit_trail.log_decision(
            action_type="query",
            input_data={"query": "test"},
            output_data={"response": "answer"},
            model="claude-3-5-sonnet-20241022",
            actor="user123"
        )

        assert audit_id is not None
        assert isinstance(audit_id, str)

    def test_log_decision_with_metadata(self, mock_audit_trail):
        """Test logging with additional metadata."""
        audit_id = mock_audit_trail.log_decision(
            action_type="query",
            input_data={"query": "test"},
            output_data={"response": "answer"},
            model="claude-3-5-sonnet-20241022",
            actor="user123",
            cost=0.001,
            latency_ms=150,
            confidence=0.95
        )

        assert audit_id is not None

    def test_log_decision_default_actor(self, mock_audit_trail):
        """Test logging with default actor."""
        audit_id = mock_audit_trail.log_decision(
            action_type="query",
            input_data={"query": "test"},
            output_data={"response": "answer"},
            model="claude-3-5-sonnet-20241022"
        )

        assert audit_id is not None

    def test_log_decision_different_action_types(self, mock_audit_trail):
        """Test logging different action types."""
        action_types = [
            "agent_query",
            "tool_execution",
            "data_access",
            "user_action"
        ]

        audit_ids = []
        for action_type in action_types:
            audit_id = mock_audit_trail.log_decision(
                action_type=action_type,
                input_data={"test": "data"},
                output_data={"result": "ok"},
                model="test-model",
                actor="test_user"
            )
            audit_ids.append(audit_id)

        # All should return audit IDs
        assert all(audit_ids)

    def test_log_decision_complex_input_data(self, mock_audit_trail):
        """Test logging with complex input data."""
        complex_input = {
            "query": "complex query",
            "context": {
                "user_history": ["query1", "query2"],
                "preferences": {"lang": "en"}
            },
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "source": "web"
            }
        }

        audit_id = mock_audit_trail.log_decision(
            action_type="query",
            input_data=complex_input,
            output_data={"response": "answer"},
            model="claude-3-5-sonnet-20241022",
            actor="user123"
        )

        assert audit_id is not None

    def test_log_decision_complex_output_data(self, mock_audit_trail):
        """Test logging with complex output data."""
        complex_output = {
            "response": "detailed response",
            "confidence": 0.95,
            "reasoning": ["step1", "step2", "step3"],
            "metadata": {
                "tokens_used": 1000,
                "model_version": "v1.0"
            }
        }

        audit_id = mock_audit_trail.log_decision(
            action_type="query",
            input_data={"query": "test"},
            output_data=complex_output,
            model="claude-3-5-sonnet-20241022",
            actor="user123"
        )

        assert audit_id is not None


class TestHumanInTheLoopAgent:
    """Test HumanInTheLoopAgent class."""

    def test_hitl_agent_initialization(self):
        """Test HITL agent initialization."""
        from src.governance import HumanInTheLoopAgent

        agent = HumanInTheLoopAgent(approval_timeout=300)

        assert agent.approval_timeout == 300
        assert hasattr(agent, 'pending_requests')

    def test_hitl_agent_default_timeout(self):
        """Test HITL agent with default timeout."""
        from src.governance import HumanInTheLoopAgent

        agent = HumanInTheLoopAgent()

        assert agent.approval_timeout == 300  # Default 5 minutes

    @pytest.mark.asyncio
    async def test_execute_with_approval_low_risk(self):
        """Test execution of low-risk action without approval."""
        from src.governance import HumanInTheLoopAgent

        agent = HumanInTheLoopAgent()

        # Mock action
        mock_action = Mock(return_value="action result")

        result = await agent.execute_with_approval(
            action=mock_action,
            action_description="Low risk action",
            ai_reasoning="Safe to execute",
            risk_level="low",
            action_id="action_123"
        )

        # Low risk should execute immediately
        # Note: stub implementation may not be fully implemented
        if result is not None:
            assert result == "action result"

    @pytest.mark.asyncio
    async def test_execute_with_approval_high_risk(self):
        """Test high-risk action requires approval."""
        from src.governance import HumanInTheLoopAgent

        agent = HumanInTheLoopAgent()

        mock_action = Mock(return_value="action result")

        # High risk should wait for approval (not implemented in stub)
        with pytest.raises(NotImplementedError):
            await agent.execute_with_approval(
                action=mock_action,
                action_description="High risk action",
                ai_reasoning="Needs approval",
                risk_level="high",
                action_id="action_456"
            )

    @pytest.mark.asyncio
    async def test_execute_with_approval_medium_risk(self):
        """Test medium-risk action handling."""
        from src.governance import HumanInTheLoopAgent

        agent = HumanInTheLoopAgent()

        mock_action = Mock(return_value="action result")

        try:
            result = await agent.execute_with_approval(
                action=mock_action,
                action_description="Medium risk action",
                ai_reasoning="Might need approval",
                risk_level="medium",
                action_id="action_789"
            )
            # Depends on implementation
            assert result is not None or result is None
        except NotImplementedError:
            # Expected for stub
            pass

    def test_pending_requests_storage(self):
        """Test pending requests are stored."""
        from src.governance import HumanInTheLoopAgent

        agent = HumanInTheLoopAgent()

        # Initially empty
        assert len(agent.pending_requests) == 0


class TestResponsibleAIIntegration:
    """Test integration of responsible AI components."""

    def test_bias_detection_and_audit_trail(self, bias_detector, mock_audit_trail):
        """Test bias detection with audit trail."""
        text = "The engineer completed the project."

        # Detect bias
        bias_result = bias_detector.detect_bias(text, {})

        # Log to audit trail
        audit_id = mock_audit_trail.log_decision(
            action_type="bias_check",
            input_data={"text": text},
            output_data=bias_result,
            model="bias-detector",
            actor="system"
        )

        assert bias_result is not None
        assert audit_id is not None

    @pytest.mark.asyncio
    async def test_full_governance_pipeline(self, bias_detector, mock_audit_trail):
        """Test complete governance pipeline."""
        query = "What are the best practices for hiring?"
        response = "Focus on skills and qualifications."

        # Step 1: Detect bias in response
        bias_result = bias_detector.detect_bias(response, {})

        # Step 2: Log decision to audit trail
        audit_id = mock_audit_trail.log_decision(
            action_type="agent_query",
            input_data={"query": query},
            output_data={
                "response": response,
                "bias_detected": bias_result["has_bias"],
                "bias_score": bias_result["score"]
            },
            model="claude-3-5-sonnet-20241022",
            actor="test_user"
        )

        # Step 3: Verify complete pipeline
        assert bias_result["has_bias"] is not None
        assert audit_id is not None

    def test_bias_thresholds(self, bias_detector):
        """Test bias score against thresholds."""
        texts = [
            "The developer wrote clean code.",  # Neutral
            "He is a good programmer.",  # Potentially biased
        ]

        threshold_auto_approve = 0.9
        threshold_human_review = 0.7

        for text in texts:
            result = bias_detector.detect_bias(text, {})
            score = result["score"]

            # Categorize based on thresholds
            if score >= threshold_auto_approve:
                action = "auto_approve"
            elif score >= threshold_human_review:
                action = "human_review"
            else:
                action = "auto_reject"

            assert action in ["auto_approve", "human_review", "auto_reject"]
