# Capstone Option A: AI Code Review Bot

## Project Overview

Build an API that automatically reviews code and provides structured, actionable feedback.

**Complexity**: Medium
**Estimated Time**: 2-2.5 hours

---

## Requirements

### Must Have (Core - 70%)
- [ ] POST `/review` endpoint accepting code + language
- [ ] Returns structured JSON with issues and suggestions
- [ ] Categorizes issues by severity (critical/high/medium/low)
- [ ] Categorizes issues by type (bug/security/performance/style)
- [ ] Handles at least 2 programming languages

### Should Have (Polish - 20%)
- [ ] Helpful error messages for invalid input
- [ ] Rate limiting
- [ ] Logging
- [ ] Health check endpoint

### Nice to Have (Bonus - 10%)
- [ ] GitHub webhook integration
- [ ] Inline comment suggestions with line numbers
- [ ] Batch review multiple files

---

## API Specification

### POST /review

**Request:**
```json
{
  "code": "def add(a, b):\n    return a + b",
  "language": "python",
  "focus": ["security", "performance"]  // optional
}
```

**Response:**
```json
{
  "summary": "The code is simple and functional but lacks type hints and documentation.",
  "issues": [
    {
      "severity": "low",
      "category": "style",
      "line": 1,
      "description": "Function lacks type hints",
      "suggestion": "def add(a: int, b: int) -> int:"
    }
  ],
  "suggestions": [
    "Add docstring explaining the function purpose",
    "Consider adding input validation"
  ],
  "metrics": {
    "overall_score": 7,
    "complexity": "low",
    "maintainability": "good"
  }
}
```

---

## Starter Code

### main.py
```python
"""AI Code Review Bot - Capstone A"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os

app = FastAPI(title="AI Code Review Bot")

class ReviewRequest(BaseModel):
    code: str
    language: str = "python"
    focus: Optional[List[str]] = None

class Issue(BaseModel):
    severity: str
    category: str
    line: Optional[int]
    description: str
    suggestion: str

class ReviewResponse(BaseModel):
    summary: str
    issues: List[Issue]
    suggestions: List[str]
    metrics: dict

# TODO: Implement the review logic
@app.post("/review", response_model=ReviewResponse)
async def review_code(request: ReviewRequest):
    """Review code and return structured feedback."""
    # Your implementation here
    pass

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

### prompts.py
```python
"""Prompts for code review."""

SYSTEM_PROMPT = """You are an expert code reviewer. Analyze code for:
1. Bugs and potential errors
2. Security vulnerabilities
3. Performance issues
4. Style and best practices
5. Maintainability concerns

Return structured JSON with your analysis."""

USER_PROMPT_TEMPLATE = """Review this {language} code:

```{language}
{code}
```

{focus_instruction}

Return JSON matching this schema:
{{
  "summary": "2-3 sentence overview",
  "issues": [
    {{
      "severity": "critical|high|medium|low",
      "category": "bug|security|performance|style|maintainability",
      "line": number or null,
      "description": "clear issue description",
      "suggestion": "specific fix suggestion"
    }}
  ],
  "suggestions": ["general improvement suggestions"],
  "metrics": {{
    "overall_score": 1-10,
    "complexity": "low|medium|high",
    "maintainability": "poor|fair|good|excellent"
  }}
}}"""
```

### llm_client.py
```python
"""LLM client abstraction."""
import os
from anthropic import Anthropic

class LLMClient:
    def __init__(self):
        self.client = Anthropic()
        self.model = "claude-3-5-sonnet-20241022"

    def chat(self, system: str, user: str) -> str:
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
   - Install dependencies
   - Verify API key works

2. **Core Logic** (45 min)
   - Implement `review_code` function
   - Parse LLM response to structured output
   - Handle JSON parsing errors

3. **Multi-language** (15 min)
   - Add language-specific prompt variations
   - Test with Python and JavaScript

4. **Error Handling** (15 min)
   - Input validation
   - LLM error handling
   - Graceful error responses

5. **Deploy** (15 min)
   - Deploy to Railway
   - Set environment variables
   - Verify endpoints work

6. **Demo Prep** (10 min)
   - Prepare sample code to review
   - Plan demo flow

---

## Testing

```bash
# Test with simple Python code
curl -X POST http://localhost:8000/review \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def login(user, password):\n    query = f\"SELECT * FROM users WHERE user={user}\"\n    return db.execute(query)",
    "language": "python"
  }'

# Expected: Should flag SQL injection vulnerability

# Test with JavaScript
curl -X POST http://localhost:8000/review \
  -H "Content-Type: application/json" \
  -d '{
    "code": "const data = JSON.parse(userInput);\neval(data.code);",
    "language": "javascript"
  }'

# Expected: Should flag eval() security issue
```

---

## Evaluation Checklist

- [ ] API endpoint works correctly
- [ ] Returns valid structured JSON
- [ ] Issues are properly categorized
- [ ] Handles multiple languages
- [ ] Error handling works
- [ ] Deployed and accessible
- [ ] Demo ready
