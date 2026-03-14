'use client'

import { useState } from 'react'
import { CheckCircle, AlertCircle, Database, Github } from 'lucide-react'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface IndexStats {
  count: number
  name: string
}

interface IndexResult {
  indexed_chunks: number
  repository?: string
  url?: string
  files?: string[]
  directory?: string
}

const EXTENSIONS_PLACEHOLDER = 'e.g. .py .ts .js .go (leave empty for all code files)'

export default function IndexPanel() {
  const [githubUrl, setGithubUrl] = useState('')
  const [githubBranch, setGithubBranch] = useState('')
  const [githubExts, setGithubExts] = useState('')

  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<IndexResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [stats, setStats] = useState<IndexStats | null>(null)
  const [statsLoading, setStatsLoading] = useState(false)

  const parseExtensions = (raw: string): string[] | null => {
    const parts = raw.trim().split(/[\s,]+/).filter(Boolean)
    return parts.length ? parts.map(e => (e.startsWith('.') ? e : `.${e}`)) : null
  }

  const clearIndex = async () => {
    if (!confirm('Clear all indexed documents?')) return
    try {
      await fetch(`${API_URL}/index`, { method: 'DELETE' })
      setStats(null)
      setResult(null)
    } catch {
      setError('Failed to clear index')
    }
  }

  const fetchStats = async () => {
    setStatsLoading(true)
    try {
      const res = await fetch(`${API_URL}/stats`)
      if (!res.ok) throw new Error('Failed to fetch stats')
      setStats(await res.json())
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Unknown error')
    } finally {
      setStatsLoading(false)
    }
  }

  const handleGithub = async () => {
    if (!githubUrl.trim()) { setError('Enter a repository URL.'); return }
    setLoading(true); setError(null); setResult(null)
    try {
      const res = await fetch(`${API_URL}/index/github`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          url: githubUrl.trim(),
          branch: githubBranch.trim() || null,
          extensions: parseExtensions(githubExts),
        }),
      })
      if (!res.ok) { const d = await res.json(); throw new Error(d.detail || 'Indexing failed') }
      setResult(await res.json())
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Stats bar */}
      <div className="bg-white border border-gray-200 rounded-xl p-4 flex items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <Database className="w-5 h-5 text-violet-500" />
          <span className="text-sm font-medium text-gray-700">
            {stats ? `${stats.count} chunks indexed in "${stats.name}"` : 'Index stats not loaded'}
          </span>
        </div>
        <div className="flex gap-2">
          <button
            onClick={fetchStats}
            disabled={statsLoading}
            className="text-sm px-3 py-1.5 rounded-lg border border-gray-200 hover:bg-gray-50 text-gray-600 transition-colors disabled:opacity-50"
          >
            {statsLoading ? 'Loading…' : 'Refresh Stats'}
          </button>
          <button
            onClick={clearIndex}
            className="text-sm px-3 py-1.5 rounded-lg border border-red-200 hover:bg-red-50 text-red-600 transition-colors"
          >
            Clear Index
          </button>
        </div>
      </div>

      {/* GitHub form */}
      <div className="bg-white border border-gray-200 rounded-xl p-6 space-y-4">
        <div className="flex items-center gap-2 mb-2">
          <Github className="w-5 h-5 text-gray-700" />
          <h2 className="text-sm font-semibold text-gray-700">Index a Repository</h2>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Repository URL
          </label>
          <input
            type="url"
            placeholder="https://github.com/owner/repo"
            value={githubUrl}
            onChange={e => setGithubUrl(e.target.value)}
            className="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 font-mono focus:outline-none focus:ring-2 focus:ring-violet-500"
          />
          <p className="mt-1 text-xs text-gray-400">
            GitHub, GitLab, and Bitbucket HTTPS URLs are supported.
          </p>
        </div>

        <div className="flex gap-4">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Branch <span className="text-gray-400 font-normal">(optional)</span>
            </label>
            <input
              type="text"
              placeholder="main"
              value={githubBranch}
              onChange={e => setGithubBranch(e.target.value)}
              className="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-violet-500"
            />
          </div>
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              File Extensions <span className="text-gray-400 font-normal">(optional)</span>
            </label>
            <input
              type="text"
              placeholder={EXTENSIONS_PLACEHOLDER}
              value={githubExts}
              onChange={e => setGithubExts(e.target.value)}
              className="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-violet-500"
            />
          </div>
        </div>

        <button
          onClick={handleGithub}
          disabled={loading}
          className="flex items-center gap-2 text-sm px-6 py-2 rounded-lg bg-violet-600 hover:bg-violet-700 text-white font-medium transition-colors disabled:opacity-50"
        >
          <Github className="w-4 h-4" />
          {loading ? 'Cloning & Indexing…' : 'Clone & Index Repository'}
        </button>
      </div>

      {/* Result */}
      {result && (
        <div className="bg-green-50 border border-green-200 rounded-xl p-4 flex gap-3">
          <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
          <div className="space-y-1">
            <p className="text-sm font-semibold text-green-800">
              Indexed {result.indexed_chunks} chunks successfully
            </p>
            {result.repository && (
              <p className="text-xs text-green-700">Repository: {result.repository}</p>
            )}
            {result.files && (
              <p className="text-xs text-green-700">
                Files: {result.files.slice(0, 10).join(', ')}
                {result.files.length > 10 ? ` …+${result.files.length - 10} more` : ''}
              </p>
            )}
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 flex gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}
    </div>
  )
}
