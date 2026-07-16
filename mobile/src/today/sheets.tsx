// sheets.tsx — Read-tab detail sheets (astro-screens.tsx EclipseSheet + AreaSheet).
//
// WIRED (no demo imports — that is the definition of done, see DEMO_DATA_LEDGER.md).
// Both sheets are pure views over live server data and render nothing without it. The
// backend already computed every field these used to fake: /dashboard/day-alerts returns
// the eclipse date + sutak window, and /dashboard/today returns each life area's
// detail/why/planet/houses. The old version invented all of it.
import React, { useState } from "react";
import { View, Text } from "react-native";
import { LinearGradient } from "expo-linear-gradient";
import { Mood } from "../theme";
import type { LiveArea, LiveEclipse, LiveSandhi } from "../api/today";
import { INK, INK2, GRAY, WASH, aA, sans, serif, mono } from "../ui/palette";
import { Press, Label, GlossIcon } from "../ui/atoms";
import { Icon } from "../ui/Icon";
import { EclipseGlyph } from "../ui/mood";

export function EclipseSheet({ mood, live }: { mood: Mood; live: LiveEclipse }) {
  const { accentDeep } = mood;
  if (!live) return <Empty label="No eclipse coming up" />;
  const t = live.type;
  return (
    <View>
      <Label c={aA(accentDeep, 0.9)}>Heads up</Label>
      <Text style={{ fontFamily: serif(500), fontSize: 24, color: INK, marginTop: 6 }}>
        A {t} eclipse on {live.dateLabel}
      </Text>
      <Text style={{ fontFamily: serif(400), fontSize: 16, lineHeight: 24, color: INK2, marginTop: 12 }}>{live.full}</Text>
      {live.sutakNote ? (
        <View style={{ marginTop: 16, padding: 15, borderRadius: 14, backgroundColor: WASH }}>
          <Label>Caution window</Label>
          <Text style={{ fontFamily: sans(400), fontSize: 13.5, lineHeight: 20, color: INK2, marginTop: 6 }}>{live.sutakNote}</Text>
        </View>
      ) : null}
      {live.sanskrit ? (
        <Text style={{ textAlign: "center", marginTop: 14, fontFamily: serif(400), fontSize: 16, color: GRAY }}>{live.sanskrit}</Text>
      ) : null}
    </View>
  );
}

// The Moon crossing a sign boundary. Real, dated, and at most one a day.
export function SandhiSheet({ mood, live }: { mood: Mood; live: LiveSandhi }) {
  const { accentDeep } = mood;
  if (!live) return <Empty label="No low window today" />;
  return (
    <View>
      <View style={{ flexDirection: "row", alignItems: "center", gap: 12 }}>
        <GlossIcon c1="#8385C8" c2="#4B4B88" size={40} radius={13}><EclipseGlyph type="lunar" size={21} /></GlossIcon>
        <View>
          <Text style={{ fontFamily: serif(500), fontSize: 23, color: INK, letterSpacing: -0.3 }}>A low window today</Text>
          <Text style={{ fontFamily: mono(500), fontSize: 9.5, letterSpacing: 0.5, textTransform: "uppercase", color: GRAY, marginTop: 2 }}>
            {live.fromSign} to {live.toSign}
          </Text>
        </View>
      </View>
      <View style={{ marginTop: 16, padding: 15, borderRadius: 14, backgroundColor: WASH }}>
        <Label c={aA(accentDeep, 0.9)}>When</Label>
        <Text style={{ fontFamily: sans(800), fontSize: 19, color: INK, marginTop: 5 }}>{live.start} to {live.end}</Text>
      </View>
      <Text style={{ fontFamily: serif(400), fontSize: 16, lineHeight: 25, color: INK, marginTop: 16 }}>{live.note}</Text>
      <Text style={{ fontFamily: sans(400), fontSize: 10.5, letterSpacing: 1, textTransform: "uppercase", color: GRAY, marginTop: 18, marginBottom: 7 }}>Why</Text>
      <Text style={{ fontFamily: serif(400), fontSize: 15.5, lineHeight: 25, color: INK2 }}>{live.why}</Text>
      {live.sanskrit ? (
        <Text style={{ textAlign: "center", marginTop: 16, fontFamily: serif(400), fontSize: 16, color: GRAY }}>{live.sanskrit}</Text>
      ) : null}
    </View>
  );
}

const AREA_ART: Record<string, { col: [string, string]; ic: string }> = {
  Love: { col: ["#E48AA6", "#C55C7E"], ic: "heart" },
  Work: { col: ["#6E86C4", "#4C63A0"], ic: "work" },
  Money: { col: ["#5FA97E", "#3E8060"], ic: "coin" },
};

