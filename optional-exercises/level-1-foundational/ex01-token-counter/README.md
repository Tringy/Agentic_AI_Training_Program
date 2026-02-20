# Exercise 01: Token Counter & Cost Analyzer

## Description

Build an interactive tool to analyze tokens, estimate costs, and compare different LLM models. This tool is essential for any developer working with LLM APIs, as it allows you to optimize costs and understand resource usage.

## Learning Objectives

Upon completing this exercise, you will be able to:

- ✅ Understand how tokenizers from different providers work
- ✅ Calculate precise costs for LLM API calls
- ✅ Compare efficiency of different models
- ✅ Analyze token distribution in prompts
- ✅ Optimize prompts to reduce costs

## Prerequisites

- Complete Day 1-2 of the main program
- Basic knowledge of React/Next.js or Streamlit
- API keys from OpenAI, Anthropic, Google (optional)

## Required Features

### Core Functionality

1. **Token Counter**
   - Input: text/prompt
   - Output: number of tokens per provider
   - Support for: GPT-4, Claude, Gemini

2. **Cost Calculator**
   - Calculate cost per prompt
   - Calculate cost per completion
   - Estimated total cost
   - Comparison between models

3. **Batch Analysis**
   - Analyze multiple prompts
   - Aggregated statistics
   - Export to CSV/JSON

4. **Visual Dashboard**
   - Token distribution chart
   - Cost comparison between models
   - Trend analysis (if history is saved)

### Advanced Functionality (Optional)

- 🔥 Suggested prompt optimization
- 🔥 Cost alerts (if threshold exceeded)
- 🔥 Analysis history
- 🔥 API endpoint for integration

## Suggested Tech Stack

### Option A: Next.js + TypeScript (Recommended)

```bash
# Dependencies
- next
- react
- tiktoken (OpenAI tokenizer)
- @anthropic-ai/tokenizer
- recharts (for charts)
- zustand (state management)
```

### Option B: Python + Streamlit

```bash
# Dependencies
- streamlit
- tiktoken
- anthropic
- pandas
- plotly
```

### Option C: Python + FastAPI + React

```bash
# Backend
- fastapi
- tiktoken
- anthropic

# Frontend
- vite + react
- recharts
```

## Implementation Guide

### Step 1: Project Setup

```bash
# Next.js option
npx create-next-app@latest token-analyzer --typescript
cd token-analyzer
npm install tiktoken @anthropic-ai/tokenizer recharts zustand
```

### Step 2: Implement Token Counting

**File: `lib/tokenizers.ts`**

```typescript
import { encoding_for_model } from 'tiktoken';

export interface TokenCount {
  provider: string;
  model: string;
  tokens: number;
  cost: number;
}

export async function countTokens(
  text: string,
  model: string
): Promise<number> {
  // Implement counting logic per provider
  // OpenAI: use tiktoken
  // Claude: use @anthropic-ai/tokenizer
  // Gemini: approximation
}
```

**Tasks**:
- [ ] Implement counting for GPT-4/GPT-3.5
- [ ] Implement counting for Claude (Sonnet, Opus, Haiku)
- [ ] Implement counting for Gemini (Pro, Flash)
- [ ] Create unified function `countAllTokens(text)`

### Step 3: Implement Cost Calculator

**File: `lib/pricing.ts`**

```typescript
// Updated prices (Jan 2025)
export const MODEL_PRICING = {
  'gpt-4': { input: 0.03, output: 0.06 },
  'gpt-3.5-turbo': { input: 0.0005, output: 0.0015 },
  'claude-opus-4': { input: 0.015, output: 0.075 },
  'claude-sonnet-3.5': { input: 0.003, output: 0.015 },
  'claude-haiku-3': { input: 0.00025, output: 0.00125 },
  'gemini-pro': { input: 0.00025, output: 0.0005 },
};

export function calculateCost(
  inputTokens: number,
  outputTokens: number,
  model: string
): number {
  // Implement cost calculation
  // Price per 1M tokens
}
```

**Tasks**:
- [ ] Create updated pricing table
- [ ] Implement cost calculation
- [ ] Add support for batch discounts
- [ ] Create cost comparator between models

### Step 4: Create Interactive UI

**Main components**:

1. `TextInput.tsx` - Input for text/prompt
2. `TokenDisplay.tsx` - Display results
3. `CostComparison.tsx` - Comparison table
4. `TokenChart.tsx` - Distribution visualization

**Tasks**:
- [ ] Create input with syntax highlighting
- [ ] Show tokens in real-time
- [ ] Model comparison table
- [ ] Cost chart

