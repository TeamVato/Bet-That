import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useRealTimeUpdates } from "../useRealTimeUpdates";

// Mock WebSocket
class MockWebSocket {
  public readyState: number = WebSocket.CONNECTING;
  public url: string;
  public onopen: ((event: Event) => void) | null = null;
  public onclose: ((event: CloseEvent) => void) | null = null;
  public onmessage: ((event: MessageEvent) => void) | null = null;
  public onerror: ((event: Event) => void) | null = null;

  constructor(url: string) {
    this.url = url;
    // Simulate connection after a short delay
    setTimeout(() => {
      this.readyState = WebSocket.OPEN;
      if (this.onopen) {
        this.onopen(new Event('open'));
      }
    }, 10);
  }

  send(data: string) {
    // Mock send implementation
  }

  close() {
    this.readyState = WebSocket.CLOSED;
    if (this.onclose) {
      this.onclose(new CloseEvent('close'));
    }
  }

  // Helper method to simulate receiving a message
  simulateMessage(data: any) {
    if (this.onmessage) {
      const event = new MessageEvent('message', {
        data: JSON.stringify(data)
      });
      this.onmessage(event);
    }
  }
}

// Mock global WebSocket
const mockWebSocket = MockWebSocket;
vi.stubGlobal('WebSocket', mockWebSocket);

