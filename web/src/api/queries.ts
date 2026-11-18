// Every call to the API, as TanStack Query hooks. Server state lives in
// the query cache; nothing else stores it.
import {
  useMutation,
  useQuery,
  useQueryClient,
  type QueryClient,
} from "@tanstack/react-query";
import { browserTimezone } from "@/lib/timezone";
import { currentLocale } from "@/i18n";
import { ApiError, api, unwrap } from "./client";
import type {
  AnswerRequest,
  Me,
  ReportRequest,
  Session,
  SessionSummary,
  SettingsPatch,
} from "./types";

export const keys = {
  me: ["me"] as const,
  config: ["config"] as const,
  stats: ["stats"] as const,
  subjects: ["subjects"] as const,
  subject: (slug: string) => ["subjects", slug] as const,
  activity: (start?: string, end?: string) =>
    ["activity", start ?? null, end ?? null] as const,
  session: (id: string) => ["sessions", id] as const,
};

// ---- who is asking ----

/** The signed-in user or guest; null when this browser has no session. */
export async function fetchMe(): Promise<Me | null> {
  try {
    return await unwrap(api.GET("/api/v1/me"));
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) return null;
    throw error;
  }
}

let guestRequest: Promise<Me> | null = null;

/**
 * Start playing without an account. Callers that ask at the same moment
 * share one request, so a first visit never makes two guests.
 */
export function createGuest(): Promise<Me> {
  guestRequest ??= unwrap(
    api.POST("/api/v1/auth/guest", {
      body: { locale: currentLocale(), timezone: browserTimezone() },
    }),
  ).finally(() => {
    guestRequest = null;
  });
  return guestRequest;
}

export function useMe() {
  return useQuery({ queryKey: keys.me, queryFn: fetchMe });
}

/** After the user changed: drop everything that belonged to the old one. */
function resetUserData(queryClient: QueryClient, me: Me | null) {
  queryClient.removeQueries({
    predicate: (query) => query.queryKey[0] !== keys.me[0],
  });
  queryClient.setQueryData(keys.me, me);
}

export function useRequestMagicLink() {
  return useMutation({
    mutationFn: (email: string) =>
      unwrap(
        api.POST("/api/v1/auth/magic-link", {
          body: { email, locale: currentLocale() },
        }),
      ),
  });
}

export function useVerifyMagicLink() {
  const queryClient = useQueryClient();
  return useMutation({
    // A new account starts in the language and timezone of this device.
    mutationFn: (token: string) =>
      unwrap(
        api.POST("/api/v1/auth/magic-link/verify", {
          body: { token, locale: currentLocale(), timezone: browserTimezone() },
        }),
      ),
    onSuccess: (me) => resetUserData(queryClient, me),
  });
}

export function useLogout() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => unwrap(api.POST("/api/v1/auth/logout")),
    onSuccess: () => resetUserData(queryClient, null),
  });
}

export function useDeleteAccount() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => unwrap(api.DELETE("/api/v1/me")),
    onSuccess: () => resetUserData(queryClient, null),
  });
}

// ---- account ----

export function usePatchSettings() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (patch: SettingsPatch) =>
      unwrap(api.PATCH("/api/v1/me/settings", { body: patch })),
    onSuccess: (me, patch) => {
      queryClient.setQueryData(keys.me, me);
      // The goal, the current subject and the timezone change what the
      // stats and the catalog say.
      if (
        patch.daily_goal !== undefined ||
        patch.current_subject !== undefined ||
        patch.timezone !== undefined
      ) {
        void queryClient.invalidateQueries({ queryKey: keys.stats });
        void queryClient.invalidateQueries({ queryKey: keys.subjects });
      }
    },
  });
}

// ---- config, catalog, stats ----

export function useConfig() {
  return useQuery({
    queryKey: keys.config,
    queryFn: () => unwrap(api.GET("/api/v1/config")),
    staleTime: 5 * 60 * 1000,
  });
}

