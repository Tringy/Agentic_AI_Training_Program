'use client'

import { useState } from 'react'
import { Plus, Trash2, Play, Code2, AlertCircle } from 'lucide-react'
import AnalysisDisplay from './AnalysisDisplay'
import RelationshipDisplay from './RelationshipDisplay'
import LanguageBadge from './LanguageBadge'
import { DetectionResult, FileInput, MultiFileResult } from '../types'

const LANGUAGES = ['auto', 'python', 'javascript', 'typescript', 'java', 'cpp', 'go', 'rust']

const emptyFile = (): FileInput => ({ filename: '', code: '', language: 'auto' })

interface MultiFileAnalyzerProps {
  onAnalysisComplete?: () => void
}

export default function MultiFileAnalyzer({ onAnalysisComplete }: MultiFileAnalyzerProps = {}) {
  const [files, setFiles] = useState<FileInput[]>([emptyFile(), emptyFile()])
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<MultiFileResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [detectionResults, setDetectionResults] = useState<(DetectionResult | null)[]>([])
  const [cacheHit, setCacheHit] = useState(false)

  const updateFile = (index: number, patch: Partial<FileInput>) => {
    setFiles((prev) => prev.map((f, i) => (i === index ? { ...f, ...patch } : f)))
  }

  const addFile = () => {
    if (files.length < 10) setFiles((prev) => [...prev, emptyFile()])
  }

  const removeFile = (index: number) => {
    if (files.length > 2) setFiles((prev) => prev.filter((_, i) => i !== index))
  }

  const handleAnalyze = async () => {
    setLoading(true)
    setError(null)
    setResult(null)
    setDetectionResults([])
    setCacheHit(false)

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${apiUrl}/analyze/multi`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ files }),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `Analysis failed: ${response.statusText}`)
      }

      const hit = response.headers.get('X-Cache') === 'HIT'
      setCacheHit(hit)
      const data = await response.json()
      setResult(data)
      onAnalysisComplete?.()

      const apiUrl2 = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const dets = await Promise.all(
        files.map(async (f) => {
          if (f.language !== 'auto') return null
          const res = await fetch(`${apiUrl2}/detect-language`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code: f.code }),
          })
          if (!res.ok) return null
          return res.json() as Promise<DetectionResult>
        })
      )
      setDetectionResults(dets)
    } catch (err: any) {
      setError(err.message || 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  const canAnalyze = files.every((f) => f.filename.trim() && f.code.trim()) && files.length >= 2

  return (
    <div className="space-y-8">
      {/* File slots */}
      <div className="space-y-6">
        {files.map((file, index) => (
          <div
            key={index}
            className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 space-y-4"
          >
            <div className="flex items-center justify-between">
              <h3 className="font-semibold text-gray-800 flex items-center gap-2">
                <Code2 className="w-4 h-4 text-indigo-600" />
                File {index + 1}
              </h3>
              {files.length > 2 && (
                <button
                  onClick={() => removeFile(index)}
                  className="text-gray-400 hover:text-red-500 transition-colors"
                  title="Remove file"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              )}
            </div>

            <div className="flex gap-3">
              <input
                type="text"
                placeholder="filename (e.g. auth.py)"
                value={file.filename}
                onChange={(e) => updateFile(index, { filename: e.target.value })}
                className="flex-1 rounded-md border border-gray-300 px-3 py-1.5 text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
              <select
                value={file.language}
                onChange={(e) => { updateFile(index, { language: e.target.value }); setDetectionResults([]) }}
                className="rounded-md border border-gray-300 px-3 py-1.5 text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                {LANGUAGES.map((lang) => (
                  <option key={lang} value={lang}>
                    {lang === 'auto' ? 'Auto-detect' : lang.charAt(0).toUpperCase() + lang.slice(1)}
                  </option>
                ))}
              </select>
              {detectionResults[index] && <LanguageBadge detection={detectionResults[index]!} />}
            </div>

            <textarea
              placeholder="Paste code here…"
              value={file.code}
              onChange={(e) => updateFile(index, { code: e.target.value })}
              rows={8}
              className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm font-mono text-gray-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-y"
            />
          </div>
        ))}
      </div>

      {/* Add file / Analyze buttons */}
      <div className="flex items-center gap-4">
        {files.length < 10 && (
          <button
            onClick={addFile}
            className="flex items-center gap-2 rounded-lg border border-dashed border-indigo-400 px-4 py-2 text-sm text-indigo-600 hover:bg-indigo-50 transition-colors"
          >
            <Plus className="w-4 h-4" />
            Add file ({files.length}/10)
          </button>
        )}

        <button
          onClick={handleAnalyze}
          disabled={!canAnalyze || loading}
          className="ml-auto flex items-center gap-2 rounded-lg bg-indigo-600 px-6 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? (
            <>
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Analyzing…
            </>
          ) : (
            <>
              <Play className="w-4 h-4" />
              Analyze {files.length} files
            </>
          )}
        </button>
      </div>

      {/* Error */}
      {error && (
        <div className="flex items-start gap-3 rounded-lg bg-red-50 border border-red-200 p-4 text-red-700 text-sm">
          <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      {/* Results */}
      {cacheHit && result && (
        <div className="flex items-center gap-1.5 text-xs font-medium text-green-700 bg-green-50 border border-green-200 rounded-md px-3 py-1.5 w-fit">
          <span className="w-2 h-2 rounded-full bg-green-500 inline-block" />
          Served from cache
        </div>
      )}

      {result && (
        <div className="space-y-10">
          {/* Cross-file relationships */}
          <RelationshipDisplay
            relationships={result.relationships}
            overallSummary={result.overall_summary}
          />

          {/* Per-file analyses */}
          <div className="space-y-8">
            <h2 className="text-xl font-semibold text-gray-900">Per-file Analysis</h2>
            {result.files.map(({ filename, result: fileResult }, index) => (
              <div key={filename}>
                <h3 className="text-base font-medium text-gray-700 mb-3 font-mono flex items-center gap-2">
                  {filename}
                  {detectionResults[index] && <LanguageBadge detection={detectionResults[index]!} />}
                </h3>
                <AnalysisDisplay result={fileResult} type="general" />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
