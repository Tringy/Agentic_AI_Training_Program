---
applyTo: "**/prompts.py,**/llm_client.py,**/analyzer.py,**/agent.py"
---

# LLM Agent Patterns

These conventions apply to every lab and capstone project that calls an LLM. They ensure consistent, testable behaviour across single-call agents, multi-step agents, RAG pipelines, and multi-agent systems.

## LLMClient ABC Pattern

All LLM interaction is abstracted behind a shared interface. **Never call provider SDKs directly in business logic** — always go through `LLMClient`.

```python
from abc import ABC, abstractmethod
from typing import List, Dict

class LLMClient(ABC):
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]]) -> str:
        """Send a message list and return the text response."""
        ...

class AnthropicClient(LLMClient):
    def __init__(self):
        import anthropic
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    def chat(self, messages: List[Dict[str, str]]) -> str:
        # Anthropic requires system message as separate param
        system = next((m["content"] for m in messages if m["role"] == "system"), "")
        user_msgs = [m for m in messages if m["role"] != "system"]
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=8096,
            system=system,
            messages=user_msgs,
        )
        return response.content[0].text

class OpenAIClient(LLMClient):
    def __init__(self):
        from openai import OpenAI
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def chat(self, messages: List[Dict[str, str]]) -> str:
        response = self.client.chat.completions.create(
            model="gpt-4o", messages=messages
        )
        return response.choices[0].message.content

class GoogleClient(LLMClient):
    def __init__(self):
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel("gemini-2.5-flash-lite")

    def chat(self, messages: List[Dict[str, str]]) -> str:
        # Concatenate system + user messages into a single prompt
        full_prompt = "\n".join(m["content"] for m in messages)
        response = self.model.generate_content(full_prompt)
        return response.text

def get_llm_client(provider: str) -> LLMClient:
    clients = {
        "anthropic": AnthropicClient,
        "openai":    OpenAIClient,
        "google":    GoogleClient,
    }
    if provider not in clients:
        raise ValueError(f"Unknown provider: {provider}. Choose from {list(clients)}")
    return clients[provider]()
```

## Structured JSON Output Convention

All prompts must end with an explicit JSON schema instruction. Always parse defensively:

```python
def _parse_json(response: str) -> dict:
    """Strip markdown fences and parse JSON."""
    text = response.strip()
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]
    return json.loads(text.strip())
```

Immediately validate the result with a Pydantic model:

```python
data = self._parse_json(raw)
return AnalysisResult(**data)   # raises ValidationError on schema mismatch
```

## Prompt Engineering Conventions

### System prompt pattern
```python
ANALYSIS_SYSTEM = """You are an expert code reviewer. Analyze the provided code and return ONLY valid JSON — no markdown, no explanation outside the JSON.

Return this exact schema:
{
  "summary": "string",
  "issues": [{"severity": "critical|high|medium|low", "line": number|null,
               "category": "bug|security|performance|style|maintainability",
               "description": "string", "suggestion": "string"}],
  "suggestions": ["string"],
  "metrics": {"complexity": "low|medium|high",
               "readability": "poor|fair|good|excellent",
               "test_coverage_estimate": "none|partial|good"}
}"""
```

### User prompt pattern
```python
def build_user_prompt(code: str, language: str) -> str:
    return f"Analyze this {language} code:\n\n```{language}\n{code}\n```"
```

### Injecting framework profiles
```python
def build_migration_prompt(source: str, target: str, code: str,
                            source_profile: dict, target_profile: dict) -> str:
    return MIGRATION_PROMPT.format(
        source=source, target=target, code=code,
        source_profile=json.dumps(source_profile, indent=2),
        target_profile=json.dumps(target_profile, indent=2),
    )
```

## Multi-Step Agent State Machine

When an agent needs to pause for human input or complete multiple LLM-driven phases, use a `Phase` enum and drive all transitions through a central `run()` method. Store state in a dataclass (or Pydantic model) keyed by a `job_id` so individual HTTP endpoints can read/update it.

```python
from enum import Enum
from dataclasses import dataclass, field

class Phase(Enum):
    # Define phases that match your workflow
    # Common pattern: ANALYZE → PLAN → AWAITING_APPROVAL → EXECUTE → VERIFY → COMPLETE
    ANALYSIS          = "analysis"
    PLANNING          = "planning"
    AWAITING_APPROVAL = "awaiting_approval"
    EXECUTION         = "execution"
    VERIFICATION      = "verification"
    COMPLETE          = "complete"

class MyAgent:
    def run(self, state: MyState):
        """Drive agent forward until a pause point (e.g. human approval)."""
        if state.phase == Phase.ANALYSIS:
            self._analyze(state)    # transitions state.phase → PLANNING
        if state.phase == Phase.PLANNING:
            self._plan(state)       # transitions state.phase → AWAITING_APPROVAL
        # Returns here — the HTTP layer persists state and returns job_id to caller

    def resume(self, state: MyState):
        """Called after a human gate is passed — drives execution to completion."""
        state.phase = Phase.EXECUTION
        self._execute(state)        # → VERIFICATION
        if state.phase == Phase.VERIFICATION:
            self._verify(state)     # → COMPLETE
```

