// Shared TypeScript types for the migration API

export interface StepResult {
  id: number
  description: string
  status: 'pending' | 'in_progress' | 'completed' | 'failed'
  wave_index?: number
  dependencies?: number[]
}

export interface ValidationEntry {
  file: string
  valid: boolean
  issues: string[]
}

export interface VerificationResult {
  files_migrated: number
  steps_completed: number
  issues: string[]
  validations: ValidationEntry[]
}

export interface MigrationResponse {
  success: boolean
  migrated_files: Record<string, string>
  plan_executed: StepResult[]
  verification: VerificationResult
  errors: string[]
}

/** HTTP 202 response from POST /migrate — plan ready for review */
export interface ApprovalPlanResponse {
  job_id: string
  status: 'awaiting_approval'
  plan: StepResult[]
  analysis?: Record<string, unknown>
}

/** POST /migrate/{job_id}/approve */
export interface ApproveResponse {
  job_id: string
  status: 'executing'
}

/** GET /migrate/{job_id}/reject */
export interface RejectResponse {
  job_id: string
  status: 'rejected'
}

export interface WaveStep {
  id: number
  description: string
  status: string
}

export interface WaveProgress {
  wave_index: number
  steps: WaveStep[]
}

/** GET /migrate/{job_id}/progress */
export interface ProgressResponse {
  job_id: string
  phase: string
  execution_mode: string
  waves: WaveProgress[]
}

export type JobStatus =
  | 'awaiting_approval'
  | 'executing'
  | 'completed'
  | 'failed'
  | 'rejected'
  | 'timed_out'

/** GET /migrate/{job_id}/status */
export interface JobStatusResponse {
  job_id: string
  status: JobStatus
  phase: string
  plan_executed: StepResult[]
  migrated_files: Record<string, string>
  verification: VerificationResult
  errors: string[]
}

export const SUPPORTED_FRAMEWORKS = [
  { name: 'express', language: 'JavaScript' },
  { name: 'fastapi', language: 'Python' },
  { name: 'flask', language: 'Python' },
  { name: 'django', language: 'Python' },
  { name: 'nestjs', language: 'TypeScript' },
  { name: 'hono', language: 'TypeScript' },
  { name: 'dataform', language: 'SQLX' },
  { name: 'dbt', language: 'SQL' },
]

export interface FrameworkProfile {
  name: string
  language: string
  file_extensions: string[]
  description: string
  migration_notes: string[]
  idiomatic_patterns: string[]
  independent_file_types: string[]
}

export interface DetectFrameworkResponse {
  detected_source: string | null
  confidence: 'high' | 'medium' | 'low'
  alternatives: string[]
  evidence: string[]
}

export interface Snapshot {
  step_index: number
  step_description: string
  timestamp: string
  files_count: number
}

export interface RollbackRecord {
  timestamp: string
  from_step: number
  to_step: number
  reason: 'automatic' | 'manual'
}

export interface RollbackResponse {
  success: boolean
  rolled_back_to_step: number
  migrated_files_count: number
  migrated_files: Record<string, string>
  plan_executed: StepResult[]
}
