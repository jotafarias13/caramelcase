import { useTranslation } from "react-i18next";
import { useMe, useStats } from "@/api/queries";
import { useIsDesktop } from "@/lib/useIsDesktop";
import { cn } from "@/lib/utils";
import { Explain, explainedLabel } from "./Explain";
import { RatingChip, StreakChip } from "./ui/chips";

/** A student's rating before the first answer in a subject. */
const STARTING_RATING = 1000;

// A chip under its word, as one button that explains the number.
const chipButton =
  "flex cursor-pointer flex-col items-start gap-0.5 rounded-tile text-left";
const chipWord = cn(
  "font-mono text-[11px] leading-4 text-fg-muted",
  explainedLabel,
);

type UserChipsProps = {
  /**
   * The layout this copy is drawn in. The other one is in the page too,
   * hidden by CSS, and a hint must open only where it can be seen.
   */
  shownOn: "phone" | "desktop";
  className?: string;
};

/**
 * The streak and the rating in the current subject, side by side: at the
 * top of Home on phones and at the bottom of the sidebar on desktop. Each
 * has its name on top and says what it is on a tap. The design draws the
 * two numbers alone; a new student could not tell what they were
 * (docs/DECISIONS.md, "Guidance").
 */
export function UserChips({ shownOn, className }: UserChipsProps) {
  const { t } = useTranslation();
  const me = useMe();
  const stats = useStats();
  const visible = useIsDesktop() === (shownOn === "desktop");
  if (!stats.data) return null;

  const { streak, subjects } = stats.data;
  const days = streak.status === "lost" ? 0 : streak.current;
  const current = subjects.find(
    (subject) => subject.slug === me.data?.current_subject,
  );
  const rating = Math.round(current?.rating ?? STARTING_RATING);
  // The streak means something once there is a session behind it.
  const practiced = stats.data.sessions_finished > 0;

  return (
    <div className={cn("flex items-end gap-2", className)}>
      <Explain topic="streak" hint={visible && practiced}>
        <button
          type="button"
          aria-label={t("nav.streak_chip", { count: days })}
          className={chipButton}
        >
          <span className={chipWord}>{t("common.streak")}</span>
          <StreakChip>{days}</StreakChip>
        </button>
      </Explain>
      <Explain topic="rating">
        <button
          type="button"
          aria-label={t("nav.rating_chip", { rating })}
          className={chipButton}
        >
          <span className={chipWord}>{t("common.rating")}</span>
          <RatingChip>{rating}</RatingChip>
        </button>
      </Explain>
    </div>
  );
}
