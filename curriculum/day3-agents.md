# Day 3: Agent Architectures

## Learning Objectives

By the end of Day 3, you will be able to:
- Explain what makes an AI "agent" vs. a simple LLM call
- Implement context management and memory systems
- Implement tool-use and function calling across LLM providers
- Ensure structured, validated outputs from agents
- Apply agent patterns like ReAct, Planning, and Verification
- Design and build multi-agent systems
- Choose the right framework for different agent needs
- Build and deploy a complete migration workflow agent

---

## Table of Contents

1. [Agent Fundamentals](#fundamentals)
2. [Tool-Use & Function Calling](#tool-use)
3. [Agent Patterns](#patterns)
4. [Exercise 1: Design an Agent](#exercise-1)
5. [Multi-Agent Systems](#multi-agent)
6. [Framework Comparison](#frameworks)
7. [Lab 03: Migration Workflow Agent](#lab-03)

---

<a name="fundamentals"></a>
## 1. Agent Fundamentals (1 hour)

### 1.1 What Makes an "Agent"?

An **agent** is an LLM-powered system that can **autonomously decide** what actions to take to accomplish a goal. Unlike a simple LLM call where you ask a question and get an answer, an agent can:

1. **Perceive** its environment (receive inputs and understand context)
2. **Reason** about what to do next (LLM decides which action is needed)
3. **Act** on the environment (call functions, use tools, access APIs)
4. **Iterate** based on results (check if goal is achieved, decide next step, repeat)

**The key difference: Autonomy and iteration**

| Simple LLM Call | Agent |
|----------------|-------|
| **You decide** what to ask | **Agent decides** what actions to take |
| Single request → single response | Loops until task complete |
| No access to external tools | Can use multiple tools autonomously |
| Stateless (no memory) | Maintains state and memory across steps |
| Example: "Summarize this text" | Example: "Research competitor pricing and create a comparison report" |

**Real-world analogy:**
- **Simple LLM**: Like asking someone a question. They answer once and you're done.
- **Agent**: Like delegating a task to an assistant. They figure out what steps are needed, gather information, use tools (web search, calculators, databases), and come back when the job is done.

**Why agents matter:**
Without agents, you'd need to manually orchestrate every step:
1. You call the LLM: "What competitors should I research?"
2. LLM responds with a list
3. **You manually** search the web for each competitor
4. **You manually** parse the results
5. **You manually** call the LLM again to summarize findings
6. **You manually** format the final report

With an agent, you just say: "Research competitor pricing and create a comparison report"—and the agent handles steps 1-6 automatically.

```
┌─────────────────────────────────────────────────────────────────┐
│                        The Agent Loop                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                    ┌─────────────┐                              │
│                    │   OBSERVE   │ ◄───────────────┐            │
│                    └──────┬──────┘                 │            │
│                           │                        │            │
│                           ▼                        │            │
│                    ┌─────────────┐                 │            │
│                    │    THINK    │                 │ Results    │
│                    │    (LLM)    │                 │            │
│                    └──────┬──────┘                 │            │
│                           │                        │            │
│                           ▼                        │            │
│                    ┌─────────────┐                 │            │
│          ┌─────────│   DECIDE    │─────────┐       │            │
│          │         └─────────────┘         │       │            │
│          │                                 │       │            │
│          ▼                                 ▼       │            │
│   ┌─────────────┐                   ┌─────────────┐│            │
│   │  USE TOOL   │───────────────────│    DONE     ││            │
│   └─────────────┘                   └─────────────┘│            │
│          │                                         │            │
│          └─────────────────────────────────────────┘            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Agent vs. Simple LLM Call:**

| Simple LLM Call | Agent |
|-----------------|-------|
| Single request → response | Iterative loop |
| No external actions | Uses tools/APIs |
| Stateless | Maintains state/memory |
| Deterministic flow | Dynamic based on results |
| Human controls iteration | Agent controls iteration |

### 1.2 Core Agent Components

<details>
<summary><b>Python</b></summary>

```python
# Minimal agent structure
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class AgentState:
    """Represents the current state of an agent."""
    messages: List[Dict[str, str]]
    tool_results: List[Any]
    iterations: int
    is_complete: bool

class Tool(ABC):
    """Base class for agent tools."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name for the LLM to reference."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Description of what the tool does."""
        pass

    @property
    @abstractmethod
    def parameters(self) -> Dict[str, Any]:
        """JSON schema for tool parameters."""
        pass

    @abstractmethod
    def execute(self, **kwargs) -> str:
        """Execute the tool and return result."""
        pass

class Agent:
    """Basic agent implementation."""

    def __init__(
        self,
        llm_client,
        tools: List[Tool],
        system_prompt: str,
        max_iterations: int = 10
    ):
        self.llm = llm_client
        self.tools = {t.name: t for t in tools}
        self.system_prompt = system_prompt
        self.max_iterations = max_iterations

    def run(self, user_input: str) -> str:
        """Run the agent loop."""
        state = AgentState(
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_input}
            ],
            tool_results=[],
            iterations=0,
            is_complete=False
        )

        while not state.is_complete and state.iterations < self.max_iterations:
            state = self._step(state)
            state.iterations += 1

        # Return final response
        return state.messages[-1]["content"]

    def _step(self, state: AgentState) -> AgentState:
        """Single step of the agent loop."""
        # Get LLM response with tool options
        response = self.llm.chat_with_tools(
            messages=state.messages,
            tools=list(self.tools.values())
        )

        # Check if LLM wants to use a tool
        if response.tool_calls:
            for tool_call in response.tool_calls:
                tool = self.tools[tool_call.name]
                result = tool.execute(**tool_call.arguments)
                state.tool_results.append(result)
                state.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })
        else:
            # No tool call = final response
            state.messages.append({
                "role": "assistant",
                "content": response.content
            })
            state.is_complete = True

        return state
```

</details>

<details>
<summary><b>TypeScript</b></summary>

```typescript
// Minimal agent structure
interface AgentState {
  messages: Array<{ role: string; content: string }>;
  toolResults: any[];
  iterations: number;
  isComplete: boolean;
}

interface ToolDefinition {
  name: string;
  description: string;
  parameters: Record<string, any>;
}

abstract class Tool {
  abstract get name(): string;
  abstract get description(): string;
  abstract get parameters(): Record<string, any>;
  abstract execute(args: Record<string, any>): Promise<string>;

  toDefinition(): ToolDefinition {
    return {
      name: this.name,
      description: this.description,
      parameters: this.parameters,
    };
  }
}

class Agent {
  private tools: Map<string, Tool>;

  constructor(
    private llm: LLMClient,
    tools: Tool[],
    private systemPrompt: string,
    private maxIterations: number = 10
  ) {
    this.tools = new Map(tools.map((t) => [t.name, t]));
  }

  async run(userInput: string): Promise<string> {
    let state: AgentState = {
      messages: [
        { role: 'system', content: this.systemPrompt },
        { role: 'user', content: userInput },
      ],
      toolResults: [],
      iterations: 0,
      isComplete: false,
    };

    while (!state.isComplete && state.iterations < this.maxIterations) {
      state = await this.step(state);
      state.iterations++;
    }

    // Return final response
    return state.messages[state.messages.length - 1].content;
  }

  private async step(state: AgentState): Promise<AgentState> {
    // Get LLM response with tool options
    const response = await this.llm.chatWithTools(
      state.messages,
      Array.from(this.tools.values()).map((t) => t.toDefinition())
    );

    // Check if LLM wants to use a tool
    if (response.toolCalls && response.toolCalls.length > 0) {
      for (const toolCall of response.toolCalls) {
        const tool = this.tools.get(toolCall.name)!;
        const result = await tool.execute(toolCall.arguments);
        state.toolResults.push(result);
        state.messages.push({
          role: 'tool',
          content: result,
        });
      }
    } else {
      // No tool call = final response
      state.messages.push({
        role: 'assistant',
        content: response.content,
      });
      state.isComplete = true;
    }

    return state;
  }
}
```

</details>

### 1.3 Memory Types

Agents need different types of memory to function effectively. Think of memory as the "knowledge retention system" that makes an agent intelligent over time.

**Why memory matters:**
Without memory, every conversation with your agent starts from scratch. The agent can't remember user preferences, learn from past mistakes, or maintain context across sessions. This severely limits usefulness for real applications.

**Human analogy:**
- **Short-term memory**: Like remembering what was just said in the current conversation
- **Long-term memory**: Like remembering someone's name, preferences, or past experiences
- **Episodic memory**: Like remembering "Last time I tried this approach, it didn't work"
- **Working memory**: Like your mental scratch pad when solving a problem

```
┌─────────────────────────────────────────────────────────────────┐
│                       Agent Memory Types                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  SHORT-TERM MEMORY                                              │
│  ─────────────────                                              │
│  • Current conversation messages                                │
│  • Tool results from current task                               │
│  • Lives in context window                                      │
│  • Lost when context is cleared                                 │
│                                                                 │
│  LONG-TERM MEMORY                                               │
│  ────────────────                                               │
│  • Persisted to database/file                                   │
│  • User preferences, past interactions                          │
│  • Retrieved via RAG or explicit query                          │
│  • Survives across sessions                                     │
│                                                                 │
│  EPISODIC MEMORY                                                │
│  ───────────────                                                │
│  • Summaries of past task completions                           │
│  • "I did X before and it worked/failed"                        │
│  • Helps agent learn from experience                            │
│                                                                 │
│  WORKING MEMORY                                                 │
│  ──────────────                                                 │
│  • Scratchpad for current reasoning                             │
│  • Intermediate results                                         │
│  • Plan execution state                                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Practical examples for each memory type:**

**SHORT-TERM MEMORY (Current Conversation)**
- **Example**: Code review agent
  - Stores: Current conversation messages, code being reviewed
  - Use case: "Looking at lines 10-15 you mentioned earlier, I see the same pattern on line 42"
  - Lifetime: Cleared when conversation ends
  - Storage: In the context window sent to LLM

**LONG-TERM MEMORY (Persistent Facts)**
- **Example**: Customer support agent
  - Stores: User preferences ("prefers email over phone"), account history, past issues
  - Use case: "I remember you had trouble with payments last month. Is this related?"
  - Lifetime: Persists across sessions, stored in database
  - Storage: Vector database (Pinecone, Chroma, etc.)

**EPISODIC MEMORY (Task History)**
- **Example**: DevOps agent
  - Stores: Past deployments and their outcomes
  - Use case: "Last time we deployed on Friday, it caused issues. Let's schedule for Thursday instead."
  - Lifetime: Permanent record of completed tasks
  - Storage: Database with task logs

**WORKING MEMORY (Current Task State)**
- **Example**: Research agent gathering information
  - Stores: Intermediate results, current step in multi-step task, temporary data
  - Use case: Storing search results while deciding what to research next
  - Lifetime: Duration of current task only
  - Storage: Agent's state dictionary

**When to use each memory type:**
| Memory Type | Use When... |
|-------------|-------------|
| Short-term | Following multi-turn conversation context |
| Long-term | Need to remember facts across sessions |
| Episodic | Learning from past task attempts |
| Working | Tracking state during complex multi-step tasks |

**Memory Implementation:**

<details>
<summary><b>Python</b></summary>

```python
from dataclasses import dataclass, field
from typing import List, Dict, Any
from datetime import datetime
import json

@dataclass
class MemoryEntry:
    content: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

class AgentMemory:
    """Manages different types of agent memory."""

    def __init__(self, max_short_term: int = 50):
        self.short_term: List[MemoryEntry] = []
        self.long_term: List[MemoryEntry] = []  # Would be DB in production
        self.working: Dict[str, Any] = {}
        self.max_short_term = max_short_term

    def add_short_term(self, content: str, metadata: Dict = None):
        """Add to short-term memory with automatic pruning."""
        entry = MemoryEntry(
            content=content,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        self.short_term.append(entry)

        # Prune if too long
        if len(self.short_term) > self.max_short_term:
            # Summarize and move to long-term
            self._consolidate_short_term()

    def add_long_term(self, content: str, metadata: Dict = None):
        """Add directly to long-term memory."""
        entry = MemoryEntry(
            content=content,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        self.long_term.append(entry)

    def get_relevant(self, query: str, k: int = 5) -> List[str]:
        """Retrieve relevant memories (simplified - would use embeddings)."""
        # In production, use vector similarity
        all_memories = self.short_term + self.long_term
        # Simple keyword matching for demo
        relevant = [m for m in all_memories if any(
            word.lower() in m.content.lower()
            for word in query.split()
        )]
        return [m.content for m in relevant[:k]]

    def set_working(self, key: str, value: Any):
        """Set working memory value."""
        self.working[key] = value

    def get_working(self, key: str, default: Any = None) -> Any:
        """Get working memory value."""
        return self.working.get(key, default)

    def _consolidate_short_term(self):
        """Summarize old short-term memories and move to long-term."""
        # Keep last N entries
        keep = self.short_term[-10:]
        to_summarize = self.short_term[:-10]

        if to_summarize:
            # In production, use LLM to summarize
            summary = f"Summary of {len(to_summarize)} interactions"
            self.add_long_term(summary, {"type": "summary"})

        self.short_term = keep
```

</details>

<details>
<summary><b>TypeScript</b></summary>

```typescript
interface MemoryEntry {
  content: string;
  timestamp: Date;
  metadata: Record<string, any>;
}

class AgentMemory {
  private shortTerm: MemoryEntry[] = [];
  private longTerm: MemoryEntry[] = []; // Would be DB in production
  private working: Map<string, any> = new Map();

  constructor(private maxShortTerm: number = 50) {}

  addShortTerm(content: string, metadata: Record<string, any> = {}): void {
    const entry: MemoryEntry = {
      content,
      timestamp: new Date(),
      metadata,
    };
    this.shortTerm.push(entry);

    // Prune if too long
    if (this.shortTerm.length > this.maxShortTerm) {
      this.consolidateShortTerm();
    }
  }

  addLongTerm(content: string, metadata: Record<string, any> = {}): void {
    const entry: MemoryEntry = {
      content,
      timestamp: new Date(),
      metadata,
    };
    this.longTerm.push(entry);
  }

  getRelevant(query: string, k: number = 5): string[] {
    // In production, use vector similarity
    const allMemories = [...this.shortTerm, ...this.longTerm];
    const queryWords = query.toLowerCase().split(/\s+/);

    // Simple keyword matching for demo
    const relevant = allMemories.filter((m) =>
      queryWords.some((word) => m.content.toLowerCase().includes(word))
    );

    return relevant.slice(0, k).map((m) => m.content);
  }

  setWorking(key: string, value: any): void {
    this.working.set(key, value);
  }

  getWorking<T>(key: string, defaultValue?: T): T | undefined {
    return this.working.has(key) ? this.working.get(key) : defaultValue;
  }

  private consolidateShortTerm(): void {
    // Keep last N entries
    const keep = this.shortTerm.slice(-10);
    const toSummarize = this.shortTerm.slice(0, -10);

    if (toSummarize.length > 0) {
      // In production, use LLM to summarize
      const summary = `Summary of ${toSummarize.length} interactions`;
      this.addLongTerm(summary, { type: 'summary' });
    }

    this.shortTerm = keep;
  }
}
```

</details>

### 1.4 State Management

<details>
<summary><b>Python</b></summary>

```python
from enum import Enum
from typing import Optional
from dataclasses import dataclass, field

class AgentStatus(Enum):
    IDLE = "idle"
    THINKING = "thinking"
    EXECUTING = "executing"
    WAITING = "waiting"  # Waiting for external input
    COMPLETE = "complete"
    ERROR = "error"

@dataclass
class TaskState:
    """State for a single task."""
    task_id: str
    description: str
    status: AgentStatus = AgentStatus.IDLE
    steps_completed: List[str] = field(default_factory=list)
    current_step: Optional[str] = None
    result: Optional[Any] = None
    error: Optional[str] = None

@dataclass
class AgentContext:
    """Full agent context."""
    current_task: Optional[TaskState] = None
    task_history: List[TaskState] = field(default_factory=list)
    memory: AgentMemory = field(default_factory=AgentMemory)

    def start_task(self, task_id: str, description: str):
        """Start a new task."""
        self.current_task = TaskState(
            task_id=task_id,
            description=description,
            status=AgentStatus.THINKING
        )

    def complete_step(self, step: str):
        """Mark a step as complete."""
        if self.current_task:
            self.current_task.steps_completed.append(step)

    def finish_task(self, result: Any = None, error: str = None):
        """Finish the current task."""
        if self.current_task:
            if error:
                self.current_task.status = AgentStatus.ERROR
                self.current_task.error = error
            else:
                self.current_task.status = AgentStatus.COMPLETE
                self.current_task.result = result

            self.task_history.append(self.current_task)
            self.current_task = None
```

</details>

<details>
<summary><b>TypeScript</b></summary>

```typescript
type AgentStatus = 'idle' | 'thinking' | 'executing' | 'waiting' | 'complete' | 'error';

interface TaskState {
  taskId: string;
  description: string;
  status: AgentStatus;
  stepsCompleted: string[];
  currentStep?: string;
  result?: any;
  error?: string;
}

interface AgentContext {
  currentTask: TaskState | null;
  taskHistory: TaskState[];
  memory: AgentMemory;
}

// Immutable state updates (functional approach)
function createContext(): AgentContext {
  return {
    currentTask: null,
    taskHistory: [],
    memory: new AgentMemory(),
  };
}

function startTask(context: AgentContext, taskId: string, description: string): AgentContext {
  return {
    ...context,
    currentTask: {
      taskId,
      description,
      status: 'thinking',
      stepsCompleted: [],
    },
  };
}

function completeStep(context: AgentContext, step: string): AgentContext {
  if (!context.currentTask) return context;

  return {
    ...context,
    currentTask: {
      ...context.currentTask,
      stepsCompleted: [...context.currentTask.stepsCompleted, step],
    },
  };
}

function finishTask(
  context: AgentContext,
  result?: any,
  error?: string
): AgentContext {
  if (!context.currentTask) return context;

  const finishedTask: TaskState = {
    ...context.currentTask,
    status: error ? 'error' : 'complete',
    result,
    error,
  };

  return {
    ...context,
    currentTask: null,
    taskHistory: [...context.taskHistory, finishedTask],
  };
}
```

</details>

### 1.4 Context Management Strategies (30 min)

As conversations grow, managing context becomes critical. The LLM's context window is finite, and costs scale with context size.

```
┌─────────────────────────────────────────────────────────────────┐
│                  Context Management Strategies                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  CHALLENGE: Context Window Limitations                          │
│  • Claude: 200K tokens (~150K words)                            │
│  • GPT-4: 128K tokens (~96K words)                              │
│  • Costs increase linearly with context                         │
│  • Performance degrades with very long contexts                 │
│                                                                 │
│  STRATEGIES:                                                    │
│                                                                 │
│  1. SLIDING WINDOW                                              │
│     Keep recent N messages, drop oldest                         │
│     ┌─────┬─────┬─────┬─────┬─────┐                            │
│     │ M1  │ M2  │ M3  │ M4  │ M5  │ → Keep last 3              │
│     └─────┴─────┴─────┴─────┴─────┘                            │
│                   ↓     ↓     ↓                                 │
│                 ┌─────┬─────┬─────┐                            │
│                 │ M3  │ M4  │ M5  │                            │
│                 └─────┴─────┴─────┘                            │
│                                                                 │
│  2. ROLLING SUMMARIZATION                                       │
│     Periodically summarize and compress history                 │
│     ┌─────┬─────┬─────┬─────┐                                  │
│     │ M1  │ M2  │ M3  │ M4  │ → Summarize M1-M3               │
│     └─────┴─────┴─────┴─────┘                                  │
│           ↓                                                     │
│     ┌───────────┬─────┐                                        │
│     │  Summary  │ M4  │                                        │
│     └───────────┴─────┘                                        │
│                                                                 │
│  3. SELECTIVE RETENTION                                         │
│     Keep important messages, drop routine ones                  │
│     • Always keep: System prompt, user goals                    │
│     • Sometimes keep: Key decisions, errors                     │
│     • Usually drop: Routine confirmations                       │
│                                                                 │
│  4. EXTERNAL MEMORY                                             │
│     Store in vector DB, retrieve when needed                    │
│     ┌─────────────┐         ┌──────────────┐                   │
│     │   Context   │────────▶│  Vector DB   │                   │
│     │   Window    │◀────────│  (All History)│                   │
│     └─────────────┘ Retrieve└──────────────┘                   │
│                      Relevant                                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Strategy 1: Sliding Window Implementation**

<details>
<summary><b>Python</b></summary>

```python
# agents/context_manager.py
"""Context management strategies for agents."""
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class ContextWindow:
    """Manages a sliding window of messages."""
    messages: List[Dict[str, str]]
    max_messages: int
    system_prompt: str

    def add_message(self, role: str, content: str) -> None:
        """Add message and maintain window size."""
        self.messages.append({"role": role, "content": content})

        # Keep system prompt + last N messages
        if len(self.messages) > self.max_messages + 1:  # +1 for system
            # Keep system prompt and drop oldest user/assistant messages
            system_msg = self.messages[0]
            recent_messages = self.messages[-(self.max_messages):]
            self.messages = [system_msg] + recent_messages

    def get_messages(self) -> List[Dict[str, str]]:
        """Get current message window."""
        return self.messages

    def get_context_size(self) -> int:
        """Estimate token count (rough)."""
        total_chars = sum(len(m["content"]) for m in self.messages)
        return total_chars // 4  # Rough token estimate

# Usage
context = ContextWindow(
    messages=[{"role": "system", "content": "You are a helpful assistant."}],
    max_messages=10,
    system_prompt="You are a helpful assistant."
)

context.add_message("user", "What's 2+2?")
context.add_message("assistant", "2+2 equals 4.")
# ... continues with sliding window behavior
```

</details>

<details>
<summary><b>TypeScript</b></summary>

```typescript
// agents/context-manager.ts
/**
 * Context management strategies for agents.
 */

interface Message {
  role: string;
  content: string;
}

export class ContextWindow {
  private messages: Message[];

  constructor(
    private systemPrompt: string,
    private maxMessages: number
  ) {
    this.messages = [{ role: 'system', content: systemPrompt }];
  }

  addMessage(role: string, content: string): void {
    this.messages.push({ role, content });

    // Keep system prompt + last N messages
    if (this.messages.length > this.maxMessages + 1) {
      const systemMsg = this.messages[0];
      const recentMessages = this.messages.slice(-(this.maxMessages));
      this.messages = [systemMsg, ...recentMessages];
    }
  }

  getMessages(): Message[] {
    return [...this.messages];
  }

  getContextSize(): number {
    const totalChars = this.messages.reduce(
      (sum, m) => sum + m.content.length,
      0
    );
    return Math.floor(totalChars / 4); // Rough token estimate
  }
}

// Usage
const context = new ContextWindow(
  'You are a helpful assistant.',
  10
);

context.addMessage('user', "What's 2+2?");
context.addMessage('assistant', '2+2 equals 4.');
```

</details>

**Strategy 2: Rolling Summarization**

<details>
<summary><b>Python</b></summary>

```python
# agents/summarizing_context.py
"""Context manager with automatic summarization."""
from typing import List, Dict
import anthropic

class SummarizingContext:
    """Manages context with periodic summarization."""

    def __init__(
        self,
        llm_client,
        system_prompt: str,
        summarize_every: int = 10,
        keep_recent: int = 3
    ):
        self.llm = llm_client
        self.system_prompt = system_prompt
        self.messages = [{"role": "system", "content": system_prompt}]
        self.summary = ""
        self.summarize_every = summarize_every
        self.keep_recent = keep_recent
        self.message_count = 0

    def add_message(self, role: str, content: str) -> None:
        """Add message and summarize if needed."""
        self.messages.append({"role": role, "content": content})
        self.message_count += 1

        # Check if we need to summarize
        if self.message_count >= self.summarize_every:
            self._summarize_and_compress()

    def _summarize_and_compress(self) -> None:
        """Summarize old messages and keep recent ones."""
        # Separate messages to summarize from recent messages
        to_summarize = self.messages[1:-self.keep_recent]  # Skip system
        recent = self.messages[-self.keep_recent:]

        if not to_summarize:
            return

        # Create summarization prompt
        conversation = "\n".join([
            f"{m['role']}: {m['content']}"
            for m in to_summarize
        ])

        summary_prompt = f"""
        Summarize this conversation concisely. Focus on:
        1. Key information exchanged
        2. Decisions made
        3. Important context for future messages

        Previous summary: {self.summary if self.summary else "None"}

        New conversation:
        {conversation}

        Provide a concise summary (3-5 sentences):
        """

        # Get summary from LLM
        response = self.llm.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=300,
            messages=[{"role": "user", "content": summary_prompt}]
        )

        self.summary = response.content[0].text

        # Rebuild message list with summary
        self.messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "system", "content": f"Summary of previous conversation: {self.summary}"}
        ] + recent

        self.message_count = 0

    def get_messages(self) -> List[Dict[str, str]]:
        """Get current messages including summary."""
        return self.messages
