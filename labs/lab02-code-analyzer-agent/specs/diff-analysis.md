# Feature: Diff Analysis

## Functional Requirements
1. Accept two versions of the same code file (`before` and `after`) plus a language
2. Analyze both versions independently using the existing `CodeAnalyzer.analyze()` logic
3. Identify issues introduced in `after` that were not present in `before`
4. Identify issues from `before` that no longer appear in `after` (resolved)
5. List regression risks: behavioural changes that may break existing functionality
6. Compare quality metrics between both versions
7. Return a plain-language `change_summary` (2–3 sentences)

---

## Acceptance Criteria

```
GIVEN both `before` and `after` fields are provided
WHEN POST /analyze/diff is called
THEN the response must:
  - Return introduced, resolved, regressions, change_summary
  - Include metrics_before and metrics_after
  - Have status code 200

GIVEN only one field is provided (before or after)
WHEN POST /analyze/diff is called
THEN response must:
  - Have status code 422
  - Return a validation error

GIVEN a change with no new issues
WHEN POST /analyze/diff is called
THEN introduced must:
  - Be an empty list []
```

---

## Response Schema

```json
{
  "introduced":    [ ...Issue ],
  "resolved":      [ ...Issue ],
  "regressions":   ["string"],
  "change_summary": "string",
  "metrics_before": { ...Metrics },
  "metrics_after":  { ...Metrics }
}
```

---

## Files to Add / Update

| File | Change |
|---|---|
| `python/analyzer.py` | Add `DiffResult` model; add `analyze_diff()` method |
| `python/prompts.py` | Add `DIFF_ANALYSIS_PROMPT` for comparing the two analyses |
| `python/main.py` | Add `POST /analyze/diff` endpoint |
| `frontend/components/DiffAnalyzer.tsx` | NEW – two code panes (Before / After), shared language selector, calls `/analyze/diff` |
| `frontend/components/DiffDisplay.tsx` | NEW – renders introduced/resolved columns, regression warnings, and side-by-side metrics |
| `frontend/app/diff/page.tsx` | NEW – standalone page using `DiffAnalyzer` |
| `frontend/app/layout.tsx` | Add nav link to `/diff` |
| `frontend/types.ts` | Add `DiffResult` interface |

---

## Implementation Notes

- **Two-pass LLM strategy**: call `analyze()` on `before` and `after` independently, then pass both resulting `AnalysisResult` objects to a second LLM call using `DIFF_ANALYSIS_PROMPT` to derive `introduced`, `resolved`, `regressions`, and `change_summary`.
- Do not diff the raw code strings directly; let the LLM compare the two structured analyses.
- `DiffDisplay` should reuse the existing `AnalysisDisplay` issue list for the Introduced and Resolved columns, applying a red/green background tint respectively.
- Both panes in `DiffAnalyzer` share one language selector — the same value is sent for both `before` and `after`.