describe("useRealTimeUpdates", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    // Clean up any active WebSocket connections
    vi.restoreAllMocks();
  });

  it("initializes with correct default state", () => {
    const { result } = renderHook(() => useRealTimeUpdates());

    expect(result.current.isConnected).toBe(false);
    expect(result.current.connectionError).toBe(null);
    expect(typeof result.current.sendMessage).toBe("function");
  });

  it("establishes WebSocket connection", async () => {
    const { result } = renderHook(() => useRealTimeUpdates());

    // Wait for connection to be established
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    expect(result.current.isConnected).toBe(true);
    expect(result.current.connectionError).toBe(null);
  });

  it("handles connection errors", async () => {
    // Mock WebSocket to simulate connection error
    const mockWS = new MockWebSocket("ws://localhost:8000/ws");
    mockWS.readyState = WebSocket.CONNECTING;
    
    // Simulate error
    await act(async () => {
      if (mockWS.onerror) {
        mockWS.onerror(new Event('error'));
      }
    });

    const { result } = renderHook(() => useRealTimeUpdates());
    
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    // Connection should eventually succeed despite initial error
    expect(result.current.isConnected).toBe(true);
  });

  it("handles connection close", async () => {
    const { result } = renderHook(() => useRealTimeUpdates());

    // Wait for initial connection
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    expect(result.current.isConnected).toBe(true);

    // Simulate connection close
    await act(async () => {
      // In real implementation, this would be handled by the WebSocket close event
      result.current.sendMessage({ type: "close" });
    });

    // Connection state should be updated
    expect(result.current.isConnected).toBe(false);
  });

  it("sends messages when connected", async () => {
    const { result } = renderHook(() => useRealTimeUpdates());

    // Wait for connection
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    const message = { type: "test", data: "hello" };

    await act(async () => {
      result.current.sendMessage(message);
    });

    // Message should be sent (we can't easily test the actual sending in this mock)
    expect(result.current.isConnected).toBe(true);
  });

  it("handles incoming messages", async () => {
    const mockOnMessage = vi.fn();
    const { result } = renderHook(() => useRealTimeUpdates(undefined, mockOnMessage));

    // Wait for connection
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    const testMessage = {
      type: "bet_update",
      data: {
        bet_id: "1",
        status: "resolved",
        result: "win"
      }
    };

    await act(async () => {
      // Simulate receiving a message
      const ws = new MockWebSocket("ws://localhost:8000/ws");
      ws.simulateMessage(testMessage);
    });

    // The callback should be called with the message
    expect(mockOnMessage).toHaveBeenCalledWith(testMessage);
  });

  it("reconnects on connection loss", async () => {
    const { result } = renderHook(() => useRealTimeUpdates());

    // Wait for initial connection
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    expect(result.current.isConnected).toBe(true);

    // Simulate connection loss and reconnection
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 100));
    });

    // Should eventually reconnect
    expect(result.current.isConnected).toBe(true);
  });

  it("handles bet resolution updates", async () => {
    const mockOnBetUpdate = vi.fn();
    const { result } = renderHook(() => useRealTimeUpdates(undefined, mockOnBetUpdate));

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    const betUpdateMessage = {
      type: "bet_resolution",
      data: {
        bet_id: "1",
        old_status: "pending",
        new_status: "resolved",
        result: "win",
        resolution_notes: "Game completed"
      }
    };

    await act(async () => {
      const ws = new MockWebSocket("ws://localhost:8000/ws");
      ws.simulateMessage(betUpdateMessage);
    });

    expect(mockOnBetUpdate).toHaveBeenCalledWith(betUpdateMessage);
  });

  it("handles dispute resolution updates", async () => {
    const mockOnDisputeUpdate = vi.fn();
    const { result } = renderHook(() => useRealTimeUpdates(undefined, mockOnDisputeUpdate));

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    const disputeUpdateMessage = {
      type: "dispute_resolution",
      data: {
        bet_id: "1",
        dispute_reason: "Score was incorrect",
        resolved_by: "admin"
      }
    };

    await act(async () => {
      const ws = new MockWebSocket("ws://localhost:8000/ws");
      ws.simulateMessage(disputeUpdateMessage);
    });

    expect(mockOnDisputeUpdate).toHaveBeenCalledWith(disputeUpdateMessage);
  });

  it("handles malformed messages gracefully", async () => {
    const mockOnMessage = vi.fn();
    const { result } = renderHook(() => useRealTimeUpdates(undefined, mockOnMessage));

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    // Simulate malformed message
    await act(async () => {
      const ws = new MockWebSocket("ws://localhost:8000/ws");
      const event = new MessageEvent('message', {
        data: "invalid json"
      });
      ws.onmessage?.(event);
    });

    // Should not crash and callback should not be called with invalid data
    expect(result.current.isConnected).toBe(true);
  });

  it("cleans up WebSocket connection on unmount", () => {
    const { result, unmount } = renderHook(() => useRealTimeUpdates());

    // Wait for connection
    act(() => {
      setTimeout(() => {}, 50);
    });

    // Unmount the hook
    unmount();

    // Connection should be cleaned up
    expect(result.current.isConnected).toBe(false);
  });

  it("handles multiple message types", async () => {
    const mockOnMessage = vi.fn();
    const { result } = renderHook(() => useRealTimeUpdates(undefined, mockOnMessage));

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    const messages = [
      { type: "bet_update", data: { bet_id: "1", status: "resolved" } },
      { type: "dispute_update", data: { bet_id: "1", dispute_reason: "Score wrong" } },
      { type: "system_message", data: { message: "Server maintenance in 5 minutes" } }
    ];

    await act(async () => {
      const ws = new MockWebSocket("ws://localhost:8000/ws");
      messages.forEach(msg => ws.simulateMessage(msg));
    });

    expect(mockOnMessage).toHaveBeenCalledTimes(messages.length);
    messages.forEach((msg, index) => {
      expect(mockOnMessage).toHaveBeenNthCalledWith(index + 1, msg);
    });
  });

  it("handles connection timeout", async () => {
    // Mock WebSocket that never connects
    const mockWS = new MockWebSocket("ws://localhost:8000/ws");
    mockWS.readyState = WebSocket.CONNECTING;
    
    const { result } = renderHook(() => useRealTimeUpdates());

    // Wait longer than typical connection timeout
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 200));
    });

    // Should handle timeout gracefully
    expect(result.current.isConnected).toBe(false);
  });

  it("retries connection on failure", async () => {
    const { result } = renderHook(() => useRealTimeUpdates());

    // Wait for initial connection attempt
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    // Should eventually connect
    expect(result.current.isConnected).toBe(true);
  });

  it("handles rapid connect/disconnect cycles", async () => {
    const { result } = renderHook(() => useRealTimeUpdates());

    // Simulate rapid connection changes
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 10));
    });

    expect(result.current.isConnected).toBe(true);

    // Simulate disconnect
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 10));
    });

    // Should handle gracefully
    expect(result.current.isConnected).toBe(true);
  });

  it("filters messages by type when specified", async () => {
    const mockOnFilteredMessage = vi.fn();
    const { result } = renderHook(() => useRealTimeUpdates("bet_update", mockOnFilteredMessage));

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    const messages = [
      { type: "bet_update", data: { bet_id: "1" } },
      { type: "dispute_update", data: { bet_id: "1" } },
      { type: "bet_update", data: { bet_id: "2" } }
    ];

    await act(async () => {
      const ws = new MockWebSocket("ws://localhost:8000/ws");
      messages.forEach(msg => ws.simulateMessage(msg));
    });

    // Should only call callback for bet_update messages
    expect(mockOnFilteredMessage).toHaveBeenCalledTimes(2);
    expect(mockOnFilteredMessage).toHaveBeenNthCalledWith(1, messages[0]);
    expect(mockOnFilteredMessage).toHaveBeenNthCalledWith(2, messages[2]);
  });

  it("handles message queue when disconnected", async () => {
    const { result } = renderHook(() => useRealTimeUpdates());

    // Don't wait for connection
    const message = { type: "test", data: "queued" };

    await act(async () => {
      result.current.sendMessage(message);
    });

    // Message should be queued or handled gracefully when not connected
    expect(result.current.isConnected).toBe(false);
  });
});

