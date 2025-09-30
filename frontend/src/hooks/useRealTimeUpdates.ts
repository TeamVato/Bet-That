import { useEffect, useRef, useState, useCallback } from 'react';
import { API_BASE_URL } from '@/config/api';

export interface BetResolutionUpdate {
  type: 'bet_resolved' | 'bet_disputed' | 'bet_updated';
  bet_id: string;
  user_id: string;
  data: {
    bet_id: string;
    status: string;
    result?: 'win' | 'loss' | 'push' | 'void';
    resolution_notes?: string;
    resolution_source?: string;
    dispute_reason?: string;
    updated_at: string;
  };
  timestamp: string;
}

export interface WebSocketConnection {
  isConnected: boolean;
  isConnecting: boolean;
  error: string | null;
  lastMessage: BetResolutionUpdate | null;
}

export function useRealTimeUpdates(
  userId?: string,
  onBetUpdate?: (update: BetResolutionUpdate) => void
) {
  const [connection, setConnection] = useState<WebSocketConnection>({
    isConnected: false,
    isConnecting: false,
    error: null,
    lastMessage: null,
  });

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;
  const baseReconnectDelay = 1000; // 1 second

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    setConnection(prev => ({ ...prev, isConnecting: true, error: null }));

    try {
      // Convert HTTP URL to WebSocket URL
      const wsUrl = API_BASE_URL.replace(/^https?:\/\//, 'ws://').replace(/^https:\/\//, 'wss://');
      const ws = new WebSocket(`${wsUrl}/ws/bet-updates${userId ? `?user_id=${userId}` : ''}`);

      ws.onopen = () => {
        console.log('WebSocket connected');
        setConnection(prev => ({
          ...prev,
          isConnected: true,
          isConnecting: false,
          error: null,
        }));
        reconnectAttempts.current = 0;
      };

      ws.onmessage = (event) => {
        try {
          const update: BetResolutionUpdate = JSON.parse(event.data);
          setConnection(prev => ({ ...prev, lastMessage: update }));
          
          if (onBetUpdate) {
            onBetUpdate(update);
          }
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      ws.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason);
        setConnection(prev => ({
          ...prev,
          isConnected: false,
          isConnecting: false,
        }));

        // Attempt to reconnect if not a normal closure
        if (event.code !== 1000 && reconnectAttempts.current < maxReconnectAttempts) {
          const delay = baseReconnectDelay * Math.pow(2, reconnectAttempts.current);
          reconnectAttempts.current++;
          
          console.log(`Attempting to reconnect in ${delay}ms (attempt ${reconnectAttempts.current})`);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, delay);
        } else if (reconnectAttempts.current >= maxReconnectAttempts) {
          setConnection(prev => ({
            ...prev,
            error: 'Failed to reconnect after multiple attempts',
          }));
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnection(prev => ({
          ...prev,
          error: 'WebSocket connection error',
          isConnecting: false,
        }));
      };

      wsRef.current = ws;
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      setConnection(prev => ({
        ...prev,
        error: 'Failed to create WebSocket connection',
        isConnecting: false,
      }));
    }
  }, [userId, onBetUpdate]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (wsRef.current) {
      wsRef.current.close(1000, 'Manual disconnect');
      wsRef.current = null;
    }

    setConnection(prev => ({
      ...prev,
      isConnected: false,
      isConnecting: false,
      error: null,
    }));
  }, []);

  const sendMessage = useCallback((message: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected');
    }
  }, []);

  // Auto-connect on mount and when userId changes
  useEffect(() => {
    connect();
    return () => disconnect();
  }, [connect, disconnect]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, []);

  return {
    ...connection,
    connect,
    disconnect,
    sendMessage,
  };
}

// Alternative polling-based approach for environments where WebSocket is not available
export function usePollingUpdates(
  userId?: string,
  onBetUpdate?: (update: BetResolutionUpdate) => void,
  interval: number = 30000 // 30 seconds
) {
  const [isPolling, setIsPolling] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<string | null>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const pollForUpdates = useCallback(async () => {
    if (!userId) return;

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/bets/updates?since=${lastUpdate || ''}&user_id=${userId}`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      if (data.updates && data.updates.length > 0) {
        data.updates.forEach((update: BetResolutionUpdate) => {
          if (onBetUpdate) {
            onBetUpdate(update);
          }
        });
        setLastUpdate(data.last_update || new Date().toISOString());
      }
      
      setError(null);
    } catch (err) {
      console.error('Polling error:', err);
      setError(err instanceof Error ? err.message : 'Polling failed');
    }
  }, [userId, lastUpdate, onBetUpdate]);

  const startPolling = useCallback(() => {
    if (intervalRef.current) return;
    
    setIsPolling(true);
    setError(null);
    
    // Initial poll
    pollForUpdates();
    
    // Set up interval
    intervalRef.current = setInterval(pollForUpdates, interval);
  }, [pollForUpdates, interval]);

  const stopPolling = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    setIsPolling(false);
  }, []);

  // Auto-start polling when userId is available
  useEffect(() => {
    if (userId) {
      startPolling();
    } else {
      stopPolling();
    }

    return () => stopPolling();
  }, [userId, startPolling, stopPolling]);

  return {
    isPolling,
    error,
    startPolling,
    stopPolling,
    lastUpdate,
  };
}

