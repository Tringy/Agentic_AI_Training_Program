# Lab 05: Multi-Agent Orchestration

## Objective
Build a quick multi-agent system using the supervisor pattern.

**Time Allotted**: 30 minutes

## Learning Goals
- Implement supervisor pattern for agent coordination
- Build specialized worker agents
- Orchestrate multi-step workflows

---

## Choose Your Language

| Language | Directory | Run Command |
|----------|-----------|-------------|
| Python | `python/` | `uvicorn main:app --reload` |
| TypeScript | `typescript/` | `npm run dev` |

---

## What You'll Build

A mini research assistant with:
- **Supervisor Agent**: Coordinates workers and synthesizes results
- **Researcher Agent**: Finds and summarizes information
- **Writer Agent**: Produces polished output

```
┌─────────────────────────────────────────────────────────────┐
│                  Multi-Agent Architecture                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                    ┌─────────────┐                          │
│                    │ SUPERVISOR  │                          │
│                    │    AGENT    │                          │
│                    └──────┬──────┘                          │
│                           │                                 │
│              ┌────────────┼────────────┐                    │
│              │            │            │                    │
│              ▼            ▼            ▼                    │
│       ┌──────────┐ ┌──────────┐ ┌──────────┐               │
│       │RESEARCHER│ │  WRITER  │ │ REVIEWER │               │
│       │  AGENT   │ │  AGENT   │ │  AGENT   │               │
│       └──────────┘ └──────────┘ └──────────┘               │
│                                                             │
│   Flow:                                                     │
│   1. Supervisor receives task                               │
│   2. Delegates research to Researcher                       │
│   3. Sends research to Writer for polishing                 │
│   4. Optionally sends to Reviewer                           │
│   5. Supervisor synthesizes final output                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Setup

<details>
<summary><b>Python Setup</b></summary>

```bash
cd python

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set your API key
export ANTHROPIC_API_KEY=your_key_here
# Or for OpenAI:
# export OPENAI_API_KEY=your_key_here
# export LLM_PROVIDER=openai
```

</details>

<details>
<summary><b>TypeScript Setup</b></summary>

```bash
cd typescript

# Install dependencies
npm install

# Set your API key
export ANTHROPIC_API_KEY=your_key_here
# Or for OpenAI:
# export OPENAI_API_KEY=your_key_here
# export LLM_PROVIDER=openai
```

</details>

---

## Implementation

### Worker Agents

<details>
<summary><b>Python - agents.py</b></summary>

```python
"""Worker agents for the multi-agent system."""

RESEARCHER_PROMPT = """You are a research specialist.
Your job is to gather and summarize information on a given topic.

For the given topic:
1. Identify key facts and concepts
2. Note important details
3. Highlight relationships between ideas
4. Summarize findings clearly

Be factual and cite what you're basing your information on."""

WRITER_PROMPT = """You are a professional writer.
Your job is to take research and turn it into polished content.

Given research material:
1. Organize information logically
2. Write clear, engaging prose
3. Use appropriate formatting
4. Ensure flow and readability

Match the requested tone and format."""

REVIEWER_PROMPT = """You are a content reviewer.
Your job is to review content for quality and accuracy.

For the given content:
1. Check for factual accuracy
2. Identify unclear sections
3. Suggest improvements
4. Rate overall quality (1-10)

Be constructive in your feedback."""

class WorkerAgent:
    """Base class for worker agents."""

    def __init__(self, llm_client, system_prompt: str, name: str):
        self.llm = llm_client
        self.system_prompt = system_prompt
        self.name = name

    def execute(self, task: str, context: str = "") -> str:
        """Execute a task and return result."""
        user_prompt = task
        if context:
            user_prompt = f"Context:\n{context}\n\nTask:\n{task}"

        response = self.llm.chat([
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_prompt}
        ])

        return response

class ResearcherAgent(WorkerAgent):
    def __init__(self, llm_client):
        super().__init__(llm_client, RESEARCHER_PROMPT, "Researcher")

class WriterAgent(WorkerAgent):
    def __init__(self, llm_client):
        super().__init__(llm_client, WRITER_PROMPT, "Writer")

