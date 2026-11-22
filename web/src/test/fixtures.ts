// Sample data in the API's shapes, for component tests and screenshot
// scenes. The names and numbers are those of the mockups (Carol, Estruturas
// de Dados, a 7-day streak), so a scene can be compared with its mockup.
import type {
  Activity,
  AnswerResult,
  Config,
  Me,
  Session,
  SessionQuestion,
  SessionSummary,
  Stats,
  SubjectDetail,
  SubjectRef,
  SubjectSummary,
} from "@/api/types";
import { MockResponse, type MockRequest, type Routes } from "./mock-api";

export const SESSION_ID = "5e551017-0000-4000-8000-000000000001";

export const dataStructures: SubjectRef = {
  slug: "estruturas-de-dados",
  name_pt: "Estruturas de Dados",
  name_en: "Data Structures",
  short_pt: "ed/",
  short_en: "ds/",
};

export const programming: SubjectRef = {
  slug: "introducao-a-programacao",
  name_pt: "Introdução à Programação",
  name_en: "Introduction to Programming",
  short_pt: "prog/",
  short_en: "prog/",
};

export const databases: SubjectRef = {
  slug: "banco-de-dados",
  name_pt: "Banco de Dados",
  name_en: "Databases",
  short_pt: "bd/",
  short_en: "db/",
};

export const me: Me = {
  id: "0a0a0a0a-0000-4000-8000-000000000001",
  email: "carol@email.com",
  display_name: "Carol Nunes",
  is_guest: false,
  role: "user",
  locale: "pt-BR",
  // The timezone of the test environment, so nothing is patched at start.
  timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC",
  university: "Sua universidade",
  course: "Ciência da Computação",
  current_subject: dataStructures.slug,
  settings: {
    daily_goal: 20,
    theme: "system",
    show_option_reasons: true,
    daily_reminder: false,
    weekly_email: false,
  },
};

/** Someone on a first visit: no account and no subject chosen yet. */
export const newGuest: Me = {
  ...me,
  id: "0a0a0a0a-0000-4000-8000-000000000002",
  email: null,
  display_name: null,
  is_guest: true,
  university: null,
  course: null,
  current_subject: null,
};

/** A guest who went through onboarding and is playing. */
export const guest: Me = { ...newGuest, current_subject: dataStructures.slug };

export const config: Config = {
  flags: {},
  google_sign_in: true,
  session_length: 10,
  daily_goal_options: [10, 20, 30],
  xp_per_level: 500,
  rules: {
    xp_correct: 10,
    xp_session_finished: 10,
    user_rating_start: 1000,
    mastery_mastered_from: 0.85,
    mastery_mastered_min_answers: 10,
  },
  plans: [],
  entitlements: {
    plan_key: null,
    sessions_per_day: null,
    ads: false,
    tutor_messages_per_day: null,
    exam_mode: true,
    exam_tracks: true,
  },
};

export const subjects: SubjectSummary[] = [
  {
    ...programming,
    is_current: false,
    rating: null,
    answers_count: 0,
    questions_count: 352,
    topics_count: 11,
  },
  {
    ...dataStructures,
    is_current: true,
    rating: 1240,
    answers_count: 180,
    questions_count: 264,
    topics_count: 12,
  },
  {
    ...databases,
    is_current: false,
    rating: 1102,
    answers_count: 40,
    questions_count: 264,
    topics_count: 11,
  },
];

export const subjectDetail: SubjectDetail = {
  ...subjects[1],
  next_topic: "listas-encadeadas",
  topics: [
    {
      slug: "pilhas",
      name_pt: "Pilhas e filas",
      name_en: "Stacks and queues",
      mastery: "mastered",
      correct: 27,
      total: 30,
      accuracy: 0.9,
    },
    {
      slug: "listas-encadeadas",
      name_pt: "Listas ligadas",
      name_en: "Linked lists",
      mastery: "learning",
      correct: 8,
      total: 20,
      accuracy: 0.4,
    },
    {
      slug: "arvores-binarias",
      name_pt: "Árvores binárias",
      name_en: "Binary trees",
      mastery: "new",
      correct: 0,
      total: 0,
      accuracy: 0,
    },
    {
      slug: "tabelas-hash",
      name_pt: "Tabelas hash",
      name_en: "Hash tables",
      mastery: "new",
      correct: 0,
      total: 0,
      accuracy: 0,
    },
  ],
};

