/**
 * Vector Store - ChromaDB + OpenAI Embeddings
 */

import type { QueryResult } from './types.js';

/**
 * Interface for embedding providers
 */
export interface EmbeddingProvider {
  embed(texts: string[]): Promise<number[][]>;
}

/**
 * OpenAI Embeddings provider
 */
export class OpenAIEmbeddings implements EmbeddingProvider {
  private client: InstanceType<typeof import('openai').default> | null = null;
  private model: string;

  constructor(model: string = 'text-embedding-3-small') {
    this.model = model;
  }

  private async ensureClient(): Promise<void> {
    if (!this.client) {
      const OpenAI = (await import('openai')).default;
      this.client = new OpenAI();
    }
  }

  async embed(texts: string[]): Promise<number[][]> {
    await this.ensureClient();

    const response = await this.client!.embeddings.create({
      model: this.model,
      input: texts,
    });

    return response.data.map((d) => d.embedding);
  }
}

/**
 * Simple in-memory vector store (for demo purposes)
 * In production, use ChromaDB or Pinecone client
 */
export class InMemoryVectorStore {
  private documents: Map<
    string,
    {
      content: string;
      metadata: Record<string, unknown>;
      embedding: number[];
    }
  > = new Map();
  private embeddings: EmbeddingProvider;

  constructor(embeddings: EmbeddingProvider) {
    this.embeddings = embeddings;
  }

  /**
   * Add documents with embeddings
   */
  async addDocuments(
    documents: string[],
    metadatas: Record<string, unknown>[],
    ids: string[]
  ): Promise<void> {
    const embeddings = await this.embeddings.embed(documents);

    for (let i = 0; i < documents.length; i++) {
      this.documents.set(ids[i], {
        content: documents[i],
        metadata: metadatas[i],
        embedding: embeddings[i],
      });
    }
  }

  /**
   * Query for similar documents
   */
  async query(
    queryText: string,
    nResults: number = 5,
    where?: Record<string, unknown>
  ): Promise<QueryResult[]> {
    const [queryEmbedding] = await this.embeddings.embed([queryText]);

    // Calculate cosine similarity for all documents
    const results: Array<{ id: string; distance: number }> = [];

    for (const [id, doc] of this.documents) {
      // Apply filter if specified
      if (where) {
        let matches = true;
        for (const [key, value] of Object.entries(where)) {
          if (doc.metadata[key] !== value) {
            matches = false;
            break;
          }
        }
        if (!matches) continue;
      }

      const similarity = this.cosineSimilarity(queryEmbedding, doc.embedding);
      const distance = 1 - similarity; // Convert to distance
      results.push({ id, distance });
    }

    // Sort by distance (ascending)
    results.sort((a, b) => a.distance - b.distance);

    // Return top N results
    return results.slice(0, nResults).map(({ id, distance }) => {
      const doc = this.documents.get(id)!;
      return {
        content: doc.content,
        metadata: doc.metadata,
        distance,
        id,
      };
    });
  }

  /**
   * Get collection stats
   */
  getStats(): { count: number; name: string } {
    return {
      count: this.documents.size,
      name: 'in-memory',
    };
  }

  /**
   * Clear all documents
   */
  clear(): void {
    this.documents.clear();
  }

  /**
   * Calculate cosine similarity between two vectors
   */
  private cosineSimilarity(a: number[], b: number[]): number {
    let dotProduct = 0;
    let normA = 0;
    let normB = 0;

    for (let i = 0; i < a.length; i++) {
      dotProduct += a[i] * b[i];
      normA += a[i] * a[i];
      normB += b[i] * b[i];
    }

    return dotProduct / (Math.sqrt(normA) * Math.sqrt(normB));
  }
}

/**
 * Create a vector store with OpenAI embeddings
 */
export function createVectorStore(): InMemoryVectorStore {
  return new InMemoryVectorStore(new OpenAIEmbeddings());
}
