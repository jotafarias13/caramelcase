// One-time hints: which ones this device has already shown, and which one
// may show now. Kept outside React, like the toasts. Only one hint is on
// screen at a time (docs/DECISIONS.md, "Guidance").
import { useEffect, useSyncExternalStore } from "react";

/** Every hint, in the order they show when several wait on one screen. */
export const HINTS = ["xp", "rating", "streak", "topics", "subject"] as const;
export type HintId = (typeof HINTS)[number];

const STORAGE_KEY = "caramelcase.hints";

/** The hints already shown; read from the device on first use. */
let seen: Set<HintId> | null = null;
/** The hints whose place is on screen now, and how many places each has. */
const waiting = new Map<HintId, number>();
/** The student closed a hint by doing something else: no more for now. */
let quiet = false;
const listeners = new Set<() => void>();

function emit(): void {
  listeners.forEach((listener) => listener());
}

function subscribe(listener: () => void): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

function seenHints(): Set<HintId> {
  if (seen) return seen;
  let stored: unknown = [];
  try {
    stored = JSON.parse(localStorage.getItem(STORAGE_KEY) ?? "[]");
  } catch {
    // Storage that cannot be read, or holds something else: start empty.
  }
  const list = Array.isArray(stored) ? stored : [];
  seen = new Set(HINTS.filter((id) => list.includes(id)));
  return seen;
}

/** The hint to show now, if any. */
export function activeHint(): HintId | null {
  if (quiet) return null;
  const shown = seenHints();
  return HINTS.find((id) => waiting.has(id) && !shown.has(id)) ?? null;
}

/**
 * Says that the place of a hint is on screen. Returns what to call when it
 * leaves. A screen that arrives ends the quiet a closed hint left behind.
 */
export function offerHint(id: HintId): () => void {
  waiting.set(id, (waiting.get(id) ?? 0) + 1);
  quiet = false;
  emit();
  return () => {
    const places = (waiting.get(id) ?? 1) - 1;
    if (places > 0) waiting.set(id, places);
    else waiting.delete(id);
    emit();
  };
}

/**
 * The student has seen a hint: it never shows again on this device.
 * `advance` is true for "Got it", which lets the next hint of the screen
 * show. Closing it any other way means the student is doing something
 * else, so the next one waits for the next visit to a screen.
 */
export function dismissHint(id: HintId, { advance }: { advance: boolean }) {
  const shown = seenHints();
  shown.add(id);
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify([...shown]));
  } catch {
    // Without storage the hint is only remembered until the page reloads.
  }
  if (!advance) quiet = true;
  emit();
}

/**
 * Whether the hint `id` should show now. `eligible` says that its place is
 * on screen and that the hint makes sense for this student.
 */
export function useHint(id: HintId, eligible: boolean): boolean {
  useEffect(() => (eligible ? offerHint(id) : undefined), [id, eligible]);
  const active = useSyncExternalStore(subscribe, activeHint, () => null);
  return eligible && active === id;
}

/** For tests: forget everything, as on a new device. */
export function resetHints(): void {
  seen = null;
  waiting.clear();
  quiet = false;
  emit();
}
