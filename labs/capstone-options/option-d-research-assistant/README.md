# Capstone Option D: Multi-Agent Research Assistant

## Project Overview

Build a sophisticated multi-agent system where specialized AI agents (Researcher, Writer, Reviewer) collaborate under a Supervisor to conduct research and produce polished reports.

**Complexity**: High
**Estimated Time**: 2-2.5 hours

---

## Requirements

### Must Have (Core - 70%)
- [ ] Three specialized worker agents:
  - **Researcher**: Gathers information and creates summaries
  - **Writer**: Creates polished, structured content
  - **Reviewer**: Reviews content for quality and accuracy
- [ ] Supervisor agent that:
  - Decomposes research questions into subtasks
  - Delegates to appropriate agents
  - Coordinates iterative workflow
  - Synthesizes final output
- [ ] POST `/research` endpoint accepting research question
- [ ] Iterative workflow (research → write → review → refine loop)
- [ ] Returns structured JSON with final report and metadata

### Should Have (Polish - 20%)
- [ ] Conversation history in API response (shows agent interactions)
- [ ] Configurable parameters (max_iterations, depth level)
- [ ] Error handling and timeout protection
- [ ] Progress tracking in response

### Nice to Have (Bonus - 10%)
- [ ] Streaming responses (show real-time progress)
- [ ] Web search tool for Researcher agent
- [ ] Reference tracking and citations
- [ ] Multiple report formats (brief, detailed, technical)
- [ ] Agent performance metrics (tokens used, time taken)

---

## API Specification

### POST /research

**Request:**
```json
{
  "question": "Explain the differences between RAG and fine-tuning for LLMs",
  "depth": "detailed",
  "max_iterations": 5
}
```

**Response:**
```json
{
  "report": {
    "title": "RAG vs Fine-Tuning for Large Language Models",
    "summary": "RAG and fine-tuning are complementary techniques...",
    "sections": [
      {
        "heading": "Overview",
        "content": "RAG (Retrieval-Augmented Generation) enhances LLM responses..."
      },
      {
        "heading": "Key Differences",
        "content": "1. RAG provides external knowledge dynamically..."
      },
      {
        "heading": "When to Use Each",
        "content": "Use RAG when you need up-to-date information..."
      }
    ],
    "references": [
      "Based on analysis of LLM architectures",
      "Industry best practices for knowledge integration"
    ]
  },
  "metadata": {
    "iterations": 3,
    "agents_used": ["Researcher", "Writer", "Reviewer"],
    "total_tokens": 12500,
    "duration_seconds": 45.2
  },
  "conversation_history": [
    {
      "iteration": 0,
      "agent": "Supervisor",
      "action": "DELEGATE",
      "target_agent": "Researcher",
      "task": "Research RAG and fine-tuning techniques..."
    },
    {
      "iteration": 0,
      "agent": "Researcher",
      "result": "Research findings: RAG uses retrieval..."
    },
    {
      "iteration": 1,
      "agent": "Supervisor",
      "action": "DELEGATE",
      "target_agent": "Writer",
      "task": "Create structured content from research..."
    },
    {
      "iteration": 1,
      "agent": "Writer",
      "result": "# RAG vs Fine-Tuning\n\n## Overview..."
    },
    {
      "iteration": 2,
      "agent": "Supervisor",
      "action": "DELEGATE",
      "target_agent": "Reviewer",
      "task": "Review content for accuracy..."
    },
    {
      "iteration": 2,
      "agent": "Reviewer",
      "result": "Overall quality: 9/10. Minor improvements..."
    },
    {
      "iteration": 3,
      "agent": "Supervisor",
      "action": "FINAL",
      "output": "Complete report with all sections"
    }
  ]
}
```

---

## Starter Code

