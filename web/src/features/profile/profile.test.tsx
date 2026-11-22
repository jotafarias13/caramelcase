import { screen, waitFor, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import type { Activity } from "@/api/types";
import { activity, guest, me, stats, subjectDetail } from "@/test/fixtures";
import { apiError } from "@/test/mock-api";
import { renderApp } from "@/test/render";
import { calendarMonth, weekdayLetters } from "./calendar";
import { masteryPercent } from "./mastery";

const never = () => new Promise(() => {});

/** The number in a stat tile, found by its label. */
function tile(label: string): string | null | undefined {
  return screen.getByText(label).nextElementSibling?.textContent;
}

describe("profile: who and how far", () => {
  it("shows the name, the studies, the level and the totals", async () => {
    renderApp("/profile");

    expect(
      await screen.findByRole("heading", { level: 1, name: "Carol Nunes" }),
    ).toBeInTheDocument();
    expect(
      screen.getByText("Ciência da Computação · Sua universidade"),
    ).toBeInTheDocument();
    expect(screen.getByText("Nível 4")).toBeInTheDocument();
    expect(screen.getByText("320 / 500 XP")).toBeInTheDocument();
    expect(tile("questões")).toBe("220");
    expect(tile("acertos")).toBe("78%");
    expect(tile("sessões")).toBe("22");
    expect(tile("melhor sequência")).toBe("12 dias");
  });

  it("calls a student without a name, course or university by the screen's name", async () => {
    renderApp("/profile", { routes: { "GET /me": guest } });

    expect(
      await screen.findByRole("heading", { level: 1, name: "Perfil" }),
    ).toBeInTheDocument();
    expect(screen.queryByText(/·/)).not.toBeInTheDocument();
  });

  it("shows only the part of the studies the student gave", async () => {
    renderApp("/profile", {
      routes: { "GET /me": { ...me, university: null } },
    });

    expect(
      await screen.findByText("Ciência da Computação"),
    ).toBeInTheDocument();
  });

  it("says one day for a best streak of one", async () => {
    renderApp("/profile", {
      routes: {
        "GET /me/stats": {
          ...stats,
          streak: { ...stats.streak, current: 1, longest: 1 },
        },
      },
    });

    await screen.findByText("melhor sequência");
    expect(tile("melhor sequência")).toBe("1 dia");
  });
});

describe("profile: rating and mastery", () => {
  it("shows the rating in each subject, or that it was not practiced", async () => {
    renderApp("/profile");

    const card = (
      await screen.findByRole("heading", { name: "Rating por matéria" })
    ).parentElement!;
    const rows = within(card).getAllByRole("listitem");
    expect(rows.map((row) => row.textContent)).toEqual([
      "Introdução à ProgramaçãoAinda não praticou",
      "Estruturas de Dados1240",
      "Banco de Dados1102",
    ]);
    expect(within(card).getByLabelText("Rating: 1240")).toBeInTheDocument();
  });

  it("fills each topic's bar as its state on Home", async () => {
    renderApp("/profile");

    await screen.findByRole("heading", { name: "Domínio por tópico" });
    expect(screen.getByText("estruturas de dados")).toBeInTheDocument();
    const bar = (name: string) =>
      screen.getByRole("progressbar", { name }).getAttribute("aria-valuenow");
    expect(bar("Pilhas e filas")).toBe("100");
    expect(bar("Listas ligadas")).toBe("40");
    expect(bar("Árvores binárias")).toBe("0");
  });

  it("leaves the mastery card out when the current subject is gone", async () => {
    renderApp("/profile", {
      routes: { "GET /subjects/:slug": apiError(404, "subject_not_found") },
    });

    await screen.findByRole("heading", { name: "Rating por matéria" });
    expect(
      screen.queryByRole("heading", { name: "Domínio por tópico" }),
    ).not.toBeInTheDocument();
  });
});

describe("profile: calendar", () => {
  it("names the month and the weekdays in the interface language", async () => {
    renderApp("/profile");

    expect(await screen.findByText("novembro de 2026")).toBeInTheDocument();
    expect(screen.getAllByText("Q")).toHaveLength(2);
  });

  it("uses English names in English", async () => {
    renderApp("/profile", {
      locale: "en",
      routes: { "GET /me": { ...me, locale: "en" } },
    });

    expect(await screen.findByText("November 2026")).toBeInTheDocument();
    expect(screen.getAllByText("W")).toHaveLength(1);
  });

  it("marks the days with practice and today", async () => {
    renderApp("/profile");

    await screen.findByText("novembro de 2026");
    // Days 3, 4, 6, 7 and 11 to 17 of the fixture.
    expect(screen.getAllByText("dia com prática")).toHaveLength(12);
    const today = screen.getAllByText("hoje")[0].parentElement!;
    expect(today).toHaveTextContent(/^17/);
  });
});

describe("profile: states", () => {
  it("shows the loading state while the numbers load", async () => {
    renderApp("/profile", { routes: { "GET /me/stats": never } });

    expect(await screen.findByText("Carregando…")).toBeInTheDocument();
  });

  it("shows the error screen when the activity fails", async () => {
    renderApp("/profile", {
      routes: { "GET /me/activity": apiError(500, "internal_server_error") },
    });

    expect(
      await screen.findByRole("heading", { name: "Algo deu errado" }),
    ).toBeInTheDocument();
  });

  it("before the first answer, offers the first session", async () => {
    const { api, user } = renderApp("/profile", {
      routes: { "GET /me/stats": { ...stats, questions_answered: 0 } },
    });

    expect(
      await screen.findByRole("heading", { name: "Nada por aqui ainda" }),
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("heading", { name: "Rating por matéria" }),
    ).not.toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Bora praticar" }));

    await waitFor(() => expect(api.callsTo("POST /sessions")).toHaveLength(1));
    expect(api.callsTo("POST /sessions")[0].body).toEqual({
      subject: "estruturas-de-dados",
      mode: "practice",
    });
  });
});

describe("profile: rules", () => {
  it("lays out a month from its first weekday", () => {
    const month = calendarMonth(activity);
    expect(month.leadingBlanks).toBe(0); // 1 November 2026 is a Sunday.
    expect(month.days).toHaveLength(30);
    expect(month.days[2]).toMatchObject({ day: 3, state: "practiced" });
    expect(month.days[4]).toMatchObject({ day: 5, state: "idle" });
    expect(month.days[16]).toMatchObject({ day: 17, isToday: true });
    expect(month.days[17]).toMatchObject({ day: 18, state: "future" });

    const february: Activity = {
      start: "2028-02-01",
      end: "2028-02-29",
      today: "2028-02-10",
      days: [],
    };
    const leap = calendarMonth(february);
    expect(leap.leadingBlanks).toBe(2); // A Tuesday.
    expect(leap.days).toHaveLength(29);
  });

  it("starts the week on Sunday in both languages", () => {
    expect(weekdayLetters("pt-BR")).toEqual([
      "D",
      "S",
      "T",
      "Q",
      "Q",
      "S",
      "S",
    ]);
    expect(weekdayLetters("en")).toEqual(["S", "M", "T", "W", "T", "F", "S"]);
  });

  it("fills a mastered topic, shows accuracy in progress and nothing when new", () => {
    const [mastered, learning, fresh] = subjectDetail.topics;
    expect(masteryPercent(mastered)).toBe(100);
    expect(masteryPercent(learning)).toBe(40);
    expect(
      masteryPercent({ ...learning, mastery: "practiced", accuracy: 0.726 }),
    ).toBe(73);
    expect(
      masteryPercent({ ...fresh, correct: 2, total: 3, accuracy: 0.67 }),
    ).toBe(0);
  });
});

describe("profile: what XP is", () => {
  it("explains XP from the level bar", async () => {
    const { user } = renderApp("/profile");

    await user.click(
      await screen.findByRole("button", { name: "O que é XP?" }),
    );

    expect(
      screen.getByRole("dialog", { name: "Explicação" }),
    ).toHaveTextContent("XP mede esforço e só sobe");
  });
});
