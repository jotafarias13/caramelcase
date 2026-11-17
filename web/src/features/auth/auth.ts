// The API redirects the browser to Google, and Google back to
// /auth/callback. A page navigation, not a fetch.
export const GOOGLE_START_URL = "/api/v1/auth/google/start";

/** The form the API checks too: something, @, something with a dot. */
export function looksLikeEmail(value: string): boolean {
  return /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(value);
}
