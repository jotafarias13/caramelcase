import { screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it } from "vitest";
import { config, guest, newGuest } from "@/test/fixtures";
import { apiError, type MockApi } from "@/test/mock-api";
import { renderApp } from "@/test/render";
import { flushEvents } from "@/lib/analytics";

// A first visit: the browser has no session.
const visitor = { "GET /me": apiError(401, "unauthenticated") };

/** The events the page recorded, as POST /events received them. */
async function sentEvents(api: MockApi) {
  flushEvents();
  await waitFor(() => expect(api.callsTo("POST /events")).not.toHaveLength(0));
  return api
    .callsTo("POST /events")
    .flatMap(
      (call) =>
        (call.body as { events: { name: string; props: object }[] }).events,
    );
}

beforeEach(() => {
  // Drop what earlier tests left in the queue.
  flushEvents();
});

describe("landing: the page", () => {
  it("has one h1, then the sections as h2", async () => {
    renderApp("/", { routes: visitor });

    const headings = await screen.findAllByRole("heading");
    expect(headings[0]).toHaveAccessibleName(
      "Ciência da computação em sessões de cinco minutos.",
    );
    expect(headings[0].tagName).toBe("H1");
    expect(screen.getAllByRole("heading", { level: 1 })).toHaveLength(1);
    expect(
      screen.getByRole("heading", {
        level: 2,
        name: "Três matérias pra começar",
      }),
    ).toBeInTheDocument();
  });

  it("lists the three launch subjects and a session of 10", async () => {
    renderApp("/", { routes: visitor });

    const items = await screen.findAllByRole("listitem");
    expect(items.map((item) => item.textContent)).toEqual([
      "prog/Introdução à Programação",
      "ed/Estruturas de Dados",
      "bd/Banco de Dados",
    ]);
    expect(screen.getByText(/^10 questões por sessão\./)).toBeInTheDocument();
  });

  it("takes the session length from /config", async () => {
    renderApp("/", {
      routes: { ...visitor, "GET /config": { ...config, session_length: 12 } },
    });

    expect(
      await screen.findByText(/^12 questões por sessão\./),
    ).toBeInTheDocument();
  });

  it("sends every start button to /start and Entrar to /signin", async () => {
    renderApp("/", { routes: visitor });

    const starts = await screen.findAllByRole("link", {
      name: "Bora praticar",
    });
    expect(starts).toHaveLength(2);
    for (const link of starts) expect(link).toHaveAttribute("href", "/start");
    expect(screen.getByRole("link", { name: "Entrar" })).toHaveAttribute(
      "href",
      "/signin",
    );
  });

  it("creates no guest and needs no user", async () => {
    const { api } = renderApp("/", { routes: visitor });

    await screen.findByRole("heading", { level: 1 });
    await waitFor(() => expect(api.callsTo("GET /me")).toHaveLength(1));
    expect(api.callsTo("POST /auth/guest")).toHaveLength(0);
    expect(screen.getByRole("heading", { level: 1 })).toBeInTheDocument();
  });

  it("records one landing.viewed", async () => {
    const { api } = renderApp("/", { routes: visitor });

    await screen.findByRole("heading", { level: 1 });
    const events = await sentEvents(api);
    expect(
      events.filter((event) => event.name === "landing.viewed"),
    ).toHaveLength(1);
  });
});

describe("landing: returning students", () => {
  it("sends a student who finished onboarding to Home", async () => {
    renderApp("/", { routes: { "GET /me": guest } });

    expect(
      await screen.findByRole("heading", { name: "E aí!" }),
    ).toBeInTheDocument();
  });

  it("keeps a guest who has not been through onboarding here", async () => {
    const { api } = renderApp("/", { routes: { "GET /me": newGuest } });

    await waitFor(() => expect(api.callsTo("GET /me")).toHaveLength(1));
    await new Promise((resolve) => setTimeout(resolve, 50));
    expect(screen.getByRole("heading", { level: 1 })).toBeInTheDocument();
  });
});

describe("landing: the try-it question", () => {
  it("answers right on the page, with every reason, and never asks the API", async () => {
    const { api, user } = renderApp("/", { routes: visitor });

    const check = await screen.findByRole("button", { name: "Verificar" });
    expect(check).toBeDisabled();
    await user.click(screen.getByRole("radio", { name: /Pilha/ }));
    await user.click(check);

    expect(await screen.findByRole("status")).toHaveTextContent("Mandou bem!");
    expect(
      screen.getByText(
        "A fila faz o contrário: é FIFO, o primeiro a entrar sai primeiro.",
      ),
    ).toBeInTheDocument();
    expect(
      screen.getByText(
        "Organiza os dados em hierarquia, não por ordem de chegada.",
      ),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: "Continuar praticando" }),
    ).toHaveAttribute("href", "/start");
    expect(api.callsTo("POST /sessions")).toHaveLength(0);
    expect(api.callsTo("POST /sessions/:id/answers")).toHaveLength(0);

    const events = await sentEvents(api);
    expect(events).toContainEqual(
      expect.objectContaining({
        name: "landing.sample_answered",
        props: { correct: true },
      }),
    );
  });

  it("shows a wrong answer and reveals the right one", async () => {
    const { api, user } = renderApp("/", { routes: visitor });

    await user.click(await screen.findByRole("radio", { name: /Fila/ }));
    await user.click(screen.getByRole("button", { name: "Verificar" }));

    expect(await screen.findByRole("status")).toHaveTextContent(
      "Quase. Olha só o porquê:",
    );
    expect(screen.getByRole("radio", { name: /Fila/ })).toHaveTextContent(
      "Sua resposta",
    );
    expect(screen.getByRole("radio", { name: /Pilha/ })).toHaveTextContent(
      "Resposta certa",
    );

    const events = await sentEvents(api);
    expect(events).toContainEqual(
      expect.objectContaining({
        name: "landing.sample_answered",
        props: { correct: false },
      }),
    );
  });
});

describe("landing: language", () => {
  it("switches the page to English on the device only, for a visitor", async () => {
    const { api, user } = renderApp("/", { routes: visitor });

    await user.selectOptions(
      await screen.findByRole("combobox", {
        name: "Idioma: Português (Brasil)",
      }),
      "en",
    );

    expect(
      await screen.findByRole("heading", {
        level: 1,
        name: "Computer science in five-minute sessions.",
      }),
    ).toBeInTheDocument();
    expect(localStorage.getItem("caramelcase.locale")).toBe("en");
    expect(api.callsTo("PATCH /me/settings")).toHaveLength(0);
  });

  it("stores the language on the account when there is a user", async () => {
    const { api, user } = renderApp("/", { routes: { "GET /me": newGuest } });

    await waitFor(() => expect(api.callsTo("GET /me")).toHaveLength(1));
    await user.selectOptions(
      screen.getByRole("combobox", { name: "Idioma: Português (Brasil)" }),
      "en",
    );

    await waitFor(() =>
      expect(api.callsTo("PATCH /me/settings")).toHaveLength(1),
    );
    expect(api.callsTo("PATCH /me/settings")[0].body).toEqual({
      locale: "en",
    });
  });
});
