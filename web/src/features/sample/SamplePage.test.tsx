import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { SamplePage } from "./SamplePage";

function stubHealth(result: "ok" | "error" | "unreachable") {
  const fetchHealth = vi.fn(async () => {
    if (result === "unreachable") throw new TypeError("Failed to fetch");
    return new Response("{}", { status: result === "ok" ? 200 : 503 });
  });
  vi.stubGlobal("fetch", fetchHealth);
  return fetchHealth;
}

describe("SamplePage", () => {
  it("reports the API as up when the health route answers 200", async () => {
    const fetchHealth = stubHealth("ok");

    render(<SamplePage />);

    expect(await screen.findByText("API: no ar")).toBeInTheDocument();
    expect(fetchHealth).toHaveBeenCalledWith("/api/v1/health");
  });

  it.each(["error", "unreachable"] as const)(
    "reports the API as down when the health route is %s",
    async (result) => {
      stubHealth(result);

      render(<SamplePage />);

      expect(await screen.findByText("API: fora do ar")).toBeInTheDocument();
    },
  );

  it("switches the theme from the segmented control", async () => {
    stubHealth("ok");
    render(<SamplePage />);

    await userEvent.click(screen.getByRole("radio", { name: "Claro" }));
    expect(document.documentElement.dataset.theme).toBe("light");

    await userEvent.click(screen.getByRole("radio", { name: "Escuro" }));
    expect(document.documentElement.dataset.theme).toBe("dark");
    expect(screen.getByRole("radio", { name: "Escuro" })).toBeChecked();
  });

  it("blocks clicks on a loading button", () => {
    stubHealth("ok");
    render(<SamplePage />);

    const loading = screen.getByRole("button", { name: "Verificando…" });

    expect(loading).toBeDisabled();
    expect(loading).toHaveAttribute("aria-busy", "true");
  });
});
