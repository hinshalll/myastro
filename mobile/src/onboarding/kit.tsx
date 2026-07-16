// kit.tsx — the onboarding design kit: the violet palette `P`, motion helpers
// (Rise entrance + useRaf frame loop), and the shared scaffold every step reuses
// (OScreen, StepChrome, PrimaryButton, Field, PasswordField, Dropdown, SoftChip,
// ProviderButton, TextLink). Ported 1:1 from the ASTROLO web prototype
// (screens/onboarding/onboarding.tsx). Reuses the app's fonts + shadow + Press so the
// design system is shared, not forked.
//
// RN port notes vs the web prototype:
//  - div->View, span/text->Text, input->TextInput, onClick->onPress, :active->Press scale.
//  - CSS lineHeight multipliers (1.1) become absolute px (fontSize*1.1) — RN needs numbers.
//  - transform strings become RN transform arrays.
//  - the Dropdown panel + place list open in a real Modal so they're never clipped by an
//    animated parent (the prototype's fixed-overlay trick).
//  - the page stays WHITE; violet is the single accent.
import React, { useEffect, useMemo, useRef, useState } from "react";
import {
  View, Text, TextInput, Pressable, ScrollView, Modal, Platform,
  KeyboardAvoidingView, ViewStyle,
} from "react-native";
import Animated, {
  useSharedValue, useAnimatedStyle, withTiming, withDelay, withRepeat, cancelAnimation, Easing,
} from "react-native-reanimated";
import { LinearGradient } from "expo-linear-gradient";
import Svg, { Path, Circle, Line } from "react-native-svg";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { sans, serif, mono, shadow, aA } from "../ui/palette";
import { Press, RadialGlow } from "../ui/atoms";
import { useReduceMotion, useSheen } from "../ui/motion";

// ---- palette: ASTROLO-clean white + a single soft violet accent (matches prototype P) ----
export const P = {
  paper: "#FFFFFF", paperHi: "#FBFAFC", paperLo: "#F4F4F6", card: "#FFFFFF",
  ink: "#0C0B0A", inkSoft: "#3A3733", inkMid: "#6A655D", inkFaint: "#9A958C",
  violet: "#6E4FA0", violetDeep: "#48306F", violetGlow: "#C4A9E8", plum: "#8A5A9E",
  gold: "#AE863F", goldGlow: "#E9D199",
  line: "rgba(12,11,10,0.10)", hair: "rgba(12,11,10,0.07)", field: "#F6F5F7",
  good: "#2E9C7E", warn: "#C2724E",
  // Opaque twins of aA(violet, 0.09) / aA(violet, 0.07) over the white page. Identical to the
  // eye, but NOT translucent — see androidLift() for why that matters on Android.
  violetTint: "#F2EFF6", violetTintSoft: "#F5F3F8",
};

// ---- Android elevation guard -------------------------------------------------------
// `elevation` is the ONLY part of shadow() that Android actually paints, and around these
// controls it causes two real bugs:
//  1) Toggling it on a View that WRAPS a TextInput re-attaches that view's native ViewGroup,
//     which clears the focused EditText and dismisses the keyboard. That was the "tap the box,
//     it highlights, then deselects in under a second, keyboard never opens" blocker: on tap
//     the only non-paint change in <Field> was this shadow. Web is unaffected because shadow()
//     returns boxShadow there (paint only), which is why focus held fine in the browser.
//  2) Under a TRANSLUCENT background its shadow bleeds through the view as a grey inner
//     rectangle. That was the weird box inside the selected gender chip.
// So on Android we skip the lift entirely; the violet border + tint already read as selected
// or focused. iOS and web keep the soft glow.
const ANDROID = Platform.OS === "android";
export function androidLift(opts: Parameters<typeof shadow>[0]) {
  return ANDROID ? null : shadow(opts);
}

// ================================ MOTION ============================================

