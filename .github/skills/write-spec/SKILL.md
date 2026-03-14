---
name: write-spec
description: 'Write a feature spec for any lab extension, optional exercise, or capstone challenge. Use when: creating a spec file before implementing a new endpoint, LLM feature, agent workflow, or RAG pipeline change. Produces a specs/{feature}.md file with API contract, data model, acceptance criteria (GIVEN/WHEN/THEN), and LLM/agent-specific sections where needed.'
argument-hint: 'Describe the feature to spec (e.g. "POST /analyze/security endpoint" or "human approval phase for migration agent")'
---

# Write a Feature Spec

## When to Use

Before implementing any non-trivial feature — especially for extension challenges and capstone projects. A precise spec lets AI agents generate correct code on the first pass.

## Output

Creates `specs/{feature-name}.md` next to the backend code.

## Procedure

1. **Read existing specs** in `specs/` first — identify any that this feature depends on or that depend on it
2. **Map relationships** before writing anything:
   - `depends on` — this spec requires data, models, or endpoints defined in another spec; that spec must be implemented first
   - `required by` — another spec builds on top of this one; note it so the reader understands the downstream impact
   - `extends` — this spec adds behaviour to an existing spec without replacing it; document what changes and what stays the same
   - A spec can have multiple relationships of different types; list all of them
3. **Identify the feature type** — plain endpoint, LLM call, multi-step agent workflow, or RAG/retrieval change
4. **Fill in the template below** — skip sections that don't apply
5. **Cross-reference related specs** in Behaviour and Data Model sections rather than duplicating shared details — write "see `specs/other.md`" and describe only the delta
6. **Write acceptance criteria** in GIVEN/WHEN/THEN format — one criterion per testable behaviour
7. **List out-of-scope items** to prevent scope creep

---

## Spec Template

```markdown
# {Feature Name}

## Overview
One paragraph: what it does and why it exists.

## Related Specs
| Relationship | Spec file | Why |
|---|---|---|
| depends on | `specs/other-feature.md` | This feature consumes the data/endpoint defined there |
| required by | `specs/another-feature.md` | That feature builds on top of this one |
| extends | `specs/base-feature.md` | Adds behaviour to an existing spec |

(Remove rows that don't apply. Omit the section entirely if the feature is standalone.)

## API Contract

### `METHOD /path`

**Request:**
```json
{ "field": "type — description" }
```

**Success response (`{status_code}`):**
```json
{ "field": "type — description" }
```

**Error responses:**
| Status | Condition |
|--------|-----------|
| 404 | Not found |
| 422 | Validation failed |
| 409 | Duplicate |
| 429 | Rate limited |

## Data Model Changes
New tables, columns, or schema changes (include SQL if relevant).
Note any shared models referenced from a related spec.

## Configuration
| Env var | Default | Purpose |
|---------|---------|---------|

## Behaviour
Step-by-step happy path. Note caching strategy (key, TTL) if applicable.
Reference the related spec where shared behaviour applies rather than duplicating it.

## Acceptance Criteria
GIVEN {precondition}
WHEN  {action}
THEN  {expected outcome}

## Out of Scope
```

---

## LLM Output Section (add when the feature calls an LLM)

```markdown
## LLM Output Schema
```json
{
  "field_a": "string",
  "field_b": ["array"],
  "score": 0.0
}
```

## Parsing Fallback
Strip markdown fences before `json.loads`.
On `JSONDecodeError` or `ValidationError` → HTTP 500 `{"detail": "LLM returned invalid JSON"}`.
```

---

## Agent Workflow Section (add for multi-step / stateful agents)

```markdown
## Workflow Phases
POST /start → [PHASE_A] → [PHASE_B] → (human gate) → [PHASE_C] → COMPLETE

| Phase | Triggered by | Output | Next |
|-------|-------------|--------|------|
| PHASE_A | POST /start | stored JSON | PHASE_B |
| PHASE_B | PHASE_A end | plan | AWAITING_APPROVAL |
| (gate) | POST /{id}/approve | — | PHASE_C |
| PHASE_C | approval | result | COMPLETE |
```

---

## RAG / Retrieval Section (add for search or indexing features)

```markdown
## Retrieval Strategy
| search_mode | Method | Notes |
|-------------|--------|-------|
| "vector" | ChromaDB cosine | Semantic queries |
| "keyword" | BM25 | Exact symbol names |
| "hybrid" | Vector + BM25 via RRF (k=60) | Default |
```

---

## Writing Good Acceptance Criteria

Specific and measurable — one condition per `GIVEN/WHEN/THEN` block.

**Bad:** "Caching works correctly."

**Good:**
```
GIVEN the same input has been processed once
WHEN  the same request is made again
THEN  the response header X-Cache equals "HIT"
AND   the response arrives in < 50ms
```

## File Naming

| Feature type | Filename |
|---|---|
| New endpoint | `{endpoint-name}.md` (e.g. `diff-analysis.md`) |
| Cross-cutting concern | `{concern}.md` (e.g. `caching.md`) |
| Agent phase | `{phase}.md` (e.g. `human-approval.md`) |
