'use client'

import { useState } from 'react'
import CodeAnalyzer from '@/components/CodeAnalyzer'
import CacheStatsBar from '@/components/CacheStatsBar'

export default function Home() {
  const [statsRefreshKey, setStatsRefreshKey] = useState(0)

  return (
    <main className="flex-1 max-w-7xl mx-auto w-full px-4 py-8">
      <div className="space-y-6">
        <div className="text-center space-y-2">
          <h1 className="text-3xl font-bold text-gray-900">Code Analysis Agent</h1>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Paste your code below to get instant feedback on bugs, security issues, performance, and more.
          </p>
        </div>
        <CacheStatsBar refreshKey={statsRefreshKey} />
        <CodeAnalyzer onAnalysisComplete={() => setStatsRefreshKey((k) => k + 1)} />
      </div>
    </main>
  )
}
