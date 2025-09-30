/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  readonly VITE_BETA_VIEW_ONLY: string
  readonly VITE_BETA_DISCLAIMER: string
  readonly VITE_BETA_WARNING_TITLE: string
  readonly VITE_DEMO_USER_ID: string
  readonly MODE: string
  // Add other environment variables as needed
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
