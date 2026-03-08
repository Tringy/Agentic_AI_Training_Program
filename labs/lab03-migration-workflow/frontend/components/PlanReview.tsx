'use client'

import { useState } from 'react'
import type { ApproveResponse, JobStatusResponse, RejectResponse, StepResult } from './types'

interface PlanReviewProps {
  plan: StepResult[]
  jobId: string
  analysis?: Record<string, unknown>
  onApproved: (result: ApproveResponse) => void
  onRejected: (result: RejectResponse) => void
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function PlanReview({ plan, jobId, analysis, onApproved, onRejected }: PlanReviewProps) {
  const [loading, setLoading] = useState<'approve' | 'reject' | null>(null)
  const [error, setError] = useState<string | null>(null)

  async function handleApprove() {
    setLoading('approve')
    setError(null)
    try {
      const res = await fetch(`${API_URL}/migrate/${jobId}/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({}),
      })
      if (!res.ok) {
        const body = await res.json().catch(() => ({}))
        throw new Error(body.detail ?? `HTTP ${res.status}`)
      }
      const data: ApproveResponse = await res.json()
      onApproved(data)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Approval failed')
    } finally {
      setLoading(null)
    }
  }

  async function handleReject() {
    setLoading('reject')
    setError(null)
    try {
      const res = await fetch(`${API_URL}/migrate/${jobId}/reject`, { method: 'POST' })
      if (!res.ok) {
        const body = await res.json().catch(() => ({}))
        throw new Error(body.detail ?? `HTTP ${res.status}`)
      }
      const data: RejectResponse = await res.json()
      onRejected(data)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Rejection failed')
    } finally {
      setLoading(null)
    }
  }

  const analysisItems =
    analysis && typeof analysis === 'object' ? Object.entries(analysis) : []

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* header */}
      <div className="bg-yellow-50 border border-yellow-300 rounded-xl p-5">
        <div className="flex items-start gap-3">
          <div className="text-yellow-500 mt-0.5 text-xl">⚠</div>
          <div>
            <h2 className="text-lg font-semibold text-yellow-800">Review Migration Plan</h2>
            <p className="mt-1 text-sm text-yellow-700">
              The agent has finished analysing your code and produced the plan below. Review each
              step, then <strong>Approve</strong> to start execution or <strong>Reject</strong> to
              cancel.
            </p>
            <p className="mt-1 text-xs text-yellow-600 font-mono">Job ID: {jobId}</p>
          </div>
        </div>
      </div>

      {/* analysis summary (optional) */}
      {analysisItems.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-xl p-5">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">Analysis Summary</h3>
          <dl className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-2 text-sm">
            {analysisItems.map(([key, value]) => (
              <div key={key} className="flex flex-col">
                <dt className="text-xs text-gray-500 uppercase tracking-wide">{key.replace(/_/g, ' ')}</dt>
                <dd className="text-gray-800 font-medium truncate">
                  {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                </dd>
              </div>
            ))}
          </dl>
        </div>
      )}

      {/* migration steps */}
      <div className="bg-white border border-gray-200 rounded-xl divide-y divide-gray-100">
        <div className="px-5 py-3 flex items-center justify-between">
          <h3 className="text-sm font-semibold text-gray-700">
            Migration Steps &mdash; {plan.length} step{plan.length !== 1 ? 's' : ''}
          </h3>
          {(() => {
            const waveCount = new Set(plan.map((s) => s.wave_index ?? 0)).size
            const hasParallel = (() => {
              const counts: Record<number, number> = {}
              for (const s of plan) { const w = s.wave_index ?? 0; counts[w] = (counts[w] ?? 0) + 1 }
              return Object.values(counts).some((c) => c > 1)
            })()
            return hasParallel ? (
              <span className="text-xs bg-indigo-50 text-indigo-600 border border-indigo-100 rounded-full px-2 py-0.5 font-medium">
                {waveCount} wave{waveCount !== 1 ? 's' : ''} · parallel
              </span>
            ) : null
          })()}
        </div>
        {(() => {
          const waveMap = new Map<number, typeof plan>()
          for (const step of plan) {
            const wi = step.wave_index ?? 0
            if (!waveMap.has(wi)) waveMap.set(wi, [])
            waveMap.get(wi)!.push(step)
          }
          const waves = [...waveMap.entries()].sort(([a], [b]) => a - b)
          const hasAnyParallel = waves.some(([, s]) => s.length > 1)
          return waves.map(([waveIdx, waveSteps]) => (
            <div key={waveIdx}>
              {hasAnyParallel && (
                <div className="px-5 pt-3 pb-1 flex items-center gap-2">
                  <span className="text-xs font-semibold text-slate-500 uppercase tracking-wide">
                    Wave {waveIdx + 1}
                  </span>
                  {waveSteps.length > 1 && (
                    <span className="text-xs bg-indigo-50 text-indigo-500 border border-indigo-100 rounded-full px-1.5 py-0.5 font-medium">
                      {waveSteps.length} parallel
                    </span>
                  )}
                </div>
              )}
              <div className={hasAnyParallel && waveSteps.length > 1 ? 'ml-5 border-l-2 border-indigo-100' : ''}>
                {waveSteps.map((step) => (
                  <div key={step.id} className="px-5 py-4 flex items-start gap-3 border-t border-gray-100 first:border-t-0">
                    <span className="mt-0.5 flex-shrink-0 w-7 h-7 rounded-full bg-gray-100 flex items-center justify-center text-xs font-bold text-gray-600">
                      {step.id}
                    </span>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-gray-800">{step.description}</p>
                      {step.dependencies && step.dependencies.length > 0 && (
                        <p className="mt-0.5 text-xs text-gray-400">
                          depends on step{step.dependencies.length > 1 ? 's' : ''}{' '}
                          {step.dependencies.join(', ')}
                        </p>
                      )}
                    </div>
                    <span
                      className={`flex-shrink-0 text-xs px-2 py-0.5 rounded-full font-medium ${
                        step.status === 'completed'
                          ? 'bg-green-100 text-green-700'
                          : step.status === 'failed'
                          ? 'bg-red-100 text-red-700'
                          : step.status === 'in_progress'
                          ? 'bg-blue-100 text-blue-700'
                          : 'bg-gray-100 text-gray-600'
                      }`}
                    >
                      {step.status}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          ))
        })()}
      </div>

      {/* error banner */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {/* action buttons */}
      <div className="flex gap-3 justify-end">
        <button
          onClick={handleReject}
          disabled={loading !== null}
          className="px-5 py-2.5 rounded-lg border border-gray-300 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading === 'reject' ? 'Rejecting…' : 'Reject'}
        </button>
        <button
          onClick={handleApprove}
          disabled={loading !== null}
          className="px-6 py-2.5 rounded-lg bg-emerald-600 text-white text-sm font-semibold hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading === 'approve' ? 'Approving…' : 'Approve & Execute'}
        </button>
      </div>
    </div>
  )
}
