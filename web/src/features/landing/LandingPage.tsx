import { Info, Target, TrendingUp, type LucideIcon } from "lucide-react";
import { useEffect, useRef } from "react";
import { useTranslation } from "react-i18next";
import { Link, useNavigate } from "react-router";
import { useConfig, useMe } from "@/api/queries";
import { Mel } from "@/components/Mel";
import { Wordmark } from "@/components/Wordmark";
import { Badge } from "@/components/ui/badge";
import { buttonVariants } from "@/components/ui/button-variants";
import { locales } from "@/i18n";
import { track } from "@/lib/analytics";
import { cn } from "@/lib/utils";
import { LanguageSwitch } from "./LanguageSwitch";
import { SampleQuestion } from "./SampleQuestion";

// Phones: 16 px gutters. From 768 px the phone layout in a centred column
// of at most 640 px with 24 px gutters. From 1280 px the desktop mockup's
// 1200 px container with 40 px gutters.
const column =
  "mx-auto w-full max-w-[688px] px-4 md:px-6 lg:max-w-[1200px] lg:px-10";

// The spec's session length, until /config has answered. The static HTML
// is rendered without the API, so it always says this.
const DEFAULT_SESSION_LENGTH = 10;

/**
 * The public front page at /, rendered to static HTML at build time
 * (src/prerender.tsx). Nothing in the render may touch the browser:
 * window, document and storage belong in effects and handlers.
 */
export function LandingPage() {
  useLandingVisit();
  return (
    <div className="flex flex-col">
      <LandingHeader />
      <main className={cn(column, "flex flex-col")}>
        <div className="flex flex-col gap-7 pt-2 lg:grid lg:grid-cols-[minmax(0,1fr)_460px] lg:items-start lg:gap-16 lg:pt-10 lg:pr-1.5">
          <Hero />
          <TryIt />
        </div>
        <Subjects />
        <HowItWorks />
        <ClosingCall />
      </main>
      <LandingFooter />
    </div>
  );
}

/**
 * Record the visit once, and send a returning student, someone with a
 * session who has been through onboarding, to Home. Both happen in
 * effects, so the static HTML is the same for everyone.
 */
function useLandingVisit() {
  const me = useMe();
  const navigate = useNavigate();
  const returning = Boolean(me.data?.current_subject);

  const viewed = useRef(false);
  useEffect(() => {
    if (viewed.current) return;
    viewed.current = true;
    track("landing.viewed");
  }, []);

  useEffect(() => {
    if (returning) navigate("/home", { replace: true });
  }, [returning, navigate]);
}

function LandingHeader() {
  const { t } = useTranslation();
  return (
    <header
      className={cn(
        column,
        "flex min-h-16 items-center justify-between gap-2 pt-[calc(8px+env(safe-area-inset-top))] pb-2",
      )}
    >
      <Wordmark className="text-[18px] leading-[23px] lg:text-[22px] lg:leading-[29px]" />
      <div className="flex items-center gap-0.5">
        <LanguageSwitch />
        <Link
          to="/signin"
          className={buttonVariants({ variant: "ghost", size: "md" })}
        >
          {t("landing.sign_in")}
        </Link>
      </div>
    </header>
  );
}

function Hero() {
  const { t } = useTranslation();
  return (
    <div className="flex flex-col gap-3.5 lg:gap-5">
      <div className="flex items-end gap-3 lg:gap-3.5">
        <Mel pose="wave" scale={4} className="lg:h-[162px] lg:w-[156px]" />
        <div className="pb-[46px] lg:pb-20">
          <p className="w-max rounded-[14px_14px_14px_2px] border-[1.5px] border-border-strong bg-surface px-3.5 py-2 text-[15px] leading-5 font-semibold">
            {t("landing.greeting")}
          </p>
        </div>
      </div>
      <h1 className="text-[30px] leading-9 font-bold tracking-[-0.01em] text-balance lg:max-w-[560px] lg:text-[52px] lg:leading-[58px]">
        {t("landing.title")}
      </h1>
      <p className="text-[16px] leading-6 text-fg-muted lg:max-w-[480px] lg:text-[19px] lg:leading-7">
        {t("landing.lead")}
      </p>
      <div className="flex flex-col gap-3.5 lg:flex-row lg:items-center lg:gap-4">
        <div className="pr-1 lg:pr-0">
          <Link
            to="/start"
            className={cn(buttonVariants(), "w-full lg:w-auto")}
          >
            {t("common.lets_practice")}
          </Link>
        </div>
        <p className="font-mono text-[12px] leading-4 text-fg-muted">
          {t("landing.no_sign_up")}
        </p>
      </div>
    </div>
  );
}