// Rise — the staggered entrance: opacity 0->1 + translateY(dist->0) after `delay` ms.
// The visible end-state is the base, so reduced-motion just shows content. (prototype
// useEntrance + rise() combined into one wrapper — one <Rise> per element.)
export function Rise({
  delay = 0, dist = 14, style, children,
}: { delay?: number; dist?: number; style?: ViewStyle | ViewStyle[]; children: React.ReactNode }) {
  const reduce = useReduceMotion();
  const v = useSharedValue(0);
  useEffect(() => {
    if (reduce) { v.value = 1; return; }
    v.value = withDelay(delay, withTiming(1, { duration: 520, easing: Easing.out(Easing.cubic) }));
    return () => cancelAnimation(v);
  }, [reduce, delay]);
  const a = useAnimatedStyle(() => ({ opacity: v.value, transform: [{ translateY: (1 - v.value) * dist }] }));
  return <Animated.View style={[style as any, a]}>{children}</Animated.View>;
}

// ---- ambient starfield ------------------------------------------------------------
// A handful of stars breathing slowly under the crown glow, so the onboarding feels like the
// sky without turning into a screensaver. Positions are seeded (never re-shuffle on a render)
// and each star's opacity loops on the UI thread, so the whole layer costs zero re-renders.
function Star({ x, y, size, delay, dur, gold }: any) {
  const reduce = useReduceMotion();
  const v = useSharedValue(0.5);
  useEffect(() => {
    if (reduce) { v.value = 0.5; return; }
    v.value = withDelay(delay, withRepeat(withTiming(1, { duration: dur, easing: Easing.inOut(Easing.sin) }), -1, true));
    return () => cancelAnimation(v);
  }, [reduce]);
  const a = useAnimatedStyle(() => ({ opacity: 0.14 + v.value * 0.4 }));
  return (
    <Animated.View style={[{ position: "absolute", left: `${x}%`, top: y, width: size, height: size, borderRadius: 999,
      backgroundColor: gold ? P.goldGlow : P.violetGlow }, a]} />
  );
}
export function StarField({ height = 330, n = 16 }: { height?: number; n?: number }) {
  const stars = useMemo(() => {
    let s = 7; const r = () => { s = (s * 9301 + 49297) % 233280; return s / 233280; };
    return Array.from({ length: n }, (_, i) => ({
      x: 4 + r() * 92, y: 20 + r() * (height - 40), size: 1.6 + r() * 2.2,
      delay: r() * 2800, dur: 1700 + r() * 2400, gold: i % 4 === 0,
    }));
  }, [n, height]);
  return (
    <View pointerEvents="none" style={{ position: "absolute", top: 0, left: 0, right: 0, height }}>
      {stars.map((s, i) => <Star key={i} {...s} />)}
    </View>
  );
}

// useRaf — run a callback every animation frame (drives the Reveal wheel). Works on both
// web and native via the global requestAnimationFrame. `active` gates it on/off.
export function useRaf(cb: (dt: number, t: number) => void, active = true) {
  const cbRef = useRef(cb); cbRef.current = cb;
  useEffect(() => {
    if (!active) return;
    let raf = 0; let last = Date.now();
    const loop = () => {
      const now = Date.now(); const dt = now - last; last = now;
      cbRef.current(dt, now);
      raf = requestAnimationFrame(loop);
    };
    raf = requestAnimationFrame(loop);
    return () => cancelAnimationFrame(raf);
  }, [active]);
}

// ================================ SVG GLYPHS ========================================
export function Chevron({ dir = "down", size = 16, color = P.inkFaint, sw = 1.9 }: any) {
  const d = dir === "down" ? "M6 9.5 12 15l6-5.5" : dir === "up" ? "M6 14.5 12 9l6 5.5"
    : dir === "left" ? "M15 6 9 12l6 6" : "M9 6l6 6-6 6";
  return (
    <Svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <Path d={d} stroke={color} strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round" />
    </Svg>
  );
}
export function CheckMark({ size = 16, color = P.violet, sw = 2 }: any) {
  return (
    <Svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <Path d="M5 12.5 9.5 17 19 7" stroke={color} strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round" />
    </Svg>
  );
}

// ================================ SCAFFOLD ==========================================

