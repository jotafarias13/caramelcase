import { Check } from "lucide-react";
import { cn } from "@/lib/utils";

const SIZE = 80;
const RADIUS = 32;
const STROKE = 8;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

type DailyGoalRingProps = {
  /** Questions answered today. */
  done: number;
  /** Questions the daily goal asks for. */
  goal: number;
  /** "caramel" on the goal card, "surface" on a plain card. */
  tone?: "caramel" | "surface";
  /** Read out instead of the drawing: "Meta de hoje: 12 de 20 questões". */
  label: string;
  className?: string;
};

// "Daily-goal ring" in design/README.md: 80 × 80, the arc starts at 12
// o'clock. When the goal is met the centre shows a check instead of the
// count.
export function DailyGoalRing({
  done,
  goal,
  tone = "surface",
  label,
  className,
}: DailyGoalRingProps) {
  const met = done >= goal;
  const share = goal > 0 ? Math.min(1, done / goal) : 1;
  const arc = (share * CIRCUMFERENCE).toFixed(1);
  const onCaramel = tone === "caramel";

  return (
    <div
      role="img"
      aria-label={label}
      className={cn("relative size-20 shrink-0", className)}
    >
      <svg
        aria-hidden="true"
        viewBox={`0 0 ${SIZE} ${SIZE}`}
        className="size-20"
      >
        <circle
          cx={SIZE / 2}
          cy={SIZE / 2}
          r={RADIUS}
          fill="none"
          strokeWidth={STROKE}
          className={onCaramel ? "stroke-ink-24" : "stroke-border"}
        />
        <circle
          cx={SIZE / 2}
          cy={SIZE / 2}
          r={RADIUS}
          fill="none"
          strokeWidth={STROKE}
          strokeDasharray={`${arc} ${CIRCUMFERENCE.toFixed(1)}`}
          transform={`rotate(-90 ${SIZE / 2} ${SIZE / 2})`}
          className={cn(
            onCaramel ? "stroke-ink" : "stroke-brand",
            // On caramel the arc stays ink: the correct green would vanish
            // on the caramel fill.
            met && !onCaramel && "stroke-correct",
          )}
        />
      </svg>
      {met ? (
        <div
          className={cn(
            "absolute inset-0 flex items-center justify-center",
            onCaramel ? "text-ink" : "text-correct-text",
          )}
        >
          <Check aria-hidden="true" strokeWidth={3} className="size-7" />
        </div>
      ) : (
        <div
          className={cn(
            "absolute inset-0 flex items-baseline justify-center pt-7 font-mono tabular-nums",
            onCaramel ? "text-ink" : "text-fg",
          )}
        >
          <span className="text-[18px] leading-[22px] font-extrabold">
            {done}
          </span>
          <span className="text-[11px] leading-[14px]">/{goal}</span>
        </div>
      )}
    </div>
  );
}
