import { describe, expect, it, vi } from "vitest";
import { applyTheme, getThemeChoice, setThemeChoice } from "./theme";

function stubSystemTheme(theme: "dark" | "light") {
  vi.stubGlobal("matchMedia", () => ({ matches: theme === "light" }));
}

describe("theme", () => {
  it("defaults to the system choice", () => {
    expect(getThemeChoice()).toBe("system");
  });

  it("resolves the system choice to the system's theme", () => {
    stubSystemTheme("light");
    expect(applyTheme("system")).toBe("light");
    expect(document.documentElement.dataset.theme).toBe("light");

    stubSystemTheme("dark");
    expect(applyTheme("system")).toBe("dark");
    expect(document.documentElement.dataset.theme).toBe("dark");
  });

  it("stores an explicit choice and applies it over the system's", () => {
    stubSystemTheme("dark");

    setThemeChoice("light");

    expect(getThemeChoice()).toBe("light");
    expect(document.documentElement.dataset.theme).toBe("light");
  });

  it("forgets the stored choice when set back to system", () => {
    stubSystemTheme("dark");
    setThemeChoice("light");

    setThemeChoice("system");

    expect(getThemeChoice()).toBe("system");
    expect(document.documentElement.dataset.theme).toBe("dark");
  });
});
