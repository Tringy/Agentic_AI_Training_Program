/**
 * TypeScript Agent Template - Example Usage
 * ==========================================
 *
 * Run with: npm run dev
 *
 * Make sure to set your API key:
 *   export ANTHROPIC_API_KEY=your-key
 *   # or
 *   export OPENAI_API_KEY=your-key
 *   # or
 *   export GOOGLE_API_KEY=your-key
 */

import 'dotenv/config';
import { Agent, AnthropicClient, CalculatorTool } from './agent.js';

async function main() {
  // Create LLM client
  const llm = new AnthropicClient();

  // Create tools
  const tools = [new CalculatorTool()];

  // Create agent
  const agent = new Agent(llm, tools, {
    systemPrompt: `You are a helpful assistant that can perform calculations.
When asked to calculate something, use the calculator tool.
Always show your work and explain your reasoning.`,
  });

  // Run the agent
  console.log('Running agent with question: "What is 123 * 456?"');
  console.log('---');

  const result = await agent.run('What is 123 * 456?');
  console.log('Result:', result);
}

main().catch(console.error);