export function AreaSheet({ mood, area, live, onGo }: { mood: Mood; area: string; live: LiveArea | null; onGo: (tab: string) => void }) {
  const { accent, accentDeep, glow } = mood;
  const [why, setWhy] = useState(false);
  const art = AREA_ART[area] || AREA_ART.Love;
  if (!live) return <Empty label={`No reading for ${area} today`} />;
  return (
    <View>
      <View style={{ flexDirection: "row", alignItems: "center", gap: 12 }}>
        <GlossIcon c1={art.col[0]} c2={art.col[1]} size={40} radius={13}><Icon n={art.ic} s={19} c="#FFF" sw={1.9} /></GlossIcon>
        <View style={{ flex: 1 }}>
          <View style={{ flexDirection: "row", alignItems: "baseline", gap: 8 }}>
            <Text style={{ fontFamily: serif(500), fontSize: 23, color: INK, letterSpacing: -0.3 }}>{area} today</Text>
            {live.planet ? (
              <Text style={{ fontFamily: mono(500), fontSize: 10, letterSpacing: 0.7, textTransform: "uppercase", color: accentDeep }}>· {live.planet}</Text>
            ) : null}
          </View>
          {live.houses ? (
            <Text style={{ fontFamily: mono(500), fontSize: 9.5, letterSpacing: 0.5, textTransform: "uppercase", color: GRAY, marginTop: 2 }}>{live.houses} house</Text>
          ) : null}
        </View>
        {/* Only claim the Moon is lighting this area up when it actually is. */}
        {live.inFocus ? (
          <View style={{ paddingVertical: 5, paddingHorizontal: 10, borderRadius: 999, backgroundColor: aA(accent, 0.12), borderWidth: 1, borderColor: aA(accent, 0.3) }}>
            <Text style={{ fontFamily: sans(800), fontSize: 10.5, color: accentDeep, letterSpacing: 0.3 }}>in focus</Text>
          </View>
        ) : null}
      </View>

      <Text style={{ fontFamily: serif(400), fontSize: 17, lineHeight: 25, color: INK, marginTop: 16 }}>{live.line}</Text>
      {live.detail ? (
        <>
          <Text style={{ fontFamily: sans(400), fontSize: 10.5, letterSpacing: 1, textTransform: "uppercase", color: GRAY, marginTop: 18, marginBottom: 7 }}>What it means today</Text>
          <Text style={{ fontFamily: serif(400), fontSize: 15.5, lineHeight: 25, color: INK2 }}>{live.detail}</Text>
        </>
      ) : null}

      {live.why ? (
        <>
          <Press scale={0.98} onPress={() => setWhy((w) => !w)} style={{ marginTop: 18, alignSelf: "flex-start" }}>
            <View style={{ flexDirection: "row", alignItems: "center", gap: 7, paddingVertical: 10, paddingHorizontal: 13, borderRadius: 12, backgroundColor: aA(accentDeep, 0.06), borderWidth: 1, borderColor: aA(accentDeep, 0.14) }}>
              <Text style={{ fontFamily: sans(700), fontSize: 13, color: accentDeep }}>why?</Text>
              <View style={{ transform: [{ rotate: why ? "180deg" : "0deg" }] }}><Icon n="chevD" s={13} c={accentDeep} /></View>
            </View>
          </Press>
          {why ? (
            <Text style={{ fontFamily: serif(400, true), fontSize: 14.5, lineHeight: 23, color: GRAY, marginTop: 12 }}>{live.why}</Text>
          ) : null}
        </>
      ) : null}

      {live.link ? (
        <Press scale={0.98} onPress={() => onGo(live.link!.tab)} style={{ marginTop: 22 }}>
          <View style={{ flexDirection: "row", alignItems: "center", justifyContent: "space-between", paddingVertical: 14, paddingHorizontal: 16, borderRadius: 14, borderWidth: 1, borderColor: aA(accent, 0.22), overflow: "hidden" }}>
            <LinearGradient colors={[aA(accent, 0.1), aA(glow, 0.04)]} start={{ x: 0.1, y: 0 }} end={{ x: 0.9, y: 1 }} style={{ position: "absolute", top: 0, left: 0, right: 0, bottom: 0 } as any} />
            <Text style={{ flex: 1, fontFamily: sans(700), fontSize: 14, color: INK }}>{live.link.label}</Text>
            <Icon n="chevR" s={16} c={accentDeep} />
          </View>
        </Press>
      ) : null}
    </View>
  );
}

// A sheet with no data says so. It never borrows yesterday's, or anyone else's.
function Empty({ label }: { label: string }) {
  return (
    <View style={{ paddingVertical: 26, alignItems: "center", gap: 6 }}>
      <Icon n="clock" s={22} c={GRAY} sw={1.7} />
      <Text style={{ fontFamily: serif(400), fontSize: 17, color: INK2 }}>{label}</Text>
      <Text style={{ fontFamily: sans(400), fontSize: 12.5, color: GRAY, textAlign: "center" }}>Nothing to show here right now.</Text>
    </View>
  );
}
