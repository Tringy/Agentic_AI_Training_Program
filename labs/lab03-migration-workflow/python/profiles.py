"""Framework profile metadata for the migration agent."""

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass
class FrameworkProfile:
    name: str
    language: str
    file_extensions: List[str]
    description: str
    migration_notes: List[str]
    idiomatic_patterns: List[str]
    independent_file_types: List[str]

    def format_for_prompt(self) -> str:
        """Return description + numbered migration_notes for LLM prompt injection."""
        notes = "\n".join(f"{i + 1}. {note}" for i, note in enumerate(self.migration_notes))
        return f"{self.description}\nMigration notes:\n{notes}"


PROFILES: Dict[str, FrameworkProfile] = {
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
            "Error-handling middleware (4-arg) maps to exception handlers",
        ],
        idiomatic_patterns=["express.Router()", "app.use()", "module.exports"],
        independent_file_types=["routes/*.js", "middleware/*.js"],
    ),
    "fastapi": FrameworkProfile(
        name="fastapi",
        language="python",
        file_extensions=[".py"],
        description="Modern async Python web framework with automatic OpenAPI documentation.",
        migration_notes=[
            "Pydantic models replace manual request body parsing",
            "Dependency injection via Depends() replaces middleware patterns",
            "Path operations use decorators: @app.get(), @app.post(), etc.",
            "async def handlers are preferred for I/O-bound routes",
            "HTTPException replaces manual error response construction",
        ],
        idiomatic_patterns=["@app.get", "@app.post", "Depends(", "BaseModel"],
        independent_file_types=["routers/*.py", "models/*.py"],
    ),
    "flask": FrameworkProfile(
        name="flask",
        language="python",
        file_extensions=[".py"],
        description="Lightweight WSGI Python web framework with a simple routing API.",
        migration_notes=[
            "Replace @app.route() decorators with target framework equivalents",
            "Flask request object (request.json, request.args) maps to function parameters",
            "jsonify() calls map to plain return statements in FastAPI",
            "Blueprints map to routers or controller modules",
            "Flask extensions (Flask-SQLAlchemy, Flask-Login) need target-framework replacements",
        ],
        idiomatic_patterns=["@app.route", "from flask import", "Blueprint("],
        independent_file_types=["blueprints/*.py", "views/*.py"],
    ),
    "django": FrameworkProfile(
        name="django",
        language="python",
        file_extensions=[".py"],
        description="Full-stack Python web framework following the MVT pattern with ORM and admin.",
        migration_notes=[
            "Django ORM models need to be rewritten for the target ORM or schema definition",
            "Class-based views map to router handler classes in the target framework",
            "urls.py route patterns translate to path operation decorators",
            "Django middleware maps to ASGI/WSGI middleware or dependency injection",
            "settings.py configuration maps to environment-variable-driven config",
        ],
        idiomatic_patterns=["from django", "models.Model", "views.View", "urlpatterns"],
        independent_file_types=["views/*.py", "serializers/*.py"],
    ),
    "nestjs": FrameworkProfile(
        name="nestjs",
        language="typescript",
        file_extensions=[".ts"],
        description="Opinionated TypeScript Node.js framework using decorators and dependency injection.",
        migration_notes=[
            "@Controller / @Get / @Post decorators map to route handler equivalents",
            "NestJS providers and injectable services map to DI container registrations",
            "DTOs with class-validator decorators map to Pydantic models or Zod schemas",
            "Pipes, Guards, and Interceptors map to middleware or request filters",
            "ConfigModule usage translates to environment variable reading",
        ],
        idiomatic_patterns=["@Controller(", "@Injectable(", "@Module(", "NestFactory"],
        independent_file_types=["controllers/*.ts", "services/*.ts", "dto/*.ts"],
    ),
    "hono": FrameworkProfile(
        name="hono",
        language="typescript",
        file_extensions=[".ts", ".tsx"],
        description="Ultrafast edge-runtime TypeScript web framework with a minimal API.",
        migration_notes=[
            "Hono app.get/post/put/delete map directly to target route handlers",
            "c.json() / c.text() response helpers map to return statements",
            "Hono middleware (app.use()) maps to decorators or DI middleware",
            "Context object (c) maps to request/response parameter pairs",
            "Hono validators (zValidator) map to Pydantic or DTO validation",
        ],
        idiomatic_patterns=["new Hono()", "app.get(", "c.json(", "c.req"],
        independent_file_types=["routes/*.ts", "middleware/*.ts"],
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
    "dbt": FrameworkProfile(
        name="dbt",
        language="sql",
        file_extensions=[".sql", ".yml", ".yaml"],
        description="SQL-first transformation framework using Jinja-templated SQL models with YAML schema definitions.",
        migration_notes=[
            "{{ ref('model') }} is the primary way to reference other models",
            "{{ config(materialized=...) }} sets materialisation strategy per model",
            "schema.yml holds column descriptions and generic test declarations",
            "sources.yml defines external source tables referenced via {{ source() }}",
            "Macros in macros/*.sql extend SQL with reusable Jinja functions",
        ],
        idiomatic_patterns=["{{ ref(", "{{ config(", "{{ source(", "dbt_project.yml"],
        independent_file_types=["models/**/*.sql", "macros/*.sql"],
    ),
}

