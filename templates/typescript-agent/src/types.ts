/**
 * Reusable TypeScript Agent Template - Type Definitions
 * =====================================================
 *
 * Core types for building LLM-powered agents.
 */

// ============================================================================
// Tool Types
// ============================================================================

/**
 * JSON Schema for tool parameters
 */
export interface ParameterSchema {
  type: 'object';
  properties: Record<string, {
    type: string;
    description: string;
    enum?: string[];
  }>;
  required?: string[];
}

/**
 * Represents a tool call from the LLM
 */
export interface ToolCall {
  id: string;
  name: string;
  arguments: Record<string, unknown>;
}

/**
 * Result of executing a tool
 */
export interface ToolResult {
  toolCallId: string;
  result: string;
  error?: string;
}

/**
 * Tool definition for LLM
 */
export interface ToolDefinition {
  name: string;
  description: string;
  parameters: ParameterSchema;
}

// ============================================================================
// Message Types
// ============================================================================

export type MessageRole = 'system' | 'user' | 'assistant' | 'tool';

export interface Message {
  role: MessageRole;
  content: string;
  toolCallId?: string;
  toolUse?: {
    id: string;
    name: string;
    input: Record<string, unknown>;
  };
}

// ============================================================================
// Agent State
// ============================================================================

export interface AgentState {
  messages: Message[];
  toolResults: ToolResult[];
  iteration: number;
  isComplete: boolean;
}

// ============================================================================
// LLM Response Types
// ============================================================================

export interface LLMResponse {
  content: string;
  toolCalls: ToolCall[];
}

// ============================================================================
// Agent Options
// ============================================================================

export interface AgentOptions {
  systemPrompt: string;
  maxIterations?: number;
}
