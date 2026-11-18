import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { apiError } from "@/test/mock-api";
import { renderApp } from "@/test/render";
import { LegalText } from "./LegalDocument";

// The pages are public: someone who never played has no session.
const visitor = { "GET /me": apiError(401, "unauthenticated") };

describe("legal pages", () => {
  it("shows the privacy policy with every section, marked as a draft", async () => {
    const { api } = renderApp("/privacy", { routes: visitor });

    expect(
      await screen.findByRole("heading", {
        level: 1,
        name: "Política de privacidade",
      }),
    ).toBeInTheDocument();
    const sections = screen.getAllByRole("heading", { level: 2 });
    expect(sections.map((heading) => heading.textContent)).toEqual([
      "Quem cuida dos seus dados",
      "O que guardamos",
      "Para que usamos",
      "Cookies e o seu aparelho",
      "Com quem compartilhamos",
      "Por quanto tempo",
      "Seus direitos",
      "Base legal",
      "Mudanças nesta política",
    ]);
    expect(screen.getByRole("note")).toHaveTextContent(/^Rascunho/);
    // Reading the policy creates no guest.
    expect(api.callsTo("POST /auth/guest")).toHaveLength(0);
  });

  it("shows the terms with every section", async () => {
    renderApp("/terms", { routes: visitor });

    expect(
      await screen.findByRole("heading", { level: 1, name: "Termos de uso" }),
    ).toBeInTheDocument();
    expect(screen.getAllByRole("heading", { level: 2 })).toHaveLength(9);
  });

  it("is in English for an English reader", async () => {
    renderApp("/privacy", { routes: visitor, locale: "en" });

    expect(
      await screen.findByRole("heading", { level: 1, name: "Privacy policy" }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { level: 2, name: "Your rights" }),
    ).toBeInTheDocument();
  });

  it("links one page to the other and back to the front page", async () => {
    const { user } = renderApp("/privacy", { routes: visitor });
    const legal = await screen.findByRole("navigation", {
      name: "Documentos",
    });

    await user.click(within(legal).getByRole("link", { name: "Termos" }));

    expect(
      await screen.findByRole("heading", { level: 1, name: "Termos de uso" }),
    ).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "caramelCase" })).toHaveAttribute(
      "href",
      "/",
    );
  });

  it("is linked from the landing page's footer", async () => {
    renderApp("/", { routes: visitor });

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
});

describe("LegalText", () => {
  it("makes paragraphs of blocks and a list of lines that start with a dash", () => {
    render(
      <LegalText
        text={"Primeiro parágrafo.\n\n- um\n- dois\n\nÚltimo parágrafo."}
      />,
    );

    expect(screen.getByText("Primeiro parágrafo.").tagName).toBe("P");
    const items = within(screen.getByRole("list")).getAllByRole("listitem");
    expect(items.map((item) => item.textContent)).toEqual(["um", "dois"]);
    expect(screen.getByText("Último parágrafo.").tagName).toBe("P");
  });

  it("keeps a block that mixes dashes and text as one paragraph", () => {
    render(<LegalText text={"- um\nnão é lista"} />);

    expect(screen.queryByRole("list")).not.toBeInTheDocument();
    expect(screen.getByText(/não é lista/).tagName).toBe("P");
  });
});
