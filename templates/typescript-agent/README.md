# TypeScript Agent Template

A reusable template for building LLM-powered agents in TypeScript.

## Quick Start

```bash
# Install dependencies
npm install

# Set your API key
export ANTHROPIC_API_KEY=your-key
# or
export OPENAI_API_KEY=your-key
# or
export GOOGLE_API_KEY=your-key

# Run the example
npm run dev
```

## Usage

```typescript
import { Agent, AnthropicClient, CalculatorTool } from './agent.js';

// Create LLM client
const llm = new AnthropicClient();
// Or: new OpenAIClient()
// Or: new GoogleClient()

// Create tools
const tools = [new CalculatorTool()];

// Create agent
const agent = new Agent(llm, tools, {
  systemPrompt: 'You are a helpful assistant.',
  maxIterations: 10,
});

// Run the agent
const result = await agent.run('What is 25 * 4?');
console.log(result);
```

## Creating Custom Tools

Extend the `Tool` base class:

```typescript
import { Tool, ParameterSchema } from './tools.js';

class MyCustomTool extends Tool {
  get name(): string {
    return 'my_tool';
  }

  get description(): string {
    return 'Description of what the tool does';
  }

  get parameters(): ParameterSchema {
    return {
      type: 'object',
      properties: {
        input: {
          type: 'string',
          description: 'The input parameter',
        },
      },
      required: ['input'],
    };
  }

  async execute(args: Record<string, unknown>): Promise<string> {
    const input = args.input as string;
    // Your tool logic here
    return `Processed: ${input}`;
  }
}
```

## Available LLM Clients

| Client | Provider | Default Model |
|--------|----------|---------------|
| `AnthropicClient` | Anthropic | claude-3-5-sonnet-20241022 |
| `OpenAIClient` | OpenAI | gpt-4o |
| `GoogleClient` | Google AI | gemini-1.5-flash |

## Available Tools

| Tool | Description |
|------|-------------|
| `CalculatorTool` | Basic arithmetic operations |
| `FileReaderTool` | Read file contents |
| `ShellTool` | Execute whitelisted shell commands |

## Project Structure

```
typescript-agent/
├── src/
│   ├── agent.ts       # Main Agent class
│   ├── llm-client.ts  # LLM provider clients
│   ├── tools.ts       # Tool base class and examples
│   ├── types.ts       # TypeScript type definitions
│   ├── index.ts       # Main exports
│   └── example.ts     # Usage example
├── package.json
├── tsconfig.json
└── README.md
```

## Comparison with Python Template

| Python | TypeScript |
|--------|------------|
| `from anthropic import Anthropic` | `import Anthropic from '@anthropic-ai/sdk'` |
| `@dataclass` | `interface` or `type` |
| `ABC, abstractmethod` | `abstract class` |
| `async def` | `async function` |
| `List[Dict]` | `Array<Record<string, unknown>>` |
