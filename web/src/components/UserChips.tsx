import { useTranslation } from "react-i18next";
import { useMe, useStats } from "@/api/queries";
import { cn } from "@/lib/utils";
import { RatingChip, StreakChip } from "./ui/chips";

/** A student's rating before the first answer in a subject. */
const STARTING_RATING = 1000;

/**
 * The streak and the rating in the current subject, side by side: at the
 * top of Home on phones and at the bottom of the sidebar on desktop.
 */
export function UserChips({ className }: { className?: string }) {
  const { t } = useTranslation();
  const me = useMe();
  const stats = useStats();
  if (!stats.data) return null;

  const { streak, subjects } = stats.data;
  const days = streak.status === "lost" ? 0 : streak.current;
  const current = subjects.find(
    (subject) => subject.slug === me.data?.current_subject,
  );
  const rating = Math.round(current?.rating ?? STARTING_RATING);

  return (
    <div className={cn("flex items-center gap-1.5 lg:gap-2", className)}>
      <StreakChip label={t("nav.streak_chip", { count: days })}>
        {days}
      </StreakChip>
      <RatingChip label={t("nav.rating_chip", { rating })}>{rating}</RatingChip>
    </div>
  );
}
