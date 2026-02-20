/**
 * Worker agents for the multi-agent system.
 */

import type { LLMClient } from './llm-client.js';

export const RESEARCHER_PROMPT = `You are a research specialist.
Your job is to gather and summarize information on a given topic.

For the given topic:
1. Identify key facts and concepts
2. Note important details
3. Highlight relationships between ideas
4. Summarize findings clearly

Be factual and cite what you're basing your information on.`;

export const WRITER_PROMPT = `You are a professional writer.
Your job is to take research and turn it into polished content.

Given research material:
1. Organize information logically
2. Write clear, engaging prose
3. Use appropriate formatting
4. Ensure flow and readability

Match the requested tone and format.`;

export const REVIEWER_PROMPT = `You are a content reviewer.
Your job is to review content for quality and accuracy.

For the given content:
1. Check for factual accuracy
2. Identify unclear sections
3. Suggest improvements
4. Rate overall quality (1-10)

Be constructive in your feedback.`;

/**
 * Base class for worker agents.
 */
export class WorkerAgent {
  constructor(
    protected llm: LLMClient,
    protected systemPrompt: string,
    public readonly name: string
  ) {}

  async execute(task: string, context: string = ''): Promise<string> {
    let userPrompt = task;
    if (context) {
      userPrompt = `Context:\n${context}\n\nTask:\n${task}`;
    }

    return this.llm.chat([
      { role: 'system', content: this.systemPrompt },
      { role: 'user', content: userPrompt },
    ]);
  }
}

export class ResearcherAgent extends WorkerAgent {
  constructor(llm: LLMClient) {
    super(llm, RESEARCHER_PROMPT, 'Researcher');
  }
}

export class WriterAgent extends WorkerAgent {
  constructor(llm: LLMClient) {
    super(llm, WRITER_PROMPT, 'Writer');
  }
}

export class ReviewerAgent extends WorkerAgent {
  constructor(llm: LLMClient) {
    super(llm, REVIEWER_PROMPT, 'Reviewer');
  }
}
