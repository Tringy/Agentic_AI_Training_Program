# Feature: Framework Profiles

## Overview
Framework knowledge is currently hard-coded inside `prompts.py` as plain text
injected into LLM prompts. This feature extracts that knowledge into **framework
profile** objects: structured metadata describing a framework's language, file
patterns, idiomatic conventions, and migration hints. Profiles are loaded at startup
and injected into every prompt that needs framework-specific context, making it
straightforward to add new source/target combinations without changing the agent logic.

> **Relationship to other specs**
> - **Rollback Support** (`rollback-support.md`): profile metadata (e.g., which files
>   are safe to regenerate vs. must be preserved) can inform the rollback strategy —
>   a profile can declare `"regenerable": true` for files that cost nothing to re-create,
>   avoiding unnecessary snapshot storage.
> - **Parallel Execution** (`parallel-execution.md`): profiles can declare
>   `independent_file_types` (e.g., route files are independent from each other) to
>   pre-populate step dependencies before the LLM planning call, reducing unnecessary
>   serialisation in the generated plan.
> - **Human Approval** (`human-approval.md`): the approval UI can surface profile
>   `migration_notes` as contextual hints beside each plan step, helping reviewers
>   understand what the step entails without reading the source code.

---

## Functional Requirements

1. Define a `FrameworkProfile` schema covering: name, language, file extensions,
   description, migration notes (list), idiomatic patterns, and `independent_file_types`.
2. Ship built-in profiles for every framework already listed in `/frameworks`:
   `express`, `fastapi`, `flask`, `django`, `nestjs`, `hono`, `dataform`, `dbt`.
3. Build-in profiles must be loaded from `profiles.py` at import time — no external
   files or databases required.
4. `GET /frameworks` must return full profile metadata alongside the existing name/language.
5. Add a `POST /frameworks` endpoint to register a custom profile at runtime (current
   process only; not persisted across restarts).
6. When the agent builds prompts, inject the relevant source and target profile
   metadata (description + migration_notes) into all four existing prompts.
7. Add a `POST /detect-framework` endpoint that infers the source framework from a
   set of filenames and optional snippets.

---

## Acceptance Criteria

```
GIVEN GET /frameworks is called
THEN each framework entry must include:
  - name, language, description, migration_notes (list of strings)
  - file_extensions (e.g. [".js"] for express)
  - independent_file_types (list of glob patterns or type labels)

GIVEN POST /frameworks is called with a valid profile body
THEN:
  - The new profile is immediately available in GET /frameworks
  - POST /migrate with that framework name succeeds
  - Response has status 201

GIVEN POST /frameworks is called with a duplicate name
THEN:
  - Response must have status 409
  - Return { "detail": "Profile 'X' already exists" }

GIVEN POST /detect-framework with a list of filenames
WHEN filenames include "app.py" and "requirements.txt" containing "flask"
THEN response must:
  - Return detected_source "flask" with confidence "high"
  - Return alternatives as a list of 0–2 other candidates

GIVEN a /migrate call for a registered framework pair
WHEN the agent runs analysis and planning
THEN the LLM prompts must contain the source and target profile migration_notes
```

---

## Profile Schema

```python
@dataclass
class FrameworkProfile:
    name: str                          # e.g. "express"
    language: str                      # e.g. "javascript"
    file_extensions: List[str]         # e.g. [".js", ".mjs"]
    description: str                   # one-sentence summary
    migration_notes: List[str]         # bullet points for LLM prompts
    idiomatic_patterns: List[str]      # patterns the LLM should recognise
    independent_file_types: List[str]  # file globs that can migrate in parallel
```

---

## Response Schema — `POST /detect-framework`

```json
{
  "detected_source": "flask",
  "confidence": "high",
  "alternatives": ["django"],
  "evidence": ["app.py", "from flask import Flask"]
}
```

---

## Example Built-in Profiles (abbreviated)

```python
PROFILES = {
  "express": FrameworkProfile(
    name="express",
    language="javascript",
    file_extensions=[".js", ".mjs"],
    description="Minimal Node.js web framework using callbacks and middleware chains.",
    migration_notes=[
      "Replace require() with ES module imports or target-language equivalents",
      "Express middleware (req, res, next) maps to FastAPI dependencies or Hono middleware",
      "router.get/post/put/delete map 1-to-1 to framework route decorators",
      "res.json() maps to return statements with JSON serialisation",
    ],
    idiomatic_patterns=["express.Router()", "app.use()", "module.exports"],
    independent_file_types=["routes/*.js", "middleware/*.js"],
  ),
  "dataform": FrameworkProfile(
    name="dataform",
    language="sqlx",
    file_extensions=[".sqlx"],
    description="SQL-based data transformation framework using SQLX files with config blocks.",
    migration_notes=[
      "${ref()} becomes {{ ref() }} or {{ source() }} in dbt",
      "config { type } maps to {{ config(materialized=) }}",
      "Dataform assertions become dbt schema.yml tests",
      "JavaScript blocks must be converted to Jinja macros",
      "Declaration files become sources.yml entries, not models",
    ],
    idiomatic_patterns=["config {", "${ref(", "js {"],
    independent_file_types=["definitions/**/*.sqlx"],
  ),
}
```

---

## Files to Add / Update

| File | Change |
|---|---|
| `python/profiles.py` | NEW – `FrameworkProfile` dataclass; `PROFILES` dict with all 8 built-in profiles; `get_profile()`, `register_profile()`, `detect_framework()` functions |
| `python/prompts.py` | Add `{source_profile}` and `{target_profile}` placeholders to `ANALYSIS_PROMPT`, `PLANNING_PROMPT`, `MIGRATION_PROMPT`, `VERIFICATION_PROMPT`; update `DBT_*` prompts similarly |
| `python/agent.py` | Import `get_profile`; pass `source_profile` and `target_profile` strings (joined `migration_notes`) into every `.format()` call |
| `python/main.py` | Rewrite `GET /frameworks` to return full profile list; add `POST /frameworks`; add `POST /detect-framework` |
| `frontend/components/types.ts` | Add `FrameworkProfile` and `DetectFrameworkResponse` interfaces |
| `frontend/components/MigrationForm.tsx` | On mount, fetch `GET /frameworks` and populate the dropdowns dynamically (replacing the hardcoded `SUPPORTED_FRAMEWORKS`); add a "Detect from files" button that calls `POST /detect-framework` with the pasted filenames and auto-selects the source dropdown |

---

## Implementation Notes

- `detect_framework()` in `profiles.py` should first try **extension matching** (fast,
  no LLM required) and only fall back to an LLM call when extensions are ambiguous
  (e.g., `.sql` matches both `dataform` and `dbt`).
- Keep `profiles.py` independent of `agent.py` and `prompts.py` so it can be unit
  tested without mocking the LLM.
- The `migration_notes` list for each profile should be formatted as a numbered list
  when injected into prompts: `"1. …\n2. …"` — this structure helps the LLM apply
  them systematically.
- When `POST /frameworks` registers a custom profile, validate that `name` is
  lowercase alphanumeric with hyphens only (same pattern as existing names) to prevent
  prompt injection via the name field.
- The `independent_file_types` field feeds directly into the dependency pre-population
  logic described in `parallel-execution.md`: treat any two input files whose paths
  match the same glob pattern as having no inter-dependency.
