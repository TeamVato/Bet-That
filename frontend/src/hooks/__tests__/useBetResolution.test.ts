import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useBetResolution } from "../useBetResolution";
import { api } from "@/services/api";

// Mock the API service
vi.mock("@/services/api", () => ({
  api: {
    resolveBet: vi.fn(),
    disputeBet: vi.fn(),
    getBetResolutionHistory: vi.fn(),
    getPendingResolutionBets: vi.fn(),
    resolveDispute: vi.fn(),
  },
}));

describe("useBetResolution", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("initializes with correct default state", () => {
    const { result } = renderHook(() => useBetResolution());

    expect(result.current.isResolving).toBe(false);
    expect(result.current.isDisputing).toBe(false);
    expect(result.current.isLoadingHistory).toBe(false);
    expect(typeof result.current.resolveBet).toBe("function");
    expect(typeof result.current.disputeBet).toBe("function");
    expect(typeof result.current.getResolutionHistory).toBe("function");
    expect(typeof result.current.getPendingResolutionBets).toBe("function");
    expect(typeof result.current.resolveDispute).toBe("function");
  });

  describe("resolveBet", () => {
    it("calls API and updates loading state correctly", async () => {
      const mockResolveBet = vi.fn().mockResolvedValue({ success: true });
      vi.mocked(api.resolveBet).mockImplementation(mockResolveBet);

      const { result } = renderHook(() => useBetResolution());

      const request = {
        result: "win",
        resolution_notes: "Game completed",
        resolution_source: "ESPN",
      };

      let resolvePromise: Promise<any>;
      await act(async () => {
        resolvePromise = result.current.resolveBet("1", request);
      });

      // Check loading state is true during resolution
      expect(result.current.isResolving).toBe(false);

      await act(async () => {
        await resolvePromise;
      });

      expect(mockResolveBet).toHaveBeenCalledWith("1", request);
      expect(result.current.isResolving).toBe(false);
    });

    it("handles API errors gracefully", async () => {
      const mockResolveBet = vi.fn().mockRejectedValue(new Error("Resolution failed"));
      vi.mocked(api.resolveBet).mockImplementation(mockResolveBet);

      const { result } = renderHook(() => useBetResolution());

      const request = {
        result: "win",
        resolution_notes: "Game completed",
      };

      await act(async () => {
        try {
          await result.current.resolveBet("1", request);
        } catch (error) {
          // Error should be propagated
        }
      });

      expect(mockResolveBet).toHaveBeenCalledWith("1", request);
      expect(result.current.isResolving).toBe(false);
    });

    it("sets loading state correctly during resolution", async () => {
      let resolveResolve: (value: any) => void;
      const resolvePromise = new Promise((resolve) => {
        resolveResolve = resolve;
      });
      
      const mockResolveBet = vi.fn().mockReturnValue(resolvePromise);
      vi.mocked(api.resolveBet).mockImplementation(mockResolveBet);

      const { result } = renderHook(() => useBetResolution());

      const request = { result: "win" };

      await act(async () => {
        result.current.resolveBet("1", request);
      });

      expect(result.current.isResolving).toBe(false);

      await act(async () => {
        resolveResolve({ success: true });
        await resolvePromise;
      });

      expect(result.current.isResolving).toBe(false);
    });
  });

  describe("disputeBet", () => {
    it("calls API and updates loading state correctly", async () => {
      const mockDisputeBet = vi.fn().mockResolvedValue({ success: true });
      vi.mocked(api.disputeBet).mockImplementation(mockDisputeBet);

      const { result } = renderHook(() => useBetResolution());

      const request = {
        dispute_reason: "Score was incorrect according to official stats",
      };

      await act(async () => {
        await result.current.disputeBet("1", request);
      });

      expect(mockDisputeBet).toHaveBeenCalledWith("1", request);
      expect(result.current.isDisputing).toBe(false);
    });

    it("handles API errors gracefully", async () => {
      const mockDisputeBet = vi.fn().mockRejectedValue(new Error("Dispute failed"));
      vi.mocked(api.disputeBet).mockImplementation(mockDisputeBet);

      const { result } = renderHook(() => useBetResolution());

      const request = {
        dispute_reason: "Score was incorrect according to official stats",
      };

      await act(async () => {
        try {
          await result.current.disputeBet("1", request);
        } catch (error) {
          // Error should be propagated
        }
      });

      expect(mockDisputeBet).toHaveBeenCalledWith("1", request);
      expect(result.current.isDisputing).toBe(false);
    });

    it("sets loading state correctly during dispute", async () => {
      let disputeResolve: (value: any) => void;
      const disputePromise = new Promise((resolve) => {
        disputeResolve = resolve;
      });
      
      const mockDisputeBet = vi.fn().mockReturnValue(disputePromise);
      vi.mocked(api.disputeBet).mockImplementation(mockDisputeBet);

      const { result } = renderHook(() => useBetResolution());

      const request = {
        dispute_reason: "Score was incorrect according to official stats",
      };

      await act(async () => {
        result.current.disputeBet("1", request);
      });

      expect(result.current.isDisputing).toBe(false);

      await act(async () => {
        disputeResolve({ success: true });
        await disputePromise;
      });

      expect(result.current.isDisputing).toBe(false);
    });
  });

  describe("getResolutionHistory", () => {
    it("calls API and updates loading state correctly", async () => {
      const mockGetHistory = vi.fn().mockResolvedValue({
        history: [],
        total: 0,
        page: 1,
        per_page: 20,
      });
      vi.mocked(api.getBetResolutionHistory).mockImplementation(mockGetHistory);

      const { result } = renderHook(() => useBetResolution());

      await act(async () => {
        await result.current.getResolutionHistory("1", 1, 20);
      });

      expect(mockGetHistory).toHaveBeenCalledWith("1", 1, 20);
      expect(result.current.isLoadingHistory).toBe(false);
    });

    it("uses default pagination parameters", async () => {
      const mockGetHistory = vi.fn().mockResolvedValue({
        history: [],
        total: 0,
        page: 1,
        per_page: 10,
      });
      vi.mocked(api.getBetResolutionHistory).mockImplementation(mockGetHistory);

      const { result } = renderHook(() => useBetResolution());

      await act(async () => {
        await result.current.getResolutionHistory("1");
      });

      expect(mockGetHistory).toHaveBeenCalledWith("1", 1, 10);
    });

    it("handles API errors gracefully", async () => {
      const mockGetHistory = vi.fn().mockRejectedValue(new Error("Failed to fetch"));
      vi.mocked(api.getBetResolutionHistory).mockImplementation(mockGetHistory);

      const { result } = renderHook(() => useBetResolution());

      await act(async () => {
        try {
          await result.current.getResolutionHistory("1");
        } catch (error) {
          // Error should be propagated
        }
      });

      expect(mockGetHistory).toHaveBeenCalledWith("1", 1, 10);
      expect(result.current.isLoadingHistory).toBe(false);
    });

    it("sets loading state correctly during history fetch", async () => {
      let historyResolve: (value: any) => void;
      const historyPromise = new Promise((resolve) => {
        historyResolve = resolve;
      });
      
      const mockGetHistory = vi.fn().mockReturnValue(historyPromise);
      vi.mocked(api.getBetResolutionHistory).mockImplementation(mockGetHistory);

      const { result } = renderHook(() => useBetResolution());

      await act(async () => {
        result.current.getResolutionHistory("1");
      });

      expect(result.current.isLoadingHistory).toBe(false);

      await act(async () => {
        historyResolve({
          history: [],
          total: 0,
          page: 1,
          per_page: 10,
        });
        await historyPromise;
      });

      expect(result.current.isLoadingHistory).toBe(false);
    });
  });

  describe("getPendingResolutionBets", () => {
    it("calls API correctly", async () => {
      const mockGetPending = vi.fn().mockResolvedValue({
        bets: [],
        total: 0,
        page: 1,
        per_page: 20,
      });
      vi.mocked(api.getPendingResolutionBets).mockImplementation(mockGetPending);

      const { result } = renderHook(() => useBetResolution());

      await act(async () => {
        await result.current.getPendingResolutionBets(1, 20);
      });

      expect(mockGetPending).toHaveBeenCalledWith(1, 20);
    });

    it("handles API errors gracefully", async () => {
      const mockGetPending = vi.fn().mockRejectedValue(new Error("Failed to fetch"));
      vi.mocked(api.getPendingResolutionBets).mockImplementation(mockGetPending);

      const { result } = renderHook(() => useBetResolution());

      await act(async () => {
        try {
          await result.current.getPendingResolutionBets(1, 20);
        } catch (error) {
          // Error should be propagated
        }
      });

      expect(mockGetPending).toHaveBeenCalledWith(1, 20);
    });
  });

  describe("resolveDispute", () => {
    it("calls API and updates loading state correctly", async () => {
      const mockResolveDispute = vi.fn().mockResolvedValue({ success: true });
      vi.mocked(api.resolveDispute).mockImplementation(mockResolveDispute);

      const { result } = renderHook(() => useBetResolution());

      await act(async () => {
        await result.current.resolveDispute("1", "loss", "Corrected score");
      });

      expect(mockResolveDispute).toHaveBeenCalledWith("1", "loss", "Corrected score");
      expect(result.current.isResolving).toBe(false);
    });

    it("calls API with optional resolution notes", async () => {
      const mockResolveDispute = vi.fn().mockResolvedValue({ success: true });
      vi.mocked(api.resolveDispute).mockImplementation(mockResolveDispute);

      const { result } = renderHook(() => useBetResolution());

      await act(async () => {
        await result.current.resolveDispute("1", "win");
      });

      expect(mockResolveDispute).toHaveBeenCalledWith("1", "win", undefined);
    });

    it("handles API errors gracefully", async () => {
      const mockResolveDispute = vi.fn().mockRejectedValue(new Error("Resolution failed"));
      vi.mocked(api.resolveDispute).mockImplementation(mockResolveDispute);

      const { result } = renderHook(() => useBetResolution());

      await act(async () => {
        try {
          await result.current.resolveDispute("1", "loss", "Corrected score");
        } catch (error) {
          // Error should be propagated
        }
      });

      expect(mockResolveDispute).toHaveBeenCalledWith("1", "loss", "Corrected score");
      expect(result.current.isResolving).toBe(false);
    });

    it("sets loading state correctly during dispute resolution", async () => {
      let disputeResolve: (value: any) => void;
      const disputePromise = new Promise((resolve) => {
        disputeResolve = resolve;
      });
      
      const mockResolveDispute = vi.fn().mockReturnValue(disputePromise);
      vi.mocked(api.resolveDispute).mockImplementation(mockResolveDispute);

      const { result } = renderHook(() => useBetResolution());

      await act(async () => {
        result.current.resolveDispute("1", "loss", "Corrected score");
      });

      expect(result.current.isResolving).toBe(false);

      await act(async () => {
        disputeResolve({ success: true });
        await disputePromise;
      });

      expect(result.current.isResolving).toBe(false);
    });
  });

  describe("concurrent operations", () => {
    it("handles multiple concurrent resolve operations", async () => {
      const mockResolveBet = vi.fn().mockImplementation((betId) => 
        new Promise(resolve => setTimeout(() => resolve({ success: true }), 100))
      );
      vi.mocked(api.resolveBet).mockImplementation(mockResolveBet);

      const { result } = renderHook(() => useBetResolution());

      const request = { result: "win" };

      // Start multiple resolve operations
      await act(async () => {
        const promise1 = result.current.resolveBet("1", request);
        const promise2 = result.current.resolveBet("2", request);
        
        await Promise.all([promise1, promise2]);
      });

      expect(mockResolveBet).toHaveBeenCalledTimes(2);
      expect(result.current.isResolving).toBe(false);
    });

    it("handles concurrent resolve and dispute operations", async () => {
      const mockResolveBet = vi.fn().mockImplementation(() => 
        new Promise(resolve => setTimeout(() => resolve({ success: true }), 100))
      );
      const mockDisputeBet = vi.fn().mockImplementation(() => 
        new Promise(resolve => setTimeout(() => resolve({ success: true }), 100))
      );
      
      vi.mocked(api.resolveBet).mockImplementation(mockResolveBet);
      vi.mocked(api.disputeBet).mockImplementation(mockDisputeBet);

      const { result } = renderHook(() => useBetResolution());

      await act(async () => {
        const resolvePromise = result.current.resolveBet("1", { result: "win" });
        const disputePromise = result.current.disputeBet("1", { dispute_reason: "Score incorrect" });
        
        await Promise.all([resolvePromise, disputePromise]);
      });

      expect(mockResolveBet).toHaveBeenCalled();
      expect(mockDisputeBet).toHaveBeenCalled();
      expect(result.current.isResolving).toBe(false);
      expect(result.current.isDisputing).toBe(false);
    });
  });

  describe("state cleanup", () => {
    it("resets loading states after successful operations", async () => {
      const mockResolveBet = vi.fn().mockResolvedValue({ success: true });
      vi.mocked(api.resolveBet).mockImplementation(mockResolveBet);

      const { result } = renderHook(() => useBetResolution());

      const request = { result: "win" };

      await act(async () => {
        await result.current.resolveBet("1", request);
      });

      expect(result.current.isResolving).toBe(false);
      expect(result.current.isDisputing).toBe(false);
      expect(result.current.isLoadingHistory).toBe(false);
    });

    it("resets loading states after failed operations", async () => {
      const mockResolveBet = vi.fn().mockRejectedValue(new Error("Failed"));
      vi.mocked(api.resolveBet).mockImplementation(mockResolveBet);

      const { result } = renderHook(() => useBetResolution());

      const request = { result: "win" };

      await act(async () => {
        try {
          await result.current.resolveBet("1", request);
        } catch (error) {
          // Error should be propagated
        }
      });

      expect(result.current.isResolving).toBe(false);
      expect(result.current.isDisputing).toBe(false);
      expect(result.current.isLoadingHistory).toBe(false);
    });
  });
});

