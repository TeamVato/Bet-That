import axios, { AxiosInstance } from "axios";
import type { WeeklyOddsResponse, TokenStatus } from "@/types";
import { BETA_VIEW_ONLY } from "@/config/beta";
import { API_BASE_URL } from "@/config/api";
const CACHE_TTL_MS = 4 * 60 * 1000; // 4 minutes keeps us under the 5 minute refresh cadence

type CacheRecord<T> = {
  value: T | null;
  timestamp: number;
};

const cache: {
  weeklyOdds: CacheRecord<WeeklyOddsResponse>;
  tokenStatus: CacheRecord<TokenStatus>;
} = {
  weeklyOdds: { value: null, timestamp: 0 },
  tokenStatus: { value: null, timestamp: 0 },
};

const client: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10_000,
  headers: {
    "Content-Type": "application/json",
  },
});

export interface Edge {
  id: string;
  game: string;
  type: string;
  line: number;
  edge_percentage: number;
  confidence: number;
  recommendation: string;
  bookmaker: string;
  timestamp: string;
}

export interface BetPlacement {
  game_id: string;
  market: string;
  selection: string;
  line: number;
  odds: number;
  stake: number;
  bookmaker: string;
}

export interface PlacedBet {
  id: string;
  game_name: string;
  market: string;
  selection: string;
  line: number;
  odds: number;
  stake: number;
  potential_win: number;
  potential_payout: number;
  bookmaker: string;
  status: string;
  placed_at: string;
  settled_at?: string | null;
}

export interface PlaceBetResponse {
  success: boolean;
  bet: PlacedBet;
  message: string;
}

export interface BetsSummary {
  total_bets: number;
  pending: number;
  won: number;
  lost: number;
  total_stake: number;
  net_profit: number;
  roi: number;
}

export interface MyBetsResponse {
  bets: PlacedBet[];
  summary: BetsSummary;
}

export interface CancelBetResponse {
  success: boolean;
  message: string;
}

function isCacheValid(record: CacheRecord<unknown>): boolean {
  return Boolean(record.value) && Date.now() - record.timestamp < CACHE_TTL_MS;
}

export async function getWeeklyOdds(
  forceRefresh = false,
): Promise<WeeklyOddsResponse> {
  if (!forceRefresh && isCacheValid(cache.weeklyOdds)) {
    return cache.weeklyOdds.value as WeeklyOddsResponse;
  }

  try {
    const response = await client.get("/api/odds/nfl-week");
    const payload: WeeklyOddsResponse = {
      data: Array.isArray(response.data?.data) ? response.data.data : [],
      source: response.data?.source,
      fetchedAt: new Date().toISOString(),
    };
    cache.weeklyOdds = { value: payload, timestamp: Date.now() };
    return payload;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const detail = error.response?.data?.detail ?? error.message;
      throw new Error(`Failed to load weekly odds: ${detail}`);
    }
    throw new Error("Failed to load weekly odds: unexpected error");
  }
}

export async function getTokenStatus(
  forceRefresh = false,
): Promise<TokenStatus> {
  if (!forceRefresh && isCacheValid(cache.tokenStatus)) {
    return cache.tokenStatus.value as TokenStatus;
  }

  try {
    const response = await client.get("/api/odds/token-status");
    const payload: TokenStatus = {
      ...response.data,
      refreshed_at: new Date().toISOString(),
    };
    cache.tokenStatus = { value: payload, timestamp: Date.now() };
    return payload;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const detail = error.response?.data?.detail ?? error.message;
      throw new Error(`Failed to load token status: ${detail}`);
    }
    throw new Error("Failed to load token status: unexpected error");
  }
}

export function invalidateCache(): void {
  cache.weeklyOdds = { value: null, timestamp: 0 };
  cache.tokenStatus = { value: null, timestamp: 0 };
}

export async function placeBet(
  betData: BetPlacement,
): Promise<PlaceBetResponse> {
  if (BETA_VIEW_ONLY) {
    throw new Error("Bet placement is disabled in beta view-only mode.");
  }

  try {
    const response = await client.post("/api/v1/bets/place", betData);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const detail = error.response?.data?.detail ?? error.message;
      throw new Error(`Failed to place bet: ${detail}`);
    }
    throw new Error("Failed to place bet: unexpected error");
  }
}

export async function getMyBets(): Promise<MyBetsResponse> {
  try {
    const response = await client.get("/api/v1/bets/my-bets");
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const detail = error.response?.data?.detail ?? error.message;
      throw new Error(`Failed to fetch bets: ${detail}`);
    }
    throw new Error("Failed to fetch bets: unexpected error");
  }
}

export async function cancelBet(betId: string): Promise<CancelBetResponse> {
  try {
    const response = await client.delete(`/api/v1/bets/${betId}`);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const detail = error.response?.data?.detail ?? error.message;
      throw new Error(`Failed to cancel bet: ${detail}`);
    }
    throw new Error("Failed to cancel bet: unexpected error");
  }
}

export interface BetResolveRequest {
  result: "win" | "loss" | "push" | "void";
  resolution_notes?: string;
  resolution_source?: string;
}

export interface BetDisputeRequest {
  dispute_reason: string;
}

export interface BetResolutionHistory {
  id: number;
  bet_id: number;
  action_type: string;
  previous_status?: string;
  new_status?: string;
  previous_result?: string;
  new_result?: string;
  resolution_notes?: string;
  resolution_source?: string;
  dispute_reason?: string;
  performed_by: number;
  created_at: string;
}

