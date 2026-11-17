import type { TopicWithMastery } from "@/api/types";
import { topicNodeState } from "@/components/topic-node-state";

/**
 * How full a topic's bar is under "Domínio por tópico". It follows the
 * topic's state on Home (docs/DECISIONS.md): a mastered topic is full, a
 * topic in progress shows its accuracy, and a new topic is empty, as its
 * node on Home shows no percentage either.
 */
export function masteryPercent(topic: TopicWithMastery): number {
  switch (topicNodeState(topic.mastery)) {
    case "mastered":
      return 100;
    case "in_progress":
      return Math.round(topic.accuracy * 100);
    default:
      return 0;
  }
}
