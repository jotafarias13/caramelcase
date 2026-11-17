import { describe, expect, it, vi } from "vitest";
import { detectLocale, initI18n, setLocale } from "./index";
import en from "./en.json";
import ptBR from "./pt-BR.json";

type Tree = { [key: string]: string | Tree };

/** Every string in the file, as ["a.b.c", text]. */
function flatten(tree: Tree, prefix = ""): [string, string][] {
  return Object.entries(tree).flatMap(([key, value]) => {
    const path = prefix ? `${prefix}.${key}` : key;
    return typeof value === "string"
      ? [[path, value] as [string, string]]
      : flatten(value, path);
  });
}

function variables(text: string): string[] {
  return [...text.matchAll(/{{\s*(\w+)\s*}}/g)].map((m) => m[1]).sort();
}

describe("translation files", () => {
  const portuguese = new Map(flatten(ptBR));
  const english = new Map(flatten(en));

  it("have the same keys in both languages", () => {
    expect([...english.keys()].sort()).toEqual([...portuguese.keys()].sort());
  });

  it("use the same variables in both languages", () => {
    for (const [key, text] of portuguese) {
      expect(variables(english.get(key) ?? ""), key).toEqual(variables(text));
    }
  });

  it("leave no text empty", () => {
    const empty = [...portuguese, ...english]
      .filter(([, text]) => text.trim() === "")
      .map(([key]) => key);
    expect(empty).toEqual([]);
  });
});

describe("detectLocale", () => {
  function browserLanguage(language: string) {
    vi.stubGlobal("navigator", { languages: [language], language });
  }

  it("is Portuguese by default, for any browser not set to English", () => {
    for (const language of ["pt-BR", "pt-PT", "es-AR", "fr"]) {
      browserLanguage(language);
      expect(detectLocale()).toBe("pt-BR");
    }
  });

  it("is English for a browser whose first language is English", () => {
    browserLanguage("en-GB");
    expect(detectLocale()).toBe("en");
  });

  it("keeps the language chosen on this device over the browser's", () => {
    browserLanguage("en-US");
    initI18n();
    setLocale("pt-BR");
    expect(detectLocale()).toBe("pt-BR");
  });
});
