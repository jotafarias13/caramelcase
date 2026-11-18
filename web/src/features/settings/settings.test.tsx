import { screen, waitFor, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { currentLocale } from "@/i18n";
import { getThemeChoice } from "@/lib/theme";
import { config, guest, me } from "@/test/fixtures";
import { apiError, type Routes } from "@/test/mock-api";
import { renderApp } from "@/test/render";

const saveFails: Routes = {
  "PATCH /me/settings": apiError(500, "internal_server_error"),
};

/** The API after a sign-out or a delete: nobody is signed in any more. */
function signingOut(route: "POST /auth/logout" | "DELETE /me"): Routes {
  let signedIn = true;
  return {
    "GET /me": () => (signedIn ? me : apiError(401, "unauthenticated")),
    [route]: () => {
      signedIn = false;
      return undefined;
    },
  };
}

/** The landing page's title; it can take a moment under a loaded runner. */
function findLandingHeading() {
  return screen.findByRole(
    "heading",
    { level: 1, name: "Ciência da computação em sessões de cinco minutos." },
    { timeout: 3000 },
  );
}

async function openSettings(options: Parameters<typeof renderApp>[1] = {}) {
  const view = renderApp("/settings", options);
  await screen.findByRole("heading", { level: 1, name: /Ajustes|Settings/ });
  return view;
}

describe("settings: language and theme", () => {
  it("switches the language at once and saves it", async () => {
    const { api, user } = await openSettings();

    await user.click(screen.getByRole("radio", { name: "English" }));

    expect(
      await screen.findByRole("heading", { level: 1, name: "Settings" }),
    ).toBeInTheDocument();
    expect(currentLocale()).toBe("en");
    expect(api.callsTo("PATCH /me/settings")[0].body).toEqual({
      locale: "en",
    });
  });

  it("goes back to the language it had when saving fails", async () => {
    const { user } = await openSettings({ routes: saveFails });

    await user.click(screen.getByRole("radio", { name: "English" }));

    expect(
      await screen.findByText("Não deu pra salvar. Tenta de novo."),
    ).toBeInTheDocument();
    expect(currentLocale()).toBe("pt-BR");
    expect(
      screen.getByRole("radio", { name: "Português (Brasil)" }),
    ).toBeChecked();
  });

  it("applies a theme at once, and Sistema follows the device", async () => {
    const { api, user } = await openSettings();
    expect(screen.getByRole("radio", { name: "Sistema" })).toBeChecked();

    await user.click(screen.getByRole("radio", { name: "Escuro" }));

    expect(document.documentElement.dataset.theme).toBe("dark");
    expect(getThemeChoice()).toBe("dark");
    await waitFor(() =>
      expect(api.callsTo("PATCH /me/settings")[0]?.body).toEqual({
        theme: "dark",
      }),
    );

    await user.click(screen.getByRole("radio", { name: "Sistema" }));

    // Nothing kept on the device: the system's setting decides.
    expect(getThemeChoice()).toBe("system");
    await waitFor(() =>
      expect(api.callsTo("PATCH /me/settings")[1]?.body).toEqual({
        theme: "system",
      }),
    );
  });

  it("puts the theme back when saving fails", async () => {
    const { user } = await openSettings({ routes: saveFails });

    await user.click(screen.getByRole("radio", { name: "Claro" }));

    expect(
      await screen.findByText("Não deu pra salvar. Tenta de novo."),
    ).toBeInTheDocument();
    expect(screen.getByRole("radio", { name: "Sistema" })).toBeChecked();
    expect(getThemeChoice()).toBe("system");
  });
});

describe("settings: switches", () => {
  it("turns the reasons under each option off", async () => {
    const { api, user } = await openSettings();
    const reasons = screen.getByRole("switch", {
      name: "Explicar cada alternativa",
    });
    expect(reasons).toBeChecked();

    await user.click(reasons);

    expect(reasons).not.toBeChecked();
    await waitFor(() =>
      expect(api.callsTo("PATCH /me/settings")[0]?.body).toEqual({
        show_option_reasons: false,
      }),
    );
    expect(reasons).not.toBeChecked();
  });

  it("puts the switch back and says so when saving fails", async () => {
    const { user } = await openSettings({ routes: saveFails });
    const reasons = screen.getByRole("switch", {
      name: "Explicar cada alternativa",
    });

    await user.click(reasons);

    expect(
      await screen.findByText("Não deu pra salvar. Tenta de novo."),
    ).toBeInTheDocument();
    expect(reasons).toBeChecked();
  });

  it("hides the daily reminder while the reminders flag is off", async () => {
    await openSettings();

    expect(
      screen.queryByRole("heading", { name: "Notificações" }),
    ).not.toBeInTheDocument();
    expect(
      screen.queryByRole("switch", { name: "Lembrete diário" }),
    ).not.toBeInTheDocument();
  });

  it("shows and saves the daily reminder when the flag is on", async () => {
    const { api, user } = await openSettings({
      routes: { "GET /config": { ...config, flags: { reminders: true } } },
    });

    const reminder = await screen.findByRole("switch", {
      name: "Lembrete diário",
    });
    expect(reminder).not.toBeChecked();

    await user.click(reminder);

    await waitFor(() =>
      expect(api.callsTo("PATCH /me/settings")[0]?.body).toEqual({
        daily_reminder: true,
      }),
    );
    expect(reminder).toBeChecked();
  });
});

describe("settings: account", () => {
  it("shows the email and signs out to the landing page", async () => {
    const { api, user } = await openSettings({
      routes: signingOut("POST /auth/logout"),
    });
    expect(screen.getByText("carol@email.com")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Sair" }));

    expect(await findLandingHeading()).toBeInTheDocument();
    expect(api.callsTo("POST /auth/logout")).toHaveLength(1);
  });

  it("stays and says so when signing out fails", async () => {
    const { user } = await openSettings({
      routes: { "POST /auth/logout": apiError(500, "internal_server_error") },
    });

    await user.click(screen.getByRole("button", { name: "Sair" }));

    expect(
      await screen.findByText("Não deu pra sair. Tenta de novo."),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { level: 1, name: "Ajustes" }),
    ).toBeInTheDocument();
  });

  it("offers a guest to sign in instead of an email and Sair", async () => {
    await openSettings({ routes: { "GET /me": guest } });

    expect(screen.getByRole("link", { name: "Entrar" })).toHaveAttribute(
      "href",
      "/signin",
    );
    expect(
      screen.queryByRole("button", { name: "Sair" }),
    ).not.toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Excluir conta" }),
    ).toBeInTheDocument();
  });
});

