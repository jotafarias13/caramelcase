import { useTranslation } from "react-i18next";
import type { Goal } from "@/api/types";
import { DailyGoalRing } from "@/components/DailyGoalRing";
import { Button } from "@/components/ui/button";
import { CaramelCard } from "@/components/ui/card";

type GoalCardProps = {
  goal: Goal;
  /** The name of the next topic to work on, if any is left. */
  nextTopic: string | null;
  onPractice: () => void;
  pending: boolean;
};

// The caramel card of Home: today's goal and the button that starts or
// resumes practice in the current subject.
export function GoalCard({
  goal,
  nextTopic,
  onPractice,
  pending,
}: GoalCardProps) {
  const { t } = useTranslation();
  return (
    <CaramelCard className="pt-4 pr-5 pb-5 pl-4">
      <div className="flex items-center gap-3.5">
        <DailyGoalRing
          tone="caramel"
          done={goal.questions}
          goal={goal.goal}
          label={t("home.goal_ring", { done: goal.questions, goal: goal.goal })}
        />
        <div className="flex min-w-0 flex-col gap-0.5">
          <span className="font-mono text-[11px] leading-4 font-bold">
            {t("home.goal_label")}
          </span>
          <span className="text-[20px] leading-[26px] font-bold">
            {goal.met
              ? t("home.goal_met")
              : t("home.goal_remaining", { count: goal.remaining })}
          </span>
          {nextTopic && (
            <span className="text-[14px] leading-5 font-medium">
              {t("home.next_topic", { topic: nextTopic })}
            </span>
          )}
        </div>
      </div>
      <Button
        variant="onCaramel"
        className="w-full"
        loading={pending}
        onClick={onPractice}
      >
        {goal.questions === 0 ? t("common.start") : t("common.continue")}
      </Button>
    </CaramelCard>
  );
}
