import { QueryClient } from "@tanstack/react-query";
import { act, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router";
import { afterEach, describe, expect, it, vi } from "vitest";
import { AppProviders } from "@/app/providers";
import { Toaster } from "@/components/ui/toaster";
import { initI18n } from "@/i18n";
import {
  SESSION_ID,
  answerCorrect,
  answerWrong,
  codeQuestion,
  me,
  session,
  sessionAnswered,
} from "@/test/fixtures";
import {
  apiError,
  networkFailure,
  type Routes as ApiRoutes,
} from "@/test/mock-api";
import { stubApi } from "@/test/stub-api";
import { world } from "@/test/fixtures";
import SessionPage from "./SessionPage";

const path = `/session/${SESSION_ID}`;
const savedKey = `caramelcase.answer.${SESSION_ID}.${codeQuestion.id}`;

/**
 * The session screen as renderApp would show it, with stand-ins for the
 * pages it leads to, so a test can see where the student went.
 */
function renderSession(routes: ApiRoutes = {}) {
  initI18n("pt-BR");
  const api = stubApi(world(routes));
  const user = userEvent.setup();
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false, networkMode: "always" },
      mutations: { networkMode: "always" },
    },
  });
  render(
    <AppProviders queryClient={queryClient}>
      <MemoryRouter initialEntries={[path]}>
        <Routes>
          <Route path="/session/:id" element={<SessionPage />} />
          <Route path="/session/:id/summary" element={<p>summary page</p>} />
          <Route path="/home" element={<p>home page</p>} />
        </Routes>
      </MemoryRouter>
      <Toaster />
    </AppProviders>,
  );
  return { api, user };
}

function option(name: string | RegExp) {
  return screen.getByRole("radio", { name });
}

async function answerWith(
  user: ReturnType<typeof userEvent.setup>,
  text: string,
) {
  await user.click(await screen.findByRole("radio", { name: text }));
  await user.click(screen.getByRole("button", { name: "Verificar" }));
  await screen.findByRole("button", { name: "Continuar" });
}

afterEach(() => {
  vi.restoreAllMocks();
});

describe("where the session starts", () => {
  it("resumes at the first question without an answer", async () => {
    renderSession({ "GET /sessions/:id": sessionAnswered(3) });

    const progress = await screen.findByRole("progressbar", {
      name: "Progresso da sessão",
    });
    expect(progress).toHaveAttribute("aria-valuenow", "3");
    expect(screen.getByText("4/10")).toBeInTheDocument();
    expect(
      screen.getByRole("heading", {
        level: 1,
        name: session.questions[3].stem,
      }),
    ).toBeInTheDocument();
  });

  it("sends a finished session to its summary", async () => {
    renderSession({
      "GET /sessions/:id": {
        ...sessionAnswered(10),
        finished_at: "2026-11-17T18:05:00Z",
      },
    });

    expect(await screen.findByText("summary page")).toBeInTheDocument();
  });

  it("finishes a session whose questions were all answered", async () => {
    const { api } = renderSession({ "GET /sessions/:id": sessionAnswered(10) });

    expect(await screen.findByText("summary page")).toBeInTheDocument();
    expect(api.callsTo("POST /sessions/:id/finish")).toHaveLength(1);
  });

  it("shows the 404 screen for a session that does not exist", async () => {
    renderSession({ "GET /sessions/:id": apiError(404, "session_not_found") });

    expect(await screen.findByText("Essa página fugiu")).toBeInTheDocument();
  });

  it("leaves for home without asking", async () => {
    const { user } = renderSession();

    await user.click(
      await screen.findByRole("link", { name: "Sair da sessão" }),
    );

    expect(await screen.findByText("home page")).toBeInTheDocument();
  });
});

