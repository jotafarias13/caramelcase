import type { Activity, Stats, SubjectDetail } from "../../src/api/types";
import { activity, stats, subjectDetail } from "../../src/test/fixtures";
import type { Scene } from "../scene";

// The profile mockups' sample data. Algoritmos, Sistemas Operacionais and
// Redes are not launch subjects, and the mockup's "today" is 16 November;
// the scenes answer with them so the screens can be compared, and the
// fixtures that Home relies on stay as they are.
const subject = (slug: string, name_pt: string, rating: number | null) => ({
  slug,
  name_pt,
  name_en: name_pt,
  short_pt: `${slug}/`,
  short_en: `${slug}/`,
  rating,
  answers_count: rating === null ? 0 : 100,
});

const profileStats: Stats = {
  ...stats,
  questions_answered: 312,
  correct_answers: 231,
  accuracy: 0.74,
  sessions_finished: 31,
  streak: { current: 7, longest: 12, status: "active", lost_length: null },
  subjects: [
    subject("estruturas-de-dados", "Estruturas de Dados", 1240),
    subject("algoritmos", "Algoritmos", 1105),
    subject("sistemas-operacionais", "Sistemas Operacionais", 980),
    subject("bancos-de-dados", "Bancos de Dados", null),
    subject("redes", "Redes", null),
  ],
};

const profileSubject: SubjectDetail = {
  ...subjectDetail,
  topics: [
    ...subjectDetail.topics,
    {
      slug: "grafos",
      name_pt: "Grafos",
      name_en: "Graphs",
      mastery: "new",
      correct: 0,
      total: 0,
      accuracy: 0,
    },
  ],
};

const profileActivity: Activity = {
  ...activity,
  today: "2026-11-16",
  days: [2, 3, 5, 6, 10, 11, 12, 13, 14, 15, 16].map((day) => ({
    date: `2026-11-${String(day).padStart(2, "0")}`,
    xp: 110,
    questions: 20,
    sessions_finished: 2,
    goal_met: true,
  })),
};

const devices = ["mobile", "desktop"] as const;

export const profile: Scene[] = devices.flatMap((device) => [
  {
    mockup: `v1-profile-${device}`,
    path: "/profile",
    routes: {
      "GET /me/stats": profileStats,
      "GET /subjects/:slug": profileSubject,
      "GET /me/activity": profileActivity,
    },
  },
  {
    // A student who has not answered anything yet.
    mockup: `v1-state-empty-${device}`,
    path: "/profile",
    routes: { "GET /me/stats": { ...stats, questions_answered: 0 } },
  },
]);
