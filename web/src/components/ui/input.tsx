import { TriangleAlert } from "lucide-react";
import {
  useId,
  type InputHTMLAttributes,
  type ReactNode,
  type TextareaHTMLAttributes,
} from "react";
import { cn } from "@/lib/utils";

// "Input, textarea, search" in design/README.md.
const fieldClasses = [
  "w-full rounded-md border-[1.5px] border-border-strong bg-bg-well px-3.5",
  "font-sans text-[16px] text-fg placeholder:text-fg-subtle",
  "hover:border-fg focus-visible:border-action-border",
  "focus-visible:outline-focus focus-visible:outline-offset-2",
  "disabled:cursor-not-allowed disabled:border-transparent disabled:bg-disabled disabled:text-disabled-text",
  "aria-invalid:border-2 aria-invalid:border-wrong-border",
];

type FieldFrameProps = {
  id: string;
  label: string;
  helper?: string;
  error?: string;
  children: ReactNode;
};

function FieldFrame({ id, label, helper, error, children }: FieldFrameProps) {
  return (
    <div className="flex flex-col gap-1.5">
      <label
        htmlFor={id}
        className="text-[13px] leading-[18px] font-semibold text-fg"
      >
        {label}
      </label>
      {children}
      {error ? (
        <p
          id={`${id}-note`}
          role="alert"
          className="flex items-center gap-1.5 text-caption text-wrong-text"
        >
          <TriangleAlert aria-hidden="true" className="size-3.5 shrink-0" />
          {error}
        </p>
      ) : (
        helper && (
          <p
            id={`${id}-note`}
            className="text-caption font-normal text-fg-muted"
          >
            {helper}
          </p>
        )
      )}
    </div>
  );
}

type SharedProps = {
  label: string;
  /** A line under the field. */
  helper?: string;
  /** Replaces the helper and marks the field as invalid. */
  error?: string;
};

type InputProps = InputHTMLAttributes<HTMLInputElement> & SharedProps;

export function Input({
  label,
  helper,
  error,
  className,
  ...props
}: InputProps) {
  const generatedId = useId();
  const id = props.id ?? generatedId;
  return (
    <FieldFrame id={id} label={label} helper={helper} error={error}>
      <input
        {...props}
        id={id}
        aria-invalid={error ? true : undefined}
        aria-describedby={helper || error ? `${id}-note` : undefined}
        className={cn(fieldClasses, "h-12", className)}
      />
    </FieldFrame>
  );
}

type TextareaProps = TextareaHTMLAttributes<HTMLTextAreaElement> & SharedProps;

export function Textarea({
  label,
  helper,
  error,
  className,
  ...props
}: TextareaProps) {
  const generatedId = useId();
  const id = props.id ?? generatedId;
  return (
    <FieldFrame id={id} label={label} helper={helper} error={error}>
      <textarea
        {...props}
        id={id}
        aria-invalid={error ? true : undefined}
        aria-describedby={helper || error ? `${id}-note` : undefined}
        className={cn(
          fieldClasses,
          "h-24 resize-none py-3 leading-[22px]",
          className,
        )}
      />
    </FieldFrame>
  );
}
