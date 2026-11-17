import { describe, expect, it } from "vitest";
import type { SessionSummary } from "@/api/types";
import { guest, me, summary } from "@/test/fixtures";
import {
  extendedStreakToday,
  formatDelta,
  isLoss,
  levelBar,
  leveledUp,
  shouldOfferSave,
} from "./rules";

function with_(changes: Partial<SessionSummary>): SessionSummary {
  return { ...summary, ...changes };
}

describe("isLoss", () => {
  it("is a loss only when the rating went down", () => {
    const rating = summary.rating;
    expect(isLoss(with_({ rating: { ...rating, delta: -1 } }))).toBe(true);
    expect(isLoss(with_({ rating: { ...rating, delta: 0 } }))).toBe(false);
    expect(isLoss(with_({ rating: { ...rating, delta: 14 } }))).toBe(false);
  });
});

describe("levelBar", () => {
  it("shows the level's XP with this session's part at the end", () => {
    expect(levelBar(summary)).toEqual({
      value: 332,
      max: 500,
      gained: 100,
      before: 232,
    });
    expect(leveledUp(summary)).toBe(false);
  });

  it("is full on a level up, the fresh part being what filled it", () => {
    const up = with_({
      level_before: { ...summary.level_before, level: 4, xp_in_level: 450 },
      level_after: { ...summary.level_after, level: 5, xp_in_level: 50 },
    });
    expect(leveledUp(up)).toBe(true);
    expect(levelBar(up)).toEqual({
      value: 500,
      max: 500,
      gained: 50,
      before: 450,
    });
  });
});

describe("extendedStreakToday", () => {
  it("is true when today's questions are this session's", () => {
    const goal = summary.goal;
    expect(
      extendedStreakToday(with_({ goal: { ...goal, questions: 10 } })),
    ).toBe(true);
    expect(
      extendedStreakToday(with_({ goal: { ...goal, questions: 20 } })),
    ).toBe(false);
  });
});

describe("shouldOfferSave", () => {
  it("asks a guest on the summary of the first finished session only", () => {
    expect(shouldOfferSave(guest, with_({ sessions_finished: 1 }))).toBe(true);
    expect(shouldOfferSave(guest, with_({ sessions_finished: 2 }))).toBe(false);
    expect(shouldOfferSave(me, with_({ sessions_finished: 1 }))).toBe(false);
  });
});

describe("formatDelta", () => {
  it("signs the change with a real minus sign", () => {
    expect(formatDelta(14)).toBe("+14");
    expect(formatDelta(-9)).toBe("−9");
    expect(formatDelta(0)).toBe("±0");
    expect(formatDelta(0.4)).toBe("±0");
  });
});
