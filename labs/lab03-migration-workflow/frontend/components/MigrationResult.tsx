'use client'

import { useState } from 'react'
import type { MigrationResponse, RollbackResponse, StepResult } from './types'

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

/** Safely coerce a value that may be a string or an LLM-returned object to a readable string. */
function toStr(v: unknown): string {
  if (typeof v === 'string') return v
  if (v && typeof v === 'object') {
    const o = v as Record<string, unknown>
    const parts = [o.file, o.issue ?? o.message ?? o.description, o.suggestion ?? o.fix]
      .filter(Boolean)
      .map(String)
    if (parts.length) return parts.join(' — ')
    return JSON.stringify(v)
  }
  return String(v)
}

interface Props {
  result: MigrationResponse
  jobId?: string
  onRollback?: (updated: MigrationResponse) => void
}

function StatusBadge({ status }: { status: string }) {
  const map: Record<string, string> = {
    completed: 'bg-green-100 text-green-700 border-green-200',
    failed: 'bg-red-100 text-red-700 border-red-200',
    in_progress: 'bg-yellow-100 text-yellow-700 border-yellow-200',
    pending: 'bg-slate-100 text-slate-600 border-slate-200',
  }
  const cls = map[status] ?? 'bg-slate-100 text-slate-600 border-slate-200'
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border ${cls}`}>
      {status.replace('_', ' ')}
    </span>
  )
}

function CodeBlock({ code, filename }: { code: string; filename: string }) {
  const [copied, setCopied] = useState(false)

  function copy() {
    navigator.clipboard.writeText(code).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    })
  }

  return (
    <div className="rounded-lg border border-slate-200 overflow-hidden">
      <div className="flex items-center justify-between bg-slate-800 px-4 py-2">
        <span className="text-xs font-mono text-slate-300">{filename}</span>
        <button
          onClick={copy}
          className="text-xs text-slate-400 hover:text-white flex items-center gap-1 transition-colors"
        >
          {copied ? (
            <>
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              Copied
            </>
          ) : (
            <>
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              Copy
            </>
          )}
        </button>
      </div>
      <pre className="bg-slate-900 text-slate-100 p-4 overflow-x-auto text-xs font-mono leading-relaxed max-h-96 overflow-y-auto">
        <code>{code}</code>
      </pre>
    </div>
  )
}

function Section({ title, icon, children }: { title: string; icon: React.ReactNode; children: React.ReactNode }) {
  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
      <div className="flex items-center gap-3 px-6 py-4 border-b border-slate-100 bg-slate-50">
        <span className="text-slate-500">{icon}</span>
        <h3 className="font-semibold text-slate-800">{title}</h3>
      </div>
      <div className="p-6">{children}</div>
    </div>
  )
}

/** Groups steps by wave_index and renders each wave with a label when parallel. */
function WaveList({
  steps,
  jobId,
  onRollback,
}: {
  steps: StepResult[]
  jobId?: string
  onRollback?: (toStep: number) => void
}) {
  // Group by wave_index (default 0 for sequential/missing)
  const waveMap = new Map<number, StepResult[]>()
  for (const step of steps) {
    const wi = step.wave_index ?? 0
    if (!waveMap.has(wi)) waveMap.set(wi, [])
    waveMap.get(wi)!.push(step)
  }
  const waves = [...waveMap.entries()].sort(([a], [b]) => a - b)
  const isParallel = waves.some(([, waveSteps]) => waveSteps.length > 1)

  return (
    <div className="space-y-4">
      {waves.map(([waveIdx, waveSteps]) => (
        <div key={waveIdx}>
          {isParallel && (
            <div className="flex items-center gap-2 mb-2">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wide">
                Wave {waveIdx + 1}
              </span>
              {waveSteps.length > 1 && (
                <span className="text-xs bg-indigo-50 text-indigo-600 border border-indigo-200 rounded px-1.5 py-0.5 font-medium">
                  {waveSteps.length} parallel
                </span>
              )}
              {waveIdx < waves.length - 1 && (
                <div className="flex-1 border-t border-dashed border-slate-200" />
              )}
            </div>
          )}
          <ol className={`space-y-2 ${isParallel && waveSteps.length > 1 ? 'ml-2 pl-3 border-l-2 border-indigo-100' : ''}`}>
            {waveSteps.map((step) => (
              <li key={step.id} className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center text-xs font-bold flex-shrink-0 mt-0.5">
                  {step.id}
                </div>
                <div className="flex-1 flex items-start justify-between gap-2">
                  <p className="text-sm text-slate-700">{step.description}</p>
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <StatusBadge status={step.status} />
                    {jobId && onRollback && (step.status === 'completed' || step.status === 'failed') && (
                      <button
                        onClick={() => onRollback(step.id)}
                        className="text-xs text-amber-600 hover:text-amber-800 border border-amber-300 hover:border-amber-500 rounded px-1.5 py-0.5 transition-colors"
                        title={`Rollback to before step ${step.id}`}
                      >
                        Rollback
                      </button>
                    )}
                  </div>
                </div>
              </li>
            ))}
          </ol>
        </div>
      ))}
    </div>
  )
}

export default function MigrationResult({ result, jobId, onRollback }: Props) {
  const [activeFile, setActiveFile] = useState<string | null>(
    Object.keys(result.migrated_files)[0] ?? null
  )
  const [rollbackLoading, setRollbackLoading] = useState(false)
  const [rollbackError, setRollbackError] = useState<string | null>(null)

  const migratedFilenames = Object.keys(result.migrated_files)

  async function handleRollback(toStep: number) {
    if (!jobId) return
    setRollbackLoading(true)
    setRollbackError(null)
    try {
      const res = await fetch(`${API_URL}/migrate/${jobId}/rollback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ to_step: toStep }),
      })
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }))
        setRollbackError(err.detail ?? 'Rollback failed')
        return
      }
      const data: RollbackResponse = await res.json()
      if (onRollback) {
        onRollback({
          ...result,
          migrated_files: data.migrated_files,
          plan_executed: data.plan_executed,
        })
      }
      // Reset active file to first available after rollback
      const files = Object.keys(data.migrated_files)
      setActiveFile(files[0] ?? null)
    } catch (e) {
      setRollbackError('Rollback request failed')
    } finally {
      setRollbackLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Banner */}
      <div
        className={`rounded-xl border p-4 flex items-center gap-3 ${
          result.success
            ? 'bg-green-50 border-green-200 text-green-800'
            : 'bg-red-50 border-red-200 text-red-800'
        }`}
      >
        {result.success ? (
          <svg className="w-6 h-6 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        ) : (
          <svg className="w-6 h-6 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        )}
        <div>
          <p className="font-semibold">
            {result.success ? 'Migration completed successfully!' : 'Migration completed with issues'}
          </p>
          <p className="text-sm opacity-80">
            {migratedFilenames.length} file(s) migrated · {result.plan_executed.length} step(s) executed
            {jobId && <> · <span className="font-mono text-xs">{jobId}</span></>}
          </p>
        </div>
      </div>

      {/* Migration Plan */}
      {result.plan_executed.length > 0 && (
        <Section
          title="Migration Plan"
          icon={
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
          }
        >
          {rollbackError && (
            <p className="mb-3 text-sm text-red-600 bg-red-50 border border-red-200 rounded px-3 py-2">
              {rollbackError}
            </p>
          )}
          {rollbackLoading && (
            <p className="mb-3 text-sm text-amber-600">Rolling back…</p>
          )}
          <WaveList
            steps={result.plan_executed}
            jobId={jobId}
            onRollback={handleRollback}
          />
        </Section>
      )}

      {/* Migrated Files */}
      {migratedFilenames.length > 0 && (
        <Section
          title="Migrated Files"
          icon={
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
            </svg>
          }
        >
          {/* File tabs */}
          {migratedFilenames.length > 1 && (
            <div className="flex gap-2 flex-wrap mb-4">
              {migratedFilenames.map((name) => (
                <button
                  key={name}
                  onClick={() => setActiveFile(name)}
                  className={`text-xs font-mono px-3 py-1.5 rounded-lg border transition-colors ${
                    activeFile === name
                      ? 'bg-indigo-600 text-white border-indigo-600'
                      : 'bg-white text-slate-600 border-slate-300 hover:border-indigo-400'
                  }`}
                >
                  {name}
                </button>
              ))}
            </div>
          )}

          {activeFile && result.migrated_files[activeFile] != null && (
            <CodeBlock filename={activeFile} code={result.migrated_files[activeFile]} />
          )}
        </Section>
      )}

      {/* Verification */}
      {result.verification && (
        <Section
          title="Verification"
          icon={
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          }
        >
          {/* Stats */}
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className="bg-slate-50 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-indigo-600">
                {result.verification.files_migrated ?? migratedFilenames.length}
              </div>
              <div className="text-xs text-slate-500 mt-1">Files Migrated</div>
            </div>
            <div className="bg-slate-50 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-indigo-600">
                {result.verification.steps_completed ?? result.plan_executed.length}
              </div>
              <div className="text-xs text-slate-500 mt-1">Steps Completed</div>
            </div>
          </div>

          {/* Per-file validations */}
          {result.verification.validations && result.verification.validations.length > 0 && (
            <div className="space-y-3">
              {result.verification.validations.map((v, i) => (
                <div
                  key={i}
                  className={`rounded-lg border p-3 ${
                    v.valid ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'
                  }`}
                >
                  <div className="flex items-center gap-2 mb-1">
                    {v.valid ? (
                      <svg className="w-4 h-4 text-green-600 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    ) : (
                      <svg className="w-4 h-4 text-red-600 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    )}
                    <span className="text-sm font-mono text-slate-700">{v.file}</span>
                  </div>
                  {v.issues && v.issues.length > 0 && (
                    <ul className="ml-6 space-y-1">
                      {v.issues.map((issue, j) => (
                        <li key={j} className="text-xs text-red-700">• {toStr(issue)}</li>
                      ))}
                    </ul>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Overall issues */}
          {result.verification.issues && result.verification.issues.length > 0 && (
            <div className="mt-4 space-y-1">
              <p className="text-sm font-semibold text-red-700">Issues found:</p>
              {result.verification.issues.map((issue, i) => (
                <p key={i} className="text-sm text-red-600">• {toStr(issue)}</p>
              ))}
            </div>
          )}

          {(!result.verification.issues || result.verification.issues.length === 0) &&
            (!result.verification.validations ||
              result.verification.validations.every((v) => v.valid)) && (
              <p className="text-sm text-green-700 font-medium">All files passed validation.</p>
            )}
        </Section>
      )}

      {/* Agent errors */}
      {result.errors && result.errors.length > 0 && (
        <Section
          title="Agent Errors"
          icon={
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          }
        >
          <ul className="space-y-2">
            {result.errors.map((err, i) => (
              <li key={i} className="text-sm text-red-600 bg-red-50 border border-red-200 rounded px-3 py-2">
                {err}
              </li>
            ))}
          </ul>
        </Section>
      )}
    </div>
  )
}
