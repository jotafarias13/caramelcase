import { useEffect, useState } from "react";
import { Navigate, useParams } from "react-router";
import { useFinishSession, useMe, useSession } from "@/api/queries";
import { FailureScreen, LoadingScreen } from "@/components/StateScreen";
import { QuestionScreen } from "./QuestionScreen";
import { firstOpenQuestion, nextOpenQuestion } from "./rules";

/**
 * /session/:id. Loads the session and shows its first question without an
 * answer, which is how an interrupted session resumes where it stopped.
 * A finished session goes to its summary.
 */
export default function SessionPage() {
  const { id = "" } = useParams();
  const query = useSession(id);
  const me = useMe();
  const finish = useFinishSession(id);
  // The question on screen, once the student answered it: the cached
  // session then counts it as answered, but its feedback stays until
  // "Continuar".
  const [activeId, setActiveId] = useState<string | null>(null);
  const [moved, setMoved] = useState(false);

  const session = query.data;
  const firstOpen = session ? firstOpenQuestion(session) : null;
  // Every question answered on an earlier visit, but never finished: the
  // student left on the last feedback. Finish it now.
  const finishNow =
    session !== undefined &&
    !session.finished_at &&
    activeId === null &&
    firstOpen === null;
  const { mutate: finishSession, isIdle: finishIdle } = finish;
  useEffect(() => {
    if (finishNow && finishIdle) finishSession();
  }, [finishNow, finishIdle, finishSession]);

  if (query.isPending) return <LoadingScreen />;
  if (query.isError) {
    return (
      <FailureScreen error={query.error} onRetry={() => void query.refetch()} />
    );
  }
  if (finish.isError) {
    return (
      <FailureScreen error={finish.error} onRetry={() => finishSession()} />
    );
  }
  // Finishing writes finished_at into the cached session, which lands here.
  if (query.data.finished_at) {
    return <Navigate to={`/session/${id}/summary`} replace />;
  }

  const current = query.data;
  const question =
    current.questions.find((item) => item.id === activeId) ?? firstOpen;
  if (!question) return <LoadingScreen />;

  function goOn(questionId: string) {
    const next = nextOpenQuestion(current, questionId);
    if (next) {
      setActiveId(next.id);
      setMoved(true);
    } else {
      finishSession();
    }
  }

  return (
    <QuestionScreen
      key={question.id}
      session={current}
      question={question}
      showReasons={me.data?.settings.show_option_reasons ?? true}
      onCommit={() => setActiveId(question.id)}
      onContinue={() => goOn(question.id)}
      finishing={finish.isPending}
      focusOnShow={moved}
    />
  );
}
