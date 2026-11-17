import type { Scene } from "../scene";
import { auth } from "./auth";
import { catalog } from "./catalog";
import { home } from "./home";
import { landing } from "./landing";
import { onboarding } from "./onboarding";
import { profile } from "./profile";
import { session } from "./session";
import { settings } from "./settings";
import { states } from "./states";
import { summary } from "./summary";

// One file per feature, next to the screens it covers.
export const scenes: Scene[] = [
  ...states,
  ...landing,
  ...auth,
  ...onboarding,
  ...home,
  ...catalog,
  ...session,
  ...summary,
  ...profile,
  ...settings,
];
