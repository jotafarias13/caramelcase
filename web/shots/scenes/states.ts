import { apiError, networkFailure } from "../../src/test/mock-api";
import { pending, type Scene } from "../scene";

const devices = ["mobile", "desktop"] as const;

// The system states of the app's frame. The empty state belongs to the
// profile (scenes/profile.ts).
export const states: Scene[] = devices.flatMap((device) => [
  {
    mockup: `v1-state-loading-${device}`,
    path: "/home",
    routes: { "GET /subjects": pending, "GET /subjects/:slug": pending },
  },
  {
    mockup: `v1-state-offline-${device}`,
    path: "/home",
    routes: { "GET /me": networkFailure },
  },
  {
    mockup: `v1-state-error-${device}`,
    path: "/home",
    routes: { "GET /me": apiError(500, "internal_server_error") },
  },
  { mockup: `v1-state-404-${device}`, path: "/pagina-que-nao-existe" },
  {
    mockup: `v1-state-maintenance-${device}`,
    path: "/home",
    routes: { "GET /me": apiError(503, "database_unavailable") },
  },
]);