_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9\-]*$")


def get_profile(name: str) -> Optional[FrameworkProfile]:
    """Return the profile for the given name, or None if not found."""
    return PROFILES.get(name)


def register_profile(profile: FrameworkProfile) -> None:
    """Register a custom profile at runtime. Raises ValueError on duplicate or invalid names."""
    if not _NAME_RE.match(profile.name):
        raise ValueError(f"Profile name '{profile.name}' is invalid; use lowercase alphanumeric and hyphens only")
    if profile.name in PROFILES:
        raise ValueError(f"Profile '{profile.name}' already exists")
    PROFILES[profile.name] = profile


def detect_framework(
    filenames: List[str],
    snippets: Optional[List[str]] = None,
) -> Tuple[Optional[str], str, List[str], List[str]]:
    """Infer source framework from filenames and optional content snippets.

    Returns (detected_source, confidence, alternatives, evidence).
    confidence: "high" | "medium" | "low"
    """
    scores: Dict[str, int] = {name: 0 for name in PROFILES}
    evidence: List[str] = list(filenames)

    # --- Extension matching ---
    for fname in filenames:
        ext = "." + fname.rsplit(".", 1)[-1] if "." in fname else ""
        for name, profile in PROFILES.items():
            if ext in profile.file_extensions:
                scores[name] += 1

    # --- Filename heuristics ---
    fnames_lower = [f.lower() for f in filenames]
    heuristics = [
        ("manage.py", "django", 5),
        ("settings.py", "django", 3),
        ("wsgi.py", "django", 3),
        ("asgi.py", "django", 2),
        ("app.py", "flask", 2),
        ("app.py", "fastapi", 2),
        ("main.py", "fastapi", 2),
        ("dbt_project.yml", "dbt", 10),
        ("sources.yml", "dbt", 4),
        ("dataform.json", "dataform", 10),
        ("package.json", "express", 1),
        ("package.json", "nestjs", 1),
        ("package.json", "hono", 1),
        ("requirements.txt", "flask", 1),
        ("requirements.txt", "fastapi", 1),
        ("requirements.txt", "django", 1),
    ]
    for trigger, fw, weight in heuristics:
        if trigger in fnames_lower:
            scores[fw] += weight

    # --- Snippet / content matching ---
    if snippets:
        combined = "\n".join(snippets)
        for snippet in snippets:
            evidence.append(snippet[:80])
            for name, profile in PROFILES.items():
                for pattern in profile.idiomatic_patterns:
                    if pattern in snippet:
                        scores[name] += 3

        # Extra content heuristics
        if "from flask import" in combined or "Flask(__name__)" in combined:
            scores["flask"] += 5
        if "from fastapi import" in combined or "FastAPI()" in combined:
            scores["fastapi"] += 5
        if "from django" in combined or "django.conf" in combined:
            scores["django"] += 5
        if "require('express')" in combined or 'require("express")' in combined:
            scores["express"] += 5
        if "@nestjs/" in combined or "NestFactory" in combined:
            scores["nestjs"] += 5
        if "new Hono()" in combined or "from 'hono'" in combined:
            scores["hono"] += 5

        # requirements.txt content helps disambiguate Python frameworks
        if any(f.lower() == "requirements.txt" for f in filenames):
            for line in combined.splitlines():
                pkg = line.strip().lower().split("==")[0].split(">=")[0].split("[")[0]
                if pkg == "flask":
                    scores["flask"] += 4
                elif pkg == "fastapi":
                    scores["fastapi"] += 4
                elif pkg in ("django", "django-rest-framework"):
                    scores["django"] += 4

    # --- Rank results ---
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    best_name, best_score = ranked[0]
    second_score = ranked[1][1] if len(ranked) > 1 else 0

    if best_score == 0:
        return None, "low", [], evidence

    if best_score >= second_score * 2:
        confidence = "high"
    elif best_score > second_score:
        confidence = "medium"
    else:
        confidence = "low"

    alternatives = [n for n, s in ranked[1:3] if s > 0 and n != best_name]
    return best_name, confidence, alternatives, evidence
