import { clsx, type ClassValue } from "clsx";
import { extendTailwindMerge } from "tailwind-merge";

// tailwind-merge only knows Tailwind's default scale names. Without these
// lists it reads the design's "text-title" as a colour and drops it next to
// "text-fg". The names mirror design/tailwind.theme.js; utils.test.ts fails
// when the two drift apart.
export const designScales = {
  text: [
    "display",
    "title",
    "question",
    "heading",
    "body",
    "body-sm",
    "caption",
    "button",
    "label-mono",
    "code",
    "code-lg",
    "stat-mono",
  ],
  radius: [
    "px",
    "xs",
    "sm",
    "tile",
    "md",
    "lg",
    "bubble",
    "card",
    "xl",
    "full",
  ],
  shadow: [
    "step-sm",
    "step-md",
    "step-lg",
    "step-xl",
    "selected",
    "brand",
    "overlay",
  ],
  spacing: ["gutter", "touch", "sidebar"],
  ease: ["standard", "pixel-5", "pixel-6"],
};

const twMerge = extendTailwindMerge({ extend: { theme: designScales } });

/** Join class names; a later Tailwind class wins over an earlier one. */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}
