import { useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { Navigate, Outlet, useLocation } from "react-router";
import { createGuest, keys, useMe } from "@/api/queries";
import type { Me } from "@/api/types";
import { FailureScreen, LoadingScreen } from "@/components/StateScreen";
import { useSyncPreferences } from "@/lib/preferences";

type UserState = {
  user: Me | null;
  /** There was a user and now there is none: signed out, or deleted. */
  signedOut: boolean;
  error: unknown;
  retry: () => void;
};

/**
 * The user of this browser. A first visit has none, so a guest is created
 * without asking: the student plays first and signs in later, if ever.
 * Someone who signs out is not given a new guest on the spot.
 */
function useUserOrGuest(): UserState {
  const queryClient = useQueryClient();
  const me = useMe();
  const [guestError, setGuestError] = useState<unknown>(null);
  const [hadUser, setHadUser] = useState(false);
  // Remembered while rendering, the way React asks for state that follows
  // a value: no effect, no extra paint.
  if (me.data && !hadUser) setHadUser(true);
  const signedOut = me.data === null && hadUser;
  const needsGuest = me.data === null && !hadUser && guestError === null;

  useEffect(() => {
    if (!needsGuest) return;
    let ignore = false;
    createGuest()
      .then((guest) => queryClient.setQueryData(keys.me, guest))
      .catch((error: unknown) => {
        if (!ignore) setGuestError(error);
      });
    return () => {
      ignore = true;
    };
  }, [needsGuest, queryClient]);

  return {
    user: me.data ?? null,
    signedOut,
    error: me.error ?? guestError,
    retry: () => {
      setGuestError(null);
      void me.refetch();
    },
  };
}

/**
 * Wraps every route that needs a user. Someone who has not chosen a
 * subject yet has not been through onboarding, and is sent there.
 */
export function RequireUser() {
  const { user, signedOut, error, retry } = useUserOrGuest();
  const location = useLocation();
  useSyncPreferences(user);

  if (error) return <FailureScreen error={error} onRetry={retry} />;
  if (signedOut) return <Navigate to="/" replace />;
  if (!user) return <LoadingScreen />;
  if (!user.current_subject && location.pathname !== "/start") {
    return <Navigate to="/start" replace />;
  }
  return <Outlet />;
}
