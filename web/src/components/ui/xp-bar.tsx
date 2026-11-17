import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

type XpBarProps = {
  /** "Nível 4". */
  label: string;
  /** "320 / 500 XP". */
  count: string;
  /** XP inside the level and the XP a level takes. */
  value: number;
  max: number;
  /** XP won just now: drawn as a lighter segment at the end of the bar. */
  gained?: number;
  /** A chip after the label: "+12 XP", or "Nível 5" on a level up. */
  badge?: ReactNode;
  /** What a screen reader calls the bar ("XP do nível"); the label by default. */
  barLabel?: string;
  className?: string;
};

// "XP bar" in design/README.md. A change of value or gain fills the bar
// over the xp-gain duration, which is zero under reduced motion.
export function XpBar({
  label,
  count,
  value,
  max,
  gained = 0,
  badge,
  barLabel,
  className,
}: XpBarProps) {
  const percent = (amount: number) =>
    `${Math.min(100, Math.max(0, (amount / max) * 100))}%`;
  const fresh = Math.min(gained, value);
  const segment = "transition-[width] duration-xp ease-out";

  return (
    <div className={cn("flex flex-col gap-1.5", className)}>
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="text-[13px] leading-[18px] font-bold text-fg">
            {label}
          </span>
          {badge}
        </div>
        <span className="font-mono text-[12px] leading-[18px] text-fg-muted tabular-nums">
          {count}
        </span>
      </div>
      <div
        role="progressbar"
        aria-label={barLabel ?? label}
        aria-valuemin={0}
        aria-valuemax={max}
        aria-valuenow={value}
        className="flex h-3 overflow-hidden rounded-xs border border-border-strong bg-bg-well"
      >
        <div
          className={cn("bg-xp", segment)}
          style={{ width: percent(value - fresh) }}
        />
        <div
          className={cn("bg-xp-gain", segment)}
          style={{ width: percent(fresh) }}
        />
      </div>
    </div>
  );
}
