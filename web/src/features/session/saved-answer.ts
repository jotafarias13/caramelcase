// The option a student picked, kept on the device until the server has
// graded it. It survives a reload, and an answer given without a network
// waits here to be sent when the connection returns (docs/DECISIONS.md,
// "Offline: the server still grades").
import type { OptionKey } from "@/api/types";

export type SavedAnswer = {
  key: OptionKey;
  /**
   * Set once the student pressed "Verificar": the answer is given and
   * waits for the network, with the time it took.
   */
  timeMs?: number;
};

const optionKeys: OptionKey[] = ["a", "b", "c", "d"];

function storageKey(sessionId: string, questionId: string): string {
  return `caramelcase.answer.${sessionId}.${questionId}`;
}

// localStorage can be missing or full (private windows); losing the
// selection then is better than breaking the question.
export function loadSavedAnswer(
  sessionId: string,
  questionId: string,
): SavedAnswer | null {
  try {
    const raw = localStorage.getItem(storageKey(sessionId, questionId));
    if (!raw) return null;
    const value = JSON.parse(raw) as Partial<SavedAnswer>;
    if (!optionKeys.includes(value.key as OptionKey)) return null;
    return {
      key: value.key as OptionKey,
      timeMs: typeof value.timeMs === "number" ? value.timeMs : undefined,
    };
  } catch {
    return null;
  }
}

export function saveAnswer(
  sessionId: string,
  questionId: string,
  answer: SavedAnswer,
): void {
  try {
    localStorage.setItem(
      storageKey(sessionId, questionId),
      JSON.stringify(answer),
    );
  } catch {
    // Nothing to do: see above.
  }
}

export function forgetAnswer(sessionId: string, questionId: string): void {
  try {
    localStorage.removeItem(storageKey(sessionId, questionId));
  } catch {
    // Nothing to do: see above.
  }
}
