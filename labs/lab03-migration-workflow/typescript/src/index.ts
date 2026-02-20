/**
 * Migration Workflow Agent - Hono API Application
 */

import 'dotenv/config';
import { Hono } from 'hono';
import { cors } from 'hono/cors';
import { zValidator } from '@hono/zod-validator';
import { serve } from '@hono/node-server';

import { MigrationAgent } from './agent.js';
import { createInitialState } from './state.js';
import { getLLMClient, type LLMProvider } from './llm-client.js';
import { MigrationRequestSchema, type MigrationResponse } from './types.js';

const app = new Hono();

// CORS middleware
app.use('/*', cors());

// Initialize LLM client
const provider = (process.env.LLM_PROVIDER || 'anthropic') as LLMProvider;
const llm = getLLMClient(provider);

/**
 * Run migration workflow
 */
app.post('/migrate', zValidator('json', MigrationRequestSchema), async (c) => {
  try {
    const { source_framework, target_framework, files } = c.req.valid('json');

    const agent = new MigrationAgent(llm);
    const initialState = createInitialState(
      source_framework,
      target_framework,
      files
    );

    const result = await agent.run(initialState);

    const response: MigrationResponse = {
      success: result.errors.length === 0,
      migrated_files: result.migratedFiles,
      plan_executed: result.plan.map((s) => ({
        id: s.id,
        description: s.description,
        status: s.status,
      })),
      verification: result.verificationResult || {},
      errors: result.errors,
    };

    return c.json(response);
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Unknown error';
    return c.json({ error: message }, 500);
  }
});

/**
 * Health check endpoint
 */
app.get('/health', (c) => {
  return c.json({ status: 'healthy', provider });
});

/**
 * List supported frameworks
 */
app.get('/frameworks', (c) => {
  return c.json({
    supported: [
      { name: 'express', language: 'javascript' },
      { name: 'fastapi', language: 'python' },
      { name: 'flask', language: 'python' },
      { name: 'django', language: 'python' },
      { name: 'nestjs', language: 'typescript' },
      { name: 'hono', language: 'typescript' },
    ],
  });
});

// Start server
const port = parseInt(process.env.PORT || '8000', 10);

console.log(`Migration Workflow Agent starting on port ${port}...`);
console.log(`Using LLM provider: ${provider}`);

serve({
  fetch: app.fetch,
  port,
});

export default app;
