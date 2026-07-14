// sheets.tsx — Read-tab detail sheets (astro-screens.tsx EclipseSheet + AreaSheet).
import React, { useState } from "react";
import { View, Text } from "react-native";
import { LinearGradient } from "expo-linear-gradient";
import { Mood, ECLIPSE, LIFE_AREAS, LIFE_AREA_META } from "../theme";
import { INK, INK2, GRAY, WASH, HAIR, aA, sans, serif, mono } from "../ui/palette";
import { Press, Label, GlossIcon } from "../ui/atoms";
import { Icon } from "../ui/Icon";

export function EclipseSheet({ mood, type }: { mood: Mood; type: string }) {
  const { accentDeep } = mood;
  const t = type || ECLIPSE.type;
  const sanskrit = t === "solar" ? "सूर्य ग्रहण" : "चन्द्र ग्रहण";
  return (
    <View>
      <Label c={aA(accentDeep, 0.9)}>Heads up</Label>
      <Text style={{ fontFamily: serif(500), fontSize: 24, color: INK, marginTop: 6 }}>A {t} eclipse on {ECLIPSE.date}</Text>
      <Text style={{ fontFamily: serif(400), fontSize: 16, lineHeight: 24, color: INK2, marginTop: 12 }}>{ECLIPSE.full ? ECLIPSE.full[t] : ""}</Text>
      <View style={{ marginTop: 16, padding: 15, borderRadius: 14, backgroundColor: WASH }}>
        <Label>Caution window</Label>
        <Text style={{ fontFamily: sans(400), fontSize: 13.5, lineHeight: 20, color: INK2, marginTop: 6 }}>
          The Sutak window begins about {ECLIPSE.sutakHours} hours before, around {ECLIPSE.sutakDate}, {ECLIPSE.sutakTime}.
        </Text>
      </View>
      <Text style={{ textAlign: "center", marginTop: 14, fontFamily: serif(400), fontSize: 16, color: GRAY }}>{sanskrit}</Text>
    </View>
  );
}

export function AreaSheet({ mood, area, onGo }: { mood: Mood; area: string; onGo: (tab: string) => void }) {
  const { accent, accentDeep, glow } = mood;
  const la = (LIFE_AREAS as any)[mood.key] || {};
  const meta = (LIFE_AREA_META as any)[area] || {};
  const line = area === "Love" ? la.love : area === "Work" ? la.work : la.money;
  const col = area === "Love" ? ["#E48AA6", "#C55C7E"] : area === "Work" ? ["#6E86C4", "#4C63A0"] : ["#5FA97E", "#3E8060"];
  const ic = area === "Love" ? "heart" : area === "Work" ? "work" : "coin";
  const [why, setWhy] = useState(false);
  return (
    <View>
      <View style={{ flexDirection: "row", alignItems: "center", gap: 12 }}>
        <GlossIcon c1={col[0]} c2={col[1]} size={40} radius={13}><Icon n={ic} s={19} c="#FFF" sw={1.9} /></GlossIcon>
        <View>
          <View style={{ flexDirection: "row", alignItems: "baseline", gap: 8 }}>
            <Text style={{ fontFamily: serif(500), fontSize: 23, color: INK, letterSpacing: -0.3 }}>{area} today</Text>
            <Text style={{ fontFamily: mono(500), fontSize: 10, letterSpacing: 0.7, textTransform: "uppercase", color: accentDeep }}>· {meta.planet}</Text>
          </View>
          <Text style={{ fontFamily: mono(500), fontSize: 9.5, letterSpacing: 0.5, textTransform: "uppercase", color: GRAY, marginTop: 2 }}>{meta.houses} house</Text>
        </View>
      </View>

      <Text style={{ fontFamily: serif(400), fontSize: 17, lineHeight: 25, color: INK, marginTop: 16 }}>{line}</Text>
      <Text style={{ fontFamily: sans(400), fontSize: 10.5, letterSpacing: 1, textTransform: "uppercase", color: GRAY, marginTop: 18, marginBottom: 7 }}>What it means today</Text>
      <Text style={{ fontFamily: serif(400), fontSize: 15.5, lineHeight: 25, color: INK2 }}>{meta.detail}</Text>

      <Press scale={0.98} onPress={() => setWhy((w) => !w)} style={{ marginTop: 18, alignSelf: "flex-start" }}>
        <View style={{ flexDirection: "row", alignItems: "center", gap: 7, paddingVertical: 10, paddingHorizontal: 13, borderRadius: 12, backgroundColor: aA(accentDeep, 0.06), borderWidth: 1, borderColor: aA(accentDeep, 0.14) }}>
          <Text style={{ fontFamily: sans(700), fontSize: 13, color: accentDeep }}>why?</Text>
          <View style={{ transform: [{ rotate: why ? "180deg" : "0deg" }] }}><Icon n="chevD" s={13} c={accentDeep} /></View>
        </View>
      </Press>
      {why ? (
        <Text style={{ fontFamily: serif(400, true), fontSize: 14.5, lineHeight: 23, color: GRAY, marginTop: 12 }}>{meta.why}</Text>
      ) : null}

      {meta.link ? (
        <Press scale={0.98} onPress={() => onGo(meta.link.tab)} style={{ marginTop: 22 }}>
          <View style={{ flexDirection: "row", alignItems: "center", justifyContent: "space-between", paddingVertical: 14, paddingHorizontal: 16, borderRadius: 14, borderWidth: 1, borderColor: aA(accent, 0.22), overflow: "hidden" }}>
            <LinearGradient colors={[aA(accent, 0.1), aA(glow, 0.04)]} start={{ x: 0.1, y: 0 }} end={{ x: 0.9, y: 1 }} style={{ position: "absolute", top: 0, left: 0, right: 0, bottom: 0 } as any} />
            <Text style={{ fontFamily: sans(700), fontSize: 14, color: INK }}>{meta.link.label}</Text>
            <Icon n="chevR" s={16} c={accentDeep} />
          </View>
        </Press>
      ) : null}
    </View>
  );
}
