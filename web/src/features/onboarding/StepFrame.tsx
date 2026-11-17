import { ArrowLeft } from "lucide-react";
import type { ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { Mel } from "@/components/Mel";
import { Button } from "@/components/ui/button";
import { IconButton } from "@/components/ui/icon-button";
import { cn } from "@/lib/utils";

export const STEP_COUNT = 4;

type StepFrameProps = {
  step: number;
  title: string;
  body: string;
  /** Absent on the first step, where the mockup leaves the place empty. */
  onBack?: () => void;
  onSkip: () => void;
  /** The main button, at the bottom. */
  action: ReactNode;
  children: ReactNode;
};

/** The step bar of v1-onboarding-*: back, four segments, Pular. */
function StepHeader({
  step,
  onBack,
  onSkip,
}: Pick<StepFrameProps, "step" | "onBack" | "onSkip">) {
  const { t } = useTranslation();
  return (
    <div className="flex items-center gap-2">
      {onBack ? (
        <IconButton
          aria-label={t("common.back")}
          onClick={onBack}
          className="[&_svg]:size-[22px]"
        >
          <ArrowLeft />
        </IconButton>
      ) : (
        <div className="size-11 shrink-0" />
      )}
      <div
        role="progressbar"
        aria-label={t("onboarding.step")}
        aria-valuemin={1}
        aria-valuemax={STEP_COUNT}
        aria-valuenow={step}
        className="grid grow grid-cols-4 gap-1"
      >
        {Array.from({ length: STEP_COUNT }, (_, index) => (
          <div
            key={index}
            className={cn(
              "h-2 rounded-px",
              index < step ? "bg-brand" : "bg-border",
            )}
          />
        ))}
      </div>
      {/* The mockup's ghost button keeps a transparent 1.5 px border. */}
      <Button
        variant="ghost"
        size="md"
        onClick={onSkip}
        className="border-[1.5px] border-transparent"
      >
        {t("common.skip")}
      </Button>
    </div>
  );
}

/**
 * One onboarding step. Phones: the page itself, with the button at the
 * bottom edge. From 1280 px: a 520 px card in the middle of the window.
 */
export function StepFrame({
  step,
  title,
  body,
  onBack,
  onSkip,
  action,
  children,
}: StepFrameProps) {
  const { t } = useTranslation();
  return (
    <div className="flex min-h-dvh flex-col lg:items-center lg:justify-center lg:p-10">
      <div
        className={cn(
          "flex w-full grow flex-col md:mx-auto md:max-w-[688px]",
          "lg:mx-0 lg:w-[520px] lg:max-w-none lg:grow-0 lg:gap-[22px]",
          "lg:rounded-xl lg:border lg:border-border lg:bg-surface",
          "lg:px-8 lg:pt-5 lg:pb-8 lg:shadow-step-xl",
        )}
      >
        <div className="pt-[calc(8px+env(safe-area-inset-top))] pr-2 pl-4 md:pr-4 md:pl-6 lg:-mr-3 lg:p-0">
          <StepHeader step={step} onBack={onBack} onSkip={onSkip} />
        </div>
        {/* From 1280 px the card spaces these itself (display: contents). */}
        <div className="flex grow flex-col gap-5 px-4 pt-4 pb-[calc(24px+env(safe-area-inset-bottom))] md:px-6 lg:contents">
          <div className="flex flex-col gap-2.5">
            <div className="flex items-end gap-3">
              <Mel pose="wave" head scale={4} />
              <span className="pb-1 font-mono text-[12px] leading-4 text-fg-muted">
                {t("onboarding.step_of", { step, total: STEP_COUNT })}
              </span>
            </div>
            <h1 className="text-[24px] leading-[30px] font-bold tracking-[-0.01em] text-balance">
              {title}
            </h1>
            <p className="text-[15px] leading-[22px] text-fg-muted">{body}</p>
          </div>
          {children}
          <div className="mt-auto pr-1">{action}</div>
        </div>
      </div>
    </div>
  );
}
