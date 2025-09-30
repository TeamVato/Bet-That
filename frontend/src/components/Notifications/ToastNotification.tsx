import React, { useEffect, useState } from 'react';
import { CheckCircle, XCircle, AlertTriangle, Info, X } from 'lucide-react';
import { BetResolutionUpdate } from '@/hooks/useRealTimeUpdates';

export interface ToastNotification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  duration?: number;
  action?: {
    label: string;
    onClick: () => void;
  };
  data?: any;
}

interface ToastProps {
  notification: ToastNotification;
  onClose: (id: string) => void;
}

const Toast: React.FC<ToastProps> = ({ notification, onClose }) => {
  const [isVisible, setIsVisible] = useState(true);
  const [isExiting, setIsExiting] = useState(false);

  useEffect(() => {
    const duration = notification.duration || 5000;
    const timer = setTimeout(() => {
      handleClose();
    }, duration);

    return () => clearTimeout(timer);
  }, [notification.duration]);

  const handleClose = () => {
    setIsExiting(true);
    setTimeout(() => {
      setIsVisible(false);
      onClose(notification.id);
    }, 300);
  };

  const getIcon = () => {
    switch (notification.type) {
      case 'success':
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      case 'error':
        return <XCircle className="h-5 w-5 text-red-600" />;
      case 'warning':
        return <AlertTriangle className="h-5 w-5 text-yellow-600" />;
      case 'info':
      default:
        return <Info className="h-5 w-5 text-blue-600" />;
    }
  };

  const getBackgroundColor = () => {
    switch (notification.type) {
      case 'success':
        return 'bg-green-50 border-green-200';
      case 'error':
        return 'bg-red-50 border-red-200';
      case 'warning':
        return 'bg-yellow-50 border-yellow-200';
      case 'info':
      default:
        return 'bg-blue-50 border-blue-200';
    }
  };

  if (!isVisible) return null;

  return (
    <div
      className={`
        fixed right-4 top-4 z-50 max-w-sm w-full
        transform transition-all duration-300 ease-in-out
        ${isExiting ? 'translate-x-full opacity-0' : 'translate-x-0 opacity-100'}
      `}
    >
      <div className={`
        rounded-lg border p-4 shadow-lg
        ${getBackgroundColor()}
      `}>
        <div className="flex items-start">
          <div className="flex-shrink-0">
            {getIcon()}
          </div>
          <div className="ml-3 flex-1">
            <h4 className="text-sm font-medium text-gray-900">
              {notification.title}
            </h4>
            <p className="mt-1 text-sm text-gray-600">
              {notification.message}
            </p>
            {notification.action && (
              <div className="mt-3">
                <button
                  onClick={notification.action.onClick}
                  className="text-sm font-medium text-blue-600 hover:text-blue-500"
                >
                  {notification.action.label}
                </button>
              </div>
            )}
          </div>
          <div className="ml-4 flex-shrink-0">
            <button
              onClick={handleClose}
              className="inline-flex text-gray-400 hover:text-gray-600 focus:outline-none"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Toast container component
interface ToastContainerProps {
  notifications: ToastNotification[];
  onClose: (id: string) => void;
}

export const ToastContainer: React.FC<ToastContainerProps> = ({ notifications, onClose }) => {
  return (
    <div className="fixed right-4 top-4 z-50 space-y-2">
      {notifications.map((notification) => (
        <Toast
          key={notification.id}
          notification={notification}
          onClose={onClose}
        />
      ))}
    </div>
  );
};

// Hook for managing toast notifications
export function useToastNotifications() {
  const [notifications, setNotifications] = useState<ToastNotification[]>([]);

  const addNotification = (notification: Omit<ToastNotification, 'id'>) => {
    const id = Math.random().toString(36).substr(2, 9);
    const newNotification: ToastNotification = {
      ...notification,
      id,
    };
    
    setNotifications(prev => [...prev, newNotification]);
    return id;
  };

  const removeNotification = (id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  const clearAll = () => {
    setNotifications([]);
  };

  return {
    notifications,
    addNotification,
    removeNotification,
    clearAll,
  };
}

// Utility function to create bet resolution notifications
export function createBetResolutionNotification(update: BetResolutionUpdate): Omit<ToastNotification, 'id'> {
  const { type, data } = update;
  
  switch (type) {
    case 'bet_resolved':
      const resultEmoji = {
        win: '🎉',
        loss: '😞',
        push: '🤝',
        void: '🔄'
      }[data.result || 'void'];
      
      return {
        type: 'success',
        title: `Bet Resolved ${resultEmoji}`,
        message: `Your bet has been resolved as ${data.result?.toUpperCase() || 'VOID'}. ${data.resolution_notes ? `Notes: ${data.resolution_notes}` : ''}`,
        duration: 8000,
        action: {
          label: 'View Details',
          onClick: () => {
            // Navigate to bet details
            window.location.href = `/bets/${data.bet_id}`;
          }
        },
        data: update
      };
      
    case 'bet_disputed':
      return {
        type: 'warning',
        title: 'Bet Disputed ⚠️',
        message: `A dispute has been raised for bet #${data.bet_id}. ${data.dispute_reason ? `Reason: ${data.dispute_reason}` : ''}`,
        duration: 10000,
        action: {
          label: 'Review Dispute',
          onClick: () => {
            window.location.href = `/bets/${data.bet_id}/dispute`;
          }
        },
        data: update
      };
      
    case 'bet_updated':
      return {
        type: 'info',
        title: 'Bet Updated 📝',
        message: `Bet #${data.bet_id} has been updated. Status: ${data.status}`,
        duration: 5000,
        action: {
          label: 'View Bet',
          onClick: () => {
            window.location.href = `/bets/${data.bet_id}`;
          }
        },
        data: update
      };
      
    default:
      return {
        type: 'info',
        title: 'Bet Update',
        message: `Bet #${data.bet_id} has been updated`,
        duration: 5000,
        data: update
      };
  }
}

// Component for displaying recent resolution activity
interface RecentResolutionsProps {
  updates: BetResolutionUpdate[];
  maxItems?: number;
}

export const RecentResolutions: React.FC<RecentResolutionsProps> = ({ 
  updates, 
  maxItems = 5 
}) => {
  const recentUpdates = updates.slice(0, maxItems);
  
  if (recentUpdates.length === 0) {
    return (
      <div className="p-4 bg-gray-50 rounded-lg">
        <p className="text-sm text-gray-600">No recent resolution activity</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <h3 className="text-lg font-medium text-gray-900">Recent Resolutions</h3>
      <div className="space-y-2">
        {recentUpdates.map((update) => {
          const notification = createBetResolutionNotification(update);
          return (
            <div
              key={`${update.bet_id}-${update.timestamp}`}
              className="p-3 bg-white border border-gray-200 rounded-lg shadow-sm"
            >
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0">
                  {notification.type === 'success' && <CheckCircle className="h-4 w-4 text-green-600" />}
                  {notification.type === 'warning' && <AlertTriangle className="h-4 w-4 text-yellow-600" />}
                  {notification.type === 'info' && <Info className="h-4 w-4 text-blue-600" />}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900">
                    {notification.title}
                  </p>
                  <p className="text-sm text-gray-600">
                    {notification.message}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    {new Date(update.timestamp).toLocaleString()}
                  </p>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

