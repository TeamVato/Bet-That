const rawViewOnly = (import.meta.env.VITE_BETA_VIEW_ONLY ?? 'true').toString().toLowerCase()
const rawDisclaimer = import.meta.env.VITE_BETA_DISCLAIMER ?? 'Beta recommendations - verify before betting'
const rawBannerTitle = import.meta.env.VITE_BETA_WARNING_TITLE ?? 'Beta Mode - View Only'

const truthy = new Set(['true', '1', 'yes', 'on'])

export const BETA_VIEW_ONLY = truthy.has(rawViewOnly)
export const BETA_DISCLAIMER = rawDisclaimer
export const BETA_WARNING_TITLE = rawBannerTitle
