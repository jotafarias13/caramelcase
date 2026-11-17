import { ArrowRight, CircleCheck, CircleX } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { Link } from "react-router";
import { AnswerOption } from "@/components/AnswerOption";
import { DifficultyBadge } from "@/components/DifficultyBadge";
import { Button } from "@/components/ui/button";
import { buttonVariants } from "@/components/ui/button-variants";
import { track } from "@/lib/analytics";
import { cn } from "@/lib/utils";
import {
  sampleState,
  SAMPLE_CORRECT_KEY,
  SAMPLE_KEYS,
  type SampleKey,
} from "./sample";

/**
 * The try-it question: a fixed sample that lives in the page, graded here
 * and never sent to the API (docs/DECISIONS.md). Tap an option, tap
 * Verificar, read why each option is right or wrong, then go to /start.
 */
export function SampleQuestion() {
  const { t } = useTranslation();
  const [selected, setSelected] = useState<SampleKey | null>(null);
  const [answered, setAnswered] = useState(false);
  const continueLink = useRef<HTMLAnchorElement>(null);

  function check() {
    if (!selected) return;
    setAnswered(true);
    track("landing.sample_answered", {
      correct: selected === SAMPLE_CORRECT_KEY,
    });
  }

  // Verificar is gone once the answer is in: focus goes to the next step.
  useEffect(() => {
    if (answered) continueLink.current?.focus({ preventScroll: true });
  }, [answered]);

  const correct = selected === SAMPLE_CORRECT_KEY;

  return (
    <div className="overflow-hidden rounded-card border-[1.5px] border-border-strong bg-bg shadow-step-xl">
      <div className="flex flex-col gap-2.5 bg-brand px-4 pt-3.5 pb-[18px] text-brand-fg">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-1.5 font-mono text-[12px] leading-[18px] lowercase">
            <span className="font-extrabold">
              {t("landing.sample.subject")}
            </span>
            <span aria-hidden="true">/</span>
            <span className="font-medium">{t("landing.sample.topic")}</span>
          </div>
          <DifficultyBadge level="easy" />
        </div>
        <h2 className="text-[20px] leading-[26px] font-bold text-balance">
          {t("landing.sample.stem")}
        </h2>
      </div>
      <div className="flex flex-col gap-4 px-4 pt-4 pb-5">
        <div
          role="radiogroup"
          aria-label={t("landing.options")}
          className="flex flex-col gap-3 pr-[3px]"
        >
          {SAMPLE_KEYS.map((key, index) => (
            <AnswerOption
              key={key}
              index={index + 1}
              text={t(`landing.sample.${key}`)}
              state={sampleState(key, selected, answered)}
              reason={answered ? t(`landing.sample.${key}_reason`) : null}
              onSelect={answered ? undefined : () => setSelected(key)}
            />
          ))}
        </div>
        {answered ? (
          <div className="flex flex-col gap-2.5">
            <div
              role="status"
              className={cn(
                "flex items-center gap-2",
                correct ? "text-correct-text" : "text-wrong-text",
              )}
            >
              {correct ? (
                <CircleCheck aria-hidden="true" className="size-5 shrink-0" />
              ) : (
                <CircleX aria-hidden="true" className="size-5 shrink-0" />
              )}
              <span className="text-[17px] leading-[22px] font-bold text-fg">
                {correct
                  ? t("feedback.correct_title")
                  : t("feedback.wrong_title")}
              </span>
            </div>
            <div className="pr-1">
              <Link
                ref={continueLink}
                to="/start"
                className={cn(buttonVariants(), "w-full")}
              >
                <ArrowRight aria-hidden="true" />
                {t("landing.keep_practicing")}
              </Link>
            </div>
          </div>
        ) : (
          <div className="pr-1">
            <Button className="w-full" disabled={!selected} onClick={check}>
              {t("landing.check")}
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
