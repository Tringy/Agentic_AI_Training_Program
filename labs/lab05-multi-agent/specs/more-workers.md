# More Workers

## Overview
The current system has three fixed agents: Researcher, Writer, Reviewer. This feature
makes the worker roster **configurable** — new specialist agents (Editor, Fact-Checker,
Translator, SEO-Optimizer, etc.) can be registered without modifying supervisor or
orchestration logic. Each agent is defined by a name, a system prompt, and an optional
description that is surfaced to the supervisor so it can make informed delegation
decisions.

## Related Specs
| Relationship | Spec file | Why |
|---|---|---|
| required by | `specs/parallel-workers.md` | PARALLEL_DELEGATE lists agent names; the registry is the authoritative source of available agents |
| required by | `specs/human-approval.md` | The approval payload's intermediate dict uses agent names from the registry as keys |

## API Contract

### `GET /agents`
List all registered agents and their descriptions.

**Response (`200`):**
```json
{
  "agents": [
    {
      "name": "Researcher",
      "description": "Finds and summarizes information on a topic",
      "builtin": true
    },
    {
      "name": "Editor",
      "description": "Polishes prose for grammar, clarity, and conciseness",
      "builtin": false
    }
  ]
}
```

### `POST /agents`
Register a new custom agent.

**Request:**
```json
{
  "name": "string — unique, alphanumeric + hyphens, max 32 chars",
  "system_prompt": "string — the full system prompt given to this agent",
  "description": "string — one sentence, shown to the supervisor"
}
```

**Success response (`201`):**
```json
{ "name": "string", "description": "string", "builtin": false }
```

**Error responses:**
| Status | Condition |
|--------|-----------|
| 409 | An agent with this name already exists |
| 422 | Validation failed (name format, missing fields) |

### `DELETE /agents/{name}`
Remove a custom agent. Built-in agents (Researcher, Writer, Reviewer) cannot be deleted.

**Response (`200`):**
```json
{ "name": "string", "deleted": true }
```

**Error responses:**
| Status | Condition |
|--------|-----------|
| 404 | Agent not found |
| 403 | Attempt to delete a built-in agent |

## Data Model Changes

In-memory registry — no persistence across restarts (custom agents must be
re-registered after restart, or a future spec can add SQLite backing).

```python
# agent_registry.py
from dataclasses import dataclass
from typing import Dict

@dataclass
class AgentDefinition:
    name: str
    system_prompt: str
    description: str
    builtin: bool = False

class AgentRegistry:
    def __init__(self):
        self._agents: Dict[str, AgentDefinition] = {}

    def register(self, defn: AgentDefinition) -> None: ...
    def get(self, name: str) -> AgentDefinition | None: ...
    def list(self) -> list[AgentDefinition]: ...
    def delete(self, name: str) -> bool: ...   # returns False if builtin
```

The three built-in agents are pre-registered at startup using their existing prompts
from `agents.py`.

## Behaviour

1. At startup, the built-in agents (Researcher, Writer, Reviewer) are registered in
   the `AgentRegistry` with `builtin=True`.
2. `SupervisorAgent.__init__` no longer hard-codes `self.workers = {...}`. Instead it
   accepts a reference to the registry and builds workers dynamically:
   ```python
   def _build_worker(self, defn: AgentDefinition) -> WorkerAgent:
       return WorkerAgent(self.llm, defn.system_prompt, defn.name)
   ```
3. The supervisor prompt's "Available agents" section is generated dynamically from
   the registry:
   ```
   Available agents:
   - Researcher: Finds and summarizes information on a topic
   - Writer: Creates polished content from research
   - Editor: Polishes prose for grammar, clarity, and conciseness
   ```
4. When the supervisor delegates to an agent not in the registry, the unknown name is
   logged and the iteration is skipped (fed back as
   `"Unknown agent '{name}' — available: ..."`) so the supervisor can self-correct.
5. `POST /agents` validates that `name` matches `^[A-Za-z][A-Za-z0-9-]{0,31}$` and
   that no agent with the same name (case-insensitive) exists.

## Acceptance Criteria

```
GIVEN the server starts
WHEN GET /agents is called
THEN Researcher, Writer, and Reviewer are listed with builtin=true

GIVEN POST /agents is called with a valid name, system_prompt, and description
THEN the response is 201 with the new agent's details
AND GET /agents includes the new agent
AND POST /run can delegate to the new agent by name

GIVEN POST /agents is called with a name that already exists
THEN the response is 409

GIVEN POST /agents is called with a name containing spaces
THEN the response is 422

GIVEN DELETE /agents/{name} is called for a custom agent
THEN the response is 200 with deleted=true
AND GET /agents no longer includes it
AND the supervisor prompt no longer lists it

GIVEN DELETE /agents/Researcher is called
THEN the response is 403

GIVEN the supervisor delegates to an unregistered agent name "Translator"
WHEN no such agent exists in the registry
THEN the iteration is skipped
AND the supervisor receives "Unknown agent 'Translator' — available: Researcher, Writer, Reviewer"
AND the run continues without crashing

GIVEN a custom agent "Editor" is registered
WHEN POST /run is called with a task that requires editing
THEN the supervisor can successfully delegate to "Editor"
AND the Editor's output appears in steps_taken count
```

## Out of Scope
- Persisting custom agent definitions to SQLite across restarts
- Per-agent rate limiting or cost tracking
- Versioning of agent system prompts
- Agent chaining rules (forcing Researcher always before Writer)
