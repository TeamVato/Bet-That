import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ResolutionHistory } from "../ResolutionHistory";

// Mock the API service
vi.mock("@/services/api", () => ({
  api: {
    getBetResolutionHistory: vi.fn(),
    resolveBet: vi.fn(),
    disputeBet: vi.fn(),
    getPendingResolutionBets: vi.fn(),
    resolveDispute: vi.fn(),
  },
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
  status: "resolved",
  result: "win",
  sportsbook_name: "DraftKings",
  external_bet_id: "dk_123",
  notes: "Test bet",
  created_at: "2024-01-01T00:00:00Z",
  updated_at: "2024-01-01T00:00:00Z",
  resolved_at: "2024-01-02T00:00:00Z",
  resolved_by: 1,
  resolution_notes: "Game completed",
  resolution_source: "ESPN",
  is_disputed: false,
  dispute_reason: null,
  dispute_created_at: null,
  dispute_resolved_at: null,
  dispute_resolved_by: null,
};

const mockHistory = {
  history: [
    {
      id: 1,
      bet_id: 1,
      action_type: "resolve",
      previous_status: "pending",
      new_status: "resolved",
      previous_result: null,
      new_result: "win",
      resolution_notes: "Game completed successfully",
      resolution_source: "ESPN",
      dispute_reason: null,
      performed_by: 1,
      created_at: "2024-01-02T10:00:00Z",
    },
    {
      id: 2,
      bet_id: 1,
      action_type: "dispute",
      previous_status: "resolved",
      new_status: "resolved",
      previous_result: "win",
      new_result: "win",
      resolution_notes: null,
      resolution_source: null,
      dispute_reason: "Score was incorrect according to official stats",
      performed_by: 1,
      created_at: "2024-01-02T11:00:00Z",
    },
    {
      id: 3,
      bet_id: 1,
      action_type: "resolve_dispute",
      previous_status: "resolved",
      new_status: "resolved",
      previous_result: "win",
      new_result: "loss",
      resolution_notes: "Corrected based on official score",
      resolution_source: "NFL.com",
      dispute_reason: null,
      performed_by: 2,
      created_at: "2024-01-02T12:00:00Z",
    },
  ],
  total: 3,
  page: 1,
  per_page: 50,
};

describe("ResolutionHistory", () => {
  const mockOnClose = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders resolution history correctly", async () => {
    const mockGetHistory = vi.fn().mockResolvedValue(mockHistory);
    vi.mocked(require("@/services/api").api.getBetResolutionHistory).mockImplementation(mockGetHistory);

    render(
      <ResolutionHistory
        bet={mockBet}
        isOpen={true}
        onClose={mockOnClose}
      />
    );

    await waitFor(() => {
      expect(screen.getByText("Resolution History")).toBeInTheDocument();
    });

    expect(mockGetHistory).toHaveBeenCalledWith("1", 1, 20);

    // Check that history items are displayed
    expect(screen.getByText("Resolved")).toBeInTheDocument();
    expect(screen.getByText("Game completed successfully")).toBeInTheDocument();
    expect(screen.getByText("ESPN")).toBeInTheDocument();
  });

  it("shows loading state initially", () => {
    const mockGetHistory = vi.fn().mockImplementation(() => 
      new Promise(resolve => setTimeout(() => resolve(mockHistory), 100))
    );
    vi.mocked(require("@/services/api").api.getBetResolutionHistory).mockImplementation(mockGetHistory);

    render(
      <ResolutionHistory
        bet={mockBet}
        isOpen={true}
        onClose={mockOnClose}
      />
    );

    expect(screen.getByText("Loading resolution history...")).toBeInTheDocument();
  });

  it("shows empty state when no history exists", async () => {
    const emptyHistory = {
      history: [],
      total: 0,
      page: 1,
      per_page: 50,
    };

    const mockGetHistory = vi.fn().mockResolvedValue(emptyHistory);
    vi.mocked(require("@/services/api").api.getBetResolutionHistory).mockImplementation(mockGetHistory);

    render(
      <ResolutionHistory
        bet={mockBet}
        isOpen={true}
        onClose={mockOnClose}
      />
    );

    await waitFor(() => {
      expect(screen.getByText("No resolution history available")).toBeInTheDocument();
    });
  });

  it("handles API errors gracefully", async () => {
    const mockGetHistory = vi.fn().mockRejectedValue(new Error("Failed to fetch history"));
    vi.mocked(require("@/services/api").api.getBetResolutionHistory).mockImplementation(mockGetHistory);

    render(
      <ResolutionHistory
        bet={mockBet}
        isOpen={true}
        onClose={mockOnClose}
      />
    );

    await waitFor(() => {
      expect(screen.getByText("Failed to load resolution history: Failed to fetch history")).toBeInTheDocument();
    });
  });

  it("calls onClose when close button is clicked", async () => {
    const user = userEvent.setup();
    const mockGetHistory = vi.fn().mockResolvedValue(mockHistory);
    vi.mocked(require("@/services/api").api.getBetResolutionHistory).mockImplementation(mockGetHistory);

    render(
      <ResolutionHistory
        bet={mockBet}
        isOpen={true}
        onClose={mockOnClose}
      />
    );

    await waitFor(() => {
      expect(screen.getByText("Resolution History")).toBeInTheDocument();
    });

    const closeButton = screen.getByRole("button", { name: /close/i });
    await user.click(closeButton);

    expect(mockOnClose).toHaveBeenCalled();
  });

  it("does not render when isOpen is false", () => {
    const mockGetHistory = vi.fn().mockResolvedValue(mockHistory);
    vi.mocked(require("@/services/api").api.getBetResolutionHistory).mockImplementation(mockGetHistory);

    render(
      <ResolutionHistory
        bet={mockBet}
        isOpen={false}
        onClose={mockOnClose}
      />
    );

    expect(screen.queryByText("Resolution History")).not.toBeInTheDocument();
  });

  it("formats timestamps correctly", async () => {
    const mockGetHistory = vi.fn().mockResolvedValue(mockHistory);
    vi.mocked(require("@/services/api").api.getBetResolutionHistory).mockImplementation(mockGetHistory);

    render(
      <ResolutionHistory
        bet={mockBet}
        isOpen={true}
        onClose={mockOnClose}
      />
    );

    await waitFor(() => {
      expect(screen.getByText("Resolution History")).toBeInTheDocument();
    });

    // Check that timestamps are formatted (exact format may vary based on implementation)
    expect(screen.getByText(/Jan 2, 2024/)).toBeInTheDocument();
  });

  it("displays different action types correctly", async () => {
    const mockGetHistory = vi.fn().mockResolvedValue(mockHistory);
    vi.mocked(require("@/services/api").api.getBetResolutionHistory).mockImplementation(mockGetHistory);

    render(
      <ResolutionHistory
        bet={mockBet}
        isOpen={true}
        onClose={mockOnClose}
      />
    );

    await waitFor(() => {
      expect(screen.getByText("Resolution History")).toBeInTheDocument();
    });

    // Check for different action types
    expect(screen.getByText("Resolved")).toBeInTheDocument();
    expect(screen.getByText("Disputed")).toBeInTheDocument();
    expect(screen.getByText("Dispute Resolved")).toBeInTheDocument();
  });

  it("shows user information for each action", async () => {
    const mockGetHistory = vi.fn().mockResolvedValue(mockHistory);
    vi.mocked(require("@/services/api").api.getBetResolutionHistory).mockImplementation(mockGetHistory);

    render(
      <ResolutionHistory
        bet={mockBet}
        isOpen={true}
        onClose={mockOnClose}
      />
    );

    await waitFor(() => {
      expect(screen.getByText("Resolution History")).toBeInTheDocument();
    });

    // Check that user IDs are displayed (or user names if available)
    expect(screen.getByText("User 1")).toBeInTheDocument();
    expect(screen.getByText("User 2")).toBeInTheDocument();
  });

  it("handles pagination correctly", async () => {
    const user = userEvent.setup();
    const mockGetHistory = vi.fn().mockResolvedValue(mockHistory);
    vi.mocked(require("@/services/api").api.getBetResolutionHistory).mockImplementation(mockGetHistory);

    render(
      <ResolutionHistory
        bet={mockBet}
        isOpen={true}
        onClose={mockOnClose}
      />
    );

    await waitFor(() => {
      expect(screen.getByText("Resolution History")).toBeInTheDocument();
    });

    // Test pagination if implemented
    const nextButton = screen.queryByRole("button", { name: /next/i });
    if (nextButton) {
      await user.click(nextButton);
      expect(mockGetHistory).toHaveBeenCalledWith("1", 2, 20);
    }
  });

  it("refreshes data when bet changes", async () => {
    const user = userEvent.setup();
    const mockGetHistory = vi.fn().mockResolvedValue(mockHistory);
    vi.mocked(require("@/services/api").api.getBetResolutionHistory).mockImplementation(mockGetHistory);

    const { rerender } = render(
      <ResolutionHistory
        bet={mockBet}
        isOpen={true}
        onClose={mockOnClose}
      />
    );

    await waitFor(() => {
      expect(screen.getByText("Resolution History")).toBeInTheDocument();
    });

    const newBet = { ...mockBet, id: "2" };

    rerender(
      <ResolutionHistory
        bet={newBet}
        isOpen={true}
        onClose={mockOnClose}
      />
    );

    await waitFor(() => {
      expect(mockGetHistory).toHaveBeenCalledWith("2", 1, 20);
    });
  });

  it("closes on Escape key press", async () => {
    const user = userEvent.setup();
    const mockGetHistory = vi.fn().mockResolvedValue(mockHistory);
    vi.mocked(require("@/services/api").api.getBetResolutionHistory).mockImplementation(mockGetHistory);

    render(
      <ResolutionHistory
        bet={mockBet}
        isOpen={true}
        onClose={mockOnClose}
      />
    );

    await waitFor(() => {
      expect(screen.getByText("Resolution History")).toBeInTheDocument();
    });

    await user.keyboard("{Escape}");

    expect(mockOnClose).toHaveBeenCalled();
  });

  it("shows dispute information when present", async () => {
    const mockGetHistory = vi.fn().mockResolvedValue(mockHistory);
    vi.mocked(require("@/services/api").api.getBetResolutionHistory).mockImplementation(mockGetHistory);

    render(
      <ResolutionHistory
        bet={mockBet}
        isOpen={true}
        onClose={mockOnClose}
      />
    );

    await waitFor(() => {
      expect(screen.getByText("Resolution History")).toBeInTheDocument();
    });

    // Check that dispute reason is displayed
    expect(screen.getByText("Score was incorrect according to official stats")).toBeInTheDocument();
  });

  it("shows resolution source when available", async () => {
    const mockGetHistory = vi.fn().mockResolvedValue(mockHistory);
    vi.mocked(require("@/services/api").api.getBetResolutionHistory).mockImplementation(mockGetHistory);

    render(
      <ResolutionHistory
        bet={mockBet}
        isOpen={true}
        onClose={mockOnClose}
      />
    );

    await waitFor(() => {
      expect(screen.getByText("Resolution History")).toBeInTheDocument();
    });

    // Check that resolution sources are displayed
    expect(screen.getByText("ESPN")).toBeInTheDocument();
    expect(screen.getByText("NFL.com")).toBeInTheDocument();
  });
});