```

</details>

**Strategy 3: Selective Retention**

```python
# agents/selective_context.py
"""Selective retention of important messages."""
from typing import List, Dict, Callable

class SelectiveContext:
    """Keeps messages based on importance scoring."""

    def __init__(
        self,
        system_prompt: str,
        max_messages: int,
        importance_fn: Callable[[Dict[str, str]], float]
    ):
        self.system_prompt = system_prompt
        self.messages = [{"role": "system", "content": system_prompt}]
        self.max_messages = max_messages
        self.importance_fn = importance_fn

    def add_message(self, role: str, content: str) -> None:
        """Add message with importance scoring."""
        msg = {"role": role, "content": content}
        importance = self.importance_fn(msg)
        msg["_importance"] = importance

        self.messages.append(msg)

        # If over limit, drop least important
        if len(self.messages) > self.max_messages + 1:
            # Sort by importance (keep system prompt)
            system = self.messages[0]
            user_msgs = sorted(
                self.messages[1:],
                key=lambda m: m.get("_importance", 0),
                reverse=True
            )
            self.messages = [system] + user_msgs[:self.max_messages]

    def get_messages(self) -> List[Dict[str, str]]:
        """Get messages without importance scores."""
        return [
            {k: v for k, v in m.items() if not k.startswith("_")}
            for m in self.messages
        ]

