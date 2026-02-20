/**
 * Code Analyzer Agent - Type Definitions
 */

import { z } from 'zod';

// Severity levels for issues
export const SeveritySchema = z.enum(['critical', 'high', 'medium', 'low']);
export type Severity = z.infer<typeof SeveritySchema>;

// Issue categories
export const CategorySchema = z.enum([
  'bug',
  'security',
  'performance',
  'style',
  'maintainability',
]);
export type Category = z.infer<typeof CategorySchema>;

// Complexity levels
export const ComplexitySchema = z.enum(['low', 'medium', 'high']);
export type Complexity = z.infer<typeof ComplexitySchema>;

// Readability levels
export const ReadabilitySchema = z.enum(['poor', 'fair', 'good', 'excellent']);
export type Readability = z.infer<typeof ReadabilitySchema>;

// Test coverage estimate
export const TestCoverageSchema = z.enum(['none', 'partial', 'good']);
export type TestCoverage = z.infer<typeof TestCoverageSchema>;

// Issue schema
export const IssueSchema = z.object({
  severity: SeveritySchema,
  line: z.number().nullable(),
  category: CategorySchema,
  description: z.string(),
  suggestion: z.string(),
});
export type Issue = z.infer<typeof IssueSchema>;

// Metrics schema
export const MetricsSchema = z.object({
  complexity: ComplexitySchema,
  readability: ReadabilitySchema,
  test_coverage_estimate: TestCoverageSchema,
});
export type Metrics = z.infer<typeof MetricsSchema>;

// Analysis result schema
export const AnalysisResultSchema = z.object({
  summary: z.string(),
  issues: z.array(IssueSchema),
  suggestions: z.array(z.string()),
  metrics: MetricsSchema,
});
export type AnalysisResult = z.infer<typeof AnalysisResultSchema>;

// Request schema
export const AnalyzeRequestSchema = z.object({
  code: z.string().min(1, 'Code is required'),
  language: z.string().default('python'),
});
export type AnalyzeRequest = z.infer<typeof AnalyzeRequestSchema>;
