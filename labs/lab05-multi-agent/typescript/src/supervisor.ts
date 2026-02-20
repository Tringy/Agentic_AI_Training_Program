/**
 * Supervisor agent that coordinates workers.
 */

import type { LLMClient } from './llm-client.js';
import { ResearcherAgent, WriterAgent, ReviewerAgent, WorkerAgent } from './agents.js';

const SUPERVISOR_PROMPT = `You are a supervisor managing a team of specialized agents.

Available agents:
- Researcher: Finds and summarizes information
- Writer: Creates polished content from research
- Reviewer: Reviews content for quality

Your job:
1. Analyze the incoming task
2. Decide which agent(s) to use
3. Coordinate their work
4. Synthesize the final output

For each step, output in this format:
DELEGATE: [agent_name]
TASK: [specific task for that agent]

When all work is done, output:
FINAL: [synthesized final output]`;

export interface SupervisorResult {
  result: string;
  stepsTaken: number;
}

/**
 * Supervisor that coordinates worker agents.
 */
export class SupervisorAgent {
  private workers: Map<string, WorkerAgent>;
  private results: Map<string, string> = new Map();

  constructor(private llm: LLMClient) {
    this.workers = new Map([
      ['Researcher', new ResearcherAgent(llm)],
      ['Writer', new WriterAgent(llm)],
      ['Reviewer', new ReviewerAgent(llm)],
    ]);
  }

  async run(task: string, maxIterations: number = 5): Promise<SupervisorResult> {
    // Reset results for new task
    this.results.clear();

    const messages: Array<{ role: string; content: string }> = [
      { role: 'system', content: SUPERVISOR_PROMPT },
      { role: 'user', content: `Task: ${task}` },
    ];

    for (let i = 0; i < maxIterations; i++) {
      // Get supervisor decision
      const response = await this.llm.chat(messages);
      messages.push({ role: 'assistant', content: response });

      // Check if done
      if (response.includes('FINAL:')) {
        const final = response.split('FINAL:').pop()?.trim() || '';
        return { result: final, stepsTaken: this.results.size };
      }

      // Parse and execute delegation
      if (response.includes('DELEGATE:') && response.includes('TASK:')) {
        const agentName = response
          .split('DELEGATE:')[1]
          ?.split('TASK:')[0]
          ?.trim();

        const agentTask = response.split('TASK:').pop()?.trim() || '';

        if (agentName && this.workers.has(agentName)) {
          const worker = this.workers.get(agentName)!;

          // Execute worker
          const context = this.getContext();
          const result = await worker.execute(agentTask, context);

          // Store result
          this.results.set(`${agentName}_${i}`, result);

          // Feed back to supervisor
          messages.push({
            role: 'user',
            content: `Result from ${agentName}:\n${result}`,
          });
        }
      }
    }

    return { result: this.forceFinal(), stepsTaken: this.results.size };
  }

  private getContext(): string {
    if (this.results.size === 0) {
      return '';
    }

    const parts: string[] = [];
    for (const [key, value] of this.results) {
      parts.push(`--- ${key} ---\n${value}`);
    }
    return parts.join('\n\n');
  }

  private forceFinal(): string {
    if (this.results.size > 0) {
      // Return last writer result if available
      const writerResults = Array.from(this.results.entries())
        .filter(([key]) => key.includes('Writer'))
        .map(([, value]) => value);

      if (writerResults.length > 0) {
        return writerResults[writerResults.length - 1];
      }

      // Otherwise return last result
      const values = Array.from(this.results.values());
      return values[values.length - 1];
    }

    return 'Unable to complete task.';
  }
}
