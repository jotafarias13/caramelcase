import type { Streak } from "@/api/types";

/**
 * The moments of design/screens/v1-flow-streak. "Restored" arrives with
 * streak freeze and repair (V2, V3).
 */
export type StreakMoment = "started" | "extended" | "at_risk" | "lost";

/** The moment a streak from GET /me/stats is in; null before the first. */
export function streakMoment(streak: Streak): StreakMoment | null {
  switch (streak.status) {
    case "none":
      return null;
    case "active":
      return streak.current === 1 ? "started" : "extended";
    case "at_risk":
      return "at_risk";
    case "lost":
      return "lost";
  }
}