class ReviewerAgent(WorkerAgent):
    def __init__(self, llm_client):
        super().__init__(llm_client, REVIEWER_PROMPT, "Reviewer")
```

</details>

<details>
<summary><b>TypeScript - agents.ts</b></summary>

```typescript
/**
 * Worker agents for the multi-agent system.
 */

import type { LLMClient } from './llm-client.js';

export const RESEARCHER_PROMPT = `You are a research specialist.
Your job is to gather and summarize information on a given topic.

For the given topic:
1. Identify key facts and concepts
2. Note important details
3. Highlight relationships between ideas
4. Summarize findings clearly

Be factual and cite what you're basing your information on.`;

export const WRITER_PROMPT = `You are a professional writer.
Your job is to take research and turn it into polished content.

Given research material:
1. Organize information logically
2. Write clear, engaging prose
3. Use appropriate formatting
4. Ensure flow and readability

Match the requested tone and format.`;

export const REVIEWER_PROMPT = `You are a content reviewer.
Your job is to review content for quality and accuracy.

For the given content:
1. Check for factual accuracy
2. Identify unclear sections
3. Suggest improvements
4. Rate overall quality (1-10)

Be constructive in your feedback.`;

/**
 * Base class for worker agents.
 */
export class WorkerAgent {
  constructor(
    protected llm: LLMClient,
    protected systemPrompt: string,
    public readonly name: string
  ) {}

  async execute(task: string, context: string = ''): Promise<string> {
    let userPrompt = task;
    if (context) {
      userPrompt = `Context:\n${context}\n\nTask:\n${task}`;
    }

    return this.llm.chat([
      { role: 'system', content: this.systemPrompt },
      { role: 'user', content: userPrompt },
    ]);
  }
}

export class ResearcherAgent extends WorkerAgent {
  constructor(llm: LLMClient) {
    super(llm, RESEARCHER_PROMPT, 'Researcher');
  }
}

export class WriterAgent extends WorkerAgent {
  constructor(llm: LLMClient) {
    super(llm, WRITER_PROMPT, 'Writer');
  }
}

export class ReviewerAgent extends WorkerAgent {
  constructor(llm: LLMClient) {
    super(llm, REVIEWER_PROMPT, 'Reviewer');
  }
}
```

</details>

---

### Supervisor Agent

<details>
<summary><b>Python - supervisor.py</b></summary>

```python
"""Supervisor agent that coordinates workers."""
from typing import Dict, List
from agents import ResearcherAgent, WriterAgent, ReviewerAgent

SUPERVISOR_PROMPT = """You are a supervisor managing a team of specialized agents.

Available agents:
- Researcher: Finds and summarizes information
- Writer: Creates polished content from research
- Reviewer: Reviews content for quality

Your job:
1. Analyze the incoming task
2. Decide which agent(s) to use
3. Coordinate their work
4. Synthesize the final output

For each step, output in this format:
DELEGATE: [agent_name]
TASK: [specific task for that agent]

When all work is done, output:
FINAL: [synthesized final output]"""

class SupervisorAgent:
    """Supervisor that coordinates worker agents."""

    def __init__(self, llm_client):
        self.llm = llm_client

        # Initialize workers
        self.workers = {
            "Researcher": ResearcherAgent(llm_client),
            "Writer": WriterAgent(llm_client),
            "Reviewer": ReviewerAgent(llm_client)
        }

        self.results = {}

    def run(self, task: str, max_iterations: int = 5) -> str:
        """Run the multi-agent workflow."""
        messages = [
            {"role": "system", "content": SUPERVISOR_PROMPT},
            {"role": "user", "content": f"Task: {task}"}
        ]

        for i in range(max_iterations):
            # Get supervisor decision
            response = self.llm.chat(messages)
            messages.append({"role": "assistant", "content": response})

            # Check if done
            if "FINAL:" in response:
                final = response.split("FINAL:")[-1].strip()
                return final

            # Parse and execute delegation
            if "DELEGATE:" in response and "TASK:" in response:
                agent_name = response.split("DELEGATE:")[-1].split("TASK:")[0].strip()
                agent_task = response.split("TASK:")[-1].strip()

                if agent_name in self.workers:
                    # Execute worker
                    context = self._get_context()
                    result = self.workers[agent_name].execute(agent_task, context)

                    # Store result
                    self.results[f"{agent_name}_{i}"] = result

                    # Feed back to supervisor
                    messages.append({
                        "role": "user",
                        "content": f"Result from {agent_name}:\n{result}"
                    })

        return self._force_final()

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
            # Return last writer result if available
            writer_results = [v for k, v in self.results.items() if "Writer" in k]
            if writer_results:
                return writer_results[-1]

            # Otherwise return last result
            return list(self.results.values())[-1]

        return "Unable to complete task."
