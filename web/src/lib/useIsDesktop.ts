import { useSyncExternalStore } from "react";

// The `lg` breakpoint of design/tailwind.theme.js: the sidebar layout.
const QUERY = "(min-width: 1280px)";

function subscribe(listener: () => void): () => void {
  const media = window.matchMedia?.(QUERY);
  media?.addEventListener?.("change", listener);
  return () => media?.removeEventListener?.("change", listener);
}

/**
 * True from 1280 px. Layout is CSS's job (`lg:`); this is for the few
 * things CSS cannot do, such as opening a hint only where it can be seen.
 */
export function useIsDesktop(): boolean {
  return useSyncExternalStore(
    subscribe,
    () => window.matchMedia?.(QUERY).matches ?? false,
    () => false,
  );
}
