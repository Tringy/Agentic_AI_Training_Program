import 'dotenv/config';
import { Hono } from 'hono';
import { cors } from 'hono/cors';
import { serve } from '@hono/node-server';
import { logger, errorHandler } from './middleware.js';
import { echoGet, echoPost, processPost } from './routes.js';
import type { HealthResponse } from './types.js';

// Initialize Hono app
const app = new Hono();

// Track server start time for uptime
const startTime = Date.now();

// ============================================
// Middleware
// ============================================

// Error handler (must be first)
app.use('*', errorHandler);

// Logger middleware
app.use('*', logger);

// CORS middleware
app.use(
  '*',
  cors({
    origin: process.env.CORS_ORIGIN || '*',
    allowMethods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allowHeaders: ['Content-Type', 'Authorization'],
  })
);

// ============================================
// Routes
// ============================================

// Health check endpoint
app.get('/health', (c) => {
  const uptime = Math.floor((Date.now() - startTime) / 1000);

  const response: HealthResponse = {
    status: 'ok',
    timestamp: new Date().toISOString(),
    uptime: uptime,
  };

  return c.json(response);
});

// Root endpoint
app.get('/', (c) => {
  return c.json({
    message: 'Hono TypeScript API Template',
    version: '1.0.0',
    endpoints: {
      health: '/health',
      echo: '/echo (GET/POST)',
      process: '/process (POST)',
    },
  });
});

// Echo endpoints
app.get('/echo', echoGet);
app.post('/echo', ...echoPost);

// Process endpoint (LLM example)
app.post('/process', ...processPost);

// 404 handler
app.notFound((c) => {
  return c.json(
    {
      error: 'NotFound',
      message: 'The requested resource was not found',
      timestamp: new Date().toISOString(),
    },
    404
  );
});

// ============================================
// Server Start
// ============================================

const port = parseInt(process.env.PORT || '3000', 10);

console.log(`Starting server on port ${port}...`);

serve({
  fetch: app.fetch,
  port: port,
});

console.log(`Server running at http://localhost:${port}`);
console.log(`Health check: http://localhost:${port}/health`);
