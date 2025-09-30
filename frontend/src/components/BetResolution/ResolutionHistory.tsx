import React, { useState, useEffect } from "react";
import { Clock, User, FileText, AlertTriangle, CheckCircle } from "lucide-react";
import { useBetResolution, BetResolutionHistory } from "@/hooks/useBetResolution";

interface ResolutionHistoryProps {
  betId: string;
}

export const ResolutionHistory: React.FC<ResolutionHistoryProps> = ({
  betId,
}) => {
  const [history, setHistory] = useState<BetResolutionHistory[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(false);

  const { getResolutionHistory, isLoadingHistory } = useBetResolution();

  const loadHistory = async (pageNum: number = 1) => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await getResolutionHistory(betId, pageNum, 10);
      setHistory(response.history);
      setHasMore(response.history.length === 10);
      setPage(pageNum);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load history");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadHistory(1);
  }, [betId]);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const getActionIcon = (actionType: string) => {
    switch (actionType) {
      case "resolve":
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case "dispute":
        return <AlertTriangle className="h-4 w-4 text-yellow-600" />;
      case "dispute_resolve":
        return <CheckCircle className="h-4 w-4 text-blue-600" />;
      default:
        return <FileText className="h-4 w-4 text-gray-600" />;
    }
  };

  const getActionColor = (actionType: string) => {
    switch (actionType) {
      case "resolve":
        return "bg-green-50 border-green-200";
      case "dispute":
        return "bg-yellow-50 border-yellow-200";
      case "dispute_resolve":
        return "bg-blue-50 border-blue-200";
      default:
        return "bg-gray-50 border-gray-200";
    }
  };

  const getResultBadge = (result: string) => {
    const colors = {
      win: "bg-green-100 text-green-800",
      loss: "bg-red-100 text-red-800",
      push: "bg-yellow-100 text-yellow-800",
      void: "bg-gray-100 text-gray-800",
    };

    return (
      <span
        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
          colors[result as keyof typeof colors] || "bg-gray-100 text-gray-800"
        }`}
      >
        {result}
      </span>
    );
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        <h3 className="text-lg font-medium text-gray-900">Resolution History</h3>
        <div className="space-y-3">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="animate-pulse">
              <div className="bg-gray-200 h-20 rounded-lg"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-4">
        <h3 className="text-lg font-medium text-gray-900">Resolution History</h3>
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-600">{error}</p>
          <button
            onClick={() => loadHistory(1)}
            className="mt-2 text-sm text-red-600 hover:text-red-800 underline"
          >
            Try again
          </button>
        </div>
      </div>
    );
  }

  if (history.length === 0) {
    return (
      <div className="space-y-4">
        <h3 className="text-lg font-medium text-gray-900">Resolution History</h3>
        <div className="p-4 bg-gray-50 border border-gray-200 rounded-lg">
          <p className="text-sm text-gray-600">No resolution history available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium text-gray-900">Resolution History</h3>
        {hasMore && (
          <button
            onClick={() => loadHistory(page + 1)}
            disabled={isLoadingHistory}
            className="text-sm text-blue-600 hover:text-blue-800 disabled:opacity-50"
          >
            {isLoadingHistory ? "Loading..." : "Load More"}
          </button>
        )}
      </div>

      <div className="space-y-3">
        {history.map((entry) => (
          <div
            key={entry.id}
            className={`p-4 rounded-lg border ${getActionColor(entry.action_type)}`}
          >
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0 mt-0.5">
                {getActionIcon(entry.action_type)}
              </div>
              
              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-2 mb-2">
                  <span className="text-sm font-medium text-gray-900 capitalize">
                    {entry.action_type.replace("_", " ")}
                  </span>
                  {entry.new_result && getResultBadge(entry.new_result)}
                </div>

                <div className="space-y-1 text-sm text-gray-600">
                  {entry.previous_result && entry.new_result && (
                    <div>
                      <span className="font-medium">Result changed:</span>{" "}
                      {getResultBadge(entry.previous_result)} → {getResultBadge(entry.new_result)}
                    </div>
                  )}
                  
                  {entry.resolution_notes && (
                    <div>
                      <span className="font-medium">Notes:</span> {entry.resolution_notes}
                    </div>
                  )}
                  
                  {entry.dispute_reason && (
                    <div>
                      <span className="font-medium">Dispute reason:</span> {entry.dispute_reason}
                    </div>
                  )}
                  
                  {entry.resolution_source && (
                    <div>
                      <span className="font-medium">Source:</span>{" "}
                      <a
                        href={entry.resolution_source}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-800 underline"
                      >
                        {entry.resolution_source}
                      </a>
                    </div>
                  )}
                </div>

                <div className="flex items-center space-x-4 mt-3 text-xs text-gray-500">
                  <div className="flex items-center space-x-1">
                    <Clock className="h-3 w-3" />
                    <span>{formatDate(entry.created_at)}</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <User className="h-3 w-3" />
                    <span>User #{entry.performed_by}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
