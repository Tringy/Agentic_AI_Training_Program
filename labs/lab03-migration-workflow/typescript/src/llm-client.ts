/**
 * LLM Client Abstraction for Migration Agent
 * (Same as Lab 02 - can be shared via workspace)
 */

export interface Message {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

export abstract class LLMClient {
  abstract chat(messages: Message[]): Promise<string>;
}

export class AnthropicClient extends LLMClient {
  private client: InstanceType<typeof import('@anthropic-ai/sdk').default> | null = null;
  private model: string;

  constructor(model: string = 'claude-3-5-sonnet-20241022') {
    super();
    this.model = model;
  }

  private async ensureClient(): Promise<void> {
    if (!this.client) {
      const Anthropic = (await import('@anthropic-ai/sdk')).default;
      this.client = new Anthropic();
    }
  }

  async chat(messages: Message[]): Promise<string> {
    await this.ensureClient();

    let system: string | undefined;
    const filtered: Array<{ role: 'user' | 'assistant'; content: string }> = [];

    for (const m of messages) {
      if (m.role === 'system') {
        system = m.content;
      } else {
        filtered.push({ role: m.role, content: m.content });
      }
    }

    const response = await this.client!.messages.create({
      model: this.model,
      max_tokens: 4096,
      system,
      messages: filtered,
    });

    const textBlock = response.content.find((block) => block.type === 'text');
    return textBlock?.type === 'text' ? textBlock.text : '';
  }
}

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

  async chat(messages: Message[]): Promise<string> {
    await this.ensureClient();

    const response = await this.client!.chat.completions.create({
      model: this.model,
      messages,
    });

    return response.choices[0].message.content || '';
  }
}

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

  async chat(messages: Message[]): Promise<string> {
    await this.ensureClient();

    const model = this.client!.getGenerativeModel({ model: this.model });

    let system = '';
    let userMessage = '';

    for (const m of messages) {
      if (m.role === 'system') {
        system = m.content;
      } else if (m.role === 'user') {
        userMessage = m.content;
      }
    }

    const prompt = system ? `${system}\n\n${userMessage}` : userMessage;
    const result = await model.generateContent(prompt);
    return result.response.text();
  }
}

export type LLMProvider = 'anthropic' | 'openai' | 'google';

export function getLLMClient(provider: LLMProvider = 'anthropic'): LLMClient {
  switch (provider) {
    case 'anthropic':
      return new AnthropicClient();
    case 'openai':
      return new OpenAIClient();
    case 'google':
      return new GoogleClient();
    default:
      throw new Error(`Unknown provider: ${provider}`);
  }
}
