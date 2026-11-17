import { Check, ChevronRight, Lock, Play, Star } from "lucide-react";
import type { ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { cn } from "@/lib/utils";
import type { TopicNodeState } from "./topic-node-state";

const nodeClasses: Record<TopicNodeState, string> = {
  locked:
    "border-[1.5px] border-dashed border-border-strong bg-bg text-fg-subtle",
  available:
    "border-2 border-action-border bg-surface text-action-text shadow-selected",
  in_progress:
    "border-2 border-brand-deep bg-surface text-brand-text shadow-brand",
  mastered: "border-2 border-brand-deep bg-brand text-brand-fg shadow-brand",
};

type TopicNodeProps = {
  name: string;
  state: TopicNodeState;
  /** Share of right answers, 0 to 100: shown while in progress. */
  percent?: number;
  onSelect?: () => void;
  disabled?: boolean;
};

// "Topic node" in design/README.md: one row of the topic path. Stack rows
// inside <TopicPath>, which draws the rail behind the nodes.
export function TopicNode({
  name,
  state,
  percent = 0,
  onSelect,
  disabled = false,
}: TopicNodeProps) {
  const locked = state === "locked";
  return (
    <button
      type="button"
      onClick={onSelect}
      disabled={disabled || locked}
      className={cn(
        "flex min-h-[76px] w-full items-center gap-3.5 rounded-lg px-3 py-2.5 text-left text-fg",
        "transition-[translate] duration-press ease-linear",
        "enabled:cursor-pointer enabled:hover:bg-surface-raised enabled:active:translate-x-0.5 enabled:active:translate-y-0.5",
        "disabled:cursor-not-allowed",
      )}
    >
      <span
        aria-hidden="true"
        className={cn(
          "flex size-[52px] shrink-0 items-center justify-center rounded-lg",
          nodeClasses[state],
        )}
      >
        <NodeIcon state={state} percent={percent} />
      </span>
      <span className="flex min-w-0 grow flex-col gap-[3px]">
        <span
          className={cn(
            "text-[16px] leading-[22px] font-semibold",
            locked ? "text-fg-muted" : "text-fg",
          )}
        >
          {name}
        </span>
        <StatusLine state={state} percent={percent} />
      </span>
      {!locked && (
        <ChevronRight
          aria-hidden="true"
          className="size-[18px] shrink-0 text-fg-subtle"
        />
      )}
    </button>
  );
}

function NodeIcon({
  state,
  percent,
}: {
  state: TopicNodeState;
  percent: number;
}) {
  switch (state) {
    case "locked":
      return <Lock className="size-5" />;
    case "available":
      return <Play fill="currentColor" className="size-5" />;
    case "in_progress":
      return (
        <span className="font-mono text-[13px] leading-4 font-extrabold">
          {percent}%
        </span>
      );
    case "mastered":
      return <Star fill="currentColor" className="size-[22px]" />;
  }
}

function StatusLine({
  state,
  percent,
}: {
  state: TopicNodeState;
  percent: number;
}) {
  const { t } = useTranslation();
  switch (state) {
    case "locked":
      return (
        <span className="text-[13px] leading-[18px] font-medium text-fg-muted">
          {t("home.topic_locked")}
        </span>
      );
    case "available":
      return (
        <span className="text-[13px] leading-[18px] font-semibold text-action-text">
          {t("home.topic_available")}
        </span>
      );
    case "in_progress":
      return (
        <span className="flex items-center gap-2">
          <span className="flex h-1.5 w-24 overflow-hidden rounded-px bg-border">
            <span className="bg-brand" style={{ width: `${percent}%` }} />
          </span>
          <span className="text-[13px] leading-[18px] font-medium text-fg-muted">
            {t("home.topic_in_progress")}
          </span>
          {/* The node's percentage is hidden from screen readers. */}
          <span className="sr-only">{percent}%</span>
        </span>
      );
    case "mastered":
      return (
        <span className="flex items-center gap-1 text-[13px] leading-[18px] font-semibold text-correct-text">
          <Check aria-hidden="true" strokeWidth={3} className="size-3.5" />
          <span>{t("home.topic_mastered")}</span>
        </span>
      );
  }
}

/** The rows of a topic path, on a 2 px rail that joins their nodes. */
export function TopicPath({ children }: { children: ReactNode }) {
  return (
    <div className="relative">
      <div
        aria-hidden="true"
        className="absolute top-10 bottom-10 left-[37px] w-0.5 bg-border"
      />
      <div className="relative flex flex-col gap-1">{children}</div>
    </div>
  );
}
