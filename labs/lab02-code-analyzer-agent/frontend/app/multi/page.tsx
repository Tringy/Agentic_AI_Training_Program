'use client'

import { useState } from 'react'
import MultiFileAnalyzer from '../../components/MultiFileAnalyzer'
import CacheStatsBar from '../../components/CacheStatsBar'

export default function MultiPage() {
  const [statsRefreshKey, setStatsRefreshKey] = useState(0)

  return (
    <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Multi-file Analysis</h1>
        <p className="mt-2 text-gray-500">
          Submit 2–10 files to receive individual analysis plus a cross-file relationship report.
        </p>
      </div>
      <div className="mb-6">
        <CacheStatsBar refreshKey={statsRefreshKey} />
      </div>
      <MultiFileAnalyzer onAnalysisComplete={() => setStatsRefreshKey((k) => k + 1)} />
    </main>
  )
}
