import { DetectionResult } from '../types'

const confidenceStyles: Record<DetectionResult['confidence'], string> = {
  high: 'bg-green-100 text-green-800 ring-green-300',
  medium: 'bg-yellow-100 text-yellow-800 ring-yellow-300',
  low: 'bg-red-100 text-red-800 ring-red-300',
}

export default function LanguageBadge({ detection }: { detection: DetectionResult }) {
  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ring-1 ${confidenceStyles[detection.confidence]}`}
      title={detection.alternatives.length > 0 ? `Alternatives: ${detection.alternatives.join(', ')}` : undefined}
    >
      {detection.language}
      <span className="opacity-60">({detection.confidence})</span>
    </span>
  )
}
