// Error tracking (Better Stack, through the Sentry SDK) and external
// analytics (Plausible). Each is off unless its key was set when the app
// was built: VITE_BETTER_STACK_ERRORS_DSN and VITE_PLAUSIBLE_DOMAIN
// (deploy/.env.example). While a key is empty, the build holds none of that
// service's code and nothing is sent to it.
import type { Breadcrumb, ErrorEvent } from "@sentry/browser";

const PLAUSIBLE_SCRIPT = "https://plausible.io/js/script.js";

/** Starts each service whose key is set. */
export function startMonitoring(): void {
  const dsn = import.meta.env.VITE_BETTER_STACK_ERRORS_DSN;
  if (dsn) void startErrorTracking(dsn);

  const domain = import.meta.env.VITE_PLAUSIBLE_DOMAIN;
  if (domain) {
    addAnalyticsScript(
      domain,
      import.meta.env.VITE_PLAUSIBLE_SCRIPT || PLAUSIBLE_SCRIPT,
    );
  }
}

async function startErrorTracking(dsn: string): Promise<void> {
  try {
    const Sentry = await import("@sentry/browser");
    Sentry.init({
      dsn,
      environment: import.meta.env.MODE,
      // Nothing that identifies the student (LGPD): no user, cookies,
      // headers, bodies or query strings.
      dataCollection: {
        userInfo: false,
        cookies: false,
        httpHeaders: false,
        httpBodies: [],
        urlQueryParams: false,
      },
      // And, whatever the SDK does, no query string in an address.
      beforeSend: withoutQueryInEvent,
      beforeBreadcrumb: withoutQueryInBreadcrumb,
    });
  } catch {
    // The app works the same without error tracking.
  }
}

/** Plausible counts page views without cookies; it follows the router. */
function addAnalyticsScript(domain: string, src: string): void {
  const script = document.createElement("script");
  script.defer = true;
  script.dataset.domain = domain;
  script.src = src;
  document.head.append(script);
}

/**
 * An address without its query and fragment. A sign-in link carries its
 * token in the query (/auth/callback?token=...), which must not leave.
 */
export function withoutQuery(url: string): string {
  return url.split(/[?#]/)[0];
}

export function withoutQueryInEvent(event: ErrorEvent): ErrorEvent {
  if (event.request?.url) event.request.url = withoutQuery(event.request.url);
  if (event.request) delete event.request.query_string;
  return event;
}

export function withoutQueryInBreadcrumb(breadcrumb: Breadcrumb): Breadcrumb {
  const data = breadcrumb.data;
  if (!data) return breadcrumb;
  for (const key of ["url", "from", "to"]) {
    if (typeof data[key] === "string") data[key] = withoutQuery(data[key]);
  }
  return breadcrumb;
}
