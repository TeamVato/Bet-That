import axios, { AxiosInstance } from 'axios'
import type { WeeklyOddsResponse, TokenStatus } from '@/types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'
const CACHE_TTL_MS = 4 * 60 * 1000 // 4 minutes keeps us under the 5 minute refresh cadence

type CacheRecord<T> = {
  value: T | null
  timestamp: number
}

const cache: {
  weeklyOdds: CacheRecord<WeeklyOddsResponse>
  tokenStatus: CacheRecord<TokenStatus>
} = {
  weeklyOdds: { value: null, timestamp: 0 },
  tokenStatus: { value: null, timestamp: 0 },
}

const client: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10_000,
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface Edge {
  id: string
  game: string
  type: string
  line: number
  edge_percentage: number
  confidence: number
  recommendation: string
  bookmaker: string
  timestamp: string
}

export interface BetPlacement {
  game_id: string
  market: string
  selection: string
  line: number
  odds: number
  stake: number
  bookmaker: string
}

export interface PlacedBet {
  id: string
  game_name: string
  market: string
  selection: string
  line: number
  odds: number
  stake: number
  potential_win: number
  potential_payout: number
  bookmaker: string
  status: string
  placed_at: string
  settled_at?: string | null
}

export interface PlaceBetResponse {
  success: boolean
  bet: PlacedBet
  message: string
}

export interface BetsSummary {
  total_bets: number
  pending: number
  won: number
  lost: number
  total_stake: number
  net_profit: number
  roi: number
}

export interface MyBetsResponse {
  bets: PlacedBet[]
  summary: BetsSummary
}

export interface CancelBetResponse {
  success: boolean
  message: string
}

function isCacheValid(record: CacheRecord<unknown>): boolean {
  return Boolean(record.value) && Date.now() - record.timestamp < CACHE_TTL_MS
}

export async function getWeeklyOdds(forceRefresh = false): Promise<WeeklyOddsResponse> {
  if (!forceRefresh && isCacheValid(cache.weeklyOdds)) {
    return cache.weeklyOdds.value as WeeklyOddsResponse
  }

  try {
    const response = await client.get('/api/odds/nfl-week')
    const payload: WeeklyOddsResponse = {
      data: Array.isArray(response.data?.data) ? response.data.data : [],
      source: response.data?.source,
      fetchedAt: new Date().toISOString(),
    }
    cache.weeklyOdds = { value: payload, timestamp: Date.now() }
    return payload
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const detail = error.response?.data?.detail ?? error.message
      throw new Error(`Failed to load weekly odds: ${detail}`)
    }
    throw new Error('Failed to load weekly odds: unexpected error')
  }
}

export async function getTokenStatus(forceRefresh = false): Promise<TokenStatus> {
  if (!forceRefresh && isCacheValid(cache.tokenStatus)) {
    return cache.tokenStatus.value as TokenStatus
  }

  try {
    const response = await client.get('/api/odds/token-status')
    const payload: TokenStatus = {
      ...response.data,
      refreshed_at: new Date().toISOString(),
    }
    cache.tokenStatus = { value: payload, timestamp: Date.now() }
    return payload
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const detail = error.response?.data?.detail ?? error.message
      throw new Error(`Failed to load token status: ${detail}`)
    }
    throw new Error('Failed to load token status: unexpected error')
  }
}

export function invalidateCache(): void {
  cache.weeklyOdds = { value: null, timestamp: 0 }
  cache.tokenStatus = { value: null, timestamp: 0 }
}

export async function placeBet(betData: BetPlacement): Promise<PlaceBetResponse> {
  try {
    const response = await client.post('/api/v1/bets/place', betData)
    return response.data
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const detail = error.response?.data?.detail ?? error.message
      throw new Error(`Failed to place bet: ${detail}`)
    }
    throw new Error('Failed to place bet: unexpected error')
  }
}

export async function getMyBets(): Promise<MyBetsResponse> {
  try {
    const response = await client.get('/api/v1/bets/my-bets')
    return response.data
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const detail = error.response?.data?.detail ?? error.message
      throw new Error(`Failed to fetch bets: ${detail}`)
    }
    throw new Error('Failed to fetch bets: unexpected error')
  }
}

export async function cancelBet(betId: string): Promise<CancelBetResponse> {
  try {
    const response = await client.delete(`/api/v1/bets/${betId}`)
    return response.data
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const detail = error.response?.data?.detail ?? error.message
      throw new Error(`Failed to cancel bet: ${detail}`)
    }
    throw new Error('Failed to cancel bet: unexpected error')
  }
}

export const api = {
  getWeeklyOdds,
  getTokenStatus,
  invalidateCache,
  placeBet,
  getMyBets,
  cancelBet,
}
