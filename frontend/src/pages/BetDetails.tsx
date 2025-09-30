import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { 
  ArrowLeft, 
  Calendar, 
  DollarSign, 
  Target, 
  TrendingUp, 
  Clock,
  CheckCircle,
  XCircle,
  AlertTriangle,
  FileText,
  User
} from "lucide-react";
import { PlacedBet } from "@/services/api";
import { ResolutionModal } from "@/components/BetResolution/ResolutionModal";
import { ResolutionHistory } from "@/components/BetResolution/ResolutionHistory";
import { useBetResolution } from "@/hooks/useBetResolution";
import Toast from "@/components/Toast";

export default function BetDetails() {
  const { betId } = useParams<{ betId: string }>();
  const navigate = useNavigate();
  const [bet, setBet] = useState<PlacedBet | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isResolutionModalOpen, setIsResolutionModalOpen] = useState(false);
  const [toast, setToast] = useState<{
    message: string;
    type: "success" | "error";
  } | null>(null);

  const { getPendingResolutionBets } = useBetResolution();

  useEffect(() => {
    if (betId) {
      loadBetDetails();
    }
  }, [betId]);

  const loadBetDetails = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      // For now, we'll fetch from the pending resolution bets
      // In a real app, you'd have a specific endpoint to fetch a single bet
      const response = await getPendingResolutionBets(1, 100);
      const foundBet = response.bets.find(b => b.id === betId);
      
      if (foundBet) {
        setBet(foundBet);
      } else {
        setError("Bet not found");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load bet details");
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case "settled":
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      case "cancelled":
        return <XCircle className="h-5 w-5 text-red-600" />;
      case "pending":
        return <Clock className="h-5 w-5 text-yellow-600" />;
      default:
        return <AlertTriangle className="h-5 w-5 text-gray-600" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case "settled":
        return "bg-green-100 text-green-800";
      case "cancelled":
        return "bg-red-100 text-red-800";
      case "pending":
        return "bg-yellow-100 text-yellow-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const canResolve = () => {
    return bet && bet.status.toLowerCase() === "pending";
  };

  const handleResolutionSuccess = () => {
    setIsResolutionModalOpen(false);
    setToast({
      message: "Bet resolved successfully!",
      type: "success",
    });
    // Reload bet details to show updated status
    loadBetDetails();
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="space-y-4">
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                <div className="h-4 bg-gray-200 rounded w-2/3"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !bet) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-center">
              <XCircle className="h-12 w-12 text-red-600 mx-auto mb-4" />
              <h2 className="text-xl font-semibold text-gray-900 mb-2">
                {error || "Bet not found"}
              </h2>
              <button
                onClick={() => navigate("/my-bets")}
                className="text-blue-600 hover:text-blue-800 underline"
              >
                Back to My Bets
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => navigate("/my-bets")}
            className="flex items-center text-gray-600 hover:text-gray-900 mb-4"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to My Bets
          </button>
          <h1 className="text-2xl font-bold text-gray-900">Bet Details</h1>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Bet Information */}
          <div className="lg:col-span-2 space-y-6">
            {/* Bet Summary Card */}
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900">Bet Summary</h2>
                <div className="flex items-center space-x-2">
                  {getStatusIcon(bet.status)}
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(bet.status)}`}>
                    {bet.status}
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-3">
                  <div className="flex items-center space-x-2">
                    <Target className="h-4 w-4 text-gray-500" />
                    <span className="text-sm font-medium text-gray-700">Game:</span>
                  </div>
                  <p className="text-sm text-gray-900 ml-6">{bet.game_name}</p>

                  <div className="flex items-center space-x-2">
                    <TrendingUp className="h-4 w-4 text-gray-500" />
                    <span className="text-sm font-medium text-gray-700">Market:</span>
                  </div>
                  <p className="text-sm text-gray-900 ml-6">{bet.market}</p>

                  <div className="flex items-center space-x-2">
                    <FileText className="h-4 w-4 text-gray-500" />
                    <span className="text-sm font-medium text-gray-700">Selection:</span>
                  </div>
                  <p className="text-sm text-gray-900 ml-6">{bet.selection}</p>
                </div>

                <div className="space-y-3">
                  <div className="flex items-center space-x-2">
                    <DollarSign className="h-4 w-4 text-gray-500" />
                    <span className="text-sm font-medium text-gray-700">Stake:</span>
                  </div>
                  <p className="text-sm text-gray-900 ml-6">${bet.stake}</p>

                  <div className="flex items-center space-x-2">
                    <TrendingUp className="h-4 w-4 text-gray-500" />
                    <span className="text-sm font-medium text-gray-700">Odds:</span>
                  </div>
                  <p className="text-sm text-gray-900 ml-6">
                    {bet.odds > 0 ? '+' : ''}{bet.odds}
                  </p>

                  <div className="flex items-center space-x-2">
                    <DollarSign className="h-4 w-4 text-gray-500" />
                    <span className="text-sm font-medium text-gray-700">Potential Win:</span>
                  </div>
                  <p className="text-sm text-gray-900 ml-6">${bet.potential_win}</p>
                </div>
              </div>

              <div className="mt-6 pt-4 border-t border-gray-200">
                <div className="flex items-center space-x-2">
                  <User className="h-4 w-4 text-gray-500" />
                  <span className="text-sm font-medium text-gray-700">Bookmaker:</span>
                  <span className="text-sm text-gray-900">{bet.bookmaker}</span>
                </div>
                <div className="flex items-center space-x-2 mt-2">
                  <Calendar className="h-4 w-4 text-gray-500" />
                  <span className="text-sm font-medium text-gray-700">Placed:</span>
                  <span className="text-sm text-gray-900">
                    {new Date(bet.placed_at).toLocaleString()}
                  </span>
                </div>
                {bet.settled_at && (
                  <div className="flex items-center space-x-2 mt-2">
                    <CheckCircle className="h-4 w-4 text-gray-500" />
                    <span className="text-sm font-medium text-gray-700">Settled:</span>
                    <span className="text-sm text-gray-900">
                      {new Date(bet.settled_at).toLocaleString()}
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* Resolution History */}
            <ResolutionHistory betId={bet.id} />
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Resolution Actions */}
            {canResolve() && (
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Actions</h3>
                <button
                  onClick={() => setIsResolutionModalOpen(true)}
                  className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                >
                  Resolve Bet
                </button>
              </div>
            )}

            {/* Bet Statistics */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Statistics</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Potential Payout:</span>
                  <span className="text-sm font-medium text-gray-900">
                    ${bet.potential_payout}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Net Profit:</span>
                  <span className="text-sm font-medium text-gray-900">
                    ${(bet.potential_payout - bet.stake).toFixed(2)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">ROI:</span>
                  <span className="text-sm font-medium text-gray-900">
                    {(((bet.potential_payout - bet.stake) / bet.stake) * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Resolution Modal */}
      {isResolutionModalOpen && (
        <ResolutionModal
          bet={bet}
          isOpen={isResolutionModalOpen}
          onClose={() => setIsResolutionModalOpen(false)}
          onSuccess={handleResolutionSuccess}
        />
      )}

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
