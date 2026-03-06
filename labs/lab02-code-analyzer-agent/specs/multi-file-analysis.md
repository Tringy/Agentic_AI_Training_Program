# Feature: Multi-file Analysis

## Functional Requirements
1. Accept 2–10 code files in a single request, each with a filename, code body, and language
2. Analyze every file individually using the existing `CodeAnalyzer.analyze()` logic
3. Produce a cross-file relationship report covering shared dependencies, coupling, and architectural concerns
4. Return a combined result: per-file analyses + relationship observations + overall summary

---

## Acceptance Criteria

```
GIVEN a request with 2 or more files
WHEN POST /analyze/multi is called
THEN the response must:
  - Return an individual AnalysisResult for each file
  - Include a relationships list with cross-file observations
  - Include an overall_summary string
  - Have status code 200

GIVEN a request with fewer than 2 files
WHEN POST /analyze/multi is called
THEN response must:
  - Have status code 422
  - Return a validation error

GIVEN a request with more than 10 files
WHEN POST /analyze/multi is called
THEN response must:
  - Have status code 422
  - Return a validation error
```

---

## Response Schema

```json
{
  "files": [
    { "filename": "auth.py", "result": { ...AnalysisResult } }
  ],
  "relationships": ["auth.py imports db.py but bypasses the ORM layer"],
  "overall_summary": "string"
}
```

---

## Files to Add / Update

| File | Change |
|---|---|
| `python/analyzer.py` | Add `FileInput`, `FileAnalysis`, `MultiFileResult` models; add `analyze_multi()` method |
| `python/prompts.py` | Add `MULTI_FILE_RELATIONSHIPS_PROMPT` for cross-file LLM call |
| `python/main.py` | Add `POST /analyze/multi` endpoint; validate 2–10 files |
| `frontend/components/MultiFileAnalyzer.tsx` | NEW – file slot list, Add/Remove file buttons, calls `/analyze/multi` |
| `frontend/components/RelationshipDisplay.tsx` | NEW – renders `relationships` list and `overall_summary` card |
| `frontend/app/multi/page.tsx` | NEW – standalone page using `MultiFileAnalyzer` |
| `frontend/app/layout.tsx` | Add nav link to `/multi` |
| `frontend/types.ts` | Add `FileInput`, `FileAnalysis`, `MultiFileResult` interfaces |

---

## Implementation Notes

- **Two-pass LLM strategy**: first call `analyze()` on each file individually, then make a second LLM call with all filenames + per-file summaries to generate `relationships` and `overall_summary`. Do not attempt cross-file analysis in a single prompt.
- The per-file loop should collect all `AnalysisResult` objects before issuing the second LLM call.
- Use `MULTI_FILE_RELATIONSHIPS_PROMPT` as the system prompt for the second call; pass filenames and their summaries only (not full code) to stay within token limits.
- The `MultiFileAnalyzer` component should reuse the existing `AnalysisDisplay` component for each per-file result.
