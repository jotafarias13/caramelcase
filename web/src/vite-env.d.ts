// Keys read at build time. Each is optional: empty or missing means off
// (src/lib/monitoring.ts, deploy/.env.example).
interface ImportMetaEnv {
  readonly VITE_SENTRY_DSN?: string;
  readonly VITE_PLAUSIBLE_DOMAIN?: string;
  readonly VITE_PLAUSIBLE_SCRIPT?: string;
}
