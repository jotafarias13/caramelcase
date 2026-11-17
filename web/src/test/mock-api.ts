// A stand-in for the API, used by the component tests (through
// stub-api.ts) and by the screenshot scenes (shots/). It knows nothing of
// vitest or Playwright: it maps "METHOD /path" to an answer.

export type MockRequest = {
  method: string;
  /** Without /api/v1: "/sessions/abc/answers". */
  path: string;
  query: URLSearchParams;
  /** Named parts of the path: { id: "abc" } for "/sessions/:id/answers". */
  params: Record<string, string>;
  body: unknown;
};

/** Returned by a handler that wants another status than 200. */
export class MockResponse {
  status: number;
  body: unknown;

  constructor(status: number, body?: unknown) {
    this.status = status;
    this.body = body;
  }
}

/** An answer in the API's error shape. */
export function apiError(status: number, code: string): MockResponse {
  return new MockResponse(status, { error: { code, message: code } });
}

/** Thrown by a handler to act as a request that never reached the server. */
export class NetworkFailure extends Error {}

export function networkFailure(): never {
  throw new NetworkFailure("offline");
}

/** JSON to answer with, or a function of the request that returns it. */
export type Handler = unknown | ((request: MockRequest) => unknown);

/** Keys are "GET /me" or "POST /sessions/:id/answers". */
export type Routes = Record<string, Handler>;

const API_PREFIX = "/api/v1";

function matchPath(
  pattern: string,
  path: string,
): Record<string, string> | null {
  const patternParts = pattern.split("/");
  const pathParts = path.split("/");
  if (patternParts.length !== pathParts.length) return null;
  const params: Record<string, string> = {};
  for (let index = 0; index < patternParts.length; index++) {
    const part = patternParts[index];
    if (part.startsWith(":")) params[part.slice(1)] = pathParts[index];
    else if (part !== pathParts[index]) return null;
  }
  return params;
}

export type MockApi = {
  /** Every request received, in order. */
  calls: MockRequest[];
  /** The requests to one route: callsTo("POST /sessions/:id/answers"). */
  callsTo: (route: string) => MockRequest[];
  /** Answers a request; throws NetworkFailure when the handler says so. */
  handle: (method: string, url: string, body: unknown) => Promise<MockResponse>;
};

export function createMockApi(routes: Routes): MockApi {
  const calls: MockRequest[] = [];

  function find(method: string, path: string) {
    for (const [route, handler] of Object.entries(routes)) {
      const [routeMethod, pattern] = route.split(" ");
      if (routeMethod !== method) continue;
      const params = matchPath(pattern, path);
      if (params) return { handler, params };
    }
    return null;
  }

  return {
    calls,
    callsTo(route) {
      const [method, pattern] = route.split(" ");
      return calls.filter(
        (call) => call.method === method && matchPath(pattern, call.path),
      );
    },
    async handle(method, url, body) {
      const parsed = new URL(url, "http://localhost");
      const path = parsed.pathname.slice(API_PREFIX.length);
      const found = find(method, path);
      const request: MockRequest = {
        method,
        path,
        query: parsed.searchParams,
        params: found?.params ?? {},
        body,
      };
      calls.push(request);
      if (!found) return apiError(404, "not_mocked");
      const answer =
        typeof found.handler === "function"
          ? await found.handler(request)
          : found.handler;
      if (answer instanceof MockResponse) return answer;
      return new MockResponse(answer === undefined ? 204 : 200, answer);
    },
  };
}
