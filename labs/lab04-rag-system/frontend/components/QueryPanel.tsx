'use client'

import { useEffect, useState } from 'react'
import { Search, AlertCircle, FileCode, ChevronDown, ChevronUp, RefreshCw } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface Source {
  file: string
  type: string | null
  name: string | null
  line: number | null
  relevance: number | null
  search_mode?: string
  rerank_score?: number | null
}

interface QueryResult {
  answer: string
  sources: Source[]
  context_used: string
  cache_hit?: boolean
}

interface CacheStats {
  enabled: boolean
  hits: number
  misses: number
  size: number
  max_size: number
  ttl_seconds: number
}

interface Repo {
  name: string
  url: string
  chunks: number
  indexed_at: string
}

export default function QueryPanel() {
  const [question, setQuestion] = useState('')
  const [nResults, setNResults] = useState(5)
  const [language, setLanguage] = useState('')
  const [selectedRepo, setSelectedRepo] = useState('')
  const [repos, setRepos] = useState<Repo[]>([])
  const [reposLoading, setReposLoading] = useState(false)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<QueryResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [showContext, setShowContext] = useState(false)
  const [searchMode, setSearchMode] = useState<'vector' | 'keyword' | 'hybrid'>('hybrid')
  const [enableReranking, setEnableReranking] = useState(false)
  const [cacheStats, setCacheStats] = useState<CacheStats | null>(null)

  const fetchRepos = async () => {
    setReposLoading(true)
    try {
      const res = await fetch(`${API_URL}/repos`)
      if (res.ok) {
        const data = await res.json()
        setRepos(data.repos ?? [])
      }
    } catch { /* non-fatal */ } finally {
      setReposLoading(false)
    }
  }

  const fetchCacheStats = async () => {
    try {
      const res = await fetch(`${API_URL}/cache/stats`)
      if (res.ok) setCacheStats(await res.json())
    } catch { /* non-fatal */ }
  }

  useEffect(() => { fetchRepos(); fetchCacheStats() }, [])

  const handleQuery = async () => {
    if (!question.trim()) {
      setError('Please enter a question.')
      return
    }
    setLoading(true)
    setError(null)
    setResult(null)
    setShowContext(false)

    try {
      const res = await fetch(`${API_URL}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: question.trim(),
          n_results: nResults,
          filter_language: language.trim() || null,
          filter_repository: selectedRepo || null,
          search_mode: searchMode,
          enable_reranking: enableReranking,
        }),
      })
      if (!res.ok) {
        const data = await res.json()
        throw new Error(data.detail || 'Query failed')
      }
      setResult(await res.json())
      fetchCacheStats()
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Cache stats bar */}
      {cacheStats !== null && (
        <div className="bg-white border border-gray-200 rounded-xl p-4 flex items-center justify-between gap-4">
          <p className="text-xs text-gray-500">
            Cache &mdash;{' '}
            <span className="font-medium text-gray-700">Hits: {cacheStats.hits}</span>
            {' · '}
            <span className="font-medium text-gray-700">Misses: {cacheStats.misses}</span>
            {' · '}
            <span className="font-medium text-gray-700">{cacheStats.size}/{cacheStats.max_size} entries</span>
            {' · '}
            TTL: {cacheStats.ttl_seconds}s
          </p>
          <button
            onClick={async () => {
              await fetch(`${API_URL}/cache`, { method: 'DELETE' })
              fetchCacheStats()
            }}
            className="text-sm px-3 py-1.5 rounded-lg border border-gray-200 hover:bg-gray-50 text-gray-600 transition-colors flex-shrink-0"
          >
            Clear Cache
          </button>
        </div>
      )}
      {/* Input */}
      <div className="bg-white border border-gray-200 rounded-xl p-6 space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Question</label>
          <textarea
            placeholder="How does authentication work? What does the login function do?"
            value={question}
            onChange={e => setQuestion(e.target.value)}
            rows={3}
            className="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-violet-500 resize-none"
          />
        </div>

        {/* Repository filter */}
        <div>
          <div className="flex items-center justify-between mb-1">
            <label className="text-sm font-medium text-gray-700">
              Repository{' '}
              <span className="text-gray-400 font-normal">(optional — searches all if empty)</span>
            </label>
            <button
              onClick={fetchRepos}
              disabled={reposLoading}
              className="flex items-center gap-1 text-xs text-gray-400 hover:text-violet-600 transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`w-3 h-3 ${reposLoading ? 'animate-spin' : ''}`} />
              Refresh
            </button>
          </div>
          {repos.length === 0 ? (
            <p className="text-xs text-gray-400 italic py-2">
              No indexed repositories yet. Index a codebase on the Index page first.
            </p>
          ) : (
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => setSelectedRepo('')}
                className={`text-xs px-3 py-1.5 rounded-full border transition-colors ${
                  selectedRepo === ''
                    ? 'bg-violet-600 text-white border-violet-600'
                    : 'border-gray-200 text-gray-600 hover:border-violet-400 hover:text-violet-600'
                }`}
              >
                All repos
              </button>
              {repos.map(r => (
                <button
                  key={r.name}
                  onClick={() => setSelectedRepo(prev => (prev === r.name ? '' : r.name))}
                  title={r.url || undefined}
                  className={`text-xs px-3 py-1.5 rounded-full border transition-colors ${
                    selectedRepo === r.name
                      ? 'bg-violet-600 text-white border-violet-600'
                      : 'border-gray-200 text-gray-600 hover:border-violet-400 hover:text-violet-600'
                  }`}
                >
                  {r.name}
                  <span className="ml-1.5 opacity-60">{r.chunks}</span>
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="flex gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Results</label>
            <input
              type="number"
              min={1}
              max={20}
              value={nResults}
              onChange={e => setNResults(Number(e.target.value))}
              className="w-24 text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-violet-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Filter Language{' '}
              <span className="text-gray-400 font-normal">(optional)</span>
            </label>
            <input
              type="text"
              placeholder="python, csharp…"
              value={language}
              onChange={e => setLanguage(e.target.value)}
              className="w-48 text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-violet-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Search Mode</label>
            <div className="flex rounded-lg border border-gray-200 overflow-hidden text-xs">
              {(['vector', 'keyword', 'hybrid'] as const).map(mode => (
                <button
                  key={mode}
                  onClick={() => setSearchMode(mode)}
                  className={`px-3 py-2 transition-colors ${
                    searchMode === mode
                      ? 'bg-violet-600 text-white'
                      : 'bg-white text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  {mode === 'hybrid' ? '✶ Hybrid' : mode.charAt(0).toUpperCase() + mode.slice(1)}
                </button>
              ))}
            </div>
          </div>
          <div className="flex items-end pb-0.5">
            <label className="flex items-center gap-2 cursor-pointer select-none">
              <div
                onClick={() => setEnableReranking(v => !v)}
                className={`relative w-10 h-6 rounded-full transition-colors cursor-pointer ${
                  enableReranking ? 'bg-amber-500' : 'bg-gray-200'
                }`}
              >
                <span className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full shadow transition-transform ${
                  enableReranking ? 'translate-x-4' : ''
                }`} />
              </div>
              <span className="text-sm font-medium text-gray-700">
                {enableReranking ? 'Reranking ON' : 'Rerank results'}
              </span>
            </label>
          </div>
        </div>

        <button
          onClick={handleQuery}
          disabled={loading}
          className="flex items-center gap-2 text-sm px-6 py-2 rounded-lg bg-violet-600 hover:bg-violet-700 text-white font-medium transition-colors disabled:opacity-50"
        >
          <Search className="w-4 h-4" />
          {loading ? 'Searching…' : 'Ask Question'}
        </button>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 flex gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      {/* Result */}
      {result && (
        <div className="space-y-4">
          {/* Answer */}
          <div className="bg-white border border-gray-200 rounded-xl p-6">
            <div className="flex items-center gap-2 mb-3">
              <h2 className="text-sm font-semibold text-gray-700">Answer</h2>
              {result.cache_hit && (
                <span className="text-xs px-2 py-0.5 rounded-full bg-green-100 text-green-700 font-medium">
                  ⚡ Cached
                </span>
              )}
            </div>
            <div className="prose prose-sm max-w-none text-gray-800 prose-code:before:content-none prose-code:after:content-none prose-code:bg-gray-100 prose-code:px-1 prose-code:py-0.5 prose-code:rounded prose-pre:bg-gray-900 prose-pre:text-gray-100">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{result.answer}</ReactMarkdown>
            </div>
          </div>

          {/* Sources */}
          {result.sources.length > 0 && (
            <div className="bg-white border border-gray-200 rounded-xl p-6">
              <h2 className="text-sm font-semibold text-gray-700 mb-1">
                Sources ({result.sources.length})
              </h2>
              {enableReranking && (
                <p className="text-xs text-amber-600 mb-3">
                  Results reranked by LLM{result.cache_hit ? ' (cached)' : ''}
                </p>
              )}
              <div className="space-y-2">
                {result.sources.map((src, i) => (
                  <div key={i} className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                    <FileCode className="w-4 h-4 text-violet-500 flex-shrink-0 mt-0.5" />
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-mono font-medium text-gray-800 truncate">
                        {src.file}
                        {src.name && (
                          <span className="text-gray-500"> › {src.type} {src.name}</span>
                        )}
                        {src.line && (
                          <span className="text-gray-400"> :L{src.line}</span>
                        )}
                      </p>
                    </div>
                    <div className="flex items-center gap-1.5 flex-shrink-0">
                      {src.search_mode && (
                        <span className={`text-xs px-1.5 py-0.5 rounded font-medium ${
                          src.search_mode === 'hybrid' ? 'bg-violet-100 text-violet-700' :
                          src.search_mode === 'keyword' ? 'bg-blue-100 text-blue-700' :
                          'bg-gray-100 text-gray-600'
                        }`}>
                          {src.search_mode}
                        </span>
                      )}
                      {src.rerank_score != null && (
                        <span className="text-xs px-1.5 py-0.5 rounded font-medium bg-amber-100 text-amber-700">
                          ↑ {src.rerank_score.toFixed(2)}
                        </span>
                      )}
                      <span className="text-xs font-medium text-violet-600">
                        {src.relevance != null ? `${Math.round(src.relevance * 100)}%` : '—'}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Context toggle */}
          {result.context_used && (
            <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
              <button
                onClick={() => setShowContext(v => !v)}
                className="w-full flex items-center justify-between px-6 py-4 text-sm font-semibold text-gray-700 hover:bg-gray-50 transition-colors"
              >
                <span>Context Used</span>
                {showContext ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </button>
              {showContext && (
                <div className="px-6 pb-6">
                  <pre className="text-xs font-mono text-gray-700 bg-gray-50 rounded-lg p-4 overflow-auto max-h-96 whitespace-pre-wrap">
                    {result.context_used}
                  </pre>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
