"""Migration Workflow Agent - System Prompts."""

ANALYSIS_PROMPT = """Analyze this code for migration from {source} to {target}.

Source Framework:
{source_profile}

Target Framework:
{target_profile}

Code:
```{language}
{code}
```

Identify:
1. Main components (classes, functions, routes)
2. Dependencies and imports
3. Framework-specific patterns
4. Potential migration challenges

Return as JSON:
{{
  "components": [
    {{"name": "...", "type": "class|function|route", "description": "..."}}
  ],
  "dependencies": ["..."],
  "patterns": [
    {{"pattern": "...", "description": "...", "migration_note": "..."}}
  ],
  "challenges": [
    {{"issue": "...", "severity": "low|medium|high", "suggestion": "..."}}
  ]
}}"""

PLANNING_PROMPT = """Create a migration plan based on this analysis.

Analysis: {analysis}

Source Framework: {source}
{source_profile}

Target Framework: {target}
{target_profile}

Create a step-by-step plan. Each step should be:
- Independent enough to execute separately
- Ordered by dependencies
- Specific about what changes

For "dependencies": list only the step IDs that MUST complete before this step can
start. Omit a dependency if the steps are truly independent — minimize unnecessary
serialization so that independent steps can run concurrently.

Return as JSON:
{{
  "steps": [
    {{
      "id": 1,
      "description": "...",
      "input_files": ["..."],
      "dependencies": [],
      "complexity": "low|medium|high"
    }}
  ]
}}"""

MIGRATION_PROMPT = """Migrate this code from {source} to {target}.

Source Framework:
{source_profile}

Target Framework:
{target_profile}

Source Code:
```
{code}
```

Context from previous steps:
{context}

Requirements:
1. Follow {target} best practices
2. Maintain the same functionality
3. Use appropriate types and patterns

Provide the migrated code in a code block. After the code, explain any significant changes."""

VERIFICATION_PROMPT = """Verify this migrated code is correct.

Source Framework:
{source_profile}

Target Framework: {target}
{target_profile}

Migrated Code:
```{language}
{code}
```

Check for:
1. Syntax errors
2. Missing imports
3. Framework compatibility issues
4. Logic errors

Return as JSON:
{{
  "valid": true|false,
  "issues": [
    {{"line": number, "issue": "...", "suggestion": "..."}}
  ],
  "summary": "..."
}}"""


# ─── Dataform → dbt specialized prompts ───────────────────────────────────────

DBT_ANALYSIS_PROMPT = """Analyze this Dataform file for migration to dbt.

Source Framework:
{source_profile}

Target Framework:
{target_profile}

Filename: {filename}

Dataform source code:
```sqlx
{code}
```

Identify every Dataform-specific construct present:

1. config block fields: type (table/view/incremental/operations/assertion/declaration),
   schema, tags, description, assertions (nonNull, uniqueKey, rowConditions),
   pre_operations, post_operations, columns, bigquery settings, dependencies
2. All `${{ref("...")}}` references to other models
3. JavaScript blocks (js {{ ... }}) used for dynamic SQL
4. Whether this file is a declaration (references an external source table)
5. Potential dbt equivalents for each construct

Return as JSON:
{{
  "file_type": "model|assertion|declaration|operation",
  "config": {{
    "materialization": "table|view|incremental|ephemeral|null",
    "schema": "...",
    "tags": [],
    "description": "...",
    "pre_hook": [],
    "post_hook": []
  }},
  "refs": ["model_name"],
  "has_javascript": true,
  "assertions": [
    {{"type": "not_null|unique|accepted_values|custom", "column": "...", "detail": "..."}}
  ],
  "dependencies": ["model_name"],
  "challenges": [
    {{"issue": "...", "severity": "low|medium|high", "suggestion": "..."}}
  ]
}}"""


