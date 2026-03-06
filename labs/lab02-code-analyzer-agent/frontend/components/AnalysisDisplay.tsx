import { CheckCircle, AlertTriangle, AlertOctagon, Info, ArrowUpRight } from 'lucide-react'
import clsx from 'clsx'
import { AnalysisResult } from '../types'

const SeverityIcon = ({ severity }: { severity: string }) => {
  switch (severity) {
    case 'critical':
      return <AlertOctagon className="w-5 h-5 text-red-600" />
    case 'high':
      return <AlertTriangle className="w-5 h-5 text-orange-500" />
    case 'medium':
      return <Info className="w-5 h-5 text-blue-500" />
    case 'low':
      return <CheckCircle className="w-5 h-5 text-gray-400" />
    default:
      return <Info className="w-5 h-5 text-gray-400" />
  }
}

const MetricCard = ({ label, value }: { label: string; value: string }) => (
  <div className="bg-gray-50 rounded-lg p-3 text-center border border-gray-100">
    <div className="text-xs text-gray-500 uppercase tracking-wide font-medium">{label}</div>
    <div className="text-lg font-semibold text-gray-900 mt-1 capitalize">{value}</div>
  </div>
)

export default function AnalysisDisplay({ result, type }: { result: AnalysisResult; type: string }) {
  return (
    <div className="space-y-6">
      {/* Summary Card */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Analysis Summary</h3>
        <p className="text-gray-600 leading-relaxed">{result.summary}</p>
        
        <div className="grid grid-cols-3 gap-4 mt-6">
          <MetricCard label="Complexity" value={result.metrics.complexity} />
          <MetricCard label="Readability" value={result.metrics.readability} />
          <MetricCard label="Testability" value={result.metrics.test_coverage_estimate} />
        </div>
      </div>

      {/* Issues List */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-100 flex justify-between items-center bg-gray-50">
          <h3 className="font-semibold text-gray-900">Issues Found</h3>
          <span className="bg-gray-200 text-gray-600 text-xs px-2 py-1 rounded-full font-medium">
            {result.issues.length}
          </span>
        </div>
        <div className="divide-y divide-gray-100">
          {result.issues.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              <CheckCircle className="w-8 h-8 mx-auto mb-2 text-green-500 opacity-50" />
              <p>No issues found! Great job.</p>
            </div>
          ) : (
            result.issues.map((issue, idx) => (
              <div key={idx} className="p-6 hover:bg-gray-50 transition-colors group">
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0 mt-1">
                    <SeverityIcon severity={issue.severity} />
                  </div>
                  <div className="flex-1 space-y-2">
                    <div className="flex items-center gap-2">
                      <span className={clsx(
                        "text-xs font-medium px-2 py-0.5 rounded uppercase tracking-wide",
                        issue.severity === 'critical' ? 'bg-red-100 text-red-800' :
                        issue.severity === 'high' ? 'bg-orange-100 text-orange-800' :
                        issue.severity === 'medium' ? 'bg-blue-100 text-blue-800' :
                        'bg-gray-100 text-gray-800'
                      )}>
                        {issue.severity}
                      </span>
                      <span className="text-xs text-gray-500 font-mono bg-gray-100 px-2 py-0.5 rounded">
                        {issue.line ? `Line ${issue.line}` : 'General'}
                      </span>
                      <span className="text-xs text-gray-500 capitalize ml-auto">
                        {issue.category}
                      </span>
                    </div>
                    <p className="text-gray-900 font-medium">{issue.description}</p>
                    <div className="bg-indigo-50 rounded-md p-3 text-sm text-indigo-900">
                      <span className="font-semibold mr-1">Fix:</span>
                      {issue.suggestion}
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Suggestions */}
      {result.suggestions.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <ArrowUpRight className="w-5 h-5 text-indigo-600" />
            General Improvements
          </h3>
          <ul className="space-y-3">
            {result.suggestions.map((suggestion, idx) => (
              <li key={idx} className="flex items-start gap-3 text-gray-600">
                <div className="flex-shrink-0 w-1.5 h-1.5 rounded-full bg-indigo-400 mt-2" />
                <span>{suggestion}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
