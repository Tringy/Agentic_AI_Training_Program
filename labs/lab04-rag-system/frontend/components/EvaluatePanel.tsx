'use client'

import { useState } from 'react'
import { Plus, Trash2, FlaskConical, AlertCircle, CheckCircle } from 'lucide-react'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface EvalExample {
  id: string
  question: string
  expected_answer: string
  relevant_files: string
}

interface EvalResults {
  retrieval: Record<string, number>
  generation: Record<string, number>
}

const DEFAULT_EXAMPLES: EvalExample[] = [
  {
    id: '1',
    question: 'How does login work?',
    expected_answer: 'Login validates credentials and returns a token.',
    relevant_files: 'auth.py',
  },
]

export default function EvaluatePanel() {
  const [examples, setExamples] = useState<EvalExample[]>(DEFAULT_EXAMPLES)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<EvalResults | null>(null)
  const [error, setError] = useState<string | null>(null)

  const addExample = () => {
    setExamples(prev => [
      ...prev,
      { id: Date.now().toString(), question: '', expected_answer: '', relevant_files: '' },
    ])
  }

  const removeExample = (id: string) => {
    setExamples(prev => prev.filter(e => e.id !== id))
  }

  const updateExample = (id: string, field: keyof Omit<EvalExample, 'id'>, value: string) => {
    setExamples(prev => prev.map(e => (e.id === id ? { ...e, [field]: value } : e)))
  }

  const handleEvaluate = async () => {
    const valid = examples.filter(e => e.question.trim() && e.expected_answer.trim())
    if (valid.length === 0) {
      setError('Add at least one evaluation example.')
      return
    }

    setLoading(true)
    setError(null)
    setResult(null)

    const payload = valid.map(e => ({
      question: e.question.trim(),
      expected_answer: e.expected_answer.trim(),
      relevant_files: e.relevant_files
        .split(',')
        .map(s => s.trim())
        .filter(Boolean),
    }))

    try {
      const res = await fetch(`${API_URL}/evaluate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ examples: payload }),
      })
      if (!res.ok) {
        const data = await res.json()
        throw new Error(data.detail || 'Evaluation failed')
      }
      setResult(await res.json())
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Examples */}
      <div className="space-y-4">
        {examples.map((ex, idx) => (
          <div key={ex.id} className="bg-white border border-gray-200 rounded-xl p-5 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm font-semibold text-gray-600">Example #{idx + 1}</span>
              {examples.length > 1 && (
                <button
                  onClick={() => removeExample(ex.id)}
                  className="text-gray-400 hover:text-red-500 transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              )}
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-500 mb-1">Question</label>
              <input
                type="text"
                placeholder="How does login work?"
                value={ex.question}
                onChange={e => updateExample(ex.id, 'question', e.target.value)}
                className="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-violet-500"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-500 mb-1">Expected Answer</label>
              <textarea
                placeholder="Describe the expected correct answer…"
                value={ex.expected_answer}
                onChange={e => updateExample(ex.id, 'expected_answer', e.target.value)}
                rows={2}
                className="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-violet-500 resize-none"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-500 mb-1">
                Relevant Files{' '}
                <span className="text-gray-400 font-normal">(comma-separated)</span>
              </label>
              <input
                type="text"
                placeholder="auth.py, utils.py"
                value={ex.relevant_files}
                onChange={e => updateExample(ex.id, 'relevant_files', e.target.value)}
                className="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 font-mono focus:outline-none focus:ring-2 focus:ring-violet-500"
              />
            </div>
          </div>
        ))}
      </div>

      <div className="flex gap-3">
        <button
          onClick={addExample}
          className="flex items-center gap-2 text-sm px-4 py-2 rounded-lg border border-gray-200 hover:bg-gray-50 text-gray-600 transition-colors"
        >
          <Plus className="w-4 h-4" />
          Add Example
        </button>
        <button
          onClick={handleEvaluate}
          disabled={loading}
          className="flex items-center gap-2 text-sm px-6 py-2 rounded-lg bg-violet-600 hover:bg-violet-700 text-white font-medium transition-colors disabled:opacity-50"
        >
          <FlaskConical className="w-4 h-4" />
          {loading ? 'Evaluating…' : 'Run Evaluation'}
        </button>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 flex gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="space-y-4">
          <div className="flex gap-3">
            <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
            <p className="text-sm font-semibold text-green-800">Evaluation complete</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Retrieval Metrics */}
            <div className="bg-white border border-gray-200 rounded-xl p-5">
              <h3 className="text-sm font-semibold text-gray-700 mb-4">Retrieval Metrics</h3>
              <div className="space-y-3">
                {Object.entries(result.retrieval).map(([key, value]) => (
                  <div key={key} className="flex items-center justify-between">
                    <span className="text-sm text-gray-600 font-mono">{key}</span>
                    <MetricBar value={typeof value === 'number' ? value : 0} />
                  </div>
                ))}
              </div>
            </div>
            {/* Generation Metrics */}
            <div className="bg-white border border-gray-200 rounded-xl p-5">
              <h3 className="text-sm font-semibold text-gray-700 mb-4">Generation Metrics</h3>
              <div className="space-y-3">
                {Object.entries(result.generation).map(([key, value]) => (
                  <div key={key} className="flex items-center justify-between">
                    <span className="text-sm text-gray-600 font-mono">{key}</span>
                    <MetricBar value={typeof value === 'number' ? value : 0} />
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function MetricBar({ value }: { value: number }) {
  const isCount = value > 1
  const pct = isCount ? null : Math.round(value * 100)
  return (
    <div className="flex items-center gap-2">
      {pct !== null && (
        <div className="w-24 h-2 bg-gray-100 rounded-full overflow-hidden">
          <div
            className="h-full bg-violet-500 rounded-full"
            style={{ width: `${pct}%` }}
          />
        </div>
      )}
      <span className="text-sm font-semibold text-gray-800 w-12 text-right">
        {isCount ? value : `${pct}%`}
      </span>
    </div>
  )
}
