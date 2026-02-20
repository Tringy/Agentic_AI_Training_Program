# Day 2: Advanced Prompting for Engineering

## Learning Objectives

By the end of Day 2, you will be able to:
- Write effective prompts using advanced patterns (CoT, few-shot, self-consistency)
- Design system prompts and personas for different engineering tasks
- Create specialized prompts for code analysis, generation, and review
- Work with multimodal inputs (images, PDFs, documents)
- Build prompts for large-scale migrations and refactoring
- Develop a personal prompt library for engineering tasks

---

## Table of Contents

1. [Prompt Engineering Fundamentals](#fundamentals)
2. [Advanced Prompting Patterns](#advanced-patterns)
3. [System Prompts & Persona Engineering](#system-prompts)
4. [Exercise 1: Prompt Optimization](#exercise-1)
5. [Code-Focused Prompting](#code-prompting)
6. [Multimodal Prompting](#multimodal-prompting)
7. [Migration & Refactoring Prompts](#migration-prompts)
8. [Lab 02: Build Code Analyzer Agent](#lab-02)

---

<a name="fundamentals"></a>
## 1. Prompt Engineering Fundamentals (45 min)

### 1.1 What is Prompt Engineering?

Prompt engineering is the practice of designing inputs to LLMs to get desired outputs. It's the primary way you "program" an LLM.

```
┌─────────────────────────────────────────────────────────────────┐
│                    The Prompt Engineering Stack                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  System Prompt       "You are a senior Python developer..."     │
│       │                                                         │
│       ▼                                                         │
│  Context/Examples    "Here's an example of good code..."        │
│       │                                                         │
│       ▼                                                         │
│  Task Definition     "Refactor the following function to..."    │
│       │                                                         │
│       ▼                                                         │
│  Format Specification "Return as JSON with fields..."           │
│       │                                                         │
│       ▼                                                         │
│  Input               [The actual code/data to process]          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 The RCFG Framework

**RCFG is your systematic approach to writing effective prompts.** Think of it as a recipe for getting consistent, high-quality results from LLMs.

**Why frameworks matter:**
Without structure, prompts are vague → LLM guesses intent → results are inconsistent. With RCFG, you explicitly tell the LLM WHO to be, WHAT context matters, HOW to format output, and WHAT to accomplish.

| Component | Purpose | Example | Why It Matters |
|-----------|---------|---------|----------------|
| **R**ole | Set the persona/expertise | "You are a security-focused code reviewer with 10 years experience" | Influences tone, depth, and priorities |
| **C**ontext | Provide background | "We're migrating a Django 2.x app to Django 4.x for a financial services company" | Helps LLM understand constraints and requirements |
| **F**ormat | Specify output structure | "Return JSON: {'issues': [], 'suggestions': [], 'severity': 'high/medium/low'}" | Ensures parseable, consistent output |
| **G**oal | Define the task | "Identify security vulnerabilities and breaking changes, provide fix recommendations" | Clarifies success criteria |

**Real-world comparison showing RCFG impact:**

**❌ BAD (No Structure):**
```
Review this code for issues.

def calc(x,y):
    return x+y
```

**Result:** Vague response like "This function adds two numbers. Consider adding type hints."
- Not actionable
- Misses context
- Generic advice
- Not formatted for automation

**✅ GOOD (RCFG-Structured):**
```
Role: You are a senior Python developer specializing in clean code and best practices.

Context: This function is part of a financial calculation library where precision
and readability are critical. It will be used by junior developers.

Goal: Review the code and provide:
1. Issues with naming, readability, or best practices
2. Potential bugs or edge cases
3. Specific improvement suggestions

Format: Return your review as:
## Issues
- [list of issues]

## Suggestions
- [list of specific improvements with code examples]

Code to review:
def calc(x,y):
    return x+y
```

### 1.3 Clarity Principles

**Be Specific, Not Vague**

| Vague | Specific |
|-------|----------|
| "Make this better" | "Reduce time complexity from O(n²) to O(n log n)" |
| "Fix the bug" | "Fix the off-by-one error in the loop bounds" |
| "Add comments" | "Add docstrings explaining parameters, return values, and exceptions" |
| "Optimize this" | "Reduce memory usage by avoiding list copies" |

**Use Concrete Examples**

```
Bad: "Format output nicely"

Good: "Format output as:
```json
{
  "status": "success",
  "data": {
    "processed": 150,
    "failed": 3
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```"
```

**Specify Constraints**

```
Bad: "Write a sorting function"

Good: "Write a sorting function that:
- Works on lists of integers
- Sorts in ascending order by default, with optional descending
- Has O(n log n) time complexity
- Is stable (preserves order of equal elements)
- Handles empty lists and single-element lists
- Raises TypeError for non-integer elements"
```

### 1.4 Common Prompting Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| **Ambiguity** | Model guesses intent | Be explicit about requirements |
| **Missing context** | Wrong assumptions | Provide relevant background |
| **No format spec** | Inconsistent output | Define exact output structure |
| **Too much at once** | Confused/incomplete | Break into steps |
| **Assuming knowledge** | Hallucinations | Provide facts, don't expect them |

---

<a name="advanced-patterns"></a>
## 2. Advanced Prompting Patterns (1 hour)

### 2.1 Chain-of-Thought (CoT) Prompting

**What is Chain-of-Thought:** Getting the LLM to "show its work" by reasoning step-by-step before arriving at an answer.

**Why CoT dramatically improves accuracy:**

Without CoT, the LLM tries to jump directly to the answer → makes mistakes on multi-step reasoning.

With CoT, the LLM breaks the problem down → catches its own errors → produces more accurate results.

**Real performance improvements:**
- Math problems: 20% → 80% accuracy (4x improvement)
- Complex reasoning: 35% → 75% accuracy (2x improvement)
- Code debugging: 45% → 85% accuracy (nearly 2x improvement)

**How it works (simplified):**

```
Without CoT:
User: "A store has 15 apples. They sell 8 and get 12 more. How many now?"
LLM: "19 apples" ← May be right or wrong, can't tell how it got there

With CoT:
User: "A store has 15 apples. They sell 8 and get 12 more. How many now?
      Think step by step."
LLM: "Let me work through this:
      1. Start with 15 apples
      2. Sell 8: 15 - 8 = 7 apples remaining
      3. Get 12 more: 7 + 12 = 19 apples
      Answer: 19 apples"
```

**Why showing work matters:**
- ✅ You can **verify the reasoning** (catch errors in logic)
- ✅ LLM **catches its own mistakes** while reasoning
- ✅ More **reliable for complex problems**
- ✅ **Debuggable** when things go wrong

**Basic CoT:**
```
Solve this step by step:

A function receives a list of timestamps and needs to find the longest gap
between consecutive timestamps. The timestamps are not sorted.

Think through each step before writing code.
```

**Structured CoT:**
```
Analyze this algorithm problem step by step:

Problem: Find the longest palindromic substring in a string.

Step 1: Understand the problem
- What is a palindrome?
- What does "longest" mean here?
- What are edge cases?

Step 2: Consider approaches
- What algorithms could solve this?
- What are their time/space complexities?

Step 3: Choose and justify
- Which approach is best and why?

Step 4: Implement
- Write the solution with comments explaining each part.

Step 5: Verify
- Walk through an example
- Check edge cases
```

### 2.2 Few-Shot Prompting

Provide examples to establish patterns:

```
Convert English descriptions to SQL queries.

Example 1:
Description: Get all users who signed up in 2024
SQL: SELECT * FROM users WHERE YEAR(signup_date) = 2024;

Example 2:
Description: Count orders by status
SQL: SELECT status, COUNT(*) as count FROM orders GROUP BY status;

Example 3:
Description: Find the top 5 products by revenue
SQL: SELECT product_id, SUM(quantity * price) as revenue
     FROM order_items
     GROUP BY product_id
     ORDER BY revenue DESC
     LIMIT 5;

Now convert:
Description: Get all active users who have made at least 3 orders
SQL:
```

**Few-Shot for Code Style:**
```
Refactor functions to follow our team's style guide.

Before:
def getData(userID):
    result = db.query(f"SELECT * FROM users WHERE id = {userID}")
    return result

After:
def get_user_data(user_id: int) -> Optional[User]:
    """Fetch user data by ID.

    Args:
        user_id: The unique identifier for the user.

    Returns:
        User object if found, None otherwise.
    """
    return db.query(User).filter(User.id == user_id).first()

---

Before:
def processOrder(o):
    if o.status == "pending":
        o.status = "processing"
        sendEmail(o.user)
        return True
    return False

After:
```

### 2.3 Self-Consistency

Ask the model to verify its own output:

```
Write a function to check if a binary tree is balanced.

After writing the code:
1. Verify the logic is correct by tracing through an example
2. Check for edge cases (empty tree, single node)
3. Confirm the time and space complexity
4. If you find any issues, revise the code
```

**Multi-Pass Verification:**
```
Task: Write a regex to validate email addresses.

Pass 1 - Generate:
Write the regex pattern.

Pass 2 - Test:
Test your regex against these cases:
- valid@example.com (should match)
- invalid@.com (should not match)
- test.name+tag@sub.domain.org (should match)
- @nodomain.com (should not match)

Pass 3 - Revise:
If any tests fail, revise your regex and explain the fix.
```

### 2.4 Tree of Thought

For complex problems, explore multiple approaches:

```
Problem: Design a rate limiter for an API.

Approach 1: Fixed Window
- How it works: [explain]
- Pros: [list]
- Cons: [list]
- Best for: [use cases]

Approach 2: Sliding Window
- How it works: [explain]
- Pros: [list]
- Cons: [list]
- Best for: [use cases]

Approach 3: Token Bucket
- How it works: [explain]
- Pros: [list]
- Cons: [list]
- Best for: [use cases]

Analysis:
Given our requirements (high-traffic API, need fairness across users,
distributed system), which approach is best and why?

Implementation:
Implement the chosen approach in Python.
```

### 2.5 Prompt Chaining

Break complex tasks into steps, using output as input:

```python
# Prompt chain for code review

CHAIN = [
    {
        "name": "understand",
        "prompt": """
Analyze this code and provide:
1. What the code does (1-2 sentences)
2. Key functions/classes and their purposes
3. Dependencies and external calls

Code:
{code}
"""
    },
    {
        "name": "identify_issues",
        "prompt": """
Based on this understanding of the code:
{understanding}

Identify:
1. Bugs or potential bugs
2. Performance issues
3. Security vulnerabilities
4. Code style violations

Original code:
{code}
"""
    },
    {
        "name": "suggest_fixes",
        "prompt": """
For each issue identified:
{issues}

Provide:
1. Specific fix with code
2. Explanation of why this fixes the issue
3. Any trade-offs

Original code for reference:
{code}
"""
    }
]
```

### 2.6 Pattern Quick Reference

```markdown
## Advanced Prompt Patterns Cheatsheet

### Chain-of-Thought (CoT)
Use when: Complex reasoning, math, multi-step logic
Trigger: "Think step by step", "Explain your reasoning"

### Few-Shot
Use when: Specific format/style needed, classification tasks
Structure: 3-5 examples → new input

### Self-Consistency
Use when: High accuracy needed, verifiable outputs
Method: Generate → Verify → Revise

### Tree of Thought
Use when: Design decisions, multiple valid approaches
Structure: List approaches → Analyze → Choose → Implement

### Prompt Chaining
Use when: Complex multi-stage tasks
Method: Break into steps, pass outputs forward
```

---

<a name="system-prompts"></a>
## 3. System Prompts & Persona Engineering (1 hour)

### 3.1 What is a System Prompt?

The system prompt sets the overall behavior, tone, and constraints for the model. It persists across the conversation.

```
┌─────────────────────────────────────────────────────────────────┐
│                     System Prompt Impact                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  System: "You are a helpful assistant"                          │
│  User: "Write a function to delete files"                       │
│  → Generic, may include unsafe patterns                         │
│                                                                 │
│  System: "You are a security-conscious Python developer.        │
│           Always validate inputs, handle errors safely,         │
│           and never use shell=True or eval()."                  │
│  User: "Write a function to delete files"                       │
│  → Includes path validation, error handling, safety checks      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Anatomy of an Effective System Prompt

```markdown
## System Prompt Template

### Identity & Expertise
You are [role] with expertise in [domains].

### Core Behaviors
- Always [positive behaviors]
- Never [negative behaviors/constraints]

### Response Style
- Tone: [professional/casual/technical]
- Length: [concise/detailed]
- Format: [default output format]

### Special Instructions
[Any project-specific rules or context]
```

**Example: Code Review System Prompt**
```
You are a senior software engineer conducting code reviews. You have 15 years
of experience across multiple languages and architectures.

Core behaviors:
- Be constructive and specific in feedback
- Prioritize issues by severity (critical → minor)
- Always explain WHY something is an issue, not just WHAT
- Suggest concrete fixes, not vague improvements
- Acknowledge good practices when you see them

Response format:
1. Summary (1-2 sentences)
2. Critical Issues (must fix)
3. Improvements (should fix)
4. Suggestions (nice to have)
5. Positive Notes (what's done well)

Constraints:
- Don't nitpick style if there's a linter
- Focus on logic, security, and maintainability
- Be respectful—assume the author is competent
```

### 3.3 Persona Engineering for Different Tasks

**Persona: Security Auditor**
```
You are a security auditor specializing in application security. Your task is
to identify vulnerabilities in code.

Focus areas:
- OWASP Top 10 vulnerabilities
- Input validation and sanitization
- Authentication and authorization flaws
- Sensitive data exposure
- Security misconfigurations

For each vulnerability found:
1. Severity: Critical/High/Medium/Low
2. Location: File and line number
3. Description: What the vulnerability is
4. Impact: What could happen if exploited
5. Fix: Specific remediation code

Do not:
- Report style issues unless security-related
- Suggest changes that break functionality
- Miss obvious issues by focusing on edge cases
```

**Persona: API Designer**
```
You are an API designer who creates RESTful APIs following best practices.

Principles you follow:
- RESTful resource naming conventions
- Proper HTTP method usage
- Consistent error response formats
- API versioning strategies
- Rate limiting considerations
- Documentation-first approach

Output format for API designs:
- Endpoint: METHOD /path
- Description: What it does
- Request: Headers, body schema
- Response: Status codes, body schema
- Example: curl command

Always consider:
- Backward compatibility
- Pagination for list endpoints
- Idempotency for mutations
- Authentication requirements
```

**Persona: Legacy Code Archaeologist**
```
You are a software archaeologist specializing in understanding and documenting
legacy code. You approach old code with curiosity, not judgment.

Your approach:
1. Understand before criticizing
2. Document the "why" behind unusual patterns
3. Identify the core business logic
4. Map dependencies and data flows
5. Note technical debt without dramatizing

Output format:
## Code Archaeology Report

### Purpose
What this code does in business terms.

### Architecture
How it's structured and why (probably).

### Key Components
- Component A: [purpose, importance]
- Component B: [purpose, importance]

### Historical Patterns
Patterns that seem outdated but may have reasons:
- [pattern]: Likely because [reason]

### Modernization Opportunities
What could be improved and estimated effort.

### Risks
What could break if this is changed.
```

### 3.4 Context Injection Strategies

**Strategy 1: Documentation Injection**
```
You are a developer working with the FastAPI framework.

Here is the relevant documentation for this task:

---
FastAPI Query Parameters:
Query parameters are declared as function parameters that are not part of
the path parameters. They are automatically validated and documented.

from fastapi import FastAPI, Query

app = FastAPI()

@app.get("/items/")
async def read_items(q: str = Query(default=None, max_length=50)):
    results = {"items": [{"item_id": "Foo"}]}
    if q:
        results.update({"q": q})
    return results
---

Using this documentation, [task]...
```

**Strategy 2: Codebase Patterns**
```
You are working on a codebase with these established patterns:

Error Handling:
```python
class AppError(Exception):
    def __init__(self, message: str, code: str, status: int = 400):
        self.message = message
        self.code = code
        self.status = status
```

Logging:
```python
from app.logging import get_logger
logger = get_logger(__name__)
logger.info("message", extra={"user_id": user_id})
```

Database Access:
```python
from app.db import get_session
async with get_session() as session:
    result = await session.execute(query)
```

Follow these patterns exactly in your code.
```

**Strategy 3: Constraints First**
```
CONSTRAINTS (must follow):
- Python 3.10+ only
- No external dependencies beyond stdlib
- Must handle errors gracefully
- All functions need type hints
- Max function length: 30 lines

PREFERENCES (follow when possible):
- Prefer comprehensions over loops
- Use dataclasses for data structures
- Keep cyclomatic complexity under 10

Now, implement [task]...
```

### 3.5 Exercise: Build a Code Review Persona

Create a system prompt for a code reviewer specific to your typical work:

```markdown
## Your Code Review Persona

### Identity
You are a [your typical tech stack] developer with expertise in [domains].

### Focus Areas (prioritize for your context)
1.
2.
3.
4.

### Your Team's Specific Rules
-
-
-

### Output Format
[Define how you want reviews structured]

### What to Avoid
-
-
```

---

<a name="exercise-1"></a>
## 4. Exercise 1: Prompt Optimization (30 min)

### Objective
Take weak prompts and transform them using the patterns learned.

### Exercise: Improve These Prompts

**Prompt 1: Code Generation (Weak)**
```
Write a cache function.
```

**Your Improved Version:**
```
[Write your improved prompt here]
```

**Prompt 2: Code Review (Weak)**
```
Review this code:

def process(data):
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
    return result
```

**Your Improved Version:**
```
[Write your improved prompt here]
```

**Prompt 3: Debugging (Weak)**
```
This code doesn't work, fix it:

def merge_sorted(a, b):
    result = []
    while a and b:
        if a[0] < b[0]:
            result.append(a.pop())
        else:
            result.append(b.pop())
    return result + a + b
```

**Your Improved Version:**
```
[Write your improved prompt here]
```

### Reference Solutions

<details>
<summary>Click to see example improvements</summary>

**Prompt 1 Improved:**
```
Design and implement a caching function with these requirements:

Functional Requirements:
- Cache function results based on arguments
- Support TTL (time-to-live) expiration
- Handle both sync and async functions
- Work as a decorator

Technical Specifications:
- Python 3.10+
- Thread-safe for concurrent access
- Maximum cache size: configurable
- Eviction policy: LRU when max size reached

Interface:
@cache(ttl=300, max_size=1000)
def expensive_function(x: int) -> int:
    ...

Provide:
1. Implementation with type hints
2. Usage examples
3. Test cases for edge cases
```

**Prompt 2 Improved:**
```
Role: Senior Python developer reviewing code for a production data pipeline.

Context: This function processes financial transaction data where correctness
and performance are critical. The data list can contain millions of items.

Review this code for:
1. Correctness: Does it do what it should?
2. Performance: O(n) is acceptable, but watch for hidden costs
3. Robustness: Error handling, edge cases
4. Readability: Variable names, structure
5. Pythonic style: List comprehensions, built-ins

def process(data):
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
    return result

Format your response as:
## Issues Found
[severity] Issue description → Suggested fix

## Improved Version
[Full improved code with comments]
```

**Prompt 3 Improved:**
```
Debug this merge_sorted function step by step.

Expected behavior: Merge two sorted lists into one sorted list.
Input: [1, 3, 5], [2, 4, 6]
Expected output: [1, 2, 3, 4, 5, 6]

def merge_sorted(a, b):
    result = []
    while a and b:
        if a[0] < b[0]:
            result.append(a.pop())
        else:
            result.append(b.pop())
    return result + a + b

Step 1: Trace the execution
Walk through with input [1, 3, 5], [2, 4, 6] showing the state after each
iteration.

Step 2: Identify bugs
What goes wrong and why?

Step 3: Fix
Provide the corrected code with explanation.

Step 4: Verify
Trace the fixed version with the same input.
```
</details>

---

<a name="code-prompting"></a>
## 5. Code-Focused Prompting (1 hour)

### 5.1 Prompts for Code Analysis

**Understanding Unfamiliar Code:**
```
Analyze this code as if you're onboarding to a new project.

Provide:
1. Purpose: What problem does this solve? (2-3 sentences)
2. Flow: Step-by-step execution walkthrough
3. Dependencies: External libraries/services used
4. Data: What data structures are used and why
5. Edge Cases: What inputs might cause issues
6. Questions: What would you ask the original author?

Code:
[paste code]
```

**Identifying Code Smells:**
```
Identify code smells in this code. For each smell:

1. Name the smell (e.g., "Long Method", "Feature Envy")
2. Location (line numbers or function names)
3. Why it's problematic
4. Refactoring suggestion

Focus on:
- Methods doing too many things
- Inappropriate coupling
- Duplicated logic
- Complex conditionals
- Poor naming

Code:
[paste code]
```

**Complexity Analysis:**
```
Analyze the complexity of this code:

1. Time Complexity
   - Best case: O(?)
   - Average case: O(?)
   - Worst case: O(?)
   - Explain what inputs cause each case

2. Space Complexity
   - Additional space used: O(?)
   - What contributes to space usage

3. Potential Optimizations
   - What could improve complexity?
   - Trade-offs of each optimization

Code:
[paste code]
```

### 5.2 Prompts for Code Generation

**Feature Implementation:**
```
Implement a [feature name] for our [system type].

Requirements:
- [Requirement 1]
- [Requirement 2]
- [Requirement 3]

Constraints:
- Language: [language and version]
- Must integrate with: [existing components]
- Performance: [any requirements]
- Security: [any requirements]

Existing interfaces to use:
```python
# [relevant existing code/interfaces]
```

Provide:
1. Implementation with full type hints
2. Docstrings explaining usage
3. Example usage code
4. Unit test cases
```

**Test Generation:**
```
Generate comprehensive tests for this function:

```python
def calculate_shipping(
    weight_kg: float,
    distance_km: float,
    express: bool = False
) -> float:
    """Calculate shipping cost based on weight, distance, and speed."""
    base_rate = 5.0
    weight_rate = 2.0 * weight_kg
    distance_rate = 0.1 * distance_km

    total = base_rate + weight_rate + distance_rate

    if express:
        total *= 1.5

    return round(total, 2)
```

Generate tests covering:
1. Happy path cases
2. Edge cases (zero values, very large values)
3. Error cases (negative inputs, invalid types)
4. Boundary conditions
5. Business logic verification

Use pytest. Include:
- Descriptive test names
- Arrange/Act/Assert pattern
- Parameterized tests where appropriate
```

### 5.3 Prompts for Code Review

**Security-Focused Review:**
```
Perform a security review of this code:

Check for:
1. Injection vulnerabilities (SQL, command, template)
2. Authentication/authorization issues
3. Sensitive data exposure
4. Input validation gaps
5. Error handling that leaks information
6. Insecure dependencies or configurations

For each finding:
- Severity: Critical/High/Medium/Low
- OWASP category (if applicable)
- Location in code
- Attack scenario
- Remediation with code example

Code:
[paste code]
```

**Performance Review:**
```
Review this code for performance issues:

Environment:
- Expected load: [requests/second or data volume]
- Infrastructure: [relevant details]
- Current response time: [if known]

Analyze:
1. Algorithm efficiency (time complexity)
2. Memory usage patterns
3. Database query optimization opportunities
4. Caching opportunities
5. Concurrency issues
6. I/O bottlenecks

For each issue:
- Impact: High/Medium/Low
- Measurement: How to verify the issue
- Solution: Specific code changes
- Expected improvement: Quantified if possible

Code:
[paste code]
```

### 5.4 Prompts for Debugging

**Systematic Debugging:**
```
Debug this code systematically.

Observed behavior:
[What happens]

Expected behavior:
[What should happen]

Error message (if any):
[Paste error]

Code:
[paste code]

Debugging steps:
1. Reproduce: Identify minimum reproduction case
2. Isolate: Which part of the code causes the issue?
3. Hypothesize: What could cause this behavior?
4. Verify: Test each hypothesis
5. Fix: Implement and verify the solution
```

**Root Cause Analysis:**
```
This bug was reported in production:

Symptoms:
- [Symptom 1]
- [Symptom 2]

Context:
- When it happens: [conditions]
- Frequency: [how often]
- User impact: [what users experience]

Code:
[paste code]

Perform root cause analysis:
1. What is the immediate cause?
2. What is the root cause (why did the immediate cause exist)?
3. What conditions trigger the bug?
4. Why wasn't this caught earlier?
5. How should we fix it?
6. What should we add to prevent similar bugs?
```

### 5.5 Code Prompting Library

<details>
<summary><b>Python</b></summary>

```python
# prompts/code_prompts.py
"""Reusable prompt templates for code tasks."""

ANALYZE_CODE = """
Analyze this code and provide:

1. **Purpose** (2-3 sentences)
   What problem does this solve?

2. **Key Components**
   - Main functions/classes and their roles
   - Important data structures

3. **Flow**
   Step-by-step execution for the main use case.

4. **Dependencies**
   External libraries and why they're used.

5. **Edge Cases**
   Potential inputs that might cause issues.

Code:
```{language}
{code}
```
"""

REVIEW_CODE = """
Review this code as a senior {role} engineer.

Context: {context}

Focus areas:
{focus_areas}

For each issue found:
1. Severity: Critical/High/Medium/Low
2. Location: Line numbers or function names
3. Issue: Clear description
4. Impact: Why this matters
5. Fix: Specific code change

Code:
```{language}
{code}
```
"""

GENERATE_CODE = """
Implement the following:

Task: {task_description}

Requirements:
{requirements}

Constraints:
- Language: {language}
- Style: {style_guide}
- Must integrate with: {integrations}

Provide:
1. Complete implementation with type hints
2. Docstrings for public interfaces
3. Example usage
4. Key design decisions explained
"""

DEBUG_CODE = """
Debug this code:

Observed: {observed}
Expected: {expected}
Error: {error_message}

Code:
```{language}
{code}
```

Steps:
1. Identify the bug location
2. Explain why it occurs
3. Provide the fix
4. Explain how the fix resolves the issue
5. Suggest how to prevent similar bugs
"""

WRITE_TESTS = """
Generate comprehensive tests for:

```{language}
{code}
```

Requirements:
- Framework: {test_framework}
- Coverage: {coverage_requirements}
- Style: {test_style}

Include tests for:
1. Happy path cases
2. Edge cases
3. Error handling
4. Boundary conditions
{additional_test_requirements}
"""
```

</details>

<details>
<summary><b>TypeScript</b></summary>

```typescript
// prompts/code-prompts.ts
/**
 * Reusable prompt templates for code tasks.
 */

export const ANALYZE_CODE = `
Analyze this code and provide:

1. **Purpose** (2-3 sentences)
   What problem does this solve?

2. **Key Components**
   - Main functions/classes and their roles
   - Important data structures

3. **Flow**
   Step-by-step execution for the main use case.

4. **Dependencies**
   External libraries and why they're used.

5. **Edge Cases**
   Potential inputs that might cause issues.

Code:
\`\`\`{language}
{code}
\`\`\`
`;

export const REVIEW_CODE = `
Review this code as a senior {role} engineer.

Context: {context}

Focus areas:
{focus_areas}

For each issue found:
1. Severity: Critical/High/Medium/Low
2. Location: Line numbers or function names
3. Issue: Clear description
4. Impact: Why this matters
5. Fix: Specific code change

Code:
\`\`\`{language}
{code}
\`\`\`
`;

export const GENERATE_CODE = `
Implement the following:

Task: {task_description}

Requirements:
{requirements}

Constraints:
- Language: {language}
- Style: {style_guide}
- Must integrate with: {integrations}

Provide:
1. Complete implementation with type hints
2. Docstrings for public interfaces
3. Example usage
4. Key design decisions explained
`;

export const DEBUG_CODE = `
Debug this code:

Observed: {observed}
Expected: {expected}
Error: {error_message}

Code:
\`\`\`{language}
{code}
\`\`\`

Steps:
1. Identify the bug location
2. Explain why it occurs
3. Provide the fix
4. Explain how the fix resolves the issue
5. Suggest how to prevent similar bugs
`;

export const WRITE_TESTS = `
Generate comprehensive tests for:

\`\`\`{language}
{code}
\`\`\`

Requirements:
- Framework: {test_framework}
- Coverage: {coverage_requirements}
- Style: {test_style}

Include tests for:
1. Happy path cases
2. Edge cases
3. Error handling
4. Boundary conditions
{additional_test_requirements}
`;

// Helper function to fill in template variables
export function fillTemplate(
  template: string,
  variables: Record<string, string>
): string {
  let result = template;
  for (const [key, value] of Object.entries(variables)) {
    result = result.replace(new RegExp(`\\{${key}\\}`, 'g'), value);
  }
  return result;
}

// Usage example
const prompt = fillTemplate(ANALYZE_CODE, {
  language: 'typescript',
  code: 'function add(a: number, b: number) { return a + b; }',
});
````

</details>

### 5.6 Multimodal Prompting (1 hour)

Modern LLMs like Claude 3.5, GPT-4o, and Gemini Pro support multimodal inputs (images, PDFs, audio). This section covers how to prompt effectively with visual and document inputs.

**Why Multimodal Matters:**
- Analyze screenshots of errors or UI
- Process diagrams and architecture drawings
- Extract data from PDFs with tables and images
- Review code from screenshots
- Analyze data visualizations

#### Image Analysis Prompts

**Screenshot Analysis:**
```
You are analyzing a screenshot of an error message.

Please provide:
1. Error identification
   - What is the error type?
   - What is the root cause?
2. Context clues
   - What file/line is affected?
   - What framework/language is this?
3. Solution
   - Specific steps to fix
   - Code changes needed
4. Prevention
   - How to avoid this in the future

[Image: error_screenshot.png]
```

**UI/UX Review:**
```
Analyze this user interface screenshot as a UX expert.

Evaluate:
1. Visual hierarchy and layout
2. Accessibility issues (contrast, sizing, etc.)
3. User flow and interaction patterns
4. Responsive design considerations
5. Specific improvement recommendations with mockup descriptions

[Image: dashboard_ui.png]
```

**Architecture Diagram Analysis:**
```
Analyze this system architecture diagram.

Provide:
1. Component Identification
   - List all components and their purposes
   - Identify the technologies used

2. Data Flow Analysis
   - Trace the flow of data through the system
   - Identify potential bottlenecks

3. Architecture Assessment
   - Strengths of this design
   - Potential issues or anti-patterns
   - Scalability concerns

4. Recommendations
   - Specific improvements
   - Alternative patterns to consider

[Image: system_architecture.png]
```

#### Code from Images

When working with code screenshots (common in Stack Overflow, documentation):

```
Extract and analyze the code from this screenshot.

Steps:
1. Transcribe the code exactly as shown
2. Identify the language and framework
3. Analyze what the code does
4. Identify any issues or bugs
5. Provide an improved version

Important:
- Preserve indentation exactly
- Include all comments
- Note if any text is unclear or cut off

[Image: code_screenshot.png]
```

#### PDF Document Processing

**Technical Documentation:**
```
I've uploaded a PDF of our API documentation (25 pages).

Your task:
1. Extract all endpoint definitions
   - HTTP method and path
   - Parameters (query, body, headers)
   - Response formats
   - Status codes

2. Identify inconsistencies
   - Missing parameter descriptions
   - Undocumented status codes
   - Incomplete examples

3. Generate OpenAPI/Swagger spec
   - Convert to OpenAPI 3.0 format
   - Include all extracted information

[Attached: api_docs.pdf]
```

**Data Extraction from Mixed Content:**
```
This PDF contains tables, charts, and narrative text about our system performance.

Extract and structure:
1. All tables → Convert to CSV/JSON format
2. All charts → Describe data trends and key metrics
3. Text summaries → Key findings and recommendations

Output as structured JSON:
{
  "tables": [...],
  "charts": [...],
  "key_findings": [...]
}

[Attached: performance_report.pdf]
```

#### Best Practices for Multimodal Prompting

**1. Be Specific About What to Focus On:**
```
Bad: "Look at this image"
Good: "In this error screenshot, focus on the stack trace in the terminal window (bottom half of the image) and ignore the code editor shown above."
```

**2. Provide Context:**
```
This is a screenshot of a React application's browser console.
The application is an e-commerce checkout flow.
We're seeing this error during the payment submission step.
Please analyze the error and its likely cause.

[Image: console_error.png]
```

**3. Request Structured Output:**
```
Analyze this UI mockup and provide feedback in this format:

## Positive Aspects
- [List 3-5 things done well]

## Critical Issues
- Issue: [description]
  Location: [where in the image]
  Fix: [specific recommendation]

## Enhancement Suggestions
- [Prioritized list]

[Image: ui_mockup.png]
```

**4. Handle Quality Issues:**
```
This is a photo of a whiteboard from a design session. The image quality is not perfect, and some text may be hard to read.

Please:
1. Transcribe all readable text
2. Describe diagrams and drawings
3. Mark any sections that are unclear with [UNCLEAR: approximate content]
4. Infer the overall design intent

[Image: whiteboard_photo.jpg]
```

#### Multimodal Prompt Library

<details>
<summary><b>Python</b></summary>

```python
# prompts/multimodal_prompts.py
"""Reusable multimodal prompt templates."""

ANALYZE_ERROR_SCREENSHOT = """
Analyze this error screenshot systematically.

1. **Error Identification**
   - Error type and message
   - Stack trace key points
   - Affected files/functions

2. **Context Analysis**
   - What operation was being performed?
   - What framework/language?
   - Any visible configuration or state

3. **Root Cause**
   - Most likely cause
   - Why this error occurred

4. **Solution**
   - Immediate fix steps
   - Code changes needed (be specific)
   - How to verify the fix

5. **Prevention**
   - How to catch this earlier
   - Tests to add
   - Monitoring to implement
"""

EXTRACT_DIAGRAM_INFO = """
Extract structured information from this {diagram_type} diagram.

Output as JSON:
{{
  "components": [
    {{"name": "...", "type": "...", "description": "..."}}
  ],
  "connections": [
    {{"from": "...", "to": "...", "protocol": "...", "description": "..."}}
  ],
  "data_flows": [
    {{"source": "...", "destination": "...", "data_type": "..."}}
  ],
  "notes": ["..."]
}}

Be thorough and include all visible information.
"""

CODE_FROM_IMAGE = """
Extract and improve the code from this image.

Step 1: Transcription
Transcribe the code exactly as shown, preserving:
- Exact indentation
- All comments
- Variable names
- Any visible imports

Step 2: Analysis
- What does this code do?
- What language/framework?
- Any obvious issues?

Step 3: Improvements
Provide an improved version that:
- Fixes any bugs
- Adds error handling
- Improves naming if needed
- Adds type hints (Python) or types (TypeScript)
- Includes helpful comments

Step 4: Explanation
Explain each improvement made and why.
"""

REVIEW_UI_SCREENSHOT = """
Conduct a UX review of this interface screenshot.

Evaluate:

**Visual Design** (Rate 1-5)
- Color scheme and contrast
- Typography and readability
- Spacing and alignment
- Visual hierarchy

**Usability** (Rate 1-5)
- Clarity of actions
- Feedback and affordances
- Error prevention
- Mobile responsiveness (if applicable)

**Accessibility** (Rate 1-5)
- Color contrast ratios
- Touch target sizes
- Screen reader compatibility
- Keyboard navigation

**Specific Issues**
For each issue found:
1. Severity: Critical/High/Medium/Low
2. Location: Describe where in the UI
3. Problem: What's wrong
4. Impact: Who is affected
5. Fix: Specific recommendation with CSS/HTML if needed

**Summary**
- Overall rating: X/15
- Top 3 priorities to fix
"""

ANALYZE_PDF_DOCUMENT = """
Analyze this PDF document and extract key information.

Document type: {doc_type}
Focus areas: {focus_areas}

Extraction requirements:
1. **Structure**
   - Main sections and their hierarchy
   - Page references for important content

2. **Key Information**
   - {specific_info_needed}

3. **Data Tables**
   - Convert all tables to structured format
   - Preserve relationships between data

4. **Action Items**
   - Any TODOs, warnings, or requirements
   - Who is responsible (if mentioned)

5. **Summary**
   - 3-5 bullet point summary
   - Key takeaways for engineers

Output format: {output_format}
"""
```

</details>

<details>
<summary><b>TypeScript</b></summary>

```typescript
// prompts/multimodal-prompts.ts
/**
 * Reusable multimodal prompt templates.
 */

export const ANALYZE_ERROR_SCREENSHOT = `
Analyze this error screenshot systematically.

1. **Error Identification**
   - Error type and message
   - Stack trace key points
   - Affected files/functions

2. **Context Analysis**
   - What operation was being performed?
   - What framework/language?
   - Any visible configuration or state

3. **Root Cause**
   - Most likely cause
   - Why this error occurred

4. **Solution**
   - Immediate fix steps
   - Code changes needed (be specific)
   - How to verify the fix

5. **Prevention**
   - How to catch this earlier
   - Tests to add
   - Monitoring to implement
`;

export const EXTRACT_DIAGRAM_INFO = `
Extract structured information from this {diagram_type} diagram.

Output as JSON:
{
  "components": [
    {"name": "...", "type": "...", "description": "..."}
  ],
  "connections": [
    {"from": "...", "to": "...", "protocol": "...", "description": "..."}
  ],
  "data_flows": [
    {"source": "...", "destination": "...", "data_type": "..."}
  ],
  "notes": ["..."]
}

Be thorough and include all visible information.
`;

export const CODE_FROM_IMAGE = `
Extract and improve the code from this image.

Step 1: Transcription
Transcribe the code exactly as shown, preserving:
- Exact indentation
- All comments
- Variable names
- Any visible imports

Step 2: Analysis
- What does this code do?
- What language/framework?
- Any obvious issues?

Step 3: Improvements
Provide an improved version that:
- Fixes any bugs
- Adds error handling
- Improves naming if needed
- Adds type definitions
- Includes helpful comments

Step 4: Explanation
Explain each improvement made and why.
`;

export const REVIEW_UI_SCREENSHOT = `
Conduct a UX review of this interface screenshot.

Evaluate:

**Visual Design** (Rate 1-5)
- Color scheme and contrast
- Typography and readability
- Spacing and alignment
- Visual hierarchy

**Usability** (Rate 1-5)
- Clarity of actions
- Feedback and affordances
- Error prevention
- Mobile responsiveness (if applicable)

**Accessibility** (Rate 1-5)
- Color contrast ratios
- Touch target sizes
- Screen reader compatibility
- Keyboard navigation

**Specific Issues**
For each issue found:
1. Severity: Critical/High/Medium/Low
2. Location: Describe where in the UI
3. Problem: What's wrong
4. Impact: Who is affected
5. Fix: Specific recommendation with CSS/HTML if needed

**Summary**
- Overall rating: X/15
- Top 3 priorities to fix
`;

export const ANALYZE_PDF_DOCUMENT = `
Analyze this PDF document and extract key information.

Document type: {doc_type}
Focus areas: {focus_areas}

Extraction requirements:
1. **Structure**
   - Main sections and their hierarchy
   - Page references for important content

2. **Key Information**
   - {specific_info_needed}

3. **Data Tables**
   - Convert all tables to structured format
   - Preserve relationships between data

4. **Action Items**
   - Any TODOs, warnings, or requirements
   - Who is responsible (if mentioned)

5. **Summary**
   - 3-5 bullet point summary
   - Key takeaways for engineers

Output format: {output_format}
`;

// Type-safe template filling
interface MultimodalPromptVars {
  diagram_type?: string;
  doc_type?: string;
  focus_areas?: string;
  specific_info_needed?: string;
  output_format?: string;
}

export function fillMultimodalTemplate(
  template: string,
  vars: MultimodalPromptVars
): string {
  let result = template;
  for (const [key, value] of Object.entries(vars)) {
    if (value) {
      result = result.replace(new RegExp(`\\{${key}\\}`, 'g'), value);
    }
  }
  return result;
}
```

</details>

#### Common Pitfalls with Multimodal

| Pitfall | Problem | Solution |
|---------|---------|----------|
| **Low resolution images** | Model can't read text/details | Ensure images are clear, crop to relevant area |
| **No context** | Model guesses wrong | Always explain what the image shows |
| **Assuming OCR perfection** | Model may misread text | Verify transcribed code/text |
| **Overloading** | Multiple images without clear task | One image per focused question, or clear multi-image task |
| **Ignoring format** | Mixed PDF content confuses model | Specify what to extract from PDFs explicitly |

#### Real-World Use Cases

1. **Bug Triage from Screenshots**: Developers share error screenshots in Slack → Analyze and classify automatically
2. **Documentation Review**: Extract API endpoints from PDF specs → Generate Postman collections
3. **UI Audits**: Batch analyze mockups → Generate accessibility reports
4. **Whiteboard to Code**: Photo of design session → Structured requirements document
5. **Log Analysis**: Screenshot of log dashboard → Identify patterns and issues

---

<a name="migration-prompts"></a>
## 6. Migration & Refactoring Prompts (1 hour)

### 6.1 Framework Migration Prompts

**Migration Analysis:**
```
I need to migrate from {old_framework} to {new_framework}.

Current codebase:
- Size: {approximate size}
- Age: {how old}
- Test coverage: {percentage}

Goals:
- [Goal 1]
- [Goal 2]

Constraints:
- [Constraint 1]
- [Constraint 2]

Provide:
1. Migration strategy overview
2. Breaking changes to expect
3. Step-by-step migration order
4. Risk areas and mitigation
5. Estimated effort by component
```

**Example: Django to FastAPI Migration**
```
Analyze this Django view for migration to FastAPI:

```python
from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import User
from .serializers import UserSerializer

@method_decorator(csrf_exempt, name='dispatch')
class UserView(View):
    def get(self, request, user_id=None):
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                return JsonResponse(UserSerializer(user).data)
            except User.DoesNotExist:
                return JsonResponse({'error': 'Not found'}, status=404)
        else:
            users = User.objects.all()
            return JsonResponse(
                {'users': [UserSerializer(u).data for u in users]}
            )

    def post(self, request):
        data = json.loads(request.body)
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            user = User.objects.create(**serializer.validated_data)
            return JsonResponse(UserSerializer(user).data, status=201)
        return JsonResponse(serializer.errors, status=400)
```

Provide:
1. Equivalent FastAPI code
2. Changes needed for:
   - Routing
   - Request/response handling
   - Validation (Pydantic instead of DRF serializers)
   - Database access (async SQLAlchemy)
3. What to watch out for
4. Required dependencies
```

### 6.2 Large-Scale Refactoring Prompts

**Extract Module:**
```
I need to extract a module from this monolithic codebase.

Current state:
- [Describe current structure]
- [Key dependencies]

Target module: {module_name}
Purpose: {what it should do}

The code currently intermixes:
```python
[paste relevant code]
```

Provide:
1. Boundary definition (what belongs in the new module)
2. Interface design (how other code will interact)
3. Step-by-step extraction plan
4. Dependency injection points
5. Migration strategy to avoid breaking changes
```

**Consolidate Duplicate Logic:**
```
Identify and consolidate duplicate logic in these files:

File 1: {name}
```python
{code}
```

File 2: {name}
```python
{code}
```

Provide:
1. Identified duplications with locations
2. Proposed shared abstraction
3. Refactored code
4. How each file would use the shared code
5. Any differences that need parameterization
```

### 6.3 Technical Debt Remediation

**Tech Debt Assessment:**
```
Assess technical debt in this code:

```{language}
{code}
```

Categorize debt by:
1. **Deliberate/Prudent**: Shortcuts taken knowingly for good reasons
2. **Deliberate/Reckless**: Shortcuts taken knowingly, ignoring consequences
3. **Inadvertent/Prudent**: Unknown best practices at time of writing
4. **Inadvertent/Reckless**: Lack of understanding led to poor decisions

For each item:
- Type of debt
- Location
- Impact (maintenance cost, bug risk, performance)
- Remediation effort: Low/Medium/High
- Priority: Fix now / Fix soon / Fix eventually
```

**Incremental Improvement Plan:**
```
Create an incremental improvement plan for this legacy code:

Constraints:
- Cannot do a full rewrite
- Must maintain backward compatibility
- Limited time: {available_time}

Code:
```{language}
{code}
```

Provide:
1. Quick wins (low effort, high impact)
2. Medium-term improvements (moderate effort)
3. Long-term goals (significant effort)

For each improvement:
- What to change
- Why it matters
- How to do it safely
- How to verify it worked
```

### 6.4 Documentation Generation

**Generate API Documentation:**
```
Generate comprehensive API documentation for:

```python
{code}
```

Include:
1. Module/class overview
2. For each public function/method:
   - Purpose
   - Parameters with types and descriptions
   - Return value
   - Exceptions raised
   - Usage examples
3. Common patterns and recipes
4. Gotchas and warnings

Format as Markdown suitable for a README.
```

**Generate Architecture Documentation:**
```
Based on this code, generate architecture documentation:

[paste code or describe system]

Include:
1. System overview diagram (ASCII art)
2. Component descriptions
3. Data flow between components
4. Key design decisions and rationale
5. External integrations
6. Scalability considerations
```

### 6.5 Live Demo: Express to FastAPI Migration

We'll walk through migrating a real Express.js endpoint to FastAPI:

**Original Express.js:**
```javascript
// routes/users.js
const express = require('express');
const router = express.Router();
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const User = require('../models/User');
const auth = require('../middleware/auth');

router.post('/register', async (req, res) => {
    try {
        const { email, password, name } = req.body;

        // Validation
        if (!email || !password) {
            return res.status(400).json({ error: 'Email and password required' });
        }

        // Check existing
        const existingUser = await User.findOne({ email });
        if (existingUser) {
            return res.status(400).json({ error: 'Email already registered' });
        }

        // Create user
        const hashedPassword = await bcrypt.hash(password, 10);
        const user = new User({ email, password: hashedPassword, name });
        await user.save();

        // Generate token
        const token = jwt.sign({ userId: user._id }, process.env.JWT_SECRET, {
            expiresIn: '7d'
        });

        res.status(201).json({ user: { id: user._id, email, name }, token });
    } catch (error) {
        res.status(500).json({ error: 'Server error' });
    }
});

router.get('/me', auth, async (req, res) => {
    const user = await User.findById(req.userId).select('-password');
    res.json(user);
});

module.exports = router;
```

**Migrated FastAPI:**
```python
# routers/users.py
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from passlib.hash import bcrypt
from jose import jwt
from datetime import datetime, timedelta
from typing import Optional
import os

from ..database import get_db
from ..models import User
from ..dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["users"])

# Pydantic models (replacing Joi/manual validation)
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    email: str
    name: Optional[str]

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    user: UserResponse
    token: str

# Routes
@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db = Depends(get_db)):
    # Check existing (validation automatic via Pydantic)
    existing = await db.users.find_one({"email": user_data.email})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user
    hashed_password = bcrypt.hash(user_data.password)
    user_dict = {
        "email": user_data.email,
        "password": hashed_password,
        "name": user_data.name
    }
    result = await db.users.insert_one(user_dict)

    # Generate token
    token = jwt.encode(
        {"userId": str(result.inserted_id), "exp": datetime.utcnow() + timedelta(days=7)},
        os.environ["JWT_SECRET"],
        algorithm="HS256"
    )

    return {
        "user": {"id": str(result.inserted_id), "email": user_data.email, "name": user_data.name},
        "token": token
    }

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
```

**Key Differences Explained:**
| Aspect | Express.js | FastAPI |
|--------|------------|---------|
| Validation | Manual or Joi | Pydantic automatic |
| Type safety | None | Full Python typing |
| Error handling | try/catch + res.status() | HTTPException |
| Auth middleware | Custom middleware | Depends() injection |
| Response format | Manual JSON | response_model |
| Async | async/await | async/await |

---

<a name="lab-02"></a>
## 7. Lab 02: Build Code Analyzer Agent (1h 15min)

### Lab Overview

**Goal:** Build and deploy a code analyzer agent that provides structured analysis of code files.

**Stack:**
- Python with FastAPI
- LLM integration (any provider)
- Deployment to Railway

**What You'll Practice:**
- System prompt engineering
- Structured output extraction
- Building a simple agent

### Lab Instructions

Navigate to `labs/lab02-code-analyzer-agent/` and follow the README.

**Quick Start:**
```bash
cd labs/lab02-code-analyzer-agent
# Read the lab instructions
cat README.md
# Follow steps to build the analyzer
```

### Expected Outcome

By the end of this lab, you should have:
1. A working code analyzer API
2. Custom prompts for different analysis types
3. Structured JSON output
4. Deployment to Railway

---

## Day 2 Summary

### What We Covered
1. **Prompt Fundamentals**: RCFG framework, clarity principles
2. **Advanced Patterns**: CoT, few-shot, self-consistency, tree-of-thought
3. **System Prompts**: Persona engineering, context injection
4. **Code Prompting**: Analysis, generation, review, debugging
5. **Migration Prompts**: Framework migration, refactoring strategies

### Key Takeaways
- Good prompts are specific, structured, and include context
- Use CoT for complex reasoning, few-shot for format matching
- System prompts set behavior; user prompts set tasks
- Different code tasks need different prompting strategies

### Your Prompt Library
By now you should have started building:
- [ ] At least 5 reusable code prompts
- [ ] 2-3 system prompt templates
- [ ] Examples of before/after prompt optimization

### Preparation for Day 3
- Think about what "tools" your agents might need
- Consider a multi-step workflow you'd like to automate
- Review the migration prompts—we'll build on them

---

**Navigation**: [← Day 1](./day1-foundations.md) | [Day 3: Agents →](./day3-agents.md)
