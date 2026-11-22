import { Flame, Minus, TrendingDown, TrendingUp, Zap } from "lucide-react";
import type { ReactNode } from "react";
import { useTranslation } from "react-i18next";
import type { SessionSummary } from "@/api/types";
import { Explain, explainedLabel } from "@/components/Explain";
import type { HintId } from "@/lib/hints";
import { cn } from "@/lib/utils";
import { useCountUp } from "./motion";
import { extendedStreakToday, formatDelta } from "./rules";

type StatCardProps = {
  /** What the number is: a tap on the card explains it. */
  topic: HintId;
  /** Explain it once without being asked (lib/hints.ts). */
  hint?: boolean;
  /** The colour of the 24 px icon tile. */
  tile: string;
  icon: ReactNode;
  label: string;
  value: ReactNode;
  children?: ReactNode;
};

// The "Stat card" of design/README.md, as the summary mockups draw it,
// made a button: its dotted label says that a tap explains the number.
function StatCard({
  topic,
  hint,
  tile,
  icon,
  label,
  value,
  children,
}: StatCardProps) {
  return (
    <Explain topic={topic} hint={hint}>
      <button
        type="button"
        className="flex min-w-0 cursor-pointer flex-col gap-1.5 rounded-lg border border-border bg-surface p-3 text-left hover:bg-surface-raised"
      >
        <span className="flex items-center gap-1.5">
          <span
            aria-hidden="true"
            className={cn(
              "flex size-6 shrink-0 items-center justify-center rounded-sm text-ink [&_svg]:size-3.5 [&_svg]:shrink-0",
              tile,
            )}
          >
            {icon}
          </span>
          <span
            className={cn(
              "font-mono text-[11px] leading-[14px] text-fg-muted",
              explainedLabel,
            )}
          >
            {label}
          </span>
        </span>
        <span className="font-mono text-[20px] leading-6 font-extrabold whitespace-nowrap text-fg tabular-nums">
          {value}
        </span>
        {children}
      </button>
    </Explain>
  );
}

type StatCardsProps = {
  summary: SessionSummary;
  /** Whether the one-time hints may show: not under the save prompt. */
  hints: boolean;
};

/** XP of the session, the rating in the subject and the streak. */
export function StatCards({ summary, hints }: StatCardsProps) {
  const { t } = useTranslation();
  const { rating, streak } = summary;
  // rating-delta: the number counts to its new value; a loss moves the
  // same calm way as a gain.
  const shownRating = useCountUp(
    Math.round(rating.before),
    Math.round(rating.after),
    "--dur-rating",
  );
  // streak-increment: the day this session added ticks up.
  const extended = extendedStreakToday(summary);
  const shownDays = useCountUp(
    extended ? Math.max(0, streak.current - 1) : streak.current,
    streak.current,
    "--dur-streak",
  );
  const delta = Math.round(rating.delta);
  const DeltaIcon = delta > 0 ? TrendingUp : delta < 0 ? TrendingDown : Minus;

  return (
    <div className="grid grid-cols-3 gap-2">
      <StatCard
        topic="xp"
        hint={hints}
        tile="bg-xp"
        icon={<Zap strokeWidth={2.5} />}
        label={t("common.xp")}
        value={`+${summary.xp_earned}`}
      />
      <StatCard
        topic="rating"
        hint={hints}
        tile="bg-rating"
        icon={<TrendingUp strokeWidth={2.5} />}
        label={t("common.rating")}
        value={shownRating}
      >
        <span
          className={cn(
            "flex w-max items-center gap-1 font-mono text-[13px] leading-[18px] font-bold tabular-nums",
            "animate-[fade-in_var(--dur-rating)_ease-out]",
            delta > 0 ? "text-rating-text" : "text-fg-muted",
          )}
        >
          <DeltaIcon
            aria-hidden="true"
            strokeWidth={2.5}
            className="size-3.5 shrink-0"
          />
          <span>{formatDelta(delta)}</span>
        </span>
      </StatCard>
      <StatCard
        topic="streak"
        tile="bg-streak"
        icon={<Flame strokeWidth={2.5} />}
        label={t("common.streak")}
        value={t("common.days", { count: shownDays })}
      />
    </div>
  );
}
