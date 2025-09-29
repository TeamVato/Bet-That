export type ConfidenceLevel = "low" | "medium" | "high";
export type EdgeStatus = "edge" | "monitor" | "no-action";

export interface MarketLine {
  bookmaker: string;
  price: number;
  point?: number | null;
}

export interface LineSnapshot {
  book: string;
  point: number;
  price?: number | null;
}

export interface GameOdds {
  id: string;
  home_team: string;
  away_team: string;
  commence_time: string;
  last_updated?: string;
  best_spreads?: Record<string, MarketLine>;
  best_totals?: Record<string, MarketLine>;
  totals_points?: LineSnapshot[];
  spreads_points?: LineSnapshot[];
  totals_movement?: number;
  spreads_movement?: number;
  average_total?: number | null;
  key_numbers?: number[];
  on_key_number?: boolean;
  recommendation?: string;
  confidence?: string;
  source?: string;
}

export interface EdgeSummary {
  gameId: string;
  matchup: string;
  kickoff: string;
  movement: number;
  averageTotal?: number | null;
  keyNumbers: number[];
  highestTotal?: LineSnapshot;
  lowestTotal?: LineSnapshot;
  recommendation: string;
  confidence: ConfidenceLevel;
  status: EdgeStatus;
  source?: string;
}

export interface TokenStatus {
  daily_limit: number;
  requests_made: number;
  requests_remaining: number;
  keys_configured?: number;
  key_usage_snapshot?: Record<string, number>;
  blocked_keys?: Record<string, string>;
  refreshed_at?: string;
}

export interface WeeklyOddsResponse {
  data: GameOdds[];
  source?: string;
  fetchedAt: string;
}
