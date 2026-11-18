import createClient, { type Middleware } from "openapi-fetch";
import type { paths } from "./schema";

/**
 * Every failed request ends as one of these. `status` is 0 when the request
 * never reached the server (offline, DNS, the API container is down).
 */
export class ApiError extends Error {
  status: number;
  code: string;

  constructor(status: number, code: string, message: string) {
    super(message || code);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
  }
}

/** Which full-screen state an error is shown as. */
export type ErrorKind = "offline" | "maintenance" | "not_found" | "error";

export function errorKind(error: unknown): ErrorKind {
  if (!(error instanceof ApiError)) return "error";
  if (error.status === 0) return "offline";
  if ([502, 503, 504].includes(error.status)) return "maintenance";
  if (error.status === 404) return "not_found";
  return "error";
}

/**
 * Too many requests in a row (429): the API's rate limits on sign-in,
 * answers and reports. The request can be made again a little later.
 */
export function isRateLimited(error: unknown): boolean {
  return error instanceof ApiError && error.status === 429;
}

// The API refuses a state-changing request without this header (CSRF);
// a browser never adds it to a cross-site form post.
const csrfHeader: Middleware = {
  onRequest({ request }) {
    request.headers.set("X-Requested-With", "caramelcase-web");
    return request;
  },
};

// Paths in the schema start with /api/v1. Request needs an absolute URL
// outside a browser (tests, the build-time render of the landing page).
const origin =
  typeof window === "undefined" ? "http://localhost" : window.location.origin;

export const api = createClient<paths>({
  baseUrl: origin,
  credentials: "same-origin",
  // Looked up on every call, so a test can replace the global fetch.
  fetch: (request) => globalThis.fetch(request),
});
api.use(csrfHeader);

type ApiResult<Data> = { data?: Data; error?: unknown; response: Response };

/** The data of a successful call; anything else is thrown as an ApiError. */
export async function unwrap<Data>(
  call: Promise<ApiResult<Data>>,
): Promise<Data> {
  let result: ApiResult<Data>;
  try {
    result = await call;
  } catch {
    throw new ApiError(0, "network", "The request did not reach the server");
  }
  if (result.response.ok) return result.data as Data;
  throw toApiError(result.response.status, result.error);
}

function toApiError(status: number, body: unknown): ApiError {
  // The API's single error shape. A proxy in front of it may answer HTML.
  if (typeof body === "object" && body !== null && "error" in body) {
    const { code, message } = (body as { error: Record<string, unknown> })
      .error;
    if (typeof code === "string") {
      return new ApiError(status, code, String(message ?? ""));
    }
  }
  return new ApiError(status, "unknown", "");
}
