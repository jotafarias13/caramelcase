import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router";
import { ApiError, errorKind } from "@/api/client";
import { useCreateSession } from "@/api/queries";
import { dismissToast, toast } from "@/components/ui/toast-store";

/**
 * Starts practice in a subject and opens the session. The API gives back
 * the session left unfinished in that subject, if there is one, so this
 * also resumes. When the subject has nothing to serve (409 no_questions)
 * a toast says so and offers `onSwitchSubject`, so the button that was
 * tapped is never a dead end.
 */
export function useStartPractice(onSwitchSubject: () => void) {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const createSession = useCreateSession();

  function start(subject: string) {
    if (createSession.isPending) return;
    createSession.mutate(subject, {
      onSuccess: (session) => navigate(`/session/${session.id}`),
      onError: (error) => {
        if (error instanceof ApiError && error.code === "no_questions") {
          const id = toast({
            kind: "info",
            message: t("home.no_questions"),
            action: {
              label: t("home.switch_action"),
              onClick: () => {
                dismissToast(id);
                onSwitchSubject();
              },
            },
          });
        } else if (errorKind(error) === "offline") {
          toast({ kind: "offline", message: t("states.offline_title") });
        } else {
          toast({ kind: "error", message: t("home.start_failed") });
        }
      },
    });
  }

  return { start, pending: createSession.isPending };
}
