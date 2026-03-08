'use client'

import { useEffect, useRef, useState } from 'react'
import MigrationForm from '@/components/MigrationForm'
import MigrationResult from '@/components/MigrationResult'
import PlanReview from '@/components/PlanReview'
import type {
  ApprovalPlanResponse,
  ApproveResponse,
  JobStatusResponse,
  MigrationResponse,
  RejectResponse,
  StepResult,
} from '@/components/types'

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

const ACTIVE_JOB_KEY = 'migration_active_job'
const RECENT_JOBS_KEY = 'migration_recent_jobs'
const MAX_RECENT = 20

type Stage = 'idle' | 'awaiting_approval' | 'executing' | 'complete' | 'error'

interface RecentJob {
  jobId: string
  createdAt: string
  lastStatus: string
}

function toMigrationResponse(s: JobStatusResponse): MigrationResponse {
  return {
    success: s.status === 'completed' && s.errors.length === 0,
    migrated_files: s.migrated_files,
    plan_executed: s.plan_executed,
    verification: s.verification,
    errors: s.errors,
  }
}

function readRecentJobs(): RecentJob[] {
  try { return JSON.parse(localStorage.getItem(RECENT_JOBS_KEY) ?? '[]') } catch { return [] }
}

function upsertRecentJob(jobId: string, lastStatus: string) {
  const jobs = readRecentJobs().filter((j) => j.jobId !== jobId)
  const existing = readRecentJobs().find((j) => j.jobId === jobId)
  jobs.unshift({ jobId, createdAt: existing?.createdAt ?? new Date().toISOString(), lastStatus })
  localStorage.setItem(RECENT_JOBS_KEY, JSON.stringify(jobs.slice(0, MAX_RECENT)))
}

