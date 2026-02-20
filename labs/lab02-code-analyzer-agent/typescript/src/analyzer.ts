/**
 * Code Analyzer Implementation
 */

import type { LLMClient } from './llm-client.js';
import type { AnalysisResult } from './types.js';
import { AnalysisResultSchema } from './types.js';
import {
  CODE_ANALYZER_SYSTEM,
  SECURITY_FOCUS_PROMPT,
  PERFORMANCE_FOCUS_PROMPT,
} from './prompts.js';

/**
 * LLM-powered code analyzer
 */
export class CodeAnalyzer {
  private llm: LLMClient;
  private systemPrompt: string;

  constructor(llmClient: LLMClient) {
    this.llm = llmClient;
    this.systemPrompt = CODE_ANALYZER_SYSTEM;
  }

  /**
   * Analyze code and return structured result
   */
  async analyze(code: string, language: string = 'python'): Promise<AnalysisResult> {
    const userPrompt = `Analyze this ${language} code:

\`\`\`${language}
${code}
\`\`\`

Return your analysis as JSON.`;

    const response = await this.llm.chat([
      { role: 'system', content: this.systemPrompt },
      { role: 'user', content: userPrompt },
    ]);

    return this.parseResponse(response);
  }

  /**
   * Security-focused analysis
   */
  async analyzeSecurity(
    code: string,
    language: string = 'python'
  ): Promise<AnalysisResult> {
    const userPrompt = `Analyze this ${language} code for security vulnerabilities:

\`\`\`${language}
${code}
\`\`\`

${SECURITY_FOCUS_PROMPT}`;

    const response = await this.llm.chat([
      { role: 'system', content: this.systemPrompt },
      { role: 'user', content: userPrompt },
    ]);

    return this.parseResponse(response);
  }

  /**
   * Performance-focused analysis
   */
  async analyzePerformance(
    code: string,
    language: string = 'python'
  ): Promise<AnalysisResult> {
    const userPrompt = `Analyze this ${language} code for performance issues:

\`\`\`${language}
${code}
\`\`\`

${PERFORMANCE_FOCUS_PROMPT}`;

    const response = await this.llm.chat([
      { role: 'system', content: this.systemPrompt },
      { role: 'user', content: userPrompt },
    ]);

    return this.parseResponse(response);
  }

  /**
   * Parse LLM response into structured result
   */
  private parseResponse(response: string): AnalysisResult {
    let jsonStr = response;

    // Handle markdown code blocks
    if (jsonStr.includes('```json')) {
      jsonStr = jsonStr.split('```json')[1].split('```')[0];
    } else if (jsonStr.includes('```')) {
      jsonStr = jsonStr.split('```')[1].split('```')[0];
    }

    const data = JSON.parse(jsonStr.trim());

    // Validate with Zod schema
    return AnalysisResultSchema.parse(data);
  }
}
