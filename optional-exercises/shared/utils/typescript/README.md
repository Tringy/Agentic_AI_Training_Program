# Shared Utilities - TypeScript

Consolidated utilities for the AI Training Program. TypeScript mirror of Python shared_utils.

## Installation

```bash
# From a lab or exercise
npm install ../../../optional-exercises/shared/utils/typescript

# Or build and link
cd optional-exercises/shared/utils/typescript
npm install
npm run build
npm link

# Then in your project
npm link @ai-training/shared-utils
```

## Quick Start

```typescript
import { UnifiedLLMClient, extractJSON } from '@ai-training/shared-utils';

// Create client (auto-selects free provider)
const client = new UnifiedLLMClient();

// Chat
const response = await client.chat([
  { role: 'system', content: 'You are helpful.' },
  { role: 'user', content: 'Explain LLMs in one sentence' }
]);

console.log(response);

// Parse JSON if needed
const data = extractJSON(response);
```

## Available Utilities

### LLM Client (`llm-client.ts`)
- `UnifiedLLMClient` - Auto-selecting client
- `getLLMClient(provider)` - Get specific provider
- `getFreeLLMClient(provider)` - Free providers only
- Supports: Google, Groq, Ollama (free), Anthropic, OpenAI (paid)

### Response Parsing (`parsing.ts`)
- `extractJSON(response)` - Extract JSON from markdown
- `extractCodeBlock(response, language)` - Extract code
- `extractAllCodeBlocks(response)` - Get all code blocks
- `cleanResponse(response)` - Remove LLM artifacts
- `validateJSONSchema(data, requiredKeys)` - Validate structure

## Examples

```typescript
// Use specific provider
import { getLLMClient } from '@ai-training/shared-utils';

const client = getLLMClient('google');
const response = await client.chat([
  { role: 'user', content: 'Write hello world in Python' }
]);

// Extract code
import { extractCodeBlock } from '@ai-training/shared-utils';
const code = extractCodeBlock(response, 'python');
console.log(code);
```

## TypeScript Types

Full TypeScript support with exported interfaces:
- `Message` - Chat message interface
- `LLMClient` - Abstract client interface

## Testing

```bash
npm run build
node dist/llm-client.js  # Run client tests
```