export default function Home() {
  const [stage, setStage] = useState<Stage>('idle')
  const [jobId, setJobId] = useState<string | null>(null)
  const [plan, setPlan] = useState<StepResult[]>([])
  const [analysis, setAnalysis] = useState<Record<string, unknown> | undefined>()
  const [result, setResult] = useState<MigrationResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [restoring, setRestoring] = useState(true)

  // Jobs panel
  const [jobsOpen, setJobsOpen] = useState(false)
  const [recentJobs, setRecentJobs] = useState<RecentJob[]>([])
  const [lookupId, setLookupId] = useState('')
  const [lookupResult, setLookupResult] = useState<JobStatusResponse | null>(null)
  const [lookupError, setLookupError] = useState<string | null>(null)
  const [lookupLoading, setLookupLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  const resultRef = useRef<HTMLDivElement>(null)

  // ------------------------------------------------------------------
  // Restore active job on mount
  // ------------------------------------------------------------------
  useEffect(() => {
    setRecentJobs(readRecentJobs())

    async function restore() {
      const raw = localStorage.getItem(ACTIVE_JOB_KEY)
      if (!raw) { setRestoring(false); return }
      let saved: { jobId: string; stage: Stage }
      try { saved = JSON.parse(raw) } catch { setRestoring(false); return }

      const { jobId: savedId, stage: savedStage } = saved
      if (!savedId || savedStage === 'idle' || savedStage === 'complete' || savedStage === 'error') {
        localStorage.removeItem(ACTIVE_JOB_KEY)
        setRestoring(false)
        return
      }

      try {
        const res = await fetch(`${API_URL}/migrate/${savedId}/status`)
        if (!res.ok) throw new Error('not found')
        const data: JobStatusResponse = await res.json()

        if (data.status === 'awaiting_approval') {
          // Also restore the plan
          const planRes = await fetch(`${API_URL}/migrate/${savedId}/plan`)
          if (planRes.ok) {
            const planData: ApprovalPlanResponse = await planRes.json()
            setPlan(planData.plan)
            setAnalysis(planData.analysis)
          }
          setJobId(savedId)
          setStage('awaiting_approval')
        } else if (data.status === 'executing') {
          setJobId(savedId)
          setStage('executing')
        } else if (data.status === 'completed' || data.status === 'failed') {
          setResult(toMigrationResponse(data))
          setJobId(savedId)
          setStage('complete')
        } else {
          localStorage.removeItem(ACTIVE_JOB_KEY)
        }
      } catch {
        localStorage.removeItem(ACTIVE_JOB_KEY)
      } finally {
        setRestoring(false)
      }
    }

    restore()
  }, [])

  // ------------------------------------------------------------------
  // Persist active job whenever jobId / stage changes
  // ------------------------------------------------------------------
  useEffect(() => {
    if (restoring) return
    if (jobId && stage !== 'idle' && stage !== 'error') {
      localStorage.setItem(ACTIVE_JOB_KEY, JSON.stringify({ jobId, stage }))
      upsertRecentJob(jobId, stage)
      setRecentJobs(readRecentJobs())
    } else {
      localStorage.removeItem(ACTIVE_JOB_KEY)
    }
  }, [jobId, stage, restoring])

  // ------------------------------------------------------------------
  // Update recent job status when job completes / errors
  // ------------------------------------------------------------------
  useEffect(() => {
    if (jobId && (stage === 'complete' || stage === 'error')) {
      upsertRecentJob(jobId, stage)
      setRecentJobs(readRecentJobs())
    }
  }, [stage, jobId])

  // ------------------------------------------------------------------
  // Polling while executing
  // ------------------------------------------------------------------
  useEffect(() => {
    if (stage !== 'executing' || !jobId) return

    const intervalId = setInterval(async () => {
      try {
        const r = await fetch(`${API_URL}/migrate/${jobId}/status`)
        if (!r.ok) return
        const data: JobStatusResponse = await r.json()

        if (data.status === 'completed' || data.status === 'failed') {
          setResult(toMigrationResponse(data))
          setStage('complete')
        } else if (data.status === 'timed_out' || data.status === 'rejected') {
          setError(`Job ended with status: ${data.status}`)
          setStage('error')
        }
      } catch {
        // ignore transient network errors during polling
      }
    }, 3000)

    return () => clearInterval(intervalId)
  }, [stage, jobId])

  // Scroll to results when complete
  useEffect(() => {
    if (stage === 'complete') {
      setTimeout(() => resultRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 100)
    }
  }, [stage])

  // ------------------------------------------------------------------
  // Handlers
  // ------------------------------------------------------------------
  async function handleMigrate(
    sourceFramework: string,
    targetFramework: string,
    files: Record<string, string>
  ) {
    setError(null)
    setResult(null)
    setJobId(null)
    setStage('idle')
    setSubmitting(true)

    try {
      const res = await fetch(`${API_URL}/migrate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source_framework: sourceFramework, target_framework: targetFramework, files }),
      })
      if (!res.ok) {
        const body = await res.json().catch(() => ({}))
        throw new Error(body.detail ?? `HTTP ${res.status}`)
      }

      const data: ApprovalPlanResponse = await res.json()
      setJobId(data.job_id)
      setPlan(data.plan)
      setAnalysis(data.analysis)
      setStage('awaiting_approval')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unexpected error')
      setStage('error')
    } finally {
      setSubmitting(false)
    }
  }

  function handleApproved(_res: ApproveResponse) {
    setStage('executing')
  }

  function handleRejected(_res: RejectResponse) {
    localStorage.removeItem(ACTIVE_JOB_KEY)
    setStage('idle')
    setJobId(null)
    setPlan([])
    setAnalysis(undefined)
  }

  async function handleLookup() {
    const id = lookupId.trim()
    if (!id) return
    setLookupLoading(true)
    setLookupResult(null)
    setLookupError(null)
    try {
      const res = await fetch(`${API_URL}/migrate/${id}/status`)
      if (!res.ok) throw new Error(res.status === 404 ? 'Job not found' : `HTTP ${res.status}`)
      const data: JobStatusResponse = await res.json()
      setLookupResult(data)
      upsertRecentJob(id, data.status)
      setRecentJobs(readRecentJobs())
    } catch (e) {
      setLookupError(e instanceof Error ? e.message : 'Lookup failed')
    } finally {
      setLookupLoading(false)
    }
  }

  function handleLoadResults(data: JobStatusResponse) {
    setResult(toMigrationResponse(data))
    setJobId(data.job_id)
    setStage('complete')
    setJobsOpen(false)
  }

  function handleResumeJob(job: RecentJob) {
    setLookupId(job.jobId)
    // auto-lookup
    setLookupLoading(true)
    setLookupResult(null)
    setLookupError(null)
    fetch(`${API_URL}/migrate/${job.jobId}/status`)
      .then((r) => (r.ok ? r.json() : Promise.reject(r.status === 404 ? 'Job not found' : `HTTP ${r.status}`)))
      .then((data: JobStatusResponse) => {
        setLookupResult(data)
        upsertRecentJob(job.jobId, data.status)
        setRecentJobs(readRecentJobs())
      })
      .catch((e) => setLookupError(typeof e === 'string' ? e : 'Lookup failed'))
      .finally(() => setLookupLoading(false))
  }

  // ------------------------------------------------------------------
  // Render
  // ------------------------------------------------------------------
  if (restoring) {
    return (
      <main className="max-w-5xl mx-auto px-4 py-8 flex items-center justify-center min-h-[40vh]">
        <div className="text-slate-400 text-sm flex items-center gap-2">
          <svg className="animate-spin w-4 h-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
          </svg>
          Restoring session…
        </div>
      </main>
    )
  }

  return (
    <main className="max-w-5xl mx-auto px-4 py-8 space-y-8">
      {/* Hero */}
      <div className="flex items-start justify-between gap-4">
        <div className="text-center flex-1 space-y-2">
          <h2 className="text-3xl font-bold text-slate-800">Code Migration Workflow</h2>
          <p className="text-slate-500 max-w-2xl mx-auto">
            Paste your source files, choose your target framework, and let the AI agent analyze,
            plan, and — after your review — execute and verify the migration.
          </p>
        </div>
        {/* Jobs panel toggle */}
        <button
          onClick={() => setJobsOpen((o) => !o)}
          className="flex-shrink-0 flex items-center gap-1.5 px-3 py-2 rounded-lg border border-slate-200 bg-white text-sm text-slate-600 hover:bg-slate-50 transition-colors shadow-sm"
          title="Job history"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
          Jobs
          {recentJobs.length > 0 && (
            <span className="bg-indigo-100 text-indigo-700 text-xs font-bold px-1.5 rounded-full">{recentJobs.length}</span>
          )}
        </button>
      </div>

      {/* Jobs panel */}
      {jobsOpen && (
        <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-5 space-y-4">
          <h3 className="font-semibold text-slate-700 text-sm">Job Lookup</h3>

          {/* Manual lookup */}
          <div className="flex gap-2">
            <input
              type="text"
              value={lookupId}
              onChange={(e) => setLookupId(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleLookup()}
              placeholder="Enter job ID…"
              className="flex-1 text-sm border border-slate-200 rounded-lg px-3 py-2 font-mono focus:outline-none focus:ring-2 focus:ring-indigo-300"
            />
            <button
              onClick={handleLookup}
              disabled={lookupLoading || !lookupId.trim()}
              className="px-4 py-2 bg-indigo-600 text-white text-sm rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition-colors"
            >
              {lookupLoading ? '…' : 'Check'}
            </button>
          </div>

          {/* Lookup result */}
          {lookupError && (
            <p className="text-sm text-red-600">{lookupError}</p>
          )}
          {lookupResult && (
            <div className="bg-slate-50 rounded-lg border border-slate-200 p-3 text-sm space-y-1">
              <div className="flex items-center justify-between">
                <span className="font-mono text-xs text-slate-500">{lookupResult.job_id}</span>
                <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                  lookupResult.status === 'completed' ? 'bg-green-100 text-green-700' :
                  lookupResult.status === 'failed' ? 'bg-red-100 text-red-700' :
                  lookupResult.status === 'executing' ? 'bg-blue-100 text-blue-700' :
                  lookupResult.status === 'awaiting_approval' ? 'bg-yellow-100 text-yellow-700' :
                  'bg-slate-100 text-slate-600'
                }`}>{lookupResult.status}</span>
              </div>
              <p className="text-slate-600">Phase: <span className="font-medium">{lookupResult.phase}</span></p>
              <p className="text-slate-600">Steps: {lookupResult.plan_executed.length} · Files: {Object.keys(lookupResult.migrated_files).length}</p>
              {lookupResult.errors.length > 0 && (
                <p className="text-red-600 text-xs">{lookupResult.errors[0]}</p>
              )}
              {(lookupResult.status === 'completed' || lookupResult.status === 'failed') && (
                <button
                  onClick={() => handleLoadResults(lookupResult)}
                  className="mt-2 w-full px-3 py-1.5 bg-indigo-600 text-white text-xs font-semibold rounded-lg hover:bg-indigo-700 transition-colors"
                >
                  Load Results
                </button>
              )}
            </div>
          )}

          {/* Recent jobs list */}
          {recentJobs.length > 0 && (
            <div className="space-y-2">
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Recent Jobs</p>
              <div className="divide-y divide-slate-100 border border-slate-200 rounded-lg overflow-hidden">
                {recentJobs.map((job) => (
                  <div key={job.jobId} className="flex items-center justify-between px-3 py-2 bg-white hover:bg-slate-50 text-sm">
                    <div className="min-w-0">
                      <p className="font-mono text-xs text-slate-700 truncate">{job.jobId}</p>
                      <p className="text-xs text-slate-400">{new Date(job.createdAt).toLocaleString()}</p>
                    </div>
                    <div className="flex items-center gap-2 flex-shrink-0 ml-3">
                      <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                        job.lastStatus === 'complete' || job.lastStatus === 'completed' ? 'bg-green-100 text-green-700' :
                        job.lastStatus === 'error' || job.lastStatus === 'failed' ? 'bg-red-100 text-red-700' :
                        job.lastStatus === 'executing' ? 'bg-blue-100 text-blue-700' :
                        job.lastStatus === 'awaiting_approval' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-slate-100 text-slate-600'
                      }`}>{job.lastStatus}</span>
                      <button
                        onClick={() => handleResumeJob(job)}
                        className="text-xs text-indigo-600 hover:underline"
                      >
                        Check
                      </button>
                      {(job.lastStatus === 'complete' || job.lastStatus === 'completed' || job.lastStatus === 'failed') && (
                        <button
                          onClick={async () => {
                            try {
                              const r = await fetch(`${API_URL}/migrate/${job.jobId}/status`)
                              if (!r.ok) throw new Error('not found')
                              handleLoadResults(await r.json())
                            } catch {
                              setLookupError('Could not load results for this job')
                            }
                          }}
                          className="text-xs text-emerald-600 hover:underline font-semibold"
                        >
                          Load Results
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
              <button
                onClick={() => { localStorage.removeItem(RECENT_JOBS_KEY); setRecentJobs([]) }}
                className="text-xs text-slate-400 hover:text-red-500 transition-colors"
              >
                Clear history
              </button>
            </div>
          )}
        </div>
      )}

      {/* Phase timeline */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
        {[
          { phase: '1', label: 'Analysis', active: stage !== 'idle' },
          { phase: '2', label: 'Planning', active: stage !== 'idle' },
          { phase: '✓', label: 'Review', active: stage === 'awaiting_approval' || stage === 'executing' || stage === 'complete' },
          { phase: '3', label: 'Execution', active: stage === 'executing' || stage === 'complete' },
          { phase: '4', label: 'Verification', active: stage === 'complete' },
        ].map((p) => (
          <div
            key={p.label}
            className={`rounded-lg border p-3 text-center shadow-sm transition-colors ${
              p.active ? 'border-indigo-300 bg-indigo-50' : 'border-slate-200 bg-white'
            }`}
          >
            <div
              className={`w-7 h-7 rounded-full flex items-center justify-center font-bold text-xs mx-auto mb-1 ${
                p.active ? 'bg-indigo-600 text-white' : 'bg-slate-100 text-slate-500'
              }`}
            >
              {p.phase}
            </div>
            <div className={`text-xs font-medium ${p.active ? 'text-indigo-700' : 'text-slate-500'}`}>{p.label}</div>
          </div>
        ))}
      </div>

      {/* ---- idle: show form ---- */}
      {(stage === 'idle' || stage === 'error') && (
        <MigrationForm onSubmit={handleMigrate} loading={submitting} />
      )}

      {/* ---- awaiting_approval: show plan review ---- */}
      {stage === 'awaiting_approval' && jobId && (
        <PlanReview
          plan={plan}
          jobId={jobId}
          analysis={analysis}
          onApproved={handleApproved}
          onRejected={handleRejected}
        />
      )}

      {/* ---- executing: show progress indicator ---- */}
      {stage === 'executing' && (
        <div className="bg-white border border-slate-200 rounded-xl p-8 text-center space-y-4">
          <div className="flex items-center justify-center gap-3">
            <svg className="animate-spin w-6 h-6 text-indigo-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
            </svg>
            <span className="text-slate-700 font-medium">Executing migration…</span>
          </div>
          <p className="text-sm text-slate-400">Polling for results every 3 seconds.</p>
          {jobId && <p className="text-xs text-slate-400 font-mono">Job ID: {jobId}</p>}
        </div>
      )}

      {/* ---- error banner ---- */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700 text-sm flex items-center justify-between gap-4">
          <span><strong>Error:</strong> {error}</span>
          <button
            onClick={() => { setStage('idle'); setError(null) }}
            className="text-xs underline hover:no-underline"
          >
            Start over
          </button>
        </div>
      )}

      {/* ---- complete: show results ---- */}
      {stage === 'complete' && result && (
        <div ref={resultRef} className="space-y-4">
          <MigrationResult
            result={result}
            jobId={jobId ?? undefined}
            onRollback={(updated) => setResult(updated)}
          />
          <div className="text-center">
            <button
              onClick={() => { setStage('idle'); setJobId(null); setResult(null); localStorage.removeItem(ACTIVE_JOB_KEY) }}
              className="text-sm text-slate-500 hover:text-slate-700 underline"
            >
              Start a new migration
            </button>
          </div>
        </div>
      )}
    </main>
  )
}

