import { TrendingDown, X } from "lucide-react";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Navigate, useNavigate, useParams } from "react-router";
import { useMe, useSession } from "@/api/queries";
import type { Me, Session, SessionSummary } from "@/api/types";
import { Mel } from "@/components/Mel";
import {
  ErrorScreen,
  FailureScreen,
  LoadingScreen,
} from "@/components/StateScreen";
import { Button } from "@/components/ui/button";
import { IconButton } from "@/components/ui/icon-button";
import { useStartPractice } from "@/lib/useStartPractice";
import { localName } from "@/i18n";
import { LevelBar } from "./LevelBar";
import { LevelUpBurst } from "./LevelUpBurst";
import { useMelHop } from "./motion";
import { isLoss, leveledUp, shouldOfferSave } from "./rules";
import { SaveProgressPrompt } from "./SaveProgressPrompt";
import { StatCards } from "./StatCards";

/**
 * /session/:id/summary. The summary is in the cached session when the
 * session screen has just finished it, and comes with GET /sessions/{id}
 * on a reload. A session that is not finished has no summary yet: back to
 * its questions.
 */
export default function SummaryPage() {
  const { id = "" } = useParams();
  const query = useSession(id);
  const me = useMe();

  if (query.isPending || me.isPending) return <LoadingScreen />;
  if (query.isError) {
    return (
      <FailureScreen error={query.error} onRetry={() => void query.refetch()} />
    );
  }
  if (me.isError) {
    return <FailureScreen error={me.error} onRetry={() => void me.refetch()} />;
  }
  const session = query.data;
  if (!session.finished_at) {
    return <Navigate to={`/session/${session.id}`} replace />;
  }
  // Finished but without a summary: the API always sends one, so this is
  // a stale cache. The session screen would send the student straight
  // back here, so ask again instead.
  if (!session.summary || !me.data) {
    return <ErrorScreen onRetry={() => void query.refetch()} />;
  }
  return <Summary session={session} summary={session.summary} me={me.data} />;
}

type SummaryProps = { session: Session; summary: SessionSummary; me: Me };

function Summary({ session, summary, me }: SummaryProps) {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const practice = useStartPractice(() => navigate("/subjects"));
  const [offerSave, setOfferSave] = useState(() =>
    shouldOfferSave(me, summary),
  );
  const loss = isLoss(summary);
  const goHome = () => navigate("/home");

  return (
    <main className="mx-auto flex min-h-dvh w-full max-w-[688px] flex-col gap-[18px] px-4 pt-[calc(8px+env(safe-area-inset-top))] pb-[calc(24px+env(safe-area-inset-bottom))] md:px-6 lg:max-w-[640px] lg:gap-[22px] lg:px-0 lg:pt-4 lg:pb-10">
      <div className="flex justify-end">
        <IconButton
          aria-label={t("common.close")}
          onClick={goHome}
          className="[&_svg]:size-[22px]"
        >
          <X />
        </IconButton>
      </div>

      <Hero summary={summary} />
      <StatCards summary={summary} />

      {loss && (
        <div className="flex items-center gap-2 rounded-lg border border-border bg-surface px-3 py-2.5 text-[13px] leading-[18px] text-fg-muted">
          <TrendingDown aria-hidden="true" className="size-4 shrink-0" />
          <span>{t("summary.rating_down")}</span>
        </div>
      )}

      <LevelBar summary={summary} />

      {summary.topics_to_review.length > 0 && (
        <section
          aria-labelledby="summary-review"
          className="flex flex-col gap-2"
        >
          <h2
            id="summary-review"
            className="text-[18px] leading-6 font-bold text-fg"
          >
            {t("summary.topics_to_review")}
          </h2>
          <ul className="flex flex-col overflow-hidden rounded-lg border border-border bg-surface">
            {summary.topics_to_review.map((topic) => (
              <li
                key={topic.slug}
                className="flex min-h-12 items-center justify-between gap-2 border-border px-3.5 not-first:min-h-[49px] not-first:border-t"
              >
                <span className="text-[15px] leading-5 font-medium text-fg">
                  {localName(topic)}
                </span>
                <span className="font-mono text-[12px] leading-4 text-fg-muted">
                  {t("summary.misses", { count: topic.wrong_count })}
                </span>
              </li>
            ))}
          </ul>
        </section>
      )}

      <div className="mt-auto flex flex-col gap-1 pr-1 lg:mt-0">
        <Button
          className="w-full"
          loading={practice.pending}
          onClick={() => practice.start(session.subject.slug)}
        >
          {t("summary.one_more")}
        </Button>
        <Button variant="ghost" size="md" className="w-full" onClick={goHome}>
          {t("common.back_to_home")}
        </Button>
      </div>

      <SaveProgressPrompt
        open={offerSave}
        onSave={() => navigate("/signin")}
        onDismiss={() => setOfferSave(false)}
      />
    </main>
  );
}

/** Mel, the title, the score and one line: words follow gain or loss. */
function Hero({ summary }: { summary: SessionSummary }) {
  const { t } = useTranslation();
  const loss = isLoss(summary);
  const up = leveledUp(summary);
  const mel = useMelHop<HTMLDivElement>(up);

  return (
    <div className="relative flex flex-col items-center gap-2 text-center">
      {up && <LevelUpBurst />}
      <div ref={mel}>
        <Mel
          pose={loss ? "encourage" : "celebrate"}
          scale={5}
          className="lg:hidden"
        />
        <Mel
          pose={loss ? "encourage" : "celebrate"}
          scale={6}
          className="max-lg:hidden"
        />
      </div>
      <h1 className="text-[24px] leading-[30px] font-bold tracking-[-0.01em] text-balance">
        {loss ? t("summary.title_loss") : t("summary.title_gain")}
      </h1>
      <div className="flex items-baseline gap-2">
        <span className="font-mono text-[44px] leading-[48px] font-extrabold text-fg">
          {summary.correct_count}
        </span>
        <span className="text-[18px] leading-6 font-semibold text-fg-muted">
          {t("summary.correct_of", { total: summary.total })}
        </span>
      </div>
      <p className="max-w-[320px] text-[15px] leading-[22px] text-fg-muted">
        {loss ? t("summary.line_loss") : t("summary.line_gain")}
      </p>
    </div>
  );
}
