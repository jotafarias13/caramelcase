import { useTranslation } from "react-i18next";
import { cn } from "@/lib/utils";

/** The design has three levels; a question's prior has five (1 to 5). */
export type DifficultyLevel = "easy" | "medium" | "hard";

const bars: Record<DifficultyLevel, { filled: number; colour: string }> = {
  easy: { filled: 1, colour: "bg-correct" },
  medium: { filled: 2, colour: "bg-warning" },
  hard: { filled: 3, colour: "bg-wrong" },
};

/** The difficulty badge on caramel: bars and a word, never one alone. */
export function DifficultyBadge({ level }: { level: DifficultyLevel }) {
  const { t } = useTranslation();
  const { filled, colour } = bars[level];
  return (
    <div className="flex w-max items-center gap-2 rounded-sm border border-brand-fg bg-brand-fg px-[9px] py-[3px] font-mono text-[12px] leading-4 whitespace-nowrap text-brand-cream lowercase">
      <div aria-hidden="true" className="flex items-center gap-0.5">
        {[0, 1, 2].map((bar) => (
          <div
            key={bar}
            className={cn(
              "h-2.5 w-1.5 rounded-px",
              bar < filled ? colour : "bg-ink-line",
            )}
          />
        ))}
      </div>
      <span>{t(`difficulty.${level}`)}</span>
    </div>
  );
}
