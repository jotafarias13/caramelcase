import { defineConfig, devices } from "@playwright/test";

// The end-to-end test: a guest plays a whole session against the real
// stack of docker compose, on the database `make seed` writes. Start both
// first, then run it:
//
//   make up && make seed
//   make e2e
//
// E2E_BASE_URL points it at the web app somewhere else.
const baseURL = process.env.E2E_BASE_URL ?? "http://localhost:5173";
const inCI = Boolean(process.env.CI);

export default defineConfig({
  testDir: ".",
  testMatch: "*.spec.ts",
  tsconfig: "../tsconfig.test.json",
  globalSetup: "./stack-is-up.ts",
  outputDir: "../test-results",
  reporter: inCI
    ? [
        ["list"],
        ["html", { open: "never", outputFolder: "../playwright-report" }],
      ]
    : "list",
  // The dev server compiles each page on its first request.
  timeout: 120_000,
  expect: { timeout: 15_000 },
  retries: inCI ? 1 : 0,
  use: {
    baseURL,
    serviceWorkers: "block",
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  // The same path in both languages, each at one of the design's two
  // widths. The language follows the browser's, as on a first visit.
  projects: [
    {
      name: "pt-BR, phone",
      use: {
        ...devices["Desktop Chrome"],
        viewport: { width: 360, height: 780 },
        isMobile: true,
        hasTouch: true,
        locale: "pt-BR",
        timezoneId: "America/Sao_Paulo",
      },
    },
    {
      name: "en, desktop",
      use: {
        ...devices["Desktop Chrome"],
        viewport: { width: 1280, height: 800 },
        locale: "en-US",
        timezoneId: "America/Recife",
      },
    },
  ],
});
