import { useEffect, useRef, useState } from "react";
import { motionMs } from "./motion";

const PIXELS = 24;
// The fills of the confetti in the celebrate sprite.
const colours = ["bg-xp", "bg-streak", "bg-rating", "bg-action", "bg-brand"];

/**
 * The "level-up" motion of design/README.md: 24 confetti pixels fall and
 * fade over the hero. Under reduced motion the duration token is 0 and
 * nothing is drawn. Spread and timing come from the pixel's index, so
 * every level up looks the same.
 */
export function LevelUpBurst() {
  const [duration] = useState(() => motionMs("--dur-level-up"));
  const layer = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const pixels = layer.current?.children;
    if (!duration || !pixels) return;
    const animations = Array.from(pixels, (pixel, index) =>
      pixel.animate?.(
        [
          { transform: "translateY(0)", opacity: 1 },
          { transform: `translateY(${120 + (index % 4) * 30}px)`, opacity: 0 },
        ],
        {
          duration,
          delay: (index % 6) * (duration / 12),
          easing: "ease-out",
          fill: "both",
        },
      ),
    );
    return () => animations.forEach((animation) => animation?.cancel());
  }, [duration]);

  if (!duration) return null;
  return (
    <div
      ref={layer}
      aria-hidden="true"
      className="pointer-events-none absolute inset-x-0 top-0 h-0"
    >
      {Array.from({ length: PIXELS }, (_, index) => (
        <span
          key={index}
          className={`absolute size-1.5 opacity-0 ${colours[index % colours.length]}`}
          style={{
            left: `${4 + ((index * 37) % 92)}%`,
            top: `${(index * 13) % 40}px`,
          }}
        />
      ))}
    </div>
  );
}
