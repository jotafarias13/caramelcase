import { X } from "lucide-react";
import type { Ref } from "react";
import { useTranslation } from "react-i18next";
import { Link } from "react-router";
import type { SessionQuestion, SubjectRef } from "@/api/types";
import { DifficultyBadge } from "@/components/DifficultyBadge";
import { localName, localShort } from "@/i18n";
import { cn } from "@/lib/utils";
import { difficultyLevel } from "./rules";
import { column } from "./layout";

type QuestionHeaderProps = {
  subject: SubjectRef;
  question: SessionQuestion;
  /** The question's place in the session, from 0. */
  index: number;
  total: number;
  headingRef?: Ref<HTMLHeadingElement>;
};

/** "Question header" in design/README.md: caramel in both themes. */
export function QuestionHeader({
  subject,
  question,
  index,
  total,
  headingRef,
}: QuestionHeaderProps) {
  const { t } = useTranslation();
  // The badge text ends in a slash ("ed/"); the breadcrumb draws its own.
  const subjectLabel = localShort(subject).replace(/\/$/, "");

  return (
    <header className="bg-brand text-brand-fg">
      <div
        className={cn(
          column,
          "flex flex-col pt-[calc(12px+env(safe-area-inset-top))] pb-5",
          "lg:pt-[calc(14px+env(safe-area-inset-top))] lg:pb-[26px]",
        )}
      >
        <div className="flex items-center gap-2.5">
          {/* The session can be resumed, so leaving asks nothing. */}
          <Link
            to="/home"
            aria-label={t("session.leave")}
            className="-ml-2.5 flex size-11 shrink-0 items-center justify-center rounded-md text-ink hover:bg-ink-24"
          >
            <X aria-hidden="true" strokeWidth={2.5} className="size-[22px]" />
          </Link>
          <Progress index={index} total={total} />
          <div className="font-mono text-[13px] leading-[18px] font-bold tabular-nums">
            {index + 1}/{total}
          </div>
        </div>
        <div className="mt-2.5 flex flex-wrap items-center justify-between gap-2">
          <div className="flex min-w-0 flex-wrap items-center gap-1.5 font-mono text-[12px] leading-[18px] lowercase">
            <span className="font-extrabold">{subjectLabel}</span>
            <span aria-hidden="true">/</span>
            <span className="font-medium">{localName(question.topic)}</span>
          </div>
          <DifficultyBadge level={difficultyLevel(question.difficulty)} />
        </div>
        <h1
          ref={headingRef}
          tabIndex={-1}
          lang={question.locale}
          className="mt-4 text-[22px] leading-7 font-bold tracking-[-0.01em] text-balance outline-none lg:max-w-[760px] lg:text-[26px] lg:leading-[34px]"
        >
          {question.stem}
        </h1>
      </div>
    </header>
  );
}

/** Ten segments: done, the current one, and those to do. */
function Progress({ index, total }: { index: number; total: number }) {
  const { t } = useTranslation();
  return (
    <div
      role="progressbar"
      aria-label={t("session.progress")}
      aria-valuemin={0}
      aria-valuemax={total}
      aria-valuenow={index}
      className="grid grow gap-[3px]"
      style={{ gridTemplateColumns: `repeat(${total}, minmax(0, 1fr))` }}
    >
      {Array.from({ length: total }, (_, segment) => (
        <div
          key={segment}
          className={cn(
            "h-2.5 rounded-px",
            segment < index && "bg-ink",
            segment === index &&
              "bg-brand-cream shadow-[inset_0_0_0_2px_var(--ink)]",
            segment > index && "bg-ink-24",
          )}
        />
      ))}
    </div>
  );
}
