import type { MasteryLevel } from "@/api/types";

export type TopicNodeState =
  "locked" | "available" | "in_progress" | "mastered";

/**
 * How a topic is drawn, from the student's mastery (docs/DECISIONS.md):
 * new is available, learning and practiced are in progress, mastered is
 * mastered. V1 has no locked topics.
 */
export function topicNodeState(mastery: MasteryLevel): TopicNodeState {
  switch (mastery) {
    case "new":
      return "available";
    case "learning":
    case "practiced":
      return "in_progress";
    case "mastered":
      return "mastered";
  }
}
