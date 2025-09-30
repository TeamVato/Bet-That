import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ResolutionForm } from "../ResolutionForm";

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

// Mock the bet resolution hook
vi.mock("@/hooks/useBetResolution", () => ({
  useBetResolution: () => ({
    resolveBet: vi.fn(),
    disputeBet: vi.fn(),
    isResolving: false,
    isDisputing: false,
  }),
}));

const mockBet = {
  id: "1",
  event_id: "game_123",
  market_type: "spread",
  market_description: "Point Spread",
  selection: "Home Team",
  line: -3.5,
  side: "home",
  stake: 100,
  odds_american: -110,
  odds_decimal: 1.91,
  potential_return: 190.91,
  status: "pending",
  result: null,
  sportsbook_name: "DraftKings",
  external_bet_id: "dk_123",
  notes: "Test bet",
  created_at: "2024-01-01T00:00:00Z",
  updated_at: "2024-01-01T00:00:00Z",
  resolved_at: null,
  resolved_by: null,
  resolution_notes: null,
  resolution_source: null,
  is_disputed: false,
  dispute_reason: null,
  dispute_created_at: null,
  dispute_resolved_at: null,
  dispute_resolved_by: null,
};

describe("ResolutionForm", () => {
  const mockOnSuccess = vi.fn();
  const mockOnCancel = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders resolution form correctly", () => {
    render(
      <ResolutionForm
        bet={mockBet}
        onSuccess={mockOnSuccess}
        onCancel={mockOnCancel}
      />
    );

    expect(screen.getByText("Resolve Bet")).toBeInTheDocument();
    expect(screen.getByText("Home Team -3.5 @ DraftKings")).toBeInTheDocument();
    expect(screen.getByText("$100.00 stake")).toBeInTheDocument();
    expect(screen.getByLabelText("Result")).toBeInTheDocument();
    expect(screen.getByLabelText("Resolution Notes")).toBeInTheDocument();
    expect(screen.getByLabelText("Resolution Source")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Resolve Bet" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Cancel" })).toBeInTheDocument();
  });

  it("validates required fields", async () => {
    const user = userEvent.setup();
    
    render(
      <ResolutionForm
        bet={mockBet}
        onSuccess={mockOnSuccess}
        onCancel={mockOnCancel}
      />
    );

    const resolveButton = screen.getByRole("button", { name: "Resolve Bet" });
    await user.click(resolveButton);

    await waitFor(() => {
      expect(screen.getByText("Please select a result")).toBeInTheDocument();
    });

    expect(mockOnSuccess).not.toHaveBeenCalled();
  });

  it("submits resolution with valid data", async () => {
    const user = userEvent.setup();
    const mockResolveBet = vi.fn().mockResolvedValue({ success: true });

    // Mock the hook to return our mock function
    vi.mocked(require("@/hooks/useBetResolution").useBetResolution).mockReturnValue({
      resolveBet: mockResolveBet,
      disputeBet: vi.fn(),
      isResolving: false,
      isDisputing: false,
    });

    render(
      <ResolutionForm
        bet={mockBet}
        onSuccess={mockOnSuccess}
        onCancel={mockOnCancel}
      />
    );

    // Fill out the form
    await user.selectOptions(screen.getByLabelText("Result"), "win");
    await user.type(screen.getByLabelText("Resolution Notes"), "Game completed successfully");
    await user.type(screen.getByLabelText("Resolution Source"), "ESPN");

    // Submit the form
    const resolveButton = screen.getByRole("button", { name: "Resolve Bet" });
    await user.click(resolveButton);

    await waitFor(() => {
      expect(mockResolveBet).toHaveBeenCalledWith("1", {
        result: "win",
        resolution_notes: "Game completed successfully",
        resolution_source: "ESPN",
      });
      expect(mockOnSuccess).toHaveBeenCalled();
    });
  });

  it("handles resolution errors", async () => {
    const user = userEvent.setup();
    const mockResolveBet = vi.fn().mockRejectedValue(new Error("Resolution failed"));

    vi.mocked(require("@/hooks/useBetResolution").useBetResolution).mockReturnValue({
      resolveBet: mockResolveBet,
      disputeBet: vi.fn(),
      isResolving: false,
      isDisputing: false,
    });

    render(
      <ResolutionForm
        bet={mockBet}
        onSuccess={mockOnSuccess}
        onCancel={mockOnCancel}
      />
    );

    await user.selectOptions(screen.getByLabelText("Result"), "win");
    await user.type(screen.getByLabelText("Resolution Notes"), "Game completed");

    const resolveButton = screen.getByRole("button", { name: "Resolve Bet" });
    await user.click(resolveButton);

    await waitFor(() => {
      expect(screen.getByText("Failed to resolve bet: Resolution failed")).toBeInTheDocument();
    });

    expect(mockOnSuccess).not.toHaveBeenCalled();
  });

  it("shows loading state during resolution", async () => {
    const user = userEvent.setup();
    const mockResolveBet = vi.fn().mockImplementation(() => 
      new Promise(resolve => setTimeout(resolve, 100))
    );

    vi.mocked(require("@/hooks/useBetResolution").useBetResolution).mockReturnValue({
      resolveBet: mockResolveBet,
      disputeBet: vi.fn(),
      isResolving: true,
      isDisputing: false,
    });

    render(
      <ResolutionForm
        bet={mockBet}
        onSuccess={mockOnSuccess}
        onCancel={mockOnCancel}
      />
    );

    await user.selectOptions(screen.getByLabelText("Result"), "win");

    const resolveButton = screen.getByRole("button", { name: "Resolve Bet" });
    await user.click(resolveButton);

    expect(resolveButton).toBeDisabled();
    expect(screen.getByText("Resolving...")).toBeInTheDocument();
  });

  it("calls onCancel when cancel button is clicked", async () => {
    const user = userEvent.setup();
    
    render(
      <ResolutionForm
        bet={mockBet}
        onSuccess={mockOnSuccess}
        onCancel={mockOnCancel}
      />
    );

    const cancelButton = screen.getByRole("button", { name: "Cancel" });
    await user.click(cancelButton);

    expect(mockOnCancel).toHaveBeenCalled();
  });

  it("disables form when bet is already resolved", () => {
    const resolvedBet = {
      ...mockBet,
      status: "resolved",
      result: "win",
      resolved_at: "2024-01-02T00:00:00Z",
    };

    render(
      <ResolutionForm
        bet={resolvedBet}
        onSuccess={mockOnSuccess}
        onCancel={mockOnCancel}
      />
    );

    expect(screen.getByText("This bet has already been resolved")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Resolve Bet" })).toBeDisabled();
  });

  it("shows dispute section for resolved bets", () => {
    const resolvedBet = {
      ...mockBet,
      status: "resolved",
      result: "win",
      resolved_at: "2024-01-02T00:00:00Z",
    };

    render(
      <ResolutionForm
        bet={resolvedBet}
        onSuccess={mockOnSuccess}
        onCancel={mockOnCancel}
      />
    );

    expect(screen.getByText("Dispute Resolution")).toBeInTheDocument();
    expect(screen.getByLabelText("Dispute Reason")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Dispute Resolution" })).toBeInTheDocument();
  });

  it("submits dispute with valid reason", async () => {
    const user = userEvent.setup();
    const mockDisputeBet = vi.fn().mockResolvedValue({ success: true });
    const resolvedBet = {
      ...mockBet,
      status: "resolved",
      result: "win",
      resolved_at: "2024-01-02T00:00:00Z",
    };

    vi.mocked(require("@/hooks/useBetResolution").useBetResolution).mockReturnValue({
      resolveBet: vi.fn(),
      disputeBet: mockDisputeBet,
      isResolving: false,
      isDisputing: false,
    });

    render(
      <ResolutionForm
        bet={resolvedBet}
        onSuccess={mockOnSuccess}
        onCancel={mockOnCancel}
      />
    );

    await user.type(screen.getByLabelText("Dispute Reason"), "Score was incorrect according to official stats");

    const disputeButton = screen.getByRole("button", { name: "Dispute Resolution" });
    await user.click(disputeButton);

    await waitFor(() => {
      expect(mockDisputeBet).toHaveBeenCalledWith("1", {
        dispute_reason: "Score was incorrect according to official stats",
      });
      expect(mockOnSuccess).toHaveBeenCalled();
    });
  });

  it("validates dispute reason length", async () => {
    const user = userEvent.setup();
    const resolvedBet = {
      ...mockBet,
      status: "resolved",
      result: "win",
      resolved_at: "2024-01-02T00:00:00Z",
    };

    render(
      <ResolutionForm
        bet={resolvedBet}
        onSuccess={mockOnSuccess}
        onCancel={mockOnCancel}
      />
    );

    await user.type(screen.getByLabelText("Dispute Reason"), "Bad");

    const disputeButton = screen.getByRole("button", { name: "Dispute Resolution" });
    await user.click(disputeButton);

    await waitFor(() => {
      expect(screen.getByText("Dispute reason must be at least 10 characters")).toBeInTheDocument();
    });
  });

  it("shows loading state during dispute", async () => {
    const user = userEvent.setup();
    const resolvedBet = {
      ...mockBet,
      status: "resolved",
      result: "win",
      resolved_at: "2024-01-02T00:00:00Z",
    };

    vi.mocked(require("@/hooks/useBetResolution").useBetResolution).mockReturnValue({
      resolveBet: vi.fn(),
      disputeBet: vi.fn(),
      isResolving: false,
      isDisputing: true,
    });

    render(
      <ResolutionForm
        bet={resolvedBet}
        onSuccess={mockOnSuccess}
        onCancel={mockOnCancel}
      />
    );

    await user.type(screen.getByLabelText("Dispute Reason"), "Score was incorrect according to official stats");

    const disputeButton = screen.getByRole("button", { name: "Dispute Resolution" });
    await user.click(disputeButton);

    expect(disputeButton).toBeDisabled();
    expect(screen.getByText("Disputing...")).toBeInTheDocument();
  });

  it("handles dispute errors", async () => {
    const user = userEvent.setup();
    const mockDisputeBet = vi.fn().mockRejectedValue(new Error("Dispute failed"));
    const resolvedBet = {
      ...mockBet,
      status: "resolved",
      result: "win",
      resolved_at: "2024-01-02T00:00:00Z",
    };

    vi.mocked(require("@/hooks/useBetResolution").useBetResolution).mockReturnValue({
      resolveBet: vi.fn(),
      disputeBet: mockDisputeBet,
      isResolving: false,
      isDisputing: false,
    });

    render(
      <ResolutionForm
        bet={resolvedBet}
        onSuccess={mockOnSuccess}
        onCancel={mockOnCancel}
      />
    );

    await user.type(screen.getByLabelText("Dispute Reason"), "Score was incorrect according to official stats");

    const disputeButton = screen.getByRole("button", { name: "Dispute Resolution" });
    await user.click(disputeButton);

    await waitFor(() => {
      expect(screen.getByText("Failed to dispute bet: Dispute failed")).toBeInTheDocument();
    });

    expect(mockOnSuccess).not.toHaveBeenCalled();
  });
});
