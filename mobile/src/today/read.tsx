// read.tsx — the Read sub-tab cards (astro-today.tsx): EclipseCard, ReadingCard (hero),
// LifeAreas, JournalCard, RitualPill.
import React, { useRef, useState } from "react";
import { View, Text, Pressable } from "react-native";
import Animated, { FadeIn } from "react-native-reanimated";
import { LinearGradient } from "expo-linear-gradient";
import Svg, { Defs, LinearGradient as SvgLinear, Stop, Path, G } from "react-native-svg";
import { Mood, ECLIPSE, READ_CHIPS, PERSONAL_LINES, LIFE_AREAS, MIRROR } from "../theme";
import { INK, INK2, GRAY, WASH, HAIR, aA, sans, serif, mono, cardStyle, shadow } from "../ui/palette";
import { Press, Pill, Label, GlossIcon, RadialGlow } from "../ui/atoms";
import { Icon } from "../ui/Icon";
import { MoodEmblem, EclipseGlyph } from "../ui/mood";
import { useRiseIn } from "../ui/motion";

const GOODC = "#2E7D5B", EASYC = "#B4503E";

// ===== EclipseCard =====
export function EclipseCard({ mood, delay = 0, onOpen, type, onToggleType }: any) {
  const { accent, accentDeep } = mood;
  const riseA = useRiseIn(delay);
  const t = type || ECLIPSE.type;
  const tile = t === "solar" ? ["#F6B24A", "#CE7C1B"] : ["#8385C8", "#4B4B88"];
  return (
    <Animated.View style={[{ marginBottom: 14 }, riseA]}>
      <Press scale={0.99} onPress={onOpen}>
        <View style={cardStyle({ paddingVertical: 14, paddingHorizontal: 16, flexDirection: "row", alignItems: "center", gap: 13, borderColor: aA(accent, 0.25) })}>
          <Pressable onPress={onToggleType}>
            <View>
              <GlossIcon c1={tile[0]} c2={tile[1]} size={42} radius={13}><EclipseGlyph type={t} size={24} /></GlossIcon>
              <View style={{ position: "absolute", right: -5, bottom: -5, width: 18, height: 18, borderRadius: 999, backgroundColor: "#FFF", borderWidth: 1, borderColor: HAIR, alignItems: "center", justifyContent: "center", ...shadow({ y: 1, blur: 4, opacity: 0.22, elevation: 2 }) } as any}>
                <Icon n="sync" s={11} c={accentDeep} sw={2} />
              </View>
            </View>
          </Pressable>
          <View style={{ flex: 1 }}>
            <Label c={aA(accentDeep, 0.9)}>Heads up</Label>
            <Text style={{ fontFamily: serif(500), fontSize: 17, color: INK, marginTop: 2 }}>A {t} eclipse in {ECLIPSE.inDays} days</Text>
            <Text style={{ fontFamily: sans(400), fontSize: 12.5, color: GRAY, marginTop: 2, lineHeight: 17 }}>{ECLIPSE.short ? ECLIPSE.short[t] : ""}</Text>
          </View>
          <Icon n="chevR" s={17} c={GRAY} />
        </View>
      </Press>
    </Animated.View>
  );
}

// ===== ReadingCard (hero) =====
function Chip({ label, tone }: { label: string; tone: "good" | "easy" }) {
  const c = tone === "good" ? GOODC : EASYC;
  return (
    <View style={{ flexDirection: "row", alignItems: "center", gap: 6, paddingVertical: 6, paddingLeft: 10, paddingRight: 12, borderRadius: 999, backgroundColor: tone === "good" ? "rgba(62,156,122,0.11)" : "rgba(198,90,74,0.09)", borderWidth: 1, borderColor: tone === "good" ? "rgba(62,156,122,0.30)" : "rgba(198,90,74,0.26)" }}>
      <View style={{ width: 5, height: 5, borderRadius: 999, backgroundColor: c }} />
      <Text style={{ fontFamily: sans(700), fontSize: 12.5, color: c }}>{label}</Text>
    </View>
  );
}

