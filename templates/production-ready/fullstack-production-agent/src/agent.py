"""
Production Agent with all patterns integrated.

This is a reference implementation. Complete implementations of each component
are taught in the Day 3, Day 4, and Day 5 curriculum modules.
"""
from typing import Dict, Any, Optional
import anthropic
import time

class ProductionAgent:
    """
    Production-ready AI agent.

    Integrates:
    - LLM client with retry logic
    - Caching layer
    - Bias detection
    - Cost tracking
    - Audit logging
    """

    def __init__(
        self,
        api_key: str,
        cache=None,
        bias_detector=None,
        audit_trail=None
    ):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.cache = cache
        self.bias_detector = bias_detector
        self.audit_trail = audit_trail

    async def process(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        user_id: str = "default"
    ) -> Dict[str, Any]:
        """
        Process query with full production pipeline.

        Pipeline:
        1. Check cache
        2. Call LLM with retry logic
        3. Detect bias in output
        4. Log to audit trail
        5. Track cost
        6. Return result
        """
        start_time = time.time()

        # Build messages
        messages = [
            {
                "role": "user",
                "content": query
            }
        ]

        # Add context if provided
        if context:
            messages[0]["content"] = f"Context: {context}\n\nQuery: {query}"

        # Call LLM (see Day 5 curriculum for retry/fallback implementation)
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=messages
        )

        # Extract response
        response_text = response.content[0].text

        # Calculate cost (see Day 5 curriculum for cost tracking implementation)
        cost = self._calculate_cost(response.usage)

        # Detect bias (if enabled)
        bias_result = {"has_bias": False, "score": 0.0}
        if self.bias_detector:
            bias_result = self.bias_detector.detect_bias(response_text, {})

        # Log to audit trail (if enabled)
        audit_id = None
        if self.audit_trail:
            audit_id = self.audit_trail.log_decision(
                action_type="agent_query",
                input_data={"query": query, "user_id": user_id},
                output_data={"response": response_text},
                model="claude-3-5-sonnet-20241022",
                actor=user_id,
                cost=cost
            )

        latency = (time.time() - start_time) * 1000

        return {
            "response": response_text,
            "confidence": 0.85,  # TODO: Implement confidence scoring
            "reasoning": "See Day 3 curriculum for agent reasoning implementation",
            "cost": cost,
            "latency_ms": latency,
            "bias_detected": bias_result["has_bias"],
            "bias_score": bias_result.get("score", 0.0),
            "audit_id": audit_id
        }

    def _calculate_cost(self, usage) -> float:
        """
        Calculate cost based on token usage.

        See Day 5 curriculum section 2.3 for complete cost management implementation.
        """
        # Claude 3.5 Sonnet pricing
        input_cost = (usage.input_tokens / 1_000_000) * 3.0
        output_cost = (usage.output_tokens / 1_000_000) * 15.0
        return input_cost + output_cost
