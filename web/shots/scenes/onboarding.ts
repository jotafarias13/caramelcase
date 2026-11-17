import type { SubjectSummary } from "../../src/api/types";
import { newGuest, subjects } from "../../src/test/fixtures";
import type { Scene } from "../scene";

const devices = ["mobile", "desktop"] as const;

/** The five subjects of the step 3 mockup, in its order. */
function mockupSubject(
  slug: string,
  name_pt: string,
  name_en: string,
): SubjectSummary {
  return { ...subjects[0], slug, name_pt, name_en, is_current: false };
}

const mockupSubjects: SubjectSummary[] = [
  mockupSubject(
    "estruturas-de-dados",
    "Estruturas de Dados",
    "Data Structures",
  ),
  mockupSubject("algoritmos", "Algoritmos", "Algorithms"),
  mockupSubject(
    "sistemas-operacionais",
    "Sistemas Operacionais",
    "Operating Systems",
  ),
  mockupSubject("bancos-de-dados", "Bancos de Dados", "Databases"),
  mockupSubject("redes", "Redes", "Networks"),
];

// A guest on a first visit, at each of the four steps.
export const onboarding: Scene[] = devices.flatMap((device) =>
  [1, 2, 3, 4].map((step) => ({
    mockup: `v1-onboarding-${step}-${device}`,
    path: step === 1 ? "/start" : `/start?step=${step}`,
    routes: {
      "GET /me": newGuest,
      "GET /subjects": { subjects: mockupSubjects },
    },
  })),
);
