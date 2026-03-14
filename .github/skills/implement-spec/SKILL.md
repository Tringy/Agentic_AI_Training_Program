---
name: implement-spec
description: 'Implement a feature from an existing spec file. Use when: a specs/{feature}.md exists and needs to be turned into working code. Handles related specs, dependency ordering, backend endpoint, LLM prompt, frontend component, and tests.'
argument-hint: 'Path or name of the spec to implement (e.g. "specs/diff-analysis.md")'
---

# Implement a Spec

## When to Use

- A `specs/{feature}.md` file already exists (created with `/write-spec`)
- Implementing extension challenges or capstone features

## Procedure

1. **Read the target spec** fully before writing any code

2. **Resolve related specs** — check the `Related Specs` table in the spec:
   - For each `depends on` entry: read that spec and confirm its implementation exists; implement it first if missing
   - For each `extends` entry: read that spec to understand what's being built on top of

3. **Implement in dependency order** — if spec A depends on spec B, finish B before starting A

4. **Implement backend**:
   - Add Pydantic request/response models matching the spec's API contract exactly
   - Add endpoint(s) with status codes from the spec's error table
   - Add LLM prompt to `prompts.py` if the spec has an `LLM Output Schema` section — JSON schema must match the Pydantic model field-for-field
   - Add caching if the spec's Behaviour section specifies a cache strategy
   - Add rate limiting if the endpoint is a public-facing write

5. **Implement frontend** — new component matching the spec's API contract; import types from `types.ts`; use `process.env.NEXT_PUBLIC_API_URL`

6. **Write tests** — one test per acceptance criterion in the spec; use GIVEN/WHEN/THEN as the test description

7. **Verify** — `cd python && pytest -v`, then `docker compose up` and manually check each acceptance criterion

## Rules

- Implement exactly what the spec says — no extra fields, no unrequested endpoints
- If the spec is ambiguous, re-read related specs before guessing
- `GET /health` must keep returning `{"status": "ok"}` after any change
- Never use `shell=True` in subprocess calls
