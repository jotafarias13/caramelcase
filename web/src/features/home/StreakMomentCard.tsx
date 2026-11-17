import { useTranslation } from "react-i18next";
import type { Streak } from "@/api/types";
import { Mel, type MelPose } from "@/components/Mel";
import { StreakCard } from "@/components/StreakCard";
import type { StreakMoment } from "@/components/streak-moment";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";

/** The moments that get a card of their own on Home. */
export type HomeStreakMoment = Exclude<StreakMoment, "extended">;

const poses: Record<HomeStreakMoment, MelPose> = {
  started: "celebrate",
  at_risk: "think",
  lost: "sleep",
};

type StreakMomentCardProps = {
  moment: HomeStreakMoment;
  streak: Streak;
  onPractice: () => void;
  pending: boolean;
  className?: string;
};

// A moment of design/screens/v1-flow-streak, "as it appears at the top of
// Home": Mel, the streak counter, one sentence and, when the streak needs
// a session today, a button that starts one.
export function StreakMomentCard({
  moment,
  streak,
  onPractice,
  pending,
  className,
}: StreakMomentCardProps) {
  const { t } = useTranslation();

  let body: string;
  let action: string | null = null;
  switch (moment) {
    case "started":
      body = t("streak.started_body");
      break;
    case "at_risk":
      body = t("streak.at_risk_body", { count: streak.current });
      action = t("streak.practice_now");
      break;
    case "lost":
      // The API always sends the lost length with a lost streak.
      body = t("streak.lost_body", { count: streak.lost_length ?? 1 });
      action = t("common.lets_practice");
      break;
  }

  return (
    <Card className={cn("p-3.5", className)}>
      <div className="flex items-center gap-3">
        <Mel pose={poses[moment]} head scale={3} />
        <StreakCard moment={moment} days={streak.current} />
      </div>
      <p className="text-[15px] leading-[22px] text-fg">{body}</p>
      {action && (
        <div className="pr-1">
          <Button
            size="md"
            className="w-full"
            loading={pending}
            onClick={onPractice}
          >
            {action}
          </Button>
        </div>
      )}
    </Card>
  );
}
