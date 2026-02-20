"""
Reusable Python Agent Template
==============================

This template provides a foundation for building LLM-powered agents.
Customize the system prompt, tools, and logic for your specific use case.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
import json


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class ToolCall:
    """Represents a tool call from the LLM."""
    name: str
    arguments: Dict[str, Any]
    id: str = ""

@dataclass
class ToolResult:
    """Result of executing a tool."""
    tool_call_id: str
    result: str
    error: Optional[str] = None

@dataclass
class AgentState:
    """Current state of the agent."""
    messages: List[Dict[str, str]] = field(default_factory=list)
    tool_results: List[ToolResult] = field(default_factory=list)
    iteration: int = 0
    is_complete: bool = False


# ============================================================================
# Tool Definition
# ============================================================================

class Tool(ABC):
    """Base class for agent tools."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name for LLM reference."""
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

    def to_dict(self) -> Dict[str, Any]:
        """Convert tool to dictionary for LLM."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        }


# ============================================================================
# Example Tools
# ============================================================================

class CalculatorTool(Tool):
    """Example: Simple calculator tool."""

    @property
    def name(self) -> str:
        return "calculator"

    @property
    def description(self) -> str:
        return "Perform basic arithmetic operations. Supports +, -, *, /"

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Mathematical expression to evaluate (e.g., '2 + 2')"
                }
            },
            "required": ["expression"]
        }

    def execute(self, expression: str) -> str:
        try:
            # WARNING: In production, use a safe expression parser
            result = eval(expression)
            return str(result)
        except Exception as e:
            return f"Error: {e}"


# ============================================================================
# LLM Client Interface
# ============================================================================

class LLMClient(ABC):
    """Abstract LLM client interface."""

    @abstractmethod
    def chat(self, messages: List[Dict], tools: List[Dict] = None) -> tuple[str, List[ToolCall]]:
        """
        Send messages and return (response_content, tool_calls).
        """
        pass


class AnthropicClient(LLMClient):
    """Anthropic Claude client."""

    def __init__(self, model: str = "claude-3-5-sonnet-20241022"):
        from anthropic import Anthropic
        self.client = Anthropic()
        self.model = model

    def chat(self, messages: List[Dict], tools: List[Dict] = None) -> tuple[str, List[ToolCall]]:
        # Extract system message
        system = None
        filtered = []
        for m in messages:
            if m["role"] == "system":
                system = m["content"]
            else:
                filtered.append(m)

        # Convert tools to Anthropic format
        anthropic_tools = None
        if tools:
            anthropic_tools = [
                {
                    "name": t["name"],
                    "description": t["description"],
                    "input_schema": t["parameters"]
                }
                for t in tools
            ]

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system,
            messages=filtered,
            tools=anthropic_tools
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


class OpenAIClient(LLMClient):
    """OpenAI client."""

    def __init__(self, model: str = "gpt-4o"):
        from openai import OpenAI
        self.client = OpenAI()
        self.model = model

    def chat(self, messages: List[Dict], tools: List[Dict] = None) -> tuple[str, List[ToolCall]]:
        # Convert tools to OpenAI format
        openai_tools = None
        if tools:
            openai_tools = [
                {"type": "function", "function": t}
                for t in tools
            ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=openai_tools
        )

        message = response.choices[0].message

        # Parse tool calls
        tool_calls = []
        if message.tool_calls:
            for tc in message.tool_calls:
                tool_calls.append(ToolCall(
                    id=tc.id,
                    name=tc.function.name,
                    arguments=json.loads(tc.function.arguments)
                ))

        return message.content or "", tool_calls


# ============================================================================
# Agent Core
# ============================================================================

class Agent:
    """
    Base agent that can use tools to accomplish tasks.

    Usage:
        llm = AnthropicClient()
        tools = [CalculatorTool()]
        agent = Agent(llm, tools, system_prompt="You are a helpful assistant.")
        result = agent.run("What is 25 * 4?")
    """

    def __init__(
        self,
        llm_client: LLMClient,
        tools: List[Tool],
        system_prompt: str,
        max_iterations: int = 10
    ):
        self.llm = llm_client
        self.tools = {t.name: t for t in tools}
        self.tool_definitions = [t.to_dict() for t in tools]
        self.system_prompt = system_prompt
        self.max_iterations = max_iterations

    def run(self, user_input: str) -> str:
        """Run the agent on a user input."""
        state = AgentState(
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_input}
            ]
        )

        while not state.is_complete and state.iteration < self.max_iterations:
            state = self._step(state)
            state.iteration += 1

        # Return final response
        for msg in reversed(state.messages):
            if msg["role"] == "assistant" and msg["content"]:
                return msg["content"]

        return "Unable to complete the task."

    def _step(self, state: AgentState) -> AgentState:
        """Execute one step of the agent loop."""
        content, tool_calls = self.llm.chat(
            state.messages,
            self.tool_definitions if self.tools else None
        )

        if not tool_calls:
            # No tool calls = final response
            state.messages.append({"role": "assistant", "content": content})
            state.is_complete = True
        else:
            # Execute tools
            for tc in tool_calls:
                if tc.name in self.tools:
                    result = self.tools[tc.name].execute(**tc.arguments)
                    state.tool_results.append(ToolResult(
                        tool_call_id=tc.id,
                        result=result
                    ))

                    # Add to messages (format depends on LLM provider)
                    state.messages.append({
                        "role": "assistant",
                        "content": content or "",
                        "tool_use": {"id": tc.id, "name": tc.name, "input": tc.arguments}
                    })
                    state.messages.append({
                        "role": "user",
                        "content": f"Tool result for {tc.name}: {result}"
                    })

        return state


# ============================================================================
# Usage Example
# ============================================================================

if __name__ == "__main__":
    # Example usage
    llm = AnthropicClient()
    tools = [CalculatorTool()]

    agent = Agent(
        llm_client=llm,
        tools=tools,
        system_prompt="You are a helpful assistant that can perform calculations."
    )

    result = agent.run("What is 123 * 456?")
    print(f"Result: {result}")
