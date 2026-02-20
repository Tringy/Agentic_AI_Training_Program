# Lab 03: Migration Workflow Agent

## Objective
Build a multi-step agent that can migrate code between frameworks using the planning pattern.

**Time Allotted**: 1 hour 45 minutes

## Learning Goals
- Implement the planning agent pattern
- Build multi-step workflows with verification
- Handle complex tasks with tool-use
- Manage state across agent iterations

---

## Choose Your Language

| Aspect | Python | TypeScript |
|--------|--------|------------|
| Directory | `./python` | `./typescript` |
| Framework | FastAPI | Hono |
| State | dataclasses | interfaces + functions |
| Run | `uvicorn main:app --reload` | `npm run dev` |

---

## What You'll Build

An agent that can:
1. Analyze source code to understand its structure
2. Create a migration plan
3. Execute migration steps
4. Verify the migration worked

```
┌─────────────────────────────────────────────────────────────┐
│                 Migration Agent Workflow                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Input: Source files + target framework                     │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ PHASE 1: ANALYSIS                                    │   │
│  │  • Parse source files                                │   │
│  │  • Identify patterns and dependencies                │   │
│  │  • Detect potential issues                           │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                  │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ PHASE 2: PLANNING                                    │   │
│  │  • Create step-by-step migration plan                │   │
│  │  • Identify dependencies between steps               │   │
│  │  • Estimate complexity per step                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                  │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ PHASE 3: EXECUTION                                   │   │
│  │  • Execute each step in order                        │   │
│  │  • Generate migrated code                            │   │
│  │  • Track progress and results                        │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                  │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ PHASE 4: VERIFICATION                                │   │
│  │  • Check migrated code compiles/runs                 │   │
│  │  • Identify any remaining issues                     │   │
│  │  • Generate migration report                         │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Output: Migrated files + report                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Quick Start

### Python Setup

```bash
cd python
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

export ANTHROPIC_API_KEY=your-key
uvicorn main:app --reload
```

### TypeScript Setup

```bash
cd typescript
npm install

export ANTHROPIC_API_KEY=your-key
npm run dev
```

---

## Step-by-Step Instructions

### Step 1: Define the Agent State (15 min)

<details>
<summary><b>Python</b></summary>

```python
# state.py
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum

class Phase(Enum):
    ANALYSIS = "analysis"
    PLANNING = "planning"
    EXECUTION = "execution"
    VERIFICATION = "verification"
    COMPLETE = "complete"

@dataclass
class MigrationStep:
    id: int
    description: str
    status: str = "pending"
    input_files: List[str] = field(default_factory=list)
    output_files: List[str] = field(default_factory=list)
    result: Optional[str] = None

@dataclass
class MigrationState:
    source_framework: str
    target_framework: str
    source_files: Dict[str, str]
    phase: Phase = Phase.ANALYSIS
    analysis: Optional[Dict[str, Any]] = None
    plan: List[MigrationStep] = field(default_factory=list)
    current_step: int = 0
    migrated_files: Dict[str, str] = field(default_factory=dict)
    verification_result: Optional[Dict] = None
    errors: List[str] = field(default_factory=list)
```

</details>

<details>
<summary><b>TypeScript</b></summary>

```typescript
// types.ts
export type Phase = 'analysis' | 'planning' | 'execution' | 'verification' | 'complete';

export interface MigrationStep {
  id: number;
  description: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  inputFiles: string[];
  outputFiles: string[];
  result?: string;
}

export interface MigrationState {
  sourceFramework: string;
  targetFramework: string;
  sourceFiles: Record<string, string>;
  phase: Phase;
  analysis: Record<string, unknown> | null;
  plan: MigrationStep[];
  currentStep: number;
  migratedFiles: Record<string, string>;
  verificationResult: unknown | null;
  errors: string[];
}

// state.ts - Helper functions
export function createInitialState(
  sourceFramework: string,
  targetFramework: string,
  sourceFiles: Record<string, string>
): MigrationState {
  return {
    sourceFramework,
    targetFramework,
    sourceFiles,
    phase: 'analysis',
    analysis: null,
    plan: [],
    currentStep: 0,
    migratedFiles: {},
    verificationResult: null,
    errors: [],
  };
}
```

</details>

### Step 2: Implement the Agent Core (25 min)

<details>
<summary><b>Python</b></summary>

```python
# agent.py
class MigrationAgent:
    def __init__(self, llm_client):
        self.llm = llm_client

    def run(self, state: MigrationState) -> MigrationState:
        """Run through all phases."""
        while state.phase != Phase.COMPLETE:
            state = self._step(state)
            if state.errors:
                break
        return state

    def _step(self, state: MigrationState) -> MigrationState:
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
        # ... analyze each file
        state.phase = Phase.PLANNING
        return state

    def _plan(self, state: MigrationState) -> MigrationState:
        """Phase 2: Create migration plan."""
        # ... create step-by-step plan
        state.phase = Phase.EXECUTION
        return state

    def _execute(self, state: MigrationState) -> MigrationState:
        """Phase 3: Execute migration steps."""
        # ... execute each step
        state.phase = Phase.VERIFICATION
        return state

    def _verify(self, state: MigrationState) -> MigrationState:
        """Phase 4: Verify results."""
        # ... verify migrated code
        state.phase = Phase.COMPLETE
        return state
