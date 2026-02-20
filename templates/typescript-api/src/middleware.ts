import { Context, Next } from 'hono';
import type { ErrorResponse } from './types.js';

// Logger Middleware
export const logger = async (c: Context, next: Next) => {
  const start = Date.now();
  const method = c.req.method;
  const path = c.req.path;

  console.log(`--> ${method} ${path}`);

  await next();

  const elapsed = Date.now() - start;
  const status = c.res.status;

  console.log(`<-- ${method} ${path} ${status} (${elapsed}ms)`);
};

// Error Handler Middleware
export const errorHandler = async (c: Context, next: Next) => {
  try {
    await next();
  } catch (error) {
    console.error('Error:', error);

    const errorResponse: ErrorResponse = {
      error: error instanceof Error ? error.name : 'UnknownError',
      message: error instanceof Error ? error.message : 'An unknown error occurred',
      timestamp: new Date().toISOString(),
    };

    return c.json(errorResponse, 500);
  }
};

// CORS Middleware (optional - use built-in Hono CORS for production)
export const customCors = async (c: Context, next: Next) => {
  const origin = process.env.CORS_ORIGIN || '*';

  c.header('Access-Control-Allow-Origin', origin);
  c.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  c.header('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  if (c.req.method === 'OPTIONS') {
    return c.text('', 204);
  }

  await next();
};
