// Language and theme are kept on the device, so they hold before there is
// a user, and on the account, so they follow the user to another device.
import { useEffect } from "react";
import { useMe, usePatchSettings } from "@/api/queries";
import type { Locale, Me, ThemeSetting } from "@/api/types";
import { currentLocale, setLocale } from "@/i18n";
import { getThemeChoice, setThemeChoice } from "./theme";
import { browserTimezone } from "./timezone";

/** Called when the account could not be saved and the device went back. */
type OnSaveError = (error: unknown) => void;

/**
 * Switches the language at once. If the account cannot be saved, the
 * device goes back to the previous language: otherwise the account would
 * win on the next visit and the change would undo itself later.
 */
export function useChangeLocale(
  onError?: OnSaveError,
): (locale: Locale) => void {
  const me = useMe();
  const patch = usePatchSettings();
  return (locale) => {
    const previous = currentLocale();
    setLocale(locale);
    if (!me.data) return;
    patch.mutate(
      { locale },
      {
        onError: (error) => {
          setLocale(previous);
          onError?.(error);
        },
      },
    );
  };
}

/** Switches the theme at once; goes back as useChangeLocale does. */
export function useChangeTheme(
  onError?: OnSaveError,
): (theme: ThemeSetting) => void {
  const me = useMe();
  const patch = usePatchSettings();
  return (theme) => {
    const previous = getThemeChoice();
    setThemeChoice(theme);
    if (!me.data) return;
    patch.mutate(
      { theme },
      {
        onError: (error) => {
          setThemeChoice(previous);
          onError?.(error);
        },
      },
    );
  };
}

/**
 * When the account says something else than the device (a sign-in on a new
 * device), the account wins. The timezone goes the other way: the device
 * knows where the student is, and the API counts days in that timezone.
 */
export function useSyncPreferences(me: Me | null | undefined): void {
  const { mutate } = usePatchSettings();
  const locale = me?.locale;
  const theme = me?.settings.theme;
  const timezone = me?.timezone;

  useEffect(() => {
    if (locale && locale !== currentLocale()) setLocale(locale);
  }, [locale]);

  useEffect(() => {
    if (theme && theme !== getThemeChoice()) setThemeChoice(theme);
  }, [theme]);

  useEffect(() => {
    if (timezone && timezone !== browserTimezone()) {
      mutate({ timezone: browserTimezone() });
    }
  }, [timezone, mutate]);
}
