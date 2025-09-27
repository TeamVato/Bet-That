import { format } from 'date-fns'
import EdgeCard from './EdgeCard'
import type { EdgeSummary, EdgeStatus } from '@/types'

interface EnrichedGame {
  id: string
  matchup: string
  kickoff: string
  movement: number
  averageTotal?: number | null
  lowestTotalPoint?: number
  highestTotalPoint?: number
  lowestBook?: string
  highestBook?: string
  keyNumbers: number[]
  status: EdgeStatus
  onKeyNumber?: boolean
  recommendation?: string
}

interface GameListProps {
  games: EnrichedGame[]
  edges: EdgeSummary[]
  isLoading?: boolean
  error?: string | null
  onRefresh: () => void
  isRefreshing?: boolean
  lastFetchedLabel?: string
}

const statusBadge: Record<EdgeStatus, string> = {
  'edge': 'bg-emerald-500/20 text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-200',
  'monitor': 'bg-amber-400/20 text-amber-600 dark:bg-amber-400/20 dark:text-amber-200',
  'no-action': 'bg-rose-500/15 text-rose-600 dark:bg-rose-500/20 dark:text-rose-200',
}

const statusCopy: Record<EdgeStatus, string> = {
  'edge': 'Edge found',
  'monitor': 'Monitoring',
  'no-action': 'No action',
}

function formatKickoff(time: string) {
  try {
    return format(new Date(time), 'EEE h:mm a')
  } catch (error) {
    return 'TBD'
  }
}

export default function GameList({ games, edges, isLoading, error, onRefresh, isRefreshing, lastFetchedLabel }: GameListProps) {
  return (
    <section className="space-y-6">
      <header className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-50">This Week&apos;s Games</h2>
          <p className="text-sm text-gray-500 dark:text-gray-400">Tracking totals movement across top U.S. books.</p>
          {lastFetchedLabel && (
            <p className="text-xs text-gray-400 dark:text-gray-500">Updated {lastFetchedLabel}</p>
          )}
        </div>
        <button
          className="btn border-gray-300 bg-white text-sm dark:border-slate-700 dark:bg-slate-900"
          onClick={onRefresh}
          disabled={isRefreshing}
        >
          {isRefreshing ? 'Refreshing…' : 'Refresh Data'}
        </button>
      </header>

      {isLoading ? (
        <div className="rounded-2xl border border-dashed border-gray-300 p-10 text-center text-sm text-gray-500 dark:border-slate-700 dark:text-gray-400">
          Loading the latest board…
        </div>
      ) : error ? (
        <div className="rounded-2xl border border-rose-400/60 bg-rose-50 p-4 text-sm text-rose-600 dark:border-rose-500/40 dark:bg-rose-500/10 dark:text-rose-200">
          {error}
        </div>
      ) : (
        <div className="space-y-6">
          <section className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-base font-medium text-gray-900 dark:text-gray-100">Double-Edge Opportunities</h3>
              <span className="text-xs text-gray-500 dark:text-gray-400" title="Edges flag 2+ point gaps between books. That is usually when arbitrage windows open.">
                Threshold: 2pt movement
              </span>
            </div>
            {edges.length === 0 ? (
              <div className="rounded-2xl border border-dashed border-gray-300 bg-white/40 p-6 text-sm leading-relaxed text-gray-600 dark:border-slate-700 dark:bg-slate-900/40 dark:text-gray-300">
                No edges right now — totally normal. Markets usually pop closer to kickoff. Keep tracking movement or set alerts.
              </div>
            ) : (
              <div className="grid gap-4 md:grid-cols-2">
                {edges.map(edge => <EdgeCard key={edge.gameId} edge={edge} />)}
              </div>
            )}
          </section>

          <section className="space-y-4">
            <h3 className="text-base font-medium text-gray-900 dark:text-gray-100">Full Board</h3>
            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              {games.map(game => (
                <article key={game.id} className="card p-4 bg-white/80 dark:bg-slate-900/70">
                  <header className="flex items-start justify-between gap-2">
                    <div>
                      <p className="text-sm font-semibold text-gray-900 dark:text-gray-100">{game.matchup}</p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">{formatKickoff(game.kickoff)}</p>
                    </div>
                    <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${statusBadge[game.status]}`}>{statusCopy[game.status]}</span>
                  </header>
                  <dl className="mt-3 space-y-2 text-xs text-gray-600 dark:text-gray-300">
                    <div className="flex items-center justify-between" title="Total gap between books">
                      <dt className="uppercase tracking-wide text-gray-500 dark:text-gray-400">Movement</dt>
                      <dd className="font-semibold text-gray-900 dark:text-gray-100">{game.movement.toFixed(1)} pts</dd>
                    </div>
                    {game.lowestTotalPoint !== undefined && game.highestTotalPoint !== undefined && (
                      <div className="flex flex-wrap gap-x-4 gap-y-1">
                        <div>
                          <dt className="uppercase tracking-wide text-gray-500 dark:text-gray-400">Low</dt>
                          <dd>{game.lowestTotalPoint.toFixed(1)} ({game.lowestBook})</dd>
                        </div>
                        <div>
                          <dt className="uppercase tracking-wide text-gray-500 dark:text-gray-400">High</dt>
                          <dd>{game.highestTotalPoint.toFixed(1)} ({game.highestBook})</dd>
                        </div>
                      </div>
                    )}
                    {game.averageTotal != null && (
                      <div>
                        <dt className="uppercase tracking-wide text-gray-500 dark:text-gray-400">Avg</dt>
                        <dd>{game.averageTotal.toFixed(1)}</dd>
                      </div>
                    )}
                    {game.keyNumbers.length > 0 && (
                      <div className="flex items-center gap-1 text-amber-600 dark:text-amber-300" title="Totals close to key football numbers demand extra caution.">
                        <span>⚠️ Key number {game.keyNumbers.join(', ')}</span>
                      </div>
                    )}
                  </dl>
                  <p className="mt-3 text-xs text-gray-500 dark:text-gray-400" title="Educational tip">
                    {game.recommendation ?? 'Keep tracking for double-edge swing.'}
                  </p>
                </article>
              ))}
            </div>
          </section>
        </div>
      )}
    </section>
  )
}
