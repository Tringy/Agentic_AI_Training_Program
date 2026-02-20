/**
 * Unified LLM Client for AI Training Program - TypeScript
 *
 * Consolidated LLM client supporting all major providers with a unified interface.
 * TypeScript mirror of Python shared_utils.llm_client
 *
 * Supported Providers:
 *   FREE:
 *     - Google AI Studio (Gemini) - Most generous free tier
 *     - Groq - Fastest inference
 *     - Ollama - Completely local/offline
 *
 *   PAID:
 *     - Anthropic (Claude) - Best for long context
 *     - OpenAI (GPT) - Broad capabilities
 *
 * @example
 * ```typescript
 * import { UnifiedLLMClient } from '@ai-training/shared-utils';
 *
 * const client = new UnifiedLLMClient();
 * const response = await client.chat([
 *   { role: 'user', content: 'Hello!' }
 * ]);
 * ```
 */

import Anthropic from '@anthropic-ai/sdk';
import OpenAI from 'openai';
import { GoogleGenerativeAI } from '@google/generative-ai';

export interface Message {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

export abstract class LLMClient {
  abstract chat(messages: Message[]): Promise<string>;
  abstract get modelName(): string;
}

// =============================================================================
// FREE PROVIDERS
// =============================================================================

export class GoogleAIClient extends LLMClient {
  private genai: GoogleGenerativeAI;
  private model: any;
  private _modelName: string;

  constructor(model: string = 'gemini-1.5-flash') {
    super();
    const apiKey = process.env.GOOGLE_API_KEY;

    if (!apiKey) {
      throw new Error(
        'GOOGLE_API_KEY environment variable not set. ' +
        'Get one at https://aistudio.google.com/app/apikey'
      );
    }

    this.genai = new GoogleGenerativeAI(apiKey);
    this.model = this.genai.getGenerativeModel({ model });
    this._modelName = model;
  }

  get modelName(): string {
    return this._modelName;
  }

  async chat(messages: Message[]): Promise<string> {
    // Combine system message with first user message
    let systemContent = '';
    const chatMessages: any[] = [];

    for (const msg of messages) {
      if (msg.role === 'system') {
        systemContent = msg.content + '\n\n';
      } else if (msg.role === 'user') {
        const content = systemContent + msg.content;
        chatMessages.push({ role: 'user', parts: [{ text: content }] });
        systemContent = '';
      } else if (msg.role === 'assistant') {
        chatMessages.push({ role: 'model', parts: [{ text: msg.content }] });
      }
    }

    // Simple case: single message
    if (chatMessages.length === 1) {
      const result = await this.model.generateContent(chatMessages[0].parts[0].text);
      return result.response.text();
    }

    // Multi-turn conversation
    const chat = this.model.startChat({
      history: chatMessages.slice(0, -1)
    });

    const result = await chat.sendMessage(
      chatMessages[chatMessages.length - 1].parts[0].text
    );

    return result.response.text();
  }
}

export class GroqClient extends LLMClient {
  private client: OpenAI;
  private _modelName: string;

  constructor(model: string = 'llama-3.1-70b-versatile') {
    super();
    const apiKey = process.env.GROQ_API_KEY;

    if (!apiKey) {
      throw new Error(
        'GROQ_API_KEY environment variable not set. ' +
        'Get one at https://console.groq.com/'
      );
    }

    this.client = new OpenAI({
      apiKey,
      baseURL: 'https://api.groq.com/openai/v1'
    });
    this._modelName = model;
  }

  get modelName(): string {
    return this._modelName;
  }

  async chat(messages: Message[]): Promise<string> {
    const response = await this.client.chat.completions.create({
      model: this._modelName,
      messages: messages as any,
      max_tokens: 4096
    });

    return response.choices[0]?.message?.content || '';
  }
}

export class OllamaClient extends LLMClient {
  private client: OpenAI;
  private _modelName: string;

  constructor(model: string = 'llama3.1:8b', baseURL: string = 'http://localhost:11434/v1') {
    super();

    this.client = new OpenAI({
      apiKey: 'ollama', // Required but not used
      baseURL
    });
    this._modelName = model;
  }

  get modelName(): string {
    return this._modelName;
  }

  async chat(messages: Message[]): Promise<string> {
    try {
      const response = await this.client.chat.completions.create({
        model: this._modelName,
        messages: messages as any
      });

      return response.choices[0]?.message?.content || '';
    } catch (error) {
      throw new Error(
        `Could not connect to Ollama. Make sure it's running and model '${this._modelName}' is pulled. ` +
        `Error: ${error}`
      );
    }
  }
}

// =============================================================================
// PAID PROVIDERS
// =============================================================================

export class AnthropicClient extends LLMClient {
  private client: Anthropic;
  private _modelName: string;

  constructor(model: string = 'claude-3-5-sonnet-20241022') {
    super();
    const apiKey = process.env.ANTHROPIC_API_KEY;

    if (!apiKey) {
      throw new Error(
        'ANTHROPIC_API_KEY environment variable not set. ' +
        'Get one at https://console.anthropic.com/'
      );
    }

    this.client = new Anthropic({ apiKey });
    this._modelName = model;
  }