export function ReadingCard({ mood, delay = 0, onCycle, onShare, onTiming }: any) {
  const { accent, accentDeep, glow } = mood;
  const riseA = useRiseIn(delay);
  const [whyOpen, setWhyOpen] = useState(false);
  const chips = (READ_CHIPS as any)[mood.key] || { good: [], easy: [] };
  const personal = (PERSONAL_LINES as any)[mood.key];
  return (
    <Animated.View style={[{ marginBottom: 24 }, riseA]}>
      <View style={cardStyle({ padding: 20, overflow: "hidden" })}>
        <LinearGradient colors={["#FFFFFF", aA(glow, 0.07)]} start={{ x: 0.1, y: 0 }} end={{ x: 0.35, y: 1 }} style={{ position: "absolute", top: 0, left: 0, right: 0, bottom: 0 } as any} />
        <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "flex-start" }}>
          <View style={{ flex: 1, paddingRight: 14 }}>
            <View style={{ marginBottom: 9 }}><Label c={aA(accentDeep, 0.9)}>Today's reading</Label></View>
            <Press onPress={onCycle} scale={0.96} style={{ alignSelf: "flex-start" }}>
              <Text style={{ fontFamily: serif(500), fontSize: 48, color: INK, letterSpacing: -1.4, lineHeight: 50 }}>{mood.key}</Text>
            </Press>
          </View>
          <MoodEmblem mood={mood} size={60} />
        </View>
        <Text style={{ fontFamily: serif(400), fontSize: 18, lineHeight: 26, color: INK2, marginTop: 14 }}>{mood.forecast.mood}</Text>
        {personal ? (
          <View style={{ flexDirection: "row", gap: 10, alignItems: "flex-start", marginTop: 14 }}>
            <View style={{ width: 7, height: 7, borderRadius: 999, backgroundColor: accent, marginTop: 7 }} />
            <Text style={{ flex: 1, fontFamily: serif(400, true), fontSize: 15.5, lineHeight: 22, color: INK2 }}>{personal}</Text>
          </View>
        ) : null}
        {/* chip rows */}
        <View style={{ marginTop: 16, paddingTop: 16, borderTopWidth: 1, borderTopColor: HAIR, gap: 12 }}>
          <View style={{ flexDirection: "row", alignItems: "center", gap: 10, flexWrap: "wrap" }}>
            <Text style={{ fontFamily: mono(600), fontSize: 9, letterSpacing: 0.8, textTransform: "uppercase", color: GOODC, width: 50 }}>Good{"\n"}for</Text>
            {chips.good.map((c: string) => <Chip key={c} label={c} tone="good" />)}
          </View>
          <View style={{ flexDirection: "row", alignItems: "center", gap: 10, flexWrap: "wrap" }}>
            <Text style={{ fontFamily: mono(600), fontSize: 9, letterSpacing: 0.8, textTransform: "uppercase", color: EASYC, width: 50 }}>Go{"\n"}easy</Text>
            {chips.easy.map((c: string) => <Chip key={c} label={c} tone="easy" />)}
          </View>
        </View>
        {chips.offDay ? <Text style={{ fontFamily: serif(400, true), fontSize: 14, color: GRAY, marginTop: 12 }}>a low-key day for you, keep it light</Text> : null}
        {/* strongest-window nugget */}
        <Press scale={0.98} onPress={onTiming} style={{ marginTop: 16 }}>
          <View style={{ flexDirection: "row", alignItems: "center", gap: 11, paddingVertical: 12, paddingHorizontal: 14, borderRadius: 14, backgroundColor: aA(accent, 0.07), borderWidth: 1, borderColor: aA(accent, 0.18) }}>
            <Icon n="clock" s={17} c={accentDeep} sw={1.9} />
            <View style={{ flex: 1, flexDirection: "row" }}>
              <Text style={{ fontFamily: sans(700), fontSize: 13, color: INK }}>Strongest window today</Text>
              <Text style={{ fontFamily: sans(700), fontSize: 13, color: accentDeep }}>{"  ·  11:40–12:30"}</Text>
            </View>
            <Icon n="chevR" s={16} c={accentDeep} />
          </View>
        </Press>
        {/* footer */}
        <View style={{ flexDirection: "row", alignItems: "center", gap: 10, marginTop: 14 }}>
          <Press onPress={() => setWhyOpen((v) => !v)} scale={0.97} style={{ flex: 1 }}>
            <View style={{ flexDirection: "row", alignItems: "center", justifyContent: "center", gap: 8, paddingVertical: 13, paddingHorizontal: 18, borderRadius: 14, backgroundColor: INK, ...shadow({ y: 7, blur: 18, opacity: 0.42, color: INK, elevation: 5 }) } as any}>
              <Text style={{ fontFamily: sans(700), fontSize: 13.5, color: "#FFF", letterSpacing: 0.2 }}>{whyOpen ? "close" : "why this?"}</Text>
              <View style={{ transform: [{ rotate: whyOpen ? "180deg" : "0deg" }] }}><Icon n="chevD" s={14} c="#FFF" /></View>
            </View>
          </Press>
          <Press scale={0.94} onPress={onShare}>
            <Pill radius={14} style={{ width: 48, height: 48, alignItems: "center", justifyContent: "center" }}>
              <Icon n="share" s={18} c={INK} />
            </Pill>
          </Press>
        </View>
        {whyOpen ? (
          <Animated.View entering={FadeIn.duration(280)} style={{ marginTop: 14 }}>
            <View style={{ padding: 15, borderRadius: 14, backgroundColor: WASH, borderWidth: 1, borderColor: HAIR }}>
              <Text style={{ fontFamily: serif(400), fontSize: 15.5, lineHeight: 24, color: INK2 }}>{mood.forecast.why}</Text>
            </View>
          </Animated.View>
        ) : null}
      </View>
    </Animated.View>
  );
}

