import { format } from 'date-fns'
import type { EdgeSummary } from '@/types'

interface EdgeCardProps {
  edge: EdgeSummary
}

const statusStyles: Record<EdgeSummary['status'], string> = {
  'edge': 'border-emerald-500/80 bg-emerald-500/5 dark:bg-emerald-500/10',
  'monitor': 'border-amber-400/80 bg-amber-400/10 dark:bg-amber-400/20',
  'no-action': 'border-rose-500/70 bg-rose-500/5 dark:bg-rose-500/10',
}

const confidenceCopy: Record<EdgeSummary['confidence'], string> = {
  low: 'Low',
  medium: 'Medium',
  high: 'High',
}

function formatKickoff(timestamp: string) {
  try {
    return format(new Date(timestamp), 'EEE, MMM d • h:mm a')
  } catch (error) {
    return 'TBD'
  }
}

export default function EdgeCard({ edge }: EdgeCardProps) {
  const movementPercent = Math.min(100, Math.round((edge.movement / 5) * 100))
  const statusClass = statusStyles[edge.status]
  const keyNumberLabel = edge.keyNumbers.length > 0 ? edge.keyNumbers.join(', ') : null

  return (
    <article className={`card border-l-4 ${statusClass} p-4 transition hover:-translate-y-0.5 hover:shadow-lg`}> 
      <header className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">{edge.matchup}</h3>
          <p className="text-sm text-gray-500 dark:text-gray-400">Kickoff: {formatKickoff(edge.kickoff)}</p>
        </div>
        <div className="text-right text-sm">
          <p className="font-medium text-emerald-500 dark:text-emerald-300">{edge.movement.toFixed(1)} pt movement</p>
          <p className="text-xs text-gray-500 dark:text-gray-400">Confidence: {confidenceCopy[edge.confidence]}</p>
        </div>
      </header>

      <div className="mt-4 space-y-3">
        <div className="space-y-1" title="How far the market has moved between books. Bigger swings create double-edge opportunities.">
          <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
            <span>Line movement</span>
            <span>{movementPercent}% of 5pt window</span>
          </div>
          <div className="h-2 rounded-full bg-gray-200 dark:bg-slate-700">
            <div className="h-2 rounded-full bg-emerald-500 transition-all" style={{ width: `${movementPercent}%` }} />
          </div>
        </div>

        <div className="grid gap-3 text-sm sm:grid-cols-2">
          {edge.lowestTotal && (
            <div className="rounded-lg border border-gray-200/80 bg-white/60 p-3 dark:border-slate-700 dark:bg-slate-900/60">
              <p className="text-xs uppercase tracking-wide text-gray-500 dark:text-gray-400">Buy Low</p>
              <p className="mt-1 font-semibold text-gray-900 dark:text-gray-100">{edge.lowestTotal.point.toFixed(1)} total</p>
              <p className="text-xs text-gray-500 dark:text-gray-400">{edge.lowestTotal.book} {edge.lowestTotal.price ? `(${edge.lowestTotal.price > 0 ? '+' : ''}${edge.lowestTotal.price})` : ''}</p>
            </div>
          )}

          {edge.highestTotal && (
            <div className="rounded-lg border border-gray-200/80 bg-white/60 p-3 dark:border-slate-700 dark:bg-slate-900/60">
              <p className="text-xs uppercase tracking-wide text-gray-500 dark:text-gray-400">Sell High</p>
              <p className="mt-1 font-semibold text-gray-900 dark:text-gray-100">{edge.highestTotal.point.toFixed(1)} total</p>
              <p className="text-xs text-gray-500 dark:text-gray-400">{edge.highestTotal.book} {edge.highestTotal.price ? `(${edge.highestTotal.price > 0 ? '+' : ''}${edge.highestTotal.price})` : ''}</p>
            </div>
          )}
        </div>

        <div className="rounded-lg border border-dashed border-emerald-400/60 bg-emerald-500/5 p-3 text-sm text-emerald-700 dark:border-emerald-400/40 dark:bg-emerald-500/10 dark:text-emerald-200">
          <p className="font-medium">Recommendation</p>
          <p className="mt-1 leading-relaxed">{edge.recommendation}</p>
          <p className="mt-2 text-xs text-emerald-600/80 dark:text-emerald-300/80" title="Education first: this system highlights discrepancies so you can learn how markets move.">
            Track only — not financial advice.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3 text-xs text-gray-500 dark:text-gray-400">
          {edge.averageTotal != null && (
            <span className="rounded-full bg-gray-100 px-2 py-0.5 dark:bg-slate-800">Avg total {edge.averageTotal.toFixed(1)}</span>
          )}
          {keyNumberLabel && (
            <span className="rounded-full bg-amber-100 px-2 py-0.5 text-amber-700 dark:bg-amber-900/50 dark:text-amber-200" title="Totals that land on key football numbers tend to get stuck. Watch closely.">
              ⚠️ Key number: {keyNumberLabel}
            </span>
          )}
          <span className="rounded-full bg-slate-100 px-2 py-0.5 dark:bg-slate-800">Source: {edge.source ?? 'mixed'}</span>
        </div>
      </div>
    </article>
  )
}
