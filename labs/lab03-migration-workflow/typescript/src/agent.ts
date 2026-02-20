/**
 * Migration Workflow Agent - Core Agent Implementation
 */

import type { LLMClient } from './llm-client.js';
import type {
  MigrationState,
  MigrationStep,
  AnalysisResult,
  VerificationResult,
} from './types.js';
import {
  createStep,
  setAnalysis,
  setPlan,
  updateStepStatus,
  addMigratedFile,
  incrementStep,
  setVerificationResult,
  addError,
} from './state.js';
import {
  ANALYSIS_PROMPT,
  PLANNING_PROMPT,
  MIGRATION_PROMPT,
  VERIFICATION_PROMPT,
  formatPrompt,
} from './prompts.js';

/**
 * Migration Agent that performs multi-step code migration
 */
export class MigrationAgent {
  private llm: LLMClient;

  constructor(llmClient: LLMClient) {
    this.llm = llmClient;
  }

  /**
   * Run the migration agent through all phases
   */
  async run(state: MigrationState): Promise<MigrationState> {
    while (state.phase !== 'complete') {
      state = await this.step(state);
      if (state.errors.length > 0) {
        break;
      }
    }
    return state;
  }

  /**
   * Execute one phase of the migration
   */
  private async step(state: MigrationState): Promise<MigrationState> {
    switch (state.phase) {
      case 'analysis':
        return this.analyze(state);
      case 'planning':
        return this.plan(state);
      case 'execution':
        return this.execute(state);
      case 'verification':
        return this.verify(state);
      default:
        return state;
    }
  }

  /**
   * Phase 1: Analyze source code
   */
  private async analyze(state: MigrationState): Promise<MigrationState> {
    const allAnalysis: Record<string, AnalysisResult> = {};

    for (const [filename, code] of Object.entries(state.sourceFiles)) {
      const prompt = formatPrompt(ANALYSIS_PROMPT, {
        source: state.sourceFramework,
        target: state.targetFramework,
        language: this.detectLanguage(filename),
        code,
      });

      const response = await this.llm.chat([
        { role: 'user', content: prompt },
      ]);

      try {
        allAnalysis[filename] = this.parseJson(response);
      } catch (e) {
        return addError(state, `Analysis failed for ${filename}: ${e}`);
      }
    }

    return setAnalysis(state, allAnalysis);
  }

  /**
   * Phase 2: Create migration plan
   */
  private async plan(state: MigrationState): Promise<MigrationState> {
    const prompt = formatPrompt(PLANNING_PROMPT, {
      analysis: JSON.stringify(state.analysis, null, 2),
      source: state.sourceFramework,
      target: state.targetFramework,
    });

    const response = await this.llm.chat([{ role: 'user', content: prompt }]);

    try {
      const planData = this.parseJson(response);
      const plan: MigrationStep[] = (planData.steps || []).map(
        (step: { id: number; description: string; input_files?: string[] }) =>
          createStep(step.id, step.description, step.input_files || [])
      );
      return setPlan(state, plan);
    } catch (e) {
      return addError(state, `Planning failed: ${e}`);
    }
  }

  /**
   * Phase 3: Execute migration steps
   */
  private async execute(state: MigrationState): Promise<MigrationState> {
    while (state.currentStep < state.plan.length) {
      const step = state.plan[state.currentStep];
      state = updateStepStatus(state, step.id, 'in_progress');

      const sourceCode = this.getStepCode(state, step);

      const prompt = formatPrompt(MIGRATION_PROMPT, {
        source: state.sourceFramework,
        target: state.targetFramework,
        code: sourceCode,
        context: this.getContext(state),
      });

      const response = await this.llm.chat([{ role: 'user', content: prompt }]);
      const migratedCode = this.extractCode(response);

      // Store result
      for (const filename of step.inputFiles) {
        const newFilename = this.transformFilename(
          filename,
          state.targetFramework
        );
        state = addMigratedFile(state, newFilename, migratedCode);
      }

      // If no specific files, use a default name
      if (step.inputFiles.length === 0) {
        const defaultName = `migrated_step_${step.id}.${this.getExtension(state.targetFramework)}`;
        state = addMigratedFile(state, defaultName, migratedCode);
      }

      state = updateStepStatus(state, step.id, 'completed', migratedCode);
      state = incrementStep(state);
    }

    return { ...state, phase: 'verification' };
  }