describe("answering", () => {
  it("keeps Verificar disabled until an option is chosen", async () => {
    const { user } = renderSession();

    const check = await screen.findByRole("button", { name: "Verificar" });
    expect(check).toBeDisabled();
    await user.click(option("24"));

    expect(option("24")).toHaveAttribute("aria-checked", "true");
    expect(check).toBeEnabled();
  });

  it("chooses with keys 1 to 4, checks with Enter and continues with Enter", async () => {
    const { api, user } = renderSession();
    await screen.findByRole("radiogroup", { name: "Alternativas" });

    await user.keyboard("2");
    expect(option("24")).toHaveAttribute("aria-checked", "true");
    await user.keyboard("{Enter}");

    await screen.findByText("Mandou bem!");
    const [request] = api.callsTo("POST /sessions/:id/answers");
    expect(request.body).toEqual({
      question_id: codeQuestion.id,
      key: "b",
      time_ms: expect.any(Number),
    });

    await user.keyboard("{Enter}");
    expect(await screen.findByText("2/10")).toBeInTheDocument();
  });

  it("shows the reason under every option when the setting is on", async () => {
    const { user } = renderSession();

    await answerWith(user, "24");

    expect(option(/^24/)).toHaveTextContent("Correta");
    expect(screen.getByText("f(4) = 4 × 3 × 2 × 1 = 24.")).toBeInTheDocument();
    expect(screen.getByText(/10 seria a soma/)).toBeInTheDocument();
    expect(screen.queryByText(answerCorrect.explanation)).toBeNull();
    expect(screen.getByText("+10 XP")).toBeInTheDocument();
  });

  it("shows the explanation instead when reasons are off", async () => {
    const { user } = renderSession({
      "GET /me": {
        ...me,
        settings: { ...me.settings, show_option_reasons: false },
      },
      "POST /sessions/:id/answers": answerWrong,
    });

    await answerWith(user, "16");

    expect(screen.getByText(answerWrong.explanation)).toBeInTheDocument();
    expect(screen.queryByText(/10 seria a soma/)).toBeNull();
  });

  it("marks a wrong answer and the right one", async () => {
    const { user } = renderSession({
      "POST /sessions/:id/answers": answerWrong,
    });

    await answerWith(user, "16");

    expect(screen.getByText("Quase. Olha só o porquê:")).toBeInTheDocument();
    expect(option(/^16/)).toHaveTextContent("Sua resposta");
    expect(option(/^24/)).toHaveTextContent("Resposta certa");
  });

  it("finishes the session after the last question", async () => {
    const { api, user } = renderSession({
      "GET /sessions/:id": sessionAnswered(9),
      "POST /sessions/:id/answers": {
        ...answerCorrect,
        session_complete: true,
      },
    });

    await answerWith(user, "O(log n)");
    await user.click(screen.getByRole("button", { name: "Continuar" }));

    expect(await screen.findByText("summary page")).toBeInTheDocument();
    expect(api.callsTo("POST /sessions/:id/finish")).toHaveLength(1);
  });
});

describe("reporting a question", () => {
  it("sends the reason and the details, then says thanks", async () => {
    const { api, user } = renderSession();
    await answerWith(user, "24");

    await user.click(screen.getByRole("button", { name: "Reportar questão" }));
    const dialog = await screen.findByRole("dialog", {
      name: "Reportar questão",
    });
    const send = within(dialog).getByRole("button", { name: "Enviar" });
    expect(send).toBeDisabled();
    await user.click(
      within(dialog).getByRole("radio", { name: "Enunciado ambíguo" }),
    );
    await user.type(
      within(dialog).getByLabelText("Detalhes (opcional)"),
      "Duas leituras possíveis",
    );
    await user.click(send);

    expect(await screen.findByText(/Valeu pelo aviso/)).toBeInTheDocument();
    const [request] = api.callsTo("POST /questions/:id/report");
    expect(request.params.id).toBe(codeQuestion.id);
    expect(request.body).toEqual({
      reason: "ambiguous_wording",
      comment: "Duas leituras possíveis",
    });
    await waitFor(() => expect(screen.queryByRole("dialog")).toBeNull());
  });
});

