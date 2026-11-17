// First-party product events, sent to POST /events in batches. Losing an
// event is fine; breaking the app over one is not, so nothing here throws.
import { api } from "@/api/client";
import type { EventIn } from "@/api/types";

const FLUSH_AFTER_MS = 5000;
const MAX_BATCH = 50;

let queue: EventIn[] = [];
let timer: ReturnType<typeof setTimeout> | null = null;

/** Record that something happened. Names are lower case with dots. */
export function track(name: string, props?: Record<string, unknown>): void {
  queue.push({
    name,
    occurred_at: new Date().toISOString(),
    props: props ?? {},
  });
  if (queue.length >= MAX_BATCH) flushEvents();
  else timer ??= setTimeout(flushEvents, FLUSH_AFTER_MS);
}

export function flushEvents(): void {
  if (timer) clearTimeout(timer);
  timer = null;
  if (queue.length === 0) return;
  const events = queue;
  queue = [];
  // keepalive lets the request outlive the page that sent it.
  api
    .POST("/api/v1/events", { body: { events }, keepalive: true })
    .catch(() => undefined);
}

if (typeof window !== "undefined") {
  window.addEventListener("pagehide", flushEvents);
}
