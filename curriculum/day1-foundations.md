# Day 1: GenAI Foundations & AI-First Engineering

## Learning Objectives

By the end of Day 1, you will be able to:
- Explain how Large Language Models work at a practical level
- Identify the strengths, limitations, and appropriate use cases for different LLMs
- Apply "Vibe Coding" and AI-first development methodologies
- Select and configure AI coding tools for your workflow
- Build and deploy your first AI-assisted application

---

## Table of Contents

1. [Welcome & Setup](#welcome)
2. [LLM Fundamentals](#llm-fundamentals)
3. [Model Behavior & Constraints](#model-behavior)
4. [Exercise 1: Model Comparison](#exercise-1)
5. [Vibe Coding & AI-First Development](#vibe-coding)
6. [Tool Landscape](#tool-landscape)
7. [Lab 01: Build First AI-Assisted App](#lab-01)

---

<a name="welcome"></a>
## 1. Welcome & Program Overview (30 min)

### What This Program Is

This is an **intensive, engineering-focused** training program designed to make you productive in agentic AI projects within one week. We emphasize:

- **Practical skills** over theoretical depth
- **Production patterns** over toy examples
- **LLM-agnostic approaches** that work across providers
- **Real deployments** on every lab

### What You'll Build This Week

```
Day 1: URL Shortener (AI-assisted full-stack)
Day 2: Code Analyzer Agent
Day 3: Migration Workflow Agent
Day 4: RAG System with Evaluation
Day 5: Capstone Project (your choice)
```

### Environment Setup Verification

Run the verification script to check your setup:

```bash
# Verify all environments (Python + TypeScript)
./scripts/verify-setup.sh

# Verify Python only
./scripts/verify-setup.sh python

# Verify TypeScript only
./scripts/verify-setup.sh typescript
```

The script will check:
- **Python**: version 3.10+, pip, packages (openai, anthropic, fastapi, etc.)
- **TypeScript**: Node.js 18+, npm, packages (@anthropic-ai/sdk, openai, hono, etc.)
- **API Keys**: ANTHROPIC_API_KEY, OPENAI_API_KEY, GOOGLE_API_KEY
- **Tools**: git, curl, deployment CLIs

Example output:
```
=== Python Environment ===

✓ Python 3.11.5
✓ pip 23.2.1
✓ Virtual environment active: .venv

Python Packages:
✓ openai (1.12.0)
✓ anthropic (0.18.1)
✓ fastapi (0.109.0)
...

=== Summary ===

Passed: 12
Failed: 0
Warnings: 3

============================================
  All required checks passed! Ready to go.
============================================
```

---

<a name="llm-fundamentals"></a>
## 2. LLM Fundamentals (1 hour)

### 2.1 What is a Large Language Model?

An LLM is a neural network trained to predict the next token in a sequence. Despite this simple objective, scale and training data have produced **emergent capabilities**—abilities that weren't explicitly programmed but emerged from the training process.

**What does "emergent capabilities" mean?**
Think of it like learning to ride a bike: you practice balancing, pedaling, and steering separately, but at some point, these skills combine and you can suddenly *ride*. Similarly, LLMs trained on massive text datasets develop unexpected abilities like:
- **Reasoning**: Breaking down complex problems step-by-step
- **Code generation**: Writing functional programs in multiple languages
- **Translation**: Converting between languages they've seen
- **Few-shot learning**: Understanding new tasks from just a few examples
- **Chain-of-thought**: Explaining their reasoning process

These capabilities weren't explicitly taught—they emerged from patterns in the training data.

```
┌─────────────────────────────────────────────────────────────────┐
│                    How LLMs Generate Text                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Input: "The capital of France is"                              │
│                                                                 │
│  ┌──────────┐    ┌──────────────┐    ┌─────────────────────┐   │
│  │ Tokenize │───▶│   Process    │───▶│ Probability over    │   │
│  │          │    │  (Attention) │    │ all tokens          │   │
│  └──────────┘    └──────────────┘    └─────────────────────┘   │
│                                              │                  │
│  Tokens:                            "Paris": 0.92               │
│  ["The", "capital",                 "Lyon": 0.03                │
│   "of", "France", "is"]             "Berlin": 0.01              │
│                                     ...                         │
│                                              │                  │
│                                              ▼                  │
│                                     Sample: "Paris"             │
│                                                                 │
│  Output: "The capital of France is Paris"                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Tokens: The Atomic Unit

LLMs don't see characters or words—they see **tokens**. Think of tokens as the "atoms" of text that LLMs process.

**Why tokens matter in practice:**
- **Cost estimation**: API pricing is per token ($3-15 per million tokens). A 10,000-word document = ~13,000 tokens = $0.04-0.20 to process
- **Context limits**: Models have token limits (128K-1M tokens). Need to fit your prompt, conversation history, AND response within this budget
- **Performance**: More tokens = slower response and higher latency
- **Unexpected behavior**: Token boundaries can split words unexpectedly, causing issues with rare words or code

**Real-world impact example:**
- Your app lets users paste documents. A user pastes a 50-page PDF (15,000 words ≈ 20,000 tokens)
- At $3/million tokens input + $15/million output, this single request costs: $0.06 input + $0.30 output (2,000 token response) = $0.36
- If 1,000 users do this monthly: $360/month just for this feature
- **This is why understanding tokens is critical for building production AI apps.**

<details>
<summary><b>Python</b></summary>

```python
# Token counting example (works with any tiktoken-compatible model)
import tiktoken

def count_tokens(text: str, model: str = "gpt-4") -> int:
    """Count tokens for a given text."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

# Examples
examples = [
    "Hello, world!",
    "def fibonacci(n): return n if n < 2 else fibonacci(n-1) + fibonacci(n-2)",
    "The quick brown fox jumps over the lazy dog.",
    "supercalifragilisticexpialidocious",
]

for text in examples:
    tokens = count_tokens(text)
    ratio = len(text) / tokens
    print(f"{tokens:3d} tokens | {len(text):3d} chars | ratio: {ratio:.1f} | {text[:50]}...")
```

</details>

<details>
<summary><b>TypeScript</b></summary>

```typescript
// Token counting example using gpt-tokenizer
import { encode } from 'gpt-tokenizer';

function countTokens(text: string): number {
  return encode(text).length;
}

// Examples
const examples = [
  'Hello, world!',
  'def fibonacci(n): return n if n < 2 else fibonacci(n-1) + fibonacci(n-2)',
  'The quick brown fox jumps over the lazy dog.',
  'supercalifragilisticexpialidocious',
];

for (const text of examples) {
  const tokens = countTokens(text);
  const ratio = text.length / tokens;
  console.log(`${tokens.toString().padStart(3)} tokens | ${text.length.toString().padStart(3)} chars | ratio: ${ratio.toFixed(1)} | ${text.slice(0, 50)}...`);
}
```

</details>

**Token Rules of Thumb:**
- English: ~4 characters per token
- Code: ~3 characters per token (more symbols)
- Other languages: varies widely (can be 1-2 chars/token for CJK)

### 2.3 Context Windows

The context window is the total tokens the model can "see" at once (input + output). Think of it as the model's "working memory" or "attention span."

**What fits in a context window:**
- 128K tokens ≈ 96,000 words ≈ a 300-page novel
- 200K tokens ≈ 150,000 words ≈ a 500-page technical book
- 1M tokens ≈ 750,000 words ≈ entire Lord of the Rings trilogy

| Model | Context Window | Approx. Pages | What You Can Fit |
|-------|---------------|---------------|------------------|
| GPT-4o | 128K | ~300 pages | Small codebase, documentation site |
| Claude 3.5 Sonnet | 200K | ~500 pages | Medium codebase, multiple docs |
| Gemini 1.5 Pro | 1M+ | ~2,500 pages | Entire repository, large datasets |
| GPT-4 Turbo | 128K | ~300 pages | Small codebase, documentation site |

**Practical Implications & Real Examples:**

**1. What you can include:**
- ✅ **128K**: Include 5-10 relevant code files + conversation history + response
- ✅ **200K**: Include entire API documentation + user's code + conversation
- ✅ **1M**: Include entire codebase for analysis + conversation history

**2. Cost implications:**
```
Example: Processing a large document
- 100K token input × $3/MTok = $0.30 per request
- User asks 10 questions: $3.00
- 1,000 users: $3,000/month just for input
- **Context size directly impacts your costs**
```

**3. The "Lost in the Middle" problem:**
Even with huge context windows, models pay less attention to middle sections:
```
┌─────────────────────────────────┐
│ BEGINNING: Strong attention ✓   │  ← Model focuses here
├─────────────────────────────────┤
│ MIDDLE: Weak attention ⚠️        │  ← Often missed!
├─────────────────────────────────┤
│ END: Strong attention ✓          │  ← Model focuses here
└─────────────────────────────────┘
```

**Best practices:**
- ✅ Put critical info at the **beginning and end** of your prompt
- ✅ Use **clear section headers** to help model navigate
- ✅ Include **only relevant context** (more ≠ better)
- ❌ Don't dump entire codebase if you only need 3 files

**Real-world tradeoff:**
- **Option A**: Send entire 50-file codebase (100K tokens) → Higher cost, slower, potential attention issues
- **Option B**: Send only 3 relevant files (10K tokens) → 90% cheaper, faster, better focus
- **Best practice**: Use RAG or file selection to send only what's needed

### 2.4 Key Parameters

#### Temperature
Controls randomness in output. Range: 0.0 to 2.0 (typically 0.0 to 1.0)

```
Temperature 0.0: Deterministic, always picks highest probability
Temperature 0.7: Balanced creativity and coherence (default)
Temperature 1.0+: More creative/random, can be incoherent
```

**Guidelines:**
- Code generation: 0.0-0.3 (want consistency)
- Creative writing: 0.7-0.9
- Brainstorming: 0.8-1.0
- Factual Q&A: 0.0-0.2

#### Top-p (Nucleus Sampling)
Alternative to temperature. Considers only tokens whose cumulative probability reaches p.

```
Top-p 0.1: Very focused, only most likely tokens
Top-p 0.9: Considers wider range of possibilities
Top-p 1.0: Considers all tokens
```

**Best Practice:** Use temperature OR top-p, not both at extreme values.

### 2.5 Model Comparison Overview

**How to choose the right model for your use case:**

| Aspect | Claude 3.5 Sonnet | GPT-4o | Gemini 1.5 Pro |
|--------|-------------------|--------|----------------|
| **Strengths** | Reasoning, safety, long context | Broad capabilities, vision | Speed, multimodal, huge context |
| **Code Quality** | Excellent (9/10) | Excellent (9/10) | Very Good (8/10) |
| **Speed** | Fast (~2-3s) | Fast (~2-3s) | Very Fast (~1-2s) |
| **Context** | 200K | 128K | 1M+ |
| **Cost** | $3/$15 per 1M tokens | $5/$15 per 1M tokens | $1.25/$5 per 1M tokens |
| **Best For** | Complex reasoning, code review | General purpose, function calling | Large codebases, multimodal |

**Real-world cost comparison:**
```
Scenario: Customer support bot (1,000 conversations/day, avg 2K tokens input + 500 tokens output)

Claude 3.5 Sonnet:
- Input: 2M tokens × $3 = $6.00
- Output: 500K tokens × $15 = $7.50
- Total: $13.50/day = $405/month

GPT-4o:
- Input: 2M tokens × $5 = $10.00
- Output: 500K tokens × $15 = $7.50
- Total: $17.50/day = $525/month

Gemini 1.5 Pro:
- Input: 2M tokens × $1.25 = $2.50
- Output: 500K tokens × $5 = $2.50
- Total: $5.00/day = $150/month

Savings: Gemini is 73% cheaper than Claude, 79% cheaper than GPT-4o
```

**Decision framework:**

**Choose Claude 3.5 Sonnet when:**
- ✅ Code quality is critical (code review, generation, refactoring)
- ✅ Need deep reasoning (complex problem-solving, analysis)
- ✅ Safety/reliability is paramount (medical, legal, financial)
- ✅ Need 200K context (analyzing large documents)
- 💰 Budget: Mid-range

**Choose GPT-4o when:**
- ✅ Need strong function calling (agents, tool use)
- ✅ Want ecosystem compatibility (most tutorials use OpenAI)
- ✅ Multimodal needs (vision capabilities)
- ✅ General-purpose, balanced performance
- 💰 Budget: Mid-range

**Choose Gemini 1.5 Pro when:**
- ✅ Processing huge documents (1M+ token context)
- ✅ Speed is critical (fastest inference)
- ✅ Cost optimization is priority (cheapest)
- ✅ Multimodal at scale (images, video)
- 💰 Budget: Cost-conscious

**Model selection strategy:**
1. **Start with Claude 3.5 Sonnet** for development (best balance of quality/cost)
2. **A/B test** with GPT-4o and Gemini for your specific use case
3. **Measure** quality, speed, and cost in production
4. **Optimize** by routing tasks to appropriate models:
   - Simple queries → Haiku/3.5-turbo (cheaper)
   - Complex reasoning → Sonnet/GPT-4o (better quality)
   - Huge context → Gemini (1M+ tokens)

### 2.6 API Basics (LLM-Agnostic Pattern)

Here's a pattern that works across all major providers:

<details>
<summary><b>Python</b></summary>

```python
# utils/llm_client.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import os

class LLMClient(ABC):
    """Abstract base class for LLM clients."""

    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Send a chat completion request."""
        pass

class OpenAIClient(LLMClient):
    def __init__(self, model: str = "gpt-4o"):
        from openai import OpenAI
        self.client = OpenAI()
        self.model = model

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            **kwargs
        )
        return response.choices[0].message.content

class AnthropicClient(LLMClient):
    def __init__(self, model: str = "claude-3-5-sonnet-20241022"):
        from anthropic import Anthropic
        self.client = Anthropic()
        self.model = model

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        # Anthropic uses 'system' separately
        system = None
        filtered_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system = msg["content"]
            else:
                filtered_messages.append(msg)

        response = self.client.messages.create(
            model=self.model,
            max_tokens=kwargs.get("max_tokens", 4096),
            system=system,
            messages=filtered_messages
        )
        return response.content[0].text

def get_llm_client(provider: str = "anthropic") -> LLMClient:
    """Factory function to get the appropriate LLM client."""
    providers = {
        "openai": OpenAIClient,
        "anthropic": AnthropicClient,
    }

    if provider not in providers:
        raise ValueError(f"Unknown provider: {provider}. Choose from: {list(providers.keys())}")

    return providers[provider]()

# Usage example
if __name__ == "__main__":
    client = get_llm_client("anthropic")  # or "openai"

    messages = [
        {"role": "system", "content": "You are a helpful coding assistant."},
        {"role": "user", "content": "Write a function to reverse a string."}
    ]

    response = client.chat(messages)
    print(response)
```

</details>

<details>
<summary><b>TypeScript</b></summary>

```typescript
// utils/llm-client.ts
import Anthropic from '@anthropic-ai/sdk';
import OpenAI from 'openai';

export interface Message {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

export abstract class LLMClient {
  abstract chat(messages: Message[]): Promise<string>;
}

export class OpenAIClient extends LLMClient {
  private client: OpenAI;
  private model: string;

  constructor(model: string = 'gpt-4o') {
    super();
    this.client = new OpenAI();
    this.model = model;
  }

  async chat(messages: Message[]): Promise<string> {
    const response = await this.client.chat.completions.create({
      model: this.model,
      messages,
    });
    return response.choices[0].message.content || '';
  }
}

export class AnthropicClient extends LLMClient {
  private client: Anthropic;
  private model: string;

  constructor(model: string = 'claude-3-5-sonnet-20241022') {
    super();
    this.client = new Anthropic();
    this.model = model;
  }

  async chat(messages: Message[]): Promise<string> {
    // Anthropic uses 'system' separately
    let system: string | undefined;
    const filtered: Array<{ role: 'user' | 'assistant'; content: string }> = [];

    for (const msg of messages) {
      if (msg.role === 'system') {
        system = msg.content;
      } else {
        filtered.push({ role: msg.role, content: msg.content });
      }
    }

    const response = await this.client.messages.create({
      model: this.model,
      max_tokens: 4096,
      system,
      messages: filtered,
    });

    const textBlock = response.content.find((block) => block.type === 'text');
    return textBlock?.type === 'text' ? textBlock.text : '';
  }
}

export type LLMProvider = 'anthropic' | 'openai';

export function getLLMClient(provider: LLMProvider = 'anthropic'): LLMClient {
  switch (provider) {
    case 'anthropic':
      return new AnthropicClient();
    case 'openai':
      return new OpenAIClient();
    default:
      throw new Error(`Unknown provider: ${provider}`);
  }
}

// Usage example
async function main() {
  const client = getLLMClient('anthropic'); // or 'openai'

  const messages: Message[] = [
    { role: 'system', content: 'You are a helpful coding assistant.' },
    { role: 'user', content: 'Write a function to reverse a string.' },
  ];

  const response = await client.chat(messages);
  console.log(response);
}

main();
```

</details>

---

<a name="model-behavior"></a>
## 3. Model Behavior & Constraints (1 hour)

### 3.1 How Models "Reason"

LLMs don't truly reason—they pattern match at massive scale. This has implications:

**What LLMs Do Well:**
- Pattern completion based on training data
- Following structured formats
- Combining concepts in novel ways
- Code generation for common patterns

**What LLMs Struggle With:**
- True logical deduction
- Counting and arithmetic (improving with newer models)
- Maintaining state across long contexts
- Tasks requiring world state knowledge

```python
# Demonstration: Where reasoning breaks down
prompts_that_fool_llms = [
    # Counting challenge
    "How many 'r's are in 'strawberry'?",  # Often gets wrong

    # Logic puzzle with twist
    "A bat and ball cost $1.10 total. The bat costs $1 more than the ball. How much does the ball cost?",

    # Temporal reasoning
    "If I put a book on the table, then put a cup on the book, then remove the book, where is the cup?",
]
```

### 3.2 Hallucinations

Hallucinations are confident-sounding but incorrect outputs. They're one of the most critical issues in production AI systems.

**Why hallucinations occur:**
- **Pattern completion over truth**: The model is trained to predict plausible next tokens, not to verify facts. If it's seen similar patterns in training, it will continue them—even if false
- **Confidence without knowledge**: Models can't distinguish between things they "know" (saw in training) vs. things they're guessing
- **Interpolation**: When asked about something new, models blend patterns from training data, creating plausible but false information

**Real-world hallucination examples:**
1. **API Hallucination**: Asked to use a Python library, the model invents `library.nonexistent_function()` that sounds plausible but doesn't exist. Your code breaks in production.
2. **Fact Hallucination**: Asked "When did Python 4.0 release?", it confidently states "Python 4.0 was released in 2022" (it doesn't exist yet).
3. **Citation Hallucination**: Asked for sources, it invents realistic-looking research papers with fake DOIs and author names that don't exist.
4. **Code Hallucination**: Generates SQL queries that look correct but contain syntax errors or reference non-existent columns.

**Business impact:**
- Customer support bot gives wrong product information → lost sales, angry customers
- Code generation tool creates broken code → developer trust erodes, productivity drops
- Legal document analysis makes up case law → severe legal liability

This is why **verification, testing, and RAG** (grounding in real data) are essential in production systems.

**Types of Hallucinations:**

| Type | Example | Mitigation |
|------|---------|------------|
| **Factual** | Incorrect dates, names, stats | RAG, verification prompts |
| **Code** | Non-existent APIs/functions | Testing, documentation reference |
| **Citation** | Made-up references | Explicit "cite only real sources" |
| **Logical** | Invalid reasoning steps | Chain-of-thought, verification |

**Hallucination Mitigation Strategies:**

```python
# Strategy 1: Explicit uncertainty acknowledgment
UNCERTAINTY_PROMPT = """
If you're not certain about something, say so explicitly.
Use phrases like "I believe", "I'm not certain", or "You should verify this".
Never make up information.
"""

# Strategy 2: Verification chain
VERIFICATION_PROMPT = """
After providing your answer, add a "Verification" section where you:
1. List any facts that should be verified
2. Note any assumptions you made
3. Suggest how to validate your response
"""

# Strategy 3: Grounding with context
def grounded_query(question: str, context: str) -> str:
    return f"""
Answer the following question using ONLY the provided context.
If the context doesn't contain the answer, say "I cannot find this in the provided context."

Context:
{context}

Question: {question}
"""
```

### 3.3 Context Window Limitations

Even with large context windows, performance degrades:

```
┌─────────────────────────────────────────────────────────────────┐
│              Attention Pattern in Long Contexts                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Attention Strength                                             │
│  █████████                                                      │
│  ████████  ←── Beginning (strong)                               │
│  ███████                                                        │
│  ██████                                                         │
│  █████                                                          │
│  ████     ←── Middle (weakest - "lost in the middle")           │
│  ████                                                           │
│  █████                                                          │
│  ██████                                                         │
│  ███████                                                        │
│  ████████ ←── End (strong, recency bias)                        │
│  █████████                                                      │
│                                                                 │
│  Position in Context ──────────────────────────────────────▶    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Best Practices for Long Context:**
1. Put critical information at the beginning AND end
2. Use clear section headers
3. Summarize key points before asking questions
4. For code: include relevant files, not entire codebase

### 3.4 Safety Boundaries and Refusals

Models have built-in safety filters that sometimes trigger unexpectedly:

**Common Refusal Triggers:**
- Security-related code (even legitimate)
- Content that could be misused
- Requests that seem to bypass guidelines

**Working with Refusals:**

```python
# Bad: Vague request that might trigger safety
bad_prompt = "How do I hack into a system?"

# Good: Clear, legitimate context
good_prompt = """
I'm a security engineer conducting authorized penetration testing on our company's
web application. I need to test for SQL injection vulnerabilities.

Can you show me common SQL injection patterns I should test for, and how to
properly parameterize queries to prevent them?
"""

# Best: Include explicit authorization context
best_prompt = """
Context: I'm writing a security scanning tool for our internal DevOps pipeline.
Task: Generate test cases for common web vulnerabilities (OWASP Top 10).
Purpose: These will be used in our CI/CD pipeline to catch vulnerabilities before deployment.
Output: Python pytest functions that test for each vulnerability type.
"""
```

### 3.5 Checklist: Working with Model Constraints

```markdown
## Model Constraints Checklist

### Before Sending a Prompt
- [ ] Is my request clear and unambiguous?
- [ ] Have I provided necessary context?
- [ ] Am I asking for something within the model's capabilities?
- [ ] Have I considered potential hallucination risks?

### For Code Generation
- [ ] Have I specified the language and framework?
- [ ] Have I provided example input/output?
- [ ] Will I test the generated code?
- [ ] Have I included relevant API documentation?

### For Long Contexts
- [ ] Is critical information at the start and end?
- [ ] Have I used clear section markers?
- [ ] Is there a summary of key points?
- [ ] Have I chunked appropriately?

### For Sensitive Requests
- [ ] Have I provided legitimate context?
- [ ] Is my purpose clearly stated?
- [ ] Would a human reviewer understand the intent?
```

---

<a name="exercise-1"></a>
## 4. Exercise 1: Model Comparison (45 min)

### Objective
Compare behavior across three LLM providers to understand their differences.

### Setup

<details>
<summary><b>Python</b></summary>

```python
# exercise1_model_comparison.py
from utils.llm_client import get_llm_client
import json
from datetime import datetime

# Test prompts covering different capabilities
TEST_PROMPTS = [
    {
        "name": "code_generation",
        "prompt": "Write a function that finds the longest palindromic substring. Include type hints and a docstring.",
        "evaluate": ["correctness", "code_quality", "documentation"]
    },
    {
        "name": "reasoning",
        "prompt": "A farmer has 17 sheep. All but 9 die. How many sheep are left? Explain your reasoning step by step.",
        "evaluate": ["correct_answer", "explanation_quality"]
    },
    {
        "name": "refactoring",
        "prompt": "Refactor this code to be more idiomatic:\n\ndef get_evens(numbers):\n    result = []\n    for i in range(len(numbers)):\n        if numbers[i] % 2 == 0:\n            result.append(numbers[i])\n    return result",
        "evaluate": ["improvement", "explanation"]
    },
]

def run_comparison():
    providers = ["openai", "anthropic"]
    results = {}

    for test in TEST_PROMPTS:
        results[test["name"]] = {}
        print(f"\n{'='*60}")
        print(f"Test: {test['name']}")

        for provider in providers:
            try:
                client = get_llm_client(provider)
                messages = [
                    {"role": "system", "content": "You are a helpful programming assistant."},
                    {"role": "user", "content": test["prompt"]}
                ]

                response = client.chat(messages)
                results[test["name"]][provider] = {
                    "response": response,
                    "timestamp": datetime.now().isoformat()
                }

                print(f"\n--- {provider.upper()} ---")
                print(response[:500] + "..." if len(response) > 500 else response)

            except Exception as e:
                results[test["name"]][provider] = {"error": str(e)}
                print(f"\n--- {provider.upper()} ---")
                print(f"Error: {e}")

    # Save results
    with open("model_comparison_results.json", "w") as f:
        json.dump(results, f, indent=2)

    return results

if __name__ == "__main__":
    run_comparison()
```

</details>

<details>
<summary><b>TypeScript</b></summary>

```typescript
// exercise1_model_comparison.ts
import { getLLMClient, type LLMProvider, type Message } from './utils/llm-client';
import { writeFileSync } from 'fs';

interface TestPrompt {
  name: string;
  prompt: string;
  evaluate: string[];
}

const TEST_PROMPTS: TestPrompt[] = [
  {
    name: 'code_generation',
    prompt: 'Write a function that finds the longest palindromic substring. Include type annotations and JSDoc.',
    evaluate: ['correctness', 'code_quality', 'documentation'],
  },
  {
    name: 'reasoning',
    prompt: 'A farmer has 17 sheep. All but 9 die. How many sheep are left? Explain your reasoning step by step.',
    evaluate: ['correct_answer', 'explanation_quality'],
  },
  {
    name: 'refactoring',
    prompt: 'Refactor this code to be more idiomatic:\n\nfunction getEvens(numbers) {\n  const result = [];\n  for (let i = 0; i < numbers.length; i++) {\n    if (numbers[i] % 2 === 0) {\n      result.push(numbers[i]);\n    }\n  }\n  return result;\n}',
    evaluate: ['improvement', 'explanation'],
  },
];

async function runComparison() {
  const providers: LLMProvider[] = ['openai', 'anthropic'];
  const results: Record<string, Record<string, unknown>> = {};

  for (const test of TEST_PROMPTS) {
    results[test.name] = {};
    console.log(`\n${'='.repeat(60)}`);
    console.log(`Test: ${test.name}`);

    for (const provider of providers) {
      try {
        const client = getLLMClient(provider);
        const messages: Message[] = [
          { role: 'system', content: 'You are a helpful programming assistant.' },
          { role: 'user', content: test.prompt },
        ];

        const response = await client.chat(messages);
        results[test.name][provider] = {
          response,
          timestamp: new Date().toISOString(),
        };

        console.log(`\n--- ${provider.toUpperCase()} ---`);
        console.log(response.length > 500 ? response.slice(0, 500) + '...' : response);
      } catch (error) {
        results[test.name][provider] = { error: String(error) };
        console.log(`\n--- ${provider.toUpperCase()} ---`);
        console.log(`Error: ${error}`);
      }
    }
  }

  // Save results
  writeFileSync('model_comparison_results.json', JSON.stringify(results, null, 2));
  return results;
}

runComparison();
```

</details>

### Your Task

1. **Run the comparison** with all three providers
2. **Fill out this evaluation matrix:**

```markdown
## Model Comparison Report

### Code Generation
| Criteria | OpenAI | Anthropic | Gemini | Notes |
|----------|--------|-----------|--------|-------|
| Correctness | | | | |
| Code Quality | | | | |
| Documentation | | | | |

### Reasoning
| Criteria | OpenAI | Anthropic | Gemini | Notes |
|----------|--------|-----------|--------|-------|
| Correct Answer | | | | |
| Explanation | | | | |

### Refactoring
| Criteria | OpenAI | Anthropic | Gemini | Notes |
|----------|--------|-----------|--------|-------|
| Improvement | | | | |
| Explanation | | | | |

### Ambiguous Request Handling
| Criteria | OpenAI | Anthropic | Gemini | Notes |
|----------|--------|-----------|--------|-------|
| Interpretation | | | | |
| Suggestions | | | | |

### Overall Impressions
- Best for code generation:
- Best for reasoning:
- Best for refactoring:
- Most helpful with ambiguous requests:
- Fastest response time:
- Personal preference and why:
```

3. **Document 3 interesting differences** you observed

---

<a name="vibe-coding"></a>
## 5. Vibe Coding & AI-First Development (1 hour)

### 5.1 What is "Vibe Coding"?

"Vibe Coding" is a term coined to describe a new paradigm where developers:
- Describe what they want in natural language
- Let AI generate the implementation
- Guide and refine through conversation
- Focus on high-level architecture and validation

```
Traditional Development:
┌──────────────────────────────────────────────────────┐
│  Developer writes every line of code manually        │
│  ↓                                                   │
│  Developer debugs every error manually               │
│  ↓                                                   │
│  Developer refactors by rewriting                    │
└──────────────────────────────────────────────────────┘

Vibe Coding:
┌──────────────────────────────────────────────────────┐
│  Developer describes intent clearly                  │
│  ↓                                                   │
│  AI generates implementation                         │
│  ↓                                                   │
│  Developer reviews, tests, guides refinement         │
│  ↓                                                   │
│  Developer validates correctness and edge cases      │
└──────────────────────────────────────────────────────┘
```

### 5.2 AI-First Development Methodology

**The AI-First Loop:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI-First Development Loop                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│     ┌─────────┐                                                 │
│     │ SPECIFY │ ◄────────────────────────────────────┐          │
│     └────┬────┘                                      │          │
│          │ What do I need?                           │          │
│          ▼                                           │          │
│     ┌─────────┐                                      │          │
│     │GENERATE │                                      │          │
│     └────┬────┘                                      │          │
│          │ AI creates implementation                 │ Iterate  │
│          ▼                                           │          │
│     ┌─────────┐                                      │          │
│     │ REVIEW  │                                      │          │
│     └────┬────┘                                      │          │
│          │ Is this correct?                          │          │
│          ▼                                           │          │
│     ┌─────────┐      No                              │          │
│     │ VERIFY  │ ─────────────────────────────────────┘          │
│     └────┬────┘                                                 │
│          │ Yes                                                  │
│          ▼                                                      │
│     ┌─────────┐                                                 │
│     │ DEPLOY  │                                                 │
│     └─────────┘                                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 5.3 When to Use AI vs. Traditional Coding

| Situation | Use AI | Use Traditional |
|-----------|--------|-----------------|
| Boilerplate/scaffolding | ✅ | |
| Well-understood patterns | ✅ | |
| Code you need to deeply understand | | ✅ |
| Security-critical sections | Review only | ✅ |
| Novel algorithms | Assist | ✅ |
| Documentation | ✅ | |
| Tests for existing code | ✅ | |
| Performance optimization | Assist | ✅ |
| Learning new technologies | ✅ | |

### 5.4 Effective Human-AI Collaboration Patterns

**Pattern 1: Scaffolding First**
```
Human: "Create the project structure for a FastAPI app with
       authentication, a PostgreSQL database, and Redis caching."
AI:    [Generates project structure, files, configs]
Human: "Now implement the user model and authentication endpoints."
AI:    [Generates specific implementation]
```

**Pattern 2: Iterative Refinement**
```
Human: "Write a function to parse log files."
AI:    [Generates basic implementation]
Human: "Add support for gzipped files and handle malformed lines."
AI:    [Refines implementation]
Human: "Add type hints and improve error messages."
AI:    [Final refinement]
```

**Pattern 3: Review and Explain**
```
Human: "Review this code for potential issues: [code]"
AI:    [Identifies issues, suggests improvements]
Human: "Fix the SQL injection vulnerability you identified."
AI:    [Provides fix]
```

**Pattern 4: Test-Driven Generation**
```
Human: "Here are my test cases: [tests]. Write code to pass them."
AI:    [Generates implementation matching tests]
```

### 5.5 Common Vibe Coding Pitfalls

| Pitfall | Problem | Solution |
|---------|---------|----------|
| **Blind acceptance** | Accepting code without understanding | Always review, run tests |
| **Underspecification** | Vague prompts → wrong code | Be specific about requirements |
| **Context overload** | Dumping too much code | Provide relevant context only |
| **Over-reliance** | Using AI for everything | Know when traditional is better |
| **Ignoring errors** | Assuming AI output is correct | Test everything |

### 5.6 Vibe Coding Quick Reference

```markdown
## Vibe Coding Best Practices

### Do:
- ✅ Specify language, framework, and version
- ✅ Provide example inputs and expected outputs
- ✅ Break complex tasks into steps
- ✅ Review and test all generated code
- ✅ Ask for explanations when needed
- ✅ Use AI for boilerplate and scaffolding

### Don't:
- ❌ Accept code blindly without review
- ❌ Use overly vague prompts
- ❌ Dump entire codebases as context
- ❌ Assume AI understands your full system
- ❌ Skip testing because "AI wrote it"
- ❌ Use AI for code you need to deeply understand
```

---

<a name="tool-landscape"></a>
## 6. Tool Landscape (1 hour)

### 6.1 AI Coding Tools Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI Coding Tool Categories                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  CLI Tools              IDE Extensions           Full IDEs      │
│  ──────────             ──────────────           ─────────      │
│  • Claude Code          • GitHub Copilot         • Cursor       │
│  • Aider                • Continue               • Windsurf     │
│  • Gemini CLI           • Codeium                               │
│  • GPT CLI              • Amazon Q                              │
│                                                                 │
│  Best for:              Best for:                Best for:      │
│  Terminal workflows     Existing IDE users       Full AI-first  │
│  Git integration        Inline completions       Integrated exp │
│  Scripting              Quick suggestions        Chat + code    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 6.2 Claude Code (CLI)

**Installation:**
```bash
# Install via npm
npm install -g @anthropic-ai/claude-code

# Or via pip
pip install claude-code
```

**Key Features:**
- Terminal-based interface
- Deep file system integration
- Git-aware operations
- Multi-file editing

**Example Workflow:**
```bash
# Start Claude Code in a project
cd my-project
claude

# Common commands within Claude Code
> /help              # Show available commands
> /add file.py       # Add file to context
> /clear             # Clear conversation
```

### 6.3 Cursor IDE

**Key Features:**
- VS Code fork with native AI
- Cmd+K for inline edits
- Cmd+L for chat
- Multi-file context

**Setup:**
```
1. Download from cursor.sh
2. Import VS Code settings (optional)
3. Configure AI provider in settings
```

**Power User Tips:**
```
Cmd+K: "Convert this to TypeScript"  → Inline transformation
Cmd+L: "Explain this function"       → Sidebar chat
Cmd+Shift+L: Add selection to chat context
@ mentions: @file.py @codebase @docs
```

### 6.4 Gemini CLI

**Installation:**
```bash
# Install via npm
npm install -g @anthropic-ai/gemini-cli

# Or use Google Cloud SDK
gcloud components install gemini-cli
```

**Key Features:**
- Google ecosystem integration
- Fast responses
- Large context window
- Multimodal support

### 6.5 Tool Selection Matrix

Fill this out based on your needs:

```markdown
## Tool Selection Matrix

| Factor | Weight | Claude Code | Cursor | Gemini CLI | Your Choice |
|--------|--------|-------------|--------|------------|-------------|
| Terminal preference | /10 | | | | |
| IDE integration | /10 | | | | |
| Cost sensitivity | /10 | | | | |
| Team collaboration | /10 | | | | |
| Offline capability | /10 | | | | |
| Learning curve | /10 | | | | |
| **Total** | | | | | |

My primary tool: ________________
My backup tool: ________________
```

### 6.6 Tool Configuration Templates

**Claude Code Settings:**
```json
// ~/.claude/settings.json
{
  "model": "claude-3-5-sonnet-20241022",
  "temperature": 0.1,
  "max_tokens": 4096,
  "auto_save": true,
  "git_integration": true
}
```

**Cursor Settings:**
```json
// .cursor/settings.json
{
  "ai.model": "claude-3-5-sonnet",
  "ai.temperature": 0.2,
  "ai.contextLength": 16000,
  "ai.autoComplete": true
}
```

---

<a name="lab-01"></a>
## 7. Lab 01: Build First AI-Assisted App (1h 15min)

### Lab Overview

**Goal:** Build and deploy a URL shortener using AI-assisted development.

**Stack:**
- Python FastAPI backend
- TypeScript/Next.js frontend
- SQLite database (simple)
- Deployment to Vercel

**What You'll Practice:**
- AI-assisted scaffolding
- Iterative development with AI
- Deployment workflow

### Lab Instructions

Navigate to `labs/lab01-vibe-coding-intro/` and follow the README.

**Quick Start:**
```bash
cd labs/lab01-vibe-coding-intro
# Read the lab instructions
cat README.md
# Follow steps to build the URL shortener
```

### Expected Outcome

By the end of this lab, you should have:
1. A working URL shortener running locally
2. The application deployed to Vercel
3. Experience with AI-assisted development workflow

### Verification

```bash
# Test locally
curl -X POST http://localhost:8000/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.example.com/very/long/url"}'

# Should return something like:
# {"short_url": "http://localhost:8000/abc123"}
```

---

## Day 1 Summary

### What We Covered
1. **LLM Fundamentals**: Tokens, context windows, parameters
2. **Model Behavior**: Reasoning limits, hallucinations, constraints
3. **Vibe Coding**: AI-first development methodology
4. **Tool Landscape**: Claude Code, Cursor, and alternatives
5. **Practical Lab**: Built and deployed first AI-assisted app

### Key Takeaways
- LLMs are pattern matchers, not reasoners—work with this, not against it
- Hallucinations are inevitable—always verify
- AI-first development requires clear specifications and verification
- Choose tools based on your workflow, not hype

### Preparation for Day 2
- Review your model comparison notes
- Think about code tasks that could benefit from better prompts
- Consider a codebase you'd like to analyze

---

**Navigation**: [← Schedule](./SCHEDULE.md) | [Day 2: Prompting →](./day2-prompting.md)
