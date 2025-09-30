import React, { useState, useEffect } from 'react';
import { Clock, CheckCircle, XCircle, AlertTriangle, DollarSign, TrendingUp } from 'lucide-react';
import { PlacedBet } from '@/services/api';
import { BetResolutionUpdate } from '@/hooks/useRealTimeUpdates';

interface BetCardProps {
  bet: PlacedBet;
  onUpdate?: (bet: PlacedBet) => void;
  showActions?: boolean;
  className?: string;
}

export const BetCard: React.FC<BetCardProps> = ({ 
  bet, 
  onUpdate, 
  showActions = true,
  className = '' 
}) => {
  const [localBet, setLocalBet] = useState<PlacedBet>(bet);
  const [isUpdating, setIsUpdating] = useState(false);

  // Update local bet when prop changes
  useEffect(() => {
    setLocalBet(bet);
  }, [bet]);

  // Handle real-time updates for this specific bet
  const handleBetUpdate = (update: BetResolutionUpdate) => {
    if (update.data.bet_id === localBet.id) {
      setIsUpdating(true);
      
      // Update the local bet state
      const updatedBet: PlacedBet = {
        ...localBet,
        status: update.data.status,
        settled_at: update.data.updated_at,
      };
      
      setLocalBet(updatedBet);
      
      // Notify parent component
      if (onUpdate) {
        onUpdate(updatedBet);
      }
      
      // Reset updating state after animation
      setTimeout(() => setIsUpdating(false), 1000);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'settled':
      case 'resolved':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'cancelled':
      case 'voided':
        return <XCircle className="h-4 w-4 text-red-600" />;
      case 'disputed':
        return <AlertTriangle className="h-4 w-4 text-yellow-600" />;
      case 'pending':
      case 'matched':
      default:
        return <Clock className="h-4 w-4 text-blue-600" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'settled':
      case 'resolved':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'cancelled':
      case 'voided':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'disputed':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'pending':
      case 'matched':
      default:
        return 'bg-blue-100 text-blue-800 border-blue-200';
    }
  };

  const getResultBadge = (result?: string) => {
    if (!result) return null;
    
    const colors = {
      win: 'bg-green-100 text-green-800',
      loss: 'bg-red-100 text-red-800',
      push: 'bg-yellow-100 text-yellow-800',
      void: 'bg-gray-100 text-gray-800',
    };

    return (
      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${colors[result as keyof typeof colors] || 'bg-gray-100 text-gray-800'}`}>
        {result.toUpperCase()}
      </span>
    );
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const isResolved = localBet.status.toLowerCase() === 'settled' || localBet.status.toLowerCase() === 'resolved';
  const isDisputed = localBet.status.toLowerCase() === 'disputed';
  const isPending = localBet.status.toLowerCase() === 'pending' || localBet.status.toLowerCase() === 'matched';

  return (
    <div className={`
      bg-white rounded-lg border border-gray-200 p-4 shadow-sm hover:shadow-md transition-all duration-200
      ${isUpdating ? 'ring-2 ring-blue-500 ring-opacity-50' : ''}
      ${className}
    `}>
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 truncate">
            {localBet.game_name}
          </h3>
          <p className="text-sm text-gray-600">
            {localBet.market} • {localBet.selection}
          </p>
        </div>
        <div className="flex items-center space-x-2">
          {getStatusIcon(localBet.status)}
          <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(localBet.status)}`}>
            {localBet.status}
          </span>
        </div>
      </div>

      {/* Bet Details */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <p className="text-xs text-gray-500 uppercase tracking-wide">Stake</p>
          <p className="text-lg font-semibold text-gray-900">
            {formatCurrency(localBet.stake)}
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-500 uppercase tracking-wide">Odds</p>
          <p className="text-lg font-semibold text-gray-900">
            {localBet.odds.toFixed(2)}
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-500 uppercase tracking-wide">Potential Win</p>
          <p className="text-lg font-semibold text-green-600">
            {formatCurrency(localBet.potential_win)}
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-500 uppercase tracking-wide">Total Payout</p>
          <p className="text-lg font-semibold text-blue-600">
            {formatCurrency(localBet.potential_payout)}
          </p>
        </div>
      </div>

      {/* Result Badge (if resolved) */}
      {isResolved && localBet.result && (
        <div className="mb-3">
          {getResultBadge(localBet.result)}
        </div>
      )}

      {/* Timeline */}
      <div className="border-t border-gray-100 pt-3">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <div className="flex items-center space-x-1">
            <Clock className="h-3 w-3" />
            <span>Placed {formatDate(localBet.placed_at)}</span>
          </div>
          {localBet.settled_at && (
            <div className="flex items-center space-x-1">
              <CheckCircle className="h-3 w-3" />
              <span>Settled {formatDate(localBet.settled_at)}</span>
            </div>
          )}
        </div>
      </div>

      {/* Actions */}
      {showActions && (
        <div className="border-t border-gray-100 pt-3 mt-3">
          <div className="flex space-x-2">
            <button
              onClick={() => window.location.href = `/bets/${localBet.id}`}
              className="flex-1 px-3 py-2 text-sm font-medium text-blue-600 bg-blue-50 rounded-md hover:bg-blue-100 transition-colors"
            >
              View Details
            </button>
            
            {isDisputed && (
              <button
                onClick={() => window.location.href = `/bets/${localBet.id}/dispute`}
                className="flex-1 px-3 py-2 text-sm font-medium text-yellow-600 bg-yellow-50 rounded-md hover:bg-yellow-100 transition-colors"
              >
                Review Dispute
              </button>
            )}
            
            {isPending && (
              <button
                onClick={() => window.location.href = `/bets/${localBet.id}/resolve`}
                className="flex-1 px-3 py-2 text-sm font-medium text-green-600 bg-green-50 rounded-md hover:bg-green-100 transition-colors"
              >
                Resolve
              </button>
            )}
          </div>
        </div>
      )}

      {/* Real-time update indicator */}
      {isUpdating && (
        <div className="absolute inset-0 bg-blue-50 bg-opacity-50 rounded-lg flex items-center justify-center">
          <div className="flex items-center space-x-2 text-blue-600">
            <TrendingUp className="h-4 w-4 animate-pulse" />
            <span className="text-sm font-medium">Updating...</span>
          </div>
        </div>
      )}
    </div>
  );
};

// Bet list component with filtering
interface BetListProps {
  bets: PlacedBet[];
  onBetUpdate?: (bet: PlacedBet) => void;
  showFilters?: boolean;
  className?: string;
}

export const BetList: React.FC<BetListProps> = ({ 
  bets, 
  onBetUpdate, 
  showFilters = true,
  className = '' 
}) => {
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [resultFilter, setResultFilter] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');

  const filteredBets = bets.filter(bet => {
    const matchesStatus = statusFilter === 'all' || bet.status.toLowerCase() === statusFilter.toLowerCase();
    const matchesResult = resultFilter === 'all' || (bet.result && bet.result.toLowerCase() === resultFilter.toLowerCase());
    const matchesSearch = searchTerm === '' || 
      bet.game_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      bet.market.toLowerCase().includes(searchTerm.toLowerCase()) ||
      bet.selection.toLowerCase().includes(searchTerm.toLowerCase());
    
    return matchesStatus && matchesResult && matchesSearch;
  });

  const statusOptions = [
    { value: 'all', label: 'All Statuses' },
    { value: 'pending', label: 'Pending' },
    { value: 'matched', label: 'Matched' },
    { value: 'settled', label: 'Settled' },
    { value: 'disputed', label: 'Disputed' },
    { value: 'cancelled', label: 'Cancelled' },
  ];

  const resultOptions = [
    { value: 'all', label: 'All Results' },
    { value: 'win', label: 'Win' },
    { value: 'loss', label: 'Loss' },
    { value: 'push', label: 'Push' },
    { value: 'void', label: 'Void' },
  ];

  return (
    <div className={className}>
      {/* Filters */}
      {showFilters && (
        <div className="mb-6 space-y-4">
          <div className="flex flex-wrap gap-4">
            <div className="flex-1 min-w-64">
              <input
                type="text"
                placeholder="Search bets..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              {statusOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            <select
              value={resultFilter}
              onChange={(e) => setResultFilter(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              {resultOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
          
          <div className="text-sm text-gray-600">
            Showing {filteredBets.length} of {bets.length} bets
          </div>
        </div>
      )}

      {/* Bet Grid */}
      {filteredBets.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500">No bets found matching your criteria</p>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {filteredBets.map(bet => (
            <BetCard
              key={bet.id}
              bet={bet}
              onUpdate={onBetUpdate}
              showActions={true}
            />
          ))}
        </div>
      )}
    </div>
  );
};

