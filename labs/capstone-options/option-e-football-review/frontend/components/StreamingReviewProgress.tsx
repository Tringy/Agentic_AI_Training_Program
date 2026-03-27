"use client";

import { useEffect, useState } from "react";
import type { GameReviewResponse } from "@/types";

interface StreamingReviewProgressProps {
  gameId: string;
  depth?: "brief" | "standard" | "detailed";
  format?: "brief" | "standard" | "technical";
  onComplete: (review: GameReviewResponse) => void;
  onError: (error: string) => void;
}

interface StreamEvent {
  state: "agent_thinking" | "agent_working" | "chunk" | "complete" | "error";
  message?: string;
  agent?: string;
  insight?: string;
  review?: GameReviewResponse;
  detail?: string;
}

export default function StreamingReviewProgress({
  gameId,
  depth = "standard",
  format = "standard",
  onComplete,
  onError,
}: StreamingReviewProgressProps) {
  const [events, setEvents] = useState<StreamEvent[]>([]);
  const [isConnecting, setIsConnecting] = useState(true);

  useEffect(() => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    const streamUrl = `${apiUrl}/games/${gameId}/review/stream?depth=${depth}&format=${format}`;

    const startStreaming = async () => {
      try {
        const response = await fetch(streamUrl, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        console.log("✅ Streaming connection established");

        const reader = response.body?.getReader();
        const decoder = new TextDecoder();

        if (!reader) {
          throw new Error("Response body is not readable");
        }

        let buffer = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n");

          // Keep the last incomplete line in the buffer
          buffer = lines.pop() || "";

          for (const line of lines) {
            if (line.startsWith("data: ")) {
              try {
                const jsonStr = line.slice(6);
                const data = JSON.parse(jsonStr) as StreamEvent;

                console.log("📊 Event received:", data.state, data);
                setEvents((prev) => [...prev, data]);

                if (data.state === "complete" && data.review) {
                  setIsConnecting(false);
                  onComplete(data.review);
                } else if (data.state === "error") {
                  setIsConnecting(false);
                  onError(data.detail || "Streaming error");
                }
              } catch (parseErr) {
                console.error("Failed to parse SSE line:", line, parseErr);
              }
            }
          }
        }

        // Process any remaining buffer
        if (buffer.trim().startsWith("data: ")) {
          try {
            const jsonStr = buffer.trim().slice(6);
            const data = JSON.parse(jsonStr) as StreamEvent;
            setEvents((prev) => [...prev, data]);

            if (data.state === "complete" && data.review) {
              setIsConnecting(false);
              onComplete(data.review);
            } else if (data.state === "error") {
              setIsConnecting(false);
              onError(data.detail || "Streaming error");
            }
          } catch (parseErr) {
            console.error("Failed to parse final SSE line:", buffer, parseErr);
          }
        }
      } catch (error) {
        setIsConnecting(false);
        onError(
          error instanceof Error ? error.message : "Unknown streaming error"
        );
      }
    };

    startStreaming();
  }, [gameId, depth, format, onComplete, onError]);

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 text-sm text-gray-400">
        <div
          className={`w-2 h-2 rounded-full ${
            isConnecting ? "bg-goal-accent animate-pulse" : "bg-green-400"
          }`}
        />
        {isConnecting ? "Streaming..." : "Complete"}
      </div>

      <div className="space-y-2 max-h-96 overflow-y-auto">
        {events.length === 0 ? (
          <div className="text-center text-gray-400 py-4">
            Waiting for stream...
          </div>
        ) : (
          events.map((event, i) => (
            <div
              key={i}
              className="flex items-start gap-3 px-4 py-3 bg-gray-900 border border-gray-700 rounded animate-in fade-in"
            >
              <div className="w-2 h-2 mt-1.5 bg-goal-accent rounded-full flex-shrink-0 animate-pulse" />
              <div className="flex-1 min-w-0">
                {event.state === "agent_thinking" && (
                  <>
                    <span className="text-sm font-semibold text-goal-accent">
                      🧠 Analyzing
                    </span>
                    {event.message && (
                      <p className="text-xs text-gray-400 mt-1">
                        {event.message}
                      </p>
                    )}
                  </>
                )}
                {event.state === "agent_working" && (
                  <>
                    <span className="text-sm font-semibold text-goal-yellow">
                      ⚙️ {event.agent || "Agent"}
                    </span>
                    {event.message && (
                      <p className="text-xs text-gray-400 mt-1">
                        {event.message}
                      </p>
                    )}
                  </>
                )}
                {event.state === "chunk" && (
                  <>
                    <span className="text-sm font-semibold text-cyan-400">
                      💡 Insight
                    </span>
                    {event.insight && (
                      <p className="text-xs text-gray-300 mt-1 line-clamp-2">
                        {event.insight}
                      </p>
                    )}
                  </>
                )}
                {event.state === "complete" && (
                  <span className="text-sm font-semibold text-green-400">
                    ✅ Analysis Complete
                  </span>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