# Example importance function
def importance_scorer(message: Dict[str, str]) -> float:
    """Score message importance (0-1)."""
    content = message["content"].lower()
    score = 0.5  # baseline

    # High importance indicators
    if any(word in content for word in ["error", "fail", "bug", "issue"]):
        score += 0.3
    if any(word in content for word in ["decision", "requirement", "must"]):
        score += 0.2
    if "?" in content:  # Questions are important
        score += 0.1

    # Low importance indicators
    if any(word in content for word in ["ok", "thanks", "got it"]):
        score -= 0.2

    return min(1.0, max(0.0, score))

# Usage
context = SelectiveContext(
    system_prompt="You are a helpful assistant.",
    max_messages=10,
    importance_fn=importance_scorer
)
```

**When to Use Each Strategy:**

| Strategy | Best For | Pros | Cons |
|----------|----------|------|------|
| **Sliding Window** | Short tasks, uniform importance | Simple, predictable | Loses old context completely |
| **Summarization** | Long conversations | Preserves key info | Summary may miss details |
| **Selective** | Mixed-importance messages | Keeps what matters | Requires good scoring function |
| **External Memory** | Very long-term context | Unlimited history | Adds retrieval latency |

**Context Management Best Practices:**

1. **Always preserve system prompt** - Never drop it from context
2. **Monitor token usage** - Log context size and costs
3. **Test with long conversations** - Verify behavior at limits
4. **Combine strategies** - Use summarization + selective retention
5. **Make it configurable** - Different tasks need different strategies

### 1.5 Memory Systems Implementation (30 min)

Building on the memory types from section 1.3, here we implement practical memory systems.

**Long-Term Memory with Vector Storage:**

<details>
<summary><b>Python</b></summary>

```python
# agents/long_term_memory.py
"""Long-term memory implementation using vector storage."""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import chromadb
from chromadb.config import Settings

@dataclass
class MemoryEntry:
    """A single memory entry."""
    content: str
    metadata: Dict[str, Any]
    timestamp: datetime
    embedding: Optional[List[float]] = None

class LongTermMemory:
    """Persistent memory using ChromaDB."""

    def __init__(
        self,
        collection_name: str,
        embedding_function
    ):
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory="./.chroma"
        ))
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=embedding_function
        )

    def store(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Store a memory."""
        memory_id = f"mem_{datetime.now().timestamp()}"

        self.collection.add(
            ids=[memory_id],
            documents=[content],
            metadatas=[metadata or {}]
        )

        return memory_id

    def recall(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Recall relevant memories."""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=filter_metadata
        )

        memories = []
        for i in range(len(results['ids'][0])):
            memories.append({
                'id': results['ids'][0][i],
                'content': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i]
            })

        return memories

    def forget(self, memory_id: str) -> None:
        """Delete a memory."""
        self.collection.delete(ids=[memory_id])

# Usage example
from chromadb.utils import embedding_functions

embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

memory = LongTermMemory(
    collection_name="agent_memories",
    embedding_function=embedding_fn
)

# Store memories
memory.store(
    "User prefers Python over JavaScript",
    metadata={"type": "preference", "user": "john"}
)

memory.store(
    "Successfully migrated authentication to OAuth2",
    metadata={"type": "task_completion", "date": "2024-01-15"}
)

# Recall relevant memories
relevant = memory.recall(
    query="What language does the user prefer?",
    n_results=3
)

for mem in relevant:
    print(f"Memory: {mem['content']}")
    print(f"Relevance: {1 - mem['distance']:.2f}")
```

</details>

**Episodic Memory (Task History):**

<details>
<summary><b>Python</b></summary>

```python
# agents/episodic_memory.py
"""Episodic memory for tracking task completions."""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import json

@dataclass
class Episode:
    """A completed task episode."""
    task: str
    outcome: str  # "success" or "failure"
    steps_taken: List[str]
    tools_used: List[str]
    duration_seconds: float
    errors_encountered: List[str]
    timestamp: datetime
    learning: Optional[str] = None  # What was learned

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for storage."""
        d = asdict(self)
        d['timestamp'] = self.timestamp.isoformat()
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Episode':
        """Load from dict."""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)

class EpisodicMemory:
    """Manages episodic memory of task completions."""

    def __init__(self, storage_path: str = "./episodes.json"):
        self.storage_path = storage_path
        self.episodes: List[Episode] = []
        self._load()

    def record_episode(self, episode: Episode) -> None:
        """Record a completed task episode."""
        self.episodes.append(episode)
        self._save()

    def find_similar_tasks(
        self,
        task_description: str,
        limit: int = 5
    ) -> List[Episode]:
        """Find similar past tasks."""
        # Simple keyword matching (in production, use embeddings)
        keywords = set(task_description.lower().split())

        scored_episodes = []
        for episode in self.episodes:
            episode_keywords = set(episode.task.lower().split())
            similarity = len(keywords & episode_keywords) / len(keywords | episode_keywords)
            scored_episodes.append((similarity, episode))

        scored_episodes.sort(reverse=True, key=lambda x: x[0])
        return [ep for _, ep in scored_episodes[:limit]]

    def get_success_rate(self, task_type: Optional[str] = None) -> float:
        """Calculate success rate for task type."""
        relevant_episodes = self.episodes

        if task_type:
            relevant_episodes = [
                ep for ep in self.episodes
                if task_type.lower() in ep.task.lower()
            ]

        if not relevant_episodes:
            return 0.0

        successes = sum(1 for ep in relevant_episodes if ep.outcome == "success")
        return successes / len(relevant_episodes)

    def get_learnings(self, task_type: Optional[str] = None) -> List[str]:
        """Extract learnings from past episodes."""
        relevant_episodes = self.episodes

        if task_type:
            relevant_episodes = [
                ep for ep in self.episodes
                if task_type.lower() in ep.task.lower()
            ]

        return [
            ep.learning
            for ep in relevant_episodes
            if ep.learning
        ]

    def _save(self) -> None:
        """Persist episodes to disk."""
        with open(self.storage_path, 'w') as f:
            json.dump(
                [ep.to_dict() for ep in self.episodes],
                f,
                indent=2
            )

    def _load(self) -> None:
        """Load episodes from disk."""
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                self.episodes = [Episode.from_dict(ep) for ep in data]
        except FileNotFoundError:
            self.episodes = []

# Usage in an agent
episodic_memory = EpisodicMemory()

# Before starting a task, check history
similar_tasks = episodic_memory.find_similar_tasks(
    "Migrate Express.js API to FastAPI"
)

if similar_tasks:
    print(f"Found {len(similar_tasks)} similar past tasks")
    for task in similar_tasks:
        print(f"  - {task.task}: {task.outcome}")
        if task.learning:
            print(f"    Learning: {task.learning}")

# After completing a task
episode = Episode(
    task="Migrate Express.js API to FastAPI",
    outcome="success",
    steps_taken=[
        "Analyzed Express routes",
        "Created FastAPI equivalents",
        "Migrated authentication middleware",
        "Updated tests"
    ],
    tools_used=["code_analyzer", "test_runner"],
    duration_seconds=1847.5,
    errors_encountered=["Authentication middleware initially failed"],
    timestamp=datetime.now(),
    learning="FastAPI's Depends() is cleaner than Express middleware chains"
)

episodic_memory.record_episode(episode)
```

</details>

**Complete Memory System Integration:**

```python
# agents/memory_agent.py
"""Agent with comprehensive memory system."""
from typing import List, Dict, Any
from .long_term_memory import LongTermMemory
from .episodic_memory import EpisodicMemory, Episode
from .context_manager import SummarizingContext
from datetime import datetime

class MemoryEnhancedAgent:
    """Agent with short-term, long-term, and episodic memory."""

    def __init__(
        self,
        llm_client,
        system_prompt: str,
        long_term_memory: LongTermMemory,
        episodic_memory: EpisodicMemory
    ):
        self.llm = llm_client
        self.short_term = SummarizingContext(
            llm_client=llm_client,
            system_prompt=system_prompt,
            summarize_every=10,
            keep_recent=3
        )
        self.long_term = long_term_memory
        self.episodic = episodic_memory
        self.current_task_start = None
        self.current_task_steps = []

    async def process(self, user_input: str) -> str:
        """Process input with full memory context."""
        # 1. Recall relevant long-term memories
        relevant_memories = self.long_term.recall(user_input, n_results=3)
        memory_context = "\n".join([
            f"- {m['content']}"
            for m in relevant_memories
        ])

        # 2. Recall similar past tasks
        similar_tasks = self.episodic.find_similar_tasks(user_input, limit=2)
        task_context = ""
        if similar_tasks:
            task_context = "\n".join([
                f"- Previous: {t.task} → {t.outcome}"
                + (f" (Learning: {t.learning})" if t.learning else "")
                for t in similar_tasks
            ])

        # 3. Build enhanced prompt with memory context
        enhanced_prompt = f"""
        Relevant memories:
        {memory_context if memory_context else "None"}

        Similar past tasks:
        {task_context if task_context else "None"}

        Current request:
        {user_input}
        """

        # 4. Add to short-term memory and process
        self.short_term.add_message("user", enhanced_prompt)

        response = await self.llm.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            messages=self.short_term.get_messages()
        )

        response_text = response.content[0].text
        self.short_term.add_message("assistant", response_text)

        # 5. Store important information in long-term memory
        if self._is_important(user_input):
            self.long_term.store(
                f"User said: {user_input}",
                metadata={"type": "user_input", "timestamp": datetime.now().isoformat()}
            )

        return response_text

    def start_task(self, task_description: str) -> None:
        """Mark the start of a task for episodic memory."""
        self.current_task_start = datetime.now()
        self.current_task_steps = []

    def record_step(self, step_description: str) -> None:
        """Record a step in the current task."""
        self.current_task_steps.append(step_description)

    def complete_task(
        self,
        outcome: str,
        learning: Optional[str] = None
    ) -> None:
        """Record task completion in episodic memory."""
        if not self.current_task_start:
            return

        duration = (datetime.now() - self.current_task_start).total_seconds()

        episode = Episode(
            task=self.current_task_steps[0] if self.current_task_steps else "Unknown task",
            outcome=outcome,
            steps_taken=self.current_task_steps,
            tools_used=[],  # Track from actual tool usage
            duration_seconds=duration,
            errors_encountered=[],  # Track from actual errors
            timestamp=datetime.now(),
            learning=learning
        )

        self.episodic.record_episode(episode)

        # Reset task tracking
        self.current_task_start = None
        self.current_task_steps = []

    def _is_important(self, text: str) -> bool:
        """Determine if information should be stored long-term."""
        important_keywords = [
            "prefer", "always", "never", "remember",
            "important", "critical", "requirement"
        ]
        return any(keyword in text.lower() for keyword in important_keywords)
```

**Memory System Summary:**

| Memory Type | Storage | Retrieval | Use Case |
|-------------|---------|-----------|----------|
| **Short-term** | Context window | Automatic | Current conversation |
| **Long-term** | Vector DB | Semantic search | User preferences, facts |
| **Episodic** | JSON/Database | Similarity matching | Learning from past tasks |
| **Working** | Agent state | Direct access | Current task execution |

---

<a name="tool-use"></a>
## 2. Tool-Use & Function Calling (1 hour)

### 2.1 What is Function Calling?

Function calling lets LLMs request execution of predefined functions with structured arguments.

```
┌─────────────────────────────────────────────────────────────────┐
│                    Function Calling Flow                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Define tools → 2. Send to LLM → 3. LLM decides → 4. Execute │
│                                                                 │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐        │
│  │   Tools     │     │    LLM      │     │  Your Code  │        │
│  │ Definition  │────▶│  Decides    │────▶│  Executes   │        │
│  │             │     │  Which Tool │     │  The Tool   │        │
│  └─────────────┘     └─────────────┘     └─────────────┘        │
│                                                 │               │
│                                                 │               │
│  ┌─────────────┐     ┌─────────────┐            │               │
│  │   Final     │◀────│  LLM Uses   │◀───────────┘               │
│  │  Response   │     │   Result    │                            │
│  └─────────────┘     └─────────────┘                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Tool Definition Best Practices

**Good Tool Definition:**

<details>
<summary><b>Python</b></summary>

```python
# tools/file_tools.py
from typing import List, Optional

def read_file_tool():
    """Definition for a file reading tool."""
    return {
        "name": "read_file",
        "description": """Read the contents of a file at the given path.
Use this when you need to examine file contents.
Returns the full file content as a string.
Returns an error message if the file doesn't exist.""",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "The absolute or relative path to the file to read"
                },
                "encoding": {
                    "type": "string",
                    "description": "File encoding (default: utf-8)",
                    "default": "utf-8"
                }
            },
            "required": ["file_path"]
        }
    }

def list_directory_tool():
    """Definition for a directory listing tool."""
    return {
        "name": "list_directory",
        "description": """List files and directories in a given path.
Use this to explore directory structure.
Returns a list of file/directory names with their types.""",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Directory path to list (default: current directory)",
                    "default": "."
                },
                "include_hidden": {
                    "type": "boolean",
                    "description": "Include hidden files (starting with .)",
                    "default": False
                },
                "recursive": {
                    "type": "boolean",
                    "description": "List recursively",
                    "default": False
                }
            },
            "required": []
        }
    }
