import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Link } from "react-router";
import { errorKind } from "@/api/client";
import { useMe, useStats, useSubject, useSubjects } from "@/api/queries";
import type { Me, Stats, SubjectDetail } from "@/api/types";
import { RatingCard } from "@/components/RatingCard";
import {
  EmptyState,
  FailureScreen,
  LoadingState,
} from "@/components/StateScreen";
import { StreakCard } from "@/components/StreakCard";
import { streakMoment } from "@/components/streak-moment";
import { TopicNode, TopicPath } from "@/components/TopicNode";
import { topicNodeState } from "@/components/topic-node-state";
import { UserChips } from "@/components/UserChips";
import { Button } from "@/components/ui/button";
import { buttonVariants } from "@/components/ui/button-variants";
import { localName } from "@/i18n";
import { cn } from "@/lib/utils";
import { GoalCard } from "./GoalCard";
import { StreakMomentCard } from "./StreakMomentCard";
import { SubjectSwitcher } from "./SubjectSwitcher";
import { useStartPractice } from "@/lib/useStartPractice";

/** "Carol" from "Carol Nunes"; null for a guest or an email account. */
function firstName(me: Me): string | null {
  const first = me.display_name?.trim().split(/\s+/)[0];
  return first ? first : null;
}

export default function HomePage() {
  const me = useMe();
  const stats = useStats();
  const subject = useSubject(me.data?.current_subject);
  // Loaded now, so the subject switcher opens with its list ready.
  useSubjects();

  if (subject.error && errorKind(subject.error) === "not_found") {
    return <SubjectGone />;
  }
  const failed = stats.error ? stats : subject.error ? subject : null;
  if (failed) {
    return (
      <FailureScreen
        error={failed.error}
        onRetry={() => void failed.refetch()}
      />
    );
  }
  if (!me.data || !stats.data || !subject.data) return <LoadingState />;

  return <Home me={me.data} stats={stats.data} subject={subject.data} />;
}

type HomeProps = { me: Me; stats: Stats; subject: SubjectDetail };

function Home({ me, stats, subject }: HomeProps) {
  const { t } = useTranslation();
  const [switcherOpen, setSwitcherOpen] = useState(false);
  const practice = useStartPractice(() => setSwitcherOpen(true));
  const startPractice = () => practice.start(subject.slug);

  const name = firstName(me);
  const moment = streakMoment(stats.streak);
  const nextTopic = subject.topics.find(
    (topic) => topic.slug === subject.next_topic,
  );
  const change = stats.last_rating_change;

  return (
    <>
      {/* Phones: greeting and chips, then the switcher on its own row.
          From 1280 px: greeting and switcher share the row. */}
      <div className="grid grid-cols-[minmax(0,1fr)_auto] items-center gap-x-2 gap-y-4 lg:grid-cols-[minmax(0,1fr)_340px] lg:gap-x-4">
        <h1 className="text-[22px] leading-7 font-bold tracking-[-0.01em] text-balance lg:text-[30px] lg:leading-9">
          {name ? t("home.greeting", { name }) : t("home.greeting_no_name")}
        </h1>
        <UserChips className="lg:hidden" />
        <div className="col-span-2 pr-[3px] lg:col-span-1 lg:col-start-2 lg:row-start-1 lg:pr-0">
          <SubjectSwitcher
            current={subject}
            open={switcherOpen}
            onOpenChange={setSwitcherOpen}
          />
        </div>
      </div>

      <div className="flex flex-col gap-4 lg:grid lg:grid-cols-[minmax(0,1fr)_360px] lg:items-start lg:gap-8">
        <div className="flex flex-col gap-4 lg:col-start-2 lg:row-start-1 lg:gap-5 lg:pr-1.5">
          <div className="pr-1.5 lg:pr-0">
            <GoalCard
              goal={stats.goal}
              nextTopic={nextTopic ? localName(nextTopic) : null}
              onPractice={startPractice}
              pending={practice.pending}
            />
          </div>
          {moment === "extended" && (
            // Phones show the streak in the chips at the top.
            <StreakCard
              moment="extended"
              days={stats.streak.current}
              goalMet={stats.goal.met}
              className="hidden lg:flex"
            />
          )}
          {moment && moment !== "extended" && (
            // At the top on phones, under the goal from 1280 px.
            <StreakMomentCard
              moment={moment}
              streak={stats.streak}
              onPractice={startPractice}
              pending={practice.pending}
              className="max-lg:order-first"
            />
          )}
          {change && (
            <RatingCard
              label={t("home.rating_label", {
                subject: localName(change.subject).toLocaleLowerCase(),
              })}
              rating={change.after}
              delta={change.delta}
              className="hidden lg:flex"
            />
          )}
        </div>

        <section
          aria-labelledby="home-topics"
          className="flex flex-col gap-1.5 lg:col-start-1 lg:row-start-1 lg:gap-3 lg:rounded-card lg:border lg:border-border lg:bg-surface lg:p-5"
        >
          <h2
            id="home-topics"
            className="text-[18px] leading-6 font-bold text-fg"
          >
            {t("home.topics")}
          </h2>
          {subject.topics.length === 0 ? (
            <EmptyState
              title={t("home.no_topics_title")}
              body={t("home.no_topics_body")}
            >
              <Button variant="secondary" onClick={() => setSwitcherOpen(true)}>
                {t("home.switch_title")}
              </Button>
            </EmptyState>
          ) : (
            <TopicPath>
              {subject.topics.map((topic) => (
                <TopicNode
                  key={topic.slug}
                  name={localName(topic)}
                  state={topicNodeState(topic.mastery)}
                  percent={Math.round(topic.accuracy * 100)}
                  // Sessions are per subject in V1 (docs/DECISIONS.md).
                  onSelect={startPractice}
                  disabled={practice.pending}
                />
              ))}
            </TopicPath>
          )}
        </section>
      </div>
    </>
  );
}

/** The current subject is no longer published: send the student to pick. */
function SubjectGone() {
  const { t } = useTranslation();
  return (
    <EmptyState
      title={t("home.no_subject_title")}
      body={t("home.no_subject_body")}
    >
      <Link
        to="/subjects"
        className={cn(buttonVariants({ variant: "primary" }), "w-full")}
      >
        {t("home.all_subjects")}
      </Link>
    </EmptyState>
  );
}
