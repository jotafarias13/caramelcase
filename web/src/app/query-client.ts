import { QueryClient } from "@tanstack/react-query";
import { ApiError } from "@/api/client";

/** One retry for a failure that may pass; none for an answer that will not. */
function shouldRetry(failureCount: number, error: unknown): boolean {
  if (error instanceof ApiError && (error.status === 0 || error.status < 500)) {
    return false;
  }
  return failureCount < 1;
}

export function createQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 30 * 1000,
        retry: shouldRetry,
        refetchOnWindowFocus: false,
        // Run even when the browser says it is offline: the request fails
        // at once and the screen shows the offline state with a retry,
        // instead of waiting without a word.
        networkMode: "always",
      },
      mutations: { networkMode: "always" },
    },
  });
}