```

</details>

<details>
<summary><b>TypeScript</b></summary>

```typescript
// tools/file-tools.ts
import { z } from 'zod';

// Using Zod for type-safe tool definitions
const ReadFileSchema = z.object({
  file_path: z.string().describe('The absolute or relative path to the file to read'),
  encoding: z.string().default('utf-8').describe('File encoding (default: utf-8)'),
});

const ListDirectorySchema = z.object({
  path: z.string().default('.').describe('Directory path to list (default: current directory)'),
  include_hidden: z.boolean().default(false).describe('Include hidden files (starting with .)'),
  recursive: z.boolean().default(false).describe('List recursively'),
});

// Tool definition helper using Zod schema
function zodToJsonSchema(schema: z.ZodObject<any>): Record<string, any> {
  // Convert Zod schema to JSON Schema format
  const shape = schema.shape;
  const properties: Record<string, any> = {};
  const required: string[] = [];

  for (const [key, value] of Object.entries(shape)) {
    const zodValue = value as z.ZodTypeAny;
    properties[key] = {
      type: getZodType(zodValue),
      description: zodValue.description,
    };
    if (!zodValue.isOptional() && !hasDefault(zodValue)) {
      required.push(key);
    }
  }

  return { type: 'object', properties, required };
}

const readFileTool = {
  name: 'read_file',
  description: `Read the contents of a file at the given path.
Use this when you need to examine file contents.
Returns the full file content as a string.
Returns an error message if the file doesn't exist.`,
  parameters: zodToJsonSchema(ReadFileSchema),
};

const listDirectoryTool = {
  name: 'list_directory',
  description: `List files and directories in a given path.
Use this to explore directory structure.
Returns a list of file/directory names with their types.`,
  parameters: zodToJsonSchema(ListDirectorySchema),
};
```

</details>

**Tool Description Guidelines:**
| Do | Don't |
|----|-------|
| Explain when to use the tool | Be vague about purpose |
| Describe return values | Leave output unclear |
| Mention error conditions | Assume always succeeds |
| Use clear parameter names | Use ambiguous names |
| Provide sensible defaults | Require unnecessary params |

### 2.3 LLM-Agnostic Function Calling

Different providers have different formats. Here's a unified approach:

<details>
<summary><b>Python</b></summary>

```python
# utils/function_calling.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class ToolCall:
    """Standardized tool call representation."""
    id: str
    name: str
    arguments: Dict[str, Any]

@dataclass
class ToolResult:
    """Result from executing a tool."""
    tool_call_id: str
    result: str
    error: Optional[str] = None

class FunctionCallingClient(ABC):
    """Base class for function-calling enabled clients."""

    @abstractmethod
    def chat_with_tools(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]]
    ) -> tuple[str, List[ToolCall]]:
        """
        Send messages with tools available.
        Returns (content, tool_calls).
        """
        pass

class OpenAIFunctionCalling(FunctionCallingClient):
    def __init__(self, model: str = "gpt-4o"):
        from openai import OpenAI
        self.client = OpenAI()
        self.model = model

    def chat_with_tools(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]]
    ) -> tuple[str, List[ToolCall]]:
        # Convert to OpenAI format
        openai_tools = [
            {"type": "function", "function": tool}
            for tool in tools
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=openai_tools if openai_tools else None
        )

        message = response.choices[0].message

        # Extract tool calls
        tool_calls = []
        if message.tool_calls:
            for tc in message.tool_calls:
                tool_calls.append(ToolCall(
                    id=tc.id,
                    name=tc.function.name,
                    arguments=json.loads(tc.function.arguments)
                ))

        return message.content or "", tool_calls

class AnthropicFunctionCalling(FunctionCallingClient):
    def __init__(self, model: str = "claude-3-5-sonnet-20241022"):
        from anthropic import Anthropic
        self.client = Anthropic()
        self.model = model

    def chat_with_tools(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]]
    ) -> tuple[str, List[ToolCall]]:
        # Convert to Anthropic format
        anthropic_tools = [
            {
                "name": tool["name"],
                "description": tool["description"],
                "input_schema": tool["parameters"]
            }
            for tool in tools
        ]

        # Extract system message
        system = None
        filtered_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system = msg["content"]
            else:
                filtered_messages.append(msg)

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system,
            messages=filtered_messages,
            tools=anthropic_tools if anthropic_tools else None
        )

        # Parse response
        content = ""
        tool_calls = []

        for block in response.content:
            if block.type == "text":
                content += block.text
            elif block.type == "tool_use":
                tool_calls.append(ToolCall(
                    id=block.id,
                    name=block.name,
                    arguments=block.input
                ))

        return content, tool_calls
```

</details>

<details>
<summary><b>TypeScript</b></summary>

```typescript
// utils/function-calling.ts
interface ToolCall {
  id: string;
  name: string;
  arguments: Record<string, any>;
}

interface ToolResult {
  toolCallId: string;
  result: string;
  error?: string;
}

interface ToolDefinition {
  name: string;
  description: string;
  parameters: Record<string, any>;
}

interface ChatWithToolsResponse {
  content: string;
  toolCalls: ToolCall[];
}

abstract class FunctionCallingClient {
  abstract chatWithTools(
    messages: Array<{ role: string; content: string }>,
    tools: ToolDefinition[]
  ): Promise<ChatWithToolsResponse>;
}

class OpenAIFunctionCalling extends FunctionCallingClient {
  private client: InstanceType<typeof import('openai').default> | null = null;

  constructor(private model: string = 'gpt-4o') {
    super();
  }

  private async ensureClient() {
    if (!this.client) {
      const OpenAI = (await import('openai')).default;
      this.client = new OpenAI();
    }
  }

  async chatWithTools(
    messages: Array<{ role: string; content: string }>,
    tools: ToolDefinition[]
  ): Promise<ChatWithToolsResponse> {
    await this.ensureClient();

    const openaiTools = tools.map((tool) => ({
      type: 'function' as const,
      function: tool,
    }));

    const response = await this.client!.chat.completions.create({
      model: this.model,
      messages: messages as any,
      tools: openaiTools.length > 0 ? openaiTools : undefined,
    });

    const message = response.choices[0].message;
    const toolCalls: ToolCall[] = (message.tool_calls || []).map((tc) => ({
      id: tc.id,
      name: tc.function.name,
      arguments: JSON.parse(tc.function.arguments),
    }));

    return { content: message.content || '', toolCalls };
  }
}

class AnthropicFunctionCalling extends FunctionCallingClient {
  private client: InstanceType<typeof import('@anthropic-ai/sdk').default> | null = null;

  constructor(private model: string = 'claude-3-5-sonnet-20241022') {
    super();
  }

  private async ensureClient() {
    if (!this.client) {
      const Anthropic = (await import('@anthropic-ai/sdk')).default;
      this.client = new Anthropic();
    }
  }

  async chatWithTools(
    messages: Array<{ role: string; content: string }>,
    tools: ToolDefinition[]
  ): Promise<ChatWithToolsResponse> {
    await this.ensureClient();

    const anthropicTools = tools.map((tool) => ({
      name: tool.name,
      description: tool.description,
      input_schema: tool.parameters,
    }));

    // Extract system message
    let system: string | undefined;
    const filtered = messages.filter((msg) => {
      if (msg.role === 'system') {
        system = msg.content;
        return false;
      }
      return true;
    });

    const response = await this.client!.messages.create({
      model: this.model,
      max_tokens: 4096,
      system,
      messages: filtered as any,
      tools: anthropicTools.length > 0 ? anthropicTools : undefined,
    });

    let content = '';
    const toolCalls: ToolCall[] = [];

    for (const block of response.content) {
      if (block.type === 'text') {
        content += block.text;
      } else if (block.type === 'tool_use') {
        toolCalls.push({
          id: block.id,
          name: block.name,
          arguments: block.input as Record<string, any>,
        });
      }
    }

    return { content, toolCalls };
  }
}
```

</details>

### 2.4 Error Handling and Retries

<details>
<summary><b>Python</b></summary>

```python
# tools/executor.py
from typing import Dict, Any, Callable, Optional
import traceback
import time

class ToolExecutor:
    """Executes tools with error handling and retries."""

    def __init__(
        self,
        tools: Dict[str, Callable],
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        self.tools = tools
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def execute(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> ToolResult:
        """Execute a tool with retries and error handling."""

        if tool_name not in self.tools:
            return ToolResult(
                tool_call_id="",
                result="",
                error=f"Unknown tool: {tool_name}"
            )

        tool_func = self.tools[tool_name]
        last_error = None

        for attempt in range(self.max_retries):
            try:
                result = tool_func(**arguments)
                return ToolResult(
                    tool_call_id="",
                    result=str(result)
                )
            except Exception as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))  # Exponential backoff

        # All retries failed
        return ToolResult(
            tool_call_id="",
            result="",
            error=f"Tool execution failed after {self.max_retries} attempts: {str(last_error)}\n{traceback.format_exc()}"
        )

    def execute_with_timeout(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        timeout: float = 30.0
    ) -> ToolResult:
        """Execute with timeout (using threading)."""
        import threading
        from queue import Queue

        result_queue = Queue()

        def run():
            result = self.execute(tool_name, arguments)
            result_queue.put(result)

        thread = threading.Thread(target=run)
        thread.start()
        thread.join(timeout=timeout)

        if thread.is_alive():
            return ToolResult(
                tool_call_id="",
                result="",
                error=f"Tool execution timed out after {timeout}s"
            )

        return result_queue.get()
```

</details>

<details>
<summary><b>TypeScript</b></summary>

```typescript
// tools/executor.ts
type ToolFunction = (args: Record<string, any>) => Promise<string> | string;

interface ToolResult {
  toolCallId: string;
  result: string;
  error?: string;
}

class ToolExecutor {
  constructor(
    private tools: Map<string, ToolFunction>,
    private maxRetries: number = 3,
    private retryDelay: number = 1000
  ) {}

  async execute(toolName: string, arguments_: Record<string, any>): Promise<ToolResult> {
    const tool = this.tools.get(toolName);

    if (!tool) {
      return {
        toolCallId: '',
        result: '',
        error: `Unknown tool: ${toolName}`,
      };
    }

    let lastError: Error | null = null;

    for (let attempt = 0; attempt < this.maxRetries; attempt++) {
      try {
        const result = await tool(arguments_);
        return {
          toolCallId: '',
          result: String(result),
        };
      } catch (e) {
        lastError = e as Error;
        if (attempt < this.maxRetries - 1) {
          // Exponential backoff
          await this.sleep(this.retryDelay * (attempt + 1));
        }
      }
    }

    // All retries failed
    return {
      toolCallId: '',
      result: '',
      error: `Tool execution failed after ${this.maxRetries} attempts: ${lastError?.message}\n${lastError?.stack}`,
    };
  }

  async executeWithTimeout(
    toolName: string,
    arguments_: Record<string, any>,
    timeout: number = 30000
  ): Promise<ToolResult> {
    const timeoutPromise = new Promise<ToolResult>((_, reject) =>
      setTimeout(() => reject(new Error('Timeout')), timeout)
    );

    try {
      return await Promise.race([this.execute(toolName, arguments_), timeoutPromise]);
    } catch (e) {
      if ((e as Error).message === 'Timeout') {
        return {
          toolCallId: '',
          result: '',
          error: `Tool execution timed out after ${timeout}ms`,
        };
      }
      throw e;
    }
  }

  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}
```

</details>

### 2.5 Live Demo: File System Agent

<details>
<summary><b>Python</b></summary>

```python
# demos/file_agent.py
"""Demo: Simple file system agent."""
import os
from pathlib import Path

# Tool implementations
def read_file(file_path: str, encoding: str = "utf-8") -> str:
    """Read file contents."""
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File not found: {file_path}"
    except Exception as e:
        return f"Error reading file: {e}"

def list_directory(
    path: str = ".",
    include_hidden: bool = False,
    recursive: bool = False
) -> str:
    """List directory contents."""
    try:
        p = Path(path)
        if not p.exists():
            return f"Error: Path not found: {path}"

        if recursive:
            items = list(p.rglob("*"))
        else:
            items = list(p.iterdir())

        if not include_hidden:
            items = [i for i in items if not i.name.startswith('.')]

        result = []
        for item in sorted(items):
            item_type = "DIR" if item.is_dir() else "FILE"
            result.append(f"[{item_type}] {item}")

        return "\n".join(result) if result else "Directory is empty"
    except Exception as e:
        return f"Error listing directory: {e}"

def write_file(file_path: str, content: str) -> str:
    """Write content to file."""
    try:
        with open(file_path, 'w') as f:
            f.write(content)
        return f"Successfully wrote {len(content)} characters to {file_path}"
    except Exception as e:
        return f"Error writing file: {e}"

# Tool definitions
TOOLS = [
    {
        "name": "read_file",
        "description": "Read the contents of a file",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path to the file"},
                "encoding": {"type": "string", "default": "utf-8"}
            },
            "required": ["file_path"]
        }
    },
    {
        "name": "list_directory",
        "description": "List contents of a directory",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "default": "."},
                "include_hidden": {"type": "boolean", "default": False},
                "recursive": {"type": "boolean", "default": False}
            },
            "required": []
        }
    },
    {
        "name": "write_file",
        "description": "Write content to a file",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string"},
                "content": {"type": "string"}
            },
            "required": ["file_path", "content"]
        }
    }
]

