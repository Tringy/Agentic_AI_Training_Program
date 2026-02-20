# Exercise 12: Autonomous Debugger Agent

## Description
Autonomous agent that analyzes errors, investigates code, proposes fixes, and validates solutions.

## Objectives
- Automatically analyze stack traces
- Investigate related code
- Generate potential fixes
- Validate fixes with tests
- Iterate until functional solution

## Agent Loop

```
Error → Analyze → Investigate → Generate Fix → Test → Success?
           ↑                                              ↓ No
           └──────────────── Iterate ────────────────────┘
```

## Core Implementation

```python
from langgraph.prebuilt import create_react_agent
from langchain_anthropic import ChatAnthropic

class AutonomousDebugger:
    def __init__(self):
        self.llm = ChatAnthropic(model="claude-sonnet-4")
        self.tools = [
            self.read_file_tool,
            self.run_tests_tool,
            self.apply_fix_tool,
            self.search_code_tool,
        ]

        self.agent = create_react_agent(
            self.llm,
            self.tools,
            state_modifier=self.get_system_prompt()
        )

    def get_system_prompt(self) -> str:
        return """
You are an expert debugging agent. Given an error:

1. ANALYZE the stack trace and error message
2. INVESTIGATE relevant code files
3. IDENTIFY the root cause
4. GENERATE a fix
5. TEST the fix
6. If test fails, ITERATE

Tools available:
- read_file(path): Read file contents
- search_code(query): Search codebase
- run_tests(test_file): Run specific tests
- apply_fix(file, old_code, new_code): Apply fix

Always explain your reasoning at each step.
"""

    async def debug(self, error: str, context: dict) -> DebugResult:
        """Main debugging loop"""
        print(f"🐛 Analyzing error: {error[:100]}...")

        result = await self.agent.ainvoke({
            "messages": [{
                "role": "user",
                "content": f"""
Debug this error:

Error:
{error}

Context:
- File: {context.get('file', 'unknown')}
- Function: {context.get('function', 'unknown')}
- Test: {context.get('test', 'unknown')}

Find the root cause and fix it.
"""
            }]
        })

        return self._parse_result(result)

    def read_file_tool(self, path: str) -> str:
        """Read source code file"""
        try:
            with open(path, 'r') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {e}"

    def search_code_tool(self, query: str) -> List[str]:
        """Search codebase for relevant code"""
        # Use ripgrep or similar
        result = subprocess.run(
            ['rg', '--files-with-matches', query],
            capture_output=True,
            text=True
        )
        return result.stdout.strip().split('\n')

    def run_tests_tool(self, test_file: str) -> str:
        """Run tests and return results"""
        result = subprocess.run(
            ['pytest', test_file, '-v'],
            capture_output=True,
            text=True
        )
        return result.stdout + result.stderr

    def apply_fix_tool(self, file: str, old_code: str, new_code: str) -> str:
        """Apply a code fix"""
        try:
            with open(file, 'r') as f:
                content = f.read()

            if old_code not in content:
                return f"Error: old_code not found in {file}"

            new_content = content.replace(old_code, new_code)

            with open(file, 'w') as f:
                f.write(new_content)

            return f"✅ Fix applied to {file}"
        except Exception as e:
            return f"Error applying fix: {e}"
```

## Example Debugging Session

```python
debugger = AutonomousDebugger()

# Real error from test failure
error = """
FAILED tests/test_calculator.py::test_divide - ZeroDivisionError: division by zero
tests/test_calculator.py:10: in test_divide
    result = calculator.divide(10, 0)
calculator.py:15: in divide
    return a / b
"""

result = await debugger.debug(error, {
    "file": "calculator.py",
    "test": "tests/test_calculator.py::test_divide"
})

# Agent output:
# 1. Reading calculator.py...
# 2. Found divide function at line 14-15
# 3. Issue: No zero-division check
# 4. Generating fix...
# 5. Applying fix: Add zero check
# 6. Running tests...
# 7. ✅ Tests pass! Fix successful
```

## Advanced Features

### 1. Multi-Step Reasoning

```python
class ReasoningDebugger(AutonomousDebugger):
    async def debug_with_reasoning(self, error: str):
        # Step 1: Hypothesize causes
        hypotheses = await self._generate_hypotheses(error)

        # Step 2: Test each hypothesis
        for hypothesis in hypotheses:
            print(f"🧪 Testing: {hypothesis}")

            evidence = await self._gather_evidence(hypothesis)

            if self._supports_hypothesis(evidence):
                # Generate fix based on confirmed hypothesis
                fix = await self._generate_fix(hypothesis)
                if await self._validate_fix(fix):
                    return fix

        return None

    async def _generate_hypotheses(self, error: str) -> List[str]:
        response = await self.llm.ainvoke(f"""
Given this error:
{error}

Generate 3 most likely root causes, ordered by probability.
        """)
        return parse_list(response.content)
```

### 2. Learning from Fixes

```python
class LearningDebugger(AutonomousDebugger):
    def __init__(self):
        super().__init__()
        self.fix_database = []

    async def debug(self, error: str, context: dict):
        # Check if we've seen similar errors
        similar_fixes = self._find_similar_errors(error)

        if similar_fixes:
            print(f"📚 Found {len(similar_fixes)} similar past fixes")
            # Try applying similar fixes first
            for fix in similar_fixes:
                if await self._try_fix(fix):
                    return fix

        # Fallback to standard debugging
        result = await super().debug(error, context)

        # Store successful fix
        if result.success:
            self._store_fix(error, result.fix)

        return result
```

### 3. Interactive Mode

```python
class InteractiveDebugger(AutonomousDebugger):
    async def debug_interactive(self, error: str):
        print("🤖 Starting interactive debugging session...")

        while True:
            # Agent proposes action
            action = await self.agent.next_action()

            print(f"\n🤔 Agent proposes: {action}")
            print("Options: [a]pprove, [m]odify, [s]kip, [q]uit")

            choice = input("> ").lower()

            if choice == 'a':
                result = await self.agent.execute(action)
                print(f"Result: {result}")
            elif choice == 'm':
                modified = input("Modified action: ")
                result = await self.agent.execute(modified)
            elif choice == 's':
                continue
            elif choice == 'q':
                break
```

## Testing

```python
def test_simple_fix():
    """Test fixing a simple TypeError"""
    error = "TypeError: unsupported operand type(s) for +: 'int' and 'str'"

    debugger = AutonomousDebugger()
    result = debugger.debug(error, {
        "file": "example.py",
        "line": 10
    })

    assert result.success
    assert "type conversion" in result.fix.lower()

def test_iterative_debugging():
    """Test that agent iterates on failed fixes"""
    debugger = AutonomousDebugger()

    # Track iterations
    iterations = []

    def track_iteration(attempt):
        iterations.append(attempt)

    debugger.on_iteration = track_iteration

    result = debugger.debug(complex_error, context)

    assert len(iterations) > 1  # Should iterate
    assert result.success
```

## Challenges Extra

1. **Multi-File Bugs**: Debug errors spanning multiple files
2. **Performance Issues**: Identify and fix performance bugs
3. **Git Bisect Integration**: Find commit that introduced bug
4. **Explain Fix**: Generate detailed explanation of fix

## Resources
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [ReAct Pattern](https://arxiv.org/abs/2210.03629)
- [Autonomous Agents](https://lilianweng.github.io/posts/2023-06-23-agent/)

**Time**: 8-10h

---

**Debug automáticamente! 🤖**
