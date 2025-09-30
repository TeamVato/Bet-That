import React, { useState, useEffect } from 'react';
import DashboardView from "@/components/Dashboard";
import DashboardErrorBoundary from "@/components/DashboardErrorBoundary";
import { ToastContainer, useToastNotifications, createBetResolutionNotification } from "@/components/Notifications/ToastNotification";
import { useRealTimeUpdates, BetResolutionUpdate } from "@/hooks/useRealTimeUpdates";
import { RecentResolutions } from "@/components/Notifications/ToastNotification";

export default function DashboardPage() {
  const [recentUpdates, setRecentUpdates] = useState<BetResolutionUpdate[]>([]);
  const { notifications, addNotification, removeNotification } = useToastNotifications();
  
  // Handle real-time bet updates
  const handleBetUpdate = (update: BetResolutionUpdate) => {
    // Add to recent updates
    setRecentUpdates(prev => [update, ...prev.slice(0, 9)]); // Keep last 10 updates
    
    // Create and show toast notification
    const notification = createBetResolutionNotification(update);
    addNotification(notification);
  };

  // Use real-time updates (WebSocket)
  const { isConnected, error: wsError } = useRealTimeUpdates(undefined, handleBetUpdate);

  // Show connection status
  useEffect(() => {
    if (wsError) {
      addNotification({
        type: 'error',
        title: 'Connection Error',
        message: 'Failed to connect to real-time updates. Some notifications may be delayed.',
        duration: 8000,
      });
    } else if (isConnected) {
      addNotification({
        type: 'success',
        title: 'Connected',
        message: 'Real-time updates are now active',
        duration: 3000,
      });
    }
  }, [isConnected, wsError, addNotification]);

  return (
    <DashboardErrorBoundary>
      <div className="min-h-screen bg-gray-50">
        {/* Toast Notifications */}
        <ToastContainer 
          notifications={notifications} 
          onClose={removeNotification} 
        />
        
        {/* Main Dashboard */}
        <DashboardView />
        
        {/* Recent Resolutions Sidebar */}
        {recentUpdates.length > 0 && (
          <div className="fixed right-4 top-20 w-80 max-h-96 overflow-y-auto bg-white rounded-lg shadow-lg border border-gray-200 p-4 z-40">
            <RecentResolutions updates={recentUpdates} maxItems={5} />
          </div>
        )}
        
        {/* Connection Status Indicator */}
        <div className="fixed bottom-4 left-4 z-30">
          <div className={`
            px-3 py-2 rounded-full text-xs font-medium shadow-sm
            ${isConnected 
              ? 'bg-green-100 text-green-800 border border-green-200' 
              : 'bg-red-100 text-red-800 border border-red-200'
            }
          `}>
            {isConnected ? '🟢 Live Updates' : '🔴 Offline'}
          </div>
        </div>
      </div>
    </DashboardErrorBoundary>
  );
}
