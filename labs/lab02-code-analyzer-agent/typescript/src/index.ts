/**
 * Code Analyzer Agent - Hono API Application
 */

import 'dotenv/config';
import { Hono } from 'hono';
import { cors } from 'hono/cors';
import { zValidator } from '@hono/zod-validator';
import { serve } from '@hono/node-server';

import { CodeAnalyzer } from './analyzer.js';
import { getLLMClient, type LLMProvider } from './llm-client.js';
import { AnalyzeRequestSchema, type AnalysisResult } from './types.js';

const app = new Hono();

// CORS middleware
app.use('/*', cors());

// Initialize analyzer with configured provider
const provider = (process.env.LLM_PROVIDER || 'anthropic') as LLMProvider;
const llm = getLLMClient(provider);
const analyzer = new CodeAnalyzer(llm);

/**
 * Analyze code and return structured feedback
 */
app.post('/analyze', zValidator('json', AnalyzeRequestSchema), async (c) => {
  try {
    const { code, language } = c.req.valid('json');
    const result: AnalysisResult = await analyzer.analyze(code, language);
    return c.json(result);
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Unknown error';
    return c.json({ error: message }, 500);
  }
});

/**
 * Security-focused code analysis
 */
app.post(
  '/analyze/security',
  zValidator('json', AnalyzeRequestSchema),
  async (c) => {
    try {
      const { code, language } = c.req.valid('json');
      const result: AnalysisResult = await analyzer.analyzeSecurity(
        code,
        language
      );
      return c.json(result);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      return c.json({ error: message }, 500);
    }
  }
);

/**
 * Performance-focused code analysis
 */
app.post(
  '/analyze/performance',
  zValidator('json', AnalyzeRequestSchema),
  async (c) => {
    try {
      const { code, language } = c.req.valid('json');
      const result: AnalysisResult = await analyzer.analyzePerformance(
        code,
        language
      );
      return c.json(result);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      return c.json({ error: message }, 500);
    }
  }
);

/**
 * Health check endpoint
 */
app.get('/health', (c) => {
  return c.json({ status: 'healthy', provider });
});

// Start server
const port = parseInt(process.env.PORT || '8000', 10);

console.log(`Code Analyzer Agent starting on port ${port}...`);
console.log(`Using LLM provider: ${provider}`);

serve({
  fetch: app.fetch,
  port,
});

export default app;
