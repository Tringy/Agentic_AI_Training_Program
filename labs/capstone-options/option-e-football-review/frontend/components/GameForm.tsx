"use client";

import { useState, useEffect } from "react";
import { parseApiError } from "@/lib/apiError";
import type { APIError, GameReviewResponse } from "@/types";

export interface Game {
  id: string;
  date: string;
  home_team: string;
  away_team: string;
  final_score: string;
  competition: string;
  stadium: string;
  scorers: { minute: number; player: string; team: string }[];
}

interface GamePickerProps {
  onGameSelected: (sessionId: string, result: GameReviewResponse) => void;
}

export default function GameForm({ onGameSelected }: GamePickerProps) {
  const [games, setGames] = useState<Game[]>([]);
  const [loading, setLoading] = useState(true);
  const [reviewLoading, setReviewLoading] = useState(false);
  const [error, setError] = useState<APIError | null>(null);
  const [selectedGame, setSelectedGame] = useState<string | null>(null);
  const [depth, setDepth] = useState<"brief" | "standard" | "detailed">("standard");
  const [format, setFormat] = useState<"brief" | "standard" | "technical">("standard");
  const [maxIterations, setMaxIterations] = useState<1 | 2 | 3 | 4>(4);
  const [lastAttempt, setLastAttempt] = useState<{ gameId: string } | null>(null);

  useEffect(() => {
    const fetchGames = async () => {
      try {
        setLoading(true);
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/games`
        );
        if (!response.ok) {
          const body = await response.json();
          throw parseApiError(body);
        }
        const data = await response.json();
        setGames(data.games);
      } catch (err) {
        if (typeof err === "object" && err !== null && "error_code" in err) {
          setError(err as APIError);
        } else {
          setError({
            detail: err instanceof Error ? err.message : "Failed to load games",
            error_code: "HTTP_ERROR",
            retryable: false,
            request_id: "unknown",
          });
        }
      } finally {
        setLoading(false);
      }
    };

    fetchGames();
  }, []);

  const handleSelectGame = async (gameId: string, force = false) => {
    if (!force && selectedGame === gameId) return; // Already selected

    setSelectedGame(gameId);
    setReviewLoading(true);
    setError(null);
    setLastAttempt({ gameId });

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/games/${gameId}/review?depth=${depth}&format=${format}&max_iterations=${maxIterations}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw parseApiError(errorData);
      }

      const result: GameReviewResponse = await response.json();
      onGameSelected(result.game_id, result);
    } catch (err) {
      if (typeof err === "object" && err !== null && "error_code" in err) {
        setError(err as APIError);
      } else {
        setError({
          detail: err instanceof Error ? err.message : "An error occurred",
          error_code: "HTTP_ERROR",
          retryable: false,
          request_id: "unknown",
        });
      }
      setSelectedGame(null);
    } finally {
      setReviewLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="w-full max-w-2xl mx-auto p-6 text-center">
        <div className="text-goal-accent animate-pulse">Loading games...</div>
      </div>
    );
  }

  if (error && games.length === 0) {
    return (
      <div className="w-full max-w-2xl mx-auto p-6 bg-red-900/20 border border-red-500 rounded-lg text-red-300">
        <p className="font-semibold">Error: {error.detail}</p>
        <p className="text-xs text-red-200 mt-1">Code: {error.error_code} · Request: {error.request_id}</p>
        {error.retryable && <p className="text-xs mt-2">This error is retryable.</p>}
      </div>
    );
  }

  return (
    <div className="w-full max-w-2xl mx-auto p-6">
      <h2 className="text-2xl font-bold text-goal-accent mb-6">
        Select a Game to Review
      </h2>

      {error && games.length > 0 && (
        <div className="bg-red-900/20 border border-red-500 text-red-300 px-4 py-3 rounded mb-6">
          <p className="font-semibold">{error.detail}</p>
          <p className="text-xs text-red-200 mt-1">Code: {error.error_code} · Request: {error.request_id}</p>
          {error.retryable && (
            <div className="mt-3 flex items-center gap-3">
              <span className="text-xs">This error is retryable.</span>
              <button
                type="button"
                onClick={() => lastAttempt && handleSelectGame(lastAttempt.gameId, true)}
                disabled={reviewLoading || !lastAttempt}
                className="text-xs px-3 py-1 rounded border border-red-300 hover:bg-red-800 disabled:opacity-50"
              >
                Retry
              </button>
            </div>
          )}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div className="flex flex-col gap-2">
          <label htmlFor="depth" className="text-sm font-semibold text-goal-accent">
            Analysis Depth
          </label>
          <select
            id="depth"
            value={depth}
            onChange={(e) => setDepth(e.target.value as "brief" | "standard" | "detailed")}
            className="px-3 py-2 bg-gray-800 border border-gray-600 rounded text-gray-100"
            disabled={reviewLoading}
          >
            <option value="brief">Brief (fast)</option>
            <option value="standard">Standard (balanced)</option>
            <option value="detailed">Detailed (comprehensive)</option>
          </select>
        </div>
        <div className="flex flex-col gap-2">
          <label htmlFor="format" className="text-sm font-semibold text-goal-accent">
            Report Format
          </label>
          <select
            id="format"
            value={format}
            onChange={(e) => setFormat(e.target.value as "brief" | "standard" | "technical")}
            className="px-3 py-2 bg-gray-800 border border-gray-600 rounded text-gray-100"
            disabled={reviewLoading}
          >
            <option value="brief">Brief (summary)</option>
            <option value="standard">Standard (balanced)</option>
            <option value="technical">Technical (detailed stats)</option>
          </select>
        </div>
      </div>

      <div className="mb-6 flex flex-col gap-2">
        <label htmlFor="max-iterations" className="text-sm font-semibold text-goal-accent">
          Max Iterations
        </label>
        <select
          id="max-iterations"
          value={maxIterations}
          onChange={(e) => setMaxIterations(Number(e.target.value) as 1 | 2 | 3 | 4)}
          className="px-3 py-2 bg-gray-800 border border-gray-600 rounded text-gray-100"
          disabled={reviewLoading}
        >
          <option value={1}>1 specialist</option>
          <option value={2}>2 specialists</option>
          <option value={3}>3 specialists</option>
          <option value={4}>4 specialists</option>
        </select>
        <p className="text-xs text-gray-400">
          Controls how many specialist agents run before synthesis.
        </p>
      </div>

      <div className="grid gap-4">
        {games.map((game) => (
          <button
            key={game.id}
            onClick={() => handleSelectGame(game.id)}
            disabled={reviewLoading}
            className={`p-4 rounded-lg border-2 text-left transition-all ${
              selectedGame === game.id
                ? "border-goal-accent bg-goal-accent/10"
                : "border-goal-shadow/30 hover:border-goal-accent/50"
            } ${
              reviewLoading && selectedGame === game.id
                ? "opacity-50 cursor-not-allowed"
                : "cursor-pointer"
            }`}
          >
            <div className="flex justify-between items-start mb-2">
              <h3 className="text-lg font-bold text-white">
                {game.home_team} vs {game.away_team}
              </h3>
              <span className="text-goal-accent font-bold text-xl">
                {game.final_score}
              </span>
            </div>
            <div className="text-sm text-goal-accent/70 space-y-1 mb-3">
              <p>📅 {game.date} &nbsp;·&nbsp; 🏆 {game.competition} &nbsp;·&nbsp; 🏟️ {game.stadium}</p>
            </div>
            {game.scorers.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {game.scorers.map((s, idx) => (
                  <span
                    key={idx}
                    className="text-xs bg-goal-shadow/20 border border-goal-shadow/30 rounded px-2 py-0.5 text-white"
                  >
                    ⚽ {s.minute}&apos; {s.player}
                  </span>
                ))}
              </div>
            )}
            {selectedGame === game.id && reviewLoading && (
              <div className="mt-3 text-goal-accent text-sm animate-pulse">
                Analyzing match...
              </div>
            )}
          </button>
        ))}
      </div>
    </div>
  );
}
