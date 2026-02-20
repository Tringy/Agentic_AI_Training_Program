/**
 * TypeScript Agent Template - Main Entry Point
 * =============================================
 *
 * Re-exports all components for easy importing.
 */

export { Agent } from './agent.js';
export {
  LLMClient,
  AnthropicClient,
  OpenAIClient,
  GoogleClient,
  createLLMClient,
  type LLMProvider,
} from './llm-client.js';
export {
  Tool,
  CalculatorTool,
  FileReaderTool,
  ShellTool,
} from './tools.js';
export type {
  ToolCall,
  ToolResult,
  ToolDefinition,
  Message,
  MessageRole,
  AgentState,
  AgentOptions,
  LLMResponse,
  ParameterSchema,
} from './types.js';
