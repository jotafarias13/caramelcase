import type { Page } from "@playwright/test";
import type { Session, SessionQuestion, SubjectRef } from "../../src/api/types";
import {
  SESSION_ID,
  answerCorrect,
  answerWrong,
  codeQuestion,
  me,
  session as freshSession,
} from "../../src/test/fixtures";
import { pending, type Scene } from "../scene";

// The mockups' sample data. Their breadcrumb shows "Programação" where the
// app shows the subject's short badge text, so these subjects carry the
// mockups' words as their short text.
const programming: SubjectRef = {
  slug: "introducao-a-programacao",
  name_pt: "Programação",
  name_en: "Programming",
  short_pt: "Programação",
  short_en: "Programming",
};

const operatingSystems: SubjectRef = {
  slug: "sistemas-operacionais",
  name_pt: "Sistemas Operacionais",
  name_en: "Operating Systems",
  short_pt: "Sistemas Operacionais",
  short_en: "Operating Systems",
};

const algorithms: SubjectRef = {
  slug: "algoritmos",
  name_pt: "Algoritmos",
  name_en: "Algorithms",
  short_pt: "Algoritmos",
  short_en: "Algorithms",
};

const dataStructures: SubjectRef = {
  slug: "estruturas-de-dados",
  name_pt: "Estruturas de Dados",
  name_en: "Data Structures",
  short_pt: "Estruturas de Dados",
  short_en: "Data Structures",
};

const longTextQuestion: SessionQuestion = {
  ...codeQuestion,
  id: "9e571000-0000-4000-8000-000000000101",
  difficulty: 3,
  topic: {
    slug: "gerenciamento-de-memoria",
    name_pt: "Gerenciamento de memória",
    name_en: "Memory management",
  },
  stem: "Em um sistema com paginação por demanda, o que acontece quando um processo acessa uma página que não está na memória principal?",
  code: null,
  code_language: null,
  options: [
    {
      key: "a",
      text: "Ocorre uma falta de página e o sistema operacional carrega a página do disco",
    },
    {
      key: "b",
      text: "O processo é encerrado imediatamente com erro de segmentação",
    },
    {
      key: "c",
      text: "O processador ignora o acesso e segue para a próxima instrução",
    },
    {
      key: "d",
      text: "A página é criada vazia na memória, sem consultar o disco",
    },
  ],
};

const englishQuestion: SessionQuestion = {
  ...codeQuestion,
  id: "9e571000-0000-4000-8000-000000000102",
  locale: "en",
  difficulty: 1,
  topic: {
    slug: "pilhas",
    name_pt: "Pilhas e filas",
    name_en: "Stacks and queues",
  },
  stem: "Which data structure follows the LIFO (last in, first out) policy?",
  code: null,
  code_language: null,
  options: [
    { key: "a", text: "Queue" },
    { key: "b", text: "Stack" },
    { key: "c", text: "Linked list" },
    { key: "d", text: "Binary tree" },
  ],
};

// The mockup's code has a docstring and comments, which the bank's code
// does not (docs/DECISIONS.md); the scene reproduces the mockup.
const binarySearchCode = [
  "def busca_binaria(vetor, alvo):",
  '    """Devolve o índice de alvo em vetor, ou -1 se não achar."""',
  "    inicio, fim = 0, len(vetor) - 1",
  "    while inicio <= fim:",
  "        meio = (inicio + fim) // 2  # divide o intervalo ao meio",
  "        if vetor[meio] == alvo:",
  "            return meio",
  "        if vetor[meio] < alvo:",
  "            inicio = meio + 1       # descarta a metade esquerda",
  "        else:",
  "            fim = meio - 1          # descarta a metade direita",
  "    return -1",
].join("\n");

const longCodeQuestion: SessionQuestion = {
  ...codeQuestion,
  id: "9e571000-0000-4000-8000-000000000103",
  difficulty: 3,
  topic: {
    slug: "busca-binaria",
    name_pt: "Busca binária",
    name_en: "Binary search",
  },
  stem: "O que esta função devolve para vetor = [1, 3, 5, 7, 9] e alvo = 7?",
  code: binarySearchCode,
  options: [
    { key: "a", text: "2" },
    { key: "b", text: "3" },
    { key: "c", text: "4" },
    { key: "d", text: "-1" },
  ],
};

