"use client"
import { useCallback, useEffect, useState } from 'react'
import { Brain, RefreshCw, Trash2 } from 'lucide-react'
import type { MemoryEntry, MemoryListResponse } from '@/types'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function MemoryPanel() {
  const [entries, setEntries] = useState<MemoryEntry[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  const [clearing, setClearing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchMemory = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch(`${API_BASE}/memory`)
      if (!res.ok) throw new Error(`Failed to fetch memory (${res.status})`)
      const data: MemoryListResponse = await res.json()
      setEntries(data.entries)
      setTotal(data.total)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchMemory()
  }, [fetchMemory])

  async function handleClear() {
    if (!confirm('Clear all memory entries?')) return
    setClearing(true)
    try {
      const res = await fetch(`${API_BASE}/memory`, { method: 'DELETE' })
      if (!res.ok) throw new Error(`Failed to clear memory (${res.status})`)
      setEntries([])
      setTotal(0)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setClearing(false)
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Brain className="w-5 h-5 text-purple-600" />
          <h2 className="text-lg font-semibold text-gray-800">Agent Memory</h2>
          <span className="text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded-full font-medium">
            {total} entr{total === 1 ? 'y' : 'ies'}
          </span>
        </div>
        <div className="flex gap-2">
          <button
            onClick={fetchMemory}
            disabled={loading}
            title="Refresh"
            className="p-1.5 text-gray-400 hover:text-gray-600 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
          <button
            onClick={handleClear}
            disabled={clearing || entries.length === 0}
            title="Clear all memory"
            className="p-1.5 text-red-400 hover:text-red-600 transition-colors disabled:opacity-50"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {error && (
        <p className="text-sm text-red-600 bg-red-50 rounded px-3 py-2 border border-red-200">{error}</p>
      )}

      {entries.length === 0 && !loading && (
        <p className="text-sm text-gray-400 text-center py-4">No memory entries yet. Run a task to build memory.</p>
      )}

      <ul className="space-y-3">
        {entries.map((entry) => (
          <li key={entry.id} className="border border-gray-100 rounded-lg p-4 bg-gray-50 space-y-1">
            <div className="flex items-start justify-between gap-2">
              <p className="text-xs font-semibold text-purple-700 truncate flex-1">{entry.task}</p>
              <span className="text-xs text-gray-400 whitespace-nowrap">
                {new Date(entry.created_at).toLocaleString()}
              </span>
            </div>
            <p className="text-sm text-gray-600 leading-relaxed">{entry.summary}</p>
          </li>
        ))}
      </ul>
    </div>
  )
}