// OScreen — the white page wrapper: soft top violet crown glow + optional scroll +
// keyboard avoidance. Every step lives inside one.
export function OScreen({
  children, crown = 0.16, scroll = false, keyboard = false, stars = false,
}: { children: React.ReactNode; crown?: number; scroll?: boolean; keyboard?: boolean; stars?: boolean }) {
  const body = (
    <View style={{ flex: 1, backgroundColor: P.paper }}>
      {/* ambient top crown — a whisper of violet, page stays white */}
      <View pointerEvents="none" style={{ position: "absolute", top: -140, left: 0, right: 0, alignItems: "center" }}>
        <RadialGlow color={P.violetGlow} size={520} opacity={crown} />
      </View>
      {stars ? <StarField /> : null}
      {scroll ? (
        <ScrollView style={{ flex: 1 }} contentContainerStyle={{ flexGrow: 1 }} keyboardShouldPersistTaps="handled" showsVerticalScrollIndicator={false}>
          {children}
        </ScrollView>
      ) : (
        <View style={{ flex: 1 }}>{children}</View>
      )}
    </View>
  );
  // iOS only: it's the one platform that needs manual avoidance. On Android the OS already
  // resizes the window for the keyboard, so KeyboardAvoidingView had no behavior to apply and
  // did nothing there except re-render the screen on every keyboard event.
  if (keyboard && Platform.OS === "ios") {
    return <KeyboardAvoidingView style={{ flex: 1 }} behavior="padding">{body}</KeyboardAvoidingView>;
  }
  return body;
}

// BackArrow — round chevron-left, top-left of every step.
export function BackArrow({ onPress }: { onPress?: () => void }) {
  return (
    <Press onPress={onPress} scale={0.9} hitSlop={8}
      style={{ width: 40, height: 40, marginLeft: -8, borderRadius: 999, alignItems: "center", justifyContent: "center" }}>
      <Chevron dir="left" size={22} color={P.ink} />
    </Press>
  );
}

// StepChrome — back arrow + "STEP n OF 5" mono label + a 5-segment progress bar.
export function StepChrome({ step, total = 5, onBack }: { step: number; total?: number; onBack?: () => void }) {
  return (
    <View style={{ paddingTop: 8 }}>
      <View style={{ flexDirection: "row", alignItems: "center", justifyContent: "space-between", minHeight: 40 }}>
        {onBack ? <BackArrow onPress={onBack} /> : <View style={{ width: 32 }} />}
        <Text style={{ fontFamily: mono(500), fontSize: 10.5, letterSpacing: 2, textTransform: "uppercase", color: P.inkFaint }}>
          Step {step} of {total}
        </Text>
      </View>
      <View style={{ flexDirection: "row", gap: 5, marginTop: 12 }}>
        {Array.from({ length: total }).map((_, i) => (
          <View key={i} style={{ flex: 1, height: 3, borderRadius: 2, backgroundColor: i < step ? P.ink : P.line }} />
        ))}
      </View>
    </View>
  );
}

// PrimaryButton — the black glossy CTA: rounded-rect 16 (NOT a pill), soft shadow, a slow
// diagonal sheen. Disabled -> muted, no press, no sheen.
export function PrimaryButton({ label, onPress, disabled = false }: { label: string; onPress?: () => void; disabled?: boolean }) {
  const sheen = useSheen(230, 5.5);
  if (disabled) {
    return (
      <View style={{ width: "100%", paddingVertical: 17, borderRadius: 16, alignItems: "center", backgroundColor: P.paperLo, borderWidth: 1, borderColor: P.line }}>
        <Text style={{ fontFamily: sans(700), fontSize: 16, letterSpacing: 0.3, color: P.inkFaint }}>{label}</Text>
      </View>
    );
  }
  return (
    <Press onPress={onPress} scale={0.975} style={{ width: "100%", borderRadius: 16, backgroundColor: P.ink, ...shadow({ y: 12, blur: 30, opacity: 0.42, color: P.ink, elevation: 6 }) }}>
      {/* inner clips the sheen; outer casts the (rounded) shadow */}
      <View style={{ borderRadius: 16, overflow: "hidden", paddingVertical: 17, alignItems: "center", justifyContent: "center", borderWidth: 1, borderColor: aA("#FFFFFF", 0.06) }}>
        <LinearGradient colors={["#2A2724", P.ink]} start={{ x: 0, y: 0 }} end={{ x: 0, y: 1 }} style={{ position: "absolute", top: 0, left: 0, right: 0, bottom: 0 }} />
        {/* top inner highlight */}
        <View pointerEvents="none" style={{ position: "absolute", top: 0, left: 0, right: 0, height: 1, backgroundColor: aA("#FFFFFF", 0.14) }} />
        {/* MOTION: slow diagonal sheen sweep */}
        <Animated.View pointerEvents="none" style={[{ position: "absolute", top: -30, bottom: -30, width: 90, backgroundColor: aA("#FFFFFF", 0.10) }, sheen]} />
        <Text style={{ fontFamily: sans(700), fontSize: 16, letterSpacing: 0.3, color: "#FBFAF8" }}>{label}</Text>
      </View>
    </Press>
  );
}