```

</details>

<details>
<summary><b>TypeScript</b></summary>

```typescript
// agent.ts
export class MigrationAgent {
  private llm: LLMClient;

  constructor(llmClient: LLMClient) {
    this.llm = llmClient;
  }

  async run(state: MigrationState): Promise<MigrationState> {
    while (state.phase !== 'complete') {
      state = await this.step(state);
      if (state.errors.length > 0) break;
    }
    return state;
  }

  private async step(state: MigrationState): Promise<MigrationState> {
    switch (state.phase) {
      case 'analysis':
        return this.analyze(state);
      case 'planning':
        return this.plan(state);
      case 'execution':
        return this.execute(state);
      case 'verification':
        return this.verify(state);
      default:
        return state;
    }
  }

  private async analyze(state: MigrationState): Promise<MigrationState> {
    // ... analyze each file
    return { ...state, phase: 'planning' };
  }

  private async plan(state: MigrationState): Promise<MigrationState> {
    // ... create step-by-step plan
    return { ...state, phase: 'execution' };
  }

  private async execute(state: MigrationState): Promise<MigrationState> {
    // ... execute each step
    return { ...state, phase: 'verification' };
  }

  private async verify(state: MigrationState): Promise<MigrationState> {
    // ... verify migrated code
    return { ...state, phase: 'complete' };
  }
}
```

</details>

### Step 3: Build the API (15 min)

<details>
<summary><b>Python (FastAPI)</b></summary>

```python
# main.py
@app.post("/migrate", response_model=MigrationResponse)
async def migrate(request: MigrationRequest):
    agent = MigrationAgent(llm)
    state = MigrationState(
        source_framework=request.source_framework,
        target_framework=request.target_framework,
        source_files=request.files
    )
    result = agent.run(state)
    return MigrationResponse(
        success=len(result.errors) == 0,
        migrated_files=result.migrated_files,
        plan_executed=[...],
        verification=result.verification_result or {},
        errors=result.errors
    )
```

</details>

<details>
<summary><b>TypeScript (Hono)</b></summary>

```typescript
// index.ts
app.post('/migrate', zValidator('json', MigrationRequestSchema), async (c) => {
  const { source_framework, target_framework, files } = c.req.valid('json');

  const agent = new MigrationAgent(llm);
  const initialState = createInitialState(source_framework, target_framework, files);
  const result = await agent.run(initialState);

  return c.json({
    success: result.errors.length === 0,
    migrated_files: result.migratedFiles,
    plan_executed: result.plan.map(s => ({ id: s.id, description: s.description, status: s.status })),
    verification: result.verificationResult || {},
    errors: result.errors,
  });
});
```

</details>

### Step 4: Test with Sample Migration (15 min)

```bash
# Test migrating Express.js to FastAPI
curl -X POST http://localhost:8000/migrate \
  -H "Content-Type: application/json" \
  -d '{
    "source_framework": "express",
    "target_framework": "fastapi",
    "files": {
      "routes/users.js": "const express = require('\''express'\'');\nconst router = express.Router();\n\nrouter.get('\''/users'\'', async (req, res) => {\n    const users = await db.getUsers();\n    res.json(users);\n});\n\nmodule.exports = router;"
    }
  }'
```

---

## Project Structure

```
lab03-migration-workflow/
├── README.md
├── python/
│   ├── main.py           # FastAPI application
│   ├── agent.py          # MigrationAgent class
│   ├── state.py          # State dataclasses
│   ├── prompts.py        # System prompts
│   └── requirements.txt
└── typescript/
    ├── src/
    │   ├── index.ts      # Hono application
    │   ├── agent.ts      # MigrationAgent class
    │   ├── state.ts      # State management
    │   ├── types.ts      # Type definitions
    │   ├── prompts.ts    # System prompts
    │   └── llm-client.ts
    ├── package.json
    └── tsconfig.json
```

---

## Deliverables

- [ ] Working migration agent with all 4 phases
- [ ] Proper state management
- [ ] Plan creation and execution
- [ ] Verification step
- [ ] Deployed to Railway/Vercel

---

## Extension Challenges

1. **Rollback Support**: Add ability to rollback failed migrations
2. **Parallel Execution**: Execute independent steps in parallel
3. **Human Approval**: Add human-in-the-loop for plan approval
4. **Multiple Frameworks**: Support more source/target combinations

---

**Next**: [Lab 04 - RAG System](../lab04-rag-system/)
