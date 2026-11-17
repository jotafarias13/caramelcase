import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

const tones = {
  brand: "bg-brand text-brand-fg",
  info: "bg-info-tint text-info-text",
  correct: "bg-correct-tint text-correct-text",
  warning: "bg-warning-tint text-warning-text",
  neutral: "bg-surface-raised text-fg-muted",
};

type BadgeProps = {
  tone?: keyof typeof tones;
  children: ReactNode;
  className?: string;
};

// "Badge" in design/README.md: a small mono label, such as a subject's
// "ed/" or a count.
export function Badge({ tone = "brand", children, className }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex shrink-0 items-center gap-1 rounded-sm px-2 py-0.5 whitespace-nowrap",
        "font-mono text-[11px] leading-4 font-bold [&_svg]:size-3",
        tones[tone],
        className,
      )}
    >
      {children}
    </span>
  );
}
