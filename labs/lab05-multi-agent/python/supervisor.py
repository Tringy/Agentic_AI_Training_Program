"""Supervisor agent that coordinates workers."""

import asyncio
import os
import time
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

from agent_registry import AgentDefinition, AgentRegistry
from agents import AgentTraceEntry, WorkerAgent

if TYPE_CHECKING:
    from job_store import Job

MAX_PARALLEL_WORKERS = int(os.getenv("MAX_PARALLEL_WORKERS", "4"))

SUPERVISOR_PROMPT_TEMPLATE = """You are a supervisor managing a team of specialized agents.

Generalist agents (use when no specialist fits):
{generalist_list}

Specialist agents (prefer these when the task matches their description):
{specialist_list}

RULES (follow strictly):
- Read every specialist agent's description first. If any specialist covers the task, delegate to it instead of the generalist pipeline.
- Choose ONLY the agents the task actually requires — do not call agents whose work is unnecessary.
- Output EXACTLY ONE action per response — either a DELEGATE/PARALLEL_DELEGATE or a FINAL, never both.
- Do NOT answer the task yourself. Always use your agents.

For a single agent, output ONLY this:
DELEGATE: [agent_name]
TASK: [specific task for that agent]

To run multiple independent agents concurrently, output ONLY this:
PARALLEL_DELEGATE: [agent1], [agent2]
TASK_[agent1]: [task for agent1]
TASK_[agent2]: [task for agent2]

After all delegations are complete and you have received results, output ONLY this:
FINAL: [synthesized final output]"""


def _build_supervisor_prompt(registry: AgentRegistry) -> str:
    generalists = [d for d in registry.list() if d.builtin]
    specialists = [d for d in registry.list() if not d.builtin]

    generalist_lines = "\n".join(f"- {d.name}: {d.description}" for d in generalists) or "  (none)"
    specialist_lines = "\n".join(f"- {d.name}: {d.description}" for d in specialists) or "  (none registered — use generalists)"

    return SUPERVISOR_PROMPT_TEMPLATE.format(
        generalist_list=generalist_lines,
        specialist_list=specialist_lines,
    )


def _build_user_message(task: str, memory_entries: List[dict]) -> str:
    """Build the initial user message, prepending MEMORY CONTEXT if entries exist."""
    if not memory_entries:
        return f"Task: {task}"
    lines = ["MEMORY CONTEXT (previous tasks — use if relevant):"]
    for i, entry in enumerate(memory_entries, 1):
        lines.append(f'[{i}] Task: "{entry["task"]}"')
        lines.append(f'    Summary: "{entry["summary"]}"')
    lines.append("")
    lines.append(f"Current task: {task}")
    return "\n".join(lines)


def _parse_parallel_delegate(response: str) -> Optional[List[Tuple[str, str]]]:
    """Parse a PARALLEL_DELEGATE block. Returns list of (agent_name, task) or None."""
    if "PARALLEL_DELEGATE:" not in response:
        return None
    lines = response.strip().splitlines()
    agents_line = ""
    task_map: Dict[str, str] = {}
    for line in lines:
        if line.startswith("PARALLEL_DELEGATE:"):
            agents_line = line.split("PARALLEL_DELEGATE:", 1)[1].strip()
        elif line.startswith("TASK_"):
            rest = line[len("TASK_") :]
            if ":" in rest:
                name, task_text = rest.split(":", 1)
                task_map[name.strip()] = task_text.strip()

    agent_names = [a.strip() for a in agents_line.split(",") if a.strip()]
    if not agent_names:
        return None
    return [(name, task_map.get(name, "")) for name in agent_names]


