/**
 * Reusable TypeScript Agent Template
 * ===================================
 *
 * This template provides a foundation for building LLM-powered agents.
 * Customize the system prompt, tools, and logic for your specific use case.
 *
 * Usage:
 *   const llm = new AnthropicClient();
 *   const tools = [new CalculatorTool()];
 *   const agent = new Agent(llm, tools, { systemPrompt: "You are helpful." });
 *   const result = await agent.run("What is 25 * 4?");
 */

import type { LLMClient } from './llm-client.js';
import type { Tool } from './tools.js';
import type {
  AgentState,
  AgentOptions,
  Message,
  ToolResult
} from './types.js';

// ============================================================================
// Agent Core
// ============================================================================

/**
 * Base agent that can use tools to accomplish tasks.
 */
export class Agent {
  private llm: LLMClient;
  private tools: Map<string, Tool>;
  private systemPrompt: string;
  private maxIterations: number;

  constructor(
    llmClient: LLMClient,
    tools: Tool[],
    options: AgentOptions
  ) {
    this.llm = llmClient;
    this.tools = new Map(tools.map((t) => [t.name, t]));
    this.systemPrompt = options.systemPrompt;
    this.maxIterations = options.maxIterations ?? 10;
  }

  /**
   * Run the agent on a user input
   */
  async run(userInput: string): Promise<string> {
    const state: AgentState = {
      messages: [
        { role: 'system', content: this.systemPrompt },
        { role: 'user', content: userInput },
      ],
      toolResults: [],
      iteration: 0,
      isComplete: false,
    };

    while (!state.isComplete && state.iteration < this.maxIterations) {
      await this.step(state);
      state.iteration++;
    }

    // Return final response
    for (let i = state.messages.length - 1; i >= 0; i--) {
      const msg = state.messages[i];
      if (msg.role === 'assistant' && msg.content) {
        return msg.content;
      }
    }

    return 'Unable to complete the task.';
  }

  /**
   * Execute one step of the agent loop
   */
  private async step(state: AgentState): Promise<void> {
    const toolDefinitions = Array.from(this.tools.values()).map((t) =>
      t.toDefinition()
    );

    const { content, toolCalls } = await this.llm.chat(
      state.messages,
      toolDefinitions.length > 0 ? toolDefinitions : undefined
    );

    if (toolCalls.length === 0) {
      // No tool calls = final response
      state.messages.push({ role: 'assistant', content });
      state.isComplete = true;
      return;
    }

    // Execute tools
    for (const tc of toolCalls) {
      const tool = this.tools.get(tc.name);

      if (tool) {
        const result = await tool.execute(tc.arguments);
        const toolResult: ToolResult = {
          toolCallId: tc.id,
          result,
        };
        state.toolResults.push(toolResult);

        // Add assistant message with tool use
        state.messages.push({
          role: 'assistant',
          content: content || '',
          toolUse: {
            id: tc.id,
            name: tc.name,
            input: tc.arguments,
          },
        });

        // Add tool result as user message
        state.messages.push({
          role: 'user',
          content: `Tool result for ${tc.name}: ${result}`,
        });
      }
    }
  }

  /**
   * Get the current tools
   */
  getTools(): Tool[] {
    return Array.from(this.tools.values());
  }

  /**
   * Add a tool to the agent
   */
  addTool(tool: Tool): void {
    this.tools.set(tool.name, tool);
  }

  /**
   * Remove a tool from the agent
   */
  removeTool(name: string): boolean {
    return this.tools.delete(name);
  }
}

// ============================================================================
// Exports
// ============================================================================

export { LLMClient, AnthropicClient, OpenAIClient, GoogleClient, createLLMClient } from './llm-client.js';
export { Tool, CalculatorTool, FileReaderTool, ShellTool } from './tools.js';
export type {
  ToolCall,
  ToolResult,
  ToolDefinition,
  Message,
  AgentState,
  AgentOptions,
  LLMResponse,
  ParameterSchema,
} from './types.js';
