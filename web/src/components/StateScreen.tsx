// The system states of design/screens/v1-state-*: loading, empty, offline,
// error, 404 and maintenance. Every screen uses these.
import type { ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { Link } from "react-router";
import { errorKind } from "@/api/client";
import { cn } from "@/lib/utils";
import { Mel, type MelPose } from "./Mel";
import { Wordmark } from "./Wordmark";
import { Button } from "./ui/button";
import { buttonVariants } from "./ui/button-variants";

type StateMessageProps = {
  pose: MelPose;
  /** A line of mono type above the title, as on the 404 screen. */
  code?: string;
  title: string;
  body: string;
  /** "status" for a state the student did not ask for (offline). */
  role?: "main" | "status";
  children?: ReactNode;
};

/** Mel, a title, a line of text and up to two actions, centred. */
export function StateMessage({
  pose,
  code,
  title,
  body,
  role = "main",
  children,
}: StateMessageProps) {
  return (
    <div
      role={role}
      className="flex grow flex-col items-center justify-center gap-3.5 px-5 py-6 text-center"
    >
      <Mel pose={pose} scale={6} />
      {code && (
        <div className="font-mono text-[13px] leading-[18px] font-bold text-brand-text">
          {code}
        </div>
      )}
      <h1 className="text-[24px] leading-[30px] font-bold tracking-[-0.01em] text-balance lg:text-[30px] lg:leading-9">
        {title}
      </h1>
      <p className="max-w-[320px] text-[15px] leading-[22px] text-fg-muted">
        {body}
      </p>
      {children && (
        <div className="mt-1.5 flex w-full max-w-[320px] flex-col gap-1.5 pr-1">
          {children}
        </div>
      )}
    </div>
  );
}

/** Covers the whole window, navigation included, as the mockups do. */
function FullScreen({ children }: { children: ReactNode }) {
  return (
    <div className="fixed inset-0 z-40 flex flex-col overflow-y-auto bg-bg pt-[env(safe-area-inset-top)] pb-[env(safe-area-inset-bottom)]">
      <header className="flex items-center px-5 pt-4">
        <Wordmark className="text-[18px] leading-[23px]" />
      </header>
      {children}
    </div>
  );
}

function HomeLink({ variant }: { variant: "primary" | "ghost" }) {
  const { t } = useTranslation();
  return (
    <Link
      to="/home"
      className={cn(
        buttonVariants({ variant, size: variant === "primary" ? "lg" : "md" }),
        "w-full",
      )}
    >
      {t("common.back_to_home")}
    </Link>
  );
}

/** Skeleton blocks and a thinking Mel, inside the screen's own frame. */
export function LoadingState() {
  const { t } = useTranslation();
  const block = "rounded-lg border border-border bg-surface";
  return (
    <div className="flex flex-col gap-4 lg:gap-6">
      <div
        aria-hidden="true"
        className={cn(block, "h-[30px] w-[calc(60%+2px)]")}
      />
      <div aria-hidden="true" className={cn(block, "h-[54px]")} />
      <div aria-hidden="true" className={cn(block, "h-[152px]")} />
      <div
        role="status"
        className="flex items-center justify-center gap-2.5 py-2"
      >
        <Mel pose="think" head scale={3} />
        <span className="text-[15px] leading-5 font-semibold text-fg-muted">
          {t("common.loading")}
        </span>
      </div>
      <div aria-hidden="true" className={cn(block, "h-[66px]")} />
      <div aria-hidden="true" className={cn(block, "h-[66px]")} />
      <div aria-hidden="true" className={cn(block, "h-[66px]")} />
    </div>
  );
}

/** For a route without the app's navigation: the skeleton with gutters. */
export function LoadingScreen() {
  return (
    <div className="mx-auto w-full max-w-[688px] px-4 pt-[calc(16px+env(safe-area-inset-top))] pb-5 md:px-6 lg:pt-8">
      <LoadingState />
    </div>
  );
}

type EmptyStateProps = {
  title?: string;
  body?: string;
  /** The one thing to do next, usually a primary button. */
  children?: ReactNode;
};

/** Nothing to show yet. Sits inside the screen, under its title. */
export function EmptyState({ title, body, children }: EmptyStateProps) {
  const { t } = useTranslation();
  return (
    <StateMessage
      pose="wave"
      title={title ?? t("states.empty_title")}
      body={body ?? t("states.empty_body")}
    >
      {children}
    </StateMessage>
  );
}

export function OfflineScreen({ onRetry }: { onRetry?: () => void }) {
  const { t } = useTranslation();
  return (
    <FullScreen>
      <StateMessage
        pose="sleep"
        role="status"
        title={t("states.offline_title")}
        body={t("states.offline_body")}
      >
        {onRetry && (
          <Button className="w-full" onClick={onRetry}>
            {t("common.try_again")}
          </Button>
        )}
      </StateMessage>
    </FullScreen>
  );
}

export function ErrorScreen({ onRetry }: { onRetry?: () => void }) {
  const { t } = useTranslation();
  return (
    <FullScreen>
      <StateMessage
        pose="encourage"
        title={t("states.error_title")}
        body={t("states.error_body")}
      >
        {onRetry && (
          <Button className="w-full" onClick={onRetry}>
            {t("common.try_again")}
          </Button>
        )}
        <HomeLink variant={onRetry ? "ghost" : "primary"} />
      </StateMessage>
    </FullScreen>
  );
}

export function NotFoundScreen() {
  const { t } = useTranslation();
  return (
    <FullScreen>
      <StateMessage
        pose="mischief"
        code={t("states.not_found_code")}
        title={t("states.not_found_title")}
        body={t("states.not_found_body")}
      >
        <HomeLink variant="primary" />
      </StateMessage>
    </FullScreen>
  );
}

export function MaintenanceScreen() {
  const { t } = useTranslation();
  return (
    <FullScreen>
      <StateMessage
        pose="study"
        code={t("states.maintenance_code")}
        title={t("states.maintenance_title")}
        body={t("states.maintenance_body")}
      />
    </FullScreen>
  );
}

type FailureScreenProps = {
  /** What a query or mutation threw. */
  error: unknown;
  onRetry?: () => void;
};

/** The right full-screen state for a failed request. */
export function FailureScreen({ error, onRetry }: FailureScreenProps) {
  switch (errorKind(error)) {
    case "offline":
      return <OfflineScreen onRetry={onRetry} />;
    case "maintenance":
      return <MaintenanceScreen />;
    case "not_found":
      return <NotFoundScreen />;
    default:
      return <ErrorScreen onRetry={onRetry} />;
  }
}
