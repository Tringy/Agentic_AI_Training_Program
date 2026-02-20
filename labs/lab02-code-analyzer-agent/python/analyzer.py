"""Code Analyzer implementation."""
from typing import Optional, List
from pydantic import BaseModel
import json

from prompts import CODE_ANALYZER_SYSTEM, SECURITY_FOCUS_PROMPT, PERFORMANCE_FOCUS_PROMPT
from llm_client import LLMClient


class Issue(BaseModel):
    """Represents a code issue."""
    severity: str
    line: Optional[int] = None
    category: str
    description: str
    suggestion: str


class Metrics(BaseModel):
    """Code quality metrics."""
    complexity: str
    readability: str
    test_coverage_estimate: str


class AnalysisResult(BaseModel):
    """Structured analysis result."""
    summary: str
    issues: List[Issue]
    suggestions: List[str]
    metrics: Metrics


class CodeAnalyzer:
    """LLM-powered code analyzer."""

    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        self.system_prompt = CODE_ANALYZER_SYSTEM

    def analyze(self, code: str, language: str = "python") -> AnalysisResult:
        """Analyze code and return structured result."""
        user_prompt = f"""Analyze this {language} code:

```{language}
{code}
```

Return your analysis as JSON."""

        response = self.llm.chat([
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_prompt}
        ])

        return self._parse_response(response)

    def analyze_security(self, code: str, language: str = "python") -> AnalysisResult:
        """Security-focused analysis."""
        user_prompt = f"""Analyze this {language} code for security vulnerabilities:

```{language}
{code}
```

{SECURITY_FOCUS_PROMPT}"""

        response = self.llm.chat([
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_prompt}
        ])

        return self._parse_response(response)

    def analyze_performance(self, code: str, language: str = "python") -> AnalysisResult:
        """Performance-focused analysis."""
        user_prompt = f"""Analyze this {language} code for performance issues:

```{language}
{code}
```

{PERFORMANCE_FOCUS_PROMPT}"""

        response = self.llm.chat([
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_prompt}
        ])

        return self._parse_response(response)

    def _parse_response(self, response: str) -> AnalysisResult:
        """Parse LLM response into structured result."""
        # Handle markdown code blocks
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0]
        elif "```" in response:
            response = response.split("```")[1].split("```")[0]

        data = json.loads(response.strip())
        return AnalysisResult(**data)
