export interface TaskRequest {
  task: string;
  max_iterations: number;
  require_approval?: boolean;
}

export interface AgentTraceEntry {
  agent: string;
  parallel_group: number;
  duration_ms: number;
}

export interface TaskResponse {
  result: string;
  steps_taken: number;
  memory_context_used: boolean;
  workers_used: string[];
  agent_trace: AgentTraceEntry[];
}

export interface MemoryEntry {
  id: number;
  task: string;
  summary: string;
  created_at: string;
}

export interface MemoryListResponse {
  entries: MemoryEntry[];
  total: number;
}

export interface JobStartResponse {
  job_id: string;
  status: string;
  intermediate: Record<string, string>;
}

export interface JobStatusResponse {
  job_id: string;
  status: string;
  intermediate: Record<string, string>;
  result?: string;
  steps_taken: number;
  workers_used: string[];
  agent_trace: AgentTraceEntry[];
}

export interface ApproveRequest {
  override_task?: string;
}

export interface AgentDef {
  name: string;
  description: string;
  builtin: boolean;
}

export interface AgentsListResponse {
  agents: AgentDef[];
}

export interface AgentCreateRequest {
  name: string;
  system_prompt: string;
  description: string;
}