```

</details>

<details>
<summary><b>TypeScript - supervisor.ts</b></summary>

```typescript
/**
 * Supervisor agent that coordinates workers.
 */

import type { LLMClient } from './llm-client.js';
import { ResearcherAgent, WriterAgent, ReviewerAgent, WorkerAgent } from './agents.js';

const SUPERVISOR_PROMPT = `You are a supervisor managing a team of specialized agents.

Available agents:
- Researcher: Finds and summarizes information
- Writer: Creates polished content from research
- Reviewer: Reviews content for quality

Your job:
1. Analyze the incoming task
2. Decide which agent(s) to use
3. Coordinate their work
4. Synthesize the final output

For each step, output in this format:
DELEGATE: [agent_name]
TASK: [specific task for that agent]

When all work is done, output:
FINAL: [synthesized final output]`;

export interface SupervisorResult {
  result: string;
  stepsTaken: number;
}

/**
 * Supervisor that coordinates worker agents.
 */
export class SupervisorAgent {
  private workers: Map<string, WorkerAgent>;
  private results: Map<string, string> = new Map();

  constructor(private llm: LLMClient) {
    this.workers = new Map([
      ['Researcher', new ResearcherAgent(llm)],
      ['Writer', new WriterAgent(llm)],
      ['Reviewer', new ReviewerAgent(llm)],
    ]);
  }

  async run(task: string, maxIterations: number = 5): Promise<SupervisorResult> {
    // Reset results for new task
    this.results.clear();

    const messages: Array<{ role: string; content: string }> = [
      { role: 'system', content: SUPERVISOR_PROMPT },
      { role: 'user', content: `Task: ${task}` },
    ];

    for (let i = 0; i < maxIterations; i++) {
      // Get supervisor decision
      const response = await this.llm.chat(messages);
      messages.push({ role: 'assistant', content: response });

      // Check if done
      if (response.includes('FINAL:')) {
        const final = response.split('FINAL:').pop()?.trim() || '';
        return { result: final, stepsTaken: this.results.size };
      }

      // Parse and execute delegation
      if (response.includes('DELEGATE:') && response.includes('TASK:')) {
        const agentName = response
          .split('DELEGATE:')[1]
          ?.split('TASK:')[0]
          ?.trim();

        const agentTask = response.split('TASK:').pop()?.trim() || '';

        if (agentName && this.workers.has(agentName)) {
          const worker = this.workers.get(agentName)!;

          // Execute worker
          const context = this.getContext();
          const result = await worker.execute(agentTask, context);

          // Store result
          this.results.set(`${agentName}_${i}`, result);

          // Feed back to supervisor
          messages.push({
            role: 'user',
            content: `Result from ${agentName}:\n${result}`,
          });
        }
      }
    }

    return { result: this.forceFinal(), stepsTaken: this.results.size };
  }

  private getContext(): string {
    if (this.results.size === 0) {
      return '';
    }

    const parts: string[] = [];
    for (const [key, value] of this.results) {
      parts.push(`--- ${key} ---\n${value}`);
    }
    return parts.join('\n\n');
  }

