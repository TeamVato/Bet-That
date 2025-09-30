import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { 
  ArrowLeft, 
  RefreshCw, 
  Download, 
  Calendar,
  TrendingUp,
  BarChart3
} from "lucide-react";
import { ResolutionStats } from "@/components/Analytics/ResolutionStats";
import { ResolutionChart } from "@/components/Analytics/ResolutionChart";
import { useResolutionAnalytics } from "@/hooks/useResolutionAnalytics";
import Toast from "@/components/Toast";

export default function ResolutionAnalytics() {
  const navigate = useNavigate();
  const { analytics, isLoading, error, refetch } = useResolutionAnalytics();
  const [toast, setToast] = useState<{
    message: string;
    type: "success" | "error";
  } | null>(null);

  const handleRefresh = async () => {
    try {
      await refetch();
      setToast({
        message: "Analytics refreshed successfully!",
        type: "success",
      });
    } catch (err) {
      setToast({
        message: "Failed to refresh analytics",
        type: "error",
      });
    }
  };

  const handleExport = () => {
    // This will be implemented when we add the export functionality
    setToast({
      message: "Export functionality coming soon!",
      type: "success",
    });
  };

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-center">
              <BarChart3 className="h-12 w-12 text-red-600 mx-auto mb-4" />
              <h2 className="text-xl font-semibold text-gray-900 mb-2">
                Failed to load analytics
              </h2>
              <p className="text-gray-600 mb-4">{error}</p>
              <button
                onClick={handleRefresh}
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
                onClick={() => navigate("/my-bets")}
                className="flex items-center text-gray-600 hover:text-gray-900"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to My Bets
              </button>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">
                  Resolution Analytics
                </h1>
                <p className="text-gray-600 mt-1">
                  Comprehensive insights into bet resolution performance
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <button
                onClick={handleRefresh}
                disabled={isLoading}
                className="flex items-center px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? "animate-spin" : ""}`} />
                Refresh
              </button>
              <button
                onClick={handleExport}
                className="flex items-center px-4 py-2 text-white bg-green-600 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
              >
                <Download className="h-4 w-4 mr-2" />
                Export
              </button>
            </div>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="mb-8">
          <div className="flex items-center mb-4">
            <TrendingUp className="h-5 w-5 text-blue-600 mr-2" />
            <h2 className="text-xl font-semibold text-gray-900">Key Metrics</h2>
          </div>
          {analytics && <ResolutionStats analytics={analytics} isLoading={isLoading} />}
        </div>

        {/* Charts and Visualizations */}
        <div className="mb-8">
          <div className="flex items-center mb-4">
            <BarChart3 className="h-5 w-5 text-blue-600 mr-2" />
            <h2 className="text-xl font-semibold text-gray-900">Analytics Dashboard</h2>
          </div>
          {analytics && <ResolutionChart analytics={analytics} isLoading={isLoading} />}
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button
              onClick={() => navigate("/resolution-history")}
              className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <Calendar className="h-8 w-8 text-blue-600 mr-3" />
              <div className="text-left">
                <div className="font-medium text-gray-900">Resolution History</div>
                <div className="text-sm text-gray-600">View detailed resolution history</div>
              </div>
            </button>
            <button
              onClick={() => navigate("/my-bets")}
              className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <TrendingUp className="h-8 w-8 text-green-600 mr-3" />
              <div className="text-left">
                <div className="font-medium text-gray-900">My Bets</div>
                <div className="text-sm text-gray-600">Manage your active bets</div>
              </div>
            </button>
            <button
              onClick={handleExport}
              className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <Download className="h-8 w-8 text-purple-600 mr-3" />
              <div className="text-left">
                <div className="font-medium text-gray-900">Export Data</div>
                <div className="text-sm text-gray-600">Download resolution data</div>
              </div>
            </button>
          </div>
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
