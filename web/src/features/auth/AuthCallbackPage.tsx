import { useEffect, useRef } from "react";
import { useTranslation } from "react-i18next";
import { Link, Navigate, useSearchParams } from "react-router";
import { ApiError } from "@/api/client";
import { useVerifyMagicLink } from "@/api/queries";
import { Wordmark } from "@/components/Wordmark";
import {
  FailureScreen,
  LoadingScreen,
  StateMessage,
} from "@/components/StateScreen";
import { buttonVariants } from "@/components/ui/button-variants";
import { cn } from "@/lib/utils";

/**
 * /auth/callback, where the emailed link lands (?token=...) and where the
 * API sends the browser back from Google: with ?error=... when it failed,
 * with nothing when the sign-in worked and the cookie is already set.
 */
export default function AuthCallbackPage() {
  const [params] = useSearchParams();
  const token = params.get("token");
  const error = params.get("error");

  if (token) return <VerifyLink token={token} />;
  if (error) return <GoogleFailed error={error} />;
  return <Navigate to="/home" replace />;
}

function VerifyLink({ token }: { token: string }) {
  const verify = useVerifyMagicLink();
  const { mutate } = verify;
  // A link works once. React runs effects twice in development, and a
  // second request would spend the token and answer invalid_magic_link.
  const sentFor = useRef<string | null>(null);

  useEffect(() => {
    if (sentFor.current === token) return;
    sentFor.current = token;
    mutate(token);
  }, [token, mutate]);

  if (verify.isSuccess) return <Navigate to="/home" replace />;
  if (verify.error instanceof ApiError && verify.error.status === 400) {
    return <LinkInvalid />;
  }
  if (verify.error) {
    return <FailureScreen error={verify.error} onRetry={() => mutate(token)} />;
  }
  return <LoadingScreen />;
}

/** The link was used already or is older than 15 minutes. */
function LinkInvalid() {
  const { t } = useTranslation();
  return (
    <CallbackMessage
      title={t("signin.link_invalid_title")}
      body={t("signin.link_invalid_body")}
      action={t("signin.new_link")}
    />
  );
}

function GoogleFailed({ error }: { error: string }) {
  const { t } = useTranslation();
  return (
    <CallbackMessage
      title={t("signin.google_failed_title")}
      body={
        error === "google_email_not_verified"
          ? t("signin.google_unverified_body")
          : t("signin.google_failed_body")
      }
      action={t("signin.back_to_signin")}
    />
  );
}

/** The frame of the system states, with the way back to /signin. */
function CallbackMessage({
  title,
  body,
  action,
}: {
  title: string;
  body: string;
  action: string;
}) {
  return (
    <div className="flex min-h-dvh flex-col pt-[env(safe-area-inset-top)] pb-[env(safe-area-inset-bottom)]">
      <header className="flex items-center px-5 pt-4">
        <Wordmark className="text-[18px] leading-[23px]" />
      </header>
      <StateMessage pose="encourage" title={title} body={body}>
        <Link
          to="/signin"
          replace
          className={cn(buttonVariants({ variant: "primary" }), "w-full")}
        >
          {action}
        </Link>
      </StateMessage>
    </div>
  );
}