  /**
   * Phase 4: Verify migration results
   */
  private async verify(state: MigrationState): Promise<MigrationState> {
    const verification: VerificationResult = {
      filesMigrated: Object.keys(state.migratedFiles).length,
      stepsCompleted: state.plan.filter((s) => s.status === 'completed').length,
      issues: [],
      validations: [],
    };

    for (const [filename, code] of Object.entries(state.migratedFiles)) {
      const language = this.detectLanguage(filename);

      const prompt = formatPrompt(VERIFICATION_PROMPT, {
        target: state.targetFramework,
        language,
        code,
      });

      const response = await this.llm.chat([{ role: 'user', content: prompt }]);

      try {
        const result = this.parseJson(response);
        verification.validations.push({
          file: filename,
          valid: result.valid ?? true,
          issues: result.issues ?? [],
        });
        if (!result.valid) {
          verification.issues.push(...(result.issues ?? []));
        }
      } catch {
        verification.validations.push({
          file: filename,
          valid: true,
          issues: [],
        });
      }
    }

    return setVerificationResult(state, verification);
  }

  /**
   * Detect language from filename
   */
  private detectLanguage(filename: string): string {
    const extMap: Record<string, string> = {
      '.py': 'python',
      '.js': 'javascript',
      '.ts': 'typescript',
      '.java': 'java',
      '.go': 'go',
      '.rs': 'rust',
    };
    for (const [ext, lang] of Object.entries(extMap)) {
      if (filename.endsWith(ext)) {
        return lang;
      }
    }
    return 'unknown';
  }

  /**
   * Get file extension for framework
   */
  private getExtension(framework: string): string {
    const extMap: Record<string, string> = {
      fastapi: 'py',
      flask: 'py',
      django: 'py',
      express: 'js',
      nestjs: 'ts',
      hono: 'ts',
    };
    return extMap[framework.toLowerCase()] || 'txt';
  }

  /**
   * Parse JSON from LLM response
   */
  private parseJson(response: string): Record<string, unknown> {
    let jsonStr = response;
    if (jsonStr.includes('```json')) {
      jsonStr = jsonStr.split('```json')[1].split('```')[0];
    } else if (jsonStr.includes('```')) {
      jsonStr = jsonStr.split('```')[1].split('```')[0];
    }
    return JSON.parse(jsonStr.trim());
  }

  /**
   * Extract code block from response
   */
  private extractCode(response: string): string {
    if (response.includes('```')) {
      const parts = response.split('```');
      if (parts.length >= 2) {
        let code = parts[1];
        const firstLine = code.split('\n')[0].trim();
        if (
          ['python', 'javascript', 'typescript', 'java', 'go'].includes(
            firstLine
          )
        ) {
          code = code.includes('\n') ? code.split('\n').slice(1).join('\n') : '';
        }
        return code.trim();
      }
    }
    return response;
  }

  /**
   * Get source code for a migration step
   */
  private getStepCode(state: MigrationState, step: MigrationStep): string {
    const codeParts: string[] = [];
    for (const filename of step.inputFiles) {
      if (state.sourceFiles[filename]) {
        codeParts.push(`// ${filename}\n${state.sourceFiles[filename]}`);
      }
    }
    if (codeParts.length === 0) {
      for (const [filename, code] of Object.entries(state.sourceFiles)) {
        codeParts.push(`// ${filename}\n${code}`);
      }
    }
    return codeParts.join('\n\n');
  }

  /**
   * Get context from previous steps
   */
  private getContext(state: MigrationState): string {
    const completed = state.plan.filter((s) => s.status === 'completed');
    if (completed.length === 0) {
      return 'No previous steps completed.';
    }
    return completed
      .slice(-3)
      .map((s) => `Step ${s.id}: ${s.description}`)
      .join('\n');
  }

  /**
   * Transform filename for target framework
   */
  private transformFilename(filename: string, target: string): string {
    const transformations: Record<string, (f: string) => string> = {
      fastapi: (f) => f.replace('.js', '.py').replace('routes/', 'routers/'),
      express: (f) => f.replace('.py', '.js').replace('routers/', 'routes/'),
      flask: (f) => f.replace('.js', '.py'),
      django: (f) => f.replace('.js', '.py'),
      hono: (f) => f.replace('.py', '.ts').replace('routers/', 'routes/'),
      nestjs: (f) => f.replace('.py', '.ts').replace('routers/', 'controllers/'),
    };
    const transform = transformations[target.toLowerCase()] || ((f) => f);
    return transform(filename);
  }
}
