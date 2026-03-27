"""Specialist agents for football game analysis."""

from dataclasses import dataclass
from typing import Optional, Tuple

from prompts import ASSISTANT_COACH_PROMPT, COACH_PROMPT, FAN_PROMPT, JOURNALIST_PROMPT


@dataclass
class AgentTraceEntry:
    """Entry in agent execution trace."""

    agent: str
    action: str
    duration_ms: int
    content: Optional[str] = None


class SpecialistAgent:
    """Base class for specialist football analysis agents."""

    def __init__(self, llm_client, system_prompt: str, name: str):
        self.llm = llm_client
        self.system_prompt = system_prompt
        self.name = name

    def execute(self, task: str, context: str = "", max_tokens: int = 256) -> str:
        """Execute a task and return analysis."""
        user_prompt = task
        if context:
            user_prompt = f"Context:\n{context}\n\nTask:\n{task}"

        response = self.llm.chat(self.system_prompt, user_prompt, max_tokens=max_tokens)
        return response

    def execute_with_tokens(self, task: str, context: str = "", max_tokens: int = 256) -> Tuple[str, int, int]:
        """Execute a task and return analysis with token counts.

        Returns: (response_text, prompt_tokens, completion_tokens)
        """
        user_prompt = task
        if context:
            user_prompt = f"Context:\n{context}\n\nTask:\n{task}"

        response_text, prompt_tokens, completion_tokens = self.llm.chat_with_tokens(self.system_prompt, user_prompt, max_tokens=max_tokens)
        return response_text, prompt_tokens, completion_tokens


class JournalistAgent(SpecialistAgent):
    """Analyzes match narrative and key moments."""

    def __init__(self, llm_client):
        super().__init__(llm_client, JOURNALIST_PROMPT, "Journalist")


class CoachAgent(SpecialistAgent):
    """Provides tactical analysis and strategy insights."""

    def __init__(self, llm_client):
        super().__init__(llm_client, COACH_PROMPT, "Coach")


class AssistantCoachAgent(SpecialistAgent):
    """Offers detailed performance breakdown."""

    def __init__(self, llm_client):
        super().__init__(llm_client, ASSISTANT_COACH_PROMPT, "AssistantCoach")


class FanAgent(SpecialistAgent):
    """Delivers emotional perspective and hot takes."""

    def __init__(self, llm_client):
        super().__init__(llm_client, FAN_PROMPT, "Fan")
