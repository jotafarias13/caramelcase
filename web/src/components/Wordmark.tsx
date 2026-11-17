import { cn } from "@/lib/utils";

type WordmarkProps = {
  /** Set the size with a font-size class: text-[20px] leading-[26px]. */
  className?: string;
};

// The name as the mockups draw it: mono type with the capital C in a
// caramel block. The brand name is the same in every language.
export function Wordmark({ className }: WordmarkProps) {
  /* eslint-disable local/no-hardcoded-copy */
  return (
    <span
      translate="no"
      className={cn(
        "block font-mono font-extrabold tracking-[-0.02em] whitespace-nowrap text-fg",
        className,
      )}
    >
      <span>caramel</span>
      <span className="mx-[0.04em] rounded-px bg-brand px-[0.07em] text-brand-fg">
        C
      </span>
      <span>ase</span>
    </span>
  );
  /* eslint-enable local/no-hardcoded-copy */
}
