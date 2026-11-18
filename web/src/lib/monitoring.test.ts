import type { ErrorEvent } from "@sentry/browser";
import { afterEach, describe, expect, it, vi } from "vitest";
import {
  startMonitoring,
  withoutQuery,
  withoutQueryInBreadcrumb,
  withoutQueryInEvent,
} from "./monitoring";

const sentryInit = vi.hoisted(() => vi.fn());
vi.mock("@sentry/browser", () => ({ init: sentryInit }));

function analyticsScripts(): HTMLScriptElement[] {
  return [...document.head.querySelectorAll("script")].filter((script) =>
    script.src.includes("plausible"),
  );
}

afterEach(() => {
  vi.unstubAllEnvs();
  sentryInit.mockClear();
  for (const script of analyticsScripts()) script.remove();
});

describe("startMonitoring", () => {
  it("starts nothing without keys", async () => {
    vi.stubEnv("VITE_SENTRY_DSN", "");
    vi.stubEnv("VITE_PLAUSIBLE_DOMAIN", "");

    startMonitoring();
    await vi.dynamicImportSettled();

    expect(sentryInit).not.toHaveBeenCalled();
    expect(analyticsScripts()).toHaveLength(0);
  });

  it("starts Sentry with its DSN and without personal data", async () => {
    vi.stubEnv("VITE_SENTRY_DSN", "https://key@errors.example.com/1");

    startMonitoring();
    await vi.dynamicImportSettled();

    expect(sentryInit).toHaveBeenCalledWith(
      expect.objectContaining({
        dsn: "https://key@errors.example.com/1",
        dataCollection: expect.objectContaining({
          userInfo: false,
          urlQueryParams: false,
        }),
      }),
    );
  });

  it("adds Plausible's script for the domain", () => {
    vi.stubEnv("VITE_PLAUSIBLE_DOMAIN", "caramelcase.example.com");

    startMonitoring();

    const [script] = analyticsScripts();
    expect(script.dataset.domain).toBe("caramelcase.example.com");
    expect(script.src).toBe("https://plausible.io/js/script.js");
    expect(script.defer).toBe(true);
  });

  it("takes another Plausible script when one is set", () => {
    vi.stubEnv("VITE_PLAUSIBLE_DOMAIN", "caramelcase.example.com");
    vi.stubEnv(
      "VITE_PLAUSIBLE_SCRIPT",
      "https://plausible.example.com/js/script.js",
    );

    startMonitoring();

    expect(analyticsScripts()[0].src).toBe(
      "https://plausible.example.com/js/script.js",
    );
  });
});

describe("what Sentry is sent", () => {
  it("drops the query and fragment of an address", () => {
    expect(withoutQuery("https://a.com/auth/callback?token=secret#x")).toBe(
      "https://a.com/auth/callback",
    );
    expect(withoutQuery("/home")).toBe("/home");
  });

  it("drops the query of an event's page", () => {
    const event = {
      request: {
        url: "https://a.com/auth/callback?token=secret",
        query_string: "token=secret",
      },
    } as ErrorEvent;

    const sent = withoutQueryInEvent(event);

    expect(sent.request?.url).toBe("https://a.com/auth/callback");
    expect(sent.request?.query_string).toBeUndefined();
  });

  it("drops the query of a navigation or request breadcrumb", () => {
    const navigation = withoutQueryInBreadcrumb({
      category: "navigation",
      data: { from: "/signin", to: "/auth/callback?token=secret" },
    });
    const request = withoutQueryInBreadcrumb({
      category: "fetch",
      data: { url: "/api/v1/me/activity?start=2026-11-01", status_code: 200 },
    });

    expect(navigation.data).toEqual({ from: "/signin", to: "/auth/callback" });
    expect(request.data).toEqual({
      url: "/api/v1/me/activity",
      status_code: 200,
    });
  });
});
