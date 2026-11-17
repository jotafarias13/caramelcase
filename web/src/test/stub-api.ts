import { vi } from "vitest";
import {
  createMockApi,
  NetworkFailure,
  type MockApi,
  type Routes,
} from "./mock-api";

/**
 * Replace the global fetch with a mock API for one test. setup.ts puts the
 * real one back after each test.
 */
export function stubApi(routes: Routes): MockApi {
  const mock = createMockApi(routes);

  vi.stubGlobal(
    "fetch",
    async (input: Request | string, init?: RequestInit) => {
      const request =
        input instanceof Request ? input : new Request(input, init);
      const text = await request.text();
      try {
        const answer = await mock.handle(
          request.method,
          request.url,
          text ? JSON.parse(text) : undefined,
        );
        const hasBody = answer.status !== 204 && answer.body !== undefined;
        return new Response(hasBody ? JSON.stringify(answer.body) : null, {
          status: answer.status,
          headers: hasBody ? { "Content-Type": "application/json" } : {},
        });
      } catch (error) {
        if (error instanceof NetworkFailure) {
          throw new TypeError("Failed to fetch", { cause: error });
        }
        throw error;
      }
    },
  );

  return mock;
}
