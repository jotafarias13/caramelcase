import { screen, waitFor } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { currentLocale } from "@/i18n";
import { me, newGuest } from "@/test/fixtures";
import { apiError } from "@/test/mock-api";
import { renderApp } from "@/test/render";

const firstVisit = { "GET /me": newGuest };

async function findTitle(name: string) {
  return screen.findByRole("heading", { name });
}

describe("onboarding", () => {
  it("walks through the four steps and saves everything in one call", async () => {
    const { api, user } = renderApp("/start", { routes: firstVisit });

    await findTitle("Em que idioma você quer praticar?");
    await user.click(screen.getByRole("button", { name: "Continuar" }));

    await findTitle("Onde você estuda?");
    await user.type(screen.getByLabelText("Universidade"), " UFRN ");
    await user.type(screen.getByLabelText("Curso"), "Ciência da Computação");
    await user.click(screen.getByRole("button", { name: "Continuar" }));

    await findTitle("Por onde quer começar?");
    await user.click(screen.getByRole("radio", { name: "Banco de Dados" }));
    await user.click(screen.getByRole("button", { name: "Continuar" }));

    await findTitle("Qual é a sua meta diária?");
    await user.click(
      screen.getByRole("radio", { name: /30 questões por dia/ }),
    );
    await user.click(screen.getByRole("button", { name: "Bora praticar" }));

    await waitFor(() => expect(api.callsTo("POST /sessions")).toHaveLength(1));
    const patches = api.callsTo("PATCH /me/settings");
    expect(patches).toHaveLength(1);
    expect(patches[0].body).toEqual({
      university: "UFRN",
      course: "Ciência da Computação",
      current_subject: "banco-de-dados",
      daily_goal: 30,
    });
    expect(api.callsTo("POST /sessions")[0].body).toEqual({
      subject: "banco-de-dados",
      mode: "practice",
    });
  });

  it("starts the first session when it finishes", async () => {
    const { user } = renderApp("/start?step=4", { routes: firstVisit });

    await user.click(
      await screen.findByRole("button", { name: "Bora praticar" }),
    );

    // The step bar is gone, and the session screen has no navigation,
    // unlike Home.
    await waitFor(() =>
      expect(
        screen.queryByRole("progressbar", { name: "Etapa" }),
      ).not.toBeInTheDocument(),
    );
    expect(
      screen.queryByRole("navigation", { name: "Principal" }),
    ).not.toBeInTheDocument();
  });

  it("goes Home when the first session cannot start", async () => {
    const { user } = renderApp("/start?step=4", {
      routes: {
        ...firstVisit,
        "POST /sessions": apiError(409, "no_questions"),
      },
    });

    await user.click(
      await screen.findByRole("button", { name: "Bora praticar" }),
    );

    expect(
      (await screen.findAllByRole("navigation", { name: "Principal" })).length,
    ).toBeGreaterThan(0);
  });

  it("stays on the last step and says so when saving fails", async () => {
    const { api, user } = renderApp("/start?step=4", {
      routes: {
        ...firstVisit,
        "PATCH /me/settings": apiError(500, "internal_server_error"),
      },
    });

    await user.click(
      await screen.findByRole("button", { name: "Bora praticar" }),
    );

    expect(
      await screen.findByText("Não deu pra salvar. Tenta de novo."),
    ).toBeInTheDocument();
    expect(screen.getByRole("heading")).toHaveTextContent(
      "Qual é a sua meta diária?",
    );
    expect(api.callsTo("POST /sessions")).toHaveLength(0);
  });

  it("changes the language at once on the first step", async () => {
    const { api, user } = renderApp("/start", { routes: firstVisit });

    await user.click(await screen.findByRole("radio", { name: "English" }));

    expect(
      await findTitle("Which language do you want to practice in?"),
    ).toBeInTheDocument();
    expect(currentLocale()).toBe("en");
    await waitFor(() =>
      expect(api.callsTo("PATCH /me/settings")[0]?.body).toEqual({
        locale: "en",
      }),
    );
  });

  it("stores nothing for university and course when step 2 is skipped", async () => {
    const { api, user } = renderApp("/start?step=2", { routes: firstVisit });

    await user.type(await screen.findByLabelText("Universidade"), "UFRN");
    await user.click(screen.getByRole("button", { name: "Pular" }));
    await findTitle("Por onde quer começar?");
    await user.click(screen.getByRole("button", { name: "Continuar" }));
    await user.click(
      await screen.findByRole("button", { name: "Bora praticar" }),
    );

    await waitFor(() =>
      expect(api.callsTo("PATCH /me/settings")).toHaveLength(1),
    );
    expect(api.callsTo("PATCH /me/settings")[0].body).toMatchObject({
      university: null,
      course: null,
    });
  });

  it("goes back to the previous step", async () => {
    const { user } = renderApp("/start?step=3", { routes: firstVisit });

    await findTitle("Por onde quer começar?");
    await user.click(screen.getByRole("button", { name: "Voltar" }));

    expect(await findTitle("Onde você estuda?")).toBeInTheDocument();
  });

  it("has no way back on the first step", async () => {
    renderApp("/start", { routes: firstVisit });

    await findTitle("Em que idioma você quer praticar?");
    expect(
      screen.queryByRole("button", { name: "Voltar" }),
    ).not.toBeInTheDocument();
  });

  it("selects the first subject and a goal of 20 to begin with", async () => {
    const { user } = renderApp("/start?step=3", { routes: firstVisit });

    expect(
      await screen.findByRole("radio", { name: "Introdução à Programação" }),
    ).toBeChecked();
    await user.click(screen.getByRole("button", { name: "Continuar" }));

    expect(
      await screen.findByRole("radio", { name: /20 questões por dia/ }),
    ).toBeChecked();
    expect(
      screen.getByRole("radio", { name: /Duas sessões · cerca de 10 min/ }),
    ).toBeInTheDocument();
  });

  it("shows the step in the progress bar", async () => {
    renderApp("/start?step=2", { routes: firstVisit });

    expect(
      await screen.findByRole("progressbar", { name: "Etapa" }),
    ).toHaveAttribute("aria-valuenow", "2");
    expect(screen.getByText("etapa 2 de 4")).toBeInTheDocument();
  });

  it("sends someone who already chose a subject Home", async () => {
    renderApp("/start", { routes: { "GET /me": me } });

    expect(
      (await screen.findAllByRole("navigation", { name: "Principal" })).length,
    ).toBeGreaterThan(0);
  });

  it("shows the failure state when the subjects do not load", async () => {
    renderApp("/start?step=3", {
      routes: {
        ...firstVisit,
        "GET /subjects": apiError(500, "internal_server_error"),
      },
    });

    expect(await findTitle("Algo deu errado")).toBeInTheDocument();
  });

  it("says so when no subject is open yet", async () => {
    renderApp("/start?step=3", {
      routes: { ...firstVisit, "GET /subjects": { subjects: [] } },
    });

    expect(await findTitle("Nenhuma matéria aberta ainda")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Continuar" })).toBeDisabled();
  });
});
