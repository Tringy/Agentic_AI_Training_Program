export interface Issue {
  severity: 'critical' | 'high' | 'medium' | 'low'
  line?: number | null
  category: string
  description: string
  suggestion: string
}

export interface Metrics {
  complexity: string
  readability: string
  test_coverage_estimate: string
}

export interface AnalysisResult {
  summary: string
  issues: Issue[]
  suggestions: string[]
  metrics: Metrics
}

export interface FileInput {
  filename: string
  code: string
  language: string
}

export interface FileAnalysis {
  filename: string
  result: AnalysisResult
}

export interface MultiFileResult {
  files: FileAnalysis[]
  relationships: string[]
  overall_summary: string
}

export interface DetectionResult {
  language: string
  confidence: 'high' | 'medium' | 'low'
  alternatives: string[]
}

export interface CacheStats {
  total_entries: number
  alive: number
  expired: number
}

export interface DiffResult {
  introduced: Issue[]
  resolved: Issue[]
  regressions: string[]
  change_summary: string
  metrics_before: Metrics
  metrics_after: Metrics
}
