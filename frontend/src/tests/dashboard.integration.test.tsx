import { describe, it, vi, afterEach, expect } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import Dashboard from "@/components/Dashboard";

const mockEdgePayload = {
  edges: [
    {
      type: "QB TD Over 0.5",
      player: "Aaron Rodgers",
      team: "Pittsburgh Steelers",
      opponent: "Cleveland Browns",
      confidence: 0.76,
      expected_value: 0.13,
      reasoning: "Mock reasoning",
    },
    {
      type: "WR Receiving Under",
      player: "A.J. Green",
      team: "Cincinnati Bengals",
      opponent: "Baltimore Ravens",
      confidence: 0.7,
      expected_value: 0.09,
    },
  ],
  data_quality: 0.8,
  beta_mode: true,
  disclaimer: "Beta recommendations - verify before betting",
  view_only: true,
  summary: {
    total_edges: 2,
    avg_confidence: 0.73,
    data_freshness: 0.8,
    generated_at: "2025-09-27T07:57:04.829785",
  },
};

function mockFetchResponse(payload: unknown, status = 200) {
  return new Response(JSON.stringify(payload), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

describe("Dashboard integration", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("shows an empty state when no edges are returned", async () => {
    const emptyPayload = {
      ...mockEdgePayload,
      edges: [],
      summary: {
        total_edges: 0,
        avg_confidence: 0,
        data_freshness: 0.5,
        generated_at: "2025-09-27T08:00:00.000Z",
      },
    };

    vi.spyOn(global, "fetch").mockResolvedValueOnce(
      mockFetchResponse(emptyPayload),
    );

    render(<Dashboard />);

    const emptyState = await screen.findAllByText(
      /No active edges are available right now/i,
    );
    expect(emptyState.length).toBeGreaterThan(0);
  });

  it("renders edges from the backend payload and summary stats", async () => {
    vi.spyOn(global, "fetch").mockResolvedValueOnce(
      mockFetchResponse(mockEdgePayload),
    );

    render(<Dashboard />);

    const initialHeadings = await screen.findAllByRole("heading", {
      level: 3,
      name: "Aaron Rodgers",
    });
    expect(initialHeadings.length).toBeGreaterThan(0);
    expect(screen.getByText("A.J. Green")).toBeInTheDocument();
    expect(screen.getAllByText("Total Edges")[0]).toBeInTheDocument();
    expect(screen.getByText("2")).toBeInTheDocument();
    expect(
      screen.getAllByText("Beta recommendations - verify before betting")[0],
    ).toBeInTheDocument();
  });

  it("shows an empty state when no edges are returned", async () => {
    const emptyPayload = {
      ...mockEdgePayload,
      edges: [],
      summary: {
        total_edges: 0,
        avg_confidence: 0,
        data_freshness: 0.5,
        generated_at: "2025-09-27T08:00:00.000Z",
      },
    };

    vi.spyOn(global, "fetch").mockResolvedValueOnce(
      mockFetchResponse(emptyPayload),
    );

    render(<Dashboard />);

    const emptyState = await screen.findAllByText(
      /No active edges are available right now/i,
    );
    expect(emptyState.length).toBeGreaterThan(0);
  });

  it("opens the modal with safety notice when an edge is selected", async () => {
    vi.spyOn(global, "fetch").mockResolvedValueOnce(
      mockFetchResponse(mockEdgePayload),
    );

    render(<Dashboard />);

    const card = await screen.findByText("Aaron Rodgers");
    await userEvent.click(card);

    expect(
      screen.getByText(
        (content, element) =>
          element?.textContent === "Analysis: Mock reasoning",
      ),
    ).toBeInTheDocument();
    expect(
      screen.getByText(
        /Beta mode - Manual verification required before betting/i,
      ),
    ).toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: /close/i }));
    await waitFor(() =>
      expect(
        screen.queryByText("Analysis: Mock reasoning"),
      ).not.toBeInTheDocument(),
    );
  });

  it("shows an empty state when no edges are returned", async () => {
    const emptyPayload = {
      ...mockEdgePayload,
      edges: [],
      summary: {
        total_edges: 0,
        avg_confidence: 0,
        data_freshness: 0.5,
        generated_at: "2025-09-27T08:00:00.000Z",
      },
    };

    vi.spyOn(global, "fetch").mockResolvedValueOnce(
      mockFetchResponse(emptyPayload),
    );

    render(<Dashboard />);

    const emptyState = await screen.findAllByText(
      /No active edges are available right now/i,
    );
    expect(emptyState.length).toBeGreaterThan(0);
  });

  it("refreshes the edge list when the refresh button is pressed", async () => {
    const updatedPayload = {
      ...mockEdgePayload,
      edges: [
        {
          ...mockEdgePayload.edges[0],
          player: "Updated Player",
          confidence: 0.82,
        },
      ],
      summary: {
        ...mockEdgePayload.summary,
        total_edges: 1,
        avg_confidence: 0.82,
      },
    };

    const fetchMock = vi.spyOn(global, "fetch");
    fetchMock.mockImplementation(() =>
      Promise.resolve(mockFetchResponse(mockEdgePayload)),
    );

    render(<Dashboard />);

    const initialHeadings = await screen.findAllByRole("heading", {
      level: 3,
      name: "Aaron Rodgers",
    });
    expect(initialHeadings.length).toBeGreaterThan(0);

    fetchMock.mockImplementation(() =>
      Promise.resolve(mockFetchResponse(updatedPayload)),
    );

    const refreshButtons = screen.getAllByRole("button", { name: /refresh/i });
    await userEvent.click(refreshButtons[0]);

    const updatedHeadings = await screen.findAllByRole("heading", {
      level: 3,
      name: "Updated Player",
    });
    expect(updatedHeadings.length).toBeGreaterThan(0);
    expect(fetchMock).toHaveBeenCalled();
  });
});
