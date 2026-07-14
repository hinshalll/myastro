// LivingSkyHeader.tsx — time-of-day-aware header (astro-today.tsx LivingSkyHeader):
// gradient sky, drifting clouds, twinkling stars, sun/moon, greeting, planetary-hour line.
// Tap the card to preview dawn -> day -> dusk -> night, then back to live.
import React, { useMemo, useState, useRef } from "react";
import { View, Text, Pressable } from "react-native";
import Animated from "react-native-reanimated";
import { LinearGradient } from "expo-linear-gradient";
import Svg, { Defs, RadialGradient, Stop, Circle } from "react-native-svg";
import { Mood, NAME, DATE, HORA_LINE, FESTIVAL } from "../theme";
import { aA, serif, mono, shadow } from "../ui/palette";
import { useRiseIn, useFloatY, useTwinkle, useCloudDrift, useGlowPulse } from "../ui/motion";
import { PhaseMoon } from "../ui/mood";
import { RadialGlow } from "../ui/atoms";

function nowH() { const d = new Date(); return d.getHours() + d.getMinutes() / 60; }
function skyNameFor(h: number) { if (h >= 5 && h < 8) return "dawn"; if (h >= 8 && h < 17) return "day"; if (h >= 17 && h < 20) return "dusk"; return "night"; }

const SKIES: Record<string, any> = {
  dawn: { greet: "Good morning", colors: ["#F9CD9C", "#FBE3C6", "#FDF4E9"], locs: [0, 0.54, 1], ink: "#3A2A18", sub: "#8A6A48", cel: "sun", sunC: ["#FFF6DA", "#FFCD82"], glowC: "rgba(255,193,116,0.68)", stars: 0, clouds: 2 },
  day: { greet: "Good afternoon", colors: ["#A6D0F2", "#CDE5F6", "#EEF6FC"], locs: [0, 0.54, 1], ink: "#25384B", sub: "#5C7793", cel: "sun", sunC: ["#FFFCF0", "#FFE29A"], glowC: "rgba(255,212,116,0.62)", stars: 0, clouds: 3 },
  dusk: { greet: "Good evening", colors: ["#E89A76", "#C489AE", "#9A82C6"], locs: [0, 0.52, 1], ink: "#FFF6EF", sub: "rgba(255,246,239,0.85)", cel: "moon", glowC: "rgba(255,224,188,0.5)", stars: 6, clouds: 1 },
  night: { greet: "Good night", colors: ["#1F2A4E", "#2F3B64", "#424E7A"], locs: [0, 0.52, 1], ink: "#F4EFFA", sub: "rgba(244,239,250,0.8)", cel: "moon", glowC: "rgba(182,192,255,0.42)", stars: 16, clouds: 0 },
};
const SEQ = ["dawn", "day", "dusk", "night"];

function Star({ st, visible }: any) {
  const a = useTwinkle(st.lo, st.hi, st.d);
  if (!visible) return null;
  return <Animated.View style={[{ position: "absolute", left: `${st.x}%`, top: `${st.y}%`, width: st.sz, height: st.sz, borderRadius: 999, backgroundColor: "#FFF" }, a]} />;
}
function Cloud({ cl, visible }: any) {
  const a = useCloudDrift(cl.d, 26);
  if (!visible) return null;
  return <Animated.View style={[{ position: "absolute", top: `${cl.y}%`, left: `${cl.start}%`, width: cl.w, height: cl.w * 0.4, borderRadius: 999, backgroundColor: aA("#FFF", cl.o) }, a]} />;
}
function SunDisc({ sunC, glowC, size = 44 }: any) {
  const id = useRef("sun" + Math.random().toString(36).slice(2, 8)).current;
  return (
    <View style={{ width: size, height: size, alignItems: "center", justifyContent: "center" }}>
      <RadialGlow color={glowC} size={size * 1.9} opacity={0.9} style={{ position: "absolute", left: -size * 0.45, top: -size * 0.45 }} />
      <Svg width={size} height={size}>
        <Defs>
          <RadialGradient id={id} cx="40%" cy="38%" r="62%">
            <Stop offset="0" stopColor={sunC[0]} />
            <Stop offset="0.52" stopColor={sunC[1]} />
            <Stop offset="0.75" stopColor={sunC[1]} stopOpacity={0} />
          </RadialGradient>
        </Defs>
        <Circle cx={size / 2} cy={size / 2} r={size / 2} fill={`url(#${id})`} />
      </Svg>
    </View>
  );
}

