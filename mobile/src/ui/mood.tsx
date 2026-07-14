// mood.tsx — the day's celestial art: MoodSigil (12), MoodEmblem, PhaseMoon, EclipseGlyph.
// Ported from astro.tsx / astro-today.tsx SVG. Paths verbatim.
import React from "react";
import { View } from "react-native";
import Animated from "react-native-reanimated";
import { LinearGradient } from "expo-linear-gradient";
import Svg, { G, Path, Circle, Defs, RadialGradient, Stop, Rect } from "react-native-svg";
import { Mood } from "../theme";
import { aA, shadow } from "./palette";
import { RadialGlow } from "./atoms";
import { useFloatY, useBreathe, useSheen } from "./motion";

const S = "#FFFDF8";

// 12 per-mood celestial sigils (astro.tsx MoodSigil), drawn white on the glossy tile.
export function MoodSigil({ k }: { k: string }) {
  switch (k) {
    case "Settled":
      return (
        <G stroke={S} strokeWidth={1.3} fill="none" strokeLinecap="round" strokeLinejoin="round">
          <Path d="M5.5 12.5 L12 7 L18.5 12.5" />
          <Path d="M7.4 11.4 V17.5 H16.6 V11.4" />
          <Circle cx={12} cy={3.9} r={1} fill={S} stroke="none" />
        </G>
      );
    case "Guarded":
      return (
        <G>
          <Path d="M15.8 5.2 A7 7 0 1 0 17 15.7 A5.3 5.3 0 1 1 15.8 5.2 Z" fill={S} opacity={0.92} />
          <Path d="M4 14.4 H13.5" stroke={S} strokeWidth={1.3} strokeLinecap="round" />
          <Path d="M6 17.4 H15.5" stroke={S} strokeWidth={1.3} strokeLinecap="round" opacity={0.6} />
        </G>
      );
    case "Bold":
      return (
        <G stroke={S} strokeWidth={1.3} fill="none" strokeLinecap="round" strokeLinejoin="round">
          <Path d="M8 15.2 Q12 3.8 16 15.2" />
          <Path d="M10 15.2 Q12 9 14 15.2" />
          <Path d="M6.4 17.6 H17.6" />
        </G>
      );
    case "Tender":
      return (
        <G stroke={S} strokeWidth={1.3} fill="none" strokeLinecap="round" strokeLinejoin="round">
          <Path d="M12 4 C12 4 6.6 11 6.6 14.6 A5.4 5.4 0 0 0 17.4 14.6 C17.4 11 12 4 12 4 Z" />
          <Path d="M9.5 14.7 A2.6 2.6 0 0 0 12 17.1" opacity={0.65} />
        </G>
      );
    case "Restless":
      return (
        <G>
          <Circle cx={15.2} cy={8.8} r={2.6} fill={S} />
          <Path d="M13 10.8 L5 18" stroke={S} strokeWidth={1.3} strokeLinecap="round" />
          <Path d="M15.6 12 L9.6 18" stroke={S} strokeWidth={1.3} strokeLinecap="round" opacity={0.6} />
          <Path d="M11 9.8 L6.2 14.4" stroke={S} strokeWidth={1.3} strokeLinecap="round" opacity={0.45} />
        </G>
      );
    case "Capable":
      return (
        <G stroke={S} strokeWidth={1.3} fill="none" strokeLinecap="round" strokeLinejoin="round">
          <Path d="M4 17.4 L9.4 9 L13 14 L16 10 L20 17.4 Z" />
          <Circle cx={16.4} cy={5.4} r={1} fill={S} stroke="none" />
        </G>
      );
    case "Warm":
      return (
        <G stroke={S} strokeWidth={1.3} fill="none" strokeLinecap="round" strokeLinejoin="round">
          <Circle cx={12} cy={12} r={3.5} />
          <Path d="M12 3.6 V6 M12 18 V20.4 M3.6 12 H6 M18 12 H20.4 M6.2 6.2 L7.8 7.8 M16.2 16.2 L17.8 17.8 M17.8 6.2 L16.2 7.8 M7.8 16.2 L6.2 17.8" />
        </G>
      );
    case "Deep":
      return (
        <G fill="none" stroke={S} strokeWidth={1.3}>
          <Circle cx={12} cy={12} r={8} opacity={0.3} />
          <Circle cx={12} cy={12} r={5.2} opacity={0.55} />
          <Circle cx={12} cy={12} r={2.6} opacity={0.85} />
          <Circle cx={12} cy={12} r={1.2} fill={S} stroke="none" />
        </G>
      );
    case "Wandering":
      return (
        <G>
          <Path d="M4.5 16 C7.5 16 7.5 8 10.5 8 C13.5 8 13.5 16 16.5 16 C18.5 16 18.5 12.5 19.4 12.2" stroke={S} strokeWidth={1.3} fill="none" strokeLinecap="round" />
          <Circle cx={19.4} cy={12.1} r={1} fill={S} stroke="none" />
        </G>
      );
    case "Driven":
      return (
        <G stroke={S} strokeWidth={1.3} fill="none" strokeLinecap="round" strokeLinejoin="round">
          <Path d="M12 18 V7" />
          <Path d="M7.6 11.4 L12 6.4 L16.4 11.4" />
          <Circle cx={12} cy={4} r={0.9} fill={S} stroke="none" />
        </G>
      );
    case "Upbeat":
      return (
        <G stroke={S} strokeWidth={1.3} fill="none" strokeLinecap="round" strokeLinejoin="round">
          <Path d="M12 5 C12.6 9.5 14.5 11.4 19 12 C14.5 12.6 12.6 14.5 12 19 C11.4 14.5 9.5 12.6 5 12 C9.5 11.4 11.4 9.5 12 5 Z" />
          <Circle cx={18.4} cy={6} r={0.8} fill={S} stroke="none" />
          <Circle cx={6} cy={17.6} r={0.7} fill={S} stroke="none" opacity={0.7} />
        </G>
      );
    case "Quiet":
      return (
        <G>
          <Path d="M14.5 5 A7.4 7.4 0 1 0 14.5 19 A9.2 9.2 0 0 1 14.5 5 Z" fill={S} />
          <Circle cx={7} cy={7} r={0.8} fill={S} />
        </G>
      );
    default:
      return (
        <G stroke={S} strokeWidth={1.3} fill="none" strokeLinecap="round" strokeLinejoin="round">
          <Path d="M6 15 L12 8 L18 14" />
          <Circle cx={12} cy={8} r={1.6} fill={S} stroke="none" />
        </G>
      );
  }
}

