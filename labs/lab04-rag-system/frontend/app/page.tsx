'use client'

import IndexPanel from '@/components/IndexPanel'

export default function Home() {
  return (
    <main className="flex-1 max-w-7xl mx-auto w-full px-4 py-8">
      <div className="space-y-6">
        <div className="text-center space-y-2">
          <h1 className="text-3xl font-bold text-gray-900">Codebase RAG System</h1>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Index a GitHub repository, upload a local folder, or paste files manually — then query the codebase with natural language.
          </p>
        </div>
        <IndexPanel />
      </div>
    </main>
  )
}
