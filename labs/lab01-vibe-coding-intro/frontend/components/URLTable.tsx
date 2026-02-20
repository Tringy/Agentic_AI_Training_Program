'use client'

import React, { useState } from 'react'

interface URLEntry {
  short_code: string
  original_url: string
  click_count: number
  created_at: string
  last_accessed_at?: string
}

interface URLTableProps {
  rows: URLEntry[]
  onDelete?: (shortCode: string) => void
  onCopy?: (url: string) => void
  loading?: boolean
}

export default function URLTable({ rows, onDelete, onCopy, loading = false }: URLTableProps) {
  const [copiedCode, setCopiedCode] = useState<string | null>(null)

  const handleCopy = async (url: string, code: string) => {
    try {
      await navigator.clipboard.writeText(url)
      setCopiedCode(code)
      setTimeout(() => setCopiedCode(null), 2000)
      onCopy?.(url)
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }

  const handleDelete = (code: string) => {
    if (window.confirm(`Delete short code '${code}'? This cannot be undone.`)) {
      onDelete?.(code)
    }
  }

  if (loading) {
    return <div className="text-center py-8 text-gray-500">Loading...</div>
  }

  if (rows.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <p className="text-lg">No URLs yet</p>
        <p className="text-sm">Create your first shortened URL to see them here</p>
      </div>
    )
  }

  return (
    <div className="overflow-x-auto border border-gray-200 rounded-lg">
      <table className="w-full">
        <thead className="bg-gray-50 border-b border-gray-200">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Short Code</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Original URL</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Clicks</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Created</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Actions</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200">
          {rows.map((row) => (
            <tr key={row.short_code} className="hover:bg-gray-50">
              <td className="px-6 py-4 font-mono text-sm font-medium text-blue-600">{row.short_code}</td>
              <td className="px-6 py-4 text-sm text-gray-600 max-w-xs truncate" title={row.original_url}>
                {row.original_url}
              </td>
              <td className="px-6 py-4 text-sm text-gray-900 font-medium">{row.click_count}</td>
              <td className="px-6 py-4 text-sm text-gray-600">
                {new Date(row.created_at).toLocaleDateString()}
              </td>
              <td className="px-6 py-4 text-sm">
                <button
                  onClick={() => handleCopy(`http://localhost:3000/${row.short_code}`, row.short_code)}
                  className={`px-3 py-1 rounded text-xs font-medium mr-2 transition-colors ${
                    copiedCode === row.short_code
                      ? 'bg-green-100 text-green-700'
                      : 'bg-blue-100 text-blue-700 hover:bg-blue-200'
                  }`}
                >
                  {copiedCode === row.short_code ? 'Copied!' : 'Copy'}
                </button>
                <button
                  onClick={() => handleDelete(row.short_code)}
                  className="px-3 py-1 rounded text-xs font-medium bg-red-100 text-red-700 hover:bg-red-200 transition-colors"
                >
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
