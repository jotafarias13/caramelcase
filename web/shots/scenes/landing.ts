import type { Page } from "@playwright/test";
import { apiError } from "../../src/test/mock-api";
import type { Scene } from "../scene";

// A first visit: the browser has no session.
const visitor = { "GET /me": apiError(401, "unauthenticated") };

/**
 * The v1-flow-first mockups draw the header and the try-it question alone,
 * as if the hero were not there. Hide the rest of the page to compare.
 */
async function showOnlyTheQuestion(page: Page) {
  await page.addStyleTag({
    content: `
      main > div > div:first-child, main > section, footer { display: none !important; }
      main > div { padding-top: 28px !important; }
    `,
  });
}

async function pickStack(page: Page) {
  await page.getByRole("radio", { name: /Pilha/ }).click();
}

export const landing: Scene[] = [
  { mockup: "v1-landing-mobile", path: "/", routes: visitor },
  { mockup: "v1-landing-desktop", path: "/", routes: visitor },
  {
    mockup: "v1-flow-first-1-mobile",
    path: "/",
    routes: visitor,
    prepare: async (page) => {
      await pickStack(page);
      await showOnlyTheQuestion(page);
    },
  },
  {
    mockup: "v1-flow-first-2-mobile",
    path: "/",
    routes: visitor,
    prepare: async (page) => {
      await pickStack(page);
      await page.getByRole("button", { name: "Verificar" }).click();
      await showOnlyTheQuestion(page);
    },
  },
];