/** A session of ten whose first `index` questions are answered. */
function sessionAt(
  index: number,
  current: SessionQuestion,
  subject: SubjectRef,
): Session {
  const others = freshSession.questions.filter(
    (question) => question.id !== codeQuestion.id,
  );
  const questions = [
    ...others.slice(0, index),
    current,
    ...others.slice(index),
  ].map((question, position) =>
    position < index
      ? {
          ...question,
          answer: {
            selected_key: "b" as const,
            is_correct: true,
            xp_earned: 10,
          },
        }
      : question,
  );
  return {
    ...freshSession,
    subject,
    answered_count: index,
    correct_count: index,
    xp_earned: index * 10,
    questions,
  };
}

const path = `/session/${SESSION_ID}`;
const recursion = sessionAt(3, codeQuestion, programming);

async function choose(page: Page, text: string) {
  await page.getByRole("radio", { name: text, exact: true }).click();
  await page.mouse.move(0, 0);
}

async function check(page: Page) {
  await page.getByRole("button", { name: "Verificar" }).click();
  await page.mouse.move(0, 0);
}

async function answer(page: Page, text: string) {
  await choose(page, text);
  await check(page);
  await page.getByRole("button", { name: "Continuar" }).waitFor();
}

const devices = ["mobile", "desktop"] as const;

export const session: Scene[] = [
  {
    mockup: "v1-session-0-default-mobile",
    path,
    routes: { "GET /sessions/:id": recursion },
  },
  ...devices.map((device) => ({
    mockup: `v1-session-1-selected-${device}`,
    path,
    routes: { "GET /sessions/:id": recursion },
    prepare: (page: Page) => choose(page, "24"),
  })),
  {
    mockup: "v1-session-2-checking-mobile",
    path,
    routes: {
      "GET /sessions/:id": recursion,
      "POST /sessions/:id/answers": pending,
    },
    prepare: async (page) => {
      await choose(page, "24");
      await check(page);
    },
  },
  ...devices.map((device) => ({
    mockup: `v1-session-3-correct-${device}`,
    path,
    routes: {
      "GET /sessions/:id": recursion,
      "POST /sessions/:id/answers": answerCorrect,
    },
    prepare: (page: Page) => answer(page, "24"),
  })),
  ...devices.map((device) => ({
    mockup: `v1-session-4-wrong-${device}`,
    path,
    routes: {
      "GET /sessions/:id": recursion,
      "POST /sessions/:id/answers": answerWrong,
    },
    prepare: (page: Page) => answer(page, "16"),
  })),
  {
    mockup: "v1-session-5-reasons-off-mobile",
    path,
    routes: {
      "GET /me": {
        ...me,
        settings: { ...me.settings, show_option_reasons: false },
      },
      "GET /sessions/:id": recursion,
      "POST /sessions/:id/answers": answerWrong,
    },
    prepare: (page) => answer(page, "16"),
  },
  ...devices.map((device) => ({
    mockup: `v1-flow-longtext-pt-${device}`,
    path,
    routes: {
      "GET /sessions/:id": sessionAt(6, longTextQuestion, operatingSystems),
    },
    prepare: (page: Page) => choose(page, longTextQuestion.options[0].text),
  })),
  {
    mockup: "v1-flow-english-mobile",
    path,
    locale: "en",
    routes: {
      "GET /me": { ...me, locale: "en" },
      "GET /sessions/:id": sessionAt(0, englishQuestion, dataStructures),
    },
    prepare: (page) => choose(page, "Stack"),
  },
  {
    mockup: "v1-flow-code-mobile",
    path,
    routes: {
      "GET /sessions/:id": sessionAt(4, longCodeQuestion, algorithms),
    },
    prepare: (page) => choose(page, "3"),
  },
  {
    mockup: "v1-flow-offline-1-mobile",
    path,
    routes: { "GET /sessions/:id": recursion },
    // The answer is given without a network: it waits on the device.
    prepare: async (page) => {
      await page.context().setOffline(true);
      await choose(page, "24");
      await check(page);
    },
  },
  {
    mockup: "v1-flow-offline-2-mobile",
    path,
    routes: { "GET /sessions/:id": recursion },
    // The connection drops while the student thinks, and comes back.
    prepare: async (page) => {
      await page.context().setOffline(true);
      await choose(page, "24");
      await page.context().setOffline(false);
      await page.getByRole("status").filter({ hasText: "online" }).waitFor();
    },
  },
  ...devices.map((device) => ({
    mockup: `v1-report-${device}`,
    path,
    routes: {
      "GET /sessions/:id": recursion,
      "POST /sessions/:id/answers": answerWrong,
    },
    prepare: async (page: Page) => {
      await answer(page, "16");
      await page.getByRole("button", { name: "Reportar questão" }).click();
      await page.getByRole("radio", { name: "Enunciado ambíguo" }).click();
      await page.mouse.move(0, 0);
    },
  })),
];
