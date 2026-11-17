import { screen, waitFor } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { renderApp } from "@/test/render";

describe("subjects page", () => {
  it("lists the published subjects with their rating and marks the current one", async () => {
    renderApp("/subjects");

    const current = await screen.findByRole("button", {
      name: /Estruturas de Dados/,
    });
    expect(current).toHaveAttribute("aria-current", "true");
    expect(current).toHaveTextContent("Atual");
    expect(current).toHaveTextContent("1240");

    const unpracticed = screen.getByRole("button", {
      name: /Introdução à Programação/,
    });
    expect(unpracticed).not.toHaveAttribute("aria-current");
    expect(unpracticed).toHaveTextContent("Ainda não praticou");
  });

  it("makes the chosen subject the current one and goes home", async () => {
    const { api, user } = renderApp("/subjects");

    await user.click(
      await screen.findByRole("button", { name: /Banco de Dados/ }),
    );

    await waitFor(() =>
      expect(api.callsTo("PATCH /me/settings")).toHaveLength(1),
    );
    expect(api.callsTo("PATCH /me/settings")[0].body).toEqual({
      current_subject: "banco-de-dados",
    });
    expect(
      await screen.findByRole("heading", { name: "E aí, Carol!" }),
    ).toBeInTheDocument();
  });

  it("goes home without a change when the current subject is chosen", async () => {
    const { api, user } = renderApp("/subjects");

    await user.click(
      await screen.findByRole("button", { name: /Estruturas de Dados/ }),
    );

    expect(
      await screen.findByRole("heading", { name: "E aí, Carol!" }),
    ).toBeInTheDocument();
    expect(api.callsTo("PATCH /me/settings")).toHaveLength(0);
  });

  it("says so when no subject is published", async () => {
    renderApp("/subjects", { routes: { "GET /subjects": { subjects: [] } } });

    expect(
      await screen.findByRole("heading", {
        name: "Nenhuma matéria por aqui ainda",
      }),
    ).toBeInTheDocument();
  });
});