TOOL_MAP = {
    "read_file": read_file,
    "list_directory": list_directory,
    "write_file": write_file
}

# Agent system prompt
FILE_AGENT_SYSTEM = """You are a file system assistant. You help users explore and manage files.

Available tools:
- read_file: Read contents of a file
- list_directory: List contents of a directory
- write_file: Write content to a file

Guidelines:
1. Always confirm before writing/modifying files
2. Summarize file contents rather than dumping raw text
3. Be careful with recursive operations on large directories
4. Report errors clearly

When exploring code, provide insights about what you find."""

def run_file_agent():
    """Run the file agent interactively."""
    from utils.function_calling import AnthropicFunctionCalling

    client = AnthropicFunctionCalling()
    messages = [{"role": "system", "content": FILE_AGENT_SYSTEM}]

    print("File System Agent Ready. Type 'quit' to exit.")
    print("-" * 50)

    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() == 'quit':
            break

        messages.append({"role": "user", "content": user_input})

        # Agent loop
        while True:
            content, tool_calls = client.chat_with_tools(messages, TOOLS)

            if content:
                print(f"\nAgent: {content}")

            if not tool_calls:
                messages.append({"role": "assistant", "content": content})
                break

            # Execute tools
            for tc in tool_calls:
                print(f"\n[Executing: {tc.name}({tc.arguments})]")
                result = TOOL_MAP[tc.name](**tc.arguments)
                print(f"[Result: {result[:200]}...]" if len(result) > 200 else f"[Result: {result}]")

                messages.append({
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [{"id": tc.id, "name": tc.name, "arguments": tc.arguments}]
                })
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result
                })

if __name__ == "__main__":
    run_file_agent()
```

</details>

<details>
<summary><b>TypeScript</b></summary>

```typescript
// demos/file-agent.ts
import * as fs from 'fs';
import * as path from 'path';
import * as readline from 'readline';

// Tool implementations
function readFile(filePath: string, encoding: BufferEncoding = 'utf-8'): string {
  try {
    return fs.readFileSync(filePath, encoding);
  } catch (e) {
    const error = e as NodeJS.ErrnoException;
    if (error.code === 'ENOENT') {
      return `Error: File not found: ${filePath}`;
    }
    return `Error reading file: ${error.message}`;
  }
}

function listDirectory(
  dirPath: string = '.',
  includeHidden: boolean = false,
  recursive: boolean = false
): string {
  try {
    if (!fs.existsSync(dirPath)) {
      return `Error: Path not found: ${dirPath}`;
    }

    const items: string[] = [];

    function walkDir(dir: string) {
      const entries = fs.readdirSync(dir, { withFileTypes: true });
      for (const entry of entries) {
        if (!includeHidden && entry.name.startsWith('.')) continue;

        const fullPath = path.join(dir, entry.name);
        const itemType = entry.isDirectory() ? 'DIR' : 'FILE';
        items.push(`[${itemType}] ${fullPath}`);

        if (recursive && entry.isDirectory()) {
          walkDir(fullPath);
        }
      }
    }

    walkDir(dirPath);
    return items.length > 0 ? items.sort().join('\n') : 'Directory is empty';
  } catch (e) {
    return `Error listing directory: ${(e as Error).message}`;
  }
}

function writeFile(filePath: string, content: string): string {
  try {
    fs.writeFileSync(filePath, content);
    return `Successfully wrote ${content.length} characters to ${filePath}`;
  } catch (e) {
    return `Error writing file: ${(e as Error).message}`;
  }
}

// Tool definitions and map
const TOOLS = [
  {
    name: 'read_file',
    description: 'Read the contents of a file',
    parameters: {
      type: 'object',
      properties: {
        file_path: { type: 'string', description: 'Path to the file' },
        encoding: { type: 'string', default: 'utf-8' },
      },
      required: ['file_path'],
    },
  },
  {
    name: 'list_directory',
    description: 'List contents of a directory',
    parameters: {
      type: 'object',
      properties: {
        path: { type: 'string', default: '.' },
        include_hidden: { type: 'boolean', default: false },
        recursive: { type: 'boolean', default: false },
      },
      required: [],
    },
  },
  {
    name: 'write_file',
    description: 'Write content to a file',
    parameters: {
      type: 'object',
      properties: {
        file_path: { type: 'string' },
        content: { type: 'string' },
      },
      required: ['file_path', 'content'],
    },
  },
];

const TOOL_MAP: Record<string, (args: any) => string> = {
  read_file: (args) => readFile(args.file_path, args.encoding),
  list_directory: (args) => listDirectory(args.path, args.include_hidden, args.recursive),
  write_file: (args) => writeFile(args.file_path, args.content),
};

const FILE_AGENT_SYSTEM = `You are a file system assistant. You help users explore and manage files.

Available tools:
- read_file: Read contents of a file
- list_directory: List contents of a directory
- write_file: Write content to a file

Guidelines:
1. Always confirm before writing/modifying files
2. Summarize file contents rather than dumping raw text
3. Be careful with recursive operations on large directories
4. Report errors clearly

When exploring code, provide insights about what you find.`;

async function runFileAgent() {
  const { AnthropicFunctionCalling } = await import('./function-calling.js');

  const client = new AnthropicFunctionCalling();
  const messages: Array<{ role: string; content: string }> = [];

  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  console.log('File System Agent Ready. Type "quit" to exit.');
  console.log('-'.repeat(50));

  const prompt = () => {
    rl.question('\nYou: ', async (userInput) => {
      if (userInput.toLowerCase() === 'quit') {
        rl.close();
        return;
      }

      messages.push({ role: 'user', content: userInput });

      // Agent loop
      while (true) {
        const { content, toolCalls } = await client.chatWithTools(
          [{ role: 'system', content: FILE_AGENT_SYSTEM }, ...messages],
          TOOLS
        );

        if (content) {
          console.log(`\nAgent: ${content}`);
        }

        if (toolCalls.length === 0) {
          messages.push({ role: 'assistant', content });
          break;
        }

        // Execute tools
        for (const tc of toolCalls) {
          console.log(`\n[Executing: ${tc.name}(${JSON.stringify(tc.arguments)})]`);
          const result = TOOL_MAP[tc.name](tc.arguments);
          const display = result.length > 200 ? `${result.slice(0, 200)}...` : result;
          console.log(`[Result: ${display}]`);

          messages.push({ role: 'tool', content: result });
        }
      }

      prompt();
    });
  };

  prompt();
}

runFileAgent();
```

</details>

### 2.4 Structured Output & Schema Validation (30 min)

In production, you need predictable, parseable outputs from LLMs. Structured output ensures consistency and enables robust error handling.

```
┌─────────────────────────────────────────────────────────────────┐
│                   Structured Output Hierarchy                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  LEVEL 1: Prompt-Based (Least Reliable)                        │
│  "Return JSON with fields: name, age, email"                   │
│  ❌ May return malformed JSON                                   │
│  ❌ Fields may be missing or extra                              │
│                                                                 │
│  LEVEL 2: JSON Mode (Better)                                   │
│  Tell LLM to return valid JSON                                 │
│  ✅ Valid JSON guaranteed (most providers)                      │
│  ❌ Schema not enforced                                         │
│                                                                 │
│  LEVEL 3: Schema Enforcement (Best)                            │
│  Define exact schema, validate response                         │
│  ✅ Valid JSON                                                  │
│  ✅ Correct schema                                              │
│  ✅ Type safety                                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Level 1: Prompt-Based (Not Recommended)**

```python
# Bad: Relying only on prompts
prompt = """
Return a JSON object with these fields:
- name (string)
- age (integer)
- email (string)

User data: John Doe, 30 years old, john@example.com
"""

response = llm.complete(prompt)
data = json.loads(response)  # May fail!
```

**Level 2: JSON Mode**

<details>
<parameter name="summary"><b>Python</b></summary>

```python
# agents/json_output.py
"""JSON mode for structured outputs."""
import anthropic
import json
from typing import Dict, Any

def get_structured_response(
    client: anthropic.Anthropic,
    prompt: str,
    schema_description: str
) -> Dict[str, Any]:
    """Get JSON response with JSON mode."""

    full_prompt = f"""
    {prompt}

    Return your response as a JSON object matching this structure:
    {schema_description}

    IMPORTANT: Return ONLY the JSON object, no other text.
    """

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": full_prompt
        }]
    )

    # Parse and validate JSON
    try:
        result = json.loads(response.content[0].text)
        return result
    except json.JSONDecodeError as e:
        # Retry or raise error
        raise ValueError(f"LLM returned invalid JSON: {e}")

# Usage
schema = """
{
  "name": "string",
  "age": "integer",
  "email": "string (valid email format)"
}
"""

result = get_structured_response(
    client=anthropic.Anthropic(),
    prompt="Extract information about: John Doe, 30, john@example.com",
    schema_description=schema
)
```

</details>

**Level 3: Schema Enforcement with Pydantic/Zod**

<details>
<parameter name="summary"><b>Python with Pydantic</b></summary>

```python
# agents/structured_agent.py
"""Agent with schema-validated outputs."""
from pydantic import BaseModel, EmailStr, Field, ValidationError
from typing import List, Optional
import anthropic
import json

# Define output schemas
class UserInfo(BaseModel):
    """Schema for user information."""
    name: str = Field(..., min_length=1, max_length=100)
    age: int = Field(..., ge=0, le=150)
    email: EmailStr
    phone: Optional[str] = None

class CodeAnalysis(BaseModel):
    """Schema for code analysis results."""
    issues: List[str] = Field(default_factory=list)
    severity: str = Field(..., pattern="^(low|medium|high|critical)$")
    recommendations: List[str] = Field(default_factory=list)
    estimated_fix_time_minutes: int = Field(..., ge=0)

class StructuredAgent:
    """Agent that returns validated structured outputs."""

    def __init__(self, client: anthropic.Anthropic):
        self.client = client

    def get_structured_output[T: BaseModel](
        self,
        prompt: str,
        output_schema: type[T],
        max_retries: int = 3
    ) -> T:
        """Get LLM output and validate against schema."""

        # Generate JSON schema from Pydantic model
        json_schema = output_schema.model_json_schema()

        # Create prompt with schema
        full_prompt = f"""
        {prompt}

        Return your response as a JSON object matching this EXACT schema:
        {json.dumps(json_schema, indent=2)}

        CRITICAL REQUIREMENTS:
        - Return ONLY valid JSON, no markdown, no explanations
        - Include ALL required fields
        - Match the specified types exactly
        - Follow any constraints (min/max, patterns, etc.)
        """

        for attempt in range(max_retries):
            try:
                # Get LLM response
                response = self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=2048,
                    messages=[{"role": "user", "content": full_prompt}]
                )

                # Extract JSON (handle markdown code blocks)
                text = response.content[0].text.strip()
                if text.startswith("```json"):
                    text = text[7:]
                if text.startswith("```"):
                    text = text[3:]
                if text.endswith("```"):
                    text = text[:-3]
                text = text.strip()

                # Parse JSON
                data = json.loads(text)

                # Validate with Pydantic
                validated = output_schema.model_validate(data)
                return validated

            except (json.JSONDecodeError, ValidationError) as e:
                if attempt == max_retries - 1:
                    raise ValueError(f"Failed to get valid output after {max_retries} attempts: {e}")

                # Add error feedback for retry
                full_prompt += f"\n\nPrevious attempt failed: {str(e)}\nPlease try again with correct format."

        raise ValueError("Should not reach here")

# Usage
agent = StructuredAgent(client=anthropic.Anthropic())

# Example 1: Extract user info
user = agent.get_structured_output(
    prompt="Extract user information from: John Doe, 30 years old, contact: john@example.com",
    output_schema=UserInfo
)
print(f"Name: {user.name}, Age: {user.age}, Email: {user.email}")
# Type-safe access! IDE autocomplete works

# Example 2: Code analysis
analysis = agent.get_structured_output(
    prompt="""
    Analyze this code for issues:
    ```python
    def divide(a, b):
        return a / b
    ```
    """,
    output_schema=CodeAnalysis
)

print(f"Severity: {analysis.severity}")
for issue in analysis.issues:
    print(f"  - {issue}")
```

</details>

<details>
<parameter name="summary"><b>TypeScript with Zod</b></summary>

```typescript
// agents/structured-agent.ts
import { z } from 'zod';
import Anthropic from '@anthropic-ai/sdk';

// Define schemas with Zod
const UserInfoSchema = z.object({
  name: z.string().min(1).max(100),
  age: z.number().int().min(0).max(150),
  email: z.string().email(),
  phone: z.string().optional(),
});

const CodeAnalysisSchema = z.object({
  issues: z.array(z.string()).default([]),
  severity: z.enum(['low', 'medium', 'high', 'critical']),
  recommendations: z.array(z.string()).default([]),
  estimatedFixTimeMinutes: z.number().int().min(0),
});

type UserInfo = z.infer<typeof UserInfoSchema>;
type CodeAnalysis = z.infer<typeof CodeAnalysisSchema>;