### main.py
```python
"""Multi-Agent Research Assistant - Capstone Option D"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import time

from supervisor import SupervisorAgent
from llm_client import LLMClient

app = FastAPI(title="Multi-Agent Research Assistant")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ResearchRequest(BaseModel):
    question: str
    depth: str = "detailed"  # "brief", "detailed", "technical"
    max_iterations: int = 5

class Section(BaseModel):
    heading: str
    content: str

class Report(BaseModel):
    title: str
    summary: str
    sections: List[Section]
    references: List[str]

class ResearchResponse(BaseModel):
    report: Report
    metadata: Dict
    conversation_history: List[Dict]

@app.post("/research", response_model=ResearchResponse)
async def conduct_research(request: ResearchRequest):
    """Conduct research using multi-agent system.

    Args:
        request: Research request with question and parameters

    Returns:
        Structured research report with agent interaction history
    """
    # Validate inputs
    if not request.question or len(request.question) < 10:
        raise HTTPException(status_code=400, detail="Question too short")

    if request.depth not in ["brief", "detailed", "technical"]:
        raise HTTPException(status_code=400, detail="Invalid depth level")

    # TODO: Implement multi-agent research
    try:
        llm = LLMClient()
        supervisor = SupervisorAgent(llm)

        # Run multi-agent workflow
        result = supervisor.run(
            task=request.question,
            depth=request.depth,
            max_iterations=request.max_iterations
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Research failed: {str(e)}")

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "multi-agent-research"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### supervisor.py
```python
"""Supervisor agent that coordinates research workflow."""
from typing import Dict, List
import time

from agents import ResearcherAgent, WriterAgent, ReviewerAgent

SUPERVISOR_PROMPT = """You are a research supervisor managing a team of specialized agents.

Available agents:
- **Researcher**: Gathers comprehensive information on topics, synthesizes findings
- **Writer**: Creates polished, well-structured content from research
- **Reviewer**: Reviews content for accuracy, clarity, and completeness

Your workflow:
1. Analyze the research question
2. Break it down into subtasks if needed
3. Delegate to Researcher to gather information
4. Delegate to Writer to create structured content
5. Delegate to Reviewer to check quality
6. Iterate based on review feedback if needed
7. Synthesize final report

Output format for delegation:
DELEGATE: [agent_name]
TASK: [specific task description]

When the report is complete and reviewed:
FINAL: [final report in markdown format]

Important:
- Always gather research first before writing
- Always review before finalizing
- Keep iterations focused and efficient
- Aim for 2-4 iterations total
"""

