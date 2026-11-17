import { apiError } from "../../src/test/mock-api";
import type { Scene } from "../scene";

// A visitor without a session: sign-in needs no user.
const visitor = { "GET /me": apiError(401, "unauthenticated") };

export const auth: Scene[] = [
  { mockup: "v1-signin-mobile", path: "/signin", routes: visitor },
  { mockup: "v1-signin-desktop", path: "/signin", routes: visitor },
  {
    mockup: "v1-signin-sent-mobile",
    path: "/signin",
    routes: visitor,
    prepare: async (page) => {
      await page.getByLabel("E-mail").fill("carol@email.com");
      await page.getByRole("button", { name: "Enviar link mágico" }).click();
      await page.getByRole("heading", { name: "Olha seu e-mail" }).waitFor();
    },
  },
];
