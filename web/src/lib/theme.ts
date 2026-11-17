/**
 * Theme choice. design/tokens.css follows the system setting when <html>
 * has no data-theme, but the app always sets it to "dark" or "light" so
 * that Tailwind's dark: variant and theme-specific assets have one thing to
 * look at.
 */
export type ThemeChoice = "system" | "dark" | "light";
export type Theme = "dark" | "light";

const STORAGE_KEY = "caramelcase.theme";
const LIGHT_QUERY = "(prefers-color-scheme: light)";

function systemTheme(): Theme {
  return window.matchMedia?.(LIGHT_QUERY).matches ? "light" : "dark";
}

export function getThemeChoice(): ThemeChoice {
  const stored = localStorage.getItem(STORAGE_KEY);
  return stored === "dark" || stored === "light" ? stored : "system";
}

export function applyTheme(choice: ThemeChoice): Theme {
  const theme = choice === "system" ? systemTheme() : choice;
  document.documentElement.setAttribute("data-theme", theme);
  return theme;
}

export function setThemeChoice(choice: ThemeChoice): Theme {
  if (choice === "system") {
    localStorage.removeItem(STORAGE_KEY);
  } else {
    localStorage.setItem(STORAGE_KEY, choice);
  }
  return applyTheme(choice);
}

/** Apply the stored choice and follow the system while it is "system". */
export function initTheme(): void {
  applyTheme(getThemeChoice());
  window.matchMedia?.(LIGHT_QUERY).addEventListener("change", () => {
    applyTheme(getThemeChoice());
  });
}
