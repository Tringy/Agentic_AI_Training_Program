"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";
import AgentTimeline from "@/components/AgentTimeline";
import GameForm from "@/components/GameForm";
import StreamingReviewProgress from "@/components/StreamingReviewProgress";
import StreamingModePanel from "@/components/StreamingModePanel";
import { parseApiError } from "@/lib/apiError";
import ReviewResult from "@/components/ReviewResult";
import type { APIError, GameReviewResponse } from "@/types";

interface FollowUpReview {
  question: string;
  answer: Record<string, unknown>;
  timestamp: string;
}

export default function Home() {
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [reviewResult, setReviewResult] = useState<GameReviewResponse | null>(
    null
  );
  const [followUpReviews, setFollowUpReviews] = useState<FollowUpReview[]>([]);
  const [followUpQuestion, setFollowUpQuestion] = useState("");
  const [followUpLoading, setFollowUpLoading] = useState(false);
  const [followUpError, setFollowUpError] = useState<APIError | null>(null);
  const [lastFollowUpQuestion, setLastFollowUpQuestion] = useState<string | null>(null);
  
  // Streaming mode state
  const [streamingMode, setStreamingMode] = useState(false);
  const [selectedGameForStream, setSelectedGameForStream] = useState<string | null>(null);
  const [streamDepth, setStreamDepth] = useState<"brief" | "standard" | "detailed">("standard");
  const [streamFormat, setStreamFormat] = useState<"brief" | "standard" | "technical">("standard");

  const handleGameSelected = (sessionId: string, result: GameReviewResponse) => {
    setCurrentSessionId(sessionId);
    setReviewResult(result);
    setFollowUpReviews([]);
    setFollowUpQuestion("");
    setFollowUpError(null);
  };

  const sendFollowUp = async (questionText: string) => {
    if (!currentSessionId || questionText.trim().length < 5) return;

    setFollowUpLoading(true);
    setFollowUpError(null);
    setLastFollowUpQuestion(questionText);

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/games/${currentSessionId}/ask`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ question: questionText }),
        }
      );

      if (!response.ok) {
        throw parseApiError(await response.json());
      }

      const result = await response.json();
      setFollowUpReviews((prev) => [
        ...prev,
        {
          question: questionText,
          answer: result.answer,
          timestamp: new Date().toISOString(),
        },
      ]);
      setFollowUpQuestion("");
    } catch (err) {
      if (typeof err === "object" && err !== null && "error_code" in err) {
        setFollowUpError(err as APIError);
      } else {
        setFollowUpError({
          detail: err instanceof Error ? err.message : "An error occurred",
          error_code: "HTTP_ERROR",
          retryable: false,
          request_id: "unknown",
        });
      }
    } finally {
      setFollowUpLoading(false);
    }
  };

  const handleFollowUpSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await sendFollowUp(followUpQuestion);
  };

  const handleStreamGame = async (gameId: string) => {
    setStreamingMode(true);
    setSelectedGameForStream(gameId);
    setReviewResult(null);
    setCurrentSessionId(null);

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/games/${gameId}/stream`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            depth: streamDepth,
            format: streamFormat,
          }),
        }
      );

      if (!response.ok) {
        throw parseApiError(await response.json());
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) return;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        // Process streaming chunks here
        const text = decoder.decode(value);
        console.log("Stream chunk:", text);
      }
    } catch (err) {
      console.error("Streaming error:", err);
    } finally {
      setStreamingMode(false);
      setSelectedGameForStream(null);
    }
  };

  return (
    <div className="space-y-8">
      {/* Instructions */}
      <div className="bg-blue-900 border border-blue-700 rounded-lg p-4">
        <h3 className="font-semibold text-blue-100 mb-2">💡 How to Use</h3>
        <p className="text-blue-100 text-sm">
          Select a match from our catalog. Our multi-agent AI system will
          automatically analyze it from four different perspectives: journalistic
          narrative, tactical analysis, performance insights, and fan commentary.
          You can then ask follow-up questions about the match.
        </p>
      </div>

      {/* Streaming Mode Toggle */}
      <div className="flex gap-2 justify-center mb-4">
        <button
          onClick={() => {
            setStreamingMode(false);
            setSelectedGameForStream(null);
            setReviewResult(null);
          }}
          className={`px-4 py-2 rounded font-semibold transition-colors ${
            !streamingMode
              ? "bg-goal-accent text-pitch-900"
              : "bg-gray-700 hover:bg-gray-600 text-gray-100"
          }`}
        >
          📋 Standard Mode
        </button>
        <button
          onClick={() => setStreamingMode(true)}
          className={`px-4 py-2 rounded font-semibold transition-colors ${
            streamingMode
              ? "bg-goal-accent text-pitch-900"
              : "bg-gray-700 hover:bg-gray-600 text-gray-100"
          }`}
        >
          🔴 Stream Mode (Live)
        </button>
      </div>

      {/* Game Picker */}
      {!reviewResult && !streamingMode ? (
        <GameForm onGameSelected={handleGameSelected} />
      ) : streamingMode ? (
        <StreamingModePanel
          onGameSelected={(gameId) => {
            setSelectedGameForStream(gameId);
          }}
          selectedGameId={selectedGameForStream}
          depth={streamDepth}
          onDepthChange={setStreamDepth}
          format={streamFormat}
          onFormatChange={setStreamFormat}
          onBackClick={() => {
            setStreamingMode(false);
            setSelectedGameForStream(null);
          }}
        />
      ) : (
        <div>
          {/* Back Button */}
          <button
            onClick={() => {
              setCurrentSessionId(null);
              setReviewResult(null);
              setFollowUpReviews([]);
              setFollowUpQuestion("");
              setFollowUpError(null);
            }}
            className="mb-6 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded text-sm font-semibold transition-colors"
          >
            ← Select Another Game
          </button>

          {/* Review Results */}
          <ReviewResult result={reviewResult} />

          <div className="mt-8 pt-8 border-t border-gray-700">
            <h3 className="text-2xl font-bold text-goal-yellow mb-6">
              Agent Workflow Timeline
            </h3>
            <AgentTimeline history={reviewResult?.conversation_history ?? []} />
          </div>

          {/* Follow-up Questions Section */}
          {currentSessionId && (
            <div className="mt-8 bg-gradient-to-br from-pitch-900 to-pitch-800 rounded-lg p-6 border border-goal-shadow/30">
              <h3 className="text-xl font-bold text-goal-accent mb-4">
                Ask a Follow-up Question
              </h3>

              {followUpError && (
                <div className="bg-red-900/20 border border-red-500 text-red-300 px-4 py-3 rounded mb-4">
                  <p className="font-semibold">{followUpError.detail}</p>
                  <p className="text-xs text-red-200 mt-1">
                    Code: {followUpError.error_code} · Request: {followUpError.request_id}
                  </p>
                  {followUpError.retryable && (
                    <div className="mt-3 flex items-center gap-3">
                      <span className="text-xs">This error is retryable.</span>
                      <button
                        type="button"
                        onClick={() => lastFollowUpQuestion && sendFollowUp(lastFollowUpQuestion)}
                        disabled={followUpLoading || !lastFollowUpQuestion}
                        className="text-xs px-3 py-1 rounded border border-red-300 hover:bg-red-800 disabled:opacity-50"
                      >
                        Retry
                      </button>
                    </div>
                  )}
                </div>
              )}

              <form
                onSubmit={handleFollowUpSubmit}
                className="flex flex-col gap-4"
              >
                <textarea
                  value={followUpQuestion}
                  onChange={(e) => setFollowUpQuestion(e.target.value)}
                  placeholder="Ask any question about this match..."
                  rows={3}
                  className="w-full px-4 py-2 bg-gray-800 border border-gray-600 rounded text-gray-100 placeholder-gray-500 focus:outline-none focus:border-goal-accent"
                />
                <button
                  type="submit"
                  disabled={
                    followUpLoading || followUpQuestion.trim().length < 5
                  }
                  className="px-6 py-2 bg-gradient-to-r from-goal-accent to-pitch-500 text-pitch-900 font-bold rounded hover:from-goal-accent/90 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                >
                  {followUpLoading ? "Analyzing..." : "Get Answer"}
                </button>
              </form>

              {/* Follow-up Answers */}
              {followUpReviews.length > 0 && (
                <div className="mt-6 space-y-4">
                  <h4 className="font-semibold text-goal-accent">
                    Previous Questions
                  </h4>
                  {followUpReviews.map((review, index) => (
                    <div
                      key={index}
                      className="bg-gray-800 border border-gray-700 rounded p-4"
                    >
                      <p className="text-goal-accent font-semibold mb-3">
                        Q: {review.question}
                      </p>
                      <div className="prose prose-invert prose-sm max-w-none">
                        <ReactMarkdown>
                          {typeof review.answer === "string"
                            ? review.answer
                            : review.answer?.summary
                              ? Object.entries(review.answer)
                                  .filter(([, v]) => typeof v === "string")
                                  .map(([k, v]) => `**${k.replace(/_/g, " ")}:** ${v}`)
                                  .join("\n\n")
                              : JSON.stringify(review.answer, null, 2)}
                        </ReactMarkdown>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