export class StructuredAgent {
  constructor(private client: Anthropic) {}

  async getStructuredOutput<T>(
    prompt: string,
    schema: z.ZodSchema<T>,
    maxRetries: number = 3
  ): Promise<T> {
    // Generate JSON schema description
    const schemaDescription = JSON.stringify(schema._def, null, 2);

    let fullPrompt = `
${prompt}

Return your response as a JSON object. Be precise and follow the schema exactly.

CRITICAL REQUIREMENTS:
- Return ONLY valid JSON, no markdown, no explanations
- Include ALL required fields
- Match the specified types exactly
    `;

    for (let attempt = 0; attempt < maxRetries; attempt++) {
      try {
        // Get LLM response
        const response = await this.client.messages.create({
          model: 'claude-3-5-sonnet-20241022',
          max_tokens: 2048,
          messages: [{ role: 'user', content: fullPrompt }],
        });

        // Extract JSON (handle markdown code blocks)
        let text = response.content[0].text.trim();
        if (text.startsWith('```json')) {
          text = text.slice(7);
        }
        if (text.startsWith('```')) {
          text = text.slice(3);
        }
        if (text.endsWith('```')) {
          text = text.slice(0, -3);
        }
        text = text.trim();

        // Parse and validate
        const data = JSON.parse(text);
        const validated = schema.parse(data);
        return validated;

      } catch (error) {
        if (attempt === maxRetries - 1) {
          throw new Error(
            `Failed to get valid output after ${maxRetries} attempts: ${error}`
          );
        }

        // Add error feedback for retry
        fullPrompt += `\n\nPrevious attempt failed: ${error}\nPlease try again with correct format.`;
      }
    }

    throw new Error('Should not reach here');
  }
}

// Usage
const agent = new StructuredAgent(new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY }));

// Example 1: Extract user info
const user = await agent.getStructuredOutput(
  'Extract user information from: John Doe, 30 years old, contact: john@example.com',
  UserInfoSchema
);
console.log(`Name: ${user.name}, Age: ${user.age}, Email: ${user.email}`);
// Type-safe! TypeScript knows the shape

// Example 2: Code analysis
const analysis = await agent.getStructuredOutput(
  `
  Analyze this code for issues:
  \`\`\`python
  def divide(a, b):
      return a / b
  \`\`\`
  `,
  CodeAnalysisSchema
);

console.log(`Severity: ${analysis.severity}`);
analysis.issues.forEach(issue => console.log(`  - ${issue}`));
```

</details>

**Advanced: Retry with Validation Feedback**

```python
# agents/smart_retry.py
"""Smart retry with validation feedback."""
from pydantic import BaseModel, ValidationError
import anthropic

class SmartRetryAgent:
    """Agent that provides specific validation errors to LLM."""

    def __init__(self, client: anthropic.Anthropic):
        self.client = client

    def get_validated_output[T: BaseModel](
        self,
        prompt: str,
        schema: type[T],
        max_retries: int = 3
    ) -> T:
        """Get output with smart retry on validation errors."""

        conversation = [
            {"role": "user", "content": self._build_prompt(prompt, schema)}
        ]

        for attempt in range(max_retries):
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2048,
                messages=conversation
            )

            response_text = response.content[0].text
            conversation.append({"role": "assistant", "content": response_text})

            try:
                # Try to parse and validate
                data = self._extract_json(response_text)
                return schema.model_validate(data)

            except ValidationError as e:
                # Build specific error message
                error_details = []
                for error in e.errors():
                    field = " -> ".join(str(x) for x in error['loc'])
                    error_details.append(
                        f"Field '{field}': {error['msg']} (got: {error.get('input', 'missing')})"
                    )

                feedback = f"""
                Your response had validation errors:

                {chr(10).join(error_details)}

                Please fix these specific issues and return a corrected JSON object.
                """

                conversation.append({"role": "user", "content": feedback})

                if attempt == max_retries - 1:
                    raise ValueError(f"Failed after {max_retries} attempts:\n{chr(10).join(error_details)}")

        raise ValueError("Should not reach here")

    def _build_prompt(self, prompt: str, schema: type[BaseModel]) -> str:
        """Build prompt with schema."""
        return f"""
        {prompt}

        Return a JSON object with this schema:
        {schema.model_json_schema()}

        Return ONLY the JSON, nothing else.
        """

    def _extract_json(self, text: str) -> dict:
        """Extract JSON from response."""
        import json
        text = text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        return json.loads(text.strip())
```

**Best Practices for Structured Output:**

1. **Always use schemas** in production - Don't rely on prompts alone
2. **Implement retries** - LLMs occasionally return malformed output
3. **Provide specific error feedback** - Tell the LLM exactly what was wrong
4. **Use type-safe schemas** - Pydantic (Python) or Zod (TypeScript)
5. **Test edge cases** - Empty arrays, null values, boundary conditions
6. **Log failures** - Track when validation fails to improve prompts
7. **Set reasonable retries** - 2-3 attempts is usually sufficient
8. **Handle partial success** - Sometimes you can salvage partial data

**When Structured Output Fails:**

| Scenario | Solution |
|----------|----------|
| **Repeated validation errors** | Simplify schema, provide more examples |
| **LLM ignores format** | Use explicit "JSON mode" in prompt |
| **Missing fields** | Mark fields as optional, provide defaults |
| **Wrong types** | Add type examples in prompt ("age: 25, not '25'") |
| **Extra fields** | Configure schema to allow extras or strip them |

---

<a name="patterns"></a>
## 3. Agent Patterns (1 hour)

### 3.1 ReAct: Reasoning + Acting

The ReAct pattern alternates between reasoning (thinking) and acting (using tools).

```
┌─────────────────────────────────────────────────────────────────┐
│                      ReAct Pattern                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Task: "Find the largest file in the src directory"             │
│                                                                 │
│  Thought 1: I need to list the contents of src first            │
│  Action 1: list_directory(path="src", recursive=True)           │
│  Observation 1: [FILE] src/main.py, [FILE] src/utils.py, ...    │
│                                                                 │
│  Thought 2: I have file names but not sizes. Need to check      │
│             each file's size.                                   │
│  Action 2: get_file_info(path="src/main.py")                    │
│  Observation 2: size: 15KB, modified: 2024-01-10                │
│                                                                 │
│  Thought 3: Continue checking other files...                    │
│  Action 3: get_file_info(path="src/utils.py")                   │
│  Observation 3: size: 42KB, modified: 2024-01-08                │
│                                                                 │
│  ... (continues until all files checked)                        │
│                                                                 │
│  Thought N: src/utils.py is the largest at 42KB                 │
│  Action N: (no action - provide answer)                         │
│  Final Answer: The largest file is src/utils.py (42KB)          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**ReAct Implementation:**

<details>
<summary><b>Python</b></summary>

```python
# patterns/react.py

REACT_SYSTEM_PROMPT = """You are an AI assistant that reasons step by step before acting.

For each step, you must:
1. Thought: Explain your reasoning about what to do next
2. Action: Call a tool if needed, or provide Final Answer if done

Format your response as:
Thought: [your reasoning]
Action: [tool_name(param1="value1", param2="value2")] OR Final Answer: [your answer]

Always think before acting. Never skip the Thought step.
If you encounter an error, reason about what went wrong and try a different approach.
"""

class ReactAgent:
    """Agent using the ReAct pattern."""

    def __init__(self, llm_client, tools: Dict[str, Callable], max_iterations: int = 10):
        self.llm = llm_client
        self.tools = tools
        self.max_iterations = max_iterations

    def run(self, task: str) -> str:
        messages = [
            {"role": "system", "content": REACT_SYSTEM_PROMPT},
            {"role": "user", "content": f"Task: {task}"}
        ]

        for i in range(self.max_iterations):
            response = self.llm.chat(messages)
            messages.append({"role": "assistant", "content": response})

            # Parse the response
            if "Final Answer:" in response:
                # Extract and return final answer
                answer = response.split("Final Answer:")[-1].strip()
                return answer

            # Extract and execute action
            if "Action:" in response:
                action_str = response.split("Action:")[-1].split("\n")[0].strip()
                result = self._execute_action(action_str)

                # Add observation
                observation = f"Observation: {result}"
                messages.append({"role": "user", "content": observation})

        return "Max iterations reached without final answer"

    def _execute_action(self, action_str: str) -> str:
        """Parse and execute an action string."""
        try:
            # Parse action like: tool_name(param1="value1")
            tool_name = action_str.split("(")[0]
            # ... parse arguments
            return self.tools[tool_name](**args)
        except Exception as e:
            return f"Error executing action: {e}"
```

</details>

<details>
<summary><b>TypeScript</b></summary>

```typescript
// patterns/react.ts
const REACT_SYSTEM_PROMPT = `You are an AI assistant that reasons step by step before acting.

For each step, you must:
1. Thought: Explain your reasoning about what to do next
2. Action: Call a tool if needed, or provide Final Answer if done

Format your response as:
Thought: [your reasoning]
Action: [tool_name(param1="value1", param2="value2")] OR Final Answer: [your answer]

Always think before acting. Never skip the Thought step.
If you encounter an error, reason about what went wrong and try a different approach.
`;

type ToolFunction = (args: Record<string, any>) => Promise<string> | string;

class ReactAgent {
  constructor(
    private llm: LLMClient,
    private tools: Map<string, ToolFunction>,
    private maxIterations: number = 10
  ) {}

  async run(task: string): Promise<string> {
    const messages: Array<{ role: string; content: string }> = [
      { role: 'system', content: REACT_SYSTEM_PROMPT },
      { role: 'user', content: `Task: ${task}` },
    ];

    for (let i = 0; i < this.maxIterations; i++) {
      const response = await this.llm.chat(messages);
      messages.push({ role: 'assistant', content: response });

      // Parse the response
      if (response.includes('Final Answer:')) {
        const answer = response.split('Final Answer:').pop()?.trim() || '';
        return answer;
      }

      // Extract and execute action
      if (response.includes('Action:')) {
        const actionStr = response.split('Action:').pop()?.split('\n')[0].trim() || '';
        const result = await this.executeAction(actionStr);

        // Add observation
        messages.push({ role: 'user', content: `Observation: ${result}` });
      }
    }

    return 'Max iterations reached without final answer';
  }

  private async executeAction(actionStr: string): Promise<string> {
    try {
      // Parse action like: tool_name(param1="value1")
      const toolName = actionStr.split('(')[0];
      const argsMatch = actionStr.match(/\((.*)\)/s);
      const args = argsMatch ? this.parseArgs(argsMatch[1]) : {};

      const tool = this.tools.get(toolName);
      if (!tool) {
        return `Error: Unknown tool ${toolName}`;
      }

      return await tool(args);
    } catch (e) {
      return `Error executing action: ${(e as Error).message}`;
    }
  }

  private parseArgs(argsStr: string): Record<string, any> {
    // Simple argument parser - production code would be more robust
    const args: Record<string, any> = {};
    const regex = /(\w+)=["']([^"']+)["']/g;
    let match;
    while ((match = regex.exec(argsStr)) !== null) {
      args[match[1]] = match[2];
    }
    return args;
  }
}
```

</details>

### 3.2 Planning Agents

Planning agents create a plan before executing, enabling complex multi-step tasks.

```
┌─────────────────────────────────────────────────────────────────┐
│                    Planning Agent Flow                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Task: "Migrate auth module from Express to FastAPI"            │
│                                                                 │
│  ┌─────────────────────────────────────────────┐                │
│  │              PLANNING PHASE                 │                │
│  │                                             │                │
│  │  1. Analyze existing Express auth code      │                │
│  │  2. Identify dependencies (bcrypt, jwt)     │                │
│  │  3. Map Express patterns to FastAPI         │                │
│  │  4. Create new file structure               │                │
│  │  5. Implement user model (Pydantic)         │                │
│  │  6. Implement auth endpoints                │                │
│  │  7. Add tests                               │                │
│  │  8. Verify functionality                    │                │
│  └─────────────────────────────────────────────┘                │
│                          │                                      │
│                          ▼                                      │
│  ┌─────────────────────────────────────────────┐                │
│  │             EXECUTION PHASE                 │                │
│  │                                             │                │
│  │  Step 1: ✓ Read routes/auth.js              │                │
│  │  Step 2: ✓ Found bcryptjs, jsonwebtoken     │                │
│  │  Step 3: ✓ Mapped to FastAPI equivalents    │                │
│  │  Step 4: ⟳ Creating routers/auth.py         │ ← Current      │
│  │  Step 5: ○ Pending                          │                │
│  │  ...                                        │                │
│  └─────────────────────────────────────────────┘                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Planning Agent Implementation:**

<details>
<summary><b>Python</b></summary>

```python
# patterns/planning.py
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

class StepStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class PlanStep:
    id: int
    description: str
    status: StepStatus = StepStatus.PENDING
    result: Optional[str] = None
    dependencies: List[int] = None  # IDs of steps this depends on

@dataclass
class Plan:
    task: str
    steps: List[PlanStep]
    current_step: int = 0

PLANNING_PROMPT = """Create a detailed plan for the following task.
Break it into concrete, executable steps.

Task: {task}

Output your plan as a numbered list:
1. [First step]
2. [Second step]
...

Guidelines:
- Each step should be independently verifiable
- Include validation/testing steps
- Consider rollback steps for risky operations
- Order steps by dependencies
"""

