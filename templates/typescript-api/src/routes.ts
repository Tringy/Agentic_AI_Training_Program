import { Context } from 'hono';
import { zValidator } from '@hono/zod-validator';
import Anthropic from '@anthropic-ai/sdk';
import { EchoSchema, ProcessSchema } from './types.js';
import type { EchoResponse, ProcessResponse } from './types.js';

// Initialize Anthropic client
const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY || '',
});

// GET /echo - Simple echo endpoint
export const echoGet = (c: Context) => {
  const message = c.req.query('message') || 'Hello, World!';

  const response: EchoResponse = {
    message: message,
    timestamp: new Date().toISOString(),
  };

  return c.json(response);
};

// POST /echo - Echo with validation
export const echoPost = [
  zValidator('json', EchoSchema),
  async (c: Context) => {
    const { message } = c.req.valid('json');

    const response: EchoResponse = {
      message: message,
      timestamp: new Date().toISOString(),
    };

    return c.json(response);
  },
];

// POST /process - Example LLM processing endpoint
export const processPost = [
  zValidator('json', ProcessSchema),
  async (c: Context) => {
    const { prompt, model, maxTokens } = c.req.valid('json');
    const startTime = Date.now();

    try {
      const message = await anthropic.messages.create({
        model: model,
        max_tokens: maxTokens,
        messages: [
          {
            role: 'user',
            content: prompt,
          },
        ],
      });

      const processingTime = Date.now() - startTime;
      const result = message.content[0].type === 'text' ? message.content[0].text : '';

      const response: ProcessResponse = {
        result: result,
        model: model,
        processingTime: processingTime,
      };

      return c.json(response);
    } catch (error) {
      console.error('LLM processing error:', error);
      throw new Error(error instanceof Error ? error.message : 'Failed to process request');
    }
  },
];
