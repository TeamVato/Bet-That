import { BETA_VIEW_ONLY } from "@/config/beta";
import { API_BASE_URL } from "@/config/api";
import { env } from "@/config/env";

const DEMO_USER_ID = env.demoUserId;

export class ApiError extends Error {
  status: number;
  detail: any;
  retryAfter?: number;
  constructor(
    message: string,
    status: number,
    detail?: any,
    retryAfter?: number,
  ) {
    super(message);
    this.status = status;
    this.detail = detail;
    this.retryAfter = retryAfter;
  }
}

async function request(path: string, opts: RequestInit = {}, needAuth = false) {
  const headers: Record<string, string> = {
    "content-type": "application/json",
  };
  if (needAuth) {
    if (!DEMO_USER_ID)
      throw new ApiError("Unauthorized: set VITE_DEMO_USER_ID", 401);
    headers["X-User-Id"] = DEMO_USER_ID;
  }
  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...opts,
    headers: { ...headers, ...(opts.headers || {}) },
  });
  if (!res.ok) {
    const retry = res.headers.get("Retry-After")
      ? parseInt(res.headers.get("Retry-After")!, 10)
      : undefined;
    let detail: any = undefined;
    try {
      detail = await res.json();
    } catch {}
    throw new ApiError(
      detail?.error || res.statusText,
      res.status,
      detail,
      retry,
    );
  }
  return res.json();
}

export const api = {
  health: () => request("/health"),
  deepHealth: () => request("/healthz/deep"),
  oddsBest: (market?: string) =>
    request(
      `/odds/best${market ? `?market=${encodeURIComponent(market)}` : ""}`,
    ),
  register: (payload: { external_id: string; email: string }) =>
    request("/me/register", { method: "POST", body: JSON.stringify(payload) }),
  myBets: () => request("/me/bets", {}, true),
  createBet: (payload: any) => {
    if (BETA_VIEW_ONLY) {
      throw new ApiError("Bet creation disabled in beta view-only mode.", 403, {
        reason: "view_only",
      });
    }
    return request(
      "/me/bets",
      { method: "POST", body: JSON.stringify(payload) },
      true,
    );
  },
  subscribe: () => request("/digest/subscribe", { method: "POST" }, true),
};
