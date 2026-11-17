import { Fragment, useEffect, useRef, useState, type RefObject } from "react";
import { useTranslation } from "react-i18next";
import { tokenizeLines, type TokenKind } from "@/lib/highlight";
import { cn } from "@/lib/utils";

const tokenColour: Record<TokenKind, string | undefined> = {
  keyword: "text-syn-keyword",
  function: "text-syn-function",
  number: "text-syn-number",
  string: "text-syn-string",
  comment: "text-syn-comment",
  plain: undefined,
};

type CodeBlockProps = {
  code: string;
  /** "python", "c" or "sql"; another value is shown without colours. */
  language: string | null;
  className?: string;
};

/**
 * "Code block" in design/README.md: dark in both themes, numbered lines,
 * and long lines that scroll sideways inside the block, with a fade on the
 * right edge while something is cut off.
 */
export function CodeBlock({ code, language, className }: CodeBlockProps) {
  const { t } = useTranslation();
  const scroller = useRef<HTMLDivElement>(null);
  const cut = useCutOffRight(scroller);
  const lines = tokenizeLines(code, language);

  return (
    <div
      data-code={language ?? undefined}
      className={cn(
        "relative overflow-hidden rounded-lg border border-code-border bg-ink",
        className,
      )}
    >
      <div className="flex items-center justify-between border-b border-ink-line px-3 py-[7px] font-mono text-[11px] leading-4 text-ink-muted">
        <span>{language}</span>
        <span>{t("session.code_lines", { count: lines.length })}</span>
      </div>
      <div
        ref={scroller}
        // A region that scrolls must be reachable without a pointer.
        tabIndex={0}
        role="region"
        aria-label={t("session.code")}
        className="overflow-x-auto py-3"
      >
        <div className="grid grid-cols-[34px_max-content] font-mono text-[13px] leading-[21px] whitespace-pre text-ink-text [font-variant-ligatures:none] lg:text-[14px] lg:leading-[22px]">
          {lines.map((tokens, lineIndex) => (
            <Fragment key={lineIndex}>
              <span
                aria-hidden="true"
                className="pr-3 text-right text-ink-subtle"
              >
                {lineIndex + 1}
              </span>
              <span className="pr-4">
                {tokens.length === 0
                  ? " "
                  : tokens.map((token, tokenIndex) => (
                      <span
                        key={tokenIndex}
                        className={tokenColour[token.kind]}
                      >
                        {token.text}
                      </span>
                    ))}
              </span>
            </Fragment>
          ))}
        </div>
      </div>
      {cut && (
        <div
          aria-hidden="true"
          className="pointer-events-none absolute top-8 right-0 bottom-0 w-8 bg-[linear-gradient(90deg,transparent,var(--ink))]"
        />
      )}
    </div>
  );
}

/** Whether the scrolled content goes on past the right edge. */
function useCutOffRight(scroller: RefObject<HTMLDivElement | null>): boolean {
  const [cut, setCut] = useState(false);

  useEffect(() => {
    const element = scroller.current;
    // Without ResizeObserver (old browsers, tests) the fade is left out.
    if (!element || typeof ResizeObserver === "undefined") return;
    const update = () =>
      setCut(
        element.scrollLeft + element.clientWidth < element.scrollWidth - 1,
      );
    // It reports once at the start, and again when the fonts arrive.
    const observer = new ResizeObserver(update);
    observer.observe(element);
    if (element.firstElementChild) observer.observe(element.firstElementChild);
    element.addEventListener("scroll", update, { passive: true });
    return () => {
      observer.disconnect();
      element.removeEventListener("scroll", update);
    };
  }, [scroller]);

  return cut;
}
