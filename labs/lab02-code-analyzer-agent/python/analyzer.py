"""Code Analyzer implementation."""

import json
from typing import List, Optional

from llm_client import LLMClient
from prompts import (
    CODE_ANALYZER_SYSTEM,
    DIFF_ANALYSIS_PROMPT,
    LANGUAGE_DETECTION_PROMPT,
    MULTI_FILE_RELATIONSHIPS_PROMPT,
    PERFORMANCE_FOCUS_PROMPT,
    SECURITY_FOCUS_PROMPT,
)
from pydantic import BaseModel


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


class DetectionResult(BaseModel):
    """Result of language detection."""

    language: str
    confidence: str
    alternatives: List[str] = []


class FileInput(BaseModel):
    """A single file submitted for multi-file analysis."""

    filename: str
    code: str
    language: str = "auto"


class FileAnalysis(BaseModel):
    """Per-file analysis result in a multi-file request."""

    filename: str
    result: AnalysisResult


class MultiFileResult(BaseModel):
    """Combined result for a multi-file analysis request."""

    files: List[FileAnalysis]
    relationships: List[str]
    overall_summary: str


class DiffResult(BaseModel):
    """Result of comparing two code versions."""

    introduced: List[Issue]
    resolved: List[Issue]
    regressions: List[str]
    change_summary: str
    metrics_before: Metrics
    metrics_after: Metrics


class CodeAnalyzer:
    """LLM-powered code analyzer."""

    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        self.system_prompt = CODE_ANALYZER_SYSTEM

    def detect_language(self, code: str) -> DetectionResult:
        """Detect the programming language of the given code."""
        user_prompt = f"Detect the programming language of this code snippet:\n\n{code}"
        response = self.llm.chat([{"role": "system", "content": LANGUAGE_DETECTION_PROMPT}, {"role": "user", "content": user_prompt}])
        data = self._parse_json(response)
        return DetectionResult(**data)

    def analyze(self, code: str, language: str = "python") -> AnalysisResult:
        """Analyze code and return structured result."""
        user_prompt = f"""Analyze this {language} code:

```{language}
{code}
```

Return your analysis as JSON."""

        response = self.llm.chat([{"role": "system", "content": self.system_prompt}, {"role": "user", "content": user_prompt}])

        return self._parse_response(response)

    def analyze_security(self, code: str, language: str = "python") -> AnalysisResult:
        """Security-focused analysis."""
        user_prompt = f"""Analyze this {language} code for security vulnerabilities:

```{language}
{code}
```

{SECURITY_FOCUS_PROMPT}"""

        response = self.llm.chat([{"role": "system", "content": self.system_prompt}, {"role": "user", "content": user_prompt}])

        return self._parse_response(response)

    def analyze_performance(self, code: str, language: str = "python") -> AnalysisResult:
        """Performance-focused analysis."""
        user_prompt = f"""Analyze this {language} code for performance issues:

```{language}
{code}
```

{PERFORMANCE_FOCUS_PROMPT}"""

        response = self.llm.chat([{"role": "system", "content": self.system_prompt}, {"role": "user", "content": user_prompt}])

        return self._parse_response(response)

    def analyze_diff(self, before: str, after: str, language: str = "python") -> DiffResult:
        """Compare two code versions and return a structured diff analysis."""
        result_before = self.analyze(before, language)
        result_after = self.analyze(after, language)

        user_prompt = (
            f"Before analysis:\n{result_before.model_dump_json()}\n\n"
            f"After analysis:\n{result_after.model_dump_json()}\n\n"
            "Compare these two analyses and return the diff as JSON."
        )
        response = self.llm.chat(
            [
                {"role": "system", "content": DIFF_ANALYSIS_PROMPT},
                {"role": "user", "content": user_prompt},
            ]
        )
        data = self._parse_json(response)
        return DiffResult(
            introduced=[Issue(**i) for i in data.get("introduced", [])],
            resolved=[Issue(**i) for i in data.get("resolved", [])],
            regressions=data.get("regressions", []),
            change_summary=data.get("change_summary", ""),
            metrics_before=result_before.metrics,
            metrics_after=result_after.metrics,
        )

    def analyze_multi(self, files: List["FileInput"]) -> "MultiFileResult":
        """Analyze multiple files and produce a cross-file relationship report."""
        # First pass: analyze each file individually
        file_analyses: List[FileAnalysis] = []
        summaries: List[str] = []
        for file_input in files:
            language = file_input.language
            if language == "auto":
                detected = self.detect_language(file_input.code)
                language = detected.language
            result = self.analyze(file_input.code, language)
            file_analyses.append(FileAnalysis(filename=file_input.filename, result=result))
            summaries.append(f"{file_input.filename}: {result.summary}")

        # Second pass: cross-file relationships using per-file summaries only
        summaries_text = "\n".join(summaries)
        user_prompt = f"Files analyzed:\n{summaries_text}\n\n" "Provide a cross-file relationship analysis as JSON."
        response = self.llm.chat(
            [
                {"role": "system", "content": MULTI_FILE_RELATIONSHIPS_PROMPT},
                {"role": "user", "content": user_prompt},
            ]
        )

        data = self._parse_json(response)
        return MultiFileResult(
            files=file_analyses,
            relationships=data.get("relationships", []),
            overall_summary=data.get("overall_summary", ""),
        )

    def _parse_json(self, response: str) -> dict:
        """Strip markdown fences and parse JSON."""
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0]
        elif "```" in response:
            response = response.split("```")[1].split("```")[0]
        return json.loads(response.strip())

    def _parse_response(self, response: str) -> AnalysisResult:
        """Parse LLM response into structured result."""
        data = self._parse_json(response)
        return AnalysisResult(**data)
