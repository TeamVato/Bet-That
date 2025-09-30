import { useState, useEffect } from "react";
import { 
  api, 
  ResolutionAnalytics, 
  ResolutionHistoryFilters, 
  ResolutionHistoryResponse 
} from "@/services/api";

export function useResolutionAnalytics() {
  const [analytics, setAnalytics] = useState<ResolutionAnalytics | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchAnalytics = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await api.getResolutionAnalytics();
      setAnalytics(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch analytics");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  return {
    analytics,
    isLoading,
    error,
    refetch: fetchAnalytics,
  };
}

export function useResolutionHistory(filters: ResolutionHistoryFilters = {}) {
  const [history, setHistory] = useState<ResolutionHistoryResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchHistory = async (newFilters?: ResolutionHistoryFilters) => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await api.getResolutionHistory(newFilters || filters);
      setHistory(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch history");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [JSON.stringify(filters)]);

  const exportData = async (format: "csv" | "json" = "csv") => {
    try {
      const blob = await api.exportResolutionData(filters, format);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `resolution-data.${format}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      throw new Error(err instanceof Error ? err.message : "Failed to export data");
    }
  };

  return {
    history,
    isLoading,
    error,
    refetch: fetchHistory,
    exportData,
  };
}

