import { QueryClient } from "@tanstack/react-query";
import { render, screen, waitFor, within } from "@testing-library/react";
import { StrictMode } from "react";
import { MemoryRouter } from "react-router";
import { describe, expect, it } from "vitest";
import { AppProviders } from "@/app/providers";
import { AppRoutes } from "@/app/routes";
import { initI18n } from "@/i18n";
import { browserTimezone } from "@/lib/timezone";
import { config, me, world } from "@/test/fixtures";
import { apiError, type Routes } from "@/test/mock-api";
import { renderApp } from "@/test/render";
import { stubApi } from "@/test/stub-api";

const visitor = { "GET /me": apiError(401, "unauthenticated") };

/** The app as main.tsx renders it: in StrictMode, effects run twice. */
function renderStrict(path: string, routes: Routes = {}) {
  initI18n("pt-BR");
  const api = stubApi(world(routes));
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  render(
    <StrictMode>
      <AppProviders queryClient={queryClient}>
        <MemoryRouter initialEntries={[path]}>
          <AppRoutes />
        </MemoryRouter>
      </AppProviders>
    </StrictMode>,
  );
  return { api };
}

describe("sign-in", () => {
  it("works for a visitor without any user, and creates none", async () => {
    const { api } = renderApp("/signin", { routes: visitor });

    expect(
      await screen.findByRole("heading", { name: "Entrar no caramelCase" }),
    ).toBeInTheDocument();
    expect(api.callsTo("POST /auth/guest")).toHaveLength(0);
  });

  it("sends the browser to the API's Google route, with the language and timezone in use", async () => {
    renderApp("/signin", { routes: visitor });

    const link = await screen.findByRole("link", {
      name: /Continuar com Google/,
    });
    const url = new URL(link.getAttribute("href") ?? "", "http://app");
    expect(url.pathname).toBe("/api/v1/auth/google/start");
    expect(url.searchParams.get("locale")).toBe("pt-BR");
    expect(url.searchParams.get("timezone")).toBe(browserTimezone());
  });

  it("asks Google for an English account when the app is in English", async () => {
    renderApp("/signin", { routes: visitor, locale: "en" });

    const link = await screen.findByRole("link", {
      name: /Continue with Google/,
    });
    expect(link.getAttribute("href")).toContain("locale=en");
  });

  it("hides Google when this server has no Google sign-in", async () => {
    renderApp("/signin", {
      routes: {
        ...visitor,
        "GET /config": { ...config, google_sign_in: false },
      },
    });

    await screen.findByRole("heading", { name: "Entrar no caramelCase" });
    await waitFor(() =>
      expect(screen.queryByText("ou")).not.toBeInTheDocument(),
    );
    expect(
      screen.queryByRole("link", { name: /Continuar com Google/ }),
    ).not.toBeInTheDocument();
  });

  it("checks the address's form before sending", async () => {
    const { api, user } = renderApp("/signin", { routes: visitor });

    await user.type(await screen.findByLabelText("E-mail"), "carol@email");
    await user.click(
      screen.getByRole("button", { name: "Enviar link mágico" }),
    );

    expect(screen.getByLabelText("E-mail")).toHaveAttribute(
      "aria-invalid",
      "true",
    );
    expect(
      screen.getByText("Esse e-mail parece incompleto. Confere?"),
    ).toBeInTheDocument();
    expect(api.callsTo("POST /auth/magic-link")).toHaveLength(0);
  });

  it("sends the link and says where it went", async () => {
    const { api, user } = renderApp("/signin", { routes: visitor });

    await user.type(
      await screen.findByLabelText("E-mail"),
      " carol@email.com{Enter}",
    );

    expect(
      await screen.findByRole("heading", { name: "Olha seu e-mail" }),
    ).toBeInTheDocument();
    expect(
      screen.getByText(
        "Mandamos um link pra carol@email.com. Abra neste aparelho pra entrar.",
      ),
    ).toBeInTheDocument();
    expect(api.callsTo("POST /auth/magic-link")[0].body).toEqual({
      email: "carol@email.com",
      locale: "pt-BR",
    });
  });

  it("resends the link, and goes back to the form for another address", async () => {
    const { api, user } = renderApp("/signin", { routes: visitor });

    await user.type(
      await screen.findByLabelText("E-mail"),
      "carol@email.com{Enter}",
    );
    await user.click(
      await screen.findByRole("button", { name: "Reenviar link" }),
    );

    expect(await screen.findByText("Mandamos outro link.")).toBeInTheDocument();
    expect(api.callsTo("POST /auth/magic-link")).toHaveLength(2);

    await user.click(screen.getByRole("button", { name: "Usar outro e-mail" }));
    expect(screen.getByLabelText("E-mail")).toBeInTheDocument();
  });

  it("stays on the form and says so when the link cannot be sent", async () => {
    const { user } = renderApp("/signin", {
      routes: {
        ...visitor,
        "POST /auth/magic-link": apiError(500, "internal_server_error"),
      },
    });

    await user.type(
      await screen.findByLabelText("E-mail"),
      "carol@email.com{Enter}",
    );

    expect(
      await screen.findByText("Não deu pra mandar o link. Tenta de novo."),
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("heading", { name: "Olha seu e-mail" }),
    ).not.toBeInTheDocument();
  });

  it("says to wait when too many links were asked for", async () => {
    const { user } = renderApp("/signin", {
      routes: {
        ...visitor,
        "POST /auth/magic-link": apiError(429, "rate_limited"),
      },
    });

    await user.type(
      await screen.findByLabelText("E-mail"),
      "carol@email.com{Enter}",
    );

    expect(
      await screen.findByText(
        "Muitas tentativas seguidas. Espera um pouquinho e tenta de novo.",
      ),
    ).toBeInTheDocument();
  });

  it("links to the privacy policy and the terms", async () => {
    renderApp("/signin", { routes: visitor });

    const legal = await screen.findByRole("navigation", {
      name: "Documentos",
    });
    expect(
      within(legal).getByRole("link", { name: "Privacidade" }),
    ).toHaveAttribute("href", "/privacy");
    expect(within(legal).getByRole("link", { name: "Termos" })).toHaveAttribute(
      "href",
      "/terms",
    );
  });

  it("lets the student carry on without an account", async () => {
    renderApp("/signin", { routes: visitor });

    expect(
      await screen.findByRole("link", { name: "Continuar sem conta" }),
    ).toHaveAttribute("href", "/home");
  });
});

