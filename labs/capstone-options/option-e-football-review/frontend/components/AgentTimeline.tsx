"use client";

import type { ConversationEntry } from "@/types";

interface AgentTimelineProps {
  history: ConversationEntry[];
}

export default function AgentTimeline({ history }: AgentTimelineProps) {
  if (!history || history.length === 0) {
    return (
      <div className="rounded-lg border border-gray-700 bg-gray-900 p-4 text-sm text-gray-400">
        No workflow events available.
      </div>
    );
  }

  return (
    <div className="space-y-3" data-testid="agent-timeline">
      {history.map((entry, index) => (
        <div
          key={`${entry.iteration}-${entry.agent}-${index}`}
          className="grid grid-cols-[140px_16px_1fr] gap-3 items-start"
          data-testid="timeline-node"
        >
          <div className="text-right">
            <p className="text-sm font-semibold text-goal-accent">{entry.agent}</p>
            <p className="text-xs text-gray-400">Iteration {entry.iteration}</p>
          </div>

          <div className="flex flex-col items-center h-full pt-1">
            <div className="h-3 w-3 rounded-full bg-goal-accent" />
            {index < history.length - 1 && <div className="mt-1 w-px flex-1 bg-gray-700" />}
          </div>

          <div className="rounded-lg border border-gray-700 bg-gray-900 px-4 py-3">
            <div className="flex items-center gap-2">
              <span className="rounded bg-pitch-800 px-2 py-0.5 text-xs font-semibold text-goal-accent">
                {entry.action}
              </span>
              <span className="text-xs text-gray-400">{entry.duration_ms} ms</span>
            </div>
            {entry.content && (
              <p className="mt-2 text-sm text-gray-200 leading-relaxed">{entry.content}</p>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
