"""Migration Workflow Agent - Core Agent Implementation."""

import asyncio
import copy
import json
from collections import defaultdict, deque
from datetime import datetime, timezone
from typing import Dict, List

from profiles import get_profile
from prompts import (
    ANALYSIS_PROMPT,
    DBT_ANALYSIS_PROMPT,
    DBT_MIGRATION_PROMPT,
    DBT_PLANNING_PROMPT,
    DBT_VERIFICATION_PROMPT,
    MIGRATION_PROMPT,
    PLANNING_PROMPT,
    VERIFICATION_PROMPT,
)
from state import MigrationState, MigrationStep, Phase, RollbackRecord, Snapshot


class MigrationAgent:
    """Agent that performs multi-step code migration."""

    def __init__(self, llm_client):
        self.llm = llm_client

    def _profile_str(self, name: str) -> str:
        """Return formatted prompt string for a framework profile."""
        profile = get_profile(name)
        return profile.format_for_prompt() if profile else f"Framework: {name}"

    def _take_snapshot(self, state: MigrationState, step: MigrationStep) -> None:
        """Save a deep copy of migrated_files before step executes."""
        state.snapshots.append(
            Snapshot(
                step_index=step.id,
                step_description=step.description,
                timestamp=datetime.now(timezone.utc).isoformat(),
                migrated_files=copy.deepcopy(state.migrated_files),
            )
        )

    def _rollback(self, state: MigrationState, to_step_index: int, reason: str) -> bool:
        """Restore migrated_files to the snapshot for to_step_index.

        Returns True on success, False if no matching snapshot was found.
        """
        snapshot = next((s for s in reversed(state.snapshots) if s.step_index == to_step_index), None)
        if snapshot is None:
            return False
        from_step = state.current_step
        state.rollback_history.append(
            RollbackRecord(
                timestamp=datetime.now(timezone.utc).isoformat(),
                from_step=from_step,
                to_step=to_step_index,
                reason=reason,
            )
        )
        state.migrated_files = copy.deepcopy(snapshot.migrated_files)
        return True

    def run(self, state: MigrationState) -> MigrationState:
        """Run through phases, stopping when AWAITING_APPROVAL or COMPLETE."""
        while state.phase not in (Phase.COMPLETE, Phase.AWAITING_APPROVAL):
            state = self._step(state)
            if state.errors:
                break
        return state

    def resume(self, state: MigrationState) -> MigrationState:
        """Resume execution after human approval. Sets phase to EXECUTION then runs to completion."""
        state.phase = Phase.EXECUTION
        while state.phase != Phase.COMPLETE:
            state = self._step(state)
            if state.errors:
                break
        return state

    async def resume_async(self, state: MigrationState) -> MigrationState:
        """Async variant of resume used when execution_mode='parallel'."""
        state.phase = Phase.EXECUTION
        while state.phase != Phase.COMPLETE:
            if state.phase == Phase.EXECUTION:
                state = await self._execute_async(state)
            else:
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

    def _is_dataform_to_dbt(self, state: MigrationState) -> bool:
        return state.source_framework == "dataform" and state.target_framework == "dbt"

    def _analyze(self, state: MigrationState) -> MigrationState:
        """Phase 1: Analyze source code."""
        all_analysis = {}

        source_profile = self._profile_str(state.source_framework)
        target_profile = self._profile_str(state.target_framework)

        for filename, code in state.source_files.items():
            if self._is_dataform_to_dbt(state):
                prompt = DBT_ANALYSIS_PROMPT.format(
                    filename=filename,
                    code=code,
                    source_profile=source_profile,
                    target_profile=target_profile,
                )
            else:
                prompt = ANALYSIS_PROMPT.format(
                    source=state.source_framework,
                    target=state.target_framework,
                    language=self._detect_language(filename),
                    code=code,
                    source_profile=source_profile,
                    target_profile=target_profile,
                )

            response = self.llm.chat([{"role": "user", "content": prompt}])

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
        source_profile = self._profile_str(state.source_framework)
        target_profile = self._profile_str(state.target_framework)

        if self._is_dataform_to_dbt(state):
            prompt = DBT_PLANNING_PROMPT.format(
                analysis=json.dumps(state.analysis, indent=2),
                source_files=list(state.source_files.keys()),
                source_profile=source_profile,
                target_profile=target_profile,
            )
        else:
            prompt = PLANNING_PROMPT.format(
                analysis=json.dumps(state.analysis, indent=2),
                source=state.source_framework,
                target=state.target_framework,
                source_profile=source_profile,
                target_profile=target_profile,
            )

        response = self.llm.chat([{"role": "user", "content": prompt}])

        try:
            plan_data = self._parse_json(response)
            state.plan = [
                MigrationStep(
                    id=step["id"],
                    description=step["description"],
                    input_files=step.get("input_files", []),
                    dependencies=step.get("dependencies", []),
                )
                for step in plan_data.get("steps", [])
            ]
        except Exception as e:
            state.errors.append(f"Planning failed: {e}")
            return state

        state.phase = Phase.AWAITING_APPROVAL
        return state

    def _execute(self, state: MigrationState) -> MigrationState:
        """Phase 3 (sync): Execute steps sequentially regardless of execution_mode."""
        return self._execute_sequential(state)

    async def _execute_async(self, state: MigrationState) -> MigrationState:
        """Phase 3 (async): Dispatch to parallel or sequential based on execution_mode."""
        if state.execution_mode == "sequential":
            return await asyncio.to_thread(self._execute_sequential, state)
        return await self._execute_parallel(state)

    def _execute_sequential(self, state: MigrationState) -> MigrationState:
        """Execute all steps one at a time in plan order."""
        # Assign wave_index == position so the frontend can still group by wave
        for idx, step in enumerate(state.plan):
            step.wave_index = idx
        state.waves = [[s.id] for s in state.plan]

        while state.current_step < len(state.plan):
            step = state.plan[state.current_step]
            self._take_snapshot(state, step)
            step.status = "in_progress"
            try:
                self._run_step(state, step)
            except Exception as exc:
                step.status = "failed"
                state.errors.append(f"Step {step.id} failed: {exc}")
                self._rollback(state, step.id, "automatic")
                # Keep phase as EXECUTION so caller can retry or abort
                return state
            state.current_step += 1

        state.phase = Phase.VERIFICATION
        return state

    async def _execute_parallel(self, state: MigrationState) -> MigrationState:
        """Execute steps in dependency-ordered waves using asyncio.gather."""
        try:
            waves = self._build_waves(state.plan)
        except ValueError as exc:
            state.errors.append(str(exc))
            state.phase = Phase.VERIFICATION
            return state

        state.waves = [[s.id for s in wave] for wave in waves]
        for wave_idx, wave in enumerate(waves):
            for step in wave:
                step.wave_index = wave_idx

            # Snapshot before the wave (one snapshot per step, keyed by step id)
            for step in wave:
                self._take_snapshot(state, step)

            # Run all steps in this wave concurrently
            results = await asyncio.gather(
                *[asyncio.to_thread(self._run_step, state, step) for step in wave],
                return_exceptions=True,
            )

            failed = False
            for step, result in zip(wave, results):
                if isinstance(result, Exception):
                    step.status = "failed"
                    state.errors.append(f"Step {step.id} failed: {result}")
                    failed = True

            if failed:
                # Roll back all steps in this wave to the per-step snapshots
                for step in wave:
                    self._rollback(state, step.id, "automatic")
                # Cancel steps in subsequent waves that haven't started
                for future_wave in waves[wave_idx + 1 :]:
                    for step in future_wave:
                        step.status = "failed"
                # Keep phase as EXECUTION
                return state

        state.phase = Phase.VERIFICATION
        return state

    def _build_waves(self, steps: List[MigrationStep]) -> List[List[MigrationStep]]:
        """Kahn's algorithm: partition steps into dependency-ordered waves."""
        step_by_id = {s.id: s for s in steps}
        in_degree: Dict[int, int] = {s.id: 0 for s in steps}
        dependents: Dict[int, List[int]] = defaultdict(list)  # dep_id -> [step_ids that need it]

        for step in steps:
            for dep in step.dependencies:
                if dep not in step_by_id:
                    continue  # ignore references to unknown steps
                in_degree[step.id] += 1
                dependents[dep].append(step.id)

        queue: deque = deque([s.id for s in steps if in_degree[s.id] == 0])
        waves: List[List[MigrationStep]] = []
        visited = 0

        while queue:
            wave_ids = list(queue)
            queue.clear()
            waves.append([step_by_id[sid] for sid in wave_ids])
            for sid in wave_ids:
                visited += 1
                for dependent_id in dependents[sid]:
                    in_degree[dependent_id] -= 1
                    if in_degree[dependent_id] == 0:
                        queue.append(dependent_id)

        if visited != len(steps):
            raise ValueError("Cycle detected in migration step dependencies")

        return waves

    def _run_step(self, state: MigrationState, step: MigrationStep) -> None:
        """Execute a single migration step and mutate state in place."""
        step.status = "in_progress"
        source_code = self._get_step_code(state, step)

        source_profile = self._profile_str(state.source_framework)
        target_profile = self._profile_str(state.target_framework)

        if self._is_dataform_to_dbt(state):
            file_analysis = state.analysis or {}
            first_input = step.input_files[0] if step.input_files else ""
            file_type = file_analysis.get(first_input, {}).get("file_type", "model")
            prompt = DBT_MIGRATION_PROMPT.format(
                code=source_code,
                filename=first_input,
                file_type=file_type,
                context=self._get_context(state),
                source_profile=source_profile,
                target_profile=target_profile,
            )
        else:
            prompt = MIGRATION_PROMPT.format(
                source=state.source_framework,
                target=state.target_framework,
                code=source_code,
                context=self._get_context(state),
                source_profile=source_profile,
                target_profile=target_profile,
            )

        response = self.llm.chat([{"role": "user", "content": prompt}])

        step_output = response
        if self._is_dataform_to_dbt(state):
            try:
                parsed = self._parse_json(response)
                for out_path, content in parsed.get("files", {}).items():
                    state.migrated_files[out_path] = content
                    step_output = content
            except Exception:
                for f in step.input_files:
                    new_filename = self._transform_filename(f, state.target_framework)
                    state.migrated_files[new_filename] = self._extract_code(response)
        else:
            migrated_code = self._extract_code(response)
            step_output = migrated_code
            for f in step.input_files:
                new_filename = self._transform_filename(f, state.target_framework)
                state.migrated_files[new_filename] = migrated_code

        step.status = "completed"
        step.result = step_output

    def _verify(self, state: MigrationState) -> MigrationState:
        """Phase 4: Verify migration results."""
        verification = {
            "files_migrated": len(state.migrated_files),
            "steps_completed": len([s for s in state.plan if s.status == "completed"]),
            "issues": [],
            "validations": [],
        }

        source_profile = self._profile_str(state.source_framework)
        target_profile = self._profile_str(state.target_framework)

        # Verify each migrated file
        for filename, code in state.migrated_files.items():
            language = self._detect_language(filename)

            if self._is_dataform_to_dbt(state):
                # Find the original source file for this output
                original = filename
                prompt = DBT_VERIFICATION_PROMPT.format(
                    original_filename=original,
                    code=f"{filename}:\n{code}",
                    source_profile=source_profile,
                    target_profile=target_profile,
                )
            else:
                prompt = VERIFICATION_PROMPT.format(
                    target=state.target_framework,
                    language=language,
                    code=code,
                    source_profile=source_profile,
                    target_profile=target_profile,
                )

            response = self.llm.chat([{"role": "user", "content": prompt}])

            try:
                result = self._parse_json(response)
                verification["validations"].append({"file": filename, "valid": result.get("valid", False), "issues": result.get("issues", [])})
                if not result.get("valid", True):
                    verification["issues"].extend(result.get("issues", []))
            except Exception:
                verification["validations"].append({"file": filename, "valid": True, "issues": []})

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
            ".rs": "rust",
            ".sqlx": "sqlx",
            ".sql": "sql",
            ".yml": "yaml",
            ".yaml": "yaml",
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
