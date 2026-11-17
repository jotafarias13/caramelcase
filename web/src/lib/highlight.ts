// A small syntax highlighter for the three languages questions are written
// in. It only has to tell apart the five kinds of token the design colours
// (design/README.md, "Code block"); everything else is plain text.

export type TokenKind =
  "keyword" | "function" | "number" | "string" | "comment" | "plain";

export type Token = { kind: TokenKind; text: string };

type Language = {
  keywords: Set<string>;
  /** SQL keywords are matched without case. */
  ignoreCase: boolean;
  lineComment: RegExp;
  blockComment: RegExp | null;
  string: RegExp;
};

function words(list: string): Set<string> {
  return new Set(list.split(" "));
}

const languages: Record<string, Language> = {
  python: {
    keywords: words(
      "and as assert break class continue def del elif else except False " +
        "finally for from global if import in is lambda None nonlocal not " +
        "or pass raise return True try while with yield",
    ),
    ignoreCase: false,
    lineComment: /#.*/y,
    blockComment: null,
    string:
      /[fFrRbB]{0,2}("""[\s\S]*?"""|'''[\s\S]*?'''|"(?:\\.|[^"\\\n])*"|'(?:\\.|[^'\\\n])*')/y,
  },
  c: {
    keywords: words(
      "auto break case char const continue default do double else enum " +
        "extern float for goto if int long register return short signed " +
        "sizeof static struct switch typedef union unsigned void volatile " +
        "while NULL",
    ),
    ignoreCase: false,
    lineComment: /\/\/.*/y,
    blockComment: /\/\*[\s\S]*?\*\//y,
    string: /"(?:\\.|[^"\\\n])*"|'(?:\\.|[^'\\\n])*'/y,
  },
  sql: {
    keywords: words(
      "add all alter and as asc between by case check column constraint " +
        "create cross default delete desc distinct drop else end except " +
        "exists foreign from full group having in index inner insert " +
        "intersect into is join key left like limit not null on or order " +
        "outer primary references right select set table then union unique " +
        "update values view when where",
    ),
    ignoreCase: true,
    lineComment: /--.*/y,
    blockComment: /\/\*[\s\S]*?\*\//y,
    string: /'(?:''|[^'])*'/y,
  },
};

const preprocessor = /#\s*\w+/y;
const number = /(?:0[xX][\da-fA-F]+|\d+\.?\d*(?:[eE][+-]?\d+)?)[uUlLfF]*/y;
const identifier = /[A-Za-z_]\w*/y;
const callAhead = /\s*\(/y;

function matchAt(pattern: RegExp, code: string, index: number): string | null {
  pattern.lastIndex = index;
  return pattern.exec(code)?.[0] ?? null;
}

/** Split code into tokens. An unknown language comes back as plain text. */
export function tokenize(code: string, languageName: string | null): Token[] {
  const language = languages[languageName ?? ""];
  if (!language) return [{ kind: "plain", text: code }];

  const tokens: Token[] = [];
  const push = (kind: TokenKind, text: string) => {
    const last = tokens[tokens.length - 1];
    if (kind === "plain" && last?.kind === "plain") last.text += text;
    else tokens.push({ kind, text });
  };

  let index = 0;
  while (index < code.length) {
    const comment =
      matchAt(language.lineComment, code, index) ??
      (language.blockComment && matchAt(language.blockComment, code, index));
    // In C, "#include" is a directive, not a comment or an operator.
    const directive =
      languageName === "c" ? matchAt(preprocessor, code, index) : null;
    const text = matchAt(language.string, code, index);
    const word = matchAt(identifier, code, index);
    const digits = word ? null : matchAt(number, code, index);

    if (directive) {
      push("keyword", directive);
      index += directive.length;
    } else if (comment) {
      push("comment", comment);
      index += comment.length;
    } else if (text) {
      push("string", text);
      index += text.length;
    } else if (word) {
      const key = language.ignoreCase ? word.toLowerCase() : word;
      const isCall = matchAt(callAhead, code, index + word.length) !== null;
      if (language.keywords.has(key)) push("keyword", word);
      else if (isCall) push("function", word);
      else push("plain", word);
      index += word.length;
    } else if (digits) {
      push("number", digits);
      index += digits.length;
    } else {
      push("plain", code[index]);
      index += 1;
    }
  }
  return tokens;
}

/** The tokens of each line; a token that spans lines is cut at the breaks. */
export function tokenizeLines(
  code: string,
  languageName: string | null,
): Token[][] {
  const lines: Token[][] = [[]];
  for (const token of tokenize(code, languageName)) {
    const parts = token.text.split("\n");
    parts.forEach((part, partIndex) => {
      if (partIndex > 0) lines.push([]);
      if (part) lines[lines.length - 1].push({ kind: token.kind, text: part });
    });
  }
  return lines;
}
