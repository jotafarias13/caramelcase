import { Info } from "lucide-react";
import { useTranslation } from "react-i18next";
import { Link } from "react-router";
import { Wordmark } from "@/components/Wordmark";
import { LanguageSwitch } from "@/features/landing/LanguageSwitch";
import { cn } from "@/lib/utils";
import { LegalLinks } from "./LegalLinks";

// A reading column: about 80 characters a line at the body size.
const column = "mx-auto w-full max-w-[768px] px-4 md:px-6";

export type LegalSection = { title: string; body: string };

type LegalDocumentProps = {
  title: string;
  intro: string;
  sections: LegalSection[];
};

/**
 * The privacy policy and the terms. No mockup draws them (design/README.md
 * lists them under "Not designed"): the landing page's header and footer
 * around a column of headings and paragraphs. Open to anyone; nothing
 * here needs a user.
 */
export function LegalDocument({ title, intro, sections }: LegalDocumentProps) {
  const { t } = useTranslation();
  return (
    <div className="flex min-h-dvh flex-col">
      <header
        className={cn(
          column,
          "flex min-h-16 items-center justify-between gap-2 pt-[calc(8px+env(safe-area-inset-top))] pb-2",
        )}
      >
        <Link to="/" className="inline-flex min-h-11 items-center">
          <Wordmark className="text-[18px] leading-[23px]" />
        </Link>
        <LanguageSwitch />
      </header>
      <main className={cn(column, "flex grow flex-col gap-6 pt-2 pb-10")}>
        <div className="flex flex-col gap-1.5">
          <h1 className="text-[24px] leading-[30px] font-bold tracking-[-0.01em] text-balance lg:text-[30px] lg:leading-9">
            {title}
          </h1>
          <p className="font-mono text-[12px] leading-4 text-fg-muted">
            {t("legal.updated")}
          </p>
        </div>
        <p
          role="note"
          className="flex items-start gap-2.5 rounded-lg border border-border bg-surface px-4 py-3 text-[14px] leading-5 text-fg-muted"
        >
          <Info aria-hidden="true" className="mt-px size-[18px] shrink-0" />
          <span>{t("legal.draft")}</span>
        </p>
        <p className="text-[16px] leading-6 text-fg">{intro}</p>
        {sections.map((section) => (
          <section key={section.title} className="flex flex-col gap-2">
            <h2 className="text-[18px] leading-6 font-bold text-fg">
              {section.title}
            </h2>
            <LegalText text={section.body} />
          </section>
        ))}
      </main>
      <div className={column}>
        <footer className="flex flex-wrap items-center justify-between gap-x-3 border-t border-border pt-2 pb-[calc(16px+env(safe-area-inset-bottom))] font-mono text-[12px] leading-4 text-fg-muted">
          <span>{t("common.brand")}</span>
          <LegalLinks />
        </footer>
      </div>
    </div>
  );
}

/**
 * A section's text from the translation files: blocks apart by a blank
 * line are paragraphs, and a block whose every line starts with "- " is a
 * list.
 */
export function LegalText({ text }: { text: string }) {
  const blocks = text.split("\n\n");
  return (
    <div className="flex flex-col gap-3 text-[16px] leading-6 text-fg">
      {blocks.map((block) => {
        const lines = block.split("\n");
        if (lines.every((line) => line.startsWith("- "))) {
          return (
            <ul
              key={block}
              className="flex list-disc flex-col gap-1.5 pl-5 marker:text-fg-subtle"
            >
              {lines.map((line) => (
                <li key={line}>{line.slice(2)}</li>
              ))}
            </ul>
          );
        }
        return <p key={block}>{block}</p>;
      })}
    </div>
  );
}