export const stats: Stats = {
  today: "2026-11-17",
  level: { level: 4, total_xp: 1820, xp_in_level: 320, xp_per_level: 500 },
  streak: { current: 7, longest: 12, status: "active", lost_length: null },
  goal: { goal: 20, questions: 12, remaining: 8, met: false },
  questions_answered: 220,
  correct_answers: 172,
  accuracy: 0.78,
  sessions_finished: 22,
  subjects: subjects.map((subject) => ({
    slug: subject.slug,
    name_pt: subject.name_pt,
    name_en: subject.name_en,
    short_pt: subject.short_pt,
    short_en: subject.short_en,
    rating: subject.rating,
    answers_count: subject.answers_count,
  })),
  last_rating_change: {
    subject: dataStructures,
    before: 1226,
    after: 1240,
    delta: 14,
  },
};

export const activity: Activity = {
  start: "2026-11-01",
  end: "2026-11-30",
  today: "2026-11-17",
  days: [3, 4, 6, 7, 11, 12, 13, 14, 15, 16, 17].map((day) => ({
    date: `2026-11-${String(day).padStart(2, "0")}`,
    xp: 110,
    questions: 20,
    sessions_finished: 2,
    goal_met: true,
  })),
};

const recursionCode = [
  "def f(n):",
  "    if n <= 1:",
  "        return 1",
  "    return n * f(n - 1)",
  "",
  "print(f(4))",
].join("\n");

function question(index: number, overrides: Partial<SessionQuestion> = {}) {
  const base: SessionQuestion = {
    id: `9e571000-0000-4000-8000-${String(index).padStart(12, "0")}`,
    type: "mcq",
    locale: "pt-BR",
    difficulty: 3,
    topic: {
      slug: "busca-binaria",
      name_pt: "Busca binária",
      name_en: "Binary search",
    },
    stem: "Qual é a complexidade de tempo, no pior caso, da busca binária em um vetor ordenado de n elementos?",
    code: null,
    code_language: null,
    options: [
      { key: "a", text: "O(1)" },
      { key: "b", text: "O(log n)" },
      { key: "c", text: "O(n)" },
      { key: "d", text: "O(n log n)" },
    ],
    answer: null,
  };
  return { ...base, ...overrides };
}

/** A question with code: what the recursion mockups show. */
export const codeQuestion = question(1, {
  difficulty: 1,
  topic: { slug: "recursao", name_pt: "Recursão", name_en: "Recursion" },
  stem: "O que este programa imprime?",
  code: recursionCode,
  code_language: "python",
  options: [
    { key: "a", text: "10" },
    { key: "b", text: "24" },
    { key: "c", text: "16" },
    { key: "d", text: "RecursionError" },
  ],
});

/** A session of ten in which nothing was answered yet. */
export const session: Session = {
  id: SESSION_ID,
  mode: "practice",
  subject: dataStructures,
  started_at: "2026-11-17T18:00:00Z",
  finished_at: null,
  answered_count: 0,
  correct_count: 0,
  xp_earned: 0,
  summary: null,
  questions: [
    codeQuestion,
    ...Array.from({ length: 9 }, (_, index) => question(index + 2)),
  ],
};

/** The same session with its first `count` questions answered correctly. */
export function sessionAnswered(count: number): Session {
  return {
    ...session,
    answered_count: count,
    correct_count: count,
    xp_earned: count * 10,
    questions: session.questions.map((item, index) =>
      index < count
        ? {
            ...item,
            answer: { selected_key: "b", is_correct: true, xp_earned: 10 },
          }
        : item,
    ),
  };
}

const recursionReasons: AnswerResult["reasons"] = [
  { key: "a", reason: "10 seria a soma 4 + 3 + 2 + 1. O programa multiplica." },
  { key: "b", reason: "f(4) = 4 × 3 × 2 × 1 = 24." },
  {
    key: "c",
    reason:
      "16 seria 4 × 4. Cada chamada multiplica por f(n - 1), não por n de novo.",
  },
  {
    key: "d",
    reason: "O caso base n <= 1 encerra a recursão, então não há erro.",
  },
];

