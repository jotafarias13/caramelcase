import { ToggleGroup } from "radix-ui";
import { cn } from "@/lib/utils";

type SegmentedControlProps<Value extends string> = {
  /** Names the group for screen readers. */
  label: string;
  value: Value;
  options: { value: Value; label: string }[];
  onChange: (value: Value) => void;
  className?: string;
};

// "Segmented control" in design/README.md: exactly one item is active.
export function SegmentedControl<Value extends string>({
  label,
  value,
  options,
  onChange,
  className,
}: SegmentedControlProps<Value>) {
  return (
    <ToggleGroup.Root
      type="single"
      aria-label={label}
      value={value}
      // Radix sends "" when the active item is pressed again; keep it active.
      onValueChange={(next) => next && onChange(next as Value)}
      className={cn(
        "flex gap-1 rounded-lg border-[1.5px] border-border-strong bg-bg-well p-1",
        className,
      )}
    >
      {options.map((option) => (
        <ToggleGroup.Item
          key={option.value}
          value={option.value}
          className={cn(
            "min-h-touch flex-1 cursor-pointer rounded-tile px-1.5 py-1",
            "text-[14px] leading-[18px] font-medium text-fg",
            "data-[state=on]:bg-brand data-[state=on]:font-bold data-[state=on]:text-brand-fg",
          )}
        >
          {option.label}
        </ToggleGroup.Item>
      ))}
    </ToggleGroup.Root>
  );
}
