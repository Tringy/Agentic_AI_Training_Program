# Feature: Language Detection

## Functional Requirements
1. Automatically detect the programming language of submitted code via a dedicated endpoint
2. Return the detected language, a confidence level (`high` / `medium` / `low`), and up to 3 alternative candidates
3. Integrate auto-detection into all three existing analyze endpoints: when `language` is `"auto"`, detect before analyzing
4. Allow users to still select a language manually (manual selection always overrides auto-detection)
5. Surface the detected language in the frontend after analysis completes

---

## Acceptance Criteria

```
GIVEN valid code is submitted
WHEN POST /detect-language is called
THEN response must:
  - Return language as a lowercase canonical name (e.g. "python", "typescript")
  - Return confidence as "high", "medium", or "low"
  - Return alternatives as a list of 0–3 strings
  - Have status code 200

GIVEN an analyze request with language set to "auto"
WHEN POST /analyze (or /analyze/security or /analyze/performance) is called
THEN the endpoint must:
  - Detect the language first
  - Use the detected language for the full analysis
  - Behave identically to a request with an explicit language

GIVEN an analyze request with an explicit language (e.g. "go")
WHEN POST /analyze is called
THEN auto-detection must NOT be invoked
```

---

## Response Schema — `/detect-language`

```json
{
  "language":     "python",
  "confidence":   "high",
  "alternatives": ["ruby"]
}
```

---

## Files to Add / Update

| File | Change |
|---|---|
| `python/analyzer.py` | Add `DetectionResult` model; add `detect_language()` method |
| `python/prompts.py` | Add `LANGUAGE_DETECTION_PROMPT` |
| `python/main.py` | Add `POST /detect-language` endpoint; add `"auto"` branch in the three existing analyze endpoints |
| `frontend/components/CodeAnalyzer.tsx` | Add `"Auto-detect"` (value `"auto"`) as first option in `LANGUAGES`; set as default; show `LanguageBadge` after analysis |
| `frontend/components/LanguageBadge.tsx` | NEW – inline badge showing detected language and confidence; color-coded green/yellow/red |
| `frontend/types.ts` | Add `DetectionResult` interface |

---

## Implementation Notes

- `LANGUAGE_DETECTION_PROMPT` must instruct the LLM to return JSON only with fields `language`, `confidence`, and `alternatives`.
- Detection is a single, lightweight LLM call — keep `max_tokens` low (128 is sufficient).
- In the three existing analyze endpoints, add an `if request.language == "auto"` branch before the `analyzer.analyze()` call; extract and use `detected.language`.
- In `CodeAnalyzer.tsx`, after a successful response where `language` was `"auto"`, call `POST /detect-language` with the same code to retrieve the `DetectionResult` and render `LanguageBadge` next to the selector.