// TextLink — a quiet text button.
export function TextLink({ label, onPress, color = P.inkMid, strong = false }: any) {
  return (
    <Press onPress={onPress} scale={0.96} hitSlop={8} style={{ padding: 6, alignSelf: "center" }}>
      <Text style={{ fontFamily: sans(strong ? 600 : 500), fontSize: 14, color }}>{label}</Text>
    </Press>
  );
}

// SoftChip — selectable pill chip (gender, part-of-day). Active = violet-tinted.
export function SoftChip({ label, sub, active, onPress, grow = false }: any) {
  return (
    <Press onPress={onPress} scale={0.96}
      style={{ flexGrow: grow ? 1 : 0, flexBasis: grow ? 0 : "auto", paddingVertical: sub ? 12 : 10, paddingHorizontal: 18, borderRadius: 14, alignItems: "center",
        backgroundColor: active ? P.violetTint : P.paper, borderWidth: 1.5, borderColor: active ? P.violet : P.line,
        ...(active ? androidLift({ y: 6, blur: 18, opacity: 0.28, color: P.violet, elevation: 2 }) : null) } as any}>
      <Text style={{ fontFamily: sans(active ? 700 : 500), fontSize: 15, color: active ? P.violetDeep : P.inkSoft }}>{label}</Text>
      {sub ? <Text style={{ fontFamily: sans(500), fontSize: 11.5, color: active ? aA(P.violetDeep, 0.7) : P.inkFaint, marginTop: 2 }}>{sub}</Text> : null}
    </Press>
  );
}

// Field — text input with a floating mono label + a violet focus ring.
export function Field({
  value, onChange, placeholder, label, autoFocus, onFocus, onBlur, keyboardType, secureTextEntry, autoCapitalize, right,
}: any) {
  const [foc, setFoc] = useState(false);
  return (
    <View style={{ width: "100%" }}>
      {label ? (
        <Text style={{ fontFamily: mono(500), fontSize: 10, letterSpacing: 1.6, textTransform: "uppercase", color: foc ? P.violet : P.inkFaint, marginBottom: 8 }}>{label}</Text>
      ) : null}
      {/* focus ring: colour only on Android (see androidLift) so the keyboard can attach */}
      <View style={{ borderRadius: 14, backgroundColor: foc ? P.paper : P.field, borderWidth: 1.5, borderColor: foc ? P.violet : P.line, paddingHorizontal: 16, flexDirection: "row", alignItems: "center",
        ...(foc ? androidLift({ y: 6, blur: 18, opacity: 0.26, color: P.violet, elevation: 2 }) : null) } as any}>
        <TextInput
          value={value}
          onChangeText={onChange}
          placeholder={placeholder}
          placeholderTextColor={P.inkFaint}
          autoFocus={autoFocus}
          keyboardType={keyboardType}
          secureTextEntry={secureTextEntry}
          autoCapitalize={autoCapitalize}
          onFocus={() => { setFoc(true); onFocus && onFocus(); }}
          onBlur={() => { setFoc(false); onBlur && onBlur(); }}
          style={{ flex: 1, height: 54, fontFamily: sans(500), fontSize: 17, color: P.ink, ...(Platform.OS === "web" ? { outlineWidth: 0 } : null) } as any}
          underlineColorAndroid="transparent"
        />
        {right}
      </View>
    </View>
  );
}

