import { Flame, TriangleAlert } from "lucide-react";
import { useTranslation } from "react-i18next";
import { cn } from "@/lib/utils";
import type { StreakMoment } from "./streak-moment";

const tileClasses: Record<StreakMoment, string> = {
  started: "border-solid border-streak bg-streak text-streak-fg",
  extended: "border-solid border-streak bg-streak text-streak-fg",
  at_risk:
    "border-dashed border-warning-border bg-warning-tint text-warning-text",
  lost: "border-dashed border-border-strong bg-bg text-fg-subtle",
};

type StreakCardProps = {
  moment: StreakMoment;
  /** Days in a row; ignored once the streak is lost. */
  days: number;
  /**
   * Whether today's goal is met. The streak counts a day with one finished
   * session, so "extended" names the goal only when it is true.
   */
  goalMet?: boolean;
  className?: string;
};

// "Streak counter" in design/README.md: a 248 × 64 card.
export function StreakCard({
  moment,
  days,
  goalMet = false,
  className,
}: StreakCardProps) {
  const { t } = useTranslation();
  const lost = moment === "lost";
  const filled = moment === "started" || moment === "extended";

  return (
    <div
      className={cn(
        "flex h-16 w-[248px] max-w-full min-w-0 shrink items-center gap-3 rounded-lg px-3",
        "border-[1.5px] border-border-strong bg-surface",
        className,
      )}
    >
      <span
        aria-hidden="true"
        className={cn(
          "flex size-10 shrink-0 items-center justify-center rounded-tile border-[1.5px]",
          tileClasses[moment],
        )}
      >
        <Flame
          className="size-[22px]"
          fill={filled ? "currentColor" : "none"}
        />
      </span>
      <div className="flex min-w-0 flex-col gap-0.5">
        <div
          className={cn(
            "text-[15px] leading-5 font-bold",
            lost ? "text-fg-muted" : "text-fg",
          )}
        >
          {lost
            ? t("streak.lost_title")
            : t("streak.days_in_a_row", { count: days })}
        </div>
        <SubLine moment={moment} goalMet={goalMet} />
      </div>
    </div>
  );
}

function SubLine({
  moment,
  goalMet,
}: {
  moment: StreakMoment;
  goalMet: boolean;
}) {
  const { t } = useTranslation();
  const line = "flex items-center gap-1 text-[12px] leading-4 font-medium";
  switch (moment) {
    case "started":
      return (
        <div className={cn(line, "text-fg-muted")}>
          <span>{t("streak.started_sub")}</span>
        </div>
      );
    case "extended":
      return (
        <div className={cn(line, "text-fg-muted")}>
          <span>
            {goalMet
              ? t("streak.extended_goal_met_sub")
              : t("streak.extended_sub")}
          </span>
        </div>
      );
    case "at_risk":
      return (
        <div className={cn(line, "text-warning-text")}>
          <TriangleAlert
            aria-hidden="true"
            strokeWidth={2.5}
            className="size-3 shrink-0"
          />
          <span>{t("streak.at_risk_sub")}</span>
        </div>
      );
    case "lost":
      return (
        <div className={cn(line, "text-fg-muted")}>
          <span>{t("streak.lost_sub")}</span>
        </div>
      );
  }
}
