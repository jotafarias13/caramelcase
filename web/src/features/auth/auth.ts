import { currentLocale } from "@/i18n";
import { browserTimezone } from "@/lib/timezone";

/**
 * The API redirects the browser to Google, and Google back to
 * /auth/callback: a page navigation, not a fetch. It carries the
 * language and timezone of this device, for an account the sign-in
 * creates.
 */
export function googleStartUrl(): string {
  const query = new URLSearchParams({
    locale: currentLocale(),
    timezone: browserTimezone(),
  });
  return `/api/v1/auth/google/start?${query}`;
}

/** The form the API checks too: something, @, something with a dot. */
export function looksLikeEmail(value: string): boolean {
  return /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(value);
}
