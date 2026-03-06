'use client'

import { useState } from 'react'
import { Play } from 'lucide-react'
import DiffDisplay from './DiffDisplay'
import { DiffResult } from '../types'

const LANGUAGES = [
  'auto',
  'python',
  'javascript',
  'typescript',
  'java',
  'cpp',
  'go',
  'rust',
]

export default function DiffAnalyzer() {
  const [before, setBefore] = useState('')
  const [after, setAfter] = useState('')
  const [language, setLanguage] = useState('auto')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<DiffResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleAnalyze = async () => {
    if (!before.trim() || !after.trim()) return

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${apiUrl}/analyze/diff`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ before, after, language }),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `Analysis failed: ${response.statusText}`)
      }

      const data = await response.json()
      setResult(data)
    } catch (err: any) {
      setError(err.message || 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Controls bar */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 flex items-center gap-4">
        <div className="flex items-center gap-2">
          <label className="text-sm font-medium text-gray-700">Language</label>
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="block w-36 rounded-md border-0 py-1.5 pl-3 pr-8 text-gray-900 ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-indigo-600 sm:text-sm sm:leading-6"
          >
            {LANGUAGES.map((l) => (
              <option key={l} value={l}>
                {l === 'auto' ? 'Auto-detect' : l.charAt(0).toUpperCase() + l.slice(1)}
              </option>
            ))}
          </select>
        </div>
        <button
          onClick={handleAnalyze}
          disabled={loading || !before.trim() || !after.trim()}
          className="ml-auto flex items-center gap-2 bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? (
            <>
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Analyzing…
            </>
          ) : (
            <>
              <Play className="w-4 h-4" />
              Analyze Diff
            </>
          )}
        </button>
      </div>

      {/* Side-by-side code panes */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="px-4 py-3 bg-gray-50 border-b border-gray-100 flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-red-400" />
            <span className="text-sm font-semibold text-gray-700">Before</span>
          </div>
          <textarea
            value={before}
            onChange={(e) => setBefore(e.target.value)}
            placeholder="Paste the original code here…"
            className="block w-full h-72 p-4 font-mono text-sm text-gray-900 placeholder:text-gray-400 resize-none focus:outline-none"
            spellCheck={false}
          />
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="px-4 py-3 bg-gray-50 border-b border-gray-100 flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-green-400" />
            <span className="text-sm font-semibold text-gray-700">After</span>
          </div>
          <textarea
            value={after}
            onChange={(e) => setAfter(e.target.value)}
            placeholder="Paste the updated code here…"
            className="block w-full h-72 p-4 font-mono text-sm text-gray-900 placeholder:text-gray-400 resize-none focus:outline-none"
            spellCheck={false}
          />
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700 text-sm">
          {error}
        </div>
      )}

      {/* Results */}
      {result && <DiffDisplay result={result} />}
    </div>
  )
}
