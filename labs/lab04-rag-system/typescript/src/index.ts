/**
 * RAG System - Hono API Application
 */

import 'dotenv/config';
import { Hono } from 'hono';
import { cors } from 'hono/cors';
import { zValidator } from '@hono/zod-validator';
import { serve } from '@hono/node-server';

import { CodebaseRAG } from './pipeline.js';
import { RAGEvaluator, createEvalDataset } from './evaluation.js';
import { getLLMClient, type LLMProvider } from './llm-client.js';
import {
  QueryRequestSchema,
  IndexFilesRequestSchema,
  IndexDirectoryRequestSchema,
  EvalRequestSchema,
} from './types.js';

const app = new Hono();

// CORS middleware
app.use('/*', cors());

// Initialize RAG
const provider = (process.env.LLM_PROVIDER || 'anthropic') as LLMProvider;
const llm = getLLMClient(provider);
const rag = new CodebaseRAG(llm);

/**
 * Index a directory
 */
app.post(
  '/index/directory',
  zValidator('json', IndexDirectoryRequestSchema),
  async (c) => {
    try {
      const { directory, extensions } = c.req.valid('json');
      const count = await rag.indexDirectory(directory, extensions);
      return c.json({ indexed_chunks: count, directory });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      return c.json({ error: message }, 500);
    }
  }
);

/**
 * Index files from request body
 */
app.post('/index/files', zValidator('json', IndexFilesRequestSchema), async (c) => {
  try {
    const { files } = c.req.valid('json');
    const count = await rag.indexFiles(files);
    return c.json({ indexed_chunks: count, files: Object.keys(files) });
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Unknown error';
    return c.json({ error: message }, 500);
  }
});

/**
 * Query the codebase
 */
app.post('/query', zValidator('json', QueryRequestSchema), async (c) => {
  try {
    const { question, n_results, filter_language } = c.req.valid('json');
    const result = await rag.query(question, n_results, filter_language);
    return c.json({
      answer: result.answer,
      sources: result.sources,
      context_used: result.contextUsed,
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Unknown error';
    return c.json({ error: message }, 500);
  }
});

/**
 * Evaluate RAG performance
 */
app.post('/evaluate', zValidator('json', EvalRequestSchema), async (c) => {
  try {
    const { examples } = c.req.valid('json');
    const evalExamples = createEvalDataset(examples);
    const evaluator = new RAGEvaluator(rag, llm);

    const retrievalMetrics = await evaluator.evaluateRetrieval(evalExamples);
    const generationMetrics = await evaluator.evaluateGeneration(evalExamples);

    return c.json({
      retrieval: retrievalMetrics,
      generation: generationMetrics,
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Unknown error';
    return c.json({ error: message }, 500);
  }
});

/**
 * Get index statistics
 */
app.get('/stats', (c) => {
  return c.json(rag.getStats());
});

/**
 * Clear the index
 */
app.delete('/index', (c) => {
  rag.clearIndex();
  return c.json({ status: 'cleared' });
});

/**
 * Health check
 */
app.get('/health', (c) => {
  return c.json({ status: 'healthy', provider });
});

// Start server
const port = parseInt(process.env.PORT || '8000', 10);

console.log(`RAG System starting on port ${port}...`);
console.log(`Using LLM provider: ${provider}`);

serve({
  fetch: app.fetch,
  port,
});

export default app;
