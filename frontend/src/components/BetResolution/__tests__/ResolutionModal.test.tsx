import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ResolutionModal } from "../ResolutionModal";

// Mock the ResolutionForm component
vi.mock("../ResolutionForm", () => ({
  ResolutionForm: ({ onSuccess, onCancel }: any) => (
    <div data-testid="resolution-form">
      <button onClick={onSuccess}>Mock Resolve</button>
      <button onClick={onCancel}>Mock Cancel</button>
    </div>
  ),
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

describe("ResolutionModal", () => {
  const mockOnClose = vi.fn();
  const mockOnSuccess = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders modal when open", () => {
    render(
      <ResolutionModal
        bet={mockBet}
        isOpen={true}
        onClose={mockOnClose}
        onSuccess={mockOnSuccess}
      />
    );

    expect(screen.getByTestId("resolution-form")).toBeInTheDocument();
    expect(screen.getByText("Resolve Bet")).toBeInTheDocument();
  });

  it("does not render modal when closed", () => {
    render(
      <ResolutionModal
        bet={mockBet}
        isOpen={false}
        onClose={mockOnClose}
        onSuccess={mockOnSuccess}
      />
    );

    expect(screen.queryByTestId("resolution-form")).not.toBeInTheDocument();
  });

  it("calls onClose when close button is clicked", async () => {
    const user = userEvent.setup();
    
    render(
      <ResolutionModal
        bet={mockBet}
        isOpen={true}
        onClose={mockOnClose}
        onSuccess={mockOnSuccess}
      />
    );

    const closeButton = screen.getByRole("button", { name: /close/i });
    await user.click(closeButton);

    expect(mockOnClose).toHaveBeenCalled();
  });

  it("calls onClose when clicking outside modal", async () => {
    const user = userEvent.setup();
    
    render(
      <ResolutionModal
        bet={mockBet}
        isOpen={true}
        onClose={mockOnClose}
        onSuccess={mockOnSuccess}
      />
    );

    const backdrop = screen.getByTestId("modal-backdrop");
    await user.click(backdrop);

    expect(mockOnClose).toHaveBeenCalled();
  });

  it("does not close when clicking inside modal content", async () => {
    const user = userEvent.setup();
    
    render(
      <ResolutionModal
        bet={mockBet}
        isOpen={true}
        onClose={mockOnClose}
        onSuccess={mockOnSuccess}
      />
    );

    const modalContent = screen.getByTestId("modal-content");
    await user.click(modalContent);

    expect(mockOnClose).not.toHaveBeenCalled();
  });

  it("calls onClose when form cancel is triggered", async () => {
    const user = userEvent.setup();
    
    render(
      <ResolutionModal
        bet={mockBet}
        isOpen={true}
        onClose={mockOnClose}
        onSuccess={mockOnSuccess}
      />
    );

    const cancelButton = screen.getByRole("button", { name: "Mock Cancel" });
    await user.click(cancelButton);

    expect(mockOnClose).toHaveBeenCalled();
  });

  it("calls onSuccess and onClose when form success is triggered", async () => {
    const user = userEvent.setup();
    
    render(
      <ResolutionModal
        bet={mockBet}
        isOpen={true}
        onClose={mockOnClose}
        onSuccess={mockOnSuccess}
      />
    );

    const resolveButton = screen.getByRole("button", { name: "Mock Resolve" });
    await user.click(resolveButton);

    expect(mockOnSuccess).toHaveBeenCalled();
    expect(mockOnClose).toHaveBeenCalled();
  });

  it("closes modal on Escape key press", async () => {
    const user = userEvent.setup();
    
    render(
      <ResolutionModal
        bet={mockBet}
        isOpen={true}
        onClose={mockOnClose}
        onSuccess={mockOnSuccess}
      />
    );

    await user.keyboard("{Escape}");

    expect(mockOnClose).toHaveBeenCalled();
  });

  it("traps focus within modal", async () => {
    const user = userEvent.setup();
    
    render(
      <ResolutionModal
        bet={mockBet}
        isOpen={true}
        onClose={mockOnClose}
        onSuccess={mockOnSuccess}
      />
    );

    // Focus should be on the close button initially
    const closeButton = screen.getByRole("button", { name: /close/i });
    expect(document.activeElement).toBe(closeButton);

    // Tab should cycle through modal elements
    await user.tab();
    expect(document.activeElement).toBe(screen.getByRole("button", { name: "Mock Resolve" }));

    await user.tab();
    expect(document.activeElement).toBe(screen.getByRole("button", { name: "Mock Cancel" }));

    // Tab should cycle back to first element
    await user.tab();
    expect(document.activeElement).toBe(closeButton);
  });

  it("displays bet information correctly", () => {
    render(
      <ResolutionModal
        bet={mockBet}
        isOpen={true}
        onClose={mockOnClose}
        onSuccess={mockOnSuccess}
      />
    );

    expect(screen.getByText("Resolve Bet")).toBeInTheDocument();
    // The bet information should be passed to ResolutionForm
    expect(screen.getByTestId("resolution-form")).toBeInTheDocument();
  });

  it("handles missing bet gracefully", () => {
    render(
      <ResolutionModal
        bet={null}
        isOpen={true}
        onClose={mockOnClose}
        onSuccess={mockOnSuccess}
      />
    );

    expect(screen.getByText("No bet selected")).toBeInTheDocument();
  });

  it("applies correct CSS classes for styling", () => {
    render(
      <ResolutionModal
        bet={mockBet}
        isOpen={true}
        onClose={mockOnClose}
        onSuccess={mockOnSuccess}
      />
    );

    const backdrop = screen.getByTestId("modal-backdrop");
    const content = screen.getByTestId("modal-content");

    expect(backdrop).toHaveClass("fixed", "inset-0", "z-50", "flex", "items-center", "justify-center", "bg-black", "bg-opacity-50");
    expect(content).toHaveClass("bg-white", "rounded-lg", "shadow-xl", "max-w-md", "w-full", "mx-4");
  });

  it("prevents body scroll when modal is open", () => {
    // Mock document.body.style
    const originalOverflow = document.body.style.overflow;
    
    render(
      <ResolutionModal
        bet={mockBet}
        isOpen={true}
        onClose={mockOnClose}
        onSuccess={mockOnSuccess}
      />
    );

    expect(document.body.style.overflow).toBe("hidden");

    // Cleanup
    document.body.style.overflow = originalOverflow;
  });

  it("restores body scroll when modal is closed", () => {
    const originalOverflow = document.body.style.overflow;
    
    const { rerender } = render(
      <ResolutionModal
        bet={mockBet}
        isOpen={true}
        onClose={mockOnClose}
        onSuccess={mockOnSuccess}
      />
    );

    expect(document.body.style.overflow).toBe("hidden");

    // Close the modal
    rerender(
      <ResolutionModal
        bet={mockBet}
        isOpen={false}
        onClose={mockOnClose}
        onSuccess={mockOnSuccess}
      />
    );

    expect(document.body.style.overflow).toBe("");

    // Cleanup
    document.body.style.overflow = originalOverflow;
  });
});

