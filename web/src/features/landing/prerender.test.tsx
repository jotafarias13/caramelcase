// @vitest-environment node
// No window, document or storage here, as in the build: the landing page
// must render to HTML without them.
import { describe, expect, it } from "vitest";
import { render } from "@/prerender";

describe("landing: static HTML", () => {
  it("renders the page in Portuguese without a browser", () => {
    const page = render();

    expect(page.lang).toBe("pt-BR");
    expect(page.title).toBe(
      "caramelCase · Ciência da computação em sessões de cinco minutos",
    );
    expect(page.html).toContain("<h1");
    expect(page.html).toContain(
      "Ciência da computação em sessões de cinco minutos.",
    );
    expect(page.html).toContain(
      "Qual estrutura de dados segue a política LIFO",
    );
    expect(page.html).toContain('href="/start"');
  });
});
