import type { ReactNode } from "react";
import { useConfig } from "@/api/queries";
import {
  FailureScreen,
  LoadingScreen,
  NotFoundScreen,
} from "@/components/StateScreen";

type FlaggedProps = {
  /** A key of the feature_flags table, such as "review_queue". */
  flag: string;
  /** Usually a React.lazy component, so its code loads only when on. */
  children: ReactNode;
};

/**
 * A route behind a feature flag. While the flag is off the page does not
 * exist: the student sees the 404 screen and the feature's code is never
 * requested.
 */
export function Flagged({ flag, children }: FlaggedProps) {
  const config = useConfig();
  if (config.error) {
    return <FailureScreen error={config.error} onRetry={config.refetch} />;
  }
  if (!config.data) return <LoadingScreen />;
  if (!config.data.flags[flag]) return <NotFoundScreen />;
  return children;
}
