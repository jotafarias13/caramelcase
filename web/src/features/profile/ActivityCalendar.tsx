import { useTranslation } from "react-i18next";
import type { Activity } from "@/api/types";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import {
  calendarMonth,
  monthLabel,
  weekdayLetters,
  type CalendarDay,
} from "./calendar";

const dayStyles: Record<CalendarDay["state"], string> = {
  practiced: "bg-streak font-extrabold text-streak-fg",
  idle: "bg-bg-well text-fg",
  future: "text-disabled-text",
};

function Day({ day }: { day: CalendarDay }) {
  const { t } = useTranslation();
  return (
    <span
      className={cn(
        "flex h-9 items-center justify-center rounded-sm font-mono text-[13px] leading-4",
        dayStyles[day.state],
        day.isToday && "outline-2 outline-offset-2 outline-fg",
      )}
    >
      {day.day}
      {/* The colours and the outline say this to the eye. */}
      {day.state === "practiced" && (
        <span className="sr-only">{t("profile.day_with_practice")}</span>
      )}
      {day.isToday && <span className="sr-only">{t("profile.today")}</span>}
    </span>
  );
}

/** "Calendário": this month, with the days the student practiced. */
export function ActivityCalendar({ activity }: { activity: Activity }) {
  const { t, i18n } = useTranslation();
  // Month and weekday names come from the browser in the interface language.
  const locale = i18n.language;
  const month = calendarMonth(activity);

  return (
    <Card>
      <div className="flex items-center justify-between gap-2">
        <h2 className="text-[18px] leading-6 font-bold text-fg">
          {t("profile.calendar")}
        </h2>
        <span className="font-mono text-[12px] leading-4 text-fg-muted">
          {monthLabel(month.first, locale)}
        </span>
      </div>
      <div className="grid grid-cols-7 gap-1.5">
        {weekdayLetters(locale).map((letter, index) => (
          <span
            key={index}
            aria-hidden="true"
            className="text-center font-mono text-[11px] leading-4 text-fg-muted"
          >
            {letter}
          </span>
        ))}
        {Array.from({ length: month.leadingBlanks }, (_, index) => (
          <span key={`blank-${index}`} aria-hidden="true" />
        ))}
        {month.days.map((day) => (
          <Day key={day.date} day={day} />
        ))}
      </div>
      <div
        aria-hidden="true"
        className="flex items-center gap-2 text-[12px] leading-4 text-fg-muted"
      >
        <span className="size-3 rounded-px bg-streak" />
        <span>{t("profile.day_with_practice")}</span>
        <span className="ml-2 size-3.5 rounded-px border-2 border-fg" />
        <span>{t("profile.today")}</span>
      </div>
    </Card>
  );
}
