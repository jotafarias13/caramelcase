import { Info } from "lucide-react";
import { Popover } from "radix-ui";
import { useRef, useState, type ReactElement } from "react";
import { useTranslation } from "react-i18next";
import { useConfig } from "@/api/queries";
import { dismissHint, useHint, type HintId } from "@/lib/hints";
import { cn } from "@/lib/utils";
import { IconButton } from "./ui/icon-button";

/**
 * One or two sentences on what a number means. The numbers in them are
 * the API's settings, from /config; null until that has loaded.
 */
function useExplanation(topic: HintId): string | null {
  const { t } = useTranslation();
  const config = useConfig().data;
  if (!config) return null;
  const { rules } = config;
  switch (topic) {
    case "xp":
      return t("explain.xp", {
        correct: rules.xp_correct,
        finish: rules.xp_session_finished,
        level: config.xp_per_level,
      });
    case "rating":
      return t("explain.rating", {
        start: Math.round(rules.user_rating_start),
      });
    case "streak":
      return t("explain.streak");
    case "topics":
      return t("explain.topics", {
        percent: Math.round(rules.mastery_mastered_from * 100),
        answers: rules.mastery_mastered_min_answers,
      });
    case "subject":
      return t("explain.subject");
  }
}

type ExplainProps = {
  /** What is explained. */
  topic: HintId;
  /**
   * Also show it once without being asked, when its turn comes
   * (lib/hints.ts). Set it in one place per topic, and only where that
   * place can be seen.
   */
  hint?: boolean;
  /**
   * "trigger": the child is a button, and a tap on it opens the
   * explanation at any time. "anchor": the child only marks the place,
   * and the explanation shows as a hint alone.
   */
  as?: "trigger" | "anchor";
  children: ReactElement;
};

// The explanation of a number, next to it. It opens on a tap and, as a
// hint, once by itself. The design has no mockup of it: the look is the
// "Tooltip" of design/README.md, plus a button to close it. It never
// blocks the screen: a tap anywhere else closes it and still does what it
// was meant to do.
export function Explain({
  topic,
  hint = false,
  as = "trigger",
  children,
}: ExplainProps) {
  const { t } = useTranslation();
  const text = useExplanation(topic);
  const [asked, setAsked] = useState(false);
  // Whether the focus goes back to the button when the explanation
  // closes: only when the student opened it from there.
  const returnFocus = useRef(false);
  const hinting = useHint(topic, hint && text !== null);

  function ask() {
    returnFocus.current = true;
    setAsked(true);
  }

  function close(advance: boolean) {
    if (hinting) dismissHint(topic, { advance });
    setAsked(false);
  }

  return (
    <Popover.Root
      open={text !== null && (asked || hinting)}
      onOpenChange={(open) => (open ? ask() : close(false))}
    >
      {as === "anchor" ? (
        <Popover.Anchor asChild>{children}</Popover.Anchor>
      ) : (
        <Popover.Trigger asChild>{children}</Popover.Trigger>
      )}
      <Popover.Portal>
        <Popover.Content
          aria-label={t("explain.label")}
          sideOffset={6}
          collisionPadding={16}
          // A hint that opens by itself leaves the focus where it was. It
          // also stays open when the focus moves, which happens as the
          // hint before it closes and would close this one unread.
          onOpenAutoFocus={(event) => {
            if (!asked) event.preventDefault();
          }}
          onFocusOutside={(event) => {
            if (!asked) event.preventDefault();
          }}
          onCloseAutoFocus={(event) => {
            if (!returnFocus.current) event.preventDefault();
            returnFocus.current = false;
          }}
          className={cn(
            "z-40 flex w-max max-w-[min(280px,calc(100vw-32px))] flex-col rounded-tile",
            "bg-fg px-3 pt-2 text-[13px] leading-[18px] font-medium text-bg shadow-overlay",
            "animate-[fade-in_var(--dur-overlay-in)_var(--ease-standard)]",
          )}
        >
          <p>{text}</p>
          <button
            type="button"
            onClick={() => close(true)}
            className="-mr-1 min-h-11 cursor-pointer self-end rounded-sm px-1 font-bold underline underline-offset-2 focus-visible:outline-bg"
          >
            {t("explain.got_it")}
          </button>
          <Popover.Arrow width={10} height={5} className="fill-fg" />
        </Popover.Content>
      </Popover.Portal>
    </Popover.Root>
  );
}

/** The mono label of a number that explains itself on a tap. */
export const explainedLabel =
  "underline decoration-dotted decoration-1 underline-offset-[3px]";

type ExplainButtonProps = {
  topic: HintId;
  /** What the button asks: "O que é XP?". */
  label: string;
  hint?: boolean;
  className?: string;
};

/**
 * An info icon that opens an explanation, for a place without a label of
 * its own to tap. It takes 16 px in the layout and 44 px under a finger.
 */
export function ExplainButton({
  topic,
  label,
  hint,
  className,
}: ExplainButtonProps) {
  return (
    <Explain topic={topic} hint={hint}>
      <IconButton
        aria-label={label}
        className={cn("-m-3.5 text-fg-subtle [&_svg]:size-4", className)}
      >
        <Info aria-hidden="true" />
      </IconButton>
    </Explain>
  );
}
