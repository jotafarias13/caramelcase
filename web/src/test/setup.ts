import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterEach, vi } from "vitest";
import { clearToasts } from "@/components/ui/toast-store";

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  clearToasts();
  // A test in the node environment (the landing page's static HTML) has
  // no browser to reset.
  if (typeof window === "undefined") return;
  localStorage.clear();
  document.documentElement.removeAttribute("data-theme");
});
