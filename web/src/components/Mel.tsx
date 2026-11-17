import celebrate from "@design/assets/mel-celebrate.svg";
import encourage from "@design/assets/mel-encourage.svg";
import headCelebrate from "@design/assets/mel-head-celebrate.svg";
import headEncourage from "@design/assets/mel-head-encourage.svg";
import headMischief from "@design/assets/mel-head-mischief.svg";
import headSleep from "@design/assets/mel-head-sleep.svg";
import headStudy from "@design/assets/mel-head-study.svg";
import headThink from "@design/assets/mel-head-think.svg";
import headWave from "@design/assets/mel-head-wave.svg";
import mischief from "@design/assets/mel-mischief.svg";
import sleep from "@design/assets/mel-sleep.svg";
import study from "@design/assets/mel-study.svg";
import think from "@design/assets/mel-think.svg";
import wave from "@design/assets/mel-wave.svg";
import { useTranslation } from "react-i18next";
import { cn } from "@/lib/utils";

const sprites = { wave, celebrate, encourage, think, sleep, mischief, study };
const heads = {
  wave: headWave,
  celebrate: headCelebrate,
  encourage: headEncourage,
  think: headThink,
  sleep: headSleep,
  mischief: headMischief,
  study: headStudy,
};

// A full sprite is drawn on a 26 × 27 px canvas, a head crop on 21 × 14.
const SPRITE = { width: 26, height: 27 };
const HEAD = { width: 21, height: 14 };

export type MelPose = keyof typeof sprites;

type MelProps = {
  pose: MelPose;
  /** Whole number: 4 to 6 for a sprite, 2 to 4 for a head. */
  scale: number;
  /** The head-only crop, for panels and avatars. */
  head?: boolean;
  /** Pass "" when Mel is decoration; by default the pose is described. */
  alt?: string;
  className?: string;
};

export function Mel({ pose, scale, head = false, alt, className }: MelProps) {
  const { t } = useTranslation();
  const size = head ? HEAD : SPRITE;
  return (
    <img
      src={head ? heads[pose] : sprites[pose]}
      alt={alt ?? t(`mel.${pose}`)}
      width={size.width * scale}
      height={size.height * scale}
      className={cn("shrink-0 [image-rendering:pixelated]", className)}
    />
  );
}
