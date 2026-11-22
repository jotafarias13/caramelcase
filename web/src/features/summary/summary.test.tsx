import { QueryClient } from "@tanstack/react-query";
import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router";
import { describe, expect, it } from "vitest";
import { keys } from "@/api/queries";
import type { Locale, SessionSummary } from "@/api/types";
import { AppProviders } from "@/app/providers";
import { Toaster } from "@/components/ui/toaster";
import { initI18n } from "@/i18n";
import {
  SESSION_ID,
  finishedSession,
  guest,
  session,
  summary,
  world,
} from "@/test/fixtures";
import {
  apiError,
  networkFailure,
  type Routes as ApiRoutes,
} from "@/test/mock-api";
import { stubApi } from "@/test/stub-api";
import SummaryPage from "./SummaryPage";

const path = `/session/${SESSION_ID}/summary`;
const never = () => new Promise(() => {});

type Options = { routes?: ApiRoutes; locale?: Locale; cached?: boolean };

/**
 * The summary screen with stand-ins for the pages it leads to, so a test
 * can see where the student went. By default the API answers with the
 * finished session of the fixtures, as on a reload.
 */
function renderSummary({
  routes = {},
  locale = "pt-BR",
  cached,
}: Options = {}) {
  initI18n(locale);
  const api = stubApi(
    world({ "GET /sessions/:id": finishedSession, ...routes }),
  );
  const user = userEvent.setup();
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false, networkMode: "always" },
      mutations: { networkMode: "always" },
    },
  });
  if (cached)
    queryClient.setQueryData(keys.session(SESSION_ID), finishedSession);
  render(
    <AppProviders queryClient={queryClient}>
      <MemoryRouter initialEntries={[path]}>
        <Routes>
          <Route path="/session/:id/summary" element={<SummaryPage />} />
          <Route path="/session/:id" element={<p>session page</p>} />
          <Route path="/home" element={<p>home page</p>} />
          <Route path="/signin" element={<p>sign-in page</p>} />
          <Route path="/subjects" element={<p>subjects page</p>} />
        </Routes>
      </MemoryRouter>
      <Toaster />
    </AppProviders>,
  );
  return { api, user };
}

function finishedWith(changes: Partial<SessionSummary>) {
  return { ...finishedSession, summary: { ...summary, ...changes } };
}

