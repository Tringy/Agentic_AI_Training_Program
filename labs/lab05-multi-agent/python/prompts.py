"""LLM prompt templates for the multi-agent system."""

SUMMARISER_PROMPT = """You are a concise summariser. Given a completed task and its result, 
produce a one-paragraph summary (maximum 120 words) suitable for use as memory context in future tasks.

Respond with ONLY valid JSON — no markdown fences, no extra text:
{"summary": "..."}"""


def build_summariser_message(task: str, result: str) -> list:
    """Build messages for the summariser LLM call."""
    return [
        {"role": "system", "content": SUMMARISER_PROMPT},
        {"role": "user", "content": f"Task: {task}\n\nResult:\n{result}"},
    ]
