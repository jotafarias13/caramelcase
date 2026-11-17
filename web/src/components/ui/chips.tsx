import { Flame, TrendingUp, Zap } from "lucide-react";
import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

// The 32 px chips of design/README.md: streak (pink), rating (lime) and
// XP (violet). Each takes the number as its child.
const chip =
  "inline-flex h-8 w-max shrink-0 items-center rounded-tile px-2.5 font-mono text-[14px] leading-5 font-extrabold tabular-nums [&_svg]:size-[15px] [&_svg]:shrink-0";

type ChipProps = {
  children: ReactNode;
  /** Says what the number is, for a screen reader. */
  label?: string;
  className?: string;
};

export function StreakChip({ children, label, className }: ChipProps) {
  return (
    <span
      aria-label={label}
      className={cn(chip, "gap-[5px] bg-streak text-streak-fg", className)}
    >
      <Flame aria-hidden="true" fill="currentColor" />
      <span>{children}</span>
    </span>
  );
}

export function RatingChip({ children, label, className }: ChipProps) {
  return (
    <span
      aria-label={label}
      className={cn(chip, "gap-1.5 bg-rating text-rating-fg", className)}
    >
      <TrendingUp aria-hidden="true" strokeWidth={2.5} />
      <span>{children}</span>
    </span>
  );
}

export function XpChip({ children, label, className }: ChipProps) {
  return (
    <span
      aria-label={label}
      className={cn(chip, "gap-1.5 bg-xp text-xp-fg", className)}
    >
      <Zap aria-hidden="true" fill="currentColor" />
      <span>{children}</span>
    </span>
  );
}