// glossy celestial emblem — the day's glyph tile, float + sheen + breathing sigil.
export function MoodEmblem({ mood, size = 60, radius = 18 }: { mood: Mood; size?: number; radius?: number }) {
  const { accent, accentDeep, glow } = mood;
  const floatA = useFloatY(5);
  const breatheA = useBreathe(mood.feel?.breathe || 6);
  const sheenA = useSheen(size, 5);
  const sigilSize = size * 0.66;
  return (
    <Animated.View style={[{ width: size, height: size }, floatA]}>
      {/* halo */}
      <RadialGlow color={glow} size={size + 12} opacity={0.4} style={{ position: "absolute", left: -6, top: -6 }} />
      {/* tile — outer view holds the soft rounded shadow (no clipping); inner clips the gloss */}
      <View style={{ width: size, height: size, borderRadius: radius, backgroundColor: accentDeep, ...shadow({ y: 8, blur: 22, opacity: 0.5, color: accentDeep, elevation: 6 }) } as any}>
        <View style={{ width: size, height: size, borderRadius: radius, overflow: "hidden" }}>
          <LinearGradient colors={[glow, accent, accentDeep]} locations={[0, 0.55, 1]} start={{ x: 0.15, y: 0 }} end={{ x: 0.85, y: 1 }} style={{ position: "absolute", inset: 0 } as any} />
          {/* top white highlight */}
          <View style={{ position: "absolute", top: 0, left: 0, right: 0, height: "46%" }}>
            <LinearGradient colors={[aA("#FFF", 0.45), aA("#FFF", 0)]} start={{ x: 0, y: 0 }} end={{ x: 0, y: 1 }} style={{ flex: 1 }} />
          </View>
          {/* sheen sweep */}
          <Animated.View style={[{ position: "absolute", top: -size * 0.3, bottom: -size * 0.3, width: size * 0.5 }, sheenA]}>
            <LinearGradient colors={["transparent", aA("#FFF", 0.35), "transparent"]} start={{ x: 0, y: 0 }} end={{ x: 1, y: 0 }} style={{ flex: 1 }} />
          </Animated.View>
          {/* sigil */}
          <View style={{ position: "absolute", inset: 0, alignItems: "center", justifyContent: "center" } as any}>
            <Animated.View style={[{ width: sigilSize, height: sigilSize }, breatheA]}>
              <Svg width="100%" height="100%" viewBox="0 0 24 24" fill="none"><MoodSigil k={mood.key} /></Svg>
            </Animated.View>
          </View>
        </View>
      </View>
    </Animated.View>
  );
}