export function useSubjects() {
  return useQuery({
    queryKey: keys.subjects,
    queryFn: () => unwrap(api.GET("/api/v1/subjects")),
  });
}

export function useSubject(slug: string | null | undefined) {
  return useQuery({
    queryKey: keys.subject(slug ?? ""),
    queryFn: () =>
      unwrap(
        api.GET("/api/v1/subjects/{slug}", {
          params: { path: { slug: slug ?? "" } },
        }),
      ),
    enabled: Boolean(slug),
  });
}

export function useStats() {
  return useQuery({
    queryKey: keys.stats,
    queryFn: () => unwrap(api.GET("/api/v1/me/stats")),
  });
}

/** Without arguments: the current month of the user's calendar. */
export function useActivity(start?: string, end?: string) {
  return useQuery({
    queryKey: keys.activity(start, end),
    queryFn: () =>
      unwrap(
        api.GET("/api/v1/me/activity", { params: { query: { start, end } } }),
      ),
  });
}

// ---- practice ----

/** Starts a session, or gives back the one left unfinished in the subject. */
export function useCreateSession() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (subject: string) =>
      unwrap(
        api.POST("/api/v1/sessions", { body: { subject, mode: "practice" } }),
      ),
    onSuccess: (session) => {
      queryClient.setQueryData(keys.session(session.id), session);
    },
  });
}

export function useSession(id: string) {
  return useQuery({
    queryKey: keys.session(id),
    queryFn: () =>
      unwrap(
        api.GET("/api/v1/sessions/{session_id}", {
          params: { path: { session_id: id } },
        }),
      ),
    // The session screen keeps its own place; a refetch in the middle of
    // a question would only move things under the student.
    staleTime: Infinity,
  });
}

export function useAnswer(sessionId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (answer: AnswerRequest) =>
      unwrap(
        api.POST("/api/v1/sessions/{session_id}/answers", {
          params: { path: { session_id: sessionId } },
          body: answer,
        }),
      ),
    // Keep the cached session in step, so leaving and coming back resumes
    // at the next question without a request.
    onSuccess: (result, answer) => {
      queryClient.setQueryData<Session>(keys.session(sessionId), (session) =>
        session ? withAnswer(session, answer, result) : session,
      );
    },
  });
}

function withAnswer(
  session: Session,
  answer: AnswerRequest,
  result: { is_correct: boolean; xp_earned: number },
): Session {
  const question = session.questions.find((q) => q.id === answer.question_id);
  if (!question || question.answer) return session;
  return {
    ...session,
    answered_count: session.answered_count + 1,
    correct_count: session.correct_count + (result.is_correct ? 1 : 0),
    xp_earned: session.xp_earned + result.xp_earned,
    questions: session.questions.map((q) =>
      q.id === answer.question_id
        ? {
            ...q,
            answer: {
              selected_key: answer.key,
              is_correct: result.is_correct,
              xp_earned: result.xp_earned,
            },
          }
        : q,
    ),
  };
}

export function useFinishSession(sessionId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () =>
      unwrap(
        api.POST("/api/v1/sessions/{session_id}/finish", {
          params: { path: { session_id: sessionId } },
        }),
      ),
    onSuccess: (summary: SessionSummary) => {
      queryClient.setQueryData<Session>(keys.session(sessionId), (session) =>
        session
          ? {
              ...session,
              finished_at: session.finished_at ?? new Date().toISOString(),
              xp_earned: summary.xp_earned,
              summary,
            }
          : session,
      );
      // A finished session moves the streak, the goal, ratings and mastery.
      void queryClient.invalidateQueries({ queryKey: keys.stats });
      void queryClient.invalidateQueries({ queryKey: keys.subjects });
      void queryClient.invalidateQueries({ queryKey: ["activity"] });
    },
  });
}

export function useReportQuestion(questionId: string) {
  return useMutation({
    mutationFn: (report: ReportRequest) =>
      unwrap(
        api.POST("/api/v1/questions/{question_id}/report", {
          params: { path: { question_id: questionId } },
          body: report,
        }),
      ),
  });
}
