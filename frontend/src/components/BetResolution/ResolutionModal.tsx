import React from "react";
import { X } from "lucide-react";
import { ResolutionForm } from "./ResolutionForm";
import { PlacedBet } from "@/services/api";

interface ResolutionModalProps {
  bet: PlacedBet;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export const ResolutionModal: React.FC<ResolutionModalProps> = ({
  bet,
  isOpen,
  onClose,
  onSuccess,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black bg-opacity-50"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="relative bg-white rounded-lg shadow-xl max-w-md w-full mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">
            Resolve Bet
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {/* Bet Summary */}
          <div className="mb-6 p-4 bg-gray-50 rounded-lg">
            <h3 className="font-medium text-gray-900 mb-2">Bet Details</h3>
            <div className="space-y-1 text-sm text-gray-600">
              <div><span className="font-medium">Game:</span> {bet.game_name}</div>
              <div><span className="font-medium">Market:</span> {bet.market}</div>
              <div><span className="font-medium">Selection:</span> {bet.selection}</div>
              <div><span className="font-medium">Stake:</span> ${bet.stake}</div>
              <div><span className="font-medium">Odds:</span> {bet.odds > 0 ? '+' : ''}{bet.odds}</div>
              <div><span className="font-medium">Potential Win:</span> ${bet.potential_win}</div>
            </div>
          </div>

          {/* Resolution Form */}
          <ResolutionForm
            bet={bet}
            onSuccess={onSuccess}
            onCancel={onClose}
          />
        </div>
      </div>
    </div>
  );
};
