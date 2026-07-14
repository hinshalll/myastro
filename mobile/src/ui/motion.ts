// motion.ts — the prototype's Home.html @keyframes, ported to Reanimated 4 hooks.
// Each returns an animated style you spread onto an <Animated.View>. All honour the OS
// "reduce motion" setting (falls back to the static end-state).
import { useEffect, useState } from "react";
import { AccessibilityInfo } from "react-native";
import {
  useSharedValue, useAnimatedStyle, withRepeat, withTiming, withDelay,
  cancelAnimation, Easing,
} from "react-native-reanimated";

const EASE = Easing.inOut(Easing.ease);
const LINEAR = Easing.linear;
const RISE_BEZIER = Easing.bezier(0.2, 0.85, 0.25, 1);

export function useReduceMotion(): boolean {
  const [reduce, setReduce] = useState(false);
  useEffect(() => {
    let on = true;
    AccessibilityInfo.isReduceMotionEnabled().then((v) => { if (on) setReduce(!!v); });
    const sub = AccessibilityInfo.addEventListener("reduceMotionChanged", (v) => setReduce(!!v));
    return () => { on = false; sub?.remove?.(); };
  }, []);
  return reduce;
}

// ping-pong 0→1→0 loop shared value (floatY / breathe / twinkle / halo / cloudDrift)
function usePingPong(period: number, reduce: boolean) {
  const v = useSharedValue(0);
  useEffect(() => {
    if (reduce) { v.value = 0; return; }
    v.value = withRepeat(withTiming(1, { duration: period * 1000, easing: EASE }), -1, true);
    return () => cancelAnimation(v);
  }, [reduce, period]);
  return v;
}

// one-way 0→1 loop (spin / pulseRing / sheen)
function useSweep(period: number, reduce: boolean) {
  const v = useSharedValue(0);
  useEffect(() => {
    if (reduce) { v.value = 0; return; }
    v.value = withRepeat(withTiming(1, { duration: period * 1000, easing: LINEAR }), -1, false);
    return () => cancelAnimation(v);
  }, [reduce, period]);
  return v;
}

// floatY — gentle vertical bob (translateY 0 → -dist → 0)
export function useFloatY(period = 6, dist = 7) {
  const reduce = useReduceMotion();
  const v = usePingPong(period, reduce);
  return useAnimatedStyle(() => ({ transform: [{ translateY: -dist * v.value }] }));
}

// breathe — scale 1 → 1.07 → 1
export function useBreathe(period = 6) {
  const reduce = useReduceMotion();
  const v = usePingPong(period, reduce);
  return useAnimatedStyle(() => ({ transform: [{ scale: 1 + 0.07 * v.value }] }));
}

// haloBreathe — opacity .5→.82 + scale 1→1.08
export function useHalo(period = 5) {
  const reduce = useReduceMotion();
  const v = usePingPong(period, reduce);
  return useAnimatedStyle(() => ({ opacity: 0.5 + 0.32 * v.value, transform: [{ scale: 1 + 0.08 * v.value }] }));
}

// twinkle — opacity lo→hi
export function useTwinkle(lo = 0.3, hi = 0.95, period = 3) {
  const reduce = useReduceMotion();
  const v = usePingPong(period, reduce);
  return useAnimatedStyle(() => ({ opacity: lo + (hi - lo) * (reduce ? 1 : v.value) }));
}

// cloudDrift — translateX 0 → dist → 0
export function useCloudDrift(period = 30, dist = 26) {
  const reduce = useReduceMotion();
  const v = usePingPong(period, reduce);
  return useAnimatedStyle(() => ({ transform: [{ translateX: dist * v.value }] }));
}

// spinSlow — rotate 0 → 360
export function useSpin(period = 1) {
  const reduce = useReduceMotion();
  const v = useSweep(period, reduce);
  return useAnimatedStyle(() => ({ transform: [{ rotate: `${360 * v.value}deg` }] }));
}

// glowPulse — a soft ring behind a live dot (opacity + scale bloom)
export function useGlowPulse(period = 2.6) {
  const reduce = useReduceMotion();
  const v = usePingPong(period, reduce);
  return useAnimatedStyle(() => ({ opacity: 0.45 + 0.4 * v.value, transform: [{ scale: 1 + 0.28 * v.value }] }));
}

// pulseRing — expanding fade (FAB unread ring): scale 1→2.4, opacity .5→0
export function usePulseRing(period = 1.8) {
  const reduce = useReduceMotion();
  const v = useSweep(period, reduce);
  return useAnimatedStyle(() => ({ opacity: reduce ? 0 : 0.5 * (1 - v.value), transform: [{ scale: 1 + 1.4 * v.value }] }));
}

// sheen — a diagonal highlight sweeping across a tile (translateX)
export function useSheen(travel: number, period = 5) {
  const reduce = useReduceMotion();
  const v = useSweep(period, reduce);
  return useAnimatedStyle(() => ({ opacity: reduce ? 0 : 1, transform: [{ translateX: -travel + 2 * travel * v.value }, { rotate: "18deg" }] }));
}

// riseIn — card entrance: opacity 0→1 + translateY 18→0, staggered by delayMs
export function useRiseIn(delayMs = 0, dist = 18) {
  const reduce = useReduceMotion();
  const v = useSharedValue(0);
  useEffect(() => {
    if (reduce) { v.value = 1; return; }
    v.value = withDelay(delayMs, withTiming(1, { duration: 600, easing: RISE_BEZIER }));
    return () => cancelAnimation(v);
  }, [reduce, delayMs]);
  return useAnimatedStyle(() => ({ opacity: v.value, transform: [{ translateY: dist * (1 - v.value) }] }));
}
