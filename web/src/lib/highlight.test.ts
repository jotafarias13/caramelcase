import { describe, expect, it } from "vitest";
import { tokenize, tokenizeLines, type Token } from "./highlight";

function kinds(tokens: Token[]): string[] {
  return tokens
    .filter((token) => token.kind !== "plain")
    .map((token) => `${token.kind}:${token.text}`);
}

describe("tokenize", () => {
  it("colours Python keywords, calls, numbers and strings", () => {
    const code = 'def f(n):\n    return n * f(n - 1) if n > 1 else "fim"';
    expect(kinds(tokenize(code, "python"))).toEqual([
      "keyword:def",
      "function:f",
      "keyword:return",
      "function:f",
      "number:1",
      "keyword:if",
      "number:1",
      "keyword:else",
      'string:"fim"',
    ]);
  });

  it("reads a C directive, a format string and a comment", () => {
    const code =
      '#include <stdio.h>\nint main(void) { printf("%d\\n", 3); } // x';
    expect(kinds(tokenize(code, "c"))).toEqual([
      "keyword:#include",
      "keyword:int",
      "function:main",
      "keyword:void",
      "function:printf",
      'string:"%d\\n"',
      "number:3",
      "comment:// x",
    ]);
  });

  it("matches SQL keywords without case and keeps their spelling", () => {
    const code = "select COUNT(*) from aluno WHERE nome = 'Ana' -- fim";
    expect(kinds(tokenize(code, "sql"))).toEqual([
      "keyword:select",
      "function:COUNT",
      "keyword:from",
      "keyword:WHERE",
      "string:'Ana'",
      "comment:-- fim",
    ]);
  });

  it("does not read a digit inside a name as a number", () => {
    expect(kinds(tokenize("x1 = 2", "python"))).toEqual(["number:2"]);
  });

  it("gives back every character, in order", () => {
    const code = "for i in range(3):\n\tprint(i)  # ok\n";
    const text = tokenize(code, "python")
      .map((token) => token.text)
      .join("");
    expect(text).toBe(code);
  });

  it("leaves an unknown language as plain text", () => {
    expect(tokenize("a = 1", null)).toEqual([{ kind: "plain", text: "a = 1" }]);
    expect(tokenize("a = 1", "rust")).toEqual([
      { kind: "plain", text: "a = 1" },
    ]);
  });
});

describe("tokenizeLines", () => {
  it("returns one list per line, empty lines included", () => {
    const lines = tokenizeLines("a = 1\n\nprint(a)", "python");
    expect(lines).toHaveLength(3);
    expect(lines[1]).toEqual([]);
    expect(lines[2][0]).toEqual({ kind: "function", text: "print" });
  });

  it("cuts a string that spans lines at the line break", () => {
    const lines = tokenizeLines('s = """a\nb"""', "python");
    expect(lines[0].at(-1)).toEqual({ kind: "string", text: '"""a' });
    expect(lines[1]).toEqual([{ kind: "string", text: 'b"""' }]);
  });
});
