# Exercise 15: Multi-Agent Orchestrator System

## Description
Orchestration system for multiple specialized agents that collaborate to solve complex tasks.

## Objectives
- Orchestrate multiple specialized agents
- Implement communication protocols
- Manage shared state and memory
- Prevent infinite loops and deadlocks
- Scale horizontally

## Architecture

```
User Request → Orchestrator → [Planner Agent]
                            → [Research Agent]
                            → [Code Agent]
                            → [QA Agent]
                            → Synthesizer → Response
```

## Agent Types

### 1. Orchestrator
Central coordinator que delega tareas

### 2. Specialized Agents
- **Planner**: Breaks down complex tasks
- **Researcher**: Gathers information
- **Coder**: Writes/modifies code
- **QA**: Tests and validates
- **Reviewer**: Code review
- **Documenter**: Writes docs

## Core Implementation

```python
from enum import Enum
from typing import List, Dict, Any
import asyncio
from dataclasses import dataclass

class AgentRole(Enum):
    ORCHESTRATOR = "orchestrator"
    PLANNER = "planner"
    RESEARCHER = "researcher"
    CODER = "coder"
    QA = "qa"
    REVIEWER = "reviewer"

@dataclass
class Message:
    from_agent: str
    to_agent: str
    content: str
    message_type: str  # "request", "response", "question"
    metadata: Dict[str, Any]

@dataclass
class Task:
    id: str
    description: str
    assigned_to: str | None
    status: str  # "pending", "in_progress", "completed", "failed"
    result: Any | None
    dependencies: List[str]

class Agent:
    def __init__(self, role: AgentRole, llm):
        self.role = role
        self.llm = llm
        self.inbox: asyncio.Queue = asyncio.Queue()

    async def process_message(self, message: Message) -> Message:
        """Process incoming message and generate response"""
        raise NotImplementedError

    async def run(self):
        """Main agent loop"""
        while True:
            message = await self.inbox.get()
            response = await self.process_message(message)
            await self._send_message(response)

class Orchestrator:
    def __init__(self):
        self.agents: Dict[AgentRole, Agent] = {}
        self.tasks: Dict[str, Task] = {}
        self.shared_state = SharedState()
        self.message_bus = MessageBus()

    def register_agent(self, agent: Agent):
        """Register specialized agent"""
        self.agents[agent.role] = agent

    async def execute_request(self, user_request: str) -> str:
        """Main orchestration logic"""
        print(f"🎯 Orchestrating: {user_request}")

        # 1. Create execution plan
        plan = await self._create_plan(user_request)
        print(f"📋 Plan: {len(plan)} tasks")

        # 2. Execute tasks with dependencies
        results = await self._execute_plan(plan)

        # 3. Synthesize final result
        final_result = await self._synthesize_results(results)

        return final_result

    async def _create_plan(self, request: str) -> List[Task]:
        """Delegate to Planner agent"""
        planner = self.agents[AgentRole.PLANNER]

        message = Message(
            from_agent="orchestrator",
            to_agent="planner",
            content=f"Create execution plan for: {request}",
            message_type="request",
            metadata={}
        )

        response = await self._send_and_wait(planner, message)
        return self._parse_plan(response.content)

    async def _execute_plan(self, plan: List[Task]) -> Dict[str, Any]:
        """Execute tasks respecting dependencies"""
        results = {}
        completed = set()

        while len(completed) < len(plan):
            # Find tasks ready to execute
            ready_tasks = [
                task for task in plan
                if task.id not in completed
                and all(dep in completed for dep in task.dependencies)
            ]

            if not ready_tasks:
                raise Exception("Deadlock detected in task dependencies")

            # Execute ready tasks in parallel
            await asyncio.gather(*[
                self._execute_task(task, results)
                for task in ready_tasks
            ])

            completed.update(task.id for task in ready_tasks)

        return results

    async def _execute_task(self, task: Task, results: Dict):
        """Execute single task by delegating to appropriate agent"""
        print(f"⚙️  Executing: {task.description}")

        # Select agent based on task type
        agent = self._select_agent_for_task(task)

        # Prepare context from dependencies
        context = {
            dep_id: results[dep_id]
            for dep_id in task.dependencies
        }

        # Send task to agent
        message = Message(
            from_agent="orchestrator",
            to_agent=agent.role.value,
            content=task.description,
            message_type="request",
            metadata={"context": context}
        )

        response = await self._send_and_wait(agent, message)

        # Store result
        task.status = "completed"
        task.result = response.content
        results[task.id] = response.content

        print(f"✅ Completed: {task.description}")

    def _select_agent_for_task(self, task: Task) -> Agent:
        """Select appropriate agent based on task description"""
        description_lower = task.description.lower()

        if any(word in description_lower for word in ['research', 'find', 'search']):
            return self.agents[AgentRole.RESEARCHER]
        elif any(word in description_lower for word in ['code', 'implement', 'write']):
            return self.agents[AgentRole.CODER]
        elif any(word in description_lower for word in ['test', 'validate']):
            return self.agents[AgentRole.QA]
        elif any(word in description_lower for word in ['review', 'check']):
            return self.agents[AgentRole.REVIEWER]
        else:
            return self.agents[AgentRole.PLANNER]

    async def _send_and_wait(self, agent: Agent, message: Message) -> Message:
        """Send message and wait for response"""
        await agent.inbox.put(message)

        # Wait for response (with timeout)
        try:
            response = await asyncio.wait_for(
                agent.inbox.get(),
                timeout=30.0
            )
            return response
        except asyncio.TimeoutError:
            raise Exception(f"Agent {agent.role} timed out")
```

## Specialized Agent Implementations