export interface BetResolutionHistoryResponse {
  history: BetResolutionHistory[];
  total: number;
  page: number;
  per_page: number;
}

export async function resolveBet(betId: string, request: BetResolveRequest): Promise<PlacedBet> {
  try {
    const response = await client.post(`/api/v1/bets/${betId}/resolve`, request);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const detail = error.response?.data?.detail ?? error.message;
      throw new Error(`Failed to resolve bet: ${detail}`);
    }
    throw new Error("Failed to resolve bet: unexpected error");
  }
}

export async function disputeBet(betId: string, request: BetDisputeRequest): Promise<PlacedBet> {
  try {
    const response = await client.post(`/api/v1/bets/${betId}/dispute`, request);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const detail = error.response?.data?.detail ?? error.message;
      throw new Error(`Failed to dispute bet: ${detail}`);
    }
    throw new Error("Failed to dispute bet: unexpected error");
  }
}

export async function getBetResolutionHistory(
  betId: string,
  page: number = 1,
  perPage: number = 10
): Promise<BetResolutionHistoryResponse> {
  try {
    const response = await client.get(
      `/api/v1/bets/${betId}/resolution-history?page=${page}&per_page=${perPage}`
    );
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const detail = error.response?.data?.detail ?? error.message;
      throw new Error(`Failed to fetch resolution history: ${detail}`);
    }
    throw new Error("Failed to fetch resolution history: unexpected error");
  }
}

export async function getPendingResolutionBets(
  page: number = 1,
  perPage: number = 20
): Promise<MyBetsResponse> {
  try {
    const response = await client.get(
      `/api/v1/bets/pending-resolution?page=${page}&per_page=${perPage}`
    );
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const detail = error.response?.data?.detail ?? error.message;
      throw new Error(`Failed to fetch pending bets: ${detail}`);
    }
    throw new Error("Failed to fetch pending bets: unexpected error");
  }
}

export async function resolveDispute(
  betId: string,
  result: "win" | "loss" | "push" | "void",
  resolutionNotes?: string
): Promise<PlacedBet> {
  try {
    const response = await client.put(`/api/v1/bets/${betId}/resolve-dispute`, {
      result,
      resolution_notes: resolutionNotes,
    });
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const detail = error.response?.data?.detail ?? error.message;
      throw new Error(`Failed to resolve dispute: ${detail}`);
    }
    throw new Error("Failed to resolve dispute: unexpected error");
  }
}

// Analytics interfaces
export interface ResolutionAnalytics {
  total_resolutions: number;
  average_resolution_time_hours: number;
  resolution_accuracy_percentage: number;
  outcome_distribution: {
    win: number;
    loss: number;
    push: number;
    void: number;
  };
  most_active_resolvers: Array<{
    user_id: number;
    user_name: string;
    resolution_count: number;
  }>;
  resolution_trends: Array<{
    date: string;
    resolutions_count: number;
    average_time_hours: number;
  }>;
  dispute_rate: number;
  average_dispute_resolution_time_hours: number;
}

export interface ResolutionHistoryFilters {
  start_date?: string;
  end_date?: string;
  result?: string;
  resolver_id?: number;
  has_dispute?: boolean;
  page?: number;
  per_page?: number;
}

export interface ResolutionHistoryItem {
  id: number;
  bet_id: number;
  game_name: string;
  market: string;
  selection: string;
  result: string;
  resolved_at: string;
  resolved_by: number;
  resolver_name: string;
  resolution_notes?: string;
  is_disputed: boolean;
  dispute_reason?: string;
  dispute_resolved_at?: string;
  resolution_time_hours: number;
}

export interface ResolutionHistoryResponse {
  history: ResolutionHistoryItem[];
  total: number;
  page: number;
  per_page: number;
}

export async function getResolutionAnalytics(): Promise<ResolutionAnalytics> {
  try {
    const response = await client.get("/api/v1/analytics/resolution");
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const detail = error.response?.data?.detail ?? error.message;
      throw new Error(`Failed to fetch resolution analytics: ${detail}`);
    }
    throw new Error("Failed to fetch resolution analytics: unexpected error");
  }
}

export async function getResolutionHistory(
  filters: ResolutionHistoryFilters = {}
): Promise<ResolutionHistoryResponse> {
  try {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        params.append(key, value.toString());
      }
    });
    
    const response = await client.get(`/api/v1/analytics/resolution-history?${params}`);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const detail = error.response?.data?.detail ?? error.message;
      throw new Error(`Failed to fetch resolution history: ${detail}`);
    }
    throw new Error("Failed to fetch resolution history: unexpected error");
  }
}

export async function exportResolutionData(
  filters: ResolutionHistoryFilters = {},
  format: "csv" | "json" = "csv"
): Promise<Blob> {
  try {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        params.append(key, value.toString());
      }
    });
    params.append("format", format);
    
    const response = await client.get(`/api/v1/analytics/export-resolution-data?${params}`, {
      responseType: "blob",
    });
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const detail = error.response?.data?.detail ?? error.message;
      throw new Error(`Failed to export resolution data: ${detail}`);
    }
    throw new Error("Failed to export resolution data: unexpected error");
  }
}

export const api = {
  getWeeklyOdds,
  getTokenStatus,
  invalidateCache,
  placeBet,
  getMyBets,
  cancelBet,
  resolveBet,
  disputeBet,
  getBetResolutionHistory,
  getPendingResolutionBets,
  resolveDispute,
  getResolutionAnalytics,
  getResolutionHistory,
  exportResolutionData,
};
