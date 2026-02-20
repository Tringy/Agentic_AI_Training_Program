/**
 * RAG System - Type Definitions
 */

import { z } from 'zod';

// Code chunk
export interface CodeChunk {
  content: string;
  metadata: {
    filename: string;
    language: string;
    type: 'header' | 'function' | 'class' | 'block';
    name?: string;
    lineStart?: number;
    lineEnd?: number;
  };
  chunkId: string;
}

// Query result
export interface QueryResult {
  content: string;
  metadata: Record<string, unknown>;
  distance: number;
  id: string;
}

// RAG response
export interface RAGResponse {
  answer: string;
  sources: Array<{
    file: string;
    type?: string;
    name?: string;
    line?: number;
    relevance: number;
  }>;
  contextUsed: string;
}

// Evaluation types
export interface EvalExample {
  question: string;
  expectedAnswer: string;
  relevantFiles: string[];
}

export interface RetrievalMetrics {
  [key: string]: number | string;
}

export interface GenerationMetrics {
  relevance: number;
  accuracy: number;
  nExamples: number;
}

// API Request schemas
export const QueryRequestSchema = z.object({
  question: z.string().min(1),
  n_results: z.number().default(5),
  filter_language: z.string().optional(),
});
export type QueryRequest = z.infer<typeof QueryRequestSchema>;

export const IndexFilesRequestSchema = z.object({
  files: z.record(z.string()),
});
export type IndexFilesRequest = z.infer<typeof IndexFilesRequestSchema>;

export const IndexDirectoryRequestSchema = z.object({
  directory: z.string(),
  extensions: z.array(z.string()).optional(),
});
export type IndexDirectoryRequest = z.infer<typeof IndexDirectoryRequestSchema>;

export const EvalRequestSchema = z.object({
  examples: z.array(
    z.object({
      question: z.string(),
      expected_answer: z.string(),
      relevant_files: z.array(z.string()),
    })
  ),
});
export type EvalRequest = z.infer<typeof EvalRequestSchema>;