```python
class PlannerAgent(Agent):
    async def process_message(self, message: Message) -> Message:
        prompt = f"""
You are a planning agent. Break down this request into subtasks:

Request: {message.content}

Create a detailed plan with:
1. Task descriptions
2. Dependencies between tasks
3. Agent assignments

Output as JSON.
"""

        response = await self.llm.ainvoke(prompt)

        return Message(
            from_agent=self.role.value,
            to_agent=message.from_agent,
            content=response.content,
            message_type="response",
            metadata={}
        )

class CoderAgent(Agent):
    async def process_message(self, message: Message) -> Message:
        context = message.metadata.get('context', {})

        prompt = f"""
You are a coding agent. Implement the following:

Task: {message.content}

Context from previous tasks:
{json.dumps(context, indent=2)}

Write clean, tested code.
"""

        response = await self.llm.ainvoke(prompt)

        # Save code to file
        code = self._extract_code(response.content)
        file_path = self._save_code(code)

        return Message(
            from_agent=self.role.value,
            to_agent=message.from_agent,
            content=response.content,
            message_type="response",
            metadata={"file_path": file_path}
        )

class QAAgent(Agent):
    async def process_message(self, message: Message) -> Message:
        """Test code from previous task"""
        code_file = message.metadata.get('context', {}).get('file_path')

        if not code_file:
            return self._error_response("No code file provided")

        # Run tests
        test_result = subprocess.run(
            ['pytest', code_file, '-v'],
            capture_output=True,
            text=True
        )

        passed = test_result.returncode == 0

        return Message(
            from_agent=self.role.value,
            to_agent=message.from_agent,
            content=f"Tests {'passed' if passed else 'failed'}\n{test_result.stdout}",
            message_type="response",
            metadata={"tests_passed": passed}
        )
```

## Shared State Management

```python
class SharedState:
    """Thread-safe shared state for agents"""

    def __init__(self):
        self._state: Dict[str, Any] = {}
        self._lock = asyncio.Lock()

    async def set(self, key: str, value: Any):
        async with self._lock:
            self._state[key] = value

    async def get(self, key: str) -> Any:
        async with self._lock:
            return self._state.get(key)

    async def update(self, updates: Dict[str, Any]):
        async with self._lock:
            self._state.update(updates)
```

## Loop Prevention

```python
class LoopDetector:
    """Detect and prevent infinite loops in agent communication"""

    def __init__(self, max_iterations=20):
        self.max_iterations = max_iterations
        self.iteration_count = 0
        self.message_history = []

    def check_loop(self, message: Message) -> bool:
        """Check if we're in a loop"""
        self.iteration_count += 1

        if self.iteration_count > self.max_iterations:
            raise Exception("Max iterations exceeded - possible infinite loop")

        # Check for repeated message patterns
        self.message_history.append(message)
        if self._detect_pattern(self.message_history[-10:]):
            raise Exception("Repeated message pattern detected - infinite loop")

        return False

    def _detect_pattern(self, recent_messages: List[Message]) -> bool:
        """Detect if same messages are repeating"""
        if len(recent_messages) < 4:
            return False

        # Simple pattern detection: check if messages repeat
        pattern_size = 2
        pattern = recent_messages[-pattern_size:]

        for i in range(len(recent_messages) - pattern_size * 2):
            if recent_messages[i:i+pattern_size] == pattern:
                return True

        return False
```

## Example Usage

```python
# Setup orchestrator
orchestrator = Orchestrator()

# Register specialized agents
orchestrator.register_agent(PlannerAgent(AgentRole.PLANNER, llm))
orchestrator.register_agent(CoderAgent(AgentRole.CODER, llm))
orchestrator.register_agent(QAAgent(AgentRole.QA, llm))
orchestrator.register_agent(ReviewerAgent(AgentRole.REVIEWER, llm))

# Execute complex request
result = await orchestrator.execute_request("""
Build a REST API for a todo app with:
1. CRUD endpoints
2. Authentication
3. Unit tests
4. Documentation
""")

print(result)
```

## Advanced Features

### 1. Dynamic Agent Spawning
```python
class DynamicOrchestrator(Orchestrator):
    async def spawn_agent_if_needed(self, task: Task):
        """Spawn specialized agent on-demand"""
        if task requires_specialized_skill:
            agent = await self._create_specialized_agent(task)
            self.register_agent(agent)
```

### 2. Consensus Mechanism
```python
async def get_consensus(self, question: str, num_agents=3):
    """Get consensus from multiple agents"""
    responses = await asyncio.gather(*[
        agent.answer(question)
        for agent in self.agents[:num_agents]
    ])

    # Majority vote or synthesize
    return self._synthesize_responses(responses)
```

## Testing

```python
async def test_orchestration():
    orchestrator = create_test_orchestrator()

    result = await orchestrator.execute_request(
        "Write a function to calculate fibonacci"
    )

    assert "def fibonacci" in result
    assert "test" in result

async def test_loop_prevention():
    detector = LoopDetector(max_iterations=10)

    for i in range(15):
        try:
            detector.check_loop(Message(...))
        except Exception as e:
            assert "Max iterations" in str(e)
            break
```

## Challenges

1. **Distributed Orchestration**: Multi-machine deployment
2. **Human-in-the-Loop**: Allow human intervention
3. **Learning System**: Agents improve from past tasks
4. **Cost Optimization**: Minimize LLM calls

## Resources
- [LangGraph Multi-Agent](https://langchain-ai.github.io/langgraph/tutorials/multi-agent/)
- [AutoGen Framework](https://microsoft.github.io/autogen/)
- [CrewAI](https://github.com/joaomdmoura/crewAI)

**Time**: 10-12h
