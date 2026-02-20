"""Migration Workflow Agent - System Prompts."""

ANALYSIS_PROMPT = """Analyze this code for migration from {source} to {target}.

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
Target Framework: {target}

Create a step-by-step plan. Each step should be:
- Independent enough to execute separately
- Ordered by dependencies
- Specific about what changes

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

Target Framework: {target}

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
