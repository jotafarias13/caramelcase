import { Minus, TrendingDown, TrendingUp } from "lucide-react";
import { useTranslation } from "react-i18next";
import { cn } from "@/lib/utils";

type RatingCardProps = {
  /** The mono label on top: "rating · estruturas de dados". */
  label: string;
  /** The rating now. */
  rating: number;
  /** How much the last session moved it. */
  delta: number;
  className?: string;
};

/** "+14", "−9" (a real minus sign) or "±0". */
function formatDelta(delta: number): string {
  if (delta > 0) return `+${delta}`;
  if (delta < 0) return `−${Math.abs(delta)}`;
  return "±0";
}

// The rating card of Home: the number, its last change and one line that
// says what it means. A loss is grey, never red (design/README.md,
// "Rating badge").
export function RatingCard({
  label,
  rating,
  delta,
  className,
}: RatingCardProps) {
  const { t } = useTranslation();
  const rounded = Math.round(delta);
  const DeltaIcon =
    rounded > 0 ? TrendingUp : rounded < 0 ? TrendingDown : Minus;
  const line =
    rounded > 0
      ? t("home.rating_up")
      : rounded < 0
        ? t("home.rating_down")
        : t("home.rating_same");

  return (
    <div
      className={cn(
        "flex w-[248px] max-w-full flex-col gap-1 rounded-lg px-4 py-3.5",
        "border-[1.5px] border-border-strong bg-surface",
        className,
      )}
    >
      <div className="font-mono text-[11px] leading-4 text-fg-muted">
        {label}
      </div>
      <div className="flex items-baseline gap-2.5">
        <span className="font-mono text-stat-mono text-fg tabular-nums">
          {Math.round(rating)}
        </span>
        <span
          className={cn(
            "flex w-max items-center gap-1 font-mono text-[13px] leading-[18px] font-bold tabular-nums",
            rounded > 0 ? "text-rating-text" : "text-fg-muted",
          )}
        >
          <DeltaIcon
            aria-hidden="true"
            strokeWidth={2.5}
            className="size-3.5 shrink-0"
          />
          <span>{formatDelta(rounded)}</span>
        </span>
      </div>
      <div className="text-[12px] leading-[17px] text-fg-muted">{line}</div>
    </div>
  );
}
