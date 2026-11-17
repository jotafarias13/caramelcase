// The summary's motion (design/README.md, "Motion": rating-delta, xp-gain,
// streak-increment, level-up). Every duration is a token of
// design/tokens.css, which is 0 under prefers-reduced-motion: then nothing
// moves and the final values are on screen from the first paint.
import { useEffect, useRef, useState } from "react";

/** A duration token ("--dur-rating") in milliseconds; 0 when unset. */
export function motionMs(token: string): number {
  if (typeof window === "undefined") return 0;
  const value = getComputedStyle(document.documentElement)
    .getPropertyValue(token)
    .trim();
  const amount = parseFloat(value);
  if (!Number.isFinite(amount) || amount <= 0) return 0;
  return value.endsWith("ms") ? amount : amount * 1000;
}

/** A number that counts from `from` to `to` over a duration token, easing out. */
export function useCountUp(from: number, to: number, token: string): number {
  const [duration] = useState(() => motionMs(token));
  const animate = duration > 0 && from !== to;
  const [value, setValue] = useState(from);

  useEffect(() => {
    if (!animate) return;
    const start = performance.now();
    let frame = 0;
    const tick = (now: number) => {
      const progress = Math.min(1, (now - start) / duration);
      const eased = 1 - (1 - progress) ** 3;
      setValue(Math.round(from + (to - from) * eased));
      if (progress < 1) frame = requestAnimationFrame(tick);
    };
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [animate, from, to, duration]);

  return animate ? value : to;
}

/**
 * False for the first frame when the token's motion is on, then true: lets
 * a CSS transition run from a starting value to the final one. True from
 * the start when the motion is off.
 */
export function useStarted(token: string): boolean {
  const [animate] = useState(() => motionMs(token) > 0);
  const [started, setStarted] = useState(false);

  useEffect(() => {
    if (!animate) return;
    const frame = requestAnimationFrame(() => setStarted(true));
    return () => cancelAnimationFrame(frame);
  }, [animate]);

  return animate ? started : true;
}

/**
 * Mel's six frames: the celebrate sprite hops in steps(6). Wraps the
 * sprite; does nothing under reduced motion.
 */
export function useMelHop<T extends HTMLElement>(active: boolean) {
  const ref = useRef<T>(null);
  useEffect(() => {
    const duration = motionMs("--dur-level-up");
    if (!active || !duration || !ref.current?.animate) return;
    const animation = ref.current.animate(
      [
        { transform: "translateY(0)" },
        { transform: "translateY(-12px)" },
        { transform: "translateY(0)" },
      ],
      { duration, easing: "steps(6)" },
    );
    return () => animation.cancel();
  }, [active]);
  return ref;
}