// ===== LifeAreas =====
export function LifeAreas({ mood, delay = 0, onArea }: any) {
  const riseA = useRiseIn(delay);
  const la = (LIFE_AREAS as any)[mood.key] || {};
  const rows = [
    { k: "Love", v: la.love, c1: "#E48AA6", c2: "#C55C7E", ic: "heart" },
    { k: "Work", v: la.work, c1: "#6E86C4", c2: "#4C63A0", ic: "work" },
    { k: "Money", v: la.money, c1: "#5FA97E", c2: "#3E8060", ic: "coin" },
  ];
  return (
    <Animated.View style={[{ marginBottom: 24 }, riseA]}>
      <View style={{ marginBottom: 10 }}><Label>Today across your life</Label></View>
      <View style={cardStyle({ padding: 6 })}>
        {rows.map((r, i) => (
          <Press key={r.k} scale={0.985} onPress={() => onArea(r.k)}>
            <View style={{ flexDirection: "row", alignItems: "center", gap: 13, padding: 12, borderTopWidth: i ? 1 : 0, borderTopColor: HAIR }}>
              <GlossIcon c1={r.c1} c2={r.c2} size={34} radius={11}><Icon n={r.ic} s={16} c="#FFF" sw={1.9} /></GlossIcon>
              <View style={{ width: 46 }}><Text style={{ fontFamily: sans(800), fontSize: 13.5, color: INK }}>{r.k}</Text></View>
              <View style={{ flex: 1 }}><Text style={{ fontFamily: serif(400), fontSize: 14.5, lineHeight: 20, color: INK2 }}>{r.v}</Text></View>
              <Icon n="chevR" s={15} c={GRAY} />
            </View>
          </Press>
        ))}
      </View>
    </Animated.View>
  );
}

// ===== JournalCard (the Mirror) =====
function BookEmblem({ mood }: { mood: Mood }) {
  const { accent, accentDeep, glow } = mood;
  const id = useRef("mir" + Math.random().toString(36).slice(2, 8)).current;
  return (
    <Svg width={56} height={56} viewBox="0 0 28 28" fill="none">
      <Defs>
        <SvgLinear id={id} x1="0" y1="0" x2="1" y2="1">
          <Stop offset="0" stopColor="#FFFDF8" />
          <Stop offset="1" stopColor={aA(glow, 0.55)} />
        </SvgLinear>
      </Defs>
      <Path d="M14 8.5 C11 6.8 8 6.8 5 7.6 L5 20.2 C8 19.4 11 19.4 14 21 Z" fill={`url(#${id})`} stroke={accentDeep} strokeWidth={0.9} strokeLinejoin="round" />
      <Path d="M14 8.5 C17 6.8 20 6.8 23 7.6 L23 20.2 C20 19.4 17 19.4 14 21 Z" fill={`url(#${id})`} stroke={accentDeep} strokeWidth={0.9} strokeLinejoin="round" />
      <Path d="M14 8.5 L14 21" stroke={accentDeep} strokeWidth={0.9} strokeLinecap="round" />
      <G stroke={aA(accentDeep, 0.5)} strokeWidth={0.7} strokeLinecap="round">
        <Path d="M7 10.6 L11.4 9.9" /><Path d="M7 12.8 L11.4 12.1" /><Path d="M7 15 L10.8 14.4" />
        <Path d="M16.6 9.9 L21 10.6" /><Path d="M16.6 12.1 L21 12.8" />
      </G>
      <Path d="M18.4 7 L18.4 15 L19.9 13.4 L21.4 15 L21.4 7 Z" fill={accent} stroke={aA("#FFF", 0.6)} strokeWidth={0.4} />
    </Svg>
  );
}