class SupervisorAgent:
    """Supervisor that coordinates worker agents."""

    def __init__(self, llm_client, registry: AgentRegistry):
        self.llm = llm_client
        self.registry = registry
        self.results: Dict[str, str] = {}
        self.agent_trace: List[AgentTraceEntry] = []
        self._parallel_group = 0

    def _build_worker(self, defn: AgentDefinition) -> WorkerAgent:
        return WorkerAgent(self.llm, defn.system_prompt, defn.name)

    def _get_worker(self, name: str) -> Optional[WorkerAgent]:
        defn = self.registry.get(name)
        if defn is None:
            return None
        return self._build_worker(defn)

    async def _run_single_worker(
        self,
        agent_name: str,
        agent_task: str,
        iteration: int,
        semaphore: asyncio.Semaphore,
        group: int,
    ) -> Tuple[str, str]:
        """Run one worker inside a semaphore, record trace, return (key, result)."""
        async with semaphore:
            worker = self._get_worker(agent_name)
            if worker is None:
                result = f"ERROR: Unknown agent '{agent_name}'"
            else:
                context = self._get_context()
                t0 = time.monotonic()
                try:
                    result = await asyncio.to_thread(worker.execute, agent_task, context)
                except Exception as exc:
                    result = f"ERROR: {exc}"
                duration_ms = int((time.monotonic() - t0) * 1000)
                self.agent_trace.append(AgentTraceEntry(agent=agent_name, parallel_group=group, duration_ms=duration_ms))
        key = f"{agent_name}_{iteration}"
        return key, result

    async def run_async(
        self,
        task: str,
        max_iterations: int = 5,
        job: Optional["Job"] = None,
        require_approval: bool = False,
        memory_entries: Optional[List[dict]] = None,
    ) -> str:
        """Run the multi-agent workflow asynchronously, with optional approval gate."""
        user_message = _build_user_message(task, memory_entries or [])
        system_prompt = _build_supervisor_prompt(self.registry)
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_message}]
        semaphore = asyncio.Semaphore(MAX_PARALLEL_WORKERS)

        for i in range(max_iterations):
            response = await asyncio.to_thread(self.llm.chat, messages)
            messages.append({"role": "assistant", "content": response})

            # Only accept FINAL after at least one worker has been called
            if "FINAL:" in response and self.results:
                final = response.split("FINAL:")[-1].strip()
                return final

            # --- Parallel delegation ---
            parallel_pairs = _parse_parallel_delegate(response)
            if parallel_pairs:
                group = self._parallel_group
                self._parallel_group += 1
                # validate agents first
                unknown = [name for name, _ in parallel_pairs if self.registry.get(name) is None]
                if unknown:
                    available = ", ".join(self.registry.names())
                    messages.append({"role": "user", "content": f"Unknown agents: {', '.join(unknown)} — available: {available}"})
                    continue

                coros = [self._run_single_worker(name, task_text, i, semaphore, group) for name, task_text in parallel_pairs]
                pairs = await asyncio.gather(*coros)
                for key, result in pairs:
                    self.results[key] = result

                # Feed all results back in one message
                parts = [f"Results from parallel group {group}:"]
                for name, _ in parallel_pairs:
                    key = f"{name}_{i}"
                    parts.append(f"--- {name} ---\n{self.results.get(key, '')}")
                messages.append({"role": "user", "content": "\n".join(parts)})

                # Approval gate after first parallel group
                if require_approval and job is not None and not job.resume_event.is_set():
                    job.intermediate = dict(self.results)
                    job.status = "awaiting_approval"
                    try:
                        await asyncio.wait_for(job.resume_event.wait(), timeout=None)
                    except asyncio.CancelledError:
                        return ""
                    if job.approved_override:
                        agent_task_override = job.approved_override
                        writer_defn = self.registry.get("Writer")
                        if writer_defn:
                            override_worker = self._build_worker(writer_defn)
                            t0 = time.monotonic()
                            result = await asyncio.to_thread(override_worker.execute, agent_task_override, self._get_context())
                            duration_ms = int((time.monotonic() - t0) * 1000)
                            self.agent_trace.append(AgentTraceEntry(agent="Writer", parallel_group=self._parallel_group, duration_ms=duration_ms))
                            self._parallel_group += 1
                            key = f"Writer_override_{i}"
                            self.results[key] = result
                            messages.append({"role": "user", "content": f"Result from Writer:\n{result}"})
                            continue
                    job.status = "executing"
                continue

            # --- Single delegation ---
            if "DELEGATE:" in response and "TASK:" in response:
                agent_name = response.split("DELEGATE:")[-1].split("TASK:")[0].strip()
                agent_task = response.split("TASK:")[-1].strip()

                worker = self._get_worker(agent_name)
                if worker is None:
                    available = ", ".join(self.registry.names())
                    messages.append({"role": "user", "content": f"Unknown agent '{agent_name}' — available: {available}"})
                    continue

                context = self._get_context()
                t0 = time.monotonic()
                result = await asyncio.to_thread(worker.execute, agent_task, context)
                duration_ms = int((time.monotonic() - t0) * 1000)
                self.agent_trace.append(AgentTraceEntry(agent=agent_name, parallel_group=self._parallel_group, duration_ms=duration_ms))
                self._parallel_group += 1
                self.results[f"{agent_name}_{i}"] = result

                # Approval gate: pause after first result (only once — event not yet set)
                if require_approval and job is not None and not job.resume_event.is_set():
                    job.intermediate = dict(self.results)
                    job.status = "awaiting_approval"
                    try:
                        await asyncio.wait_for(job.resume_event.wait(), timeout=None)
                    except asyncio.CancelledError:
                        return ""

                    if job.approved_override:
                        agent_task = job.approved_override
                        writer_defn = self.registry.get("Writer")
                        if writer_defn:
                            override_worker = self._build_worker(writer_defn)
                            t0 = time.monotonic()
                            result = await asyncio.to_thread(override_worker.execute, agent_task, self._get_context())
                            duration_ms = int((time.monotonic() - t0) * 1000)
                            self.agent_trace.append(AgentTraceEntry(agent="Writer", parallel_group=self._parallel_group, duration_ms=duration_ms))
                            self._parallel_group += 1
                            key = f"Writer_override_{i}"
                            self.results[key] = result
                            messages.append({"role": "user", "content": f"Result from Writer:\n{result}"})
                            continue
                    job.status = "executing"

                messages.append({"role": "user", "content": f"Result from {agent_name}:\n{result}"})

        return self._force_final()

    def run(self, task: str, max_iterations: int = 5) -> str:
        """Synchronous wrapper kept for backward compatibility."""
        return asyncio.run(self.run_async(task, max_iterations))

    def _get_context(self) -> str:
        """Build context from previous results."""
        if not self.results:
            return ""
        parts = []
        for key, value in self.results.items():
            parts.append(f"--- {key} ---\n{value}")
        return "\n\n".join(parts)

    def _force_final(self) -> str:
        """Force final output if max iterations reached."""
        if self.results:
            writer_results = [v for k, v in self.results.items() if "Writer" in k]
            if writer_results:
                return writer_results[-1]
            return list(self.results.values())[-1]
        return "Unable to complete task."