**Principles:**
- Each phase method is responsible for exactly one transition: it sets `state.phase` at the end
- The HTTP endpoint for approval calls `resume()` as a `BackgroundTask` so it returns `202` immediately
- Auto-reject via `asyncio` timeout: cancel the timeout task on `approve` or `reject`

## Rollback / Snapshot Pattern

For any agent that mutates shared state across multiple steps, take a deep copy snapshot before each mutation so rollback is safe and deterministic:

```python
import copy

def _take_snapshot(state, step):
    snapshot = Snapshot(
        step_index=step.id,
        step_description=step.description,
        timestamp=datetime.now().isoformat(),
        migrated_files=copy.deepcopy(state.migrated_files),
    )
    state.snapshots.append(snapshot)

def _rollback(state, to_step: int, reason: str):
    target = next((s for s in reversed(state.snapshots) if s.step_index == to_step), None)
    if target:
        state.migrated_files = copy.deepcopy(target.migrated_files)
        state.rollback_history.append(RollbackRecord(
            timestamp=datetime.now().isoformat(),
            from_step=state.current_step,
            to_step=to_step,
            reason=reason,
        ))
```

## Parallel Step Execution via Kahn's Algorithm

When an agent's plan contains steps with declared dependencies, compute independent groups (waves) via Kahn's topological sort, then execute each wave with `asyncio.gather`. This minimises wall-clock time while respecting ordering constraints.

```python
def _build_waves(plan: List[MigrationStep]) -> List[List[int]]:
    """Returns list of waves; each wave is a list of step IDs safe to run in parallel."""
    in_degree = {s.id: len(s.dependencies) for s in plan}
    dependents = {s.id: [] for s in plan}
    for step in plan:
        for dep in step.dependencies:
            dependents[dep].append(step.id)

    ready = [sid for sid, deg in in_degree.items() if deg == 0]
    waves = []
    while ready:
        waves.append(list(ready))
        next_ready = []
        for sid in ready:
            for dep_id in dependents[sid]:
                in_degree[dep_id] -= 1
                if in_degree[dep_id] == 0:
                    next_ready.append(dep_id)
        ready = next_ready

    if sum(len(w) for w in waves) != len(plan):
        raise ValueError("Dependency cycle detected in migration plan")
    return waves
```

Execute each wave concurrently:

```python
async def _execute_async(state):
    step_by_id = {s.id: s for s in state.plan}
    for wave in state.waves:
        tasks = [_run_step(state, step_by_id[sid]) for sid in wave]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        if any(isinstance(r, Exception) for r in results):
            _rollback(state, ...)   # restore last good snapshot
            break
```

## Supervisor / Worker Pattern (Multi-Agent)

For multi-agent systems, the supervisor delegates to specialised workers and synthesises their outputs. Each worker is its own `LLMClient`-backed class.

```python
class SupervisorAgent:
    def __init__(self, llm: LLMClient):
        self.llm = llm
        self.researcher = ResearcherAgent(llm)
        self.writer = WriterAgent(llm)

    def run(self, task: str) -> str:
        # 1. Decompose task
        subtasks = self._decompose(task)
        # 2. Delegate
        research = self.researcher.run(subtasks["research"])
        draft    = self.writer.run(subtasks["write"], context=research)
        # 3. Synthesise
        return self._synthesise(task, research, draft)

    def _decompose(self, task: str) -> dict:
        messages = [
            {"role": "system", "content": DECOMPOSE_PROMPT},
            {"role": "user",   "content": task},
        ]
        return self._parse_json(self.llm.chat(messages))
```

**Principles:**
- Each worker has a single, well-defined responsibility
- Workers receive structured inputs and return structured outputs (JSON → Pydantic)
- The supervisor owns orchestration logic; workers own domain logic
- Workers should be independently testable (pass mocked `LLMClient`)

## Provider Selection

Instantiate the LLM client once at application startup and inject it into every class that needs it:

```python
# main.py
provider = os.getenv("LLM_PROVIDER", "google")
llm = get_llm_client(provider)
agent = MyAgent(llm)
```

Choosing a default provider:
- `google` (Gemini) — lowest cost, good for CRUD-adjacent tasks and development
- `anthropic` (Claude) — best instruction following; prefer for complex multi-step agents
- `openai` (GPT-4o) — strong at coding tasks; preferred when embedding is also needed (same SDK)

To add a new provider: implement `LLMClient`, add it to the `clients` dict in `get_llm_client`, document its required env var (`{PROVIDER}_API_KEY`).
