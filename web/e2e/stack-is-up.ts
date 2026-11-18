import type { FullConfig } from "@playwright/test";

/**
 * Stops the run at once, saying what to do, when the app is not up:
 * otherwise every step would wait for its timeout first.
 */
export default async function stackIsUp(config: FullConfig): Promise<void> {
  const baseURL = config.projects[0].use.baseURL;
  const health = `${baseURL}/api/v1/health`;
  let status: number;
  try {
    status = (await fetch(health)).status;
  } catch {
    status = 0;
  }
  if (status !== 200) {
    throw new Error(
      `${health} answered ${status || "nothing"}. ` +
        "Start the app and fill its database first: make up && make seed",
    );
  }
}
