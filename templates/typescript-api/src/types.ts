import { z } from 'zod';

// Request/Response Types
export interface HealthResponse {
  status: 'ok' | 'error';
  timestamp: string;
  uptime: number;
}

export interface EchoResponse {
  message: string;
  timestamp: string;
}

export interface ProcessResponse {
  result: string;
  model: string;
  processingTime: number;
}

export interface ErrorResponse {
  error: string;
  message: string;
  timestamp: string;
}

// Zod Schemas for Validation
export const EchoSchema = z.object({
  message: z.string().min(1).max(1000),
});

export const ProcessSchema = z.object({
  prompt: z.string().min(1).max(5000),
  model: z.string().optional().default('claude-3-5-sonnet-20241022'),
  maxTokens: z.number().optional().default(1024),
});

export type EchoInput = z.infer<typeof EchoSchema>;
export type ProcessInput = z.infer<typeof ProcessSchema>;
