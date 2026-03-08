'use client'

import { useEffect, useState } from 'react'
import { SUPPORTED_FRAMEWORKS } from './types'
import type { DetectFrameworkResponse, FrameworkProfile } from './types'

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

interface FileEntry {
  id: number
  filename: string
  content: string
}

interface Props {
  onSubmit: (source: string, target: string, files: Record<string, string>) => void
  loading: boolean
}

const PHASES = ['Analyzing code...', 'Creating plan...', 'Executing migration...', 'Verifying results...']

let _idCounter = 0

function nextId() {
  return ++_idCounter
}

export default function MigrationForm({ onSubmit, loading }: Props) {
  const [sourceFramework, setSourceFramework] = useState('express')
  const [targetFramework, setTargetFramework] = useState('fastapi')
  const [files, setFiles] = useState<FileEntry[]>([
    { id: nextId(), filename: 'routes/users.js', content: '' },
  ])
  const [phaseIndex, setPhaseIndex] = useState(0)
  const [frameworks, setFrameworks] = useState<{ name: string; language: string }[]>(SUPPORTED_FRAMEWORKS)
  const [detecting, setDetecting] = useState(false)
  const [detectHint, setDetectHint] = useState<string | null>(null)

  // Fetch framework list from API on mount
  useEffect(() => {
    fetch(`${API_URL}/frameworks`)
      .then((r) => r.json())
      .then((data) => {
        if (data.supported && Array.isArray(data.supported)) {
          setFrameworks(data.supported as FrameworkProfile[])
        }
      })
      .catch(() => {}) // keep SUPPORTED_FRAMEWORKS fallback on error
  }, [])

  // Cycle through phase labels while loading
  useState(() => {
    if (!loading) return
    const interval = setInterval(() => {
      setPhaseIndex((i) => (i + 1) % PHASES.length)
    }, 4000)
    return () => clearInterval(interval)
  })

  async function handleDetect() {
    setDetecting(true)
    setDetectHint(null)
    try {
      const filenames = files.map((f) => f.filename).filter(Boolean)
      const snippets = files.map((f) => f.content).filter(Boolean)
      const res = await fetch(`${API_URL}/detect-framework`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filenames, snippets }),
      })
      const data: DetectFrameworkResponse = await res.json()
      if (data.detected_source && (data.confidence === 'high' || data.confidence === 'medium')) {
        setSourceFramework(data.detected_source)
        setDetectHint(`Detected: ${data.detected_source} (${data.confidence} confidence)`)
      } else if (data.detected_source) {
        setDetectHint(`Low-confidence guess: ${data.detected_source}`)
      } else {
        setDetectHint('Could not detect framework')
      }
    } catch {
      setDetectHint('Detection failed')
    } finally {
      setDetecting(false)
    }
  }

  function addFile() {
    setFiles((prev) => [...prev, { id: nextId(), filename: '', content: '' }])
  }

  function removeFile(id: number) {
    setFiles((prev) => prev.filter((f) => f.id !== id))
  }

  function updateFile(id: number, field: 'filename' | 'content', value: string) {
    setFiles((prev) => prev.map((f) => (f.id === id ? { ...f, [field]: value } : f)))
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setPhaseIndex(0)
    const fileMap: Record<string, string> = {}
    for (const f of files) {
      if (f.filename.trim()) fileMap[f.filename.trim()] = f.content
    }
    if (Object.keys(fileMap).length === 0) return
    onSubmit(sourceFramework, targetFramework, fileMap)
  }

  const canSubmit = !loading && files.some((f) => f.filename.trim() && f.content.trim())

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-xl border border-slate-200 shadow-sm divide-y divide-slate-100">
      {/* Framework selectors */}
      <div className="p-6 grid sm:grid-cols-2 gap-6">
        <div className="space-y-2">
          <label className="block text-sm font-semibold text-slate-700">Source Framework</label>
          <div className="flex gap-2">
            <select
              value={sourceFramework}
              onChange={(e) => setSourceFramework(e.target.value)}
              disabled={loading}
              className="flex-1 border border-slate-300 rounded-lg px-3 py-2 text-sm text-slate-800 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              {frameworks.map((fw) => (
                <option key={fw.name} value={fw.name}>
                  {fw.name} ({fw.language})
                </option>
              ))}
            </select>
            <button
              type="button"
              onClick={handleDetect}
              disabled={loading || detecting}
              title="Detect source framework from file names and content"
              className="px-3 py-2 text-xs font-medium text-indigo-600 border border-indigo-300 rounded-lg hover:bg-indigo-50 disabled:opacity-40 whitespace-nowrap"
            >
              {detecting ? 'Detecting…' : 'Detect'}
            </button>
          </div>
          {detectHint && (
            <p className="text-xs text-slate-500">{detectHint}</p>
          )}
        </div>

        <div className="space-y-2">
          <label className="block text-sm font-semibold text-slate-700">Target Framework</label>
          <select
            value={targetFramework}
            onChange={(e) => setTargetFramework(e.target.value)}
            disabled={loading}
            className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm text-slate-800 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:opacity-50"
          >
            {frameworks.map((fw) => (
              <option key={fw.name} value={fw.name}>
                {fw.name} ({fw.language})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Files */}
      <div className="p-6 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-slate-700">Source Files</h3>
          <button
            type="button"
            onClick={addFile}
            disabled={loading}
            className="text-xs text-indigo-600 hover:text-indigo-800 font-medium flex items-center gap-1 disabled:opacity-40"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Add File
          </button>
        </div>

        {files.map((file, index) => (
          <div key={file.id} className="border border-slate-200 rounded-lg overflow-hidden">
            <div className="flex items-center gap-2 bg-slate-50 px-3 py-2 border-b border-slate-200">
              <svg className="w-4 h-4 text-slate-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <input
                type="text"
                placeholder="e.g. routes/users.js"
                value={file.filename}
                onChange={(e) => updateFile(file.id, 'filename', e.target.value)}
                disabled={loading}
                className="flex-1 text-sm bg-transparent text-slate-700 placeholder-slate-400 focus:outline-none disabled:opacity-50"
              />
              {files.length > 1 && (
                <button
                  type="button"
                  onClick={() => removeFile(file.id)}
                  disabled={loading}
                  className="text-slate-400 hover:text-red-500 transition-colors disabled:opacity-40 flex-shrink-0"
                  title="Remove file"
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              )}
            </div>
            <textarea
              placeholder={`Paste file ${index + 1} content here...`}
              value={file.content}
              onChange={(e) => updateFile(file.id, 'content', e.target.value)}
              disabled={loading}
              rows={8}
              className="w-full px-3 py-2 text-sm font-mono text-slate-800 placeholder-slate-400 focus:outline-none resize-y disabled:opacity-50 disabled:bg-slate-50"
            />
          </div>
        ))}
      </div>

      {/* Submit */}
      <div className="p-6 flex items-center justify-between">
        <p className="text-xs text-slate-400">
          {files.filter((f) => f.filename.trim() && f.content.trim()).length} file(s) ready
        </p>
        <button
          type="submit"
          disabled={!canSubmit}
          className="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-300 text-white text-sm font-semibold px-6 py-2.5 rounded-lg transition-colors"
        >
          {loading ? (
            <>
              <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              {PHASES[phaseIndex]}
            </>
          ) : (
            <>
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              Run Migration
            </>
          )}
        </button>
      </div>
    </form>
  )
}
