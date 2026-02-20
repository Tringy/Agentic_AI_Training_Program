/**
 * RAG Evaluation utilities
 */

import type { LLMClient } from './llm-client.js';
import type { CodebaseRAG } from './pipeline.js';
import type {
  EvalExample,
  RetrievalMetrics,
  GenerationMetrics,
} from './types.js';

/**
 * Precision@K: fraction of retrieved docs that are relevant
 */
export function precisionAtK(
  retrieved: string[],
  relevant: Set<string>,
  k: number
): number {
  const retrievedK = retrieved.slice(0, k);
  const relevantRetrieved = retrievedK.filter((doc) => relevant.has(doc)).length;
  return k > 0 ? relevantRetrieved / k : 0;
}

/**
 * Recall@K: fraction of relevant docs that were retrieved
 */
export function recallAtK(
  retrieved: string[],
  relevant: Set<string>,
  k: number
): number {
  const retrievedK = retrieved.slice(0, k);
  const relevantRetrieved = retrievedK.filter((doc) => relevant.has(doc)).length;
  return relevant.size > 0 ? relevantRetrieved / relevant.size : 0;
}

/**
 * Mean Reciprocal Rank: how high is the first relevant result
 */
export function mrr(retrieved: string[], relevant: Set<string>): number {
  for (let i = 0; i < retrieved.length; i++) {
    if (relevant.has(retrieved[i])) {
      return 1 / (i + 1);
    }
  }
  return 0;
}

/**
 * RAG Evaluator
 */
export class RAGEvaluator {
  private rag: CodebaseRAG;
  private judge: LLMClient | null;

  constructor(ragSystem: CodebaseRAG, llmJudge?: LLMClient) {
    this.rag = ragSystem;
    this.judge = llmJudge || null;
  }

  /**
   * Evaluate retrieval quality
   */
  async evaluateRetrieval(
    examples: EvalExample[],
    k: number = 5
  ): Promise<RetrievalMetrics> {
    const metrics = {
      precision: [] as number[],
      recall: [] as number[],
      mrr: [] as number[],
    };

    for (const example of examples) {
      const result = await this.rag.query(example.question, k);
      const retrieved = result.sources.map((s) => s.file);
      const relevant = new Set(example.relevantFiles);

      metrics.precision.push(precisionAtK(retrieved, relevant, k));
      metrics.recall.push(recallAtK(retrieved, relevant, k));
      metrics.mrr.push(mrr(retrieved, relevant));
    }

    const n = examples.length;
    const avg = (arr: number[]) =>
      n > 0 ? Math.round((arr.reduce((a, b) => a + b, 0) / n) * 1000) / 1000 : 0;

    return {
      [`precision@${k}`]: avg(metrics.precision),
      [`recall@${k}`]: avg(metrics.recall),
      mrr: avg(metrics.mrr),
      n_examples: n,
    };
  }

  /**
   * Evaluate generation quality using LLM-as-judge
   */
  async evaluateGeneration(examples: EvalExample[]): Promise<GenerationMetrics> {
    if (!this.judge) {
      throw new Error('No LLM judge configured');
    }

    const scores = {
      relevance: [] as number[],
      accuracy: [] as number[],
    };

    for (const example of examples) {
      const result = await this.rag.query(example.question);
      const generated = result.answer;

      const relevance = await this.judgeRelevance(example.question, generated);
      scores.relevance.push(relevance);

      const accuracy = await this.judgeAccuracy(
        example.question,
        example.expectedAnswer,
        generated
      );
      scores.accuracy.push(accuracy);
    }

    const n = examples.length;
    const avg = (arr: number[]) =>
      n > 0 ? Math.round((arr.reduce((a, b) => a + b, 0) / n) * 1000) / 1000 : 0;

    return {
      relevance: avg(scores.relevance),
      accuracy: avg(scores.accuracy),
      nExamples: n,
    };
  }

  /**
   * Judge if answer is relevant to question
   */
  private async judgeRelevance(question: string, answer: string): Promise<number> {
    const prompt = `Rate how relevant this answer is to the question on a scale of 1-5.

Question: ${question}
Answer: ${answer}

Return only a single number from 1 to 5.`;

    const response = await this.judge!.chat([{ role: 'user', content: prompt }]);

    try {
      const score = parseFloat(response.trim());
      return Math.min(Math.max(score, 1), 5) / 5;
    } catch {
      return 0.5;
    }
  }

  /**
   * Judge if answer matches expected answer
   */
  private async judgeAccuracy(
    question: string,
    expected: string,
    generated: string
  ): Promise<number> {
    const prompt = `Compare these two answers to the same question on a scale of 1-5.

Question: ${question}
Expected Answer: ${expected}
Generated Answer: ${generated}

How well does the generated answer match the expected answer?
Return only a single number from 1 to 5.`;

    const response = await this.judge!.chat([{ role: 'user', content: prompt }]);

    try {
      const score = parseFloat(response.trim());
      return Math.min(Math.max(score, 1), 5) / 5;
    } catch {
      return 0.5;
    }
  }
}

/**
 * Create evaluation dataset from array of objects
 */
export function createEvalDataset(
  examples: Array<{
    question: string;
    expected_answer: string;
    relevant_files: string[];
  }>
): EvalExample[] {
  return examples.map((ex) => ({
    question: ex.question,
    expectedAnswer: ex.expected_answer,
    relevantFiles: ex.relevant_files,
  }));
}
