"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";
import type { GameReviewResponse } from "@/types";
import MetricsPanel from "./MetricsPanel";

interface ReviewResultProps {
  result: GameReviewResponse | null;
}

interface CollapsibleSectionProps {
  title: string;
  content: string | string[] | undefined | null;
  expanded: boolean;
  onToggle: () => void;
  icon: string;
}

function CollapsibleSection({
  title,
  content,
  expanded,
  onToggle,
  icon,
}: CollapsibleSectionProps) {
  const safe = content ?? "";
  const contentText =
    typeof safe === "string" ? safe : safe.join("\n• ");

  return (
    <div className="border border-gray-700 rounded-lg overflow-hidden mb-4">
      <button
        onClick={onToggle}
        className="w-full px-6 py-4 bg-gray-800 hover:bg-gray-700 flex items-center justify-between transition-colors"
      >
        <span className="flex items-center gap-3 font-semibold text-lg">
          <span>{icon}</span>
          {title}
        </span>
        <span className={`transform transition-transform ${expanded ? "rotate-180" : ""}`}>
          ▼
        </span>
      </button>
      {expanded && (
        <div className="px-6 py-4 bg-gray-900 border-t border-gray-700 prose prose-invert prose-sm max-w-none">
          <ReactMarkdown>{
            typeof safe === "string" ? safe : safe.map((s) => `- ${s}`).join("\n")
          }</ReactMarkdown>
        </div>
      )}
    </div>
  );
}

export default function ReviewResult({ result }: ReviewResultProps) {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(
    new Set(["summary"])
  );

  if (!result) {
    return null;
  }

  const toggleSection = (section: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(section)) {
      newExpanded.delete(section);
    } else {
      newExpanded.add(section);
    }
    setExpandedSections(newExpanded);
  };

  const { game_review, specialist_perspectives, metadata, progress } = result;

  return (
    <div className="space-y-6">
      {/* Game Header */}
      <div className="pitch-gradient rounded-lg p-6 text-white shadow-lg">
        <div className="flex justify-between items-center">
          <div>
            <p className="text-goal-yellow font-semibold text-sm">
              {metadata.competition && `${metadata.competition} · `}{metadata.game_date}
            </p>
            {metadata.format && (
              <p className="text-xs text-gray-300 mt-1">
                Report: <span className="text-goal-accent font-semibold capitalize">{metadata.format}</span>
              </p>
            )}
            <h2 className="text-2xl font-bold mt-1">
              {metadata.home_team} vs {metadata.away_team}
            </h2>
            <p className="text-4xl font-bold mt-1">{metadata.final_score}</p>
          </div>
          {metadata.stadium && (
            <div className="text-right text-sm text-gray-200">
              🏟️ {metadata.stadium}
            </div>
          )}
        </div>
        <div className="mt-4 grid gap-3 md:grid-cols-4">
          <div className="rounded border border-white/10 bg-black/15 px-3 py-2">
            <p className="text-[11px] uppercase tracking-wide text-gray-300">Progress</p>
            <p className="text-lg font-bold">{progress.percent_complete}%</p>
          </div>
          <div className="rounded border border-white/10 bg-black/15 px-3 py-2">
            <p className="text-[11px] uppercase tracking-wide text-gray-300">Steps</p>
            <p className="text-lg font-bold">{progress.completed_steps}/{progress.total_steps}</p>
          </div>
          <div className="rounded border border-white/10 bg-black/15 px-3 py-2">
            <p className="text-[11px] uppercase tracking-wide text-gray-300">Iterations</p>
            <p className="text-lg font-bold">{metadata.iterations}/{metadata.max_iterations ?? progress.max_iterations}</p>
          </div>
          <div className="rounded border border-white/10 bg-black/15 px-3 py-2">
            <p className="text-[11px] uppercase tracking-wide text-gray-300">Agents Used</p>
            <p className="text-lg font-bold">{metadata.agents_used?.length ?? 0}</p>
          </div>
        </div>
      </div>

      {/* Performance Metrics */}
      {metadata.agent_metrics && Object.keys(metadata.agent_metrics).length > 0 && (
        <div className="mt-8 pt-8 border-t border-gray-700">
          <MetricsPanel
            metrics={{
              agent_metrics: metadata.agent_metrics,
              total_tokens: metadata.total_tokens ?? 0,
              total_prompt_tokens: metadata.total_prompt_tokens ?? 0,
              total_completion_tokens: metadata.total_completion_tokens ?? 0,
            }}
            expanded={expandedSections.has("metrics")}
            onToggle={() => toggleSection("metrics")}
          />
        </div>
      )}

      {/* Game Review Sections */}
      <div className="space-y-4">
        <h3 className="text-2xl font-bold text-goal-yellow">Match Analysis</h3>

        <CollapsibleSection
          title="Game Summary"
          content={game_review.summary}
          expanded={expandedSections.has("summary")}
          onToggle={() => toggleSection("summary")}
          icon="📰"
        />

        <CollapsibleSection
          title="Key Moments"
          content={game_review.key_moments}
          expanded={expandedSections.has("moments")}
          onToggle={() => toggleSection("moments")}
          icon="⚡"
        />

        <CollapsibleSection
          title="Tactical Analysis"
          content={game_review.tactical_analysis}
          expanded={expandedSections.has("tactics")}
          onToggle={() => toggleSection("tactics")}
          icon="🎯"
        />

        <CollapsibleSection
          title="Performance Insights"
          content={game_review.performance_insights}
          expanded={expandedSections.has("performance")}
          onToggle={() => toggleSection("performance")}
          icon="📊"
        />

        <CollapsibleSection
          title="Fan Perspective"
          content={specialist_perspectives.fan}
          expanded={expandedSections.has("fan")}
          onToggle={() => toggleSection("fan")}
          icon="🔥"
        />

        <CollapsibleSection
          title="Final Verdict"
          content={game_review.final_verdict}
          expanded={expandedSections.has("verdict")}
          onToggle={() => toggleSection("verdict")}
          icon="🏆"
        />
      </div>

      {/* Specialist Perspectives */}
      <div className="space-y-4 mt-8 pt-8 border-t border-gray-700">
        <h3 className="text-2xl font-bold text-goal-yellow">Specialist Views</h3>

        <CollapsibleSection
          title="Journalist's Report"
          content={specialist_perspectives.journalist}
          expanded={expandedSections.has("journalist")}
          onToggle={() => toggleSection("journalist")}
          icon="📻"
        />

        <CollapsibleSection
          title="Coach's Analysis"
          content={specialist_perspectives.coach}
          expanded={expandedSections.has("coach")}
          onToggle={() => toggleSection("coach")}
          icon="👨‍🏫"
        />

        <CollapsibleSection
          title="Assistant Coach's Breakdown"
          content={specialist_perspectives.assistant_coach}
          expanded={expandedSections.has("asst_coach")}
          onToggle={() => toggleSection("asst_coach")}
          icon="📋"
        />
      </div>
    </div>
  );
}
