import { Check, CircleCheck, CircleX, X } from "lucide-react";
import { useTranslation } from "react-i18next";
import { cn } from "@/lib/utils";

/**
 * The states of "Answer option" in design/README.md. Hover, pressed and
 * focus are not states here: they follow the pointer and the keyboard.
 */
export type AnswerOptionState =
  "default" | "selected" | "correct" | "wrong" | "revealed" | "disabled";

type AnswerOptionProps = {
  /** The number on the key badge, 1 to 4: the key that selects it. */
  index: number;
  text: string;
  state: AnswerOptionState;
  /** Set the label in the code font, for code or a program's output. */
  code?: boolean;
  /** The line under the label that says why the option is right or wrong. */
  reason?: string | null;
  /** Leave out once the option can no longer be chosen. */
  onSelect?: () => void;
  /** The language of the text, when it is not the interface's. */
  lang?: string;
};

const frame: Record<AnswerOptionState, string> = {
  default: "border-[1.5px] border-border-strong bg-surface shadow-step-md",
  selected: "border-2 border-action-border bg-action-tint shadow-selected",
  correct:
    "border-2 border-correct-border bg-correct-tint shadow-[3px_3px_0_var(--correct-border)]",
  wrong: "border-2 border-wrong-border bg-wrong-tint",
  revealed: "border-2 border-dashed border-correct-border bg-surface",
  disabled: "border-[1.5px] border-border bg-bg text-disabled-text",
};

const keyBadge: Record<AnswerOptionState, string> = {
  default: "border-[1.5px] border-border-strong text-fg-muted",
  selected: "bg-action font-bold text-action-fg",
  correct: "bg-correct text-correct-fg",
  wrong: "bg-wrong text-wrong-fg",
  revealed: "border-[1.5px] border-correct-border text-correct-text",
  disabled: "border-[1.5px] border-border text-disabled-text",
};

// An option the student chose shows its label in bold.
const strong: AnswerOptionState[] = ["selected", "correct", "wrong"];

/**
 * One option of a multiple-choice question: a radio in a
 * role="radiogroup". It holds no state; the screen around it decides.
 */
export function AnswerOption({
  index,
  text,
  state,
  code = false,
  reason,
  onSelect,
  lang,
}: AnswerOptionProps) {
  const interactive = Boolean(onSelect) && state !== "disabled";
  const chosen = strong.includes(state);
  return (
    <button
      type="button"
      role="radio"
      aria-checked={chosen}
      aria-disabled={interactive ? undefined : true}
      disabled={state === "disabled"}
      onClick={interactive ? onSelect : undefined}
      className={cn(
        "flex min-h-14 w-full flex-col justify-center gap-1.5 rounded-lg px-3.5 py-3",
        "text-left font-sans text-fg",
        "transition-[background-color,border-color,translate,box-shadow] duration-select ease-out",
        frame[state],
        interactive
          ? "cursor-pointer hover:bg-surface-raised active:translate-x-0.5 active:translate-y-0.5 active:shadow-[1px_1px_0_var(--shadow-hard)]"
          : "cursor-default",
        // A selected option keeps its tint under the pointer.
        interactive && state === "selected" && "hover:bg-action-tint",
      )}
    >
      <span className="flex min-h-7 w-full items-center gap-3">
        <span
          aria-hidden="true"
          className={cn(
            "flex size-7 shrink-0 items-center justify-center rounded-sm font-mono text-[13px]",
            keyBadge[state],
          )}
        >
          <KeyBadgeContent state={state} index={index} />
        </span>
        <span
          lang={lang}
          className={cn(
            "min-w-0 grow",
            code
              ? "font-mono text-[15px] leading-[22px] [font-variant-ligatures:none]"
              : "text-[16px] leading-[22px]",
            chosen ? "font-bold" : "font-medium",
          )}
        >
          {text}
        </span>
        <OptionMark state={state} />
      </span>
      {reason && (
        <span
          lang={lang}
          className="block pl-10 text-[13px] leading-[19px] font-normal text-fg-muted"
        >
          {reason}
        </span>
      )}
    </button>
  );
}

function KeyBadgeContent({
  state,
  index,
}: {
  state: AnswerOptionState;
  index: number;
}) {
  if (state === "correct" || state === "revealed") {
    return <Check strokeWidth={3} className="size-4" />;
  }
  if (state === "wrong") return <X strokeWidth={3} className="size-4" />;
  return index;
}

/** What sits at the right end: the radio mark, or the verdict in words. */
function OptionMark({ state }: { state: AnswerOptionState }) {
  const { t } = useTranslation();
  if (state === "selected") {
    return (
      <svg
        aria-hidden="true"
        viewBox="0 0 24 24"
        fill="none"
        strokeWidth={2.5}
        className="size-5 shrink-0 stroke-action-text"
      >
        <circle cx="12" cy="12" r="9" />
        <circle cx="12" cy="12" r="3.5" className="fill-action-text" />
      </svg>
    );
  }
  const verdicts = {
    correct: { label: t("feedback.option_correct"), good: true },
    revealed: { label: t("feedback.option_revealed"), good: true },
    wrong: { label: t("feedback.option_yours"), good: false },
  };
  if (!(state in verdicts)) return null;
  const { label, good } = verdicts[state as keyof typeof verdicts];
  const Icon = good ? CircleCheck : CircleX;
  return (
    <span
      className={cn(
        "flex items-center gap-[5px] text-[12px] leading-4 font-bold whitespace-nowrap",
        good ? "text-correct-text" : "text-wrong-text",
      )}
    >
      {label}
      <Icon aria-hidden="true" className="size-[18px] shrink-0" />
    </span>
  );
}
