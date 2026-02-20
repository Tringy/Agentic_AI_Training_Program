/**
 * Multi-Agent System - Hono API Application
 */

import 'dotenv/config';
import { Hono } from 'hono';
import { cors } from 'hono/cors';
import { zValidator } from '@hono/zod-validator';
import { serve } from '@hono/node-server';
import { z } from 'zod';

import { SupervisorAgent } from './supervisor.js';
import { getLLMClient, type LLMProvider } from './llm-client.js';

const app = new Hono();

// CORS middleware
app.use('/*', cors());

// Initialize
const provider = (process.env.LLM_PROVIDER || 'anthropic') as LLMProvider;
const llm = getLLMClient(provider);
const supervisor = new SupervisorAgent(llm);

// Request schemas
const TaskRequestSchema = z.object({
  task: z.string().min(1),
  max_iterations: z.number().int().min(1).max(10).default(5),
});

/**
 * Run a multi-agent task
 */
app.post('/run', zValidator('json', TaskRequestSchema), async (c) => {
  try {
    const { task, max_iterations } = c.req.valid('json');
    const result = await supervisor.run(task, max_iterations);

    return c.json({
      result: result.result,
      steps_taken: result.stepsTaken,
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Unknown error';
    return c.json({ error: message }, 500);
  }
});

/**
 * Health check
 */
app.get('/health', (c) => {
  return c.json({ status: 'healthy', provider });
});

// Start server
const port = parseInt(process.env.PORT || '8000', 10);

console.log(`Multi-Agent System starting on port ${port}...`);
console.log(`Using LLM provider: ${provider}`);

serve({
  fetch: app.fetch,
  port,
});

export default app;
