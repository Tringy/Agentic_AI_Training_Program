import { CheckCircle, AlertTriangle, AlertOctagon, Info, ShieldAlert } from 'lucide-react'
import clsx from 'clsx'
import { DiffResult, Issue, Metrics } from '../types'

const SeverityIcon = ({ severity }: { severity: string }) => {
  switch (severity) {
    case 'critical':
      return <AlertOctagon className="w-4 h-4 text-red-600" />
    case 'high':
      return <AlertTriangle className="w-4 h-4 text-orange-500" />
    case 'medium':
      return <Info className="w-4 h-4 text-blue-500" />
    default:
      return <CheckCircle className="w-4 h-4 text-gray-400" />
  }
}

function IssueList({ issues, tint }: { issues: Issue[]; tint: 'red' | 'green' }) {
  if (issues.length === 0) {
    return (
      <div className="p-6 text-center text-gray-400 text-sm">
        <CheckCircle className="w-6 h-6 mx-auto mb-1 opacity-40" />
        None
      </div>
    )
  }
  return (
    <div className="divide-y divide-gray-100">
      {issues.map((issue, idx) => (
        <div
          key={idx}
          className={clsx(
            'p-4 text-sm',
            tint === 'red' ? 'bg-red-50' : 'bg-green-50'
          )}
        >
          <div className="flex items-center gap-2 mb-1">
            <SeverityIcon severity={issue.severity} />
            <span
              className={clsx(
                'text-xs font-medium px-1.5 py-0.5 rounded uppercase',
                issue.severity === 'critical'
                  ? 'bg-red-100 text-red-800'
                  : issue.severity === 'high'
                  ? 'bg-orange-100 text-orange-800'
                  : issue.severity === 'medium'
                  ? 'bg-blue-100 text-blue-800'
                  : 'bg-gray-100 text-gray-700'
              )}
            >
              {issue.severity}
            </span>
            <span className="text-xs text-gray-500 font-mono">
              {issue.line ? `L${issue.line}` : 'General'}
            </span>
            <span className="text-xs text-gray-400 capitalize ml-auto">{issue.category}</span>
          </div>
          <p className="text-gray-900 font-medium">{issue.description}</p>
          <p className="text-gray-600 mt-1 text-xs">{issue.suggestion}</p>
        </div>
      ))}
    </div>
  )
}

function MetricsRow({ before, after }: { before: Metrics; after: Metrics }) {
  const rows = [
    { label: 'Complexity', b: before.complexity, a: after.complexity },
    { label: 'Readability', b: before.readability, a: after.readability },
    { label: 'Testability', b: before.test_coverage_estimate, a: after.test_coverage_estimate },
  ]
  return (
    <table className="w-full text-sm">
      <thead>
        <tr className="text-xs text-gray-500 uppercase tracking-wide border-b border-gray-100">
          <th className="text-left py-2 pl-4 font-medium">Metric</th>
          <th className="text-center py-2 font-medium text-gray-500">
              <span className="inline-flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-red-400 inline-block" />Before</span>
            </th>
          <th className="text-center py-2 pr-4 font-medium text-gray-500">
              <span className="inline-flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-green-400 inline-block" />After</span>
            </th>
        </tr>
      </thead>
      <tbody>
        {rows.map(({ label, b, a }) => (
          <tr key={label} className="border-b border-gray-50 last:border-0">
            <td className="py-2 pl-4 text-gray-700">{label}</td>
            <td className="py-2 text-center capitalize text-red-700 font-medium">{b}</td>
            <td className="py-2 pr-4 text-center capitalize text-green-700 font-medium">{a}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

export default function DiffDisplay({ result }: { result: DiffResult }) {
  return (
    <div className="space-y-6">
      {/* Change Summary */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Change Summary</h3>
        <p className="text-gray-600 leading-relaxed">{result.change_summary}</p>
      </div>

      {/* Introduced / Resolved columns */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="px-4 py-3 bg-gray-50 border-b border-gray-100 flex items-center justify-between">
            <span className="text-sm font-semibold text-gray-900 flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-red-400 inline-block" />
              Introduced Issues
            </span>
            <span className="text-xs bg-red-100 text-red-700 px-2 py-0.5 rounded-full font-medium">
              {result.introduced.length}
            </span>
          </div>
          <IssueList issues={result.introduced} tint="red" />
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="px-4 py-3 bg-gray-50 border-b border-gray-100 flex items-center justify-between">
            <span className="text-sm font-semibold text-gray-900 flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-green-400 inline-block" />
              Resolved Issues
            </span>
            <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full font-medium">
              {result.resolved.length}
            </span>
          </div>
          <IssueList issues={result.resolved} tint="green" />
        </div>
      </div>

      {/* Regression Warnings */}
      {result.regressions.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-amber-200 p-6">
          <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-amber-500" />
            Regression Risks
          </h3>
          <ul className="space-y-2">
            {result.regressions.map((r, idx) => (
              <li key={idx} className="flex items-start gap-3 text-gray-700 text-sm">
                <div className="flex-shrink-0 w-1.5 h-1.5 rounded-full bg-amber-400 mt-1.5" />
                {r}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Side-by-side Metrics */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="px-4 py-3 border-b border-gray-100 bg-gray-50">
          <h3 className="font-semibold text-gray-900 text-sm">Metrics Comparison</h3>
        </div>
        <MetricsRow before={result.metrics_before} after={result.metrics_after} />
      </div>
    </div>
  )
}