describe("auth callback", () => {
  it("verifies an emailed link once, even in StrictMode, and goes Home", async () => {
    const { api } = renderStrict("/auth/callback?token=abc123");

    await screen.findAllByRole("navigation", { name: "Principal" });
    const verifies = api.callsTo("POST /auth/magic-link/verify");
    expect(verifies).toHaveLength(1);
    // A new account starts in this device's language and timezone.
    expect(verifies[0].body).toEqual({
      token: "abc123",
      locale: "pt-BR",
      timezone: browserTimezone(),
    });
  });

  it("uses the signed-in account from then on, without making a guest", async () => {
    let signedIn = false;
    const { api } = renderApp("/auth/callback?token=abc123", {
      routes: {
        "GET /me": () => (signedIn ? me : apiError(401, "unauthenticated")),
        "POST /auth/magic-link/verify": () => {
          signedIn = true;
          return me;
        },
      },
    });

    expect(
      (await screen.findAllByLabelText("Sequência: 7")).length,
    ).toBeGreaterThan(0);
    expect(api.callsTo("POST /auth/guest")).toHaveLength(0);
  });

  it("says when a link was used or is too old, and offers a new one", async () => {
    renderApp("/auth/callback?token=old", {
      routes: {
        "POST /auth/magic-link/verify": apiError(400, "invalid_magic_link"),
      },
    });

    expect(
      await screen.findByRole("heading", { name: "Esse link não vale mais" }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: "Pedir outro link" }),
    ).toHaveAttribute("href", "/signin");
  });

  it("says when Google sign-in failed", async () => {
    renderApp("/auth/callback?error=google_sign_in_failed");

    expect(
      await screen.findByRole("heading", {
        name: "Não deu pra entrar com o Google",
      }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: "Voltar pra entrada" }),
    ).toHaveAttribute("href", "/signin");
  });

  it("explains an unverified Google address", async () => {
    renderApp("/auth/callback?error=google_email_not_verified");

    expect(
      await screen.findByText(/Seu e-mail no Google ainda não foi confirmado/),
    ).toBeInTheDocument();
  });

  it("goes Home after a Google sign-in that worked", async () => {
    const { api } = renderApp("/auth/callback");

    await screen.findAllByRole("navigation", { name: "Principal" });
    expect(api.callsTo("POST /auth/magic-link/verify")).toHaveLength(0);
  });
});
