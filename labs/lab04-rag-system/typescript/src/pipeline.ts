/**
 * RAG Pipeline - Complete RAG implementation
 */

import type { LLMClient } from './llm-client.js';
import type { RAGResponse, QueryResult } from './types.js';
import { CodeChunker } from './chunker.js';
import { InMemoryVectorStore, createVectorStore } from './vector-store.js';
import * as fs from 'node:fs/promises';
import * as path from 'node:path';

const RAG_SYSTEM_PROMPT = `You are a helpful assistant that answers questions about code.
Use the provided code context to answer questions accurately.
If the context doesn't contain enough information, say so.
Always reference specific files and line numbers when possible.`;

const RAG_USER_PROMPT = `Based on the following code context, answer the question.

Context:
{context}

Question: {question}

Provide a clear, accurate answer based on the code context above.`;

export class CodebaseRAG {
  private llm: LLMClient;
  private vectorStore: InMemoryVectorStore;
  private chunker: CodeChunker;

  constructor(llmClient: LLMClient) {
    this.llm = llmClient;
    this.vectorStore = createVectorStore();
    this.chunker = new CodeChunker();
  }

  /**
   * Index a directory of code files
   */
  async indexDirectory(
    directory: string,
    extensions: string[] = ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go']
  ): Promise<number> {
    const documents: string[] = [];
    const metadatas: Record<string, unknown>[] = [];
    const ids: string[] = [];

    const skipDirs = new Set([
      '.git',
      'node_modules',
      '__pycache__',
      '.venv',
      'venv',
      'dist',
      'build',
      '.next',
    ]);

    async function walkDir(dir: string, baseDir: string): Promise<void> {
      const entries = await fs.readdir(dir, { withFileTypes: true });

      for (const entry of entries) {
        const fullPath = path.join(dir, entry.name);

        if (entry.isDirectory()) {
          if (!skipDirs.has(entry.name)) {
            await walkDir(fullPath, baseDir);
          }
        } else if (entry.isFile()) {
          if (extensions.some((ext) => entry.name.endsWith(ext))) {
            try {
              const content = await fs.readFile(fullPath, 'utf-8');
              const relativePath = path.relative(baseDir, fullPath);
              const chunks = this.chunker.chunkFile(content, relativePath);

              for (const chunk of chunks) {
                documents.push(chunk.content);
                metadatas.push(chunk.metadata as Record<string, unknown>);
                ids.push(chunk.chunkId);
              }
            } catch (error) {
              console.error(`Error processing ${fullPath}:`, error);
            }
          }
        }
      }
    }

    await walkDir(directory, directory);

    if (documents.length > 0) {
      await this.vectorStore.addDocuments(documents, metadatas, ids);
      console.log(`Indexed ${documents.length} chunks from ${directory}`);
    }

    return documents.length;
  }

  /**
   * Index files from a dictionary
   */
  async indexFiles(files: Record<string, string>): Promise<number> {
    const documents: string[] = [];
    const metadatas: Record<string, unknown>[] = [];
    const ids: string[] = [];

    for (const [filename, content] of Object.entries(files)) {
      const chunks = this.chunker.chunkFile(content, filename);

      for (const chunk of chunks) {
        documents.push(chunk.content);
        metadatas.push(chunk.metadata as Record<string, unknown>);
        ids.push(chunk.chunkId);
      }
    }

    if (documents.length > 0) {
      await this.vectorStore.addDocuments(documents, metadatas, ids);
    }

    return documents.length;
  }

  /**
   * Query the codebase
   */
  async query(
    question: string,
    nResults: number = 5,
    filterLanguage?: string
  ): Promise<RAGResponse> {
    // Build filter
    const where = filterLanguage ? { language: filterLanguage } : undefined;

    // Retrieve relevant chunks
    const results = await this.vectorStore.query(question, nResults, where);

    if (results.length === 0) {
      return {
        answer: 'No relevant code found for this question.',
        sources: [],
        contextUsed: '',
      };
    }

    // Build context
    const context = this.buildContext(results);

    // Generate answer
    const prompt = RAG_USER_PROMPT.replace('{context}', context).replace(
      '{question}',
      question
    );

    const response = await this.llm.chat([
      { role: 'system', content: RAG_SYSTEM_PROMPT },
      { role: 'user', content: prompt },
    ]);

    return {
      answer: response,
      sources: results.map((r) => ({
        file: r.metadata.filename as string,
        type: r.metadata.type as string | undefined,
        name: r.metadata.name as string | undefined,
        line: r.metadata.lineStart as number | undefined,
        relevance: Math.round((1 - r.distance) * 1000) / 1000,
      })),
      contextUsed: context,
    };
  }

  /**
   * Build context string from results
   */
  private buildContext(results: QueryResult[]): string {
    const parts: string[] = [];

    for (const r of results) {
      const metadata = r.metadata;
      let header = `File: ${metadata.filename}`;
      if (metadata.name) {
        header += ` | ${metadata.type || 'block'}: ${metadata.name}`;
      }
      if (metadata.lineStart) {
        header += ` | Line: ${metadata.lineStart}`;
      }

      parts.push(`--- ${header} ---\n${r.content}`);
    }

    return parts.join('\n\n');
  }

  /**
   * Get index statistics
   */
  getStats(): { count: number; name: string } {
    return this.vectorStore.getStats();
  }

  /**
   * Clear the index
   */
  clearIndex(): void {
    this.vectorStore.clear();
  }
}
