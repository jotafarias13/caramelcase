import celebrate from "@design/assets/mel-celebrate.svg";
import encourage from "@design/assets/mel-encourage.svg";
import mischief from "@design/assets/mel-mischief.svg";
import sleep from "@design/assets/mel-sleep.svg";
import study from "@design/assets/mel-study.svg";
import think from "@design/assets/mel-think.svg";
import wave from "@design/assets/mel-wave.svg";

const sprites = { wave, celebrate, encourage, think, sleep, mischief, study };

// Every full sprite is drawn on a 26 × 27 px canvas.
const SPRITE_WIDTH = 26;
const SPRITE_HEIGHT = 27;

type MelProps = {
  pose: keyof typeof sprites;
  /** Whole number: 4 to 6 on screens (design/README.md, "Mel"). */
  scale: number;
  /** Leave empty when Mel is decoration next to text that says the same. */
  alt?: string;
};

export function Mel({ pose, scale, alt = "" }: MelProps) {
  return (
    <img
      src={sprites[pose]}
      alt={alt}
      width={SPRITE_WIDTH * scale}
      height={SPRITE_HEIGHT * scale}
      className="shrink-0 [image-rendering:pixelated]"
    />
  );
}