  private forceFinal(): string {
    if (this.results.size > 0) {
      // Return last writer result if available
      const writerResults = Array.from(this.results.entries())
        .filter(([key]) => key.includes('Writer'))
        .map(([, value]) => value);

      if (writerResults.length > 0) {
        return writerResults[writerResults.length - 1];
      }

      // Otherwise return last result
      const values = Array.from(this.results.values());
      return values[values.length - 1];
    }

    return 'Unable to complete task.';
  }
}
```

</details>

---

### API Server

<details>
<summary><b>Python - main.py</b></summary>

```python
"""Multi-agent API."""
from fastapi import FastAPI
from pydantic import BaseModel
from supervisor import SupervisorAgent
from llm_client import get_llm_client

app = FastAPI(title="Multi-Agent System")

llm = get_llm_client("anthropic")
supervisor = SupervisorAgent(llm)

class TaskRequest(BaseModel):
    task: str
    max_iterations: int = 5

class TaskResponse(BaseModel):
    result: str
    steps_taken: int

@app.post("/run", response_model=TaskResponse)
async def run_task(request: TaskRequest):
    """Run a multi-agent task."""
    # Reset for new task
    supervisor.results = {}

    result = supervisor.run(request.task, request.max_iterations)

    return TaskResponse(
        result=result,
        steps_taken=len(supervisor.results)
    )

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

</details>

<details>
<summary><b>TypeScript - index.ts</b></summary>

```typescript
/**
 * Multi-Agent System - Hono API Application
 */

import 'dotenv/config';
import { Hono } from 'hono';
import { cors } from 'hono/cors';
import { zValidator } from '@hono/zod-validator';
import { serve } from '@hono/node-server';
import { z } from 'zod';

import { SupervisorAgent } from './supervisor.js';
import { getLLMClient, type LLMProvider } from './llm-client.js';

const app = new Hono();

// CORS middleware
app.use('/*', cors());

// Initialize
const provider = (process.env.LLM_PROVIDER || 'anthropic') as LLMProvider;
const llm = getLLMClient(provider);
const supervisor = new SupervisorAgent(llm);

// Request schemas
const TaskRequestSchema = z.object({
  task: z.string().min(1),
  max_iterations: z.number().int().min(1).max(10).default(5),
});

/**
 * Run a multi-agent task
 */
app.post('/run', zValidator('json', TaskRequestSchema), async (c) => {
  try {
    const { task, max_iterations } = c.req.valid('json');
    const result = await supervisor.run(task, max_iterations);

    return c.json({
      result: result.result,
      steps_taken: result.stepsTaken,
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Unknown error';
    return c.json({ error: message }, 500);
  }
});

/**
 * Health check
 */
app.get('/health', (c) => {
  return c.json({ status: 'healthy', provider });
});

// Start server
const port = parseInt(process.env.PORT || '8000', 10);

console.log(`Multi-Agent System starting on port ${port}...`);
console.log(`Using LLM provider: ${provider}`);

serve({
  fetch: app.fetch,
  port,
});

export default app;
```

</details>

---

## Quick Test

<details>
<summary><b>Python</b></summary>

```bash
cd python

# Run the server
uvicorn main:app --reload

# Test with a research task
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Write a brief explanation of how RAG systems work for a technical blog post",
    "max_iterations": 5
  }'
```

</details>

<details>
<summary><b>TypeScript</b></summary>

```bash
cd typescript

# Run the server
npm run dev

# Test with a research task
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Write a brief explanation of how RAG systems work for a technical blog post",
    "max_iterations": 5
  }'
```

</details>

**Expected flow:**
1. Supervisor delegates to Researcher to gather RAG information
2. Supervisor sends research to Writer for blog post format
3. Supervisor synthesizes final output

---

## Deliverables

- [ ] Working multi-agent system
- [ ] Supervisor + at least 2 worker agents
- [ ] Tested end-to-end workflow

---

## Extension Ideas (Post-Training)

1. **Parallel Workers**: Run independent workers in parallel
2. **Human Approval**: Add human-in-the-loop for important decisions
3. **Memory**: Add persistent memory across tasks
4. **More Workers**: Add specialized agents (Editor, Fact-Checker, etc.)

---

**Next**: [Capstone Project](../capstone-options/)
