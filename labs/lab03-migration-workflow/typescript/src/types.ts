/**
 * Migration Workflow Agent - Type Definitions
 */

import { z } from 'zod';

// Phase enum
export const PhaseSchema = z.enum([
  'analysis',
  'planning',
  'execution',
  'verification',
  'complete',
]);
export type Phase = z.infer<typeof PhaseSchema>;

// Migration step
export interface MigrationStep {
  id: number;
  description: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  inputFiles: string[];
  outputFiles: string[];
  result?: string;
}

// Analysis result
export interface AnalysisResult {
  components: Array<{
    name: string;
    type: 'class' | 'function' | 'route';
    description: string;
  }>;
  dependencies: string[];
  patterns: Array<{
    pattern: string;
    description: string;
    migrationNote: string;
  }>;
  challenges: Array<{
    issue: string;
    severity: 'low' | 'medium' | 'high';
    suggestion: string;
  }>;
}

// Verification result
export interface VerificationResult {
  filesMigrated: number;
  stepsCompleted: number;
  issues: Array<{
    line?: number;
    issue: string;
    suggestion: string;
  }>;
  validations: Array<{
    file: string;
    valid: boolean;
    issues: Array<{ line?: number; issue: string; suggestion: string }>;
  }>;
}

// Migration state
export interface MigrationState {
  sourceFramework: string;
  targetFramework: string;
  sourceFiles: Record<string, string>;
  phase: Phase;
  analysis: Record<string, AnalysisResult> | null;
  plan: MigrationStep[];
  currentStep: number;
  migratedFiles: Record<string, string>;
  verificationResult: VerificationResult | null;
  errors: string[];
}

// API Request/Response schemas
export const MigrationRequestSchema = z.object({
  source_framework: z.string(),
  target_framework: z.string(),
  files: z.record(z.string()),
});
export type MigrationRequest = z.infer<typeof MigrationRequestSchema>;

export interface StepResult {
  id: number;
  description: string;
  status: string;
}

export interface MigrationResponse {
  success: boolean;
  migrated_files: Record<string, string>;
  plan_executed: StepResult[];
  verification: VerificationResult | Record<string, never>;
  errors: string[];
}
