function resolveProtocol(): 'http' | 'https' {
  if (typeof window !== 'undefined' && window.location?.protocol === 'https:') {
    return 'https'
  }
  return 'http'
}

function resolveHost(): string {
  if (typeof window !== 'undefined' && window.location?.hostname) {
    return window.location.hostname
  }
  return 'localhost'
}

const rawApiBase = (import.meta.env.VITE_API_BASE_URL ?? '').trim()

function resolveApiBase(): string {
  const protocol = resolveProtocol()
  const fallbackHost = resolveHost()

  if (rawApiBase.length > 0 && !rawApiBase.includes('api:')) {
    return rawApiBase
  }

  if (rawApiBase.length > 0 && rawApiBase.includes('api:') && typeof window !== 'undefined') {
    return `${protocol}://${fallbackHost}:8000`
  }

  return `${protocol}://${fallbackHost}:8000`
}

export const API_BASE_URL = resolveApiBase().replace(/\/$/, '')
