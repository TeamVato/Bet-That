import { describe, afterEach, it, expect, vi } from "vitest";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";

import Dashboard from "../Dashboard";

const mockEdgePayload = {
  edges: [
    {
      type: "Player Prop",
      player: "Mock Player",
      team: "Mock Team",
      opponent: "Rival Team",
      confidence: 0.82,
      expected_value: 0.11,
      reasoning: "Recent usage spike and soft defense matchup.",
    },
  ],
  data_quality: 0.9,
  beta_mode: true,
  disclaimer: "Beta recommendations - verify before betting",
  view_only: true,
  summary: {
    total_edges: 1,
    avg_confidence: 0.82,
    data_freshness: 0.9,
    generated_at: new Date().toISOString(),
  },
};
describe("Dashboard", () => {
  afterEach(() => {
    vi.clearAllTimers();
    vi.restoreAllMocks();
    vi.useRealTimers();
    // Cleanup fetch stub so other tests can provide their own implementation.
    // eslint-disable-next-line @typescript-eslint/no-dynamic-delete
    delete (globalThis as { fetch?: typeof fetch }).fetch;
  });

  it("renders the dashboard surface after a successful fetch", async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockEdgePayload,
    }) as unknown as typeof fetch;

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText("Current Edges")).toBeInTheDocument();
      expect(screen.getByText("Mock Player")).toBeInTheDocument();
    });
  });

  it("shows a retry prompt when the API repeatedly fails", async () => {
    const originalSetTimeout = globalThis.setTimeout.bind(globalThis);
    vi.spyOn(globalThis, "setTimeout").mockImplementation(
      (
        callback: Parameters<typeof setTimeout>[0],
        delay?: Parameters<typeof setTimeout>[1],
        ...args: any[]
      ) => {
        const normalizedDelay =
          typeof delay === "number" && delay >= 1000 ? 0 : (delay ?? 0);
        return originalSetTimeout(callback, normalizedDelay, ...args) as any;
      },
    );
    globalThis.fetch = vi.fn().mockRejectedValue(new Error("network down"));

    render(<Dashboard />);

    await waitFor(() => {
      expect(globalThis.fetch).toHaveBeenCalled();
    });

    await new Promise((resolve) => {
      setTimeout(resolve, 0);
    });

    await waitFor(() => {
      expect(
        screen.getByText(/cannot reach the edges service/i),
      ).toBeInTheDocument();
    });
  });

  it("opens and closes the edge detail modal", async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockEdgePayload,
    }) as unknown as typeof fetch;

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText("Mock Player")).toBeInTheDocument();
    });

    fireEvent.click(screen.getAllByText("Mock Player")[0]);

    await waitFor(() => {
      expect(
        screen.getByText(/Beta mode - Manual verification required/i),
      ).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole("button", { name: /close/i }));

    await waitFor(() => {
      expect(
        screen.queryByText(/Beta mode - Manual verification required/i),
      ).not.toBeInTheDocument();
    });
  });
});