describe("rate limits", () => {
  it("says to wait when the answer is refused for coming too fast", async () => {
    const { user } = renderSession({
      "POST /sessions/:id/answers": apiError(429, "rate_limited"),
    });

    await user.click(await screen.findByRole("radio", { name: "24" }));
    await user.click(screen.getByRole("button", { name: "Verificar" }));

    expect(
      await screen.findByText(/Muitas tentativas seguidas/),
    ).toBeInTheDocument();
    expect(option("24")).toBeChecked();
    expect(
      screen.queryByRole("button", { name: "Continuar" }),
    ).not.toBeInTheDocument();
  });

  it("says to wait when a report is refused for coming too fast", async () => {
    const { user } = renderSession({
      "POST /questions/:id/report": apiError(429, "rate_limited"),
    });
    await answerWith(user, "24");

    await user.click(screen.getByRole("button", { name: "Reportar questão" }));
    const dialog = await screen.findByRole("dialog", {
      name: "Reportar questão",
    });
    await user.click(within(dialog).getByRole("radio", { name: "Outro" }));
    await user.click(within(dialog).getByRole("button", { name: "Enviar" }));

    expect(
      await screen.findByText(/Muitas tentativas seguidas/),
    ).toBeInTheDocument();
    expect(screen.getByRole("dialog")).toBeInTheDocument();
  });
});

describe("offline", () => {
  function goOffline() {
    const onLine = vi.spyOn(navigator, "onLine", "get").mockReturnValue(false);
    act(() => {
      window.dispatchEvent(new Event("offline"));
    });
    return () => {
      onLine.mockReturnValue(true);
      act(() => {
        window.dispatchEvent(new Event("online"));
      });
    };
  }

  it("keeps the answer on the device and sends it when the network returns", async () => {
    const { api, user } = renderSession();
    await screen.findByRole("radiogroup", { name: "Alternativas" });
    const goOnline = goOffline();

    await user.click(option("24"));
    await user.click(screen.getByRole("button", { name: "Verificar" }));

    expect(screen.getByText(/Você está offline/)).toBeInTheDocument();
    expect(api.callsTo("POST /sessions/:id/answers")).toHaveLength(0);
    expect(JSON.parse(localStorage.getItem(savedKey) ?? "{}")).toMatchObject({
      key: "b",
      timeMs: expect.any(Number),
    });

    goOnline();

    expect(await screen.findByText("Mandou bem!")).toBeInTheDocument();
    expect(api.callsTo("POST /sessions/:id/answers")).toHaveLength(1);
    expect(
      screen.getByText("De volta online. Sessão sincronizada."),
    ).toBeInTheDocument();
    expect(localStorage.getItem(savedKey)).toBeNull();
  });

  it("waits the same way when the request does not reach the server", async () => {
    const { user } = renderSession({
      "POST /sessions/:id/answers": networkFailure,
    });

    await user.click(await screen.findByRole("radio", { name: "24" }));
    await user.click(screen.getByRole("button", { name: "Verificar" }));

    expect(await screen.findByText(/Você está offline/)).toBeInTheDocument();
    expect(localStorage.getItem(savedKey)).toContain('"key":"b"');
  });

  it("brings back the option chosen before a reload", async () => {
    localStorage.setItem(savedKey, JSON.stringify({ key: "c" }));
    renderSession();

    await screen.findByRole("radiogroup", { name: "Alternativas" });
    expect(option("16")).toHaveAttribute("aria-checked", "true");
    expect(screen.getByRole("button", { name: "Verificar" })).toBeEnabled();
  });

  it("sends an answer that waited through a reload", async () => {
    localStorage.setItem(savedKey, JSON.stringify({ key: "b", timeMs: 4321 }));
    const { api } = renderSession();

    expect(await screen.findByText("Mandou bem!")).toBeInTheDocument();
    const [request] = api.callsTo("POST /sessions/:id/answers");
    expect(request.body).toMatchObject({ key: "b", time_ms: 4321 });
  });
});