// PasswordField — Field with a show/hide eye toggle.
export function PasswordField({ value, onChange, label, placeholder }: any) {
  const [show, setShow] = useState(false);
  const eye = (
    <Pressable onPress={() => setShow((s) => !s)} hitSlop={8} style={{ padding: 8, marginRight: -6 }}>
      {show ? (
        <Svg width={20} height={20} viewBox="0 0 24 24" fill="none">
          <Path d="M3 3l18 18M10.6 10.7a2 2 0 002.75 2.9M9.7 4.7A9.6 9.6 0 0112 4.5c5.5 0 9.5 5 9.5 7.5 0 1-.7 2.3-1.9 3.5M6 6.2C3.6 7.7 2.5 10.4 2.5 12c0 2.5 4 7.5 9.5 7.5 1.2 0 2.3-.2 3.2-.6" stroke={P.inkFaint} strokeWidth={1.7} strokeLinecap="round" strokeLinejoin="round" />
        </Svg>
      ) : (
        <Svg width={20} height={20} viewBox="0 0 24 24" fill="none">
          <Path d="M2.5 12S6 5.5 12 5.5 21.5 12 21.5 12 18 18.5 12 18.5 2.5 12 2.5 12z" stroke={P.inkFaint} strokeWidth={1.7} strokeLinecap="round" strokeLinejoin="round" />
          <Circle cx="12" cy="12" r="2.5" stroke={P.inkFaint} strokeWidth={1.7} />
        </Svg>
      )}
    </Pressable>
  );
  return <Field label={label} value={value} onChange={onChange} placeholder={placeholder} secureTextEntry={!show} autoCapitalize="none" right={eye} />;
}

// Dropdown — tap opens a real Modal with a scrollable option list (never clipped). Options
// are either {value,label} or plain strings.
export function Dropdown({ value, options, onChange, placeholder, flex = 1 }: any) {
  const [open, setOpen] = useState(false);
  const norm = options.map((o: any) => (typeof o === "object" ? o : { value: o, label: o }));
  const sel = norm.find((o: any) => o.value === value);
  return (
    <View style={{ flex }}>
      <Press onPress={() => setOpen(true)} scale={0.97}
        style={{ height: 54, borderRadius: 14, backgroundColor: open ? P.paper : P.field, borderWidth: 1.5, borderColor: open ? P.violet : P.line, paddingHorizontal: 14, flexDirection: "row", alignItems: "center", justifyContent: "space-between", gap: 6 }}>
        <Text numberOfLines={1} style={{ flex: 1, fontFamily: sans(600), fontSize: 16, color: sel ? P.ink : P.inkFaint }}>{sel ? sel.label : placeholder}</Text>
        <Chevron dir="down" size={16} color={P.inkFaint} />
      </Press>
      <Modal visible={open} transparent animationType="fade" onRequestClose={() => setOpen(false)}>
        <Pressable onPress={() => setOpen(false)} style={{ flex: 1, backgroundColor: aA(P.ink, 0.28), alignItems: "center", justifyContent: "center", padding: 30 }}>
          <Pressable onPress={() => {}} style={{ width: "100%", maxWidth: 360, maxHeight: 380, backgroundColor: P.paper, borderRadius: 16, borderWidth: 1, borderColor: P.line, padding: 6, ...shadow({ y: 20, blur: 60, opacity: 0.3, elevation: 12 }) } as any}>
            <ScrollView showsVerticalScrollIndicator={false}>
              {norm.map((o: any) => {
                const act = o.value === value;
                return (
                  <Pressable key={String(o.value)} onPress={() => { onChange(o.value); setOpen(false); }}
                    style={{ paddingVertical: 12, paddingHorizontal: 12, borderRadius: 10, backgroundColor: act ? aA(P.violet, 0.09) : "transparent", flexDirection: "row", alignItems: "center", justifyContent: "space-between" }}>
                    <Text style={{ fontFamily: sans(act ? 700 : 500), fontSize: 15.5, color: act ? P.violetDeep : P.inkSoft }}>{o.label}</Text>
                    {act ? <CheckMark size={16} color={P.violet} /> : null}
                  </Pressable>
                );
              })}
            </ScrollView>
          </Pressable>
        </Pressable>
      </Modal>
    </View>
  );
}

