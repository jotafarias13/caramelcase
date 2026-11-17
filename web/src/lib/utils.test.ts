import { createRequire } from "node:module";
import { describe, expect, it } from "vitest";
import { cn, designScales } from "./utils";

const designTheme = createRequire(import.meta.url)(
  "../../../design/tailwind.theme.js",
) as Record<string, Record<string, unknown>>;

describe("cn", () => {
  it("keeps a design font size next to a text colour", () => {
    expect(cn("text-title", "text-fg")).toBe("text-title text-fg");
  });

  it("lets the later class of the same design scale win", () => {
    expect(cn("text-title", "text-body")).toBe("text-body");
    expect(cn("rounded-lg", "rounded-card")).toBe("rounded-card");
    expect(cn("shadow-step-md", "shadow-step-sm")).toBe("shadow-step-sm");
    expect(cn("p-4", "p-gutter")).toBe("p-gutter");
  });
});

describe("designScales", () => {
  it.each([
    ["text", "fontSize"],
    ["radius", "borderRadius"],
    ["shadow", "boxShadow"],
    ["spacing", "spacing"],
    ["ease", "transitionTimingFunction"],
  ] as const)("%s lists every %s name of the design theme", (scale, key) => {
    expect(designScales[scale]).toEqual(Object.keys(designTheme[key]));
  });
});
