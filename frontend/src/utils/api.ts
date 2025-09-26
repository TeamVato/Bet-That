const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const DEMO_USER_ID = import.meta.env.VITE_DEMO_USER_ID || ''

export class ApiError extends Error {
  status: number
  detail: any
  retryAfter?: number
  constructor(message: string, status: number, detail?: any, retryAfter?: number){
    super(message); this.status = status; this.detail = detail; this.retryAfter = retryAfter
  }
}

async function request(path: string, opts: RequestInit = {}, needAuth = false){
  const headers: Record<string,string> = { 'content-type': 'application/json' }
  if (needAuth){
    if (!DEMO_USER_ID) throw new ApiError('Unauthorized: set VITE_DEMO_USER_ID', 401)
    headers['X-User-Id'] = DEMO_USER_ID
  }
  const res = await fetch(`${BASE_URL}${path}`, { ...opts, headers: { ...headers, ...(opts.headers||{}) } })
  if (!res.ok){
    const retry = res.headers.get('Retry-After') ? parseInt(res.headers.get('Retry-After')!, 10) : undefined
    let detail: any = undefined
    try { detail = await res.json() } catch {}
    throw new ApiError(detail?.error || res.statusText, res.status, detail, retry)
  }
  return res.json()
}

export const api = {
  health: () => request('/health'),
  deepHealth: () => request('/healthz/deep'),
  oddsBest: (market?: string) => request(`/odds/best${market ? `?market=${encodeURIComponent(market)}`:''}`),
  register: (payload: { external_id: string, email: string }) => request('/me/register', { method:'POST', body: JSON.stringify(payload)}),
  myBets: () => request('/me/bets', {}, true),
  createBet: (payload: any) => request('/me/bets', { method:'POST', body: JSON.stringify(payload) }, true),
  subscribe: () => request('/digest/subscribe', { method:'POST' }, true)
}