DBT_PLANNING_PROMPT = """Create a dbt migration plan for a Dataform project.

Source Framework:
{source_profile}

Target Framework:
{target_profile}

Analysis of all files:
{analysis}

Dataform project files: {source_files}

The migration must produce:
- One `.sql` file per Dataform model/view/incremental (in models/)
- One `schema.yml` per model directory with columns, descriptions, and tests
  (assertions → dbt generic tests: not_null, unique, accepted_values)
- A `sources.yml` for every Dataform declaration file
- A `dbt_project.yml` summarising the project structure
- Jinja macros in `macros/` for any Dataform JavaScript blocks

Ordering rules:
- Declarations / sources.yml must come first
- Models with no upstream refs before models that depend on them
- schema.yml files come after their corresponding model files

For "dependencies": list only the step IDs that MUST complete before this step.
Minimise unnecessary dependencies so independent steps can run concurrently.

Return as JSON:
{{
  "steps": [
    {{
      "id": 1,
      "description": "...",
      "input_files": ["..."],
      "output_files": ["..."],
      "dependencies": [],
      "complexity": "low|medium|high"
    }}
  ]
}}"""


DBT_MIGRATION_PROMPT = """Migrate this Dataform file to dbt.

Source Framework:
{source_profile}

Target Framework:
{target_profile}

Dataform source:
```sqlx
{code}
```

Filename: {filename}
File type: {file_type}
Context (already migrated files / project structure):
{context}

Migration rules — apply ALL that are relevant:

## config block → Jinja config()
- `config {{ type: "table" }}`        → `{{{{ config(materialized='table') }}}}`
- `config {{ type: "view" }}`         → `{{{{ config(materialized='view') }}}}`
- `config {{ type: "incremental" }}`  → `{{{{ config(materialized='incremental', unique_key='...') }}}}`
- `config {{ schema: "staging" }}`    → add `schema='staging'` to config()
- `config {{ tags: ["daily"] }}`      → add `tags=['daily']` to config()
- `config {{ description: "..." }}`   → goes into schema.yml, NOT in the SQL file
- `config {{ pre_operations: [...] }}` → `pre-hook` inside config()
- `config {{ post_operations: [...] }}` → `post-hook` inside config()

## Ref syntax
- `${{ref("model")}}` → `{{{{ ref('model') }}}}`
- `${{ref("schema", "model")}}` → `{{{{ ref('model') }}}}` (schema is project-level in dbt)

## Declarations → sources
- A declaration file becomes an entry in `sources.yml` — produce YAML, not SQL
- `${{ref("declared_table")}}` in other models → `{{{{ source('source_name', 'table_name') }}}}`

## Assertions → schema.yml tests
- `assertions: {{ nonNull: ["col"] }}`        → `not_null` test on that column in schema.yml
- `assertions: {{ uniqueKey: ["id"] }}`       → `unique` test on that column in schema.yml
- `assertions: {{ rowConditions: ["expr"] }}` → custom `dbt_utils.expression_is_true` test
- Assertion-type files (no SELECT, just config assertions) → entries only in schema.yml

## JavaScript blocks
- Simple JS string loops → equivalent Jinja `{{%- for x in [...] %}}` macro
- Complex JS → move to `macros/macro_name.sql` and call via `{{{{ macro_name(...) }}}}`

## Output format
Return ONLY a JSON object — no prose outside it:
{{
  "files": {{
    "models/path/filename.sql": "<full SQL content>",
    "models/path/schema.yml": "<full YAML content>"
  }}
}}

If the input is a declaration, output only `sources.yml` content under the key `sources.yml`.
"""


DBT_VERIFICATION_PROMPT = """Verify this dbt migration output.

Source Framework:
{source_profile}

Target Framework:
{target_profile}

Original Dataform file: {original_filename}
Migrated dbt output:
{code}

Check every item below and report issues:
1. All `${{ref(...)}}` have been replaced with `{{{{ ref('...') }}}}` or `{{{{ source('...','...') }}}}`
2. config() macro is valid Jinja (balanced braces, correct materialization value)
3. Incremental models have a unique_key defined
4. Schema YAML is valid (proper indentation, list syntax for tests)
5. sources.yml has correct `version: 2` header
6. No raw JavaScript remains in SQL files  
7. pre-hook / post-hook lists are quoted strings
8. All dbt ref targets match known output model filenames

Return as JSON:
{{
  "valid": true,
  "issues": [
    {{"file": "...", "issue": "...", "suggestion": "..."}}
  ],
  "summary": "..."
}}"""