class SupervisorAgent:
    """Supervisor that orchestrates multi-agent research."""

    def __init__(self, llm_client):
        """Initialize supervisor with worker agents.

        Args:
            llm_client: LLM client for supervisor decisions
        """
        self.llm = llm_client

        # Initialize worker agents
        self.workers = {
            "Researcher": ResearcherAgent(llm_client),
            "Writer": WriterAgent(llm_client),
            "Reviewer": ReviewerAgent(llm_client)
        }

        self.results = {}
        self.conversation_history = []
        self.start_time = None

    def run(
        self,
        task: str,
        depth: str = "detailed",
        max_iterations: int = 5
    ) -> Dict:
        """Run the multi-agent research workflow.

        Args:
            task: Research question or task
            depth: Detail level (brief, detailed, technical)
            max_iterations: Maximum iterations before forcing completion

        Returns:
            Complete research report with metadata
        """
        self.start_time = time.time()

        messages = [
            {"role": "system", "content": SUPERVISOR_PROMPT},
            {
                "role": "user",
                "content": f"Research question: {task}\n\nDepth level: {depth}\n\nProvide a {depth} analysis."
            }
        ]

        for i in range(max_iterations):
            # Get supervisor decision
            response = self.llm.chat(messages)
            messages.append({"role": "assistant", "content": response})

            # Log decision
            self._log_iteration(i, "Supervisor", response)

            # Check if done
            if "FINAL:" in response:
                final_report = response.split("FINAL:")[-1].strip()
                return self._format_response(final_report, i + 1)

            # Parse and execute delegation
            if "DELEGATE:" in response and "TASK:" in response:
                agent_name = response.split("DELEGATE:")[-1].split("TASK:")[0].strip()
                agent_task = response.split("TASK:")[-1].strip()

                if agent_name in self.workers:
                    # Execute worker agent
                    print(f"  Iteration {i}: Delegating to {agent_name}")

                    context = self._get_context()
                    result = self.workers[agent_name].execute(agent_task, context)

                    # Store result
                    self.results[f"{agent_name}_{i}"] = result

                    # Log result
                    self._log_iteration(i, agent_name, result)

                    # Feed back to supervisor
                    messages.append({
                        "role": "user",
                        "content": f"Result from {agent_name}:\n\n{result}"
                    })
                else:
                    # Unknown agent, ask supervisor to try again
                    messages.append({
                        "role": "user",
                        "content": f"Error: Agent '{agent_name}' not found. Available: {list(self.workers.keys())}"
                    })

        # Force final if max iterations reached
        final_report = self._force_final()
        return self._format_response(final_report, max_iterations)

    def _get_context(self) -> str:
        """Build context string from previous results."""
        if not self.results:
            return ""

        parts = []
        for key, value in self.results.items():
            parts.append(f"=== {key} ===\n{value}")

        return "\n\n".join(parts)

    def _force_final(self) -> str:
        """Force final output when max iterations reached."""
        # Try to return latest writer output
        writer_results = [v for k, v in self.results.items() if "Writer" in k]
        if writer_results:
            return writer_results[-1]

        # Otherwise return last result
        if self.results:
            return list(self.results.values())[-1]

        return "Research incomplete due to iteration limit."

    def _log_iteration(self, iteration: int, agent: str, content: str):
        """Log agent interaction to history."""
        # Parse action type
        action = "RESULT"
        if "DELEGATE:" in content:
            action = "DELEGATE"
        elif "FINAL:" in content:
            action = "FINAL"

        log_entry = {
            "iteration": iteration,
            "agent": agent,
            "action": action,
            "content": content[:200] + "..." if len(content) > 200 else content
        }

        self.conversation_history.append(log_entry)

    def _format_response(self, final_report: str, iterations: int) -> Dict:
        """Format final response with structured report and metadata.

        Args:
            final_report: Final report from agents (markdown format)
            iterations: Number of iterations used

        Returns:
            Structured response matching API spec
        """
        # Parse markdown report into sections
        report = self._parse_markdown_report(final_report)

        # Build metadata
        duration = time.time() - self.start_time
        agents_used = list(set(h['agent'] for h in self.conversation_history))

        metadata = {
            "iterations": iterations,
            "agents_used": agents_used,
            "duration_seconds": round(duration, 2)
        }

        return {
            "report": report,
            "metadata": metadata,
            "conversation_history": self.conversation_history
        }

    def _parse_markdown_report(self, markdown: str) -> Dict:
        """Parse markdown report into structured format.

        Args:
            markdown: Report in markdown format

        Returns:
            Structured report dict
        """
        # TODO: Implement markdown parsing
        # Extract title (# heading), sections (## headings), content

        lines = markdown.split('\n')

        # Simple parsing
        title = "Research Report"
        summary = ""
        sections = []
        references = []

        current_section = None
        current_content = []

        for line in lines:
            if line.startswith('# '):
                title = line[2:].strip()
            elif line.startswith('## '):
                # Save previous section
                if current_section:
                    sections.append({
                        "heading": current_section,
                        "content": '\n'.join(current_content).strip()
                    })

                # Start new section
                current_section = line[3:].strip()
                current_content = []
            elif current_section:
                current_content.append(line)
            elif line.strip() and not summary:
                # First paragraph is summary
                summary = line.strip()

        # Save last section
        if current_section:
            sections.append({
                "heading": current_section,
                "content": '\n'.join(current_content).strip()
            })

        return {
            "title": title,
            "summary": summary or "Research completed",
            "sections": sections,
            "references": references
        }
```

### agents.py
```python
"""Worker agents for research workflow."""

