// The decisions of the summary screen, as plain functions of the API's
// data, so each one is tested on its own (summary.test.tsx tests the
// screen around them).
import type { Me, SessionSummary } from "@/api/types";

/**
 * A loss when the session lowered the rating in the subject; a gain
 * otherwise, an unchanged rating included. The words change with it; the
 * colours and the motion do not turn alarming (design/README.md, "Rating
 * badge").
 */
export function isLoss(summary: SessionSummary): boolean {
  return summary.rating.delta < 0;
}

/** The session took the student into a new level. */
export function leveledUp(summary: SessionSummary): boolean {
  return summary.level_after.level > summary.level_before.level;
}

/**
 * What the XP bar shows: the XP of the level the student is in and the
 * part of it this session earned. On a level up the bar is full, as the
 * design draws it, and the fresh part is what filled the old level.
 */
export function levelBar(summary: SessionSummary): {
  value: number;
  max: number;
  gained: number;
  before: number;
} {
  const { level_before: before, level_after: after } = summary;
  const max = after.xp_per_level;
  if (leveledUp(summary)) {
    return {
      value: max,
      max,
      gained: max - before.xp_in_level,
      before: before.xp_in_level,
    };
  }
  return {
    value: after.xp_in_level,
    max,
    gained: after.xp_in_level - before.xp_in_level,
    before: before.xp_in_level,
  };
}

/**
 * The session was the first one finished today, so it is the one that
 * moved the streak: today's answered questions are exactly this session's.
 * Read at the moment of the request, like the streak itself; a false "no"
 * only skips the animation.
 */
export function extendedStreakToday(summary: SessionSummary): boolean {
  return summary.goal.questions === summary.total;
}

/**
 * The prompt to save progress. The spec asks for it after the first
 * finished session, so a guest sees it on the summary of that session and
 * on no later one: asked once, never nagged.
 */
export function shouldOfferSave(me: Me, summary: SessionSummary): boolean {
  return me.is_guest && summary.sessions_finished === 1;
}

/** "+14", "−9" (a real minus sign) or "±0". */
export function formatDelta(delta: number): string {
  const rounded = Math.round(delta);
  if (rounded > 0) return `+${rounded}`;
  if (rounded < 0) return `−${Math.abs(rounded)}`;
  return "±0";
}