export function LivingSkyHeader({ mood, delay = 0 }: { mood: Mood; delay?: number }) {
  const riseA = useRiseIn(delay);
  const floatA = useFloatY(7);
  const dotA = useGlowPulse(2.6);
  const liveName = useMemo(() => skyNameFor(nowH()), []);
  const [ov, setOv] = useState<string | null>(null);
  const name = ov || liveName;
  const sky = SKIES[name];
  const dark = name === "night" || name === "dusk";
  const greet = name === "day" && !ov && nowH() < 12 ? "Good morning" : sky.greet;

  const stars = useMemo(() => { let s = 7; const r = () => { s = (s * 9301 + 49297) % 233280; return s / 233280; }; return Array.from({ length: 18 }, () => ({ x: r() * 100, y: r() * 60, sz: 1 + r() * 1.7, lo: 0.12 + r() * 0.2, hi: 0.55 + r() * 0.45, d: 2.4 + r() * 3 })); }, []);
  const clouds = useMemo(() => { let s = 41; const r = () => { s = (s * 9301 + 49297) % 233280; return s / 233280; }; return Array.from({ length: 3 }, (_, i) => ({ y: 8 + r() * 30, w: 56 + r() * 44, o: 0.4 + r() * 0.4, d: 34 + r() * 22, start: 4 + r() * 60 })); }, []);

  const cycle = () => { const nn = SEQ[(SEQ.indexOf(name) + 1) % 4]; setOv(nn === liveName ? null : nn); };

  return (
    <Animated.View style={riseA}>
      <Pressable onPress={cycle}>
        {/* outer wrapper carries the soft rounded shadow (no clip); inner clips the sky */}
        <View style={{ borderRadius: 26, backgroundColor: sky.colors[0], ...shadow({ y: 12, blur: 30, opacity: 0.24, elevation: 5 }) } as any}>
        <View style={{ borderRadius: 26, overflow: "hidden", paddingHorizontal: 18, paddingTop: 18, paddingBottom: 20 } as any}>
          <LinearGradient colors={sky.colors} locations={sky.locs} start={{ x: 0.1, y: 0 }} end={{ x: 0.35, y: 1 }} style={{ position: "absolute", top: 0, left: 0, right: 0, bottom: 0 } as any} />
          {/* scene */}
          <View style={{ position: "absolute", top: 0, left: 0, right: 0, bottom: 0, overflow: "hidden" }} pointerEvents="none">
            {stars.map((st, i) => <Star key={i} st={st} visible={dark && i < sky.stars} />)}
            {clouds.map((cl, i) => <Cloud key={i} cl={cl} visible={i < sky.clouds} />)}
            <Animated.View style={[{ position: "absolute", right: 18, top: 22 }, floatA]}>
              {sky.cel === "moon" ? <PhaseMoon mood={mood} size={44} /> : <SunDisc sunC={sky.sunC} glowC={sky.glowC} size={44} />}
            </Animated.View>
          </View>
          {/* greeting */}
          <View style={{ marginTop: 22 }}>
            <Text style={{ fontFamily: mono(600), fontSize: 10.5, letterSpacing: 1.6, textTransform: "uppercase", color: sky.sub }}>{DATE}</Text>
            <Text style={{ fontFamily: serif(500), fontSize: 27, color: sky.ink, letterSpacing: -0.5, marginTop: 3, maxWidth: 216 }}>
              {greet}, <Text style={{ fontFamily: serif(500, true) }}>{NAME}</Text>
            </Text>
            {FESTIVAL && (
              <View style={{ alignSelf: "flex-start", flexDirection: "row", alignItems: "center", gap: 6, marginTop: 9, paddingVertical: 5, paddingHorizontal: 12, borderRadius: 999, backgroundColor: aA("#FFF", dark ? 0.18 : 0.55) }}>
                <Text style={{ fontSize: 12 }}>🪔</Text>
                <Text style={{ fontFamily: serif(500, true), fontSize: 14, color: sky.ink }}>{FESTIVAL}</Text>
              </View>
            )}
            {HORA_LINE ? (
              <View style={{ flexDirection: "row", alignItems: "center", gap: 7, marginTop: 10 }}>
                <View style={{ width: 10, height: 10, alignItems: "center", justifyContent: "center" }}>
                  <Animated.View style={[{ position: "absolute", width: 10, height: 10, borderRadius: 999, backgroundColor: aA(!dark ? "#3E9C7A" : "#8FE0BF", 0.5) }, dotA]} />
                  <View style={{ width: 6, height: 6, borderRadius: 999, backgroundColor: !dark ? "#3E9C7A" : "#8FE0BF" }} />
                </View>
                <Text style={{ fontFamily: serif(400, true), fontSize: 15, lineHeight: 21, color: sky.sub, maxWidth: 224 }}>{HORA_LINE}</Text>
              </View>
            ) : null}
          </View>
        </View>
        </View>
      </Pressable>
    </Animated.View>
  );
}
