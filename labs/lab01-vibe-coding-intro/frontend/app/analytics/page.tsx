'use client'

import { useEffect, useState } from 'react'
import URLTable from '@/components/URLTable'
import StatsCard from '@/components/StatsCard'

interface URLAnalytics {
  short_code: string
  original_url: string
  short_url: string
  click_count: number
  created_at: string
  last_accessed_at?: string
}

interface AnalyticsData {
  total_urls: number
  total_clicks: number
  average_clicks: number
  urls: URLAnalytics[]
  page: number
  total_pages: number
}

export default function AnalyticsPage() {
  const [data, setData] = useState<AnalyticsData | null>(null)
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [error, setError] = useState<string | null>(null)

  const fetchAnalytics = async (pageNum: number) => {
    try {
      setLoading(true)
      const API_BASE = process.env.NEXT_PUBLIC_API_URL || ''
      const target = API_BASE ? `${API_BASE}/api/analytics?page=${pageNum}&limit=10` : `/api/analytics?page=${pageNum}&limit=10`
      const response = await fetch(target)
      if (!response.ok) {
        throw new Error('Failed to fetch analytics')
      }
      const result = await response.json()
      setData(result)
      setPage(pageNum)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAnalytics(1)
  }, [])

  const handleDelete = async (shortCode: string) => {
    try {
      const response = await fetch(`/api/delete/${encodeURIComponent(shortCode)}`, { method: 'DELETE' })
      if (!response.ok) {
        throw new Error('Failed to delete URL')
      }
      // Refresh analytics
      await fetchAnalytics(page)
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to delete URL')
    }
  }

  return (
    <main className="min-h-[calc(100vh-64px)] bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
          <p className="text-gray-600 mt-2">Track your shortened URLs and click statistics</p>
        </div>

        {/* Stats Cards */}
        {data && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
            <StatsCard
              title="Total URLs"
              value={data.total_urls}
              icon="🔗"
            />
            <StatsCard
              title="Total Clicks"
              value={data.total_clicks}
              icon="📊"
            />
            <StatsCard
              title="Average Clicks/URL"
              value={data.average_clicks.toFixed(1)}
              icon="📈"
            />
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6 text-red-700">
            {error}
          </div>
        )}

        {/* URLs Table */}
        {data && (
          <>
            <div className="bg-white rounded-lg shadow">
              <URLTable
                rows={data.urls}
                onDelete={handleDelete}
                loading={loading}
              />
            </div>

            {/* Pagination */}
            {data.total_pages > 1 && (
              <div className="mt-6 flex justify-center gap-2">
                <button
                  onClick={() => fetchAnalytics(page - 1)}
                  disabled={page === 1}
                  className="px-4 py-2 bg-blue-600 text-white rounded disabled:bg-gray-300 disabled:cursor-not-allowed hover:bg-blue-700"
                >
                  Previous
                </button>
                <span className="px-4 py-2 text-gray-700">
                  Page {page} of {data.total_pages}
                </span>
                <button
                  onClick={() => fetchAnalytics(page + 1)}
                  disabled={page === data.total_pages}
                  className="px-4 py-2 bg-blue-600 text-white rounded disabled:bg-gray-300 disabled:cursor-not-allowed hover:bg-blue-700"
                >
                  Next
                </button>
              </div>
            )}
          </>
        )}

        {loading && !data && (
          <div className="text-center py-12 text-gray-500">
            <p>Loading analytics...</p>
          </div>
        )}
      </div>
    </main>
  )
}
