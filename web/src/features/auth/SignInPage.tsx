import { useState, type FormEvent } from "react";
import { useTranslation } from "react-i18next";
import { Link } from "react-router";
import { errorKind } from "@/api/client";
import { useConfig, useRequestMagicLink } from "@/api/queries";
import { Mel } from "@/components/Mel";
import { Button } from "@/components/ui/button";
import { buttonVariants } from "@/components/ui/button-variants";
import { Input } from "@/components/ui/input";
import { toast } from "@/components/ui/toast-store";
import { cn } from "@/lib/utils";
import { GOOGLE_START_URL, looksLikeEmail } from "./auth";
import { AuthFrame, AuthIntro } from "./AuthFrame";

/**
 * /signin: Google, an email link, or carry on as a guest. Open to anyone,
 * with or without a user; nothing here needs one.
 */
export default function SignInPage() {
  const [email, setEmail] = useState("");
  const [sentTo, setSentTo] = useState<string | null>(null);
  const requestLink = useRequestMagicLink();
  const { t } = useTranslation();

  /** Resolves true once the API took the address (202 for any address). */
  async function send(address: string): Promise<boolean> {
    try {
      await requestLink.mutateAsync(address);
      return true;
    } catch (error) {
      toast({
        kind: errorKind(error) === "offline" ? "offline" : "error",
        message: t("signin.send_failed"),
      });
      return false;
    }
  }

  if (sentTo) {
    return (
      <LinkSent
        email={sentTo}
        resending={requestLink.isPending}
        onResend={async () => {
          if (await send(sentTo)) {
            toast({ kind: "success", message: t("signin.resent") });
          }
        }}
        onOtherEmail={() => setSentTo(null)}
      />
    );
  }
  return (
    <SignInForm
      email={email}
      onEmailChange={setEmail}
      sending={requestLink.isPending}
      onSend={async (address) => {
        if (await send(address)) setSentTo(address);
      }}
    />
  );
}

type SignInFormProps = {
  email: string;
  onEmailChange: (email: string) => void;
  sending: boolean;
  onSend: (email: string) => void;
};

function SignInForm({
  email,
  onEmailChange,
  sending,
  onSend,
}: SignInFormProps) {
  const { t } = useTranslation();
  const config = useConfig();
  const [invalid, setInvalid] = useState(false);

  function submit(event: FormEvent) {
    event.preventDefault();
    const address = email.trim();
    if (!looksLikeEmail(address)) {
      setInvalid(true);
      return;
    }
    onSend(address);
  }

  return (
    <AuthFrame>
      <AuthIntro
        mel={<Mel pose="wave" scale={4} />}
        title={t("signin.title")}
        body={t("signin.body")}
      />
      {/* Shown only once /config says this server has Google sign-in. */}
      {config.data?.google_sign_in && <GoogleButton />}
      <form noValidate onSubmit={submit} className="flex flex-col gap-4">
        <Input
          type="email"
          inputMode="email"
          autoComplete="email"
          label={t("signin.email")}
          placeholder={t("signin.email_placeholder")}
          helper={t("signin.email_helper")}
          error={invalid ? t("signin.email_invalid") : undefined}
          value={email}
          onChange={(event) => {
            onEmailChange(event.target.value);
            setInvalid(false);
          }}
        />
        <div className="pr-1">
          <Button type="submit" className="w-full" loading={sending}>
            {t("signin.send")}
          </Button>
        </div>
      </form>
      <Link
        to="/home"
        className={cn(
          buttonVariants({ variant: "ghost", size: "md" }),
          "w-full",
        )}
      >
        {t("signin.without_account")}
      </Link>
    </AuthFrame>
  );
}

/** "Continuar com Google" and the "ou" rule under it. */
function GoogleButton() {
  const { t } = useTranslation();
  return (
    <>
      <div className="pr-[3px]">
        <a
          href={GOOGLE_START_URL}
          className={cn(
            buttonVariants({ variant: "secondary" }),
            "w-full gap-2.5 px-[18px]",
          )}
        >
          <span
            aria-hidden="true"
            className="flex size-[25px] items-center justify-center rounded-sm border-[1.5px] border-border-strong font-mono text-[12px] leading-[14px] font-extrabold"
          >
            {t("signin.google_mark")}
          </span>
          {t("signin.google")}
        </a>
      </div>
      <div className="flex items-center gap-3 font-mono text-[12px] leading-4 text-fg-muted">
        <div className="h-px grow bg-border" />
        <span>{t("signin.or")}</span>
        <div className="h-px grow bg-border" />
      </div>
    </>
  );
}

type LinkSentProps = {
  email: string;
  resending: boolean;
  onResend: () => void;
  onOtherEmail: () => void;
};

/** v1-signin-sent: the address the link went to, and what to do next. */
function LinkSent({ email, resending, onResend, onOtherEmail }: LinkSentProps) {
  const { t } = useTranslation();
  return (
    <AuthFrame>
      <div role="status" className="contents">
        <AuthIntro
          mel={<Mel pose="celebrate" scale={4} />}
          title={t("signin.sent_title")}
          body={t("signin.sent_body", { email })}
        />
      </div>
      <div className="pr-[3px]">
        <Button
          variant="secondary"
          className="w-full"
          loading={resending}
          onClick={onResend}
        >
          {t("signin.resend")}
        </Button>
      </div>
      <Button
        variant="ghost"
        size="md"
        className="w-full"
        onClick={onOtherEmail}
      >
        {t("signin.other_email")}
      </Button>
    </AuthFrame>
  );
}
