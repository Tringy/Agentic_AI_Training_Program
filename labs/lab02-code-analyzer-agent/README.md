# Lab 02: Code Analyzer Agent

## Objective
Build a code analysis agent that uses LLM to analyze code files and provide structured feedback.

**Time Allotted**: 1 hour 15 minutes

## Learning Goals
- Create effective system prompts for code analysis
- Implement structured output extraction
- Build a simple agent with tool-use
- Deploy to Railway/Vercel

---

## Choose Your Language

| Aspect | Python | TypeScript |
|--------|--------|------------|
| Directory | `./python` | `./typescript` |
| Framework | FastAPI | Hono |
| Validation | Pydantic | Zod |
| Run | `uvicorn main:app --reload` | `npm run dev` |
| Deploy | Railway | Vercel / Railway |

---

## What You'll Build

An API service that:
1. Accepts code via API
2. Analyzes it using an LLM
3. Returns structured JSON with issues and suggestions

```
┌─────────────────────────────────────────────────────────────┐
│                    Code Analyzer Flow                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  POST /analyze                                              │
│    ├── Input: {"code": "...", "language": "python"}         │
│    │                                                        │
│    ├── [System Prompt + Code] → LLM                         │
│    │                                                        │
│    └── Output: {                                            │
│          "summary": "Brief overview",                       │
│          "issues": [                                        │
│            {"severity": "high", "line": 5, "issue": "..."}  │
│          ],                                                 │
│          "suggestions": ["..."],                            │
│          "metrics": {"complexity": "medium", ...}           │
│        }                                                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Quick Start

### Python Setup

```bash
cd python
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set your API key
export ANTHROPIC_API_KEY=your-key
# or: export OPENAI_API_KEY=your-key

# Run
uvicorn main:app --reload
```

### TypeScript Setup

```bash
cd typescript
npm install

# Set your API key
export ANTHROPIC_API_KEY=your-key
# or: export OPENAI_API_KEY=your-key

# Run
npm run dev
```

---

## Step-by-Step Instructions

### Step 1: Create the System Prompt (15 min)

The system prompt instructs the LLM how to analyze code:

<details>
<summary><b>Python</b></summary>

```python
# prompts.py
CODE_ANALYZER_SYSTEM = """You are an expert code reviewer. Analyze the provided code and return a structured analysis.

Your analysis must include:

1. SUMMARY: A 2-3 sentence overview of what the code does and its overall quality.

2. ISSUES: List of problems found, each with:
   - severity: "critical", "high", "medium", or "low"
   - line: line number (if applicable)
   - category: "bug", "security", "performance", "style", "maintainability"
   - description: clear explanation of the issue
   - suggestion: how to fix it

3. SUGGESTIONS: General improvements that aren't bugs.

4. METRICS:
   - complexity: "low", "medium", "high"
   - readability: "poor", "fair", "good", "excellent"
   - test_coverage_estimate: "none", "partial", "good"

Return your response as valid JSON."""
```

</details>

<details>
<summary><b>TypeScript</b></summary>

```typescript
// prompts.ts
export const CODE_ANALYZER_SYSTEM = `You are an expert code reviewer. Analyze the provided code and return a structured analysis.

Your analysis must include:

1. SUMMARY: A 2-3 sentence overview of what the code does and its overall quality.

2. ISSUES: List of problems found, each with:
   - severity: "critical", "high", "medium", or "low"
   - line: line number (if applicable)
   - category: "bug", "security", "performance", "style", "maintainability"
   - description: clear explanation of the issue
   - suggestion: how to fix it

3. SUGGESTIONS: General improvements that aren't bugs.

4. METRICS:
   - complexity: "low", "medium", "high"
   - readability: "poor", "fair", "good", "excellent"
   - test_coverage_estimate: "none", "partial", "good"

Return your response as valid JSON.`;
```

</details>

### Step 2: Define Data Types (10 min)

<details>
<summary><b>Python (Pydantic)</b></summary>

```python
# analyzer.py
from typing import Optional, List
from pydantic import BaseModel

class Issue(BaseModel):
    severity: str
    line: Optional[int] = None
    category: str
    description: str
    suggestion: str

class Metrics(BaseModel):
    complexity: str
    readability: str
    test_coverage_estimate: str

class AnalysisResult(BaseModel):
    summary: str
    issues: List[Issue]
    suggestions: List[str]
    metrics: Metrics
```

</details>

<details>
<summary><b>TypeScript (Zod)</b></summary>

```typescript
// types.ts
import { z } from 'zod';

export const IssueSchema = z.object({
  severity: z.enum(['critical', 'high', 'medium', 'low']),
  line: z.number().nullable(),
  category: z.enum(['bug', 'security', 'performance', 'style', 'maintainability']),
  description: z.string(),
  suggestion: z.string(),
});

export const MetricsSchema = z.object({
  complexity: z.enum(['low', 'medium', 'high']),
  readability: z.enum(['poor', 'fair', 'good', 'excellent']),
  test_coverage_estimate: z.enum(['none', 'partial', 'good']),
});

export const AnalysisResultSchema = z.object({
  summary: z.string(),
  issues: z.array(IssueSchema),
  suggestions: z.array(z.string()),
  metrics: MetricsSchema,
});

export type AnalysisResult = z.infer<typeof AnalysisResultSchema>;
```

</details>

### Step 3: Implement the Analyzer (20 min)

<details>
<summary><b>Python</b></summary>

```python
# analyzer.py
import json
from prompts import CODE_ANALYZER_SYSTEM