describe("summary: what it shows", () => {
  it("shows the session's numbers after a gain", async () => {
    renderSummary();

    expect(
      await screen.findByRole("heading", { name: "Sessão concluída!" }),
    ).toBeInTheDocument();
    expect(screen.getByText("de 10 certas")).toBeInTheDocument();
    expect(screen.getByText("Mandou bem!")).toBeInTheDocument();
    expect(screen.getByText("+100")).toBeInTheDocument();
    expect(screen.getByText("1254")).toBeInTheDocument();
    expect(screen.getByText("+14")).toBeInTheDocument();
    expect(screen.getByText("7 dias")).toBeInTheDocument();
    expect(
      screen.queryByText(/Seu rating desceu um pouco/),
    ).not.toBeInTheDocument();
  });

  it("shows the level, its XP and this session's share of it", async () => {
    renderSummary();

    const bar = await screen.findByRole("progressbar", { name: "XP do nível" });
    expect(bar).toHaveAttribute("aria-valuenow", "332");
    expect(bar).toHaveAttribute("aria-valuemax", "500");
    expect(screen.getByText("Nível 4")).toBeInTheDocument();
    expect(screen.getByText("+100 XP")).toBeInTheDocument();
    expect(screen.getByText("332 / 500 XP")).toBeInTheDocument();
  });

  it("lists the topics to review with their misses", async () => {
    renderSummary({
      routes: {
        "GET /sessions/:id": finishedWith({
          topics_to_review: [
            { ...summary.topics_to_review[0], wrong_count: 2 },
            summary.topics_to_review[1],
          ],
        }),
      },
    });

    const section = await screen.findByRole("region", {
      name: "Tópicos pra revisar",
    });
    const rows = within(section).getAllByRole("listitem");
    expect(rows).toHaveLength(2);
    expect(rows[0]).toHaveTextContent("Recursão2 erros");
    expect(rows[1]).toHaveTextContent("Busca binária1 erro");
  });

  it("leaves the topics out when nothing was missed", async () => {
    renderSummary({
      routes: {
        "GET /sessions/:id": finishedWith({
          correct_count: 10,
          topics_to_review: [],
        }),
      },
    });

    await screen.findByRole("heading", { name: "Sessão concluída!" });
    expect(
      screen.queryByRole("heading", { name: "Tópicos pra revisar" }),
    ).not.toBeInTheDocument();
  });

  it("speaks calmly after a loss, without the alarm colour", async () => {
    renderSummary({
      routes: {
        "GET /sessions/:id": finishedWith({
          correct_count: 5,
          rating: { ...summary.rating, after: 1231, delta: -9 },
        }),
      },
    });

    expect(
      await screen.findByRole("heading", { name: "Sessão concluída" }),
    ).toBeInTheDocument();
    expect(
      screen.getByText(
        "Dia difícil acontece. As questões que você errou voltam pra revisar.",
      ),
    ).toBeInTheDocument();
    expect(
      screen.getByText(
        "Seu rating desceu um pouco. A próxima sessão vem mais leve e ele volta rápido.",
      ),
    ).toBeInTheDocument();
    expect(screen.getByText("1231")).toBeInTheDocument();
    const delta = screen.getByText("−9").parentElement!;
    expect(delta).toHaveClass("text-fg-muted");
    expect(delta.className).not.toMatch(/wrong/);
  });

  it("counts an unchanged rating as no loss", async () => {
    renderSummary({
      routes: {
        "GET /sessions/:id": finishedWith({
          rating: { ...summary.rating, after: 1240, delta: 0 },
        }),
      },
    });

    expect(
      await screen.findByRole("heading", { name: "Sessão concluída!" }),
    ).toBeInTheDocument();
    expect(screen.getByText("±0")).toBeInTheDocument();
  });

  it("names the new level after a level up", async () => {
    renderSummary({
      routes: {
        "GET /sessions/:id": finishedWith({
          level_before: { ...summary.level_before, xp_in_level: 450 },
          level_after: {
            level: 5,
            total_xp: 2050,
            xp_in_level: 50,
            xp_per_level: 500,
          },
        }),
      },
    });

    expect(await screen.findByText("Subiu de nível!")).toBeInTheDocument();
    expect(screen.getByText("Nível 5")).toBeInTheDocument();
    expect(
      screen.getByRole("progressbar", { name: "XP do nível" }),
    ).toHaveAttribute("aria-valuenow", "500");
  });

  it("speaks English", async () => {
    renderSummary({ locale: "en" });

    expect(
      await screen.findByRole("heading", { name: "Session complete!" }),
    ).toBeInTheDocument();
    expect(screen.getByText("out of 10 correct")).toBeInTheDocument();
    expect(screen.getByText("Binary search")).toBeInTheDocument();
    expect(screen.getAllByText("1 miss")).toHaveLength(2);
  });
});

describe("summary: where the data comes from", () => {
  it("uses the summary the session screen left in the cache", async () => {
    const { api } = renderSummary({
      cached: true,
      routes: { "GET /sessions/:id": apiError(500, "internal_server_error") },
    });

    expect(
      await screen.findByRole("heading", { name: "Sessão concluída!" }),
    ).toBeInTheDocument();
    expect(api.callsTo("GET /sessions/:id")).toHaveLength(0);
  });

  it("sends an unfinished session back to its questions", async () => {
    renderSummary({ routes: { "GET /sessions/:id": session } });

    expect(await screen.findByText("session page")).toBeInTheDocument();
  });

  it("shows the loading state while the session loads", async () => {
    renderSummary({ routes: { "GET /sessions/:id": never } });

    expect(await screen.findByText("Carregando…")).toBeInTheDocument();
  });

  it("shows the error screen when the session cannot be loaded", async () => {
    renderSummary({
      routes: { "GET /sessions/:id": apiError(500, "internal_server_error") },
    });

    expect(
      await screen.findByRole("heading", { name: "Algo deu errado" }),
    ).toBeInTheDocument();
  });

  it("shows the offline screen and retries from it", async () => {
    let online = false;
    const { user } = renderSummary({
      routes: {
        "GET /sessions/:id": () =>
          online ? finishedSession : networkFailure(),
      },
    });

    await screen.findByRole("heading", { name: "Sem conexão" });
    online = true;
    await user.click(screen.getByRole("button", { name: "Tentar de novo" }));

    expect(
      await screen.findByRole("heading", { name: "Sessão concluída!" }),
    ).toBeInTheDocument();
  });
});

