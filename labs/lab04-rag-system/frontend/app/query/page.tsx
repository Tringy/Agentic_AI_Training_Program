'use client'

import QueryPanel from '@/components/QueryPanel'

export default function QueryPage() {
  return (
    <main className="flex-1 max-w-7xl mx-auto w-full px-4 py-8">
      <div className="space-y-6">
        <div className="text-center space-y-2">
          <h1 className="text-3xl font-bold text-gray-900">Query Codebase</h1>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Ask natural language questions about your indexed codebase.
          </p>
        </div>
        <QueryPanel />
      </div>
    </main>
  )
}
