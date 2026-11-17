import { ChevronDown } from "lucide-react";
import { useTranslation } from "react-i18next";
import { Link } from "react-router";
import { usePatchSettings, useSubjects } from "@/api/queries";
import type { SubjectRef, SubjectSummary } from "@/api/types";
import { SubjectBadge } from "@/components/SubjectBadge";
import { Button } from "@/components/ui/button";
import { buttonVariants } from "@/components/ui/button-variants";
import { RadioRow, RadioRows } from "@/components/ui/radio-row";
import { Sheet } from "@/components/ui/sheet";
import { toast } from "@/components/ui/toast-store";
import { localName } from "@/i18n";
import { cn } from "@/lib/utils";

type SubjectSwitcherProps = {
  current: SubjectRef;
  open: boolean;
  onOpenChange: (open: boolean) => void;
};

/**
 * The button with the current subject, and the sheet it opens. The open
 * sheet is not drawn in the design ("Not designed" in design/README.md):
 * it is built from the bottom sheet and the radio rows.
 */
export function SubjectSwitcher({
  current,
  open,
  onOpenChange,
}: SubjectSwitcherProps) {
  const { t } = useTranslation();
  const name = localName(current);

  return (
    <>
      <button
        type="button"
        aria-label={t("home.switch_subject", { subject: name })}
        onClick={() => onOpenChange(true)}
        className={cn(
          "flex h-13 w-full cursor-pointer items-center gap-2.5 rounded-lg px-3.5 text-left text-fg",
          "border-[1.5px] border-border-strong bg-surface shadow-step-md",
          "transition-[translate,box-shadow] duration-press ease-linear hover:bg-surface-raised",
          "active:translate-x-0.5 active:translate-y-0.5 active:shadow-[1px_1px_0_var(--shadow-hard)]",
        )}
      >
        <SubjectBadge subject={current} />
        <span className="min-w-0 grow truncate text-[16px] leading-[22px] font-bold">
          {name}
        </span>
        <ChevronDown
          aria-hidden="true"
          className="size-[18px] shrink-0 text-fg-muted"
        />
      </button>
      <Sheet
        open={open}
        onOpenChange={onOpenChange}
        title={t("home.switch_title")}
        closeLabel={t("common.close")}
        handle
      >
        <SubjectChoices
          currentSlug={current.slug}
          onDone={() => onOpenChange(false)}
        />
      </Sheet>
    </>
  );
}

function SubjectChoices({
  currentSlug,
  onDone,
}: {
  currentSlug: string;
  onDone: () => void;
}) {
  const { t } = useTranslation();
  const subjects = useSubjects();
  const patch = usePatchSettings();

  function choose(subject: SubjectSummary) {
    if (subject.slug === currentSlug) {
      onDone();
      return;
    }
    patch.mutate(
      { current_subject: subject.slug },
      {
        onSuccess: onDone,
        onError: () =>
          toast({ kind: "error", message: t("home.switch_failed") }),
      },
    );
  }

  if (!subjects.data) {
    return subjects.error ? (
      <Button variant="secondary" onClick={() => void subjects.refetch()}>
        {t("common.try_again")}
      </Button>
    ) : (
      <p role="status" className="text-[15px] leading-5 text-fg-muted">
        {t("common.loading")}
      </p>
    );
  }

  const list = subjects.data.subjects;
  // While the change is on its way, the row tapped already looks chosen.
  const chosen = patch.isPending
    ? (patch.variables.current_subject ?? currentSlug)
    : currentSlug;

  return (
    <>
      <RadioRows
        label={t("home.switch_title")}
        value={chosen}
        onChange={(slug) => {
          const subject = list.find((item) => item.slug === slug);
          if (subject) choose(subject);
        }}
      >
        {list.map((subject) => (
          <RadioRow
            key={subject.slug}
            value={subject.slug}
            title={localName(subject)}
            leading={<SubjectBadge subject={subject} />}
            disabled={patch.isPending}
          />
        ))}
      </RadioRows>
      <Link
        to="/subjects"
        className={cn(
          buttonVariants({ variant: "ghost", size: "md" }),
          "w-full",
        )}
      >
        {t("home.all_subjects")}
      </Link>
    </>
  );
}
