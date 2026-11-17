import { defineConfig } from "@playwright/test";

// The visual check of milestone 6: each scene is photographed next to its
// mockup, in both themes. See README.md in this directory.
const port = 5180;

export default defineConfig({
  testDir: ".",
  testMatch: "shots.spec.ts",
  tsconfig: "../tsconfig.test.json",
  outputDir: "./out/.playwright",
  reporter: "list",
  fullyParallel: true,
  workers: 4,
  timeout: 90_000,
  use: { baseURL: `http://localhost:${port}` },
  webServer: {
    command: `npm run dev -- --port ${port} --strictPort`,
    url: `http://localhost:${port}`,
    reuseExistingServer: true,
    cwd: "..",
  },
});