export const answerCorrect: AnswerResult = {
  is_correct: true,
  correct_key: "b",
  reasons: recursionReasons,
  explanation: "f calcula o fatorial. f(4) = 4 × 3 × 2 × 1 = 24.",
  rating: { before: 1240, after: 1244, delta: 4 },
  xp_earned: 10,
  session_complete: false,
};

export const answerWrong: AnswerResult = {
  ...answerCorrect,
  is_correct: false,
  rating: { before: 1240, after: 1228, delta: -12 },
  xp_earned: 0,
};

// The summary mockups: 8 of 10, rating 1240 to 1254, a 7-day streak, level
// 4 at 332 / 500 XP, one miss in Recursão and one in Busca binária. Their
// "+96 XP" cannot come out of the spec's rules (10 or 15 per correct answer,
// 10 for finishing), so the session earns 100: six answers at 10, two at 15.
export const summary: SessionSummary = {
  correct_count: 8,
  total: 10,
  xp_earned: 100,
  sessions_finished: 23,
  rating: { subject: dataStructures, before: 1240, after: 1254, delta: 14 },
  streak: { current: 7, longest: 12, status: "active", lost_length: null },
  goal: { goal: 20, questions: 20, remaining: 0, met: true },
  level_before: {
    level: 4,
    total_xp: 1732,
    xp_in_level: 232,
    xp_per_level: 500,
  },
  level_after: {
    level: 4,
    total_xp: 1832,
    xp_in_level: 332,
    xp_per_level: 500,
  },
  topics_to_review: [
    {
      slug: "recursao",
      name_pt: "Recursão",
      name_en: "Recursion",
      wrong_count: 1,
    },
    {
      slug: "busca-binaria",
      name_pt: "Busca binária",
      name_en: "Binary search",
      wrong_count: 1,
    },
  ],
};

/** The session of `summary`: the first two answers wrong, the rest right. */
export const finishedSession: Session = {
  ...session,
  finished_at: "2026-11-17T18:05:00Z",
  answered_count: 10,
  correct_count: summary.correct_count,
  xp_earned: summary.xp_earned,
  summary,
  questions: session.questions.map((item, index) => {
    const isCorrect = index >= 2;
    const xp = !isCorrect ? 0 : index < 4 ? 15 : 10;
    return {
      ...item,
      answer: {
        selected_key: isCorrect ? "b" : "a",
        is_correct: isCorrect,
        xp_earned: xp,
      },
    };
  }),
};

/**
 * An API in which everything works, for a signed-in Carol in the middle of
 * her day. Pass routes to replace or add answers:
 *   world({ "GET /me": guest, "GET /me/stats": apiError(500, "boom") })
 */
export function world(overrides: Routes = {}): Routes {
  return {
    "GET /me": me,
    "GET /config": config,
    "GET /subjects": { subjects },
    "GET /subjects/:slug": subjectDetail,
    "GET /me/stats": stats,
    "GET /me/activity": activity,
    "PATCH /me/settings": (request: MockRequest) =>
      patchedMe(me, request.body as Record<string, unknown>),
    "POST /auth/guest": newGuest,
    "POST /auth/magic-link": new MockResponse(202, {}),
    "POST /auth/magic-link/verify": me,
    "POST /auth/logout": undefined,
    "DELETE /me": undefined,
    "POST /sessions": session,
    "GET /sessions/:id": session,
    "POST /sessions/:id/answers": answerCorrect,
    "POST /sessions/:id/finish": summary,
    "POST /questions/:id/report": new MockResponse(201, {
      id: "4e904700-0000-4000-8000-000000000001",
      created_at: "2026-11-17T18:03:00Z",
    }),
    "POST /events": new MockResponse(202, { accepted: 1 }),
    ...overrides,
  };
}

const settingsFields = [
  "daily_goal",
  "theme",
  "show_option_reasons",
  "daily_reminder",
  "weekly_email",
];

/** What PATCH /me/settings answers: the user with the sent fields changed. */
export function patchedMe(user: Me, patch: Record<string, unknown>): Me {
  const next: Me = { ...user, settings: { ...user.settings } };
  for (const [field, value] of Object.entries(patch)) {
    if (settingsFields.includes(field)) {
      Object.assign(next.settings, { [field]: value });
    } else {
      Object.assign(next, { [field]: value });
    }
  }
  return next;
}