RESEARCHER_PROMPT = """You are a research specialist agent.

Your role:
1. Gather comprehensive information on assigned topics
2. Synthesize findings into clear summaries
3. Identify key facts, concepts, and relationships
4. Note any uncertainties or knowledge gaps
5. Provide structured, organized research output

Output format:
# Research Findings

## Key Points
- Point 1
- Point 2
- Point 3

## Detailed Analysis
[In-depth findings with explanations]

## Sources and Reasoning
[How you arrived at these conclusions, what you based this on]

## Gaps
[Any areas that need more research or are uncertain]
"""

WRITER_PROMPT = """You are a professional technical writer agent.

Your role:
1. Transform research into polished, well-structured content
2. Organize information logically with clear sections
3. Write in clear, engaging, professional prose
4. Add appropriate formatting and structure
5. Ensure smooth flow and readability
6. Include examples where helpful

Output format:
# [Descriptive Title]

[Brief introduction paragraph]

## [Section 1 - Key Concept]
[Clear explanation with examples]

## [Section 2 - Another Concept]
[More detailed content]

## [Section 3 - Practical Applications]
[Real-world usage and examples]

## Summary
[Concise wrap-up of key takeaways]
"""

REVIEWER_PROMPT = """You are a content quality reviewer agent.

Your role:
1. Review content for accuracy and completeness
2. Check clarity, readability, and flow
3. Identify any errors, gaps, or unclear sections
4. Suggest specific improvements with examples
5. Rate overall quality objectively

Output format:
# Review Feedback

## Overall Assessment
Quality Score: [1-10]/10
[Brief overall evaluation]

## Strengths
- Strength 1
- Strength 2
- Strength 3

## Issues Found
- **Issue 1**: [Description]
  - Suggested fix: [Specific improvement]

- **Issue 2**: [Description]
  - Suggested fix: [Specific improvement]

## Missing Elements
- [Any important missing information]

## Recommendation
**[APPROVE / REVISE]**

If REVISE: [Specific guidance for improvements needed]
If APPROVE: [Why it's ready to publish]
"""

class WorkerAgent:
    """Base class for specialized worker agents."""

    def __init__(self, llm_client, system_prompt: str, name: str):
        """Initialize worker agent.

        Args:
            llm_client: LLM client for agent
            system_prompt: Specialized system prompt
            name: Agent name
        """
        self.llm = llm_client
        self.system_prompt = system_prompt
        self.name = name

    def execute(self, task: str, context: str = "") -> str:
        """Execute assigned task with optional context.

        Args:
            task: Task description from supervisor
            context: Context from previous agent results

        Returns:
            Agent's output
        """
        # Build user prompt
        user_prompt = task

        if context:
            user_prompt = f"""Previous work context:
{context}

---

Your task:
{task}"""

        # Call LLM with agent's system prompt
        response = self.llm.chat(self.system_prompt, user_prompt)

        return response


class ResearcherAgent(WorkerAgent):
    """Agent specialized in gathering and synthesizing information."""

    def __init__(self, llm_client):
        super().__init__(llm_client, RESEARCHER_PROMPT, "Researcher")


class WriterAgent(WorkerAgent):
    """Agent specialized in creating polished, structured content."""

    def __init__(self, llm_client):
        super().__init__(llm_client, WRITER_PROMPT, "Writer")


class ReviewerAgent(WorkerAgent):
    """Agent specialized in reviewing content for quality."""

    def __init__(self, llm_client):
        super().__init__(llm_client, REVIEWER_PROMPT, "Reviewer")
```

### llm_client.py
```python
"""LLM client abstraction."""
import os
from anthropic import Anthropic

class LLMClient:
    """Simple LLM client for multi-agent system."""

    def __init__(self):
        """Initialize LLM client with API key from environment."""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not found in environment. "
                "Set it in .env or export it."
            )

        self.client = Anthropic(api_key=api_key)
        self.model = "claude-3-5-sonnet-20241022"

    def chat(self, system: str, user: str) -> str:
        """Send messages to LLM and get response.

        Args:
            system: System prompt
            user: User message

        Returns:
            LLM response text
        """
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system,
            messages=[{"role": "user", "content": user}]
        )

        return response.content[0].text
