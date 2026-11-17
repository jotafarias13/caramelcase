import { screen, waitFor } from "@testing-library/react";
import { lazy } from "react";
import { describe, expect, it, vi } from "vitest";
import { config, guest, me, newGuest } from "@/test/fixtures";
import { apiError, networkFailure } from "@/test/mock-api";
import { renderApp, renderWithProviders } from "@/test/render";
import { browserTimezone } from "@/lib/timezone";
import { getThemeChoice } from "@/lib/theme";
import { currentLocale } from "@/i18n";
import { Flagged } from "./Flagged";

describe("guest first", () => {
  it("creates a guest silently when the browser has no session", async () => {
    let created = false;
    const { api } = renderApp("/home", {
      routes: {
        "GET /me": () => (created ? guest : apiError(401, "unauthenticated")),
        "POST /auth/guest": () => {
          created = true;
          return guest;
        },
      },
    });

    await screen.findAllByRole("navigation", { name: "Principal" });

    const [request] = api.callsTo("POST /auth/guest");
    expect(request.body).toEqual({
      locale: "pt-BR",
      timezone: browserTimezone(),
    });
    expect(api.callsTo("POST /auth/guest")).toHaveLength(1);
  });

  it("does not create a guest for someone who has a session", async () => {
    const { api } = renderApp("/home");

    await screen.findAllByRole("navigation", { name: "Principal" });

    expect(api.callsTo("POST /auth/guest")).toHaveLength(0);
  });

  it("sends someone who signs out to the landing page, without a new guest", async () => {
    let signedIn = true;
    const { api, queryClient } = renderApp("/home", {
      routes: {
        "GET /me": () => (signedIn ? me : apiError(401, "unauthenticated")),
      },
    });
    await screen.findAllByRole("navigation", { name: "Principal" });

    signedIn = false;
    queryClient.setQueryData(["me"], null);

    await waitFor(() =>
      expect(
        screen.queryByRole("navigation", { name: "Principal" }),
      ).not.toBeInTheDocument(),
    );
    expect(await screen.findByRole("link", { name: "Entrar" })).toBeVisible();
    expect(api.callsTo("POST /auth/guest")).toHaveLength(0);
  });

  it("sends a user without a subject to onboarding", async () => {
    const { api } = renderApp("/profile", {
      routes: { "GET /me": newGuest },
    });

    await waitFor(() => expect(api.callsTo("GET /me")).toHaveLength(1));
    await waitFor(() =>
      expect(
        screen.queryByRole("navigation", { name: "Principal" }),
      ).not.toBeInTheDocument(),
    );
  });
});

describe("preferences of the account", () => {
  it("switches to the account's language and theme", async () => {
    renderApp("/home", {
      routes: {
        "GET /me": {
          ...me,
          locale: "en",
          settings: { ...me.settings, theme: "light" },
        },
      },
    });

    await screen.findAllByRole("navigation", { name: "Main" });

    expect(currentLocale()).toBe("en");
    expect(document.documentElement.lang).toBe("en");
    expect(getThemeChoice()).toBe("light");
    expect(document.documentElement.dataset.theme).toBe("light");
  });

  it("tells the API when the device is in another timezone", async () => {
    const { api } = renderApp("/home", {
      routes: { "GET /me": { ...me, timezone: "Pacific/Kiritimati" } },
    });

    await waitFor(() =>
      expect(api.callsTo("PATCH /me/settings")).toHaveLength(1),
    );
    expect(api.callsTo("PATCH /me/settings")[0].body).toEqual({
      timezone: browserTimezone(),
    });
  });
});

describe("navigation", () => {
  it("marks the current destination", async () => {
    renderApp("/profile");

    const links = await screen.findAllByRole("link", { name: "Perfil" });

    // The sidebar and the tab bar are both in the page; CSS shows one.
    expect(links).toHaveLength(2);
    for (const link of links) {
      expect(link).toHaveAttribute("aria-current", "page");
    }
    for (const link of screen.getAllByRole("link", { name: "Início" })) {
      expect(link).not.toHaveAttribute("aria-current");
    }
  });

  it("shows the streak and the rating of the current subject", async () => {
    renderApp("/home");

    // In the sidebar, and on phones at the top of Home as well.
    expect(
      (await screen.findAllByLabelText("Sequência: 7")).length,
    ).toBeGreaterThan(0);
    expect(screen.getAllByLabelText("Rating: 1240").length).toBeGreaterThan(0);
  });
});

describe("system states", () => {
  it("shows the 404 screen for an unknown address", async () => {
    renderApp("/nao-existe");

    expect(
      await screen.findByRole("heading", { name: "Essa página fugiu" }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: "Voltar pro início" }),
    ).toHaveAttribute("href", "/home");
  });

  it("shows the offline screen and retries from it", async () => {
    let online = false;
    const { user } = renderApp("/home", {
      routes: { "GET /me": () => (online ? me : networkFailure()) },
    });

    expect(
      await screen.findByRole("heading", { name: "Sem conexão" }),
    ).toBeInTheDocument();

    online = true;
    await user.click(screen.getByRole("button", { name: "Tentar de novo" }));

    await screen.findAllByRole("navigation", { name: "Principal" });
    expect(
      screen.queryByRole("heading", { name: "Sem conexão" }),
    ).not.toBeInTheDocument();
  });

  it("shows the maintenance screen while the API answers 503", async () => {
    renderApp("/home", {
      routes: { "GET /me": apiError(503, "database_unavailable") },
    });

    expect(
      await screen.findByRole("heading", { name: "Em manutenção" }),
    ).toBeInTheDocument();
  });

  it("shows the error screen for any other failure", async () => {
    renderApp("/home", {
      routes: { "GET /me": apiError(500, "internal_server_error") },
    });

    expect(
      await screen.findByRole("heading", { name: "Algo deu errado" }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Tentar de novo" }),
    ).toBeInTheDocument();
  });
});

describe("document title", () => {
  it("is the app's name on a page of the app", async () => {
    renderApp("/nao-existe");
    await screen.findByRole("heading", { name: "Essa página fugiu" });
    expect(document.title).toBe("caramelCase");
  });
});

describe("Flagged", () => {
  function setUp(flags: Record<string, boolean>) {
    const load = vi.fn(async () => ({
      default: () => <h1>Revisão de hoje</h1>,
    }));
    const Review = lazy(load);
    renderWithProviders(
      <Flagged flag="review_queue">
        <Review />
      </Flagged>,
      { routes: { "GET /config": { ...config, flags } } },
    );
    return load;
  }

  it("renders the feature when its flag is on", async () => {
    const load = setUp({ review_queue: true });

    expect(
      await screen.findByRole("heading", { name: "Revisão de hoje" }),
    ).toBeInTheDocument();
    expect(load).toHaveBeenCalledTimes(1);
  });

  it("is a 404 and never loads the feature's code when the flag is off", async () => {
    const load = setUp({ review_queue: false });

    expect(
      await screen.findByRole("heading", { name: "Essa página fugiu" }),
    ).toBeInTheDocument();
    expect(load).not.toHaveBeenCalled();
  });
});