// a small moon showing a phase (waxing gibbous demo): lit disc + offset soft shadow
export function PhaseMoon({ mood, size = 46 }: { mood: Mood; size?: number }) {
  const { moon, accentDeep } = mood;
  const body = moon || "#EAE0CC";
  const r = size / 2;
  const idB = React.useRef("pm" + Math.random().toString(36).slice(2, 8)).current;
  const idS = idB + "s";
  return (
    <View style={{ width: size, height: size, alignItems: "center", justifyContent: "center" }}>
      {/* soft round moonglow (was a boxShadow that squared off on native) */}
      <RadialGlow color="#FFF6DC" size={size * 1.85} opacity={0.5} style={{ position: "absolute", left: -size * 0.42, top: -size * 0.42 }} />
      <Svg width={size} height={size}>
        <Defs>
          <RadialGradient id={idB} cx="38%" cy="32%" r="70%">
            <Stop offset="0" stopColor="#FFFDF6" />
            <Stop offset="0.6" stopColor={body} />
            <Stop offset="1" stopColor="#D8CAB0" />
          </RadialGradient>
          <RadialGradient id={idS} cx="78%" cy="50%" r="62%">
            <Stop offset="0.4" stopColor="rgba(20,24,46,0)" />
            <Stop offset="0.72" stopColor="rgba(20,24,46,0.5)" />
          </RadialGradient>
        </Defs>
        <Circle cx={r} cy={r} r={r} fill={`url(#${idB})`} />
        <Circle cx={r * 0.44} cy={r * 0.72} r={r * 0.11} fill={aA(accentDeep, 0.12)} />
        <Circle cx={r * 1.16} cy={r * 1.3} r={r * 0.09} fill={aA(accentDeep, 0.1)} />
        <Circle cx={r} cy={r} r={r} fill={`url(#${idS})`} />
      </Svg>
    </View>
  );
}

// solar vs lunar eclipse glyphs (astro-today.tsx EclipseGlyph)
export function EclipseGlyph({ type, size = 24 }: { type: string; size?: number }) {
  const idSun = React.useRef("es" + Math.random().toString(36).slice(2, 8)).current;
  const idMoon = idSun + "m";
  if (type === "solar") {
    return (
      <Svg width={size} height={size} viewBox="0 0 24 24" fill="none">
        <Defs>
          <RadialGradient id={idSun} cx="46%" cy="44%" r="62%">
            <Stop offset="0" stopColor="#FFF6DC" />
            <Stop offset="0.6" stopColor="#FFD684" />
            <Stop offset="1" stopColor="#F4A83C" />
          </RadialGradient>
        </Defs>
        <G stroke="#FFECB8" strokeWidth={1.5} strokeLinecap="round" opacity={0.92}>
          <Path d="M12 1.6v2.1" /><Path d="M12 20.3v2.1" /><Path d="M1.6 12h2.1" /><Path d="M20.3 12h2.1" />
          <Path d="M4.3 4.3l1.5 1.5" /><Path d="M18.2 18.2l1.5 1.5" /><Path d="M4.3 19.7l1.5-1.5" /><Path d="M18.2 5.8l1.5-1.5" />
        </G>
        <Circle cx={12} cy={12} r={7} fill={`url(#${idSun})`} />
        <Circle cx={15.4} cy={9.2} r={6} fill="#2C2A46" />
      </Svg>
    );
  }
  return (
    <Svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <Defs>
        <RadialGradient id={idMoon} cx="40%" cy="38%" r="66%">
          <Stop offset="0" stopColor="#F5F0FC" />
          <Stop offset="1" stopColor="#CEC6E6" />
        </RadialGradient>
      </Defs>
      <Circle cx={12} cy={12} r={8} fill={`url(#${idMoon})`} />
      <Circle cx={16.2} cy={13.2} r={7.6} fill="#B5462F" opacity={0.6} />
      <Circle cx={9.3} cy={9.8} r={1.2} fill="#C7BEDC" opacity={0.85} />
      <Circle cx={10.6} cy={14.4} r={0.9} fill="#C7BEDC" opacity={0.7} />
    </Svg>
  );
}
