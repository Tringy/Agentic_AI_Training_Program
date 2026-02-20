/**
 * Shared Utilities for AI Training Program - TypeScript
 *
 * Main entry point exporting all utilities.
 *
 * @packageDocumentation
 */

// LLM Client exports
export {
  LLMClient,
  UnifiedLLMClient,
  getLLMClient,
  getFreeLLMClient,
  autoSelectClient,
  GoogleAIClient,
  GroqClient,
  OllamaClient,
  AnthropicClient,
  OpenAIClient,
  type Message,
} from './llm-client.js';

// Parsing utilities
export {
  extractJSON,
  extractJSONArray,
  extractCodeBlock,
  extractAllCodeBlocks,
  cleanResponse,
  validateJSONSchema,
} from './parsing.js';
