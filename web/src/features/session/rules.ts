// The session screen's rules that need no React: which question is shown,
// how an option looks after the answer, how a difficulty is labelled.
import type { OptionKey, Session, SessionQuestion } from "@/api/types";
import type { AnswerOptionState } from "@/components/AnswerOption";
import type { DifficultyLevel } from "@/components/DifficultyBadge";

/** The three levels of the difficulty badge. */

/**
 * The design has three levels and the questions five (docs/DECISIONS.md):
 * 1 and 2 are easy, 3 is medium, 4 and 5 are hard.
 */
export function difficultyLevel(prior: number): DifficultyLevel {
  if (prior <= 2) return "easy";
  if (prior === 3) return "medium";
  return "hard";
}

/**
 * Where a session resumes: its first question without an answer. Null
 * when every question is answered.
 */
export function firstOpenQuestion(session: Session): SessionQuestion | null {
  return session.questions.find((question) => !question.answer) ?? null;
}

/** The question after `currentId` that still needs an answer, if any. */
export function nextOpenQuestion(
  session: Session,
  currentId: string,
): SessionQuestion | null {
  return (
    session.questions.find(
      (question) => !question.answer && question.id !== currentId,
    ) ?? null
  );
}

/** How far the student is: answered questions, before the current one. */
export function questionIndex(session: Session, questionId: string): number {
  const index = session.questions.findIndex(
    (question) => question.id === questionId,
  );
  return Math.max(index, 0);
}

const LONGEST_CODE_OPTION = 30;

/**
 * Options are set in the code font when they are code or output (design,
 * "Answer option"). Nothing in a question says so, so: the question shows
 * code, and every option is short and none reads as a sentence. Prose
 * options about a program ("which statement is correct") stay in Geist.
 */
export function optionsAreCode(question: SessionQuestion): boolean {
  if (!question.code) return false;
  return question.options.every(
    (option) =>
      option.text.length <= LONGEST_CODE_OPTION && !/\.\s*$/.test(option.text),
  );
}

/** The look of one option once the server has graded the answer. */
export function gradedState(
  key: OptionKey,
  chosenKey: OptionKey,
  correctKey: OptionKey,
): AnswerOptionState {
  if (key === chosenKey) return key === correctKey ? "correct" : "wrong";
  if (key === correctKey) return "revealed";
  return "default";
}

/** Milliseconds from showing a question to answering it, as the API takes it. */
export function answerTime(shownAt: number, now: number): number {
  const DAY_MS = 86_400_000;
  return Math.min(Math.max(Math.round(now - shownAt), 0), DAY_MS);
}
