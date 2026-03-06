'use client'

import { useState } from 'react'
import { AlertCircle, Shield, Zap, Terminal, Code2, Play } from 'lucide-react'
import clsx from 'clsx'
import AnalysisDisplay from './AnalysisDisplay'
import LanguageBadge from './LanguageBadge'
import { AnalysisResult, DetectionResult } from '../types'

type AnalysisType = 'general' | 'security' | 'performance'

interface CodeAnalyzerProps {
  onAnalysisComplete?: () => void
}

const LANGUAGES = [
  'auto',
  'python',
  'javascript',
  'typescript',
  'java',
  'cpp',
  'go',
  'rust',
]

export default function CodeAnalyzer({ onAnalysisComplete }: CodeAnalyzerProps = {}) {
  const [code, setCode] = useState('')
  const [language, setLanguage] = useState('auto')
  const [analysisType, setAnalysisType] = useState<AnalysisType>('general')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [detectionResult, setDetectionResult] = useState<DetectionResult | null>(null)
  const [cacheHit, setCacheHit] = useState(false)

  const handleAnalyze = async () => {
    if (!code.trim()) return

    setLoading(true)
    setError(null)
    setResult(null)
    setDetectionResult(null)
    setCacheHit(false)

    try {
      const endpoint = analysisType === 'general' ? '/analyze' : `/analyze/${analysisType}`
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      
      const response = await fetch(`${apiUrl}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ code, language }),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `Analysis failed: ${response.statusText}`)
      }

      const hit = response.headers.get('X-Cache') === 'HIT'
      setCacheHit(hit)
      const data = await response.json()
      setResult(data)
      onAnalysisComplete?.()

      if (language === 'auto') {
        const detRes = await fetch(`${apiUrl}/detect-language`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ code }),
        })
        if (detRes.ok) {
          const detData = await detRes.json()
          setDetectionResult(detData)
        }
      }
    } catch (err: any) {
      setError(err.message || 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
      {/* Left Column: Input */}
      <div className="space-y-4">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <Code2 className="w-5 h-5 text-indigo-600" />
              Source Code
            </h2>
            <div className="flex gap-2">
              <div className="flex items-center gap-2">
                <select
                  value={language}
                  onChange={(e) => { setLanguage(e.target.value); setDetectionResult(null) }}
                  className="block w-36 rounded-md border-0 py-1.5 pl-3 pr-8 text-gray-900 ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-indigo-600 sm:text-sm sm:leading-6"
                >
                  {LANGUAGES.map((lang) => (
                    <option key={lang} value={lang}>
                      {lang === 'auto' ? 'Auto-detect' : lang.charAt(0).toUpperCase() + lang.slice(1)}
                    </option>
                  ))}
                </select>
                {detectionResult && <LanguageBadge detection={detectionResult} />}
              </div>
            </div>
          </div>

          <textarea
            value={code}
            onChange={(e) => setCode(e.target.value)}
            placeholder="Paste your code here..."
            className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6 font-mono min-h-[400px]"
            spellCheck={false}
          />

          <div className="flex gap-2 pt-2">
            <button
              onClick={() => setAnalysisType('general')}
              className={clsx(
                'flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors',
                analysisType === 'general'
                  ? 'bg-indigo-50 text-indigo-700 ring-1 ring-indigo-200'
                  : 'bg-white text-gray-700 hover:bg-gray-50 ring-1 ring-gray-200'
              )}
            >
              <Terminal className="w-4 h-4" />
              General
            </button>
            <button
              onClick={() => setAnalysisType('security')}
              className={clsx(
                'flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors',
                analysisType === 'security'
                  ? 'bg-red-50 text-red-700 ring-1 ring-red-200'
                  : 'bg-white text-gray-700 hover:bg-gray-50 ring-1 ring-gray-200'
              )}
            >
              <Shield className="w-4 h-4" />
              Security
            </button>
            <button
              onClick={() => setAnalysisType('performance')}
              className={clsx(
                'flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors',
                analysisType === 'performance'
                  ? 'bg-amber-50 text-amber-700 ring-1 ring-amber-200'
                  : 'bg-white text-gray-700 hover:bg-gray-50 ring-1 ring-gray-200'
              )}
            >
              <Zap className="w-4 h-4" />
              Performance
            </button>
          </div>

          <button
            onClick={handleAnalyze}
            disabled={loading || !code.trim()}
            className="w-full flex items-center justify-center gap-2 bg-indigo-600 text-white px-4 py-3 rounded-lg font-medium hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" />
                Analyzing...
              </>
            ) : (
              <>
                <Play className="w-4 h-4" />
                Run Analysis
              </>
            )}
          </button>
        </div>
      </div>

      {/* Right Column: Output */}
      <div className="space-y-4">
        {error && (
          <div className="rounded-md bg-red-50 p-4 border border-red-200">
            <div className="flex">
              <div className="flex-shrink-0">
                <AlertCircle className="h-5 w-5 text-red-400" aria-hidden="true" />
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Analysis Error</h3>
                <div className="mt-2 text-sm text-red-700">
                  <p>{error}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {cacheHit && result && (
          <div className="flex items-center gap-1.5 text-xs font-medium text-green-700 bg-green-50 border border-green-200 rounded-md px-3 py-1.5 w-fit">
            <span className="w-2 h-2 rounded-full bg-green-500 inline-block" />
            Served from cache
          </div>
        )}

        {result ? (
          <AnalysisDisplay result={result} type={analysisType} />
        ) : (
          <div className="h-full flex flex-col items-center justify-center text-gray-400 border-2 border-dashed border-gray-200 rounded-xl min-h-[400px]">
            <Terminal className="w-12 h-12 mb-4 opacity-20" />
            <p className="text-sm text-gray-500">Run an analysis to see results here</p>
          </div>
        )}
      </div>
    </div>
  )
}