```

### requirements.txt
```
fastapi==0.109.0
uvicorn==0.27.0
pydantic==2.5.3
anthropic==0.18.0
python-dotenv==1.0.0
```

---

## Implementation Steps

1. **Setup** (10 min)
   - Copy starter files
   - Install dependencies: `pip install -r requirements.txt`
   - Set ANTHROPIC_API_KEY in .env
   - Test server: `uvicorn main:app --reload`

2. **Worker Agents** (30 min)
   - Review ResearcherAgent, WriterAgent, ReviewerAgent in agents.py
   - Test each agent individually with sample tasks
   - Verify prompts produce expected outputs
   - Adjust prompts if needed for better results

3. **Supervisor Logic** (40 min)
   - Complete `run()` method in supervisor.py
   - Implement delegation parsing (DELEGATE/TASK format)
   - Implement context building from previous results
   - Test supervisor decision-making with simple task
   - Verify agent coordination works

4. **Response Formatting** (30 min)
   - Complete `_parse_markdown_report()` in supervisor.py
   - Extract title, sections, summary from markdown
   - Build structured report object
   - Test parsing with sample markdown

5. **Workflow Integration** (20 min)
   - Connect supervisor.run() to /research endpoint
   - Test full workflow: research → write → review
   - Verify conversation history is captured
   - Test with brief vs detailed vs technical depths

6. **Iteration Handling** (15 min)
   - Test max_iterations limit
   - Verify force_final() works when limit reached
   - Test early completion (FINAL before max iterations)
   - Handle edge cases (invalid agent name, parse errors)

7. **Deploy & Demo** (15 min)
   - Deploy to Railway: `railway init && railway up`
   - Set environment variables
   - Test deployed endpoint
   - Prepare demo questions (simple, complex, technical)

---

## Testing

### Test simple research question

```bash
# Start server
uvicorn main:app --reload

# Test with simple question
curl -X POST http://localhost:8000/research \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the key differences between REST and GraphQL APIs?",
    "depth": "brief"
  }'

# Expected: Report with 1-2 sections, 1-2 iterations
```

### Test complex research question

```bash
# Test detailed research
curl -X POST http://localhost:8000/research \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Explain how transformers work in deep learning, including the attention mechanism and its applications",
    "depth": "detailed",
    "max_iterations": 7
  }'

# Expected: Comprehensive report with multiple sections, 3-5 iterations, shows research → write → review cycle
```

### Test technical depth

```bash
# Test technical analysis
curl -X POST http://localhost:8000/research \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Compare RAG and fine-tuning for LLMs",
    "depth": "technical"
  }'

# Expected: Technical report with detailed explanations, agent conversation visible in history
```

### Verify conversation history

```bash
# Check that conversation history shows agent interactions
# Expected in response:
# - "conversation_history" array
# - Shows DELEGATE actions
# - Shows agent results
# - Shows final synthesis
```

---

## Evaluation Checklist

- [ ] Three specialized agents implemented
- [ ] Supervisor coordinates agents correctly
- [ ] Delegates tasks with DELEGATE/TASK format
- [ ] Builds context from previous results
- [ ] Parses markdown into structured report
- [ ] API endpoint returns correct JSON format
- [ ] Conversation history captured
- [ ] Handles max iterations limit
- [ ] Error handling works
- [ ] Deployed and accessible
- [ ] Demo ready with sample questions

---

## TypeScript Version (Optional)

For students who prefer TypeScript, equivalent implementation available in `typescript/` directory using:
- Hono for API framework
- Same agent pattern with TypeScript types
- Identical supervisor logic
- Zod for validation

See Python version for detailed implementation guidance.

---

## Extension Ideas

If you finish early:
- Add web search tool to Researcher agent
- Implement streaming responses (SSE)
- Add citation tracking from sources
- Create specialized agents (DataAnalyzer, CodeReviewer, etc.)
- Add agent performance metrics
- Implement multi-turn conversations (follow-up questions)
- Add visualization of agent workflow
