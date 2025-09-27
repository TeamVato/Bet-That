import { useCallback, useEffect, useMemo } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { formatDistanceToNow } from 'date-fns'
import GameList from './GameList'
import TokenStatus from './TokenStatus'
import { getTokenStatus, getWeeklyOdds, invalidateCache } from '@/services/api'
import type { EdgeSummary, EdgeStatus, GameOdds, LineSnapshot } from '@/types'

const AUTO_REFRESH_MS = 5 * 60 * 1000

function buildTotalsSnapshot(game: GameOdds) {
  const totals: LineSnapshot[] = Array.isArray(game.totals_points) ? [...game.totals_points] : []
  if (totals.length === 0 && game.best_totals) {
    Object.entries(game.best_totals).forEach(([name, line]) => {
      if (line.point != null) {
        totals.push({ book: line.bookmaker || name, point: line.point, price: line.price })
      }
    })
  }
  const sorted = totals.sort((a, b) => a.point - b.point)
  const lowest = sorted[0]
  const highest = sorted[sorted.length - 1]
  const movementFromTotals = lowest && highest ? highest.point - lowest.point : 0
  const movement = typeof game.totals_movement === 'number' ? game.totals_movement : movementFromTotals
  const average = typeof game.average_total === 'number'
    ? game.average_total
    : sorted.length
      ? sorted.reduce((acc, item) => acc + item.point, 0) / sorted.length
      : null

  return { movement, lowest, highest, average }
}

function movementStatus(movement: number): EdgeStatus {
  if (movement >= 2) return 'edge'
  if (movement >= 1) return 'monitor'
  return 'no-action'
}

function buildEdgeSummary(game: GameOdds, source?: string): EdgeSummary | null {
  const { movement, lowest, highest, average } = buildTotalsSnapshot(game)
  if (movement < 2) return null

  const confidence: EdgeSummary['confidence'] = movement >= 3 ? 'high' : 'medium'
  const matchup = `${game.away_team} @ ${game.home_team}`
  const recommendation = game.recommendation
    ?? (lowest && highest
      ? `Grab Over ${lowest.point.toFixed(1)} at ${lowest.book} and keep Under ${highest.point.toFixed(1)} at ${highest.book} on your radar.`
      : 'Lock the best number across the board before it snaps back.')

  return {
    gameId: game.id,
    matchup,
    kickoff: game.commence_time,
    movement: Number.isFinite(movement) ? Number(movement) : 0,
    averageTotal: average,
    keyNumbers: Array.isArray(game.key_numbers) ? game.key_numbers : [],
    highestTotal: highest,
    lowestTotal: lowest,
    recommendation,
    confidence,
    status: 'edge',
    source,
  }
}

export default function Dashboard() {
  const queryClient = useQueryClient()

  const weeklyOddsQuery = useQuery({
    queryKey: ['nfl-week'],
    queryFn: ({ meta }) => getWeeklyOdds(Boolean(meta?.forceRefresh)),
    staleTime: 60_000,
    gcTime: 5 * 60 * 1000,
  })

  const tokenStatusQuery = useQuery({
    queryKey: ['token-status'],
    queryFn: ({ meta }) => getTokenStatus(Boolean(meta?.forceRefresh)),
    staleTime: 120_000,
    gcTime: 10 * 60 * 1000,
  })

  useEffect(() => {
    const interval = setInterval(() => {
      queryClient.invalidateQueries({ queryKey: ['nfl-week'] })
      queryClient.invalidateQueries({ queryKey: ['token-status'] })
    }, AUTO_REFRESH_MS)
    return () => clearInterval(interval)
  }, [queryClient])

  const { edges, games } = useMemo(() => {
    const payload = weeklyOddsQuery.data
    const gamesPayload: GameOdds[] = payload?.data ?? []
    const derivedEdges: EdgeSummary[] = []
    const derivedGames = gamesPayload.map((game) => {
      const { movement, lowest, highest, average } = buildTotalsSnapshot(game)
      const matchup = `${game.away_team} @ ${game.home_team}`
      const status = movementStatus(movement)

      if (movement >= 2) {
        const edge = buildEdgeSummary(game, payload?.source)
        if (edge) {
          derivedEdges.push(edge)
        }
      }

      const recommendation = game.recommendation
        ?? (status === 'edge' && lowest && highest
          ? `Edge window between ${lowest.book} (${lowest.point.toFixed(1)}) and ${highest.book} (${highest.point.toFixed(1)}).`
          : status === 'monitor'
            ? 'Hold tight—movement is building but not yet actionable.'
            : 'Nothing actionable yet. Keep learning the market flow.')

      return {
        id: game.id,
        matchup,
        kickoff: game.commence_time,
        movement: Number.isFinite(movement) ? Number(movement) : 0,
        averageTotal: average,
        lowestTotalPoint: lowest?.point,
        highestTotalPoint: highest?.point,
        lowestBook: lowest?.book,
        highestBook: highest?.book,
        keyNumbers: Array.isArray(game.key_numbers) ? game.key_numbers : [],
        status,
        onKeyNumber: Boolean(game.on_key_number),
        recommendation,
      }
    })

    return { edges: derivedEdges, games: derivedGames }
  }, [weeklyOddsQuery.data])

  const handleRefresh = useCallback(() => {
    invalidateCache()
    weeklyOddsQuery.refetch({ meta: { forceRefresh: true } })
    tokenStatusQuery.refetch({ meta: { forceRefresh: true } })
  }, [weeklyOddsQuery, tokenStatusQuery])

  const lastFetchedLabel = useMemo(() => {
    const fetchedAt = weeklyOddsQuery.data?.fetchedAt
    if (!fetchedAt) return undefined
    try {
      return formatDistanceToNow(new Date(fetchedAt), { addSuffix: true })
    } catch (error) {
      return undefined
    }
  }, [weeklyOddsQuery.data?.fetchedAt])

  const tokenLastUpdate = useMemo(() => {
    const stamp = tokenStatusQuery.data?.refreshed_at
    if (!stamp) return undefined
    try {
      return formatDistanceToNow(new Date(stamp), { addSuffix: true })
    } catch (error) {
      return undefined
    }
  }, [tokenStatusQuery.data?.refreshed_at])

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-2">
        <h1 className="text-2xl font-semibold text-gray-900 dark:text-gray-50">🏈 Bet-That Edge Tracker</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Monitoring totals movement for double-edge betting education.
        </p>
      </div>

      <TokenStatus
        status={tokenStatusQuery.data}
        isLoading={tokenStatusQuery.isLoading}
        error={tokenStatusQuery.error instanceof Error ? tokenStatusQuery.error.message : null}
        oddsSource={weeklyOddsQuery.data?.source}
        lastUpdateLabel={tokenLastUpdate}
      />

      <GameList
        games={games}
        edges={edges}
        isLoading={weeklyOddsQuery.isLoading}
        error={weeklyOddsQuery.error instanceof Error ? weeklyOddsQuery.error.message : null}
        onRefresh={handleRefresh}
        isRefreshing={weeklyOddsQuery.isFetching || tokenStatusQuery.isFetching}
        lastFetchedLabel={lastFetchedLabel}
      />
    </div>
  )
}