  get modelName(): string {
    return this._modelName;
  }

  async chat(messages: Message[]): Promise<string> {
    // Extract system message
    let system: string | undefined;
    const filtered: any[] = [];

    for (const msg of messages) {
      if (msg.role === 'system') {
        system = msg.content;
      } else {
        filtered.push({ role: msg.role, content: msg.content });
      }
    }

    const response = await this.client.messages.create({
      model: this._modelName,
      max_tokens: 4096,
      system,
      messages: filtered
    });

    return response.content[0].type === 'text' ? response.content[0].text : '';
  }
}

export class OpenAIClient extends LLMClient {
  private client: OpenAI;
  private _modelName: string;

  constructor(model: string = 'gpt-4o') {
    super();
    const apiKey = process.env.OPENAI_API_KEY;

    if (!apiKey) {
      throw new Error(
        'OPENAI_API_KEY environment variable not set. ' +
        'Get one at https://platform.openai.com/'
      );
    }

    this.client = new OpenAI({ apiKey });
    this._modelName = model;
  }

  get modelName(): string {
    return this._modelName;
  }

  async chat(messages: Message[]): Promise<string> {
    const response = await this.client.chat.completions.create({
      model: this._modelName,
      messages: messages as any
    });

    return response.choices[0]?.message?.content || '';
  }
}

// =============================================================================
// FACTORY FUNCTIONS
// =============================================================================

type ProviderName = 'google' | 'groq' | 'ollama' | 'anthropic' | 'openai';

export function getLLMClient(
  provider: ProviderName = 'google',
  model?: string
): LLMClient {
  /**
   * Get an LLM client for the specified provider.
   *
   * @param provider - Provider name (default: 'google')
   * @param model - Optional model override
   * @returns LLMClient instance
   *
   * @example
   * ```typescript
   * const client = getLLMClient('google');
   * const response = await client.chat([
   *   { role: 'user', content: 'Hello!' }
   * ]);
   * ```
   */
  const providers: Record<ProviderName, [typeof LLMClient, string]> = {
    // FREE
    google: [GoogleAIClient as any, 'gemini-1.5-flash'],
    groq: [GroqClient as any, 'llama-3.1-70b-versatile'],
    ollama: [OllamaClient as any, 'llama3.1:8b'],

    // PAID
    anthropic: [AnthropicClient as any, 'claude-3-5-sonnet-20241022'],
    openai: [OpenAIClient as any, 'gpt-4o']
  };

  if (!(provider in providers)) {
    const available = Object.keys(providers).join(', ');
    throw new Error(
      `Unknown provider: ${provider}. Available: ${available}`
    );
  }

  const [ClientClass, defaultModel] = providers[provider];
  return new ClientClass(model || defaultModel);
}

export function getFreeLLMClient(provider: 'google' | 'groq' | 'ollama' = 'google'): LLMClient {
  /**
   * Get a FREE LLM client only.
   * Prevents accidental costs.
   *
   * @param provider - Free provider name
   * @returns LLMClient instance
   */
  const freeProviders = ['google', 'groq', 'ollama'];

  if (!freeProviders.includes(provider)) {
    throw new Error(
      `Provider '${provider}' is not free. Use one of: ${freeProviders.join(', ')}`
    );
  }

  return getLLMClient(provider as ProviderName);
}

export function autoSelectClient(preferFree: boolean = true): LLMClient {
  /**
   * Automatically select best available client.
   * Checks environment variables and returns first available provider.
   */
  if (preferFree) {
    if (process.env.GOOGLE_API_KEY) return getLLMClient('google');
    if (process.env.GROQ_API_KEY) return getLLMClient('groq');

    try {
      return getLLMClient('ollama');
    } catch {
      // Ollama not available
    }
  }

  // Try paid
  if (process.env.ANTHROPIC_API_KEY) return getLLMClient('anthropic');
  if (process.env.OPENAI_API_KEY) return getLLMClient('openai');

  // Fallback to free
  if (!preferFree) {
    if (process.env.GOOGLE_API_KEY) return getLLMClient('google');
    if (process.env.GROQ_API_KEY) return getLLMClient('groq');
  }

  throw new Error(
    'No LLM provider available. Set one of these environment variables:\n' +
    '  - GOOGLE_API_KEY (free, recommended)\n' +
    '  - GROQ_API_KEY (free, fast)\n' +
    '  - ANTHROPIC_API_KEY (paid)\n' +
    '  - OPENAI_API_KEY (paid)\n' +
    'Or install and run Ollama for local inference.'
  );
}

// =============================================================================
// CONVENIENCE WRAPPER
// =============================================================================

export class UnifiedLLMClient {
  private client: LLMClient;

  constructor(provider?: ProviderName, model?: string) {
    if (provider) {
      this.client = getLLMClient(provider, model);
    } else {
      this.client = autoSelectClient();
    }
  }

  async chat(messages: Message[]): Promise<string> {
    return this.client.chat(messages);
  }

  get modelName(): string {
    return this.client.modelName;
  }
}
