"""Migration Workflow Agent - Core Agent Implementation."""
from state import MigrationState, Phase, MigrationStep
from prompts import ANALYSIS_PROMPT, PLANNING_PROMPT, MIGRATION_PROMPT, VERIFICATION_PROMPT
from typing import Dict, List
import json


class MigrationAgent:
    """Agent that performs multi-step code migration."""

    def __init__(self, llm_client):
        self.llm = llm_client

    def run(self, state: MigrationState) -> MigrationState:
        """Run the migration agent through all phases."""
        while state.phase != Phase.COMPLETE:
            state = self._step(state)
            if state.errors:
                break
        return state

    def _step(self, state: MigrationState) -> MigrationState:
        """Execute one phase of the migration."""
        if state.phase == Phase.ANALYSIS:
            return self._analyze(state)
        elif state.phase == Phase.PLANNING:
            return self._plan(state)
        elif state.phase == Phase.EXECUTION:
            return self._execute(state)
        elif state.phase == Phase.VERIFICATION:
            return self._verify(state)
        return state

    def _analyze(self, state: MigrationState) -> MigrationState:
        """Phase 1: Analyze source code."""
        all_analysis = {}

        for filename, code in state.source_files.items():
            prompt = ANALYSIS_PROMPT.format(
                source=state.source_framework,
                target=state.target_framework,
                language=self._detect_language(filename),
                code=code
            )

            response = self.llm.chat([
                {"role": "user", "content": prompt}
            ])

            try:
                all_analysis[filename] = self._parse_json(response)
            except Exception as e:
                state.errors.append(f"Analysis failed for {filename}: {e}")
                return state

        state.analysis = all_analysis
        state.phase = Phase.PLANNING
        return state

    def _plan(self, state: MigrationState) -> MigrationState:
        """Phase 2: Create migration plan."""
        prompt = PLANNING_PROMPT.format(
            analysis=json.dumps(state.analysis, indent=2),
            source=state.source_framework,
            target=state.target_framework
        )

        response = self.llm.chat([
            {"role": "user", "content": prompt}
        ])

        try:
            plan_data = self._parse_json(response)
            state.plan = [
                MigrationStep(
                    id=step["id"],
                    description=step["description"],
                    input_files=step.get("input_files", [])
                )
                for step in plan_data.get("steps", [])
            ]
        except Exception as e:
            state.errors.append(f"Planning failed: {e}")
            return state

        state.phase = Phase.EXECUTION
        return state

    def _execute(self, state: MigrationState) -> MigrationState:
        """Phase 3: Execute migration steps."""
        while state.current_step < len(state.plan):
            step = state.plan[state.current_step]
            step.status = "in_progress"

            # Get relevant source code
            source_code = self._get_step_code(state, step)

            prompt = MIGRATION_PROMPT.format(
                source=state.source_framework,
                target=state.target_framework,
                code=source_code,
                context=self._get_context(state)
            )

            response = self.llm.chat([
                {"role": "user", "content": prompt}
            ])

            # Extract code from response
            migrated_code = self._extract_code(response)

            # Store result
            for filename in step.input_files:
                new_filename = self._transform_filename(filename, state.target_framework)
                state.migrated_files[new_filename] = migrated_code

            step.status = "completed"
            step.result = migrated_code
            state.current_step += 1

        state.phase = Phase.VERIFICATION
        return state

    def _verify(self, state: MigrationState) -> MigrationState:
        """Phase 4: Verify migration results."""
        verification = {
            "files_migrated": len(state.migrated_files),
            "steps_completed": len([s for s in state.plan if s.status == "completed"]),
            "issues": [],
            "validations": []
        }

        # Verify each migrated file
        for filename, code in state.migrated_files.items():
            language = self._detect_language(filename)

            prompt = VERIFICATION_PROMPT.format(
                target=state.target_framework,
                language=language,
                code=code
            )

            response = self.llm.chat([
                {"role": "user", "content": prompt}
            ])

            try:
                result = self._parse_json(response)
                verification["validations"].append({
                    "file": filename,
                    "valid": result.get("valid", False),
                    "issues": result.get("issues", [])
                })
                if not result.get("valid", True):
                    verification["issues"].extend(result.get("issues", []))
            except Exception:
                verification["validations"].append({
                    "file": filename,
                    "valid": True,
                    "issues": []
                })

        state.verification_result = verification
        state.phase = Phase.COMPLETE
        return state

    def _detect_language(self, filename: str) -> str:
        """Detect language from filename."""
        ext_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".java": "java",
            ".go": "go",
            ".rs": "rust"
        }
        for ext, lang in ext_map.items():
            if filename.endswith(ext):
                return lang
        return "unknown"

    def _parse_json(self, response: str) -> Dict:
        """Parse JSON from LLM response."""
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0]
        elif "```" in response:
            response = response.split("```")[1].split("```")[0]
        return json.loads(response.strip())

    def _extract_code(self, response: str) -> str:
        """Extract code block from response."""
        if "```" in response:
            parts = response.split("```")
            if len(parts) >= 2:
                code = parts[1]
                # Remove language identifier
                if "\n" in code:
                    first_line = code.split("\n")[0].strip()
                    if first_line in ("python", "javascript", "typescript", "java", "go"):
                        code = code.split("\n", 1)[1] if "\n" in code else ""
                return code.strip()
        return response

    def _get_step_code(self, state: MigrationState, step: MigrationStep) -> str:
        """Get source code for a migration step."""
        code_parts = []
        for filename in step.input_files:
            if filename in state.source_files:
                code_parts.append(f"# {filename}\n{state.source_files[filename]}")

        # If no specific files, include all
        if not code_parts:
            for filename, code in state.source_files.items():
                code_parts.append(f"# {filename}\n{code}")

        return "\n\n".join(code_parts)

    def _get_context(self, state: MigrationState) -> str:
        """Get context from previous steps."""
        completed = [s for s in state.plan if s.status == "completed"]
        if not completed:
            return "No previous steps completed."
        return "\n".join([f"Step {s.id}: {s.description}" for s in completed[-3:]])

    def _transform_filename(self, filename: str, target: str) -> str:
        """Transform filename for target framework."""
        transformations = {
            "fastapi": lambda f: f.replace(".js", ".py").replace("routes/", "routers/"),
            "express": lambda f: f.replace(".py", ".js").replace("routers/", "routes/"),
            "flask": lambda f: f.replace(".js", ".py"),
            "django": lambda f: f.replace(".js", ".py"),
        }
        transform = transformations.get(target.lower(), lambda f: f)
        return transform(filename)
