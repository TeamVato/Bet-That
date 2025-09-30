import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { 
  ArrowLeft, 
  Search, 
  Filter, 
  Download, 
  Calendar,
  User,
  Clock,
  CheckCircle,
  XCircle,
  AlertTriangle,
  FileText
} from "lucide-react";
import { useResolutionHistory } from "@/hooks/useResolutionAnalytics";
import { ResolutionHistoryFilters } from "@/services/api";
import Toast from "@/components/Toast";

export default function ResolutionHistory() {
  const navigate = useNavigate();
  const [filters, setFilters] = useState<ResolutionHistoryFilters>({
    page: 1,
    per_page: 20,
  });
  const [showFilters, setShowFilters] = useState(false);
  const [toast, setToast] = useState<{
    message: string;
    type: "success" | "error";
  } | null>(null);

  const { history, isLoading, error, refetch, exportData } = useResolutionHistory(filters);

  const handleFilterChange = (key: keyof ResolutionHistoryFilters, value: any) => {
    setFilters(prev => ({
      ...prev,
      [key]: value,
      page: 1, // Reset to first page when filters change
    }));
  };

  const handleSearch = (searchTerm: string) => {
    // For now, we'll implement basic filtering
    // In a real app, you'd have a search endpoint
    setFilters(prev => ({
      ...prev,
      page: 1,
    }));
  };

  const handleExport = async (format: "csv" | "json" = "csv") => {
    try {
      await exportData(format);
      setToast({
        message: `Data exported successfully as ${format.toUpperCase()}!`,
        type: "success",
      });
    } catch (err) {
      setToast({
        message: "Failed to export data",
        type: "error",
      });
    }
  };

  const handlePageChange = (newPage: number) => {
    setFilters(prev => ({
      ...prev,
      page: newPage,
    }));
  };

  const getResultIcon = (result: string) => {
    switch (result.toLowerCase()) {
      case "win":
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case "loss":
        return <XCircle className="h-4 w-4 text-red-600" />;
      case "push":
        return <AlertTriangle className="h-4 w-4 text-yellow-600" />;
      case "void":
        return <XCircle className="h-4 w-4 text-gray-600" />;
      default:
        return <FileText className="h-4 w-4 text-gray-600" />;
    }
  };

  const getResultColor = (result: string) => {
    switch (result.toLowerCase()) {
      case "win":
        return "bg-green-100 text-green-800";
      case "loss":
        return "bg-red-100 text-red-800";
      case "push":
        return "bg-yellow-100 text-yellow-800";
      case "void":
        return "bg-gray-100 text-gray-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-center">
              <FileText className="h-12 w-12 text-red-600 mx-auto mb-4" />
              <h2 className="text-xl font-semibold text-gray-900 mb-2">
                Failed to load resolution history
              </h2>
              <p className="text-gray-600 mb-4">{error}</p>
              <button
                onClick={() => refetch()}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Try Again
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate("/resolution-analytics")}
                className="flex items-center text-gray-600 hover:text-gray-900"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Analytics
              </button>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">
                  Resolution History
                </h1>
                <p className="text-gray-600 mt-1">
                  Detailed history of all bet resolutions
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <button
                onClick={() => setShowFilters(!showFilters)}
                className="flex items-center px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
              >
                <Filter className="h-4 w-4 mr-2" />
                Filters
              </button>
              <button
                onClick={() => handleExport("csv")}
                className="flex items-center px-4 py-2 text-white bg-green-600 rounded-md hover:bg-green-700"
              >
                <Download className="h-4 w-4 mr-2" />
                Export CSV
              </button>
            </div>
          </div>
        </div>

        {/* Filters */}
        {showFilters && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Filters</h3>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Start Date
                </label>
                <input
                  type="date"
                  value={filters.start_date || ""}
                  onChange={(e) => handleFilterChange("start_date", e.target.value || undefined)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  End Date
                </label>
                <input
                  type="date"
                  value={filters.end_date || ""}
                  onChange={(e) => handleFilterChange("end_date", e.target.value || undefined)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Result
                </label>
                <select
                  value={filters.result || ""}
                  onChange={(e) => handleFilterChange("result", e.target.value || undefined)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">All Results</option>
                  <option value="win">Win</option>
                  <option value="loss">Loss</option>
                  <option value="push">Push</option>
                  <option value="void">Void</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Has Dispute
                </label>
                <select
                  value={filters.has_dispute?.toString() || ""}
                  onChange={(e) => handleFilterChange("has_dispute", e.target.value === "true" ? true : e.target.value === "false" ? false : undefined)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">All</option>
                  <option value="true">Has Dispute</option>
                  <option value="false">No Dispute</option>
                </select>
              </div>
            </div>
          </div>
        )}

        {/* History Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">
              Resolution History
              {history && (
                <span className="ml-2 text-sm font-normal text-gray-600">
                  ({history.total} total)
                </span>
              )}
            </h3>
          </div>

          {isLoading ? (
            <div className="p-6">
              <div className="animate-pulse space-y-4">
                {[...Array(5)].map((_, i) => (
                  <div key={i} className="h-16 bg-gray-200 rounded"></div>
                ))}
              </div>
            </div>
          ) : history && history.history.length > 0 ? (
            <>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Bet Details
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Result
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Resolved By
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Resolution Time
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {history.history.map((item) => (
                      <tr key={item.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div>
                            <div className="text-sm font-medium text-gray-900">
                              {item.game_name}
                            </div>
                            <div className="text-sm text-gray-500">
                              {item.market} - {item.selection}
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            {getResultIcon(item.result)}
                            <span className={`ml-2 px-2 py-1 rounded-full text-xs font-medium ${getResultColor(item.result)}`}>
                              {item.result}
                            </span>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <User className="h-4 w-4 text-gray-400 mr-2" />
                            <span className="text-sm text-gray-900">{item.resolver_name}</span>
                          </div>
                          <div className="text-sm text-gray-500">
                            {new Date(item.resolved_at).toLocaleString()}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <Clock className="h-4 w-4 text-gray-400 mr-2" />
                            <span className="text-sm text-gray-900">
                              {item.resolution_time_hours.toFixed(1)}h
                            </span>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          {item.is_disputed ? (
                            <span className="px-2 py-1 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                              Disputed
                            </span>
                          ) : (
                            <span className="px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                              Resolved
                            </span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              {history.total > (filters.per_page || 20) && (
                <div className="px-6 py-4 border-t border-gray-200">
                  <div className="flex items-center justify-between">
                    <div className="text-sm text-gray-700">
                      Showing {((filters.page || 1) - 1) * (filters.per_page || 20) + 1} to{" "}
                      {Math.min((filters.page || 1) * (filters.per_page || 20), history.total)} of{" "}
                      {history.total} results
                    </div>
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => handlePageChange((filters.page || 1) - 1)}
                        disabled={!filters.page || filters.page <= 1}
                        className="px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        Previous
                      </button>
                      <span className="px-3 py-1 text-sm text-gray-700">
                        Page {filters.page || 1} of {Math.ceil(history.total / (filters.per_page || 20))}
                      </span>
                      <button
                        onClick={() => handlePageChange((filters.page || 1) + 1)}
                        disabled={!filters.page || filters.page >= Math.ceil(history.total / (filters.per_page || 20))}
                        className="px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        Next
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="p-6 text-center">
              <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No resolution history found</h3>
              <p className="text-gray-600">Try adjusting your filters or check back later.</p>
            </div>
          )}
        </div>
      </div>

      {/* Toast Notification */}
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

