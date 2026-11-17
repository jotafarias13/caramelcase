import { screen, waitFor, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import type { Stats, Streak } from "@/api/types";
import { guest, me, stats, subjectDetail } from "@/test/fixtures";
import { apiError } from "@/test/mock-api";
import { renderApp } from "@/test/render";

function withStreak(streak: Streak): Stats {
  return { ...stats, streak };
}

const never = () => new Promise(() => {});

describe("home: greeting and data", () => {
  it("greets the student by the first word of the name", async () => {
    renderApp("/home");

    expect(
      await screen.findByRole("heading", { name: "E aí, Carol!" }),
    ).toBeInTheDocument();
  });

  it("greets a student without a name", async () => {
    renderApp("/home", { routes: { "GET /me": guest } });

    expect(
      await screen.findByRole("heading", { name: "E aí!" }),
    ).toBeInTheDocument();
  });

  it("shows the loading state while the subject loads", async () => {
    renderApp("/home", { routes: { "GET /subjects/:slug": never } });

    expect(await screen.findByText("Carregando…")).toBeInTheDocument();
    expect(
      screen.queryByRole("heading", { name: "E aí, Carol!" }),
    ).not.toBeInTheDocument();
  });

  it("asks for another subject when the current one is gone", async () => {
    renderApp("/home", {
      routes: { "GET /subjects/:slug": apiError(404, "subject_not_found") },
    });

    expect(
      await screen.findByRole("heading", { name: "Escolha uma matéria" }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: "Ver todas as matérias" }),
    ).toHaveAttribute("href", "/subjects");
  });

  it("shows the error screen when the stats fail", async () => {
    renderApp("/home", {
      routes: { "GET /me/stats": apiError(500, "internal_server_error") },
    });

    expect(
      await screen.findByRole("heading", { name: "Algo deu errado" }),
    ).toBeInTheDocument();
  });
});

describe("home: goal card", () => {
  it("shows what is left of today's goal and the next topic", async () => {
    renderApp("/home");

    expect(await screen.findByText("Faltam 8 questões")).toBeInTheDocument();
    expect(screen.getByText("Próximo: Listas ligadas")).toBeInTheDocument();
    expect(
      screen.getByRole("img", { name: "Meta de hoje: 12 de 20 questões" }),
    ).toBeInTheDocument();
  });

  it("says when today's goal is met", async () => {
    renderApp("/home", {
      routes: {
        "GET /me/stats": {
          ...stats,
          goal: { goal: 20, questions: 23, remaining: 0, met: true },
        },
      },
    });

    await screen.findByRole("heading", { name: "E aí, Carol!" });
    expect(screen.getAllByText("Meta de hoje batida").length).toBeGreaterThan(
      0,
    );
    expect(screen.queryByText(/Faltam/)).not.toBeInTheDocument();
  });

  it("starts practice in the current subject and opens the session", async () => {
    const { api, user } = renderApp("/home");

    await user.click(await screen.findByRole("button", { name: "Continuar" }));

    await waitFor(() => expect(api.callsTo("POST /sessions")).toHaveLength(1));
    expect(api.callsTo("POST /sessions")[0].body).toEqual({
      subject: "estruturas-de-dados",
      mode: "practice",
    });
    await waitFor(() =>
      expect(
        screen.queryByRole("heading", { name: "E aí, Carol!" }),
      ).not.toBeInTheDocument(),
    );
  });

  it("says when the subject has no questions and offers to switch", async () => {
    const { user } = renderApp("/home", {
      routes: { "POST /sessions": apiError(409, "no_questions") },
    });

    const button = await screen.findByRole("button", { name: "Continuar" });
    await user.click(button);

    expect(
      await screen.findByText(
        "Essa matéria ainda não tem questões pra você. Escolha outra.",
      ),
    ).toBeInTheDocument();
    expect(button).toBeEnabled();

    await user.click(screen.getByRole("button", { name: "Trocar" }));
    expect(
      await screen.findByRole("dialog", { name: "Trocar matéria" }),
    ).toBeInTheDocument();
  });

  it("says when a session could not start for another reason", async () => {
    const { user } = renderApp("/home", {
      routes: { "POST /sessions": apiError(500, "internal_server_error") },
    });

    await user.click(await screen.findByRole("button", { name: "Continuar" }));

    expect(
      await screen.findByText("Não deu pra começar a sessão. Tenta de novo."),
    ).toBeInTheDocument();
  });
});

describe("home: topics", () => {
  it("draws each topic from its mastery", async () => {
    renderApp("/home");

    const topics = await screen.findByRole("region", { name: "Tópicos" });
    const rows = within(topics).getAllByRole("button");
    expect(rows).toHaveLength(subjectDetail.topics.length);
    expect(rows[0]).toHaveTextContent("Pilhas e filasDominado");
    expect(rows[1]).toHaveTextContent("Listas ligadasEm andamento40%");
    expect(rows[2]).toHaveTextContent("Árvores bináriasComeçar");
  });

  it("starts a session of the subject when a topic is tapped", async () => {
    const { api, user } = renderApp("/home");

    await user.click(
      await screen.findByRole("button", { name: /Tabelas hash/ }),
    );

    await waitFor(() => expect(api.callsTo("POST /sessions")).toHaveLength(1));
    expect(api.callsTo("POST /sessions")[0].body).toMatchObject({
      subject: "estruturas-de-dados",
    });
  });
});