class PlanningAgent:
    """Agent that plans before executing."""

    def __init__(self, llm_client, tools: Dict, max_replans: int = 3):
        self.llm = llm_client
        self.tools = tools
        self.max_replans = max_replans

    def run(self, task: str) -> str:
        # Phase 1: Create plan
        plan = self._create_plan(task)
        print(f"Created plan with {len(plan.steps)} steps")

        # Phase 2: Execute plan
        results = []
        for i, step in enumerate(plan.steps):
            # Check dependencies
            if not self._dependencies_met(step, plan.steps):
                step.status = StepStatus.SKIPPED
                continue

            step.status = StepStatus.IN_PROGRESS
            result = self._execute_step(plan, step, results)

            if result.success:
                step.status = StepStatus.COMPLETED
                step.result = result.output
                results.append(result)
            else:
                step.status = StepStatus.FAILED
                # Attempt replan
                if not self._replan(plan, step, result.error):
                    return f"Failed at step {i+1}: {result.error}"

        return self._summarize_results(plan, results)

    def _create_plan(self, task: str) -> Plan:
        """Use LLM to create a plan."""
        prompt = PLANNING_PROMPT.format(task=task)
        response = self.llm.chat([
            {"role": "system", "content": "You are a planning assistant."},
            {"role": "user", "content": prompt}
        ])

        # Parse response into steps
        steps = self._parse_plan(response)
        return Plan(task=task, steps=steps)
```

</details>

<details>
<summary><b>TypeScript</b></summary>

```typescript
// patterns/planning.ts
type StepStatus = 'pending' | 'in_progress' | 'completed' | 'failed' | 'skipped';

interface PlanStep {
  id: number;
  description: string;
  status: StepStatus;
  result?: string;
  dependencies?: number[]; // IDs of steps this depends on
}

interface Plan {
  task: string;
  steps: PlanStep[];
  currentStep: number;
}

const PLANNING_PROMPT = `Create a detailed plan for the following task.
Break it into concrete, executable steps.

Task: {task}

Output your plan as a numbered list:
1. [First step]
2. [Second step]
...

Guidelines:
- Each step should be independently verifiable
- Include validation/testing steps
- Consider rollback steps for risky operations
- Order steps by dependencies
`;

class PlanningAgent {
  constructor(
    private llm: LLMClient,
    private tools: Map<string, ToolFunction>,
    private maxReplans: number = 3
  ) {}

  async run(task: string): Promise<string> {
    // Phase 1: Create plan
    const plan = await this.createPlan(task);
    console.log(`Created plan with ${plan.steps.length} steps`);

    // Phase 2: Execute plan
    const results: StepResult[] = [];

    for (let i = 0; i < plan.steps.length; i++) {
      const step = plan.steps[i];

      // Check dependencies
      if (!this.dependenciesMet(step, plan.steps)) {
        step.status = 'skipped';
        continue;
      }

      step.status = 'in_progress';
      const result = await this.executeStep(plan, step, results);

      if (result.success) {
        step.status = 'completed';
        step.result = result.output;
        results.push(result);
      } else {
        step.status = 'failed';
        // Attempt replan
        if (!(await this.replan(plan, step, result.error!))) {
          return `Failed at step ${i + 1}: ${result.error}`;
        }
      }
    }

    return this.summarizeResults(plan, results);
  }

  private async createPlan(task: string): Promise<Plan> {
    const prompt = PLANNING_PROMPT.replace('{task}', task);
    const response = await this.llm.chat([
      { role: 'system', content: 'You are a planning assistant.' },
      { role: 'user', content: prompt },
    ]);

    // Parse response into steps
    const steps = this.parsePlan(response);
    return { task, steps, currentStep: 0 };
  }

  private parsePlan(response: string): PlanStep[] {
    const lines = response.split('\n').filter((l) => /^\d+\./.test(l.trim()));
    return lines.map((line, i) => ({
      id: i,
      description: line.replace(/^\d+\.\s*/, '').trim(),
      status: 'pending' as StepStatus,
    }));
  }

  private dependenciesMet(step: PlanStep, allSteps: PlanStep[]): boolean {
    if (!step.dependencies) return true;
    return step.dependencies.every(
      (depId) => allSteps[depId]?.status === 'completed'
    );
  }

  // ... executeStep, replan, summarizeResults implementations
}
```

</details>

### 3.3 Verification Agents

Agents that verify their own work before declaring completion.

<details>
<summary><b>Python</b></summary>

```python
# patterns/verification.py

VERIFICATION_PROMPT = """You just completed a task. Verify your work.

Task: {task}
Your output: {output}

Verification checklist:
1. Does the output satisfy all requirements?
2. Are there any errors or issues?
3. Is the output complete?
4. Are there edge cases not handled?

Rate your confidence (1-10) and explain any concerns.
If confidence < 8, suggest improvements.
"""

class VerifyingAgent:
    """Agent that verifies its outputs."""

    def __init__(self, llm_client, tools, confidence_threshold: float = 0.8):
        self.llm = llm_client
        self.tools = tools
        self.confidence_threshold = confidence_threshold

    def run_with_verification(self, task: str) -> str:
        # Initial execution
        result = self._execute_task(task)

        # Verification loop
        for attempt in range(3):
            verification = self._verify(task, result)

            if verification.confidence >= self.confidence_threshold:
                return result

            # Improve based on feedback
            result = self._improve(task, result, verification.feedback)

        # Return best effort after max attempts
        return result

    def _verify(self, task: str, output: str) -> 'Verification':
        """Verify the output."""
        prompt = VERIFICATION_PROMPT.format(task=task, output=output)
        response = self.llm.chat([
            {"role": "user", "content": prompt}
        ])
        return self._parse_verification(response)

    def _improve(self, task: str, output: str, feedback: str) -> str:
        """Improve output based on verification feedback."""
        prompt = f"""Improve this output based on feedback.

Task: {task}
Current output: {output}
Feedback: {feedback}

Provide improved output addressing the feedback."""

        return self.llm.chat([{"role": "user", "content": prompt}])
```

</details>

<details>
<summary><b>TypeScript</b></summary>

```typescript
// patterns/verification.ts
const VERIFICATION_PROMPT = `You just completed a task. Verify your work.

Task: {task}
Your output: {output}

Verification checklist:
1. Does the output satisfy all requirements?
2. Are there any errors or issues?
3. Is the output complete?
4. Are there edge cases not handled?

Rate your confidence (1-10) and explain any concerns.
If confidence < 8, suggest improvements.
`;

interface Verification {
  confidence: number;
  feedback: string;
  concerns: string[];
}

class VerifyingAgent {
  constructor(
    private llm: LLMClient,
    private tools: Map<string, ToolFunction>,
    private confidenceThreshold: number = 0.8
  ) {}

  async runWithVerification(task: string): Promise<string> {
    // Initial execution
    let result = await this.executeTask(task);

    // Verification loop
    for (let attempt = 0; attempt < 3; attempt++) {
      const verification = await this.verify(task, result);

      if (verification.confidence >= this.confidenceThreshold) {
        return result;
      }

      // Improve based on feedback
      result = await this.improve(task, result, verification.feedback);
    }

    // Return best effort after max attempts
    return result;
  }

  private async verify(task: string, output: string): Promise<Verification> {
    const prompt = VERIFICATION_PROMPT
      .replace('{task}', task)
      .replace('{output}', output);

    const response = await this.llm.chat([{ role: 'user', content: prompt }]);
    return this.parseVerification(response);
  }

  private async improve(task: string, output: string, feedback: string): Promise<string> {
    const prompt = `Improve this output based on feedback.

Task: ${task}
Current output: ${output}
Feedback: ${feedback}

Provide improved output addressing the feedback.`;

    return this.llm.chat([{ role: 'user', content: prompt }]);
  }

  private parseVerification(response: string): Verification {
    // Extract confidence score (look for patterns like "8/10" or "confidence: 8")
    const confidenceMatch = response.match(/(\d+)\/10|confidence:\s*(\d+)/i);
    const confidence = confidenceMatch
      ? parseInt(confidenceMatch[1] || confidenceMatch[2]) / 10
      : 0.5;

    return {
      confidence,
      feedback: response,
      concerns: [],
    };
  }

  private async executeTask(task: string): Promise<string> {
    // Implementation depends on the specific task
    return this.llm.chat([{ role: 'user', content: task }]);
  }
}
```

</details>

### 3.4 Pattern Selection Guide

```markdown
## When to Use Each Pattern

### ReAct (Reasoning + Acting)
✅ Use when:
- Task requires exploration
- Multiple possible paths
- Need to adapt based on findings
- Debugging/investigation tasks

❌ Avoid when:
- Task is straightforward
- Steps are known in advance
- Speed is critical

### Planning
✅ Use when:
- Complex multi-step tasks
- Need to coordinate dependencies
- Risk of wrong order causing issues
- User needs to approve plan first

❌ Avoid when:
- Simple, single-step tasks
- Highly dynamic situations
- Requirements unclear (explore first)

### Verification
✅ Use when:
- Output correctness is critical
- Code generation tasks
- Tasks with testable criteria
- High-stakes decisions

❌ Avoid when:
- Verification would be as hard as the task
- Speed is critical
- Output is inherently subjective
```

---

<a name="exercise-1"></a>
## 4. Exercise 1: Design an Agent (15 min)

### Task
Design an agent architecture for a "Code Migration Assistant" that migrates Python 2 code to Python 3.

### Template

```markdown
## Code Migration Agent Design

### Agent Type
[ ] ReAct (explore and migrate incrementally)
[ ] Planning (analyze all, plan migration, execute)
[ ] Hybrid (plan first, use ReAct for each step)

Why:

### Required Tools
1. Tool name:
   - Purpose:
   - Parameters:

2. Tool name:
   - Purpose:
   - Parameters:

3. (add more as needed)

### Agent Flow
```
[Draw or describe the flow]
```

### Memory Requirements
- Short-term:
- Long-term:
- Working memory:

### Error Handling
How will the agent handle:
- Syntax errors in migrated code?
- Ambiguous migration patterns?
- Files it can't migrate automatically?

### Verification Strategy
How will the agent verify migrations are correct?

### Estimated Iterations
Typical iterations for a single file:
Typical iterations for a project:
```

---

<a name="multi-agent"></a>
## 5. Multi-Agent Systems (1 hour)

### 5.1 When Single Agents Aren't Enough

```
┌─────────────────────────────────────────────────────────────────┐
│                Single Agent Limitations                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. CONTEXT EXHAUSTION                                          │
│     Complex tasks exceed context window                         │
│                                                                 │
│  2. ROLE CONFUSION                                              │
│     One agent trying to be expert in everything                 │
│                                                                 │
│  3. SERIAL EXECUTION                                            │
│     Can't parallelize independent subtasks                      │
│                                                                 │
│  4. SINGLE POINT OF FAILURE                                     │
│     One mistake derails entire process                          │
│                                                                 │
│  5. LACK OF CHECKS                                              │
│     No second opinion on outputs                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 Multi-Agent Architectures

**Architecture 1: Supervisor Pattern**
```
┌─────────────────────────────────────────────────────────────────┐
│                    Supervisor Pattern                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                    ┌─────────────┐                              │
│                    │ SUPERVISOR  │                              │
│                    │   AGENT     │                              │
│                    └──────┬──────┘                              │
│                           │                                     │
│         ┌─────────────────┼─────────────────┐                   │
│         │                 │                 │                   │
│         ▼                 ▼                 ▼                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  RESEARCH   │  │   CODING    │  │   REVIEW    │              │
│  │   AGENT     │  │   AGENT     │  │   AGENT     │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│                                                                 │
│  Supervisor:                                                    │
│  - Receives task from user                                      │
│  - Delegates to specialized agents                              │
│  - Aggregates results                                           │
│  - Handles failures and retries                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Architecture 2: Pipeline Pattern**
```
┌─────────────────────────────────────────────────────────────────┐
│                     Pipeline Pattern                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────┐   ┌───────────┐   ┌───────────┐   ┌───────────┐  │
│  │  ANALYZE  │──▶│  PLAN     │──▶│  EXECUTE  │──▶│  VERIFY   │  │
│  │  AGENT    │   │  AGENT    │   │  AGENT    │   │  AGENT    │  │
│  └───────────┘   └───────────┘   └───────────┘   └───────────┘  │
│       │               │               │               │         │
│       ▼               ▼               ▼               ▼         │
│  [Analysis]      [Plan Doc]      [Output]       [Verified]      │
│                                                                 │
│  Each agent:                                                    │
│  - Specialized for one phase                                    │
│  - Passes structured output to next                             │
│  - Can request redo from previous                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Architecture 3: Debate/Consensus Pattern**
```
┌─────────────────────────────────────────────────────────────────┐
│                  Debate/Consensus Pattern                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│         ┌─────────────┐     ┌─────────────┐                     │
│         │  AGENT A    │     │  AGENT B    │                     │
│         │ (Advocate)  │     │ (Skeptic)   │                     │
│         └──────┬──────┘     └──────┬──────┘                     │
│                │                   │                            │
│                └─────────┬─────────┘                            │
│                          │                                      │
│                          ▼                                      │
│                   ┌─────────────┐                               │
│                   │   JUDGE     │                               │
│                   │   AGENT     │                               │
│                   └─────────────┘                               │
│                                                                 │
│  Flow:                                                          │
│  1. Agent A proposes solution                                   │
│  2. Agent B critiques/challenges                                │
│  3. Agent A responds to critique                                │
│  4. Repeat until Judge calls consensus                          │
│  5. Judge synthesizes final answer                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 5.3 Communication Patterns

<details>
<summary><b>Python</b></summary>

```python
# agents/multi_agent.py
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum

