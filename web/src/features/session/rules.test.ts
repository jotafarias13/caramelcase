import { describe, expect, it } from "vitest";
import { codeQuestion, session, sessionAnswered } from "@/test/fixtures";
import {
  answerTime,
  difficultyLevel,
  firstOpenQuestion,
  gradedState,
  nextOpenQuestion,
  optionsAreCode,
} from "./rules";

describe("difficultyLevel", () => {
  it("maps the five priors onto the badge's three levels", () => {
    expect([1, 2, 3, 4, 5].map(difficultyLevel)).toEqual([
      "easy",
      "easy",
      "medium",
      "hard",
      "hard",
    ]);
  });
});

describe("firstOpenQuestion", () => {
  it("is the first question without an answer", () => {
    const resumed = sessionAnswered(3);
    expect(firstOpenQuestion(resumed)?.id).toBe(resumed.questions[3].id);
  });

  it("is null when every question is answered", () => {
    expect(firstOpenQuestion(sessionAnswered(10))).toBeNull();
  });
});

describe("nextOpenQuestion", () => {
  it("skips the question on screen even before the cache knows it", () => {
    const [first, second] = session.questions;
    expect(nextOpenQuestion(session, first.id)?.id).toBe(second.id);
  });

  it("is null after the last open question", () => {
    const last = sessionAnswered(9).questions[9];
    expect(nextOpenQuestion(sessionAnswered(9), last.id)).toBeNull();
  });
});

describe("optionsAreCode", () => {
  it("is true for the outputs of a program", () => {
    expect(optionsAreCode(codeQuestion)).toBe(true);
  });

  it("is false without code", () => {
    expect(optionsAreCode(session.questions[1])).toBe(false);
  });

  it("is false for sentences about a program", () => {
    expect(
      optionsAreCode({
        ...codeQuestion,
        options: [
          { key: "a", text: "Para qualquer nó da lista." },
          { key: "b", text: "Para qualquer nó, menos o primeiro." },
          { key: "c", text: "Para qualquer nó, menos o último." },
          { key: "d", text: "Só para os nós do meio." },
        ],
      }),
    ).toBe(false);
  });
});

describe("gradedState", () => {
  it("marks a right answer as correct", () => {
    expect(gradedState("b", "b", "b")).toBe("correct");
  });

  it("marks a wrong answer and reveals the right one", () => {
    expect(gradedState("c", "c", "b")).toBe("wrong");
    expect(gradedState("b", "c", "b")).toBe("revealed");
    expect(gradedState("a", "c", "b")).toBe("default");
  });
});

describe("answerTime", () => {
  it("is the time since the question was shown, within the API's range", () => {
    expect(answerTime(1000, 4500)).toBe(3500);
    expect(answerTime(5000, 4000)).toBe(0);
    expect(answerTime(0, 10 ** 10)).toBe(86_400_000);
  });
});
