// Build-time entry: renders the landing page to HTML, in Portuguese. It is
// built for Node by `vite build --ssr` and called by the landingPrerender
// plugin of vite.config.ts. The browser never loads this file.
import { renderToString } from "react-dom/server";
import { StaticRouter } from "react-router";
import { AppProviders } from "@/app/providers";
import { LandingPage } from "@/features/landing/LandingPage";
import { defaultLocale, initI18n } from "@/i18n";

export type Prerendered = {
  /** The landing page's markup, to go inside #root. */
  html: string;
  title: string;
  description: string;
  lang: string;
};

export function render(): Prerendered {
  const i18n = initI18n(defaultLocale);
  const html = renderToString(
    <AppProviders>
      <StaticRouter location="/">
        <LandingPage />
      </StaticRouter>
    </AppProviders>,
  );
  return {
    html,
    title: i18n.t("landing.meta_title"),
    description: i18n.t("landing.meta_description"),
    lang: defaultLocale,
  };
}