export function JournalCard({ mood, delay = 0, written, onOpen }: any) {
  const { accent, accentDeep, glow } = mood;
  const riseA = useRiseIn(delay);
  const invite = useRef((MIRROR.invites || ["What's on your mind?"])[0]).current;
  return (
    <Animated.View style={[{ marginBottom: 24 }, riseA]}>
      <Press scale={0.99} onPress={onOpen}>
        <View style={cardStyle({ padding: 22, overflow: "hidden" })}>
          <LinearGradient colors={["#FFFDFB", aA(glow, 0.12)]} start={{ x: 0.1, y: 0 }} end={{ x: 0.9, y: 1 }} style={{ position: "absolute", top: 0, left: 0, right: 0, bottom: 0 } as any} />
          <RadialGlow color={glow} size={160} opacity={0.3} style={{ position: "absolute", right: -26, bottom: -30 }} />
          {/* floating book emblem */}
          <View style={{ position: "absolute", right: 16, bottom: 16 }} pointerEvents="none">
            <View style={{ width: 56, height: 56, alignItems: "center", justifyContent: "center" }}>
              <RadialGlow color={glow} size={80} opacity={0.5} style={{ position: "absolute", left: -12, top: -12 }} />
              <BookEmblem mood={mood} />
            </View>
          </View>
          <View>
            <Label c={aA(accentDeep, 0.9)}>The Mirror</Label>
            {!written ? (
              <>
                <Text style={{ fontFamily: serif(500), fontSize: 24, color: INK, marginTop: 9, letterSpacing: -0.3, maxWidth: 210, lineHeight: 29 }}>{invite}</Text>
                <Text style={{ fontFamily: serif(400, true), fontSize: 14.5, color: aA(accentDeep, 0.85), marginTop: 9 }}>set it down here, just for you</Text>
                <View style={{ marginTop: 16, gap: 9, maxWidth: 200 }}>
                  <View style={{ height: 1.5, borderRadius: 2, backgroundColor: aA(accentDeep, 0.14), width: "82%" }} />
                  <View style={{ height: 1.5, borderRadius: 2, backgroundColor: aA(accentDeep, 0.1), width: "58%" }} />
                </View>
              </>
            ) : (
              <>
                <Text style={{ fontFamily: serif(400, true), fontSize: 19, color: INK, marginTop: 9, maxWidth: 220, lineHeight: 26 }}>You wrote today. I'm holding it for you.</Text>
                <View style={{ flexDirection: "row", alignItems: "center", gap: 5, marginTop: 12 }}>
                  <Text style={{ fontFamily: sans(700), fontSize: 12.5, color: accentDeep }}>add a little more</Text>
                  <Icon n="chevR" s={13} c={accentDeep} />
                </View>
              </>
            )}
          </View>
        </View>
      </Press>
    </Animated.View>
  );
}

// ===== RitualPill =====
export function RitualPill({ mood, delay = 0, onBegin }: any) {
  const { accentDeep } = mood;
  const riseA = useRiseIn(delay);
  return (
    <Animated.View style={[{ marginBottom: 24 }, riseA]}>
      <View style={{ marginBottom: 10 }}><Label>Today's ritual</Label></View>
      <Press scale={0.985} onPress={onBegin}>
        <Pill radius={18} style={{ paddingVertical: 13, paddingHorizontal: 15, flexDirection: "row", alignItems: "center", gap: 13 }}>
          <GlossIcon c1={"#F5B642"} c2={"#C77A1E"}><IconFlame /></GlossIcon>
          <View style={{ flex: 1 }}>
            <Text style={{ fontFamily: sans(800), fontSize: 15.5, color: INK }}>light a lamp at dusk <Text style={{ fontFamily: sans(600), color: GRAY }}>· +2 🪔</Text></Text>
            <Text style={{ fontFamily: sans(400), fontSize: 12.5, color: GRAY, marginTop: 1 }}>breathe slowly for one minute, a good day for Saturn</Text>
          </View>
          <View style={{ flexDirection: "row", alignItems: "center", gap: 5 }}>
            <Text style={{ fontFamily: sans(700), fontSize: 13, color: accentDeep }}>Begin</Text>
            <Icon n="arrowR" s={14} c={accentDeep} sw={2} />
          </View>
        </Pill>
      </Press>
    </Animated.View>
  );
}

// local flame (white) for the ritual gloss tile
import { Flame } from "../ui/Icon";
function IconFlame() { return <Flame s={19} c="#FFF" />; }
