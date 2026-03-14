"use client"
import { useCallback, useEffect, useRef, useState } from 'react'
import { CheckCircle, Loader2, XCircle } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import type { AgentTraceEntry, ApproveRequest, JobStatusResponse } from '@/types'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const POLL_INTERVAL_MS = 2000

interface Props {
  jobId: string
  initialIntermediate: Record<string, string>
  onDone: (result: string, steps: number, workersUsed: string[], trace: AgentTraceEntry[]) => void
  onError: (msg: string) => void
}

export default function ApprovalPanel({ jobId, initialIntermediate, onDone, onError }: Props) {
  const [status, setStatus] = useState<string>('awaiting_approval')
  const [intermediate, setIntermediate] = useState<Record<string, string>>(initialIntermediate)
  const [overrideTask, setOverrideTask] = useState('')
  const [acting, setActing] = useState(false)
  const pollRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  const stopPolling = useCallback(() => {
    if (pollRef.current) clearTimeout(pollRef.current)
  }, [])

  const poll = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/jobs/${jobId}`)
      if (!res.ok) return
      const data: JobStatusResponse = await res.json()
      setStatus(data.status)
      if (data.intermediate && Object.keys(data.intermediate).length) {
        setIntermediate(data.intermediate)
      }
      if (data.status === 'completed' && data.result !== undefined) {
        stopPolling()
        onDone(data.result, data.steps_taken, data.workers_used ?? [], data.agent_trace ?? [])
        return
      }
      if (data.status === 'rejected' || data.status === 'timed_out') {
        stopPolling()
        onError(`Job ${data.status}.`)
        return
      }
    } catch {
      // silently retry
    }
    pollRef.current = setTimeout(poll, POLL_INTERVAL_MS)
  }, [jobId, onDone, onError, stopPolling])

  useEffect(() => {
    // Start polling immediately (in case job completes without approval)
    pollRef.current = setTimeout(poll, POLL_INTERVAL_MS)
    return stopPolling
  }, [poll, stopPolling])

  async function handleApprove() {
    setActing(true)
    try {
      const body: ApproveRequest = overrideTask.trim() ? { override_task: overrideTask.trim() } : {}
      const res = await fetch(`${API_BASE}/jobs/${jobId}/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })
      if (!res.ok) {
        const d = await res.json()
        onError(d.detail || 'Approve failed')
        return
      }
      setStatus('executing')
      // Resume polling to pick up the final result
      pollRef.current = setTimeout(poll, POLL_INTERVAL_MS)
    } finally {
      setActing(false)
    }
  }

  async function handleReject() {
    setActing(true)
    try {
      const res = await fetch(`${API_BASE}/jobs/${jobId}/reject`, { method: 'POST' })
      if (!res.ok) {
        const d = await res.json()
        onError(d.detail || 'Reject failed')
        return
      }
      onError('Task rejected.')
    } finally {
      setActing(false)
    }
  }

  const statusLabel: Record<string, string> = {
    awaiting_approval: 'Awaiting your approval',
    executing: 'Running writers…',
    completed: 'Completed',
    rejected: 'Rejected',
    timed_out: 'Timed out',
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-8 space-y-6 border-l-4 border-amber-400">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-800">Human Approval Required</h2>
        <span
          className={`text-xs px-2.5 py-1 rounded-full font-medium ${
            status === 'awaiting_approval'
              ? 'bg-amber-100 text-amber-700'
              : status === 'executing'
              ? 'bg-blue-100 text-blue-700'
              : 'bg-gray-100 text-gray-600'
          }`}
        >
          {statusLabel[status] ?? status}
        </span>
      </div>

      {/* Research results */}
      {Object.keys(intermediate).length > 0 && (
        <div className="space-y-3">
          <p className="text-sm font-medium text-gray-700">Researcher findings</p>
          {Object.entries(intermediate).map(([agent, output]) => (
            <div key={agent} className="rounded-lg border border-gray-200 bg-gray-50 p-4">
              <p className="text-xs text-indigo-600 font-semibold uppercase tracking-wide mb-1">{agent}</p>
              <div className="prose prose-sm max-w-none text-gray-700 prose-code:before:content-none prose-code:after:content-none prose-code:bg-gray-100 prose-code:px-1 prose-code:py-0.5 prose-code:rounded prose-pre:bg-gray-900 prose-pre:text-gray-100">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{output}</ReactMarkdown>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Actions — only shown while awaiting */}
      {status === 'awaiting_approval' && (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Override writing task{' '}
              <span className="text-gray-400 font-normal">(optional)</span>
            </label>
            <textarea
              value={overrideTask}
              onChange={(e) => setOverrideTask(e.target.value)}
              rows={2}
              placeholder="Leave blank to use the original task, or enter a revised instruction for the Writer agent…"
              className="w-full border border-gray-300 rounded-lg p-3 text-sm focus:outline-none focus:ring-2 focus:ring-amber-400"
            />
          </div>

          <div className="flex gap-3">
            <button
              onClick={handleApprove}
              disabled={acting}
              className="flex-1 bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white font-semibold py-2.5 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
            >
              {acting ? <Loader2 className="w-4 h-4 animate-spin" /> : <CheckCircle className="w-4 h-4" />}
              Approve &amp; Continue
            </button>
            <button
              onClick={handleReject}
              disabled={acting}
              className="flex-1 bg-red-100 hover:bg-red-200 disabled:opacity-50 text-red-700 font-semibold py-2.5 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
            >
              <XCircle className="w-4 h-4" />
              Reject
            </button>
          </div>
        </div>
      )}

      {/* Executing spinner */}
      {status === 'executing' && (
        <div className="flex items-center gap-3 text-blue-600 text-sm">
          <Loader2 className="w-4 h-4 animate-spin" />
          Writer agents are running…
        </div>
      )}
    </div>
  )
}