### Step 5: Add Batch Analysis

**File: `components/BatchAnalyzer.tsx`**

```typescript
interface BatchAnalysis {
  totalTokens: number;
  averageTokens: number;
  totalCost: number;
  distribution: Record<string, number>;
}

export function BatchAnalyzer() {
  // Allow CSV/JSON file upload
  // Analyze multiple prompts
  // Generate statistics
  // Export results
}
```

**Tasks**:
- [ ] File upload (CSV/JSON)
- [ ] Batch processing
- [ ] Aggregated statistics
- [ ] Results export

### Step 6: Visualization Dashboard

**Use Recharts to create**:

1. **Token Distribution Chart**
   - Pie chart of tokens per model

2. **Cost Comparison Bar Chart**
   - Compare costs between models

3. **Historical Trend** (Optional)
   - Line chart of usage over time

**Tasks**:
- [ ] Implement distribution chart
- [ ] Implement cost comparison
- [ ] Add interactive filters
- [ ] Make responsive

## Testing

### Unit Tests

```typescript
// __tests__/tokenizers.test.ts
describe('Token Counting', () => {
  it('should count GPT-4 tokens correctly', () => {
    const text = "Hello, world!";
    const tokens = countTokens(text, 'gpt-4');
    expect(tokens).toBeGreaterThan(0);
  });

  it('should match across similar models', () => {
    const text = "Test prompt";
    const gpt4 = countTokens(text, 'gpt-4');
    const gpt35 = countTokens(text, 'gpt-3.5-turbo');
    expect(Math.abs(gpt4 - gpt35)).toBeLessThan(3);
  });
});
```

**Tasks**:
- [ ] Tests for each tokenizer
- [ ] Tests for cost calculation
- [ ] Comparison tests
- [ ] Edge case tests

### Integration Tests

```typescript
// __tests__/e2e.test.ts
describe('Token Analyzer E2E', () => {
  it('should analyze text and show results', async () => {
    // Simulate user input
    // Verify results
    // Verify updated UI
  });
});
```

## Validation

Your implementation should:

✅ Count tokens correctly (±5% of official)
✅ Calculate costs precisely
✅ Compare at least 3 providers
✅ Have responsive and usable UI
✅ Include at least 5 unit tests
✅ Work with prompts of 1-10K tokens
✅ Export results to CSV/JSON

## Extra Challenges

1. **Cache & Performance**
   - Cache counting results
   - Optimize for long texts

2. **Real-time API Integration**
   - Connect to real APIs for validation
   - Show updated prices

3. **Prompt Optimizer**
   - Suggest ways to reduce tokens
   - Identify redundancies

4. **Browser Extension**
   - Convert to Chrome extension
   - Analyze prompts in-situ

## Resources

### Documentation
- [Tiktoken (OpenAI)](https://github.com/openai/tiktoken)
- [Anthropic Tokenizer](https://docs.anthropic.com/claude/docs/models-overview#token-counting)
- [Google Gemini Tokens](https://ai.google.dev/gemini-api/docs/tokens)

### Code Examples
- [Next.js Token Counter Example](https://github.com/examples/token-counter)
- [Streamlit Cost Calculator](https://github.com/examples/cost-calc)

### Similar Tools (Inspiration)
- [OpenAI Tokenizer](https://platform.openai.com/tokenizer)
- [Anthropic Token Counter](https://docs.anthropic.com/claude/reference/token-counter)

## Evaluation

| Criterion | Weight | Description |
|----------|------|-------------|
| **Core Functionality** | 40% | Token counting + cost calculation |
| **Multi-Provider** | 20% | Support for 3+ providers |
| **UI/UX** | 15% | Clear and usable interface |
| **Testing** | 15% | Unit tests + validation |
| **Documentation** | 10% | README + commented code |

**Minimum passing score**: 70%

## Submission

1. Code on GitHub (public or private)
2. README with:
   - Installation instructions
   - Screenshots/GIF of the tool
   - Explanation of technical decisions
3. Deployed demo (Vercel/Netlify) - Optional
4. Passing tests (screenshot or CI badge)

## Reference Solution

Once you complete the exercise, you can compare with:
- [View solution →](./solution/)

**⚠️ Try to solve it first without looking at the solution**

---

## Next Steps

After completing this exercise, consider:
- [Ex 02: Hallucination Detector →](../ex02-hallucination-detector/)
- [Ex 04: Cost Calculator Dashboard →](../ex04-cost-calculator/)

---

**Good luck! 🚀**