// ProviderButton — Apple / Google / email auth row with an inline logo.
export function ProviderButton({ kind, label, onPress }: any) {
  const dark = kind === "apple";
  const glyph = kind === "apple" ? (
    <Svg width={19} height={19} viewBox="0 0 24 24"><Path fill="#fff" d="M16.4 12.7c0-2.3 1.9-3.4 2-3.5-1.1-1.6-2.8-1.8-3.4-1.8-1.4-.1-2.8.9-3.5.9s-1.8-.8-3-.8c-1.5 0-2.9.9-3.7 2.3-1.6 2.8-.4 6.9 1.1 9.1.7 1.1 1.6 2.4 2.8 2.3 1.1 0 1.5-.7 2.9-.7s1.7.7 2.9.7c1.2 0 2-1.1 2.7-2.2.5-.8.9-1.6 1.2-2.5-.1 0-2.3-.9-2.3-3.5Zm-2.3-6.5c.6-.8 1.1-1.9.9-3-1 0-2.1.7-2.8 1.5-.6.7-1.1 1.8-1 2.8 1.1.1 2.2-.5 2.9-1.3Z" /></Svg>
  ) : kind === "google" ? (
    <Svg width={18} height={18} viewBox="0 0 24 24">
      <Path fill="#4285F4" d="M22.6 12.2c0-.7-.1-1.4-.2-2H12v3.9h6c-.3 1.4-1.1 2.6-2.3 3.4v2.8h3.7c2.2-2 3.4-5 3.4-8.1Z" />
      <Path fill="#34A853" d="M12 23c3.1 0 5.7-1 7.6-2.8l-3.7-2.8c-1 .7-2.3 1.1-3.9 1.1-3 0-5.5-2-6.4-4.7H1.8v2.9C3.7 20.6 7.5 23 12 23Z" />
      <Path fill="#FBBC05" d="M5.6 13.8c-.2-.7-.4-1.4-.4-2.2s.1-1.5.4-2.2V6.5H1.8C1 8.1.6 9.9.6 11.6s.4 3.5 1.2 5.1l3.8-2.9Z" />
      <Path fill="#EA4335" d="M12 5.4c1.7 0 3.2.6 4.4 1.7l3.3-3.3C17.7 1.9 15.1.9 12 .9 7.5.9 3.7 3.3 1.8 6.5l3.8 2.9C6.5 6.7 9 4.4 12 5.4Z" />
    </Svg>
  ) : kind === "truecaller" ? (
    // Truecaller's mark is a white handset in a rounded blue tile. Unreachable in Expo Go
    // (the native SDK is absent, so isTruecallerAvailable() is false) — present so the dev
    // build has nothing left to draw.
    <Svg width={19} height={19} viewBox="0 0 24 24">
      <Path d="M3 6a3 3 0 0 1 3-3h12a3 3 0 0 1 3 3v12a3 3 0 0 1-3 3H6a3 3 0 0 1-3-3z" fill="#0086FF" />
      <Path d="M9.2 7.1c.3-.3.8-.3 1 .1l.9 1.4c.2.3.1.7-.2.9l-.6.5c-.2.1-.2.3-.1.5.4.9 1.1 1.6 2 2 .2.1.4.1.5-.1l.5-.6c.2-.3.6-.4.9-.2l1.4.9c.4.2.4.7.1 1l-.6.6c-.5.5-1.3.7-2 .4a9 9 0 0 1-4.7-4.7c-.3-.7-.1-1.5.4-2z" fill="#FFF" />
    </Svg>
  ) : (
    <Svg width={19} height={19} viewBox="0 0 24 24" fill="none"><Path d="M3 5.5h18v13H3z" stroke={P.ink} strokeWidth={1.7} /><Path d="m4 7 8 6 8-6" stroke={P.ink} strokeWidth={1.7} strokeLinecap="round" strokeLinejoin="round" /></Svg>
  );
  return (
    <Press onPress={onPress} scale={0.98}
      style={{ width: "100%", height: 54, borderRadius: 16, flexDirection: "row", alignItems: "center", justifyContent: "center", gap: 10,
        backgroundColor: dark ? P.ink : P.paper, borderWidth: dark ? 0 : 1.5, borderColor: P.line,
        ...shadow(dark ? { y: 12, blur: 26, opacity: 0.4, color: P.ink, elevation: 5 } : { y: 6, blur: 16, opacity: 0.14, elevation: 2 }) } as any}>
      {glyph}
      <Text style={{ fontFamily: sans(600), fontSize: 15.5, color: dark ? "#FBFAF8" : P.ink }}>{label}</Text>
    </Press>
  );
}

// tiny helper: safe-area top pad for step screens
export function useTopPad(extra = 0) {
  const insets = useSafeAreaInsets();
  return insets.top + extra;
}
