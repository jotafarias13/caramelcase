import { Check } from "lucide-react";
import { Switch as RadixSwitch } from "radix-ui";
import { cn } from "@/lib/utils";

type SwitchProps = {
  checked: boolean;
  onCheckedChange: (checked: boolean) => void;
  disabled?: boolean;
  /** The id a <label htmlFor> points at, so the label is clickable. */
  id?: string;
  "aria-label"?: string;
  "aria-labelledby"?: string;
  "aria-describedby"?: string;
};

// "Toggle" in design/README.md: 52 × 30 with a square knob.
export function Switch({ checked, onCheckedChange, ...props }: SwitchProps) {
  return (
    <RadixSwitch.Root
      checked={checked}
      onCheckedChange={onCheckedChange}
      className={cn(
        "relative h-[30px] w-13 shrink-0 cursor-pointer rounded-tile border-[1.5px]",
        "border-border-strong bg-surface-raised hover:bg-border",
        "data-[state=checked]:border-action-border data-[state=checked]:bg-action",
        "data-[state=checked]:hover:bg-action-hover",
        "disabled:cursor-not-allowed disabled:border-transparent disabled:bg-disabled",
      )}
      {...props}
    >
      <RadixSwitch.Thumb
        className={cn(
          "absolute top-[2.5px] left-[2.5px] flex size-[22px] items-center justify-center",
          "rounded-xs bg-fg-muted text-transparent transition-[left] duration-select",
          "data-[state=checked]:left-[24.5px] data-[state=checked]:bg-action-fg",
          "data-[state=checked]:text-action",
        )}
      >
        <Check aria-hidden="true" strokeWidth={3} className="size-3.5" />
      </RadixSwitch.Thumb>
    </RadixSwitch.Root>
  );
}
