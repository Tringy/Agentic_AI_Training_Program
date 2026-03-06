'use client'

import { useEffect, useState } from 'react'
import { Database, Trash2 } from 'lucide-react'
import { CacheStats } from '../types'

interface CacheStatsBarProps {
  refreshKey: number
}

export default function CacheStatsBar({ refreshKey }: CacheStatsBarProps) {
  const [stats, setStats] = useState<CacheStats | null>(null)
  const [clearing, setClearing] = useState(false)

  const fetchStats = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const res = await fetch(`${apiUrl}/cache/stats`)
      if (res.ok) {
        setStats(await res.json())
      }
    } catch {
      // silently ignore – backend may not be reachable yet
    }
  }

  useEffect(() => {
    fetchStats()
  }, [refreshKey])

  const handleClear = async () => {
    setClearing(true)
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      await fetch(`${apiUrl}/cache`, { method: 'DELETE' })
      await fetchStats()
    } finally {
      setClearing(false)
    }
  }

  if (!stats) return null

  return (
    <div className="flex items-center justify-between bg-indigo-50 border border-indigo-100 rounded-lg px-4 py-2 text-sm text-indigo-700">
      <div className="flex items-center gap-2">
        <Database className="w-4 h-4" />
        <span>
          Cache: <strong>{stats.alive}</strong> active{stats.expired > 0 && `, ${stats.expired} expired`}
        </span>
      </div>
      <button
        onClick={handleClear}
        disabled={clearing || stats.total_entries === 0}
        className="flex items-center gap-1 text-xs font-medium text-indigo-600 hover:text-indigo-800 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
      >
        <Trash2 className="w-3.5 h-3.5" />
        {clearing ? 'Clearing…' : 'Clear Cache'}
      </button>
    </div>
  )
}
