import type { Session, SessionSummary } from "../../src/api/types";
import {
  finishedSession,
  guest,
  SESSION_ID,
  summary as gainSummary,
} from "../../src/test/fixtures";
import type { Scene } from "../scene";

const path = `/session/${SESSION_ID}/summary`;

function finishedWith(next: SessionSummary): Session {
  return { ...finishedSession, summary: next };
}

// v1-summary-loss: 5 of 10, rating 1231 (−9), three topics to review. Its
// "+60" is what the spec gives: five right answers at 10, and 10 for
// finishing.
const lossSummary: SessionSummary = {
  ...gainSummary,
  correct_count: 5,
  xp_earned: 60,
  rating: { ...gainSummary.rating, before: 1240, after: 1231, delta: -9 },
  level_before: {
    ...gainSummary.level_before,
    xp_in_level: 272,
    total_xp: 1772,
  },
  topics_to_review: [
    { ...gainSummary.topics_to_review[0], wrong_count: 2 },
    { ...gainSummary.topics_to_review[1], wrong_count: 2 },
    {
      slug: "pilhas",
      name_pt: "Pilhas e filas",
      name_en: "Stacks and queues",
      wrong_count: 1,
    },
  ],
};

// v1-summary-save: a guest's first finished session.
const firstSummary: SessionSummary = { ...gainSummary, sessions_finished: 1 };

const devices = ["mobile", "desktop"] as const;

export const summary: Scene[] = [
  ...devices.map((device) => ({
    mockup: `v1-summary-gain-${device}`,
    path,
    routes: { "GET /sessions/:id": finishedSession },
  })),
  {
    mockup: "v1-summary-loss-mobile",
    path,
    routes: { "GET /sessions/:id": finishedWith(lossSummary) },
  },
  ...devices.map((device) => ({
    mockup: `v1-summary-save-${device}`,
    path,
    routes: {
      "GET /me": guest,
      "GET /sessions/:id": finishedWith(firstSummary),
    },
  })),
];
