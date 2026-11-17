// Interface copy. Every string the app shows comes from pt-BR.json or
// en.json, whose texts are taken from design/copy.md; the lint rule
// local/no-hardcoded-copy fails on text written into a component.
import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import type { Locale } from "@/api/types";
import en from "./en.json";
import ptBR from "./pt-BR.json";

export const locales: Locale[] = ["pt-BR", "en"];
export const defaultLocale: Locale = "pt-BR";

const STORAGE_KEY = "caramelcase.locale";

function isLocale(value: unknown): value is Locale {
  return locales.includes(value as Locale);
}

/**
 * The language to start in: the one chosen before on this device, else
 * English for a browser set to English, else Portuguese.
 */
export function detectLocale(): Locale {
  if (typeof window === "undefined") return defaultLocale;
  const stored = localStorage.getItem(STORAGE_KEY);
  if (isLocale(stored)) return stored;
  const preferred = navigator.languages?.[0] ?? navigator.language ?? "";
  return preferred.toLowerCase().startsWith("en") ? "en" : defaultLocale;
}

export function currentLocale(): Locale {
  return isLocale(i18n.language) ? i18n.language : defaultLocale;
}

/** Switch the interface language and remember it on this device. */
export function setLocale(locale: Locale): void {
  localStorage.setItem(STORAGE_KEY, locale);
  document.documentElement.lang = locale;
  void i18n.changeLanguage(locale);
}

/**
 * Called before the first render; the resources are bundled, so it is
 * ready at once. Called again with a locale, it switches to it.
 */
export function initI18n(locale?: Locale): typeof i18n {
  if (!i18n.isInitialized) {
    void i18n.use(initReactI18next).init({
      resources: {
        "pt-BR": { translation: ptBR },
        en: { translation: en },
      },
      lng: locale ?? detectLocale(),
      fallbackLng: defaultLocale,
      // React escapes what it renders.
      interpolation: { escapeValue: false },
      initAsync: false,
    });
  } else if (locale && i18n.language !== locale) {
    void i18n.changeLanguage(locale);
  }
  if (typeof document !== "undefined") {
    document.documentElement.lang = currentLocale();
  }
  return i18n;
}

/** The name of a subject or topic in the interface language. */
export function localName(
  item: { name_pt: string; name_en: string },
  locale: Locale = currentLocale(),
): string {
  return locale === "en" ? item.name_en : item.name_pt;
}

/** A subject's short badge ("ed/", "ds/") in the interface language. */
export function localShort(
  item: { short_pt: string; short_en: string },
  locale: Locale = currentLocale(),
): string {
  return locale === "en" ? item.short_en : item.short_pt;
}
