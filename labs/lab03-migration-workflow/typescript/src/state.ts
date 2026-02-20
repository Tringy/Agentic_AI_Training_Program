/**
 * Migration Workflow Agent - State Management
 */

import type {
  MigrationState,
  MigrationStep,
  Phase,
  AnalysisResult,
  VerificationResult,
} from './types.js';

/**
 * Create initial migration state
 */
export function createInitialState(
  sourceFramework: string,
  targetFramework: string,
  sourceFiles: Record<string, string>
): MigrationState {
  return {
    sourceFramework,
    targetFramework,
    sourceFiles,
    phase: 'analysis',
    analysis: null,
    plan: [],
    currentStep: 0,
    migratedFiles: {},
    verificationResult: null,
    errors: [],
  };
}

/**
 * Create a migration step
 */
export function createStep(
  id: number,
  description: string,
  inputFiles: string[] = []
): MigrationStep {
  return {
    id,
    description,
    status: 'pending',
    inputFiles,
    outputFiles: [],
    result: undefined,
  };
}

/**
 * Update state phase
 */
export function setPhase(state: MigrationState, phase: Phase): MigrationState {
  return { ...state, phase };
}

/**
 * Set analysis result
 */
export function setAnalysis(
  state: MigrationState,
  analysis: Record<string, AnalysisResult>
): MigrationState {
  return { ...state, analysis, phase: 'planning' };
}

/**
 * Set migration plan
 */
export function setPlan(
  state: MigrationState,
  plan: MigrationStep[]
): MigrationState {
  return { ...state, plan, phase: 'execution' };
}

/**
 * Update step status
 */
export function updateStepStatus(
  state: MigrationState,
  stepId: number,
  status: MigrationStep['status'],
  result?: string
): MigrationState {
  const plan = state.plan.map((step) =>
    step.id === stepId ? { ...step, status, result } : step
  );
  return { ...state, plan };
}

/**
 * Add migrated file
 */
export function addMigratedFile(
  state: MigrationState,
  filename: string,
  content: string
): MigrationState {
  return {
    ...state,
    migratedFiles: { ...state.migratedFiles, [filename]: content },
  };
}

/**
 * Increment current step
 */
export function incrementStep(state: MigrationState): MigrationState {
  return { ...state, currentStep: state.currentStep + 1 };
}

/**
 * Set verification result
 */
export function setVerificationResult(
  state: MigrationState,
  result: VerificationResult
): MigrationState {
  return { ...state, verificationResult: result, phase: 'complete' };
}

/**
 * Add error
 */
export function addError(state: MigrationState, error: string): MigrationState {
  return { ...state, errors: [...state.errors, error] };
}