/** The sample question, beside the hero from 1280 px and under it before. */
function TryIt() {
  const { t } = useTranslation();
  return (
    <section
      aria-labelledby="try-it-label"
      className="flex flex-col gap-2.5 pr-1.5 lg:pr-0"
    >
      <p
        id="try-it-label"
        className="font-mono text-[12px] leading-4 text-brand-text"
      >
        <span aria-hidden="true">{"// "}</span>
        {t("landing.try_label")}
      </p>
      <SampleQuestion />
    </section>
  );
}

// The three launch subjects (content/catalog.yaml), in catalog order. The
// list is part of the static page, so it does not wait for the API.
const subjects = ["programming", "data_structures", "databases"] as const;

function Subjects() {
  const { t } = useTranslation();
  return (
    <section
      aria-labelledby="subjects-title"
      className="flex flex-col gap-2.5 pt-9 lg:gap-3.5 lg:pt-16"
    >
      <h2
        id="subjects-title"
        className="text-[18px] leading-6 font-bold text-fg"
      >
        {t("landing.subjects_title")}
      </h2>
      <ul className="flex flex-col gap-2.5 lg:grid lg:grid-cols-3 lg:gap-3">
        {subjects.map((subject) => (
          <li
            key={subject}
            className="flex min-h-14 items-center gap-3 rounded-lg border border-border bg-surface px-3.5 py-2 lg:flex-col lg:items-start lg:gap-2.5 lg:p-4"
          >
            {/* leading-4 again: tailwind-merge drops the badge's line
                height when the font size changes. */}
            <Badge className="text-[12px] leading-4">
              {t(`landing.subjects.${subject}_short`)}
            </Badge>
            <span className="text-[16px] leading-[22px] font-semibold text-fg">
              {t(`landing.subjects.${subject}`)}
            </span>
          </li>
        ))}
      </ul>
    </section>
  );
}

type Point = { icon: LucideIcon; title: string; body: string };

function HowItWorks() {
  const { t } = useTranslation();
  const config = useConfig();
  const length = config.data?.session_length ?? DEFAULT_SESSION_LENGTH;
  const points: Point[] = [
    {
      icon: Target,
      title: t("landing.short_title"),
      body: t("landing.short_body", { length }),
    },
    {
      icon: TrendingUp,
      title: t("landing.adaptive_title"),
      body: t("landing.adaptive_body"),
    },
    {
      icon: Info,
      title: t("landing.reasons_title"),
      body: t("landing.reasons_body"),
    },
  ];
  return (
    <section
      aria-labelledby="how-title"
      className="flex flex-col gap-[18px] pt-9 pr-1 lg:pt-14 lg:pr-1.5"
    >
      <h2 id="how-title" className="text-[18px] leading-6 font-bold text-fg">
        {t("landing.how_title")}
      </h2>
      <div className="flex flex-col gap-[18px] lg:grid lg:grid-cols-3 lg:gap-8">
        {points.map(({ icon: Icon, title, body }) => (
          <div key={title} className="flex items-start gap-3.5">
            {/* 46 px: the mockup draws a 44 px tile with its border outside. */}
            <span className="flex size-[46px] shrink-0 items-center justify-center rounded-lg border-[1.5px] border-border-strong bg-surface text-brand-text shadow-step-md">
              <Icon aria-hidden="true" className="size-[22px]" />
            </span>
            <div className="flex min-w-0 flex-col gap-1">
              <h3 className="text-[17px] leading-[22px] font-bold text-fg">
                {title}
              </h3>
              <p className="text-[14px] leading-5 text-fg-muted">{body}</p>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

function ClosingCall() {
  const { t } = useTranslation();
  return (
    <section
      aria-labelledby="cta-title"
      className="pt-10 pr-1.5 pb-8 lg:pt-14 lg:pb-10"
    >
      <div className="flex flex-col items-start gap-3.5 rounded-xl bg-brand px-5 pt-6 pb-7 text-brand-fg shadow-step-xl">
        <h2 id="cta-title" className="text-[24px] leading-[30px] font-bold">
          {t("landing.cta_title")}
        </h2>
        <p className="text-[15px] leading-[22px] font-medium">
          {t("landing.cta_body")}
        </p>
        <Link to="/start" className={buttonVariants({ variant: "onCaramel" })}>
          {t("common.lets_practice")}
        </Link>
      </div>
    </section>
  );
}

function LandingFooter() {
  const { t } = useTranslation();
  return (
    <div className={column}>
      <footer className="flex items-center justify-between gap-3 border-t border-border pt-5 pb-[calc(28px+env(safe-area-inset-bottom))] font-mono text-[12px] leading-4 text-fg-muted">
        <span>{t("common.brand")}</span>
        <span>
          {locales.map((locale, index) => (
            <span key={locale}>
              {index > 0 && " · "}
              <span lang={locale}>{t(`common.languages.${locale}`)}</span>
            </span>
          ))}
        </span>
      </footer>
    </div>
  );
}
