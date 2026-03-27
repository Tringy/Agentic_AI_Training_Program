"use client";

import { AgentMetric, MetricsSummary } from "@/types";

interface MetricsPanelProps {
  metrics?: MetricsSummary;
  expanded: boolean;
  onToggle: () => void;
}

export default function MetricsPanel({ metrics, expanded, onToggle }: MetricsPanelProps) {
  if (!metrics || !metrics.agent_metrics || Object.keys(metrics.agent_metrics).length === 0) {
    return null;
  }

  const agents = Object.entries(metrics.agent_metrics);

  return (
    <div className="border border-gray-700 rounded-lg overflow-hidden mb-4">
      <button
        onClick={onToggle}
        className="w-full px-6 py-4 bg-gray-800 hover:bg-gray-700 flex items-center justify-between transition-colors"
      >
        <span className="flex items-center gap-3 font-semibold text-lg">
          <span>📊</span>
          Performance Metrics
        </span>
        <span className={`transform transition-transform ${expanded ? "rotate-180" : ""}`}>
          ▼
        </span>
      </button>

      {expanded && (
        <div className="px-6 py-4 bg-gray-900 border-t border-gray-700 space-y-4">
          {/* Summary Cards */}
          <div className="grid grid-cols-3 gap-3">
            <div className="px-4 py-3 bg-gray-800 border border-gray-700 rounded">
              <div className="text-xs text-gray-400 uppercase tracking-wide">Total Tokens</div>
              <div className="text-2xl font-bold text-goal-accent">{metrics.total_tokens?.toLocaleString() || 0}</div>
            </div>
            <div className="px-4 py-3 bg-gray-800 border border-gray-700 rounded">
              <div className="text-xs text-gray-400 uppercase tracking-wide">Prompt Tokens</div>
              <div className="text-2xl font-bold text-blue-400">{metrics.total_prompt_tokens?.toLocaleString() || 0}</div>
            </div>
            <div className="px-4 py-3 bg-gray-800 border border-gray-700 rounded">
              <div className="text-xs text-gray-400 uppercase tracking-wide">Completion Tokens</div>
              <div className="text-2xl font-bold text-emerald-400">{metrics.total_completion_tokens?.toLocaleString() || 0}</div>
            </div>
          </div>

          {/* Per-Agent Breakdown */}
          <div className="border border-gray-700 rounded overflow-hidden">
            <div className="bg-gray-800 px-4 py-3 border-b border-gray-700">
              <h4 className="text-sm font-semibold text-gray-200">Agent Token Usage</h4>
            </div>
            <div className="divide-y divide-gray-700">
              {agents.map(([agentName, metric]) => {
                const agentPercent = Math.min(100, (metric.total_tokens / (metrics.total_tokens || 1)) * 100);
                return (
                  <div key={agentName} className="px-4 py-3 hover:bg-gray-800/50 transition-colors">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-200">{agentName}</span>
                      <span className="text-xs text-gray-400">{metric.duration_ms}ms</span>
                    </div>
                    <div className="flex items-center gap-4 text-xs">
                      <div className="flex-1">
                        <div className="flex justify-between mb-1">
                          <span className="text-gray-400">Tokens:</span>
                          <span className="text-goal-accent font-medium">{metric.total_tokens.toLocaleString()}</span>
                        </div>
                        <div className="w-full bg-gray-700 rounded-full h-2">
                          <div
                            className="bg-goal-accent rounded-full h-2 transition-all"
                            style={{
                              width: `${agentPercent}%`,
                            }}
                          />
                        </div>
                      </div>
                      <div className="text-gray-500 text-right min-w-fit whitespace-nowrap">
                        <div className="text-xs">{metric.prompt_tokens}p</div>
                        <div className="text-xs">{metric.completion_tokens}c</div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
