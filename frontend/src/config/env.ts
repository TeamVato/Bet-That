const MODE = (import.meta.env.MODE ?? "development").toString();
const IS_PRODUCTION = MODE === "production";

type ReadOptions = {
  fallback?: string;
  optional?: boolean;
};

function readEnv(key: string, options: ReadOptions = {}): string {
  const fallback = options.fallback ?? "";
  const source = import.meta.env as Record<
    string,
    string | boolean | undefined
  >;
  const candidate = source[key];
  const defaultValue = IS_PRODUCTION ? "" : fallback;
  const rawValue = (candidate ?? defaultValue).toString().trim();

  if (!rawValue && IS_PRODUCTION && !options.optional) {
    throw new Error(`Missing required environment variable: ${key}`);
  }

  return rawValue || fallback;
}

function toBoolean(value: string, defaultValue: boolean): boolean {
  if (!value) {
    return defaultValue;
  }

  const normalized = value.toLowerCase();
  if (["1", "true", "yes", "on"].includes(normalized)) return true;
  if (["0", "false", "no", "off"].includes(normalized)) return false;
  return defaultValue;
}

export const env = {
  mode: MODE,
  isProduction: IS_PRODUCTION,
  apiBaseUrl: readEnv("VITE_API_BASE_URL", {
    fallback: "http://localhost:8000",
  }),
  betaViewOnly: toBoolean(
    readEnv("VITE_BETA_VIEW_ONLY", { fallback: "true", optional: true }),
    true,
  ),
  betaDisclaimer: readEnv("VITE_BETA_DISCLAIMER", {
    fallback: "Beta recommendations - verify before betting",
    optional: true,
  }),
  betaWarningTitle: readEnv("VITE_BETA_WARNING_TITLE", {
    fallback: "Beta Mode - View Only",
    optional: true,
  }),
  demoUserId: readEnv("VITE_DEMO_USER_ID", { optional: true }),
};

export type FrontendEnv = typeof env;
