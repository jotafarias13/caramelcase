// The rules of the landing page's try-it question, apart from React. Its
// text is in the translation files under landing.sample.
import type { AnswerOptionState } from "@/components/AnswerOption";

export const SAMPLE_KEYS = ["a", "b", "c", "d"] as const;
export type SampleKey = (typeof SAMPLE_KEYS)[number];

/** "Pilha" / "Stack": the structure that is LIFO. */
export const SAMPLE_CORRECT_KEY: SampleKey = "b";

/**
 * How an option looks: chosen or not before the answer; after it, the
 * same verdicts as in a session (the choice right or wrong, and the right
 * option revealed when the choice was wrong).
 */
export function sampleState(
  key: SampleKey,
  selected: SampleKey | null,
  answered: boolean,
): AnswerOptionState {
  if (!answered) return key === selected ? "selected" : "default";
  if (key === selected) return key === SAMPLE_CORRECT_KEY ? "correct" : "wrong";
  if (key === SAMPLE_CORRECT_KEY) return "revealed";
  return "default";
}
