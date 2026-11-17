import type { Page } from "@playwright/test";
import type { Locale } from "../src/api/types";
import type { Routes } from "../src/test/mock-api";

/**
 * One mockup of design/screens/ and how to bring the app to the same
 * state: an address, the API's answers and, if needed, a few clicks.
 */
export type Scene = {
  /** The mockup's file name without ".html": "v1-home-mobile". */
  mockup: string;
  /** The address to open in the app. */
  path: string;
  /** API answers on top of the world of src/test/fixtures.ts. */
  routes?: Routes;
  /** The interface language; Portuguese by default. */
  locale?: Locale;
  /** localStorage entries set before the app starts. */
  storage?: Record<string, string>;
  /** The clock of the page, as an ISO time: "2026-11-17T18:00:00-03:00". */
  now?: string;
  /** What to do after the page loaded: select an option, open a sheet. */
  prepare?: (page: Page) => Promise<void>;
};

/** A handler for a request that never gets an answer: a loading state. */
export function pending(): Promise<never> {
  return new Promise(() => {});
}
