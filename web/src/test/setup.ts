import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterEach, vi } from "vitest";
import { clearToasts } from "@/components/ui/toast-store";
import { resetHints } from "@/lib/hints";

// jsdom has no layout, so it has no ResizeObserver; the popover of an
// explanation (Radix) asks for one to follow the size of its button.
if (typeof window !== "undefined" && typeof ResizeObserver === "undefined") {
  window.ResizeObserver = class {
    observe() {}
    unobserve() {}
    disconnect() {}
  };
}

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  clearToasts();
  resetHints();
  // A test in the node environment (the landing page's static HTML) has
  // no browser to reset.
  if (typeof window === "undefined") return;
  localStorage.clear();
  document.documentElement.removeAttribute("data-theme");
});
