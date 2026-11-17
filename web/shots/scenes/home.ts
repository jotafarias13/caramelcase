import type { Stats } from "../../src/api/types";
import { stats } from "../../src/test/fixtures";
import type { Scene } from "../scene";

// The desktop mockup's rating card shows "rating · algoritmos" at 1254
// (+14), a subject the launch catalog does not have, beside a rating chip
// of 1240 in Estruturas de Dados. The scene answers with that change so
// the card can be compared; the fixtures stay consistent.
const mockupStats: Stats = {
  ...stats,
  last_rating_change: {
    subject: {
      slug: "algoritmos",
      name_pt: "Algoritmos",
      name_en: "Algorithms",
      short_pt: "alg/",
      short_en: "alg/",
    },
    before: 1240,
    after: 1254,
    delta: 14,
  },
};

const devices = ["mobile", "desktop"] as const;

export const home: Scene[] = devices.map((device) => ({
  mockup: `v1-home-${device}`,
  path: "/home",
  routes: { "GET /me/stats": mockupStats },
}));
