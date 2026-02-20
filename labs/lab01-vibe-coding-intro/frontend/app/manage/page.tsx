'use client'

import { useEffect, useState } from 'react'
import URLTable from '@/components/URLTable'

interface URLEntry {
  short_code: string
  original_url: string
  short_url: string
  click_count: number
  created_at: string
}

export default function ManagePage() {
  const [urls, setUrls] = useState<URLEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchUrls = async () => {
    try {
      setLoading(true)
      const API_BASE = process.env.NEXT_PUBLIC_API_URL || ''
      const target = API_BASE ? `${API_BASE}/api/analytics?limit=100` : '/api/analytics?limit=100'
      const response = await fetch(target)
      if (!response.ok) {
        throw new Error('Failed to fetch URLs')
      }
      const data = await response.json()
      setUrls(data.urls)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchUrls()
  }, [])

  const handleDelete = async (shortCode: string) => {
    try {
      const response = await fetch(`/api/delete/${encodeURIComponent(shortCode)}`, { method: 'DELETE' })
      if (!response.ok) {
        throw new Error('Failed to delete URL')
      }
      // Refresh URLs
      await fetchUrls()
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to delete URL')
    }
  }

  const handleCopy = async (url: string) => {
    try {
      await navigator.clipboard.writeText(url)
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }

  return (
    <main className="min-h-[calc(100vh-64px)] bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Manage URLs</h1>
          <p className="text-gray-600 mt-2">View, copy, and delete your shortened URLs</p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6 text-red-700">
            {error}
          </div>
        )}

        {/* URLs Table */}
        <div className="bg-white rounded-lg shadow">
          <URLTable
            rows={urls}
            onDelete={handleDelete}
            onCopy={handleCopy}
            loading={loading}
          />
        </div>

        {/* Quick Stats */}
        {urls.length > 0 && (
          <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
            <h2 className="text-lg font-semibold text-blue-900 mb-4">Summary</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <p className="text-blue-600 font-medium">Total URLs</p>
                <p className="text-2xl font-bold text-blue-900">{urls.length}</p>
              </div>
              <div>
                <p className="text-blue-600 font-medium">Total Clicks</p>
                <p className="text-2xl font-bold text-blue-900">
                  {urls.reduce((sum, url) => sum + url.click_count, 0)}
                </p>
              </div>
              <div>
                <p className="text-blue-600 font-medium">Most Popular</p>
                <p className="text-2xl font-bold text-blue-900">
                  {urls.length > 0 ? Math.max(...urls.map(u => u.click_count)) : 0} clicks
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </main>
  )
}
