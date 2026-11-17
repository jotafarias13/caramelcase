// The month calendar of the profile, worked out from GET /me/activity.
// Dates are the API's local dates ("2026-11-16"), handled in UTC so that
// the device's timezone never moves a day.
import type { Activity } from "@/api/types";

/** practiced: a day the API lists; idle: a day that passed without one. */
export type DayState = "practiced" | "idle" | "future";

export type CalendarDay = {
  day: number;
  date: string;
  state: DayState;
  isToday: boolean;
};

export type CalendarMonth = {
  /** The first day of the month, as a UTC date to format. */
  first: Date;
  /** Empty cells before day 1, in a week that starts on Sunday. */
  leadingBlanks: number;
  days: CalendarDay[];
};

function isoDate(year: number, monthIndex: number, day: number): string {
  const month = String(monthIndex + 1).padStart(2, "0");
  return `${year}-${month}-${String(day).padStart(2, "0")}`;
}

/** The month that holds `activity.start`, day by day. */
export function calendarMonth(activity: Activity): CalendarMonth {
  const [year, month] = activity.start.split("-").map(Number);
  const monthIndex = month - 1;
  const first = new Date(Date.UTC(year, monthIndex, 1));
  // Day 0 of the next month is the last day of this one.
  const length = new Date(Date.UTC(year, monthIndex + 1, 0)).getUTCDate();
  const practiced = new Set(activity.days.map((day) => day.date));

  const days = Array.from({ length }, (_, index): CalendarDay => {
    const date = isoDate(year, monthIndex, index + 1);
    // ISO dates compare as strings.
    const state: DayState = practiced.has(date)
      ? "practiced"
      : date > activity.today
        ? "future"
        : "idle";
    return { day: index + 1, date, state, isToday: date === activity.today };
  });

  return { first, leadingBlanks: first.getUTCDay(), days };
}

/** "novembro de 2026" or "November 2026". */
export function monthLabel(first: Date, locale: string): string {
  return new Intl.DateTimeFormat(locale, {
    month: "long",
    year: "numeric",
    timeZone: "UTC",
  }).format(first);
}

/** One letter per weekday from Sunday: D S T Q Q S S, or S M T W T F S. */
export function weekdayLetters(locale: string): string[] {
  const format = new Intl.DateTimeFormat(locale, {
    weekday: "narrow",
    timeZone: "UTC",
  });
  // 1 January 2023 was a Sunday.
  return Array.from({ length: 7 }, (_, index) =>
    format.format(new Date(Date.UTC(2023, 0, 1 + index))),
  );
}
