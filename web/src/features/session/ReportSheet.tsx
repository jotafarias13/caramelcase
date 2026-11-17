import { useState } from "react";
import { useTranslation } from "react-i18next";
import { useReportQuestion } from "@/api/queries";
import type { ReportReason } from "@/api/types";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/input";
import { RadioRow, RadioRows } from "@/components/ui/radio-row";
import { Sheet } from "@/components/ui/sheet";
import { toast } from "@/components/ui/toast-store";

const reasons: ReportReason[] = [
  "wrong_answer",
  "ambiguous_wording",
  "typo",
  "other",
];

// A comment longer than this is an essay; the API takes any length.
const COMMENT_MAX_LENGTH = 1000;

type ReportSheetProps = {
  questionId: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
};

/**
 * design/screens/v1-report: a bottom sheet on phones, a modal from
 * 1280 px. A reason is required, details are not.
 */
export function ReportSheet({
  questionId,
  open,
  onOpenChange,
}: ReportSheetProps) {
  const { t } = useTranslation();
  const [reason, setReason] = useState<ReportReason | null>(null);
  const [comment, setComment] = useState("");
  const report = useReportQuestion(questionId);

  function send() {
    if (!reason) return;
    report.mutate(
      { reason, comment: comment.trim() || null },
      {
        onSuccess: () => {
          onOpenChange(false);
          setReason(null);
          setComment("");
          toast({ kind: "success", message: t("report.sent") });
        },
        onError: () => toast({ kind: "error", message: t("report.failed") }),
      },
    );
  }

  return (
    <Sheet
      open={open}
      onOpenChange={onOpenChange}
      title={t("report.title")}
      closeLabel={t("common.close")}
      // v1-report centres the title on the 44 px close button, which sits
      // inside the padding.
      className="gap-3 max-lg:pt-4 lg:gap-3.5 [&>div:first-child]:items-center [&>div:first-child>button]:m-0"
    >
      <p className="m-0 text-[14px] leading-5 text-fg-muted">
        {t("report.question")}
      </p>
      <RadioRows
        label={t("report.question")}
        value={reason}
        onChange={setReason}
        className="gap-2 pb-0"
      >
        {reasons.map((value) => (
          <RadioRow
            key={value}
            value={value}
            title={t(`report.reasons.${value}`)}
          />
        ))}
      </RadioRows>
      <Textarea
        label={t("report.details")}
        placeholder={t("report.details_placeholder")}
        value={comment}
        maxLength={COMMENT_MAX_LENGTH}
        onChange={(event) => setComment(event.target.value)}
      />
      <div className="flex flex-wrap items-center justify-end gap-3 pr-1">
        <Button variant="ghost" size="md" onClick={() => onOpenChange(false)}>
          {t("common.cancel")}
        </Button>
        <Button
          size="md"
          disabled={!reason}
          loading={report.isPending}
          onClick={send}
        >
          {t("common.send")}
        </Button>
      </div>
    </Sheet>
  );
}
