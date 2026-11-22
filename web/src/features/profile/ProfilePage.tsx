import { User } from "lucide-react";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router";
import { errorKind } from "@/api/client";
import { useActivity, useMe, useStats, useSubject } from "@/api/queries";
import type { Activity, Me, Stats, SubjectDetail } from "@/api/types";
import {
  EmptyState,
  FailureScreen,
  LoadingState,
} from "@/components/StateScreen";
import { ExplainButton } from "@/components/Explain";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { RatingChip } from "@/components/ui/chips";
import { XpBar } from "@/components/ui/xp-bar";
import { localName } from "@/i18n";
import { useStartPractice } from "@/lib/useStartPractice";
import { ActivityCalendar } from "./ActivityCalendar";
import { masteryPercent } from "./mastery";

export default function ProfilePage() {
  const me = useMe();
  const stats = useStats();
  const subject = useSubject(me.data?.current_subject);
  const activity = useActivity();

  // A current subject that is no longer published only hides its card.
  const subjectGone =
    subject.error !== null && errorKind(subject.error) === "not_found";
  const failed = [stats, activity, subjectGone ? null : subject].find(
    (query) => query?.error,
  );
  if (failed) {
    return (
      <FailureScreen
        error={failed.error}
        onRetry={() => void failed.refetch()}
      />
    );
  }
  if (!me.data || !stats.data) return <LoadingState />;
  if (stats.data.questions_answered === 0) return <NoAnswersYet me={me.data} />;
  if (!activity.data || (!subject.data && !subjectGone)) {
    return <LoadingState />;
  }

  return (
    <Profile
      me={me.data}
      stats={stats.data}
      subject={subject.data ?? null}
      activity={activity.data}
    />
  );
}

/** Before the first answer there are no numbers to show. */
function NoAnswersYet({ me }: { me: Me }) {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const practice = useStartPractice(() => navigate("/subjects"));
  return (
    <>
      <h1 className="text-[24px] leading-[30px] font-bold tracking-[-0.01em] text-balance">
        {t("profile.title")}
      </h1>
      <EmptyState>
        <Button
          className="w-full"
          loading={practice.pending}
          onClick={() =>
            me.current_subject && practice.start(me.current_subject)
          }
        >
          {t("common.lets_practice")}
        </Button>
      </EmptyState>
    </>
  );
}

type ProfileProps = {
  me: Me;
  stats: Stats;
  subject: SubjectDetail | null;
  activity: Activity;
};

function Profile({ me, stats, subject, activity }: ProfileProps) {
  const { t } = useTranslation();
  const { level } = stats;

  return (
    <>
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between lg:gap-8">
        <Identity me={me} />
        <XpBar
          label={t("common.level", { level: level.level })}
          count={t("profile.level_xp", {
            xp: level.xp_in_level,
            max: level.xp_per_level,
          })}
          value={level.xp_in_level}
          max={level.xp_per_level}
          info={<ExplainButton topic="xp" label={t("explain.xp_label")} />}
          className="w-full max-w-80 lg:w-80"
        />
      </div>

      <StatGrid stats={stats} />

      <div className="flex flex-col gap-4 lg:grid lg:grid-cols-[minmax(0,1fr)_400px] lg:items-start lg:gap-6">
        <div className="flex flex-col gap-4 lg:gap-6">
          <RatingBySubject stats={stats} />
          {subject && <MasteryByTopic subject={subject} />}
        </div>
        <ActivityCalendar activity={activity} />
      </div>
    </>
  );
}

/**
 * The student's initial, name and studies. Nobody is asked for a name
 * (docs/DECISIONS.md), so without one the heading is "Perfil" and the
 * tile holds a person icon; the line under it lists what the student gave.
 */
