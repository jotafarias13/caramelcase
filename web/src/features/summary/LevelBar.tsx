import { Zap } from "lucide-react";
import { useTranslation } from "react-i18next";
import type { SessionSummary } from "@/api/types";
import { Badge } from "@/components/ui/badge";
import { XpBar } from "@/components/ui/xp-bar";
import { useCountUp, useStarted } from "./motion";
import { leveledUp, levelBar } from "./rules";

// The chip of the XP bar: fill --xp, text --on-xp, an 11 px zap. It lifts
// 12 px into place over the xp-gain duration.
const chip =
  "bg-xp px-[7px] text-xp-fg [&_svg]:size-[11px] animate-[toast-in_var(--dur-xp)_ease-out]";

/**
 * The level and its XP bar, with this session's XP as the fresh segment.
 * A level up says "Subiu de nível!", fills the bar and names the new level
 * in the chip (design/README.md, "XP bar").
 */
export function LevelBar({ summary }: { summary: SessionSummary }) {
  const { t } = useTranslation();
  const bar = levelBar(summary);
  const up = leveledUp(summary);
  // xp-gain: the bar fills from where the level stood before the session,
  // and the chip counts up.
  const started = useStarted("--dur-xp");
  const shownXp = useCountUp(0, summary.xp_earned, "--dur-xp");

  return (
    <XpBar
      className="w-[320px] max-w-full self-center"
      label={
        up
          ? t("summary.level_up")
          : t("common.level", { level: summary.level_after.level })
      }
      badge={
        <Badge className={chip}>
          <Zap aria-hidden="true" strokeWidth={2.5} />
          <span>
            {up
              ? t("common.level", { level: summary.level_after.level })
              : t("common.xp_gain", { count: shownXp })}
          </span>
        </Badge>
      }
      count={t("summary.level_count", { xp: bar.value, max: bar.max })}
      barLabel={t("summary.level_xp")}
      value={started ? bar.value : bar.before}
      max={bar.max}
      gained={started ? bar.gained : 0}
    />
  );
}
