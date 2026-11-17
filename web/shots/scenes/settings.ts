import { config, me } from "../../src/test/fixtures";
import type { Scene } from "../scene";

// The mockups show the "Lembrete diário" switch, which V1 hides until the
// reminders flag is on (docs/DECISIONS.md): the scenes turn it on. The
// mockups select "Escuro" in both themes; the account here says "Sistema",
// so that each theme's shot follows its colour scheme.
const routes = {
  "GET /config": { ...config, flags: { reminders: true } },
  "GET /me": { ...me, settings: { ...me.settings, daily_reminder: true } },
};

export const settings: Scene[] = [
  { mockup: "v1-settings-mobile", path: "/settings", routes },
  { mockup: "v1-settings-desktop", path: "/settings", routes },
  {
    mockup: "v1-settings-delete-mobile",
    path: "/settings",
    routes,
    prepare: async (page) => {
      await page.getByRole("button", { name: "Excluir conta" }).click();
      await page.getByRole("alertdialog").waitFor();
    },
  },
];