describe("settings: your data", () => {
  it("downloads everything the API keeps about the user", async () => {
    await openSettings();

    const download = screen.getByRole("link", { name: "Baixar meus dados" });
    expect(download).toHaveAttribute("href", "/api/v1/me/export");
    expect(download).toHaveAttribute("download", "caramelcase-data.json");
  });

  it("offers a guest the download too", async () => {
    await openSettings({ routes: { "GET /me": guest } });

    expect(
      screen.getByRole("link", { name: "Baixar meus dados" }),
    ).toBeInTheDocument();
  });

  it("links to the privacy policy and the terms", async () => {
    await openSettings();

    const legal = screen.getByRole("navigation", { name: "Documentos" });
    expect(
      within(legal).getByRole("link", { name: "Privacidade" }),
    ).toHaveAttribute("href", "/privacy");
    expect(within(legal).getByRole("link", { name: "Termos" })).toHaveAttribute(
      "href",
      "/terms",
    );
  });
});

describe("settings: deleting the account", () => {
  it("asks first, with the safe choice first and no close button", async () => {
    const { api, user } = await openSettings();

    await user.click(screen.getByRole("button", { name: "Excluir conta" }));

    const dialog = await screen.findByRole("alertdialog", {
      name: "Excluir sua conta?",
    });
    expect(dialog).toHaveAccessibleDescription(
      "Isso apaga seu progresso, sua sequência e seu rating. Não dá pra desfazer.",
    );
    const buttons = within(dialog).getAllByRole("button");
    expect(buttons.map((button) => button.textContent)).toEqual([
      "Cancelar",
      "Excluir conta",
    ]);

    await user.click(buttons[0]);

    await waitFor(() =>
      expect(screen.queryByRole("alertdialog")).not.toBeInTheDocument(),
    );
    expect(api.callsTo("DELETE /me")).toHaveLength(0);
  });

  it("deletes the account and goes to the landing page", async () => {
    const { api, user } = await openSettings({
      routes: signingOut("DELETE /me"),
    });

    await user.click(screen.getByRole("button", { name: "Excluir conta" }));
    const dialog = await screen.findByRole("alertdialog");
    await user.click(
      within(dialog).getByRole("button", { name: "Excluir conta" }),
    );

    expect(await findLandingHeading()).toBeInTheDocument();
    expect(api.callsTo("DELETE /me")).toHaveLength(1);
  });

  it("closes the question and says so when deleting fails", async () => {
    const { user } = await openSettings({
      routes: { "DELETE /me": apiError(500, "internal_server_error") },
    });

    await user.click(screen.getByRole("button", { name: "Excluir conta" }));
    const dialog = await screen.findByRole("alertdialog");
    await user.click(
      within(dialog).getByRole("button", { name: "Excluir conta" }),
    );

    expect(
      await screen.findByText("Não deu pra excluir sua conta. Tenta de novo."),
    ).toBeInTheDocument();
    expect(screen.queryByRole("alertdialog")).not.toBeInTheDocument();
    expect(
      screen.getByRole("heading", { level: 1, name: "Ajustes" }),
    ).toBeInTheDocument();
  });
});
