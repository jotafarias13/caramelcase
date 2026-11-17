import { localShort } from "@/i18n";
import { cn } from "@/lib/utils";
import { Badge } from "./ui/badge";

type SubjectBadgeProps = {
  subject: { short_pt: string; short_en: string };
  className?: string;
};

// A subject's short name ("ed/", "bd/") in caramel, as the subject switcher
// and the catalog rows show it: the badge at 12 px.
export function SubjectBadge({ subject, className }: SubjectBadgeProps) {
  return (
    <Badge className={cn("text-[12px] leading-4", className)}>
      {localShort(subject)}
    </Badge>
  );
}