function Identity({ me }: { me: Me }) {
  const { t } = useTranslation();
  const name = me.display_name?.trim() || null;
  const studies = [me.course, me.university]
    .map((part) => part?.trim())
    .filter(Boolean)
    .join(" · ");

  return (
    <div className="flex items-center gap-3.5">
      <span
        aria-hidden="true"
        className="flex size-14 shrink-0 items-center justify-center rounded-lg bg-brand font-mono text-[24px] leading-7 font-extrabold text-brand-fg shadow-brand"
      >
        {name ? (
          name.charAt(0).toLocaleUpperCase()
        ) : (
          <User strokeWidth={2.25} className="size-7" />
        )}
      </span>
      <div className="flex min-w-0 flex-col gap-0.5">
        <h1 className="text-[22px] leading-7 font-bold tracking-[-0.01em] text-balance">
          {name ?? t("profile.title")}
        </h1>
        {studies && (
          <span className="text-[13px] leading-[18px] text-fg-muted">
            {studies}
          </span>
        )}
      </div>
    </div>
  );
}

function StatTile({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex flex-col gap-1 rounded-lg border border-border bg-surface px-3.5 py-3">
      <span className="font-mono text-[11px] leading-[14px] text-fg-muted">
        {label}
      </span>
      <span className="font-mono text-[22px] leading-[26px] font-extrabold text-fg tabular-nums">
        {value}
      </span>
    </div>
  );
}

function StatGrid({ stats }: { stats: Stats }) {
  const { t, i18n } = useTranslation();
  const number = new Intl.NumberFormat(i18n.language);
  const percent = new Intl.NumberFormat(i18n.language, { style: "percent" });

  return (
    <div className="grid grid-cols-2 gap-2 lg:grid-cols-4">
      <StatTile
        label={t("profile.questions")}
        value={number.format(stats.questions_answered)}
      />
      <StatTile
        label={t("profile.accuracy")}
        value={percent.format(stats.accuracy)}
      />
      <StatTile
        label={t("profile.sessions")}
        value={number.format(stats.sessions_finished)}
      />
      <StatTile
        label={t("profile.best_streak")}
        value={t("common.days", { count: stats.streak.longest })}
      />
    </div>
  );
}

/** Every published subject, with the student's rating or "not yet". */
function RatingBySubject({ stats }: { stats: Stats }) {
  const { t } = useTranslation();
  return (
    <Card>
      <h2 className="text-[18px] leading-6 font-bold text-fg">
        {t("profile.rating_by_subject")}
      </h2>
      <ul className="flex flex-col">
        {stats.subjects.map((subject) => {
          const rating =
            subject.rating === null ? null : Math.round(subject.rating);
          return (
            <li
              key={subject.slug}
              className="box-content flex min-h-12 items-center justify-between gap-2 border-border not-first:border-t"
            >
              <span className="text-[15px] leading-5 font-medium text-fg">
                {localName(subject)}
              </span>
              {rating === null ? (
                <span className="text-[13px] leading-[18px] text-fg-muted">
                  {t("profile.not_practiced")}
                </span>
              ) : (
                <RatingChip label={t("nav.rating_chip", { rating })}>
                  {rating}
                </RatingChip>
              )}
            </li>
          );
        })}
      </ul>
    </Card>
  );
}

/** The topics of the current subject, as on Home, each with a bar. */
function MasteryByTopic({ subject }: { subject: SubjectDetail }) {
  const { t } = useTranslation();
  return (
    <Card>
      <div className="flex flex-col gap-0.5">
        <h2 className="text-[18px] leading-6 font-bold text-fg">
          {t("profile.mastery_by_topic")}
        </h2>
        <span className="font-mono text-[11px] leading-4 text-fg-muted">
          {localName(subject).toLocaleLowerCase()}
        </span>
      </div>
      <ul className="flex flex-col gap-3">
        {subject.topics.map((topic) => {
          const name = localName(topic);
          const percent = masteryPercent(topic);
          return (
            <li key={topic.slug} className="flex flex-col gap-[5px]">
              <div className="flex items-center justify-between gap-2">
                <span className="text-[14px] leading-5 font-medium text-fg">
                  {name}
                </span>
                <span className="font-mono text-[12px] leading-4 text-fg-muted tabular-nums">
                  {percent}%
                </span>
              </div>
              <div
                role="progressbar"
                aria-label={name}
                aria-valuemin={0}
                aria-valuemax={100}
                aria-valuenow={percent}
                className="flex h-2.5 overflow-hidden rounded-px border border-border bg-bg-well"
              >
                <div className="bg-brand" style={{ width: `${percent}%` }} />
              </div>
            </li>
          );
        })}
      </ul>
    </Card>
  );
}
