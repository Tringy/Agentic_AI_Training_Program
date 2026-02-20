/**
 * Reusable TypeScript Agent Template - LLM Clients
 * ================================================
 *
 * LLM client implementations for different providers.
 */

import type { Message, ToolCall, ToolDefinition, LLMResponse } from './types.js';

// ============================================================================
// LLM Client Interface
// ============================================================================

/**
 * Abstract LLM client interface
 */
export abstract class LLMClient {
  /**
   * Send messages and return response with optional tool calls
   */
  abstract chat(
    messages: Message[],
    tools?: ToolDefinition[]
  ): Promise<LLMResponse>;
}

// ============================================================================
// Anthropic Client
// ============================================================================

/**
 * Anthropic Claude client
 */
export class AnthropicClient extends LLMClient {
  private client: InstanceType<typeof import('@anthropic-ai/sdk').default>;
  private model: string;

  constructor(model: string = 'claude-3-5-sonnet-20241022') {
    super();
    // Dynamic import handled in initialization
    this.model = model;
    this.client = null as unknown as InstanceType<typeof import('@anthropic-ai/sdk').default>;
  }

  private async ensureClient(): Promise<void> {
    if (!this.client) {
      const Anthropic = (await import('@anthropic-ai/sdk')).default;
      this.client = new Anthropic();
    }
  }

  async chat(messages: Message[], tools?: ToolDefinition[]): Promise<LLMResponse> {
    await this.ensureClient();

    // Extract system message
    let system: string | undefined;
    const filtered: Array<{ role: 'user' | 'assistant'; content: string }> = [];

    for (const m of messages) {
      if (m.role === 'system') {
        system = m.content;
      } else if (m.role === 'user' || m.role === 'assistant') {
        filtered.push({ role: m.role, content: m.content });
      }
    }

    // Convert tools to Anthropic format
    const anthropicTools = tools?.map((t) => ({
      name: t.name,
      description: t.description,
      input_schema: t.parameters,
    }));

    const response = await this.client.messages.create({
      model: this.model,
      max_tokens: 4096,
      system,
      messages: filtered,
      tools: anthropicTools,
    });

    // Parse response
    let content = '';
    const toolCalls: ToolCall[] = [];

    for (const block of response.content) {
      if (block.type === 'text') {
        content += block.text;
      } else if (block.type === 'tool_use') {
        toolCalls.push({
          id: block.id,
          name: block.name,
          arguments: block.input as Record<string, unknown>,
        });
      }
    }

    return { content, toolCalls };
  }
}

// ============================================================================
// OpenAI Client
// ============================================================================

/**
 * OpenAI client
 */
export class OpenAIClient extends LLMClient {
  private client: InstanceType<typeof import('openai').default> | null = null;
  private model: string;

  constructor(model: string = 'gpt-4o') {
    super();
    this.model = model;
  }

  private async ensureClient(): Promise<void> {
    if (!this.client) {
      const OpenAI = (await import('openai')).default;
      this.client = new OpenAI();
    }
  }

  async chat(messages: Message[], tools?: ToolDefinition[]): Promise<LLMResponse> {
    await this.ensureClient();

    // Convert messages to OpenAI format
    const openaiMessages = messages.map((m) => ({
      role: m.role as 'system' | 'user' | 'assistant',
      content: m.content,
    }));

    // Convert tools to OpenAI format
    const openaiTools = tools?.map((t) => ({
      type: 'function' as const,
      function: {
        name: t.name,
        description: t.description,
        parameters: t.parameters,
      },
    }));

    const response = await this.client!.chat.completions.create({
      model: this.model,
      messages: openaiMessages,
      tools: openaiTools,
    });

    const message = response.choices[0].message;

    // Parse tool calls
    const toolCalls: ToolCall[] = [];
    if (message.tool_calls) {
      for (const tc of message.tool_calls) {
        toolCalls.push({
          id: tc.id,
          name: tc.function.name,
          arguments: JSON.parse(tc.function.arguments),
        });
      }
    }

    return {
      content: message.content || '',
      toolCalls,
    };
  }
}

// ============================================================================
// Google Generative AI Client (Free Tier)
// ============================================================================

/**
 * Google Generative AI client (Gemini)
 */
export class GoogleClient extends LLMClient {
  private client: InstanceType<typeof import('@google/generative-ai').GoogleGenerativeAI> | null = null;
  private model: string;

  constructor(model: string = 'gemini-1.5-flash') {
    super();
    this.model = model;
  }

  private async ensureClient(): Promise<void> {
    if (!this.client) {
      const { GoogleGenerativeAI } = await import('@google/generative-ai');
      const apiKey = process.env.GOOGLE_API_KEY;
      if (!apiKey) {
        throw new Error('GOOGLE_API_KEY environment variable is required');
      }
      this.client = new GoogleGenerativeAI(apiKey);
    }
  }

  async chat(messages: Message[], tools?: ToolDefinition[]): Promise<LLMResponse> {
    await this.ensureClient();

    const model = this.client!.getGenerativeModel({ model: this.model });

    // Extract system and user messages
    let systemInstruction = '';
    const history: Array<{ role: 'user' | 'model'; parts: Array<{ text: string }> }> = [];

    for (const m of messages) {
      if (m.role === 'system') {
        systemInstruction = m.content;
      } else if (m.role === 'user') {
        history.push({ role: 'user', parts: [{ text: m.content }] });
      } else if (m.role === 'assistant') {
        history.push({ role: 'model', parts: [{ text: m.content }] });
      }
    }

    // Get last user message
    const lastUserMessage = history.pop();
    if (!lastUserMessage || lastUserMessage.role !== 'user') {
      throw new Error('Last message must be from user');
    }

    // Convert tools to Google format
    const googleTools = tools
      ? [
          {
            functionDeclarations: tools.map((t) => ({
              name: t.name,
              description: t.description,
              parameters: t.parameters,
            })),
          },
        ]
      : undefined;

    const chat = model.startChat({
      history,
      systemInstruction,
      tools: googleTools,
    });

    const result = await chat.sendMessage(lastUserMessage.parts[0].text);
    const response = result.response;

    // Parse response
    let content = '';
    const toolCalls: ToolCall[] = [];

    for (const part of response.candidates?.[0]?.content?.parts || []) {
      if ('text' in part) {
        content += part.text;
      } else if ('functionCall' in part) {
        toolCalls.push({
          id: `call_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          name: part.functionCall.name,
          arguments: part.functionCall.args as Record<string, unknown>,
        });
      }
    }

    return { content, toolCalls };
  }
}

// ============================================================================
// Factory Function
// ============================================================================

export type LLMProvider = 'anthropic' | 'openai' | 'google';

/**
 * Create an LLM client based on provider
 */
export function createLLMClient(
  provider: LLMProvider,
  model?: string
): LLMClient {
  switch (provider) {
    case 'anthropic':
      return new AnthropicClient(model);
    case 'openai':
      return new OpenAIClient(model);
    case 'google':
      return new GoogleClient(model);
    default:
      throw new Error(`Unknown provider: ${provider}`);
  }
}