class CodeAnalyzer:
    def __init__(self, llm_client):
        self.llm = llm_client
        self.system_prompt = CODE_ANALYZER_SYSTEM

    def analyze(self, code: str, language: str = "python") -> AnalysisResult:
        user_prompt = f"""Analyze this {language} code:

```{language}
{code}
```

Return your analysis as JSON."""

        response = self.llm.chat([
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_prompt}
        ])

        return self._parse_response(response)

    def _parse_response(self, response: str) -> AnalysisResult:
        # Handle markdown code blocks
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0]
        data = json.loads(response.strip())
        return AnalysisResult(**data)
```

</details>

<details>
<summary><b>TypeScript</b></summary>

```typescript
// analyzer.ts
import type { LLMClient } from './llm-client.js';
import { AnalysisResultSchema, type AnalysisResult } from './types.js';
import { CODE_ANALYZER_SYSTEM } from './prompts.js';

export class CodeAnalyzer {
  private llm: LLMClient;
  private systemPrompt: string;

  constructor(llmClient: LLMClient) {
    this.llm = llmClient;
    this.systemPrompt = CODE_ANALYZER_SYSTEM;
  }

  async analyze(code: string, language: string = 'python'): Promise<AnalysisResult> {
    const userPrompt = `Analyze this ${language} code:

\`\`\`${language}
${code}
\`\`\`

Return your analysis as JSON.`;

    const response = await this.llm.chat([
      { role: 'system', content: this.systemPrompt },
      { role: 'user', content: userPrompt },
    ]);

    return this.parseResponse(response);
  }

  private parseResponse(response: string): AnalysisResult {
    let jsonStr = response;
    if (jsonStr.includes('```json')) {
      jsonStr = jsonStr.split('```json')[1].split('```')[0];
    }
    const data = JSON.parse(jsonStr.trim());
    return AnalysisResultSchema.parse(data);  // Validates with Zod
  }
}
```

</details>

### Step 4: Build the API (15 min)

<details>
<summary><b>Python (FastAPI)</b></summary>

```python
# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from analyzer import CodeAnalyzer, AnalysisResult
from llm_client import get_llm_client

app = FastAPI(title="Code Analyzer Agent")

class AnalyzeRequest(BaseModel):
    code: str
    language: str = "python"

llm = get_llm_client("anthropic")
analyzer = CodeAnalyzer(llm)

@app.post("/analyze", response_model=AnalysisResult)
async def analyze_code(request: AnalyzeRequest):
    try:
        return analyzer.analyze(request.code, request.language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

</details>

<details>
<summary><b>TypeScript (Hono)</b></summary>

```typescript
// index.ts
import { Hono } from 'hono';
import { zValidator } from '@hono/zod-validator';
import { z } from 'zod';
import { CodeAnalyzer } from './analyzer.js';
import { getLLMClient } from './llm-client.js';

const app = new Hono();

const AnalyzeRequestSchema = z.object({
  code: z.string().min(1),
  language: z.string().default('python'),
});

const llm = getLLMClient('anthropic');
const analyzer = new CodeAnalyzer(llm);

app.post('/analyze', zValidator('json', AnalyzeRequestSchema), async (c) => {
  try {
    const { code, language } = c.req.valid('json');
    const result = await analyzer.analyze(code, language);
    return c.json(result);
  } catch (error) {
    return c.json({ error: error.message }, 500);
  }
});

app.get('/health', (c) => c.json({ status: 'healthy' }));

export default app;
```

</details>

### Step 5: Test Locally (10 min)

```bash
# Test with sample code
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def add(a,b):\n    return a+b\n\ndef process(data):\n    result=[]\n    for i in range(len(data)):\n        if data[i]>0:\n            result.append(data[i]*2)\n    return result",
    "language": "python"
  }'
```

### Step 6: Deploy

<details>
<summary><b>Python (Railway)</b></summary>

```bash
cd python

# Create Procfile
echo "web: uvicorn main:app --host 0.0.0.0 --port \$PORT" > Procfile

# Initialize and deploy
railway init
railway variables set ANTHROPIC_API_KEY=your_key
railway up
```

</details>

<details>
<summary><b>TypeScript (Vercel)</b></summary>

```bash
cd typescript

# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Set environment variable in Vercel dashboard
# ANTHROPIC_API_KEY=your_key
```

</details>

---

## Project Structure

```
lab02-code-analyzer-agent/
├── README.md                 # This file
├── python/
│   ├── main.py              # FastAPI application
│   ├── analyzer.py          # CodeAnalyzer class
│   ├── prompts.py           # System prompts
│   ├── llm_client.py        # LLM client abstraction
│   └── requirements.txt
└── typescript/
    ├── src/
    │   ├── index.ts         # Hono application
    │   ├── analyzer.ts      # CodeAnalyzer class
    │   ├── prompts.ts       # System prompts
    │   ├── llm-client.ts    # LLM client abstraction
    │   └── types.ts         # Zod schemas
    ├── package.json
    └── tsconfig.json
```

---

## Deliverables

- [ ] Working code analyzer API (Python OR TypeScript)
- [ ] Custom system prompt for analysis
- [ ] Structured JSON output
- [ ] At least 2 analysis types (general + security OR performance)
- [ ] Deployed to Railway/Vercel
- [ ] Tested with sample code

---

## Extension Challenges

1. **Multi-file Analysis**: Accept multiple files and analyze relationships
2. **Diff Analysis**: Analyze code changes between two versions
3. **Language Detection**: Auto-detect programming language
4. **Caching**: Cache results for identical code

---

**Next**: [Lab 03 - Migration Workflow Agent](../lab03-migration-workflow/)
