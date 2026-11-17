import { WifiOff } from "lucide-react";
import { useEffect, useEffectEvent, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { ApiError } from "@/api/client";
import { useAnswer } from "@/api/queries";
import type {
  AnswerResult,
  OptionKey,
  Session,
  SessionQuestion,
} from "@/api/types";
import {
  AnswerOption,
  type AnswerOptionState,
} from "@/components/AnswerOption";
import { CodeBlock } from "@/components/CodeBlock";
import { Button } from "@/components/ui/button";
import { toast } from "@/components/ui/toast-store";
import { useOnline } from "@/lib/online";
import { cn } from "@/lib/utils";
import { FeedbackPanel } from "./FeedbackPanel";
import { KeyCap } from "./KeyCap";
import { column } from "./layout";
import { QuestionHeader } from "./QuestionHeader";
import { ReportSheet } from "./ReportSheet";
import {
  answerTime,
  gradedState,
  optionsAreCode,
  questionIndex,
} from "./rules";
import { forgetAnswer, loadSavedAnswer, saveAnswer } from "./saved-answer";

type QuestionScreenProps = {
  session: Session;
  question: SessionQuestion;
  /** Show the reason under every option after the answer. */
  showReasons: boolean;
  /** Called when the student commits to an answer: the screen stays on it. */
  onCommit: () => void;
  onContinue: () => void;
  finishing: boolean;
  /** Move focus to the question: the student came here from the last one. */
  focusOnShow: boolean;
};

type Graded = { key: OptionKey; result: AnswerResult };

/**
 * One question of a session, from the first look to the feedback. Keyed by
 * the question, so every question starts with fresh state.
 */
export function QuestionScreen({
  session,
  question,
  showReasons,
  onCommit,
  onContinue,
  finishing,
  focusOnShow,
}: QuestionScreenProps) {
  const { t } = useTranslation();
  const answer = useAnswer(session.id);
  const online = useOnline();

  // What the device kept from before: a choice, or an answer waiting for
  // the network (see saved-answer.ts).
  const [saved] = useState(() => loadSavedAnswer(session.id, question.id));
  const [selected, setSelected] = useState<OptionKey | null>(
    saved?.key ?? null,
  );
  const [waitingMs, setWaitingMs] = useState<number | null>(
    saved?.timeMs ?? null,
  );
  const [graded, setGraded] = useState<Graded | null>(null);
  const [shownAt] = useState(() => Date.now());
  const [reportOpen, setReportOpen] = useState(false);

  const checking = answer.isPending;
  const canChoose = !graded && !checking;
  const codeOptions = optionsAreCode(question);

  function choose(key: OptionKey) {
    if (!canChoose) return;
    setSelected(key);
    saveAnswer(session.id, question.id, {
      key,
      timeMs: waitingMs ?? undefined,
    });
  }

  /** Keep the answer on the device until there is a network to send it. */
  function wait(key: OptionKey, timeMs: number) {
    saveAnswer(session.id, question.id, { key, timeMs });
    setWaitingMs(timeMs);
  }

  function send(key: OptionKey, timeMs: number) {
    onCommit();
    if (!navigator.onLine) {
      wait(key, timeMs);
      return;
    }
    const afterWaiting = waitingMs !== null;
    answer.mutate(
      { question_id: question.id, key, time_ms: timeMs },
      {
        onSuccess: (result) => {
          forgetAnswer(session.id, question.id);
          setWaitingMs(null);
          setGraded({ key, result });
          if (afterWaiting) {
            toast({ kind: "success", message: t("session.back_online") });
          }
        },
        onError: (error) => {
          // Status 0: the request never reached the server.
          if (error instanceof ApiError && error.status === 0) {
            wait(key, timeMs);
          } else {
            toast({ kind: "error", message: t("session.answer_failed") });
          }
        },
      },
    );
  }

  function check() {
    if (!selected || !canChoose) return;
    send(selected, waitingMs ?? answerTime(shownAt, Date.now()));
  }

  // The connection came back: send what waited, or just say so.
  const backOnline = useEffectEvent(() => {
    if (waitingMs !== null && selected && !checking) {
      send(selected, waitingMs);
    } else {
      toast({ kind: "success", message: t("session.back_online") });
    }
  });
  // An answer that waited through a reload counts as one that waited for
  // the network: it goes out as soon as the screen is up and online.
  const wasOffline = useRef(!online || waitingMs !== null);
  useEffect(() => {
    if (!online) {
      wasOffline.current = true;
    } else if (wasOffline.current) {
      wasOffline.current = false;
      backOnline();
    }
  }, [online]);

  // Keys 1 to 4 choose, Enter checks and then continues.
  const onKeyDown = useEffectEvent((event: KeyboardEvent) => {
    if (reportOpen || event.altKey || event.ctrlKey || event.metaKey) return;
    const target = event.target instanceof Element ? event.target : null;
    if (target?.closest("input, textarea, select, [role=dialog]")) return;

    const number = Number(event.key);
    if (Number.isInteger(number) && number >= 1) {
      const option = question.options[number - 1];
      if (option) choose(option.key);
      return;
    }
    if (event.key !== "Enter") return;
    // Enter on another control (the close link, Report) does its own thing.
    const control = target?.closest("a, button, [role=radio]");
    if (control && control.getAttribute("role") !== "radio") return;
    event.preventDefault();
    if (graded) onContinue();
    else check();
  });
  useEffect(() => {
    const listener = (event: KeyboardEvent) => onKeyDown(event);
    window.addEventListener("keydown", listener);
    return () => window.removeEventListener("keydown", listener);
  }, []);

  const root = useRef<HTMLDivElement>(null);
  const heading = useRef<HTMLHeadingElement>(null);
  useEffect(() => {
    if (!focusOnShow) return;
    root.current?.scrollIntoView?.({ block: "start" });
    heading.current?.focus({ preventScroll: true });
  }, [focusOnShow]);

  function optionState(key: OptionKey): AnswerOptionState {
    if (graded) return gradedState(key, graded.key, graded.result.correct_key);
    if (key === selected) return "selected";
    return checking ? "disabled" : "default";
  }

  function reasonOf(key: OptionKey): string | null {
    if (!graded || !showReasons) return null;
    return (
      graded.result.reasons.find((item) => item.key === key)?.reason ?? null
    );
  }

  return (
    <div ref={root} className="flex min-h-dvh flex-col bg-bg">
      <QuestionHeader
        subject={session.subject}
        question={question}
        index={questionIndex(session, question.id)}
        total={session.questions.length}
        headingRef={heading}
      />
      {(!online || waitingMs !== null) && (
        <div
          role="status"
          className="border-b border-warning-border bg-warning-tint text-warning-text"
        >
          <div
            className={cn(
              column,
              "flex items-center gap-2 py-2 text-[13px] leading-[18px] font-semibold",
            )}
          >
            <WifiOff aria-hidden="true" className="size-4 shrink-0" />
            <span>{t("session.offline")}</span>
          </div>
        </div>
      )}
      <main
        className={cn(
          column,
          "flex grow flex-col gap-4 pt-4",
          graded && "pb-4",
          "lg:grid lg:items-start lg:justify-center lg:gap-8 lg:pt-7 lg:pb-7",
          question.code
            ? "lg:grid-cols-[minmax(0,1fr)_440px]"
            : "lg:grid-cols-[minmax(0,640px)]",
        )}
      >
        {question.code && (
          <CodeBlock code={question.code} language={question.code_language} />
        )}
        <div
          role="radiogroup"
          aria-label={t("session.options")}
          className={cn(
            "flex flex-col gap-3 pr-[3px]",
            !graded && "mt-auto lg:mt-0",
          )}
        >
          {question.options.map((option, index) => (
            <AnswerOption
              key={option.key}
              index={index + 1}
              text={option.text}
              lang={question.locale}
              code={codeOptions}
              state={optionState(option.key)}
              reason={reasonOf(option.key)}
              onSelect={canChoose ? () => choose(option.key) : undefined}
            />
          ))}
        </div>
      </main>
      {graded ? (
        <FeedbackPanel
          result={graded.result}
          showExplanation={!showReasons}
          questionLocale={question.locale}
          onReport={() => setReportOpen(true)}
          onContinue={onContinue}
          finishing={finishing}
        />
      ) : (
        <CheckBar
          canCheck={Boolean(selected) && canChoose}
          checking={checking}
          onCheck={check}
        />
      )}
      {graded && (
        <ReportSheet
          questionId={question.id}
          open={reportOpen}
          onOpenChange={setReportOpen}
        />
      )}
    </div>
  );
}

type CheckBarProps = {
  canCheck: boolean;
  checking: boolean;
  onCheck: () => void;
};

/** "Verificar", with the keyboard's hints beside it on desktop. */
function CheckBar({ canCheck, checking, onCheck }: CheckBarProps) {
  const { t } = useTranslation();
  return (
    <div className="lg:border-t lg:border-border">
      <div
        className={cn(
          column,
          "flex items-center justify-between gap-4",
          "pt-5 pb-[calc(22px+env(safe-area-inset-bottom))]",
          "lg:pt-4 lg:pr-11 lg:pb-[calc(20px+env(safe-area-inset-bottom))]",
        )}
      >
        <div className="hidden items-center gap-2 text-[13px] leading-[18px] text-fg-muted lg:flex">
          {["1", "2", "3", "4"].map((key) => (
            <KeyCap key={key}>{key}</KeyCap>
          ))}
          <span>{t("session.key_select")}</span>
          <span aria-hidden="true">·</span>
          <KeyCap>{t("session.key_enter")}</KeyCap>
          <span>{t("session.key_check")}</span>
        </div>
        <div className="w-full pr-1 lg:w-auto lg:pr-0">
          <Button
            className="w-full lg:w-auto"
            disabled={!canCheck && !checking}
            loading={checking}
            onClick={onCheck}
          >
            {checking ? t("session.checking") : t("session.check")}
          </Button>
        </div>
      </div>
    </div>
  );
}