describe("summary: what comes next", () => {
  it("starts another session in the same subject", async () => {
    const { api, user } = renderSummary({
      routes: { "POST /sessions": { ...session, id: "next-session" } },
    });

    await user.click(await screen.findByRole("button", { name: "Mais uma" }));

    expect(await screen.findByText("session page")).toBeInTheDocument();
    expect(api.callsTo("POST /sessions")[0].body).toEqual({
      subject: "estruturas-de-dados",
      mode: "practice",
    });
  });

  it("says when another session could not start and stays usable", async () => {
    const { user } = renderSummary({
      routes: { "POST /sessions": apiError(500, "internal_server_error") },
    });

    const button = await screen.findByRole("button", { name: "Mais uma" });
    await user.click(button);

    expect(
      await screen.findByText("Não deu pra começar a sessão. Tenta de novo."),
    ).toBeInTheDocument();
    await waitFor(() => expect(button).toBeEnabled());
  });

  it("goes back to Home", async () => {
    const { user } = renderSummary();

    await user.click(
      await screen.findByRole("button", { name: "Voltar pro início" }),
    );

    expect(await screen.findByText("home page")).toBeInTheDocument();
  });

  it("closes to Home", async () => {
    const { user } = renderSummary();

    await user.click(await screen.findByRole("button", { name: "Fechar" }));

    expect(await screen.findByText("home page")).toBeInTheDocument();
  });
});

describe("summary: the prompt to save progress", () => {
  const firstForGuest: ApiRoutes = {
    "GET /me": guest,
    "GET /sessions/:id": finishedWith({ sessions_finished: 1 }),
  };

  it("asks a guest after the first finished session", async () => {
    const { user } = renderSummary({ routes: firstForGuest });

    const dialog = await screen.findByRole("dialog", {
      name: "Quer salvar esse progresso?",
    });
    await user.click(
      within(dialog).getByRole("button", { name: "Salvar meu progresso" }),
    );

    expect(await screen.findByText("sign-in page")).toBeInTheDocument();
  });

  it("goes away with Agora não", async () => {
    const { user } = renderSummary({ routes: firstForGuest });

    await user.click(await screen.findByRole("button", { name: "Agora não" }));

    await waitFor(() =>
      expect(
        screen.queryByRole("dialog", { name: "Quer salvar esse progresso?" }),
      ).not.toBeInTheDocument(),
    );
    expect(
      screen.getByRole("heading", { name: "Sessão concluída!" }),
    ).toBeInTheDocument();
  });

  it("does not ask again after a later session", async () => {
    renderSummary({
      routes: {
        "GET /me": guest,
        "GET /sessions/:id": finishedWith({ sessions_finished: 2 }),
      },
    });

    await screen.findByRole("heading", { name: "Sessão concluída!" });
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("does not ask someone who is signed in", async () => {
    renderSummary({
      routes: { "GET /sessions/:id": finishedWith({ sessions_finished: 1 }) },
    });

    await screen.findByRole("heading", { name: "Sessão concluída!" });
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });
});

describe("summary: what the numbers mean", () => {
  const hint = () => screen.queryByRole("dialog", { name: "Explicação" });

  it("explains XP and then the rating, once", async () => {
    const { user } = renderSummary();

    await waitFor(() =>
      expect(hint()).toHaveTextContent(
        "XP mede esforço e só sobe: 10 por acerto, um bônus nas questões mais difíceis e 10 por sessão concluída. A cada 500 XP você sobe de nível.",
      ),
    );
    await user.click(screen.getByRole("button", { name: "Entendi" }));
    expect(hint()).toHaveTextContent("Rating é o seu nível em cada matéria.");
    await user.click(screen.getByRole("button", { name: "Entendi" }));
    expect(hint()).not.toBeInTheDocument();
    expect(JSON.parse(localStorage.getItem("caramelcase.hints") ?? "")).toEqual(
      ["xp", "rating"],
    );
  });

  it("explains the streak when its card is tapped", async () => {
    localStorage.setItem("caramelcase.hints", JSON.stringify(["xp", "rating"]));
    const { user } = renderSummary();

    await user.click(await screen.findByRole("button", { name: /sequência/ }));

    expect(hint()).toHaveTextContent(
      "Uma sessão concluída no dia já conta, mesmo sem bater a meta.",
    );
  });

  it("waits for the prompt to save progress to close", async () => {
    const { user } = renderSummary({
      routes: {
        "GET /me": guest,
        "GET /sessions/:id": finishedWith({ sessions_finished: 1 }),
      },
    });

    await screen.findByRole("dialog", { name: "Quer salvar esse progresso?" });
    expect(hint()).not.toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Agora não" }));
    await waitFor(() => expect(hint()).toHaveTextContent("XP mede esforço"));
  });
});
