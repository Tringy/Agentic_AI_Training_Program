'use client'

import EvaluatePanel from '@/components/EvaluatePanel'

export default function EvaluatePage() {
  return (
    <main className="flex-1 max-w-7xl mx-auto w-full px-4 py-8">
      <div className="space-y-6">
        <div className="text-center space-y-2">
          <h1 className="text-3xl font-bold text-gray-900">Evaluate RAG Quality</h1>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Run retrieval and generation evaluation with labeled examples.
          </p>
        </div>
        <EvaluatePanel />
      </div>
    </main>
  )
}
