import { CircleCheck, CircleX, Flag, Zap } from "lucide-react";
import { useTranslation } from "react-i18next";
import type { AnswerResult } from "@/api/types";
import { Mel } from "@/components/Mel";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { KeyCap } from "./KeyCap";
import { column } from "./layout";

type FeedbackPanelProps = {
  result: AnswerResult;
  /** With per-option reasons off, the panel carries the explanation. */
  showExplanation: boolean;
  /** The language the question was written in. */
  questionLocale: string;
  onReport: () => void;
  onContinue: () => void;
  /** After the last question: the session is being finished. */
  finishing: boolean;
};

/**
 * "Feedback panel" in design/README.md: rises under the options after
 * Verificar. On phones a sheet-like block, from 1280 px a full-width band.
 */
export function FeedbackPanel({
  result,
  showExplanation,
  questionLocale,
  onReport,
  onContinue,
  finishing,
}: FeedbackPanelProps) {
  const { t } = useTranslation();
  const correct = result.is_correct;
  const Icon = correct ? CircleCheck : CircleX;

  return (
    <section
      aria-live="polite"
      className={cn(
        "animate-[rise-in_var(--dur-reveal-panel)_var(--ease-standard)]",
        "rounded-t-xl border-t-2 lg:rounded-none",
        correct
          ? "border-correct-border bg-correct-tint"
          : "border-wrong-border bg-wrong-tint",
      )}
    >
      <div
        className={cn(
          column,
          "flex flex-col gap-2 pt-4 pb-[calc(22px+env(safe-area-inset-bottom))]",
          "lg:flex-row lg:items-center lg:gap-6 lg:pt-[18px] lg:pr-11",
        )}
      >
        <div className="flex min-w-0 grow flex-col gap-2 lg:gap-1.5">
          <div className="flex min-w-0 items-center gap-3">
            <Mel pose={correct ? "celebrate" : "encourage"} head scale={3} />
            <div
              className={cn(
                "flex min-w-0 items-center gap-1.5",
                correct ? "text-correct-text" : "text-wrong-text",
              )}
            >
              <Icon aria-hidden="true" className="size-5 shrink-0" />
              <h2 className="text-[18px] leading-6 font-bold text-fg">
                {correct
                  ? t("feedback.correct_title")
                  : t("feedback.wrong_title")}
              </h2>
            </div>
            {correct && result.xp_earned > 0 && (
              <div className="flex items-center gap-1 rounded-sm bg-xp px-2 py-[3px] font-mono text-[12px] leading-4 font-bold whitespace-nowrap text-xp-fg">
                <Zap aria-hidden="true" strokeWidth={2.5} className="size-3" />
                <span>{t("common.xp_gain", { count: result.xp_earned })}</span>
              </div>
            )}
          </div>
          {showExplanation && (
            <p
              lang={questionLocale}
              className="m-0 text-[15px] leading-[22px] text-fg"
            >
              {result.explanation}
            </p>
          )}
        </div>
        <button
          type="button"
          onClick={onReport}
          className="flex min-h-11 w-max cursor-pointer items-center gap-1.5 text-[14px] leading-5 font-semibold text-fg-muted underline underline-offset-3"
        >
          <Flag aria-hidden="true" className="size-[15px] shrink-0" />
          <span>{t("feedback.report")}</span>
        </button>
        <div className="flex items-center gap-2.5 pr-1 lg:pr-0">
          <span className="hidden lg:flex">
            <KeyCap>{t("session.key_enter")}</KeyCap>
          </span>
          <Button
            className="w-full lg:w-auto"
            onClick={onContinue}
            loading={finishing}
          >
            {t("common.continue")}
          </Button>
        </div>
      </div>
    </section>
  );
}
