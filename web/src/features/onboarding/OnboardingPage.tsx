import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Navigate, useNavigate, useSearchParams } from "react-router";
import { errorKind } from "@/api/client";
import {
  useConfig,
  useCreateSession,
  useMe,
  usePatchSettings,
  useSubjects,
} from "@/api/queries";
import type { Locale, Me } from "@/api/types";
import {
  EmptyState,
  FailureScreen,
  LoadingScreen,
  LoadingState,
} from "@/components/StateScreen";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { RadioRow, RadioRows } from "@/components/ui/radio-row";
import { toast } from "@/components/ui/toast-store";
import { locales, localName } from "@/i18n";
import { useChangeLocale } from "@/lib/preferences";
import { STEP_COUNT, StepFrame } from "./StepFrame";

// The copy says a session "leva uns cinco minutos".
const MINUTES_PER_SESSION = 5;
// The API's limit on university and course.
const TEXT_MAX_LENGTH = 120;

/** The step in the address (/start?step=2); anything else is step 1. */
function readStep(value: string | null): number {
  const step = Number(value);
  return Number.isInteger(step) && step >= 1 && step <= STEP_COUNT ? step : 1;
}

/** An empty field is stored as nothing, not as "". */
function textOrNull(value: string): string | null {
  const trimmed = value.trim();
  return trimmed === "" ? null : trimmed;
}

/**
 * /start: language, university and course, subject, daily goal. Someone
 * who already chose a subject has been through it and goes to Home.
 */
export default function OnboardingPage() {
  const me = useMe();
  // Read once: finishing sets a subject, and that must not send the
  // student to Home on the way to the first session.
  const [alreadyDone] = useState(() => Boolean(me.data?.current_subject));

  if (alreadyDone) return <Navigate to="/home" replace />;
  // RequireUser renders this page only once there is a user.
  if (!me.data) return <LoadingScreen />;
  return <Onboarding user={me.data} />;
}

