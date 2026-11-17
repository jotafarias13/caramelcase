import { useConfig } from "@/api/queries";

/**
 * Whether a feature flag is on for this user, as GET /config says. Off
 * while the config is loading, so a flagged feature never flashes.
 */
export function useFlag(key: string): boolean {
  const config = useConfig();
  return config.data?.flags[key] ?? false;
}
