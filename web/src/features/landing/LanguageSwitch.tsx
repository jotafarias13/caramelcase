import { ChevronDown } from "lucide-react";
import { useTranslation } from "react-i18next";
import type { Locale } from "@/api/types";
import { defaultLocale, locales } from "@/i18n";
import { useChangeLocale } from "@/lib/preferences";

function asLocale(language: string): Locale {
  return locales.includes(language as Locale)
    ? (language as Locale)
    : defaultLocale;
}

/**
 * "PT-BR ▾" in the header. It is a native select laid over the label the
 * mockup draws: the phone's own picker opens, with no menu component.
 */
export function LanguageSwitch() {
  const { t, i18n } = useTranslation();
  const changeLocale = useChangeLocale();
  const current = asLocale(i18n.language);

  return (
    <label className="relative flex h-11 items-center gap-1 rounded-md px-2.5 font-mono text-[12px] leading-4 font-bold text-fg-muted hover:bg-surface-raised has-[select:focus-visible]:[outline:var(--focus-width)_solid_var(--focus-ring)] has-[select:focus-visible]:[outline-offset:var(--focus-offset)]">
      <span aria-hidden="true">{t(`common.language_short.${current}`)}</span>
      <ChevronDown aria-hidden="true" className="size-3.5 shrink-0" />
      <select
        aria-label={t("landing.language_label", {
          language: t(`common.languages.${current}`),
        })}
        value={current}
        onChange={(event) => changeLocale(asLocale(event.target.value))}
        className="absolute inset-0 cursor-pointer appearance-none opacity-0 outline-none"
      >
        {locales.map((locale) => (
          <option key={locale} value={locale} lang={locale}>
            {t(`common.languages.${locale}`)}
          </option>
        ))}
      </select>
    </label>
  );
}
