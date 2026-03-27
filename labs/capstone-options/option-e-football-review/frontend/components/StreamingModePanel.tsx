"use client";

import { useEffect, useState } from "react";
import type { GameReviewResponse, APIError } from "@/types";
import { parseApiError } from "@/lib/apiError";
import StreamingReviewProgress from "./StreamingReviewProgress";
import ReviewResult from "./ReviewResult";

interface StreamingModePanelProps {
  onGameSelected: (gameId: string) => void;
  selectedGameId: string | null;
  depth: "brief" | "standard" | "detailed";
  onDepthChange: (depth: "brief" | "standard" | "detailed") => void;
  format: "brief" | "standard" | "technical";
  onFormatChange: (format: "brief" | "standard" | "technical") => void;
  onBackClick: () => void;
}

interface Game {
  id: string;
  home_team: string;
  away_team: string;
  date: string;
}

export default function StreamingModePanel({
  onGameSelected,
  selectedGameId,
  depth,
  onDepthChange,
  format,
  onFormatChange,
  onBackClick,
}: StreamingModePanelProps) {
  const [games, setGames] = useState<Game[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<APIError | null>(null);
  const [streamingComplete, setStreamingComplete] = useState(false);
  const [streamingResult, setStreamingResult] = useState<GameReviewResponse | null>(null);

  useEffect(() => {
    const fetchGames = async () => {
      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/games`
        );
        if (!response.ok) {
          throw parseApiError(await response.json());
        }
        const data = await response.json();
        setGames(data.games || []);
      } catch (err) {
        if (typeof err === "object" && err !== null && "error_code" in err) {
          setError(err as APIError);
        }
      } finally {
        setLoading(false);
      }
    };

    fetchGames();
  }, []);

  if (streamingComplete && streamingResult) {
    return (
      <div className="space-y-6">
        <button
          onClick={() => {
            setStreamingComplete(false);
            setStreamingResult(null);
            onGameSelected(selectedGameId || "");
          }}
          className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded text-sm font-semibold transition-colors"
        >
          ← Try Another Game
        </button>
        <ReviewResult result={streamingResult} />
      </div>
    );
  }

  if (selectedGameId) {
    return (
      <div className="space-y-6">
        <button
          onClick={() => {
            onGameSelected("");
          }}
          className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded text-sm font-semibold transition-colors"
        >
          ← Select Different Game
        </button>

        <div className="bg-gradient-to-br from-pitch-900 to-pitch-800 rounded-lg p-6 border border-goal-shadow/30">
          <h3 className="text-xl font-bold text-goal-accent mb-6">
            🔴 Real-Time Stream Analysis
          </h3>

          <div className="grid grid-cols-2 gap-4 mb-6">
            <div>
              <label className="block text-sm font-semibold text-goal-yellow mb-2">
                Analysis Depth
              </label>
              <select
                value={depth}
                onChange={(e) =>
                  onDepthChange(
                    e.target.value as "brief" | "standard" | "detailed"
                  )
                }
                className="w-full px-4 py-2 bg-gray-800 border border-gray-600 rounded text-gray-100 focus:outline-none focus:border-goal-accent"
              >
                <option value="brief">Brief (Quick summary)</option>
                <option value="standard">Standard (Balanced)</option>
                <option value="detailed">Detailed (Comprehensive)</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-semibold text-goal-yellow mb-2">
                Output Format
              </label>
              <select
                value={format}
                onChange={(e) =>
                  onFormatChange(
                    e.target.value as "brief" | "standard" | "technical"
                  )
                }
                className="w-full px-4 py-2 bg-gray-800 border border-gray-600 rounded text-gray-100 focus:outline-none focus:border-goal-accent"
              >
                <option value="brief">Brief (Simple narrative)</option>
                <option value="standard">Standard (Balanced)</option>
                <option value="technical">Technical (Detailed stats)</option>
              </select>
            </div>
          </div>

          <StreamingReviewProgress
            gameId={selectedGameId}
            depth={depth}
            format={format}
            onComplete={(review) => {
              setStreamingResult(review);
              setStreamingComplete(true);
            }}
            onError={(err) => {
              setError({
                detail: err,
                error_code: "STREAM_ERROR",
                retryable: true,
                request_id: "unknown",
              });
            }}
          />
        </div>

        {error && (
          <div className="bg-red-900/20 border border-red-500 text-red-300 px-4 py-3 rounded">
            <p className="font-semibold">{error.detail}</p>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {error && (
        <div className="bg-red-900/20 border border-red-500 text-red-300 px-4 py-3 rounded">
          <p className="font-semibold">{error.detail}</p>
        </div>
      )}

      <div className="bg-gradient-to-br from-pitch-900 to-pitch-800 rounded-lg p-6 border border-goal-shadow/30">
        <h2 className="text-2xl font-bold text-goal-accent mb-4">
          🔴 Stream Testing Mode
        </h2>
        <p className="text-gray-300 mb-6">
          Watch the AI analyze a match in real-time. Select a game below and
          choose your preferred analysis depth and format.
        </p>

        {loading ? (
          <div className="text-center py-8 text-gray-400">Loading games...</div>
        ) : games.length === 0 ? (
          <div className="text-center py-8 text-gray-400">No games available</div>
        ) : (
          <div className="grid gap-3">
            {games.map((game) => (
              <button
                key={game.id}
                onClick={() => onGameSelected(game.id)}
                className="text-left p-4 bg-gray-800 border border-gray-700 rounded hover:border-goal-accent transition-colors group"
              >
                <div className="flex justify-between items-center">
                  <div>
                    <h3 className="font-semibold text-gray-100 group-hover:text-goal-accent transition-colors">
                      {game.home_team} vs {game.away_team}
                    </h3>
                    <p className="text-sm text-gray-400">{game.date}</p>
                  </div>
                  <span className="text-goal-accent text-xl">→</span>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>

      <button
        onClick={onBackClick}
        className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded text-sm font-semibold transition-colors"
      >
        ← Back to Standard Mode
      </button>
    </div>
  );
}
