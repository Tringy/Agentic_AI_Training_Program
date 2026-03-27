"""LLM client for Google Generative AI integration."""

import json
import math
import os
from typing import Tuple


class LLMClient:
    """Wrapper for Google Generative AI (Gemini) API."""

    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")

        # Lazy import avoids test-time import failures when protobuf/google SDK
        # versions are incompatible with the local interpreter.
        import google.generativeai as genai

        self._genai = genai
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash-lite")
        self.token_estimation_chars_per_token = int(os.getenv("TOKEN_ESTIMATION_CHARS_PER_TOKEN", "4"))

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count as fallback when provider metadata unavailable."""
        return max(1, math.ceil(len(text) / self.token_estimation_chars_per_token))

    def chat(self, system: str, user: str, max_tokens: int = 256) -> str:
        """Send a message and return the response."""
        combined_prompt = f"{system}\n\n{user}"
        response = self.model.generate_content(
            combined_prompt,
            generation_config=self._genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
            ),
        )
        return response.text

    def chat_with_tokens(self, system: str, user: str, max_tokens: int = 256) -> Tuple[str, int, int]:
        """Send a message and return response text with token counts.

        Returns: (response_text, prompt_tokens, completion_tokens)
        """
        combined_prompt = f"{system}\n\n{user}"
        response = self.model.generate_content(
            combined_prompt,
            generation_config=self._genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
            ),
        )

        response_text = response.text

        # Try to get actual token counts from provider metadata
        prompt_tokens = None
        completion_tokens = None

        try:
            if hasattr(response, "usage_metadata"):
                usage = response.usage_metadata
                if hasattr(usage, "prompt_token_count"):
                    prompt_tokens = usage.prompt_token_count
                if hasattr(usage, "candidates_token_count"):
                    completion_tokens = usage.candidates_token_count
        except (AttributeError, TypeError):
            pass

        # Fall back to estimation if token counts unavailable
        if prompt_tokens is None:
            prompt_tokens = self._estimate_tokens(combined_prompt)
        if completion_tokens is None:
            completion_tokens = self._estimate_tokens(response_text)

        return response_text, prompt_tokens, completion_tokens

    def chat_json(self, system: str, user: str, max_tokens: int = 512) -> dict:
        """Send a message and return parsed JSON response."""
        response_text = self.chat(system, user, max_tokens=max_tokens)

        # Strip markdown code blocks if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]

        response_text = response_text.strip()
        return json.loads(response_text)

    def chat_json_with_tokens(self, system: str, user: str, max_tokens: int = 512) -> Tuple[dict, int, int]:
        """Send a message and return parsed JSON with token counts.

        Returns: (json_dict, prompt_tokens, completion_tokens)
        """
        response_text, prompt_tokens, completion_tokens = self.chat_with_tokens(system, user, max_tokens=max_tokens)

        # Strip markdown code blocks if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]

        response_text = response_text.strip()
        return json.loads(response_text), prompt_tokens, completion_tokens