function Onboarding({ user }: { user: Me }) {
  const { t, i18n } = useTranslation();
  const locale = i18n.language as Locale;
  const navigate = useNavigate();
  const [params, setParams] = useSearchParams();
  const step = readStep(params.get("step"));

  // Both load from the first step on, so steps 3 and 4 rarely wait.
  const subjects = useSubjects();
  const config = useConfig();
  const changeLocale = useChangeLocale();
  const patch = usePatchSettings();
  const createSession = useCreateSession();

  const [university, setUniversity] = useState(user.university ?? "");
  const [course, setCourse] = useState(user.course ?? "");
  const [pickedSubject, setPickedSubject] = useState<string | null>(null);
  const [goal, setGoal] = useState(user.settings.daily_goal);

  // The first subject is selected until the student picks one.
  const subjectList = subjects.data?.subjects ?? [];
  const subject = pickedSubject ?? subjectList[0]?.slug ?? null;
  const finishing = patch.isPending || createSession.isPending;

  function goTo(next: number, replace = false) {
    setParams(next === 1 ? {} : { step: String(next) }, { replace });
  }
  const back = step > 1 ? () => goTo(step - 1, true) : undefined;

  /** Save every answer at once, then start the first session. */
  async function finish() {
    if (!subject) return;
    try {
      await patch.mutateAsync({
        university: textOrNull(university),
        course: textOrNull(course),
        current_subject: subject,
        daily_goal: goal,
      });
    } catch (error) {
      toast({
        kind: errorKind(error) === "offline" ? "offline" : "error",
        message: t("onboarding.save_failed"),
      });
      return;
    }
    try {
      const session = await createSession.mutateAsync(subject);
      navigate(`/session/${session.id}`, { replace: true });
    } catch {
      // Home shows the subject and its own way to start, with its states.
      navigate("/home", { replace: true });
    }
  }

  const continueButton = (onClick: () => void, disabled = false) => (
    <Button className="w-full" onClick={onClick} disabled={disabled}>
      {t("common.continue")}
    </Button>
  );

  if (step === 1) {
    return (
      <StepFrame
        step={1}
        title={t("onboarding.language_title")}
        body={t("onboarding.language_body")}
        onSkip={() => goTo(2)}
        action={continueButton(() => goTo(2))}
      >
        <RadioRows<Locale>
          className="pb-0"
          label={t("common.language")}
          value={locale}
          onChange={changeLocale}
        >
          {locales.map((option) => (
            <RadioRow
              key={option}
              value={option}
              title={t(`common.languages.${option}`)}
            />
          ))}
        </RadioRows>
      </StepFrame>
    );
  }

  if (step === 2) {
    return (
      <StepFrame
        step={2}
        title={t("onboarding.study_title")}
        body={t("onboarding.study_body")}
        onBack={back}
        onSkip={() => {
          setUniversity("");
          setCourse("");
          goTo(3);
        }}
        action={continueButton(() => goTo(3))}
      >
        <div className="flex flex-col gap-4">
          <Input
            label={t("onboarding.university")}
            placeholder={t("onboarding.university_placeholder")}
            value={university}
            maxLength={TEXT_MAX_LENGTH}
            autoComplete="organization"
            onChange={(event) => setUniversity(event.target.value)}
          />
          <Input
            label={t("onboarding.course")}
            placeholder={t("onboarding.course_placeholder")}
            value={course}
            maxLength={TEXT_MAX_LENGTH}
            onChange={(event) => setCourse(event.target.value)}
          />
        </div>
      </StepFrame>
    );
  }

  if (step === 3) {
    if (subjects.error) {
      return (
        <FailureScreen error={subjects.error} onRetry={subjects.refetch} />
      );
    }
    return (
      <StepFrame
        step={3}
        title={t("onboarding.subject_title")}
        body={t("onboarding.subject_body")}
        onBack={back}
        onSkip={() => goTo(4)}
        action={continueButton(() => goTo(4), !subject)}
      >
        {!subjects.data ? (
          <LoadingState />
        ) : subjectList.length === 0 ? (
          <EmptyState
            title={t("onboarding.no_subjects_title")}
            body={t("onboarding.no_subjects_body")}
          />
        ) : (
          <RadioRows
            className="pb-0"
            label={t("onboarding.subject_label")}
            value={subject}
            onChange={setPickedSubject}
          >
            {subjectList.map((item) => (
              <RadioRow
                key={item.slug}
                value={item.slug}
                title={localName(item, locale)}
              />
            ))}
          </RadioRows>
        )}
      </StepFrame>
    );
  }

  if (config.error) {
    return <FailureScreen error={config.error} onRetry={config.refetch} />;
  }
  return (
    <StepFrame
      step={4}
      title={t("onboarding.goal_title")}
      body={t("onboarding.goal_body", {
        n: config.data?.session_length ?? 10,
      })}
      onBack={back}
      onSkip={() => void finish()}
      action={
        <Button
          className="w-full"
          onClick={() => void finish()}
          loading={finishing}
          disabled={!subject || !config.data}
        >
          {t("common.lets_practice")}
        </Button>
      }
    >
      {!config.data ? (
        <LoadingState />
      ) : (
        <RadioRows
          className="pb-0"
          label={t("onboarding.goal_label")}
          value={String(goal)}
          onChange={(value) => setGoal(Number(value))}
        >
          {config.data.daily_goal_options.map((option) => (
            <GoalRow
              key={option}
              goal={option}
              sessionLength={config.data.session_length}
            />
          ))}
        </RadioRows>
      )}
    </StepFrame>
  );
}

/** "20 questões por dia" over "Duas sessões · cerca de 10 min". */
function GoalRow({
  goal,
  sessionLength,
}: {
  goal: number;
  sessionLength: number;
}) {
  const { t } = useTranslation();
  const sessions = Math.ceil(goal / sessionLength);
  const minutes = sessions * MINUTES_PER_SESSION;
  const sub =
    sessions === 1
      ? t("onboarding.goal_sessions_1", { minutes })
      : sessions === 2
        ? t("onboarding.goal_sessions_2", { minutes })
        : sessions === 3
          ? t("onboarding.goal_sessions_3", { minutes })
          : t("onboarding.goal_sessions_n", { n: sessions, minutes });
  return (
    <RadioRow
      value={String(goal)}
      title={t("onboarding.goal_option", { n: goal })}
      sub={sub}
    />
  );
}
