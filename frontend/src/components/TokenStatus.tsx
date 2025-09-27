import type { TokenStatus as TokenStatusPayload } from '@/types'

interface TokenStatusProps {
  status?: TokenStatusPayload
  isLoading?: boolean
  error?: string | null
  oddsSource?: string
  lastUpdateLabel?: string
}

function computeIndicator(status?: TokenStatusPayload) {
  if (!status) {
    return { color: 'bg-gray-400', label: 'Unknown' }
  }
  const remaining = status.requests_remaining ?? 0
  const limit = status.daily_limit ?? 0
  if (remaining <= 0) {
    return { color: 'bg-red-500', label: 'Exhausted' }
  }
  if (remaining / Math.max(limit, 1) < 0.25) {
    return { color: 'bg-amber-400', label: 'Tight' }
  }
  return { color: 'bg-emerald-500', label: 'Healthy' }
}

export default function TokenStatus({ status, isLoading, error, oddsSource, lastUpdateLabel }: TokenStatusProps) {
  const indicator = computeIndicator(status)
  const blockedKeys = status?.blocked_keys ? Object.keys(status.blocked_keys) : []

  return (
    <div className="card p-4 bg-white/80 dark:bg-slate-900/70">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-xs uppercase tracking-wide text-gray-500 dark:text-gray-400">Token Status</p>
          {isLoading ? (
            <p className="mt-1 text-sm text-gray-600 dark:text-gray-300">Checking usage…</p>
          ) : error ? (
            <p className="mt-1 text-sm text-red-500">{error}</p>
          ) : status ? (
            <div className="mt-1 flex flex-wrap items-center gap-3 text-sm text-gray-700 dark:text-gray-200">
              <span className="inline-flex items-center gap-2">
                <span className={`h-2.5 w-2.5 rounded-full ${indicator.color}`} aria-hidden />
                <span className="font-medium">{indicator.label}</span>
              </span>
              <span className="text-gray-500 dark:text-gray-400">{status.requests_remaining} remaining / {status.daily_limit} daily limit</span>
              {status.keys_configured != null && (
                <span className="text-gray-500 dark:text-gray-400">Keys: {status.keys_configured}</span>
              )}
              {blockedKeys.length > 0 && (
                <span className="rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-700 dark:bg-amber-900/40 dark:text-amber-200">
                  {blockedKeys.length} key{blockedKeys.length === 1 ? '' : 's'} cooling
                </span>
              )}
            </div>
          ) : (
            <p className="mt-1 text-sm text-gray-600 dark:text-gray-300">Status unavailable.</p>
          )}
        </div>
        <div className="text-right text-xs text-gray-500 dark:text-gray-400 space-y-1">
          {lastUpdateLabel && <p>Updated: {lastUpdateLabel}</p>}
          {oddsSource && <p>Source: {oddsSource === 'cache' ? 'Cached snapshot' : oddsSource === 'live' ? 'Live pull' : oddsSource}</p>}
          <p className="italic text-gray-400">For education & tracking only</p>
        </div>
      </div>
    </div>
  )
}
