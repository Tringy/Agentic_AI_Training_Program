/* TypeScript types for frontend. */

export type GameReview = {
  summary: string;
  key_moments: string[];
  tactical_analysis: string;
  performance_insights: string;
  fan_perspective: string;
  final_verdict: string;
};

export type SpecialistPerspectives = {
  journalist?: string;
  coach?: string;
  assistant_coach?: string;
  fan?: string;
  [key: string]: string | undefined;
};

export type ConversationEntry = {
  iteration: number;
  agent: string;
  action: string;
  content?: string;
  duration_ms: number;
};

export type ProgressInfo = {
  status: string;
  total_steps: number;
  completed_steps: number;
  percent_complete: number;
  current_step: string;
  planned_steps: string[];
  completed_steps_labels: string[];
  max_iterations: number;
};

export type GameMetadata = {
  game_date: string;
  home_team: string;
  away_team: string;
  final_score: string;
  competition?: string;
  stadium?: string;
  depth?: "brief" | "standard" | "detailed";
  format?: "brief" | "standard" | "technical";
  iterations?: number;
  max_iterations?: number;
  agents_used?: string[];
  duration_seconds?: number;
  agent_timings?: Record<string, number>;
  agent_metrics?: Record<string, AgentMetric>;
  total_tokens?: number;
  total_prompt_tokens?: number;
  total_completion_tokens?: number;
};

export type AgentMetric = {
  duration_ms: number;
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
};

export type MetricsSummary = {
  agent_metrics: Record<string, AgentMetric>;
  total_tokens: number;
  total_prompt_tokens: number;
  total_completion_tokens: number;
};

export type GameReviewResponse = {
  game_id: string;
  game_review: GameReview;
  specialist_perspectives: SpecialistPerspectives;
  conversation_history: ConversationEntry[];
  progress: ProgressInfo;
  metadata: GameMetadata;
};

export type APIError = {
  detail: string;
  error_code: string;
  retryable: boolean;
  request_id: string;
};
