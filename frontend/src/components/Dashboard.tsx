import React, {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { AlertCircle, AlertTriangle, Loader2, TrendingUp } from "lucide-react";

import Skeleton from "./Skeleton";
import Toast from "./Toast";
import { BETA_DISCLAIMER, BETA_WARNING_TITLE } from "@/config/beta";
import { API_BASE_URL } from "@/config/api";

/**
 * Representation of a calculated edge exposed by the betting engine.
 * All numeric fields are normalized (0-1) and optional metadata keys are
 * flattened to keep rendering logic resilient to partial payloads.
 */
type Edge = {
  type: string;
  player: string;
  team: string;
  opponent?: string;
  confidence: number;
  expected_value: number;
  line?: string;
  odds?: string;
  reasoning?: string;
  notes?: string;
  metrics?: Record<string, unknown>;
};

/**
 * Snapshot returned by the `/api/edges/current` endpoint. It includes
 * the rendered edges plus summary and beta-mode metadata that gate the UI.
 */
type EdgeData = {
  edges: Edge[];
  data_quality: number;
  beta_mode: boolean;
  disclaimer: string;
  view_only: boolean;
  summary: {
    total_edges: number;
    avg_confidence: number;
    data_freshness: number;
    generated_at: string;
  };
};

type SortOption = "default" | "confidence" | "expected_value" | "alphabetical";

/** Endpoint that delivers the latest computed edges. */
const EDGES_ENDPOINT = `${API_BASE_URL}/api/edges/current`;
/** Frequency for background refreshes (five minutes). */
const REFRESH_MS = 5 * 60 * 1000;
/** Maximum retry attempts for network failures. */
const MAX_RETRIES = 3;
/** Backoff interval between retries; grows linearly with attempt count. */
const RETRY_DELAY_MS = 1_500;
/** Debounce window for the manual refresh button. */
const MANUAL_REFRESH_DEBOUNCE_MS = 1_500;

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

/**
 * Primary dashboard surface for reviewing model-generated betting edges.
 * The component handles polling the backend, surfacing beta-mode warnings,
 * and giving analysts tools (sorting, filtering, drill-ins) to validate edges
 * before acting. All state is local because the dashboard operates as a
 * self-contained snapshot view.
 */
export default function Dashboard(): JSX.Element {
  /** Latest payload returned by the edges API. */
  const [edgeData, setEdgeData] = useState<EdgeData | null>(null);
  /** Currently selected edge for the detail modal. */
  const [selectedEdge, setSelectedEdge] = useState<Edge | null>(null);
  /** Tracks initial load skeleton state. */
  const [loading, setLoading] = useState(true);
  /** Indicates in-flight background refresh without blocking the UI. */
  const [isRefreshing, setIsRefreshing] = useState(false);
  /** User-facing error string for API failures. */
  const [error, setError] = useState<string | null>(null);
  /** Machine-readable error details shown in beta mode. */
  const [errorDetails, setErrorDetails] = useState<string | null>(null);
  /** Active sort strategy for edges list. */
  const [sortOption, setSortOption] = useState<SortOption>("confidence");
  /** Active edge type filter derived from payload metadata. */
  const [typeFilter, setTypeFilter] = useState<string>("all");
  /** Active team filter derived from payload metadata. */
  const [teamFilter, setTeamFilter] = useState<string>("all");
  /** Search string applied to player/team fields. */
  const [searchTerm, setSearchTerm] = useState("");
  /** Timestamp of the most recent successful fetch for freshness labels. */
  const [lastRefreshedAt, setLastRefreshedAt] = useState<Date | null>(null);
  /** Lightweight toast messaging for incremental updates. */
  const [toast, setToast] = useState<{
    message: string;
    type: "info" | "success";
  } | null>(null);

  const edgeDataRef = useRef<EdgeData | null>(null);
  const manualRefreshRef = useRef<number>(0);

  /**
   * Fetch the latest edges from the API with bounded retries. During the initial
   * mount the function drives the skeleton UI; afterwards it performs soft refreshes
   * so analysts can keep context while new data arrives. Any errors surface
   * actionable messaging but keep the previous payload available.
   */
  const fetchEdges = useCallback(async () => {
    const isInitialLoad = edgeDataRef.current === null;
    if (isInitialLoad) {
      setLoading(true);
    } else {
      setIsRefreshing(true);
    }

    let lastError: Error | null = null;

    try {
      for (let attempt = 0; attempt < MAX_RETRIES; attempt += 1) {
        try {
          const response = await fetch(EDGES_ENDPOINT);
          if (!response.ok) {
            throw new Error(`Request failed with status ${response.status}`);
          }

          const data = (await response.json()) as EdgeData;
          const buildEdgeKey = (edge: Partial<Edge>) =>
            `${edge.type ?? "Unknown Edge"}-${edge.player ?? "Unknown Player"}-${edge.team ?? "Unknown Team"}`;
          const previousEdges = edgeDataRef.current?.edges ?? [];

          edgeDataRef.current = data;
          setEdgeData(data);
          setError(null);
          setErrorDetails(null);
          setLastRefreshedAt(new Date());

          if (!isInitialLoad) {
            const previousKeys = new Set(
              previousEdges.map((edge) => buildEdgeKey(edge)),
            );
            const currentKeys = new Set(
              data.edges.map((edge) => buildEdgeKey(edge)),
            );
            const newEdgesCount = data.edges.filter(
              (edge) => !previousKeys.has(buildEdgeKey(edge)),
            ).length;
            const removedEdgesCount = previousEdges.filter(
              (edge) => !currentKeys.has(buildEdgeKey(edge)),
            ).length;

            if (newEdgesCount > 0) {
              setToast({
                message: `${newEdgesCount} new edge${newEdgesCount === 1 ? "" : "s"} detected.`,
                type: "success",
              });
            } else if (removedEdgesCount > 0) {
              setToast({
                message: `${removedEdgesCount} edge${removedEdgesCount === 1 ? "" : "s"} removed from the list.`,
                type: "info",
              });
            }
          }

          return;
        } catch (err) {
          lastError =
            err instanceof Error
              ? err
              : new Error("Unknown error fetching edges");
          if (attempt < MAX_RETRIES - 1) {
            await delay(RETRY_DELAY_MS * (attempt + 1));
          }
        }
      }

      setError(
        "We could not reach the edges service. Confirm the backend is running and try again.",
      );
      setErrorDetails(lastError?.message ?? null);
    } finally {
      if (isInitialLoad) {
        setLoading(false);
      } else {
        setIsRefreshing(false);
      }
    }
  }, []);

  const handleManualRefresh = useCallback(
    (options?: { bypassDebounce?: boolean }) => {
      // Manual refresh uses a small debounce window so repeated clicks do not spam the API.
      const now = Date.now();
      if (!options?.bypassDebounce) {
        const elapsed = now - manualRefreshRef.current;
        if (elapsed < MANUAL_REFRESH_DEBOUNCE_MS) {
          return;
        }
      }

      manualRefreshRef.current = now;
      fetchEdges();
    },
    [fetchEdges],
  );

  useEffect(() => {
    // Start polling immediately on mount; keep refreshing in the background.
    fetchEdges();
    const interval = setInterval(fetchEdges, REFRESH_MS);
    return () => clearInterval(interval);
  }, [fetchEdges]);

  /** Maps confidence scores to Tailwind classes for quick glance status. */
  const getConfidenceTone = useCallback((confidence: number) => {
    if (confidence >= 0.8) return "text-green-600 bg-green-100";
    if (confidence >= 0.65) return "text-yellow-600 bg-yellow-100";
    return "text-red-600 bg-red-100";
  }, []);

  const qualityBadge = useMemo(() => {
    if (!edgeData) {
      return { label: "Unknown", color: "bg-gray-400", percent: "—" };
    }

    const quality = edgeData.data_quality;
    const percent = `${Math.round(quality * 100)}%`;

    if (quality >= 0.8)
      return { label: "Fresh", color: "bg-green-500", percent };
    if (quality >= 0.5)
      return { label: "Recent", color: "bg-yellow-500", percent };
    return { label: "Stale", color: "bg-red-500", percent };
  }, [edgeData]);

  const bannerTitle = BETA_WARNING_TITLE;
  const edges = edgeData?.edges ?? [];
  const summary = edgeData?.summary;
  // Beta metadata keeps the UI in view-only mode until the program graduates from beta.
  const betaMode = Boolean(edgeData?.beta_mode);
  const disclaimer = edgeData?.disclaimer;
  const viewOnly = Boolean(edgeData?.view_only);
  const effectiveDisclaimer = disclaimer || BETA_DISCLAIMER;
  const generatedLabel = summary?.generated_at
    ? new Date(summary.generated_at).toLocaleString()
    : "Unknown";

  const edgeTypes = useMemo(() => {
    const types = new Set<string>();
    edges.forEach((edge) => {
      types.add(edge.type || "Unknown Edge");
    });
    return Array.from(types).sort((a, b) => a.localeCompare(b));
  }, [edges]);

  const teams = useMemo(() => {
    const uniqueTeams = new Set<string>();
    edges.forEach((edge) => {
      if (edge.team) {
        uniqueTeams.add(edge.team);
      }
    });
    return Array.from(uniqueTeams).sort((a, b) => a.localeCompare(b));
  }, [edges]);

  const sortedEdges = useMemo(() => {
    const coerceNumber = (value: unknown): number =>
      typeof value === "number" && Number.isFinite(value) ? value : 0;
    const searchValue = searchTerm.trim().toLowerCase();

    const filtered = edges.filter((edge) => {
      const matchesType =
        typeFilter === "all" || (edge.type || "Unknown Edge") === typeFilter;
      const matchesTeam =
        teamFilter === "all" || (edge.team || "Unknown Team") === teamFilter;
      const matchesSearch =
        searchValue.length === 0 ||
        [edge.player, edge.team, edge.type]
          .filter(Boolean)
          .some((value) => String(value).toLowerCase().includes(searchValue));

      return matchesType && matchesTeam && matchesSearch;
    });

    if (sortOption === "default") {
      return filtered;
    }

    const edgesCopy = filtered.slice();
    switch (sortOption) {
      case "confidence":
        edgesCopy.sort(
          (a, b) => coerceNumber(b.confidence) - coerceNumber(a.confidence),
        );
        break;
      case "expected_value":
        edgesCopy.sort(
          (a, b) =>
            coerceNumber(b.expected_value) - coerceNumber(a.expected_value),
        );
        break;
      case "alphabetical":
        edgesCopy.sort((a, b) =>
          (a.player || "").localeCompare(b.player || ""),
        );
        break;
      default:
        break;
    }

    return edgesCopy;
  }, [edges, sortOption, typeFilter, teamFilter, searchTerm]);

  const visibleEdgeCount = sortedEdges.length;
  const totalEdgeCount = summary?.total_edges ?? edges.length;
  const hasEdges = visibleEdgeCount > 0;
  const lastRefreshedLabel = lastRefreshedAt
    ? lastRefreshedAt.toLocaleTimeString()
    : "—";

  const resetFilters = useCallback(() => {
    setSortOption("confidence");
    setTypeFilter("all");
    setTeamFilter("all");
    setSearchTerm("");
  }, []);

  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState === "visible") {
        handleManualRefresh({ bypassDebounce: true });
      }
    };

    document.addEventListener("visibilitychange", handleVisibilityChange);
    return () =>
      document.removeEventListener("visibilitychange", handleVisibilityChange);
  }, [handleManualRefresh]);

  if (loading && edges.length === 0) {
    return (
      <div className="p-6 max-w-7xl mx-auto space-y-6" aria-busy="true">
        <div className="space-y-3">
          <div className="h-6 w-48 rounded bg-gray-200 animate-pulse" />
          <div className="h-4 w-72 rounded bg-gray-200 animate-pulse" />
        </div>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, index) => (
            <div
              key={`summary-skeleton-${index}`}
              className="bg-white p-4 rounded-lg shadow"
            >
              <Skeleton rows={2} />
            </div>
          ))}
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, index) => (
            <div
              key={`edge-skeleton-${index}`}
              className="bg-white p-4 rounded-lg shadow border border-gray-100"
            >
              <Skeleton rows={4} />
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error && edges.length === 0) {
    return (
      <div className="p-6 max-w-xl mx-auto">
        <div
          className="rounded-lg border border-red-200 bg-red-50 p-6 space-y-4"
          role="alert"
          aria-live="assertive"
        >
          <div className="flex items-start gap-3">
            <AlertCircle className="h-6 w-6 text-red-600 mt-0.5" aria-hidden />
            <div>
              <p className="text-lg font-semibold text-red-800">
                Cannot reach the edges service
              </p>
              <p className="text-sm text-red-700">
                Make sure the Docker stack is running on ports 5173 and 8000,
                then retry.
              </p>
              {errorDetails && (
                <p className="mt-2 text-xs text-red-600">
                  Details: {errorDetails}
                </p>
              )}
            </div>
          </div>
          <button
            type="button"
            onClick={() => handleManualRefresh({ bypassDebounce: true })}
            className="inline-flex items-center justify-center rounded bg-red-600 px-3 py-2 text-sm font-medium text-white transition hover:bg-red-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!edgeData && !loading && !error) {
    return <div className="p-4">No data available</div>;
  }

  if (loading && edges.length === 0) {
    return (
      <div className="p-6 max-w-7xl mx-auto space-y-6" aria-busy="true">
        <div className="space-y-3">
          <div className="h-6 w-48 rounded bg-gray-200 animate-pulse" />
          <div className="h-4 w-72 rounded bg-gray-200 animate-pulse" />
        </div>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, index) => (
            <div
              key={`summary-skeleton-${index}`}
              className="bg-white p-4 rounded-lg shadow"
            >
              <Skeleton rows={2} />
            </div>
          ))}
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, index) => (
            <div
              key={`edge-skeleton-${index}`}
              className="bg-white p-4 rounded-lg shadow border border-gray-100"
            >
              <Skeleton rows={4} />
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error && edges.length === 0) {
    return (
      <div className="p-6 max-w-xl mx-auto">
        <div
          className="rounded-lg border border-red-200 bg-red-50 p-6 space-y-4"
          role="alert"
          aria-live="assertive"
        >
          <div className="flex items-start gap-3">
            <AlertCircle className="h-6 w-6 text-red-600 mt-0.5" aria-hidden />
            <div>
              <p className="text-lg font-semibold text-red-800">
                Cannot reach the edges service
              </p>
              <p className="text-sm text-red-700">
                Make sure the Docker stack is running on ports 5173 and 8000,
                then retry.
              </p>
              {errorDetails && (
                <p className="mt-2 text-xs text-red-600">
                  Details: {errorDetails}
                </p>
              )}
            </div>
          </div>
          <button
            type="button"
            onClick={() => handleManualRefresh({ bypassDebounce: true })}
            className="inline-flex items-center justify-center rounded bg-red-600 px-3 py-2 text-sm font-medium text-white transition hover:bg-red-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!edgeData && !loading && !error) {
    return <div className="p-4">No data available</div>;
  }

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {error && (
        <div
          role="alert"
          className="flex items-start gap-3 rounded-lg border border-red-200 bg-red-50 p-4"
        >
          <AlertCircle className="h-5 w-5 text-red-600 mt-0.5" aria-hidden />
          <div className="flex-1">
            <p className="font-semibold text-red-800">
              Live data refresh failed.
            </p>
            <p className="text-sm text-red-700">
              Showing the last successful snapshot. Retry when ready.
            </p>
            {errorDetails && (
              <p className="mt-1 text-xs text-red-600">
                Details: {errorDetails}
              </p>
            )}
          </div>
          <button
            type="button"
            onClick={() => handleManualRefresh({ bypassDebounce: true })}
            className="rounded bg-red-600 px-3 py-1 text-sm font-medium text-white transition hover:bg-red-700"
          >
            Retry
          </button>
        </div>
      )}

      {betaMode && (
        <div
          role="alert"
          aria-live="assertive"
          className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg flex items-start gap-3"
        >
          <AlertTriangle
            className="h-5 w-5 text-yellow-600 mt-0.5"
            aria-hidden
          />
          <div>
            <p className="font-semibold text-yellow-800">{bannerTitle}</p>
            <p className="text-sm text-yellow-700">{effectiveDisclaimer}</p>
          </div>
        </div>
      )}

      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-bold">Current Edges</h1>
          <p className="text-sm text-gray-600">
            Automated discovery — manual verification required before betting.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-600">Data Quality:</span>
            <span
              className={`px-2 py-1 rounded text-white text-xs ${qualityBadge.color}`}
            >
              {qualityBadge.label} ({qualityBadge.percent})
            </span>
          </div>
          <button
            type="button"
            onClick={() => handleManualRefresh()}
            disabled={loading || isRefreshing}
            className="inline-flex items-center gap-2 rounded bg-blue-500 px-3 py-1 text-sm font-medium text-white transition hover:bg-blue-600 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isRefreshing ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
                Refreshing…
              </>
            ) : (
              "Refresh"
            )}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
        <div className="bg-white p-4 rounded-lg shadow">
          <p className="text-sm text-gray-600">Total Edges</p>
          <p className="text-2xl font-bold">{summary?.total_edges ?? 0}</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <p className="text-sm text-gray-600">Avg Confidence</p>
          <p className="text-2xl font-bold">
            {((summary?.avg_confidence ?? 0) * 100).toFixed(1)}%
          </p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <p className="text-sm text-gray-600">Data Freshness</p>
          <p className="text-2xl font-bold">
            {((summary?.data_freshness ?? 0) * 100).toFixed(0)}%
          </p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <p className="text-sm text-gray-600">Generated</p>
          <p className="text-sm font-semibold">{generatedLabel}</p>
        </div>
      </div>

      <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
        <div className="flex flex-wrap items-center gap-3">
          <label className="flex items-center gap-2 text-sm text-gray-600">
            Sort by
            <select
              value={sortOption}
              onChange={(event) =>
                setSortOption(event.target.value as SortOption)
              }
              className="rounded border border-gray-300 bg-white px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="default">Default order</option>
              <option value="confidence">Confidence (high → low)</option>
              <option value="expected_value">
                Expected Value (high → low)
              </option>
              <option value="alphabetical">Player (A → Z)</option>
            </select>
          </label>

          <label className="flex items-center gap-2 text-sm text-gray-600">
            Edge type
            <select
              value={typeFilter}
              onChange={(event) => setTypeFilter(event.target.value)}
              className="rounded border border-gray-300 bg-white px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All edge types</option>
              {edgeTypes.map((type) => (
                <option key={type} value={type}>
                  {type}
                </option>
              ))}
            </select>
          </label>

          <label className="flex items-center gap-2 text-sm text-gray-600">
            Team
            <select
              value={teamFilter}
              onChange={(event) => setTeamFilter(event.target.value)}
              className="rounded border border-gray-300 bg-white px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All teams</option>
              {teams.map((team) => (
                <option key={team} value={team}>
                  {team}
                </option>
              ))}
            </select>
          </label>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <input
            type="search"
            value={searchTerm}
            onChange={(event) => setSearchTerm(event.target.value)}
            placeholder="Search players or teams"
            className="w-full rounded border border-gray-300 px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 md:w-64"
          />
          <button
            type="button"
            onClick={resetFilters}
            className="text-sm font-medium text-blue-600 hover:underline"
          >
            Reset filters
          </button>
          <div className="flex flex-col text-xs text-gray-500">
            <span>
              Showing {visibleEdgeCount} of {totalEdgeCount} edges
            </span>
            <span>Last refreshed at {lastRefreshedLabel}</span>
          </div>
        </div>
      </div>

      {hasEdges ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {sortedEdges.map((edge, index) => {
            const playerName = edge.player || "Unknown Player";
            const teamName = edge.team || "Unknown Team";
            const opponentName = edge.opponent ? ` vs ${edge.opponent}` : "";
            const confidenceValue = Number.isFinite(edge.confidence)
              ? edge.confidence
              : 0;
            const expectedValue = Number.isFinite(edge.expected_value)
              ? edge.expected_value
              : 0;

            return (
              <button
                type="button"
                key={`${playerName}-${index}`}
                className="text-left bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow"
                onClick={() => setSelectedEdge(edge)}
              >
                <div className="flex justify-between items-start mb-2">
                  <span className="text-xs font-semibold text-gray-500 uppercase">
                    {edge.type}
                  </span>
                  <TrendingUp className="h-4 w-4 text-green-500" aria-hidden />
                </div>

                <h3 className="font-bold text-lg mb-1">{playerName}</h3>
                <p className="text-sm text-gray-600 mb-3">
                  {teamName}
                  {opponentName}
                </p>

                <div className="flex justify-between items-center">
                  <div className="flex items-center gap-2">
                    <span
                      className={`px-2 py-1 rounded text-xs font-semibold ${getConfidenceTone(confidenceValue)}`}
                    >
                      {(confidenceValue * 100).toFixed(0)}% conf
                    </span>
                    <span className="text-xs text-gray-600">
                      EV: {(expectedValue * 100).toFixed(1)}%
                    </span>
                  </div>
                  {viewOnly && (
                    <span className="text-xs text-gray-400">View Only</span>
                  )}
                </div>

                {edge.reasoning && (
                  <p className="mt-2 text-xs text-gray-500">{edge.reasoning}</p>
                )}
              </button>
            );
          })}
        </div>
      ) : (
        <div className="rounded-lg border border-dashed border-gray-300 bg-white p-6 text-sm text-gray-600">
          No active edges are available right now. The feed will refresh
          automatically when new edges appear.
        </div>
      )}

      {selectedEdge && (
        <div
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
          onClick={() => setSelectedEdge(null)}
        >
          <div
            className="bg-white rounded-lg p-6 max-w-md w-full"
            onClick={(event) => event.stopPropagation()}
          >
            <h2 className="text-xl font-bold mb-4">{selectedEdge.player}</h2>
            <div className="space-y-2">
              <p>
                <span className="font-semibold">Type:</span> {selectedEdge.type}
              </p>
              <p>
                <span className="font-semibold">Matchup:</span>{" "}
                {selectedEdge.team}
                {selectedEdge.opponent ? ` vs ${selectedEdge.opponent}` : ""}
              </p>
              <p>
                <span className="font-semibold">Confidence:</span>{" "}
                {(selectedEdge.confidence * 100).toFixed(1)}%
              </p>
              <p>
                <span className="font-semibold">Expected Value:</span>{" "}
                {(selectedEdge.expected_value * 100).toFixed(2)}%
              </p>
              {selectedEdge.line && (
                <p>
                  <span className="font-semibold">Line:</span>{" "}
                  {selectedEdge.line}
                </p>
              )}
              {selectedEdge.odds && (
                <p>
                  <span className="font-semibold">Odds:</span>{" "}
                  {selectedEdge.odds}
                </p>
              )}
              {selectedEdge.reasoning && (
                <p>
                  <span className="font-semibold">Analysis:</span>{" "}
                  {selectedEdge.reasoning}
                </p>
              )}
              {selectedEdge.notes && (
                <p>
                  <span className="font-semibold">Notes:</span>{" "}
                  {selectedEdge.notes}
                </p>
              )}
            </div>

            {selectedEdge.metrics && (
              <div className="mt-4 border-t border-gray-200 pt-4">
                <p className="font-semibold text-sm text-gray-700">
                  Key Metrics
                </p>
                <ul className="mt-2 space-y-1 text-sm text-gray-600">
                  {Object.entries(selectedEdge.metrics).map(
                    ([metricKey, metricValue]) => {
                      if (metricValue && typeof metricValue === "object") {
                        if (loading && edges.length === 0) {
                          return (
                            <div
                              className="p-6 max-w-7xl mx-auto space-y-6"
                              aria-busy="true"
                            >
                              <div className="space-y-3">
                                <div className="h-6 w-48 rounded bg-gray-200 animate-pulse" />
                                <div className="h-4 w-72 rounded bg-gray-200 animate-pulse" />
                              </div>
                              <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
                                {Array.from({ length: 4 }).map((_, index) => (
                                  <div
                                    key={`summary-skeleton-${index}`}
                                    className="bg-white p-4 rounded-lg shadow"
                                  >
                                    <Skeleton rows={2} />
                                  </div>
                                ))}
                              </div>
                              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                                {Array.from({ length: 6 }).map((_, index) => (
                                  <div
                                    key={`edge-skeleton-${index}`}
                                    className="bg-white p-4 rounded-lg shadow border border-gray-100"
                                  >
                                    <Skeleton rows={4} />
                                  </div>
                                ))}
                              </div>
                            </div>
                          );
                        }

                        if (error && edges.length === 0) {
                          return (
                            <div className="p-6 max-w-xl mx-auto">
                              <div
                                className="rounded-lg border border-red-200 bg-red-50 p-6 space-y-4"
                                role="alert"
                                aria-live="assertive"
                              >
                                <div className="flex items-start gap-3">
                                  <AlertCircle
                                    className="h-6 w-6 text-red-600 mt-0.5"
                                    aria-hidden
                                  />
                                  <div>
                                    <p className="text-lg font-semibold text-red-800">
                                      Cannot reach the edges service
                                    </p>
                                    <p className="text-sm text-red-700">
                                      Make sure the Docker stack is running on
                                      ports 5173 and 8000, then retry.
                                    </p>
                                    {errorDetails && (
                                      <p className="mt-2 text-xs text-red-600">
                                        Details: {errorDetails}
                                      </p>
                                    )}
                                  </div>
                                </div>
                                <button
                                  type="button"
                                  onClick={() =>
                                    handleManualRefresh({
                                      bypassDebounce: true,
                                    })
                                  }
                                  className="inline-flex items-center justify-center rounded bg-red-600 px-3 py-2 text-sm font-medium text-white transition hover:bg-red-700"
                                >
                                  Retry
                                </button>
                              </div>
                            </div>
                          );
                        }

                        if (!edgeData && !loading && !error) {
                          return <div className="p-4">No data available</div>;
                        }

                        return (
                          <li key={metricKey} className="text-sm text-gray-600">
                            <span className="font-semibold capitalize">
                              {metricKey}:
                            </span>
                            <ul className="ml-4 list-disc text-xs text-gray-500">
                              {Object.entries(
                                metricValue as Record<string, unknown>,
                              ).map(([nestedKey, nestedValue]) => (
                                <li key={`${metricKey}-${nestedKey}`}>
                                  {nestedKey}: {String(nestedValue)}
                                </li>
                              ))}
                            </ul>
                          </li>
                        );
                      }

                      if (loading && edges.length === 0) {
                        return (
                          <div
                            className="p-6 max-w-7xl mx-auto space-y-6"
                            aria-busy="true"
                          >
                            <div className="space-y-3">
                              <div className="h-6 w-48 rounded bg-gray-200 animate-pulse" />
                              <div className="h-4 w-72 rounded bg-gray-200 animate-pulse" />
                            </div>
                            <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
                              {Array.from({ length: 4 }).map((_, index) => (
                                <div
                                  key={`summary-skeleton-${index}`}
                                  className="bg-white p-4 rounded-lg shadow"
                                >
                                  <Skeleton rows={2} />
                                </div>
                              ))}
                            </div>
                            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                              {Array.from({ length: 6 }).map((_, index) => (
                                <div
                                  key={`edge-skeleton-${index}`}
                                  className="bg-white p-4 rounded-lg shadow border border-gray-100"
                                >
                                  <Skeleton rows={4} />
                                </div>
                              ))}
                            </div>
                          </div>
                        );
                      }

                      if (error && edges.length === 0) {
                        return (
                          <div className="p-6 max-w-xl mx-auto">
                            <div
                              className="rounded-lg border border-red-200 bg-red-50 p-6 space-y-4"
                              role="alert"
                              aria-live="assertive"
                            >
                              <div className="flex items-start gap-3">
                                <AlertCircle
                                  className="h-6 w-6 text-red-600 mt-0.5"
                                  aria-hidden
                                />
                                <div>
                                  <p className="text-lg font-semibold text-red-800">
                                    Cannot reach the edges service
                                  </p>
                                  <p className="text-sm text-red-700">
                                    Make sure the Docker stack is running on
                                    ports 5173 and 8000, then retry.
                                  </p>
                                  {errorDetails && (
                                    <p className="mt-2 text-xs text-red-600">
                                      Details: {errorDetails}
                                    </p>
                                  )}
                                </div>
                              </div>
                              <button
                                type="button"
                                onClick={() =>
                                  handleManualRefresh({ bypassDebounce: true })
                                }
                                className="inline-flex items-center justify-center rounded bg-red-600 px-3 py-2 text-sm font-medium text-white transition hover:bg-red-700"
                              >
                                Retry
                              </button>
                            </div>
                          </div>
                        );
                      }

                      if (!edgeData && !loading && !error) {
                        return <div className="p-4">No data available</div>;
                      }

                      return (
                        <li key={metricKey}>
                          <span className="font-semibold capitalize">
                            {metricKey}:
                          </span>{" "}
                          {String(metricValue)}
                        </li>
                      );
                    },
                  )}
                </ul>
              </div>
            )}

            <div className="mt-6 p-3 bg-yellow-50 rounded">
              <p className="text-sm text-yellow-800 flex items-center gap-2">
                <AlertCircle className="h-4 w-4" aria-hidden />
                Beta mode - Manual verification required before betting
              </p>
            </div>

            <button
              type="button"
              onClick={() => setSelectedEdge(null)}
              className="mt-4 w-full py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
            >
              Close
            </button>
          </div>
        </div>
      )}
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}
    </div>
  );
}
