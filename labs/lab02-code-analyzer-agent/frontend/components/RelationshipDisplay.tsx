import { GitBranch, FileText } from 'lucide-react'

interface RelationshipDisplayProps {
  relationships: string[]
  overallSummary: string
}

export default function RelationshipDisplay({
  relationships,
  overallSummary,
}: RelationshipDisplayProps) {
  return (
    <div className="space-y-4">
      {/* Overall summary card */}
      <div className="bg-indigo-50 rounded-xl border border-indigo-200 p-6">
        <h2 className="text-lg font-semibold text-indigo-900 mb-3 flex items-center gap-2">
          <FileText className="w-5 h-5" />
          Overall Summary
        </h2>
        <p className="text-indigo-800 leading-relaxed">{overallSummary}</p>
      </div>

      {/* Relationships list */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-100 flex justify-between items-center bg-gray-50">
          <h2 className="font-semibold text-gray-900 flex items-center gap-2">
            <GitBranch className="w-5 h-5 text-indigo-600" />
            Cross-file Relationships
          </h2>
          <span className="bg-gray-200 text-gray-600 text-xs px-2 py-1 rounded-full font-medium">
            {relationships.length}
          </span>
        </div>

        {relationships.length === 0 ? (
          <div className="p-8 text-center text-gray-500 text-sm">
            No cross-file relationships detected.
          </div>
        ) : (
          <ul className="divide-y divide-gray-100">
            {relationships.map((rel, idx) => (
              <li key={idx} className="px-6 py-4 flex items-start gap-3 hover:bg-gray-50 transition-colors">
                <div className="flex-shrink-0 w-1.5 h-1.5 rounded-full bg-indigo-400 mt-2" />
                <span className="text-gray-700 text-sm">{rel}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
