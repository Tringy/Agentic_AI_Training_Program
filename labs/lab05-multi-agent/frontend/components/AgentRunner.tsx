"use client"
import { useState } from 'react'
import { Loader2, Play, ChevronDown, ChevronUp } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import type { JobStartResponse, TaskResponse } from '@/types'
import ApprovalPanel from './ApprovalPanel'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const EXAMPLE_TASKS = [
  'Write a brief explanation of how RAG systems work for a technical blog post',
  'Summarize the key principles of the SOLID design principles',
  'Explain the differences between REST and GraphQL APIs',
]

export default function AgentRunner() {
  const [task, setTask] = useState('')
  const [maxIterations, setMaxIterations] = useState(5)
  const [requireApproval, setRequireApproval] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<TaskResponse | null>(null)
  const [showRaw, setShowRaw] = useState(false)
  const [pendingJob, setPendingJob] = useState<JobStartResponse | null>(null)

  function handleApprovalDone(res: string, steps: number, workers: string[], trace: import('@/types').AgentTraceEntry[]) {
    setPendingJob(null)
    setResult({ result: res, steps_taken: steps, memory_context_used: false, workers_used: workers, agent_trace: trace })
    setLoading(false)
  }

  function handleApprovalError(msg: string) {
    setPendingJob(null)
    setError(msg)
    setLoading(false)
  }

  async function handleRun() {
    if (!task.trim()) return
    setLoading(true)
    setError(null)
    setResult(null)
    setPendingJob(null)
    try {
      if (requireApproval) {
        const res = await fetch(`${API_BASE}/run-with-approval`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ task: task.trim(), max_iterations: maxIterations, require_approval: true }),
        })
        if (!res.ok) {
          const d = await res.json()
          throw new Error(d.detail || `Request failed (${res.status})`)
        }
        const data: JobStartResponse = await res.json()
        setPendingJob(data)
        // Loading stays true — ApprovalPanel drives the rest
        return
      }

      const res = await fetch(`${API_BASE}/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task: task.trim(), max_iterations: maxIterations }),
      })
      if (!res.ok) {
        const data = await res.json()
        throw new Error(data.detail || `Request failed (${res.status})`)
      }
      const data: TaskResponse = await res.json()
      setResult(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      if (!requireApproval) setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Input card */}
      <div className="bg-white rounded-lg shadow-lg p-8 space-y-5">
        <h2 className="text-lg font-semibold text-gray-800">Run a Task</h2>

        {/* Example tasks */}
        <div>
          <p className="text-xs text-gray-500 mb-2 uppercase tracking-wide">Example tasks</p>
          <div className="flex flex-wrap gap-2">
            {EXAMPLE_TASKS.map((t) => (
              <button
                key={t}
                onClick={() => setTask(t)}
                className="text-xs bg-indigo-50 hover:bg-indigo-100 text-indigo-700 px-3 py-1.5 rounded-full transition-colors"
              >
                {t.length > 60 ? t.slice(0, 57) + '...' : t}
              </button>
            ))}
          </div>
        </div>

        {/* Task input */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Task</label>
          <textarea
            value={task}
            onChange={(e) => setTask(e.target.value)}
            rows={3}
            placeholder="Describe the task for the multi-agent system..."
            className="w-full border border-gray-300 rounded-lg p-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
          />
        </div>

        {/* Max iterations */}
        <div className="flex items-center gap-4">
          <label className="text-sm font-medium text-gray-700 whitespace-nowrap">
            Max iterations: <span className="text-indigo-600 font-semibold">{maxIterations}</span>
          </label>
          <input
            type="range"
            min={1}
            max={10}
            value={maxIterations}
            onChange={(e) => setMaxIterations(Number(e.target.value))}
            className="flex-1 accent-indigo-600"
          />
          <span className="text-xs text-gray-400 w-12 text-right">1 – 10</span>
        </div>

        {/* Require approval toggle */}
        <label className="flex items-center gap-3 cursor-pointer select-none">
          <div
            onClick={() => setRequireApproval((v) => !v)}
            className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors ${requireApproval ? 'bg-amber-500' : 'bg-gray-300'}`}
          >
            <span
              className={`inline-block h-3.5 w-3.5 transform rounded-full bg-white shadow transition-transform ${requireApproval ? 'translate-x-4' : 'translate-x-1'}`}
            />
          </div>
          <span className="text-sm text-gray-700">
            Require human approval <span className="text-gray-400 font-normal">(pause after research phase)</span>
          </span>
        </label>

        <button
          onClick={handleRun}
          disabled={loading || !task.trim()}
          className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white font-semibold py-2.5 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
        >
          {loading && !pendingJob ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Running agents…
            </>
          ) : (
            <>
              <Play className="w-4 h-4" />
              Run
            </>
          )}
        </button>

        {error && (
          <div className="text-red-600 text-sm bg-red-50 rounded-lg px-4 py-3 border border-red-200">
            {error}
          </div>
        )}
      </div>

      {/* Result card */}
      {pendingJob && (
        <ApprovalPanel
          jobId={pendingJob.job_id}
          initialIntermediate={pendingJob.intermediate}
          onDone={handleApprovalDone}
          onError={handleApprovalError}
        />
      )}

      {/* Result card */}
      {result && (
        <div className="bg-white rounded-lg shadow-lg p-8 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-800">Result</h2>
            <span className="text-xs bg-green-100 text-green-700 px-2.5 py-1 rounded-full">
              {result.steps_taken} step{result.steps_taken !== 1 ? 's' : ''}
            </span>
          </div>

          {result.workers_used && result.workers_used.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              <span className="text-xs text-gray-500 mr-1 self-center">Workers used:</span>
              {result.workers_used.map((w) => (
                <span key={w} className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full font-medium">{w}</span>
              ))}
            </div>
          )}

          {result.agent_trace && result.agent_trace.length > 0 && (
            <div className="border border-gray-100 rounded-lg overflow-hidden text-xs">
              <div className="bg-gray-100 px-3 py-1.5 text-gray-500 font-medium">Agent execution trace</div>
              {Object.entries(
                result.agent_trace.reduce<Record<number, typeof result.agent_trace>>((acc, e) => {
                  ;(acc[e.parallel_group] = acc[e.parallel_group] || []).push(e)
                  return acc
                }, {})
              ).map(([group, entries]) => (
                <div key={group} className="flex flex-wrap gap-2 px-3 py-2 border-t border-gray-100 items-center">
                  <span className="text-gray-400 w-16 shrink-0">Group {group}</span>
                  {entries.map((e) => (
                    <span key={e.agent} className="flex items-center gap-1 bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded-full">
                      <span className="font-medium">{e.agent}</span>
                      <span className="text-indigo-400">{e.duration_ms}ms</span>
                    </span>
                  ))}
                </div>
              ))}
            </div>
          )}

          <div className="prose prose-sm max-w-none text-gray-700 border border-gray-100 rounded-lg p-4 bg-gray-50 prose-code:before:content-none prose-code:after:content-none prose-code:bg-gray-100 prose-code:px-1 prose-code:py-0.5 prose-code:rounded prose-pre:bg-gray-900 prose-pre:text-gray-100">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{result.result}</ReactMarkdown>
          </div>

          {/* Raw JSON toggle */}
          <button
            onClick={() => setShowRaw((v) => !v)}
            className="text-xs text-gray-400 hover:text-gray-600 flex items-center gap-1 transition-colors"
          >
            {showRaw ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
            {showRaw ? 'Hide' : 'Show'} raw JSON
          </button>

          {showRaw && (
            <pre className="text-xs bg-gray-900 text-green-300 rounded-lg p-4 overflow-auto">
              {JSON.stringify(result, null, 2)}
            </pre>
          )}
        </div>
      )}
    </div>
  )
}
