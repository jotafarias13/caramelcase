import { ArrowLeft, Check } from "lucide-react";
import { useTranslation } from "react-i18next";
import { Link, useNavigate } from "react-router";
import { usePatchSettings, useSubjects } from "@/api/queries";
import type { SubjectSummary } from "@/api/types";
import {
  EmptyState,
  FailureScreen,
  LoadingState,
} from "@/components/StateScreen";
import { SubjectBadge } from "@/components/SubjectBadge";
import { RatingChip } from "@/components/ui/chips";
import { toast } from "@/components/ui/toast-store";
import { localName } from "@/i18n";
import { cn } from "@/lib/utils";

// The published subjects; choosing one makes it the subject Home shows.
// There is no V1 mockup: the rows are those of the V2 catalog
// (design/screens/v2-catalog-*), without add, remove, search or the course
// filter, which arrive in milestone 9 (docs/DECISIONS.md).
export default function SubjectsPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const subjects = useSubjects();
  const patch = usePatchSettings();

  if (subjects.error) {
    return (
      <FailureScreen
        error={subjects.error}
        onRetry={() => void subjects.refetch()}
      />
    );
  }
  if (!subjects.data) return <LoadingState />;

  function choose(subject: SubjectSummary) {
    if (subject.is_current) {
      navigate("/home");
      return;
    }
    patch.mutate(
      { current_subject: subject.slug },
      {
        onSuccess: () => navigate("/home"),
        onError: () =>
          toast({ kind: "error", message: t("subjects.switch_failed") }),
      },
    );
  }

  const list = subjects.data.subjects;
  return (
    <div className="flex flex-col gap-4 lg:max-w-[720px] lg:gap-5">
      <div className="-ml-2.5 flex items-center gap-1">
        <Link
          to="/home"
          aria-label={t("common.back")}
          className="inline-flex size-11 shrink-0 items-center justify-center rounded-md text-fg-muted hover:bg-surface-raised active:bg-border"
        >
          <ArrowLeft aria-hidden="true" className="size-[22px]" />
        </Link>
        <h1 className="text-[24px] leading-[30px] font-bold tracking-[-0.01em] text-balance lg:text-[30px] lg:leading-9">
          {t("subjects.title")}
        </h1>
      </div>

      {list.length === 0 ? (
        <EmptyState
          title={t("subjects.empty_title")}
          body={t("subjects.empty_body")}
        />
      ) : (
        <ul className="flex flex-col gap-2 pr-[3px] pb-[3px]">
          {list.map((subject) => (
            <li key={subject.slug}>
              <SubjectRow
                subject={subject}
                onChoose={() => choose(subject)}
                disabled={patch.isPending}
              />
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

type SubjectRowProps = {
  subject: SubjectSummary;
  onChoose: () => void;
  disabled: boolean;
};

// A row of the V2 catalog: badge and name on the left. Where the V2 row
// has its add or remove button, this one shows the student's rating; the
// current subject has the selected look of a radio row.
function SubjectRow({ subject, onChoose, disabled }: SubjectRowProps) {
  const { t } = useTranslation();
  const rating = subject.rating === null ? null : Math.round(subject.rating);

  return (
    <button
      type="button"
      onClick={onChoose}
      disabled={disabled}
      aria-current={subject.is_current ? "true" : undefined}
      className={cn(
        "flex min-h-16 w-full cursor-pointer items-center gap-3 rounded-lg text-left text-fg",
        "transition-[translate] duration-press ease-linear",
        "active:translate-x-0.5 active:translate-y-0.5",
        "disabled:cursor-not-allowed",
        subject.is_current
          ? "border-2 border-action-border bg-action-tint py-[7px] pr-3 pl-[13px] shadow-selected"
          : "border border-border bg-surface py-2 pr-[13px] pl-3.5 hover:bg-surface-raised",
      )}
    >
      <span className="flex min-w-0 grow items-center gap-2.5">
        <SubjectBadge subject={subject} />
        <span className="min-w-0 text-[16px] leading-[22px] font-semibold">
          {localName(subject)}
        </span>
      </span>
      {subject.is_current && (
        <span className="flex shrink-0 items-center gap-1 text-[13px] leading-[18px] font-semibold text-action-text">
          <Check aria-hidden="true" strokeWidth={3} className="size-3.5" />
          {t("subjects.current")}
        </span>
      )}
      {rating === null ? (
        <span className="shrink-0 text-[13px] leading-[18px] text-fg-muted">
          {t("subjects.not_practiced")}
        </span>
      ) : (
        <RatingChip label={t("nav.rating_chip", { rating })}>
          {rating}
        </RatingChip>
      )}
    </button>
  );
}