class MessageType(Enum):
    TASK = "task"
    RESULT = "result"
    QUESTION = "question"
    FEEDBACK = "feedback"
    ERROR = "error"

@dataclass
class AgentMessage:
    """Message passed between agents."""
    from_agent: str
    to_agent: str
    type: MessageType
    content: Any
    metadata: Dict[str, Any] = None

class MessageBus:
    """Central message bus for agent communication."""

    def __init__(self):
        self.messages: List[AgentMessage] = []
        self.subscribers: Dict[str, List[callable]] = {}

    def publish(self, message: AgentMessage):
        """Publish a message."""
        self.messages.append(message)

        # Notify subscribers
        if message.to_agent in self.subscribers:
            for callback in self.subscribers[message.to_agent]:
                callback(message)

    def subscribe(self, agent_id: str, callback: callable):
        """Subscribe to messages for an agent."""
        if agent_id not in self.subscribers:
            self.subscribers[agent_id] = []
        self.subscribers[agent_id].append(callback)

    def get_conversation(self, agent1: str, agent2: str) -> List[AgentMessage]:
        """Get conversation between two agents."""
        return [
            m for m in self.messages
            if (m.from_agent in [agent1, agent2] and m.to_agent in [agent1, agent2])
        ]
```

</details>

<details>
<summary><b>TypeScript</b></summary>

```typescript
// agents/multi-agent.ts
type MessageType = 'task' | 'result' | 'question' | 'feedback' | 'error';

interface AgentMessage {
  fromAgent: string;
  toAgent: string;
  type: MessageType;
  content: any;
  metadata?: Record<string, any>;
}

type MessageCallback = (message: AgentMessage) => void;

class MessageBus {
  private messages: AgentMessage[] = [];
  private subscribers: Map<string, MessageCallback[]> = new Map();

  publish(message: AgentMessage): void {
    this.messages.push(message);

    // Notify subscribers
    const callbacks = this.subscribers.get(message.toAgent);
    if (callbacks) {
      callbacks.forEach((callback) => callback(message));
    }
  }

  subscribe(agentId: string, callback: MessageCallback): void {
    if (!this.subscribers.has(agentId)) {
      this.subscribers.set(agentId, []);
    }
    this.subscribers.get(agentId)!.push(callback);
  }

  getConversation(agent1: string, agent2: string): AgentMessage[] {
    const participants = [agent1, agent2];
    return this.messages.filter(
      (m) => participants.includes(m.fromAgent) && participants.includes(m.toAgent)
    );
  }

  // Get all messages for an agent
  getMessagesFor(agentId: string): AgentMessage[] {
    return this.messages.filter((m) => m.toAgent === agentId);
  }

  // Get message history
  getHistory(): AgentMessage[] {
    return [...this.messages];
  }
}
```

</details>

### 5.4 Avoiding Infinite Loops

```python
# agents/safety.py

class LoopDetector:
    """Detects and prevents infinite agent loops."""

    def __init__(self, max_iterations: int = 50, similarity_threshold: float = 0.9):
        self.max_iterations = max_iterations
        self.similarity_threshold = similarity_threshold
        self.state_history: List[str] = []

    def check_state(self, state: str) -> bool:
        """
        Check if current state suggests a loop.
        Returns True if loop detected.
        """
        # Check iteration limit
        if len(self.state_history) >= self.max_iterations:
            return True

        # Check for repeated states
        for past_state in self.state_history[-10:]:
            if self._similarity(state, past_state) > self.similarity_threshold:
                return True

        self.state_history.append(state)
        return False

    def _similarity(self, s1: str, s2: str) -> float:
        """Simple similarity check."""
        # Use more sophisticated comparison in production
        words1 = set(s1.lower().split())
        words2 = set(s2.lower().split())
        if not words1 or not words2:
            return 0.0
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        return intersection / union


class MultiAgentOrchestrator:
    """Orchestrates multiple agents with safety controls."""

    def __init__(self, agents: Dict[str, 'BaseAgent'], max_rounds: int = 10):
        self.agents = agents
        self.max_rounds = max_rounds
        self.loop_detector = LoopDetector()
        self.message_bus = MessageBus()

    def run(self, task: str) -> str:
        """Run multi-agent workflow."""
        for round_num in range(self.max_rounds):
            # Collect current state
            state = self._get_system_state()

            # Check for loops
            if self.loop_detector.check_state(state):
                return self._handle_loop_detected()

            # Run one round
            result = self._execute_round(round_num)

            if result.is_complete:
                return result.output

        return "Max rounds exceeded without completion"

    def _get_system_state(self) -> str:
        """Get string representation of system state for loop detection."""
        # Include recent messages and agent states
        recent_messages = self.message_bus.messages[-10:]
        return str([(m.from_agent, m.type, m.content[:100]) for m in recent_messages])

    def _handle_loop_detected(self) -> str:
        """Handle detected infinite loop."""
        # Options: return partial result, escalate, or try different approach
        return "Loop detected - returning best effort result"
```

### 5.5 Supervisor Agent Implementation

```python
# agents/supervisor.py

SUPERVISOR_PROMPT = """You are a supervisor managing a team of specialized agents.

Available agents:
{agent_descriptions}

Your job:
1. Analyze the incoming task
2. Break it into subtasks for your agents
3. Delegate to appropriate agents
4. Synthesize their outputs into a final result

For each decision, output:
DELEGATE: agent_name
TASK: specific task for that agent

When all subtasks are done, output:
SYNTHESIZE: [your final synthesis]

Current task: {task}
Previous results: {results}
"""

class SupervisorAgent:
    """Supervisor that coordinates specialized agents."""

    def __init__(self, llm_client, worker_agents: Dict[str, 'BaseAgent']):
        self.llm = llm_client
        self.workers = worker_agents
        self.agent_descriptions = self._build_descriptions()

    def run(self, task: str) -> str:
        results = {}
        iterations = 0
        max_iterations = 20

        while iterations < max_iterations:
            # Get supervisor decision
            decision = self._get_decision(task, results)

            if decision.type == "SYNTHESIZE":
                return decision.content

            if decision.type == "DELEGATE":
                # Execute worker agent
                worker = self.workers[decision.agent]
                result = worker.run(decision.task)
                results[f"{decision.agent}_{iterations}"] = result

            iterations += 1

        return self._force_synthesis(task, results)

    def _get_decision(self, task: str, results: Dict) -> 'Decision':
        """Get next decision from supervisor."""
        prompt = SUPERVISOR_PROMPT.format(
            agent_descriptions=self.agent_descriptions,
            task=task,
            results=json.dumps(results, indent=2)
        )

        response = self.llm.chat([
            {"role": "system", "content": "You are a project supervisor."},
            {"role": "user", "content": prompt}
        ])

        return self._parse_decision(response)

    def _build_descriptions(self) -> str:
        """Build description of available worker agents."""
        lines = []
        for name, agent in self.workers.items():
            lines.append(f"- {name}: {agent.description}")
        return "\n".join(lines)
```

---

<a name="frameworks"></a>
## 6. Framework Comparison (30 min)

### 6.1 Framework Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Agent Framework Landscape                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  LangChain/LangGraph                                            │
│  ──────────────────                                             │
│  • Most popular, largest ecosystem                              │
│  • LangGraph for complex state machines                         │
│  • Great for RAG and chains                                     │
│  • Can be verbose for simple cases                              │
│                                                                 │
│  CrewAI                                                         │
│  ──────                                                         │
│  • Focus on multi-agent collaboration                           │
│  • Role-based agent definitions                                 │
│  • Built-in task delegation                                     │
│  • Good for team simulations                                    │
│                                                                 │
│  AutoGen (Microsoft)                                            │
│  ─────────────────                                              │
│  • Conversational agent focus                                   │
│  • Human-in-the-loop support                                    │
│  • Code execution capabilities                                  │
│  • Enterprise-oriented                                          │
│                                                                 │
│  Custom Implementation                                          │
│  ─────────────────────                                          │
│  • Full control                                                 │
│  • No framework overhead                                        │
│  • More work but more flexibility                               │
│  • Good for learning                                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 6.2 Quick Comparison

| Feature | LangChain/LangGraph | CrewAI | AutoGen | Custom |
|---------|---------------------|--------|---------|--------|
| Learning Curve | Medium-High | Low-Medium | Medium | Low |
| Flexibility | High | Medium | Medium | Very High |
| Multi-Agent | ✅ (LangGraph) | ✅ Native | ✅ Native | Build yourself |
| RAG Support | ✅ Excellent | ✅ Good | ✅ Good | Build yourself |
| Production Ready | ✅ | ⚠️ Maturing | ✅ | Depends |
| Community | Very Large | Growing | Large | N/A |
| Best For | Complex pipelines | Team tasks | Conversations | Specific needs |

### 6.3 Code Comparison

**Simple Agent: LangChain**
```python
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_anthropic import ChatAnthropic
from langchain.tools import tool

@tool
def search(query: str) -> str:
    """Search for information."""
    return f"Results for: {query}"

llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")
tools = [search]
agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools)
result = executor.invoke({"input": "Find Python tutorials"})
```

**Simple Agent: CrewAI**
```python
from crewai import Agent, Task, Crew

researcher = Agent(
    role="Researcher",
    goal="Find accurate information",
    backstory="Expert at finding information",
    tools=[search_tool]
)

task = Task(
    description="Find Python tutorials",
    agent=researcher
)

crew = Crew(agents=[researcher], tasks=[task])
result = crew.kickoff()
```

**Simple Agent: Custom**
```python
class SimpleAgent:
    def __init__(self, llm, tools):
        self.llm = llm
        self.tools = tools

    def run(self, task: str) -> str:
        messages = [{"role": "user", "content": task}]
        while True:
            response, tool_calls = self.llm.chat_with_tools(messages, self.tools)
            if not tool_calls:
                return response
            for tc in tool_calls:
                result = self.tools[tc.name](**tc.args)
                messages.append({"role": "tool", "content": result})

agent = SimpleAgent(llm, tools)
result = agent.run("Find Python tutorials")
```

### 6.4 Decision Matrix

```markdown
## Framework Selection Guide

Choose **LangChain/LangGraph** if:
- [ ] Building complex RAG pipelines
- [ ] Need extensive integrations
- [ ] Want large community support
- [ ] Building production systems

Choose **CrewAI** if:
- [ ] Multi-agent collaboration is core
- [ ] Want role-based agent design
- [ ] Simulating team workflows
- [ ] Prefer simpler API

Choose **AutoGen** if:
- [ ] Need human-in-the-loop
- [ ] Building conversational systems
- [ ] Enterprise requirements
- [ ] Microsoft ecosystem

Choose **Custom** if:
- [ ] Learning how agents work
- [ ] Very specific requirements
- [ ] Minimal dependencies needed
- [ ] Full control required
```

---

<a name="lab-03"></a>
## 7. Lab 03: Migration Workflow Agent (1h 45min)

### Lab Overview

**Goal:** Build a multi-step agent that migrates code between frameworks.

**The agent will:**
1. Analyze source code
2. Create a migration plan
3. Execute migration steps
4. Verify the migration

**Stack:**
- Python
- Planning + Execution pattern
- LLM-agnostic design

### Lab Instructions

Navigate to `labs/lab03-migration-workflow/` and follow the README.

**Quick Start:**
```bash
cd labs/lab03-migration-workflow
cat README.md
# Follow steps to build the migration agent
```

### Expected Outcome

By the end of this lab, you should have:
1. A working migration workflow agent
2. Experience with the planning pattern
3. Multi-step verification
4. Deployment to Railway

---

## Day 3 Summary

### What We Covered
1. **Agent Fundamentals**: The agent loop, memory, state management
2. **Tool-Use**: Function calling across providers, error handling
3. **Agent Patterns**: ReAct, Planning, Verification
4. **Multi-Agent Systems**: Supervisor, Pipeline, Debate patterns
5. **Frameworks**: LangChain, CrewAI, AutoGen comparison

### Key Takeaways
- Agents = LLM + Tools + Loop + Memory
- Tool definitions are crucial—clear descriptions help the LLM
- Choose patterns based on task complexity
- Multi-agent systems solve context and specialization problems
- Start simple, add complexity as needed

### Architecture Diagrams You Should Have
- [ ] Basic agent loop
- [ ] ReAct pattern
- [ ] Planning agent flow
- [ ] Supervisor pattern

### Preparation for Day 4
- Think about data you'd want to search over
- Consider how you'd evaluate agent outputs
- Review the migration agent—we'll add RAG to it

---

**Navigation**: [← Day 2](./day2-prompting.md) | [Day 4: RAG & Evaluation →](./day4-rag-eval.md)