describe("home: streak", () => {
  it("warns when the streak is at risk and starts practice from there", async () => {
    const { api, user } = renderApp("/home", {
      routes: {
        "GET /me/stats": withStreak({
          current: 7,
          longest: 12,
          status: "at_risk",
          lost_length: null,
        }),
      },
    });

    expect(
      await screen.findByText(
        "Sua sequência de 7 dias acaba hoje à meia-noite.",
      ),
    ).toBeInTheDocument();
    expect(
      screen.getByText("Pratique hoje pra não perder"),
    ).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Praticar agora" }));
    await waitFor(() => expect(api.callsTo("POST /sessions")).toHaveLength(1));
  });

  it("says how long the lost streak was", async () => {
    renderApp("/home", {
      routes: {
        "GET /me/stats": withStreak({
          current: 0,
          longest: 12,
          status: "lost",
          lost_length: 7,
        }),
      },
    });

    expect(
      await screen.findByText(
        "Sua sequência de 7 dias terminou. Acontece. Bora começar outra?",
      ),
    ).toBeInTheDocument();
    expect(screen.getByText("Sequência perdida")).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Bora praticar" }),
    ).toBeInTheDocument();
  });

  it("celebrates the first day", async () => {
    renderApp("/home", {
      routes: {
        "GET /me/stats": withStreak({
          current: 1,
          longest: 1,
          status: "active",
          lost_length: null,
        }),
      },
    });

    expect(
      await screen.findByText(
        "Sua sequência começou. Volte amanhã pra manter.",
      ),
    ).toBeInTheDocument();
    expect(screen.getByText("Começou hoje")).toBeInTheDocument();
  });

  it("names the goal under an extended streak only when it is met", async () => {
    renderApp("/home");

    expect(await screen.findByText("7 dias seguidos")).toBeInTheDocument();
    expect(screen.getByText("Praticou hoje")).toBeInTheDocument();
    expect(screen.queryByText(/Bora começar outra/)).not.toBeInTheDocument();
  });

  it("shows no streak before the first session", async () => {
    renderApp("/home", {
      routes: {
        "GET /me/stats": withStreak({
          current: 0,
          longest: 0,
          status: "none",
          lost_length: null,
        }),
      },
    });

    await screen.findByRole("heading", { name: "E aí, Carol!" });
    expect(screen.queryByText(/dias seguidos/)).not.toBeInTheDocument();
    expect(screen.queryByText("Sequência perdida")).not.toBeInTheDocument();
  });
});

describe("home: rating card", () => {
  it("shows the last change, with what a gain means", async () => {
    renderApp("/home");

    expect(
      await screen.findByText("rating · estruturas de dados"),
    ).toBeInTheDocument();
    expect(screen.getByText("+14")).toBeInTheDocument();
    expect(
      screen.getByText("Subiu. Vêm questões mais difíceis."),
    ).toBeInTheDocument();
  });

  it("shows a loss calmly", async () => {
    renderApp("/home", {
      routes: {
        "GET /me/stats": {
          ...stats,
          last_rating_change: {
            ...stats.last_rating_change!,
            before: 1240,
            after: 1231,
            delta: -9,
          },
        },
      },
    });

    expect(await screen.findByText("−9")).toBeInTheDocument();
    expect(
      screen.getByText(
        "Seu rating desceu um pouco. A próxima sessão vem mais leve e ele volta rápido.",
      ),
    ).toBeInTheDocument();
  });
});

describe("home: subject switcher", () => {
  it("opens a sheet with the subjects and switches to the one chosen", async () => {
    const { api, user } = renderApp("/home");

    await user.click(
      await screen.findByRole("button", {
        name: "Trocar matéria. Atual: Estruturas de Dados",
      }),
    );
    const sheet = await screen.findByRole("dialog", { name: "Trocar matéria" });
    expect(
      within(sheet).getByRole("radio", { name: /Estruturas de Dados/ }),
    ).toBeChecked();
    expect(
      within(sheet).getByRole("link", { name: "Ver todas as matérias" }),
    ).toHaveAttribute("href", "/subjects");

    await user.click(
      within(sheet).getByRole("radio", { name: /Banco de Dados/ }),
    );

    await waitFor(() =>
      expect(api.callsTo("PATCH /me/settings")).toHaveLength(1),
    );
    expect(api.callsTo("PATCH /me/settings")[0].body).toEqual({
      current_subject: "banco-de-dados",
    });
    await waitFor(() =>
      expect(screen.queryByRole("dialog")).not.toBeInTheDocument(),
    );
  });

  it("names the subject in the account's language", async () => {
    renderApp("/home", { routes: { "GET /me": { ...me, locale: "en" } } });

    expect(
      await screen.findByRole("button", {
        name: "Switch subject. Current: Data Structures",
      }),
    ).toBeInTheDocument();
  });
});
