// NotifScreen.tsx — warm notifications (astro-screens.tsx NotifScreen).
import React from "react";
import { View, Text, ScrollView } from "react-native";
import { Mood } from "../theme";
import { PAPER, INK, GRAY, HAIR, aA, sans, serif, mono, cardStyle, shadow } from "../ui/palette";
import { Press, Pill, Label, GlossIcon } from "../ui/atoms";
import { Icon } from "../ui/Icon";

export function NotifScreen({ mood, onBack, insetTop = 44 }: any) {
  const { accent, accentDeep, glow } = mood;
  const items = [
    { ic: "moon", c1: glow, c2: accentDeep, t: "I've been thinking about you", s: "a small pattern from your last few days", now: "just now", unread: true, grp: "New" },
    { ic: "clock", c1: "#6E86C4", c2: "#4C63A0", t: "Your strong window opens at 11:40", s: "good for the pitch you noted", now: "2h ago", unread: true, grp: "New" },
    { ic: "flame", c1: "#D98A2B", c2: "#B26C18", t: "12-day streak, gently held", s: "check in today to keep it warm", now: "5h ago", unread: false, grp: "Earlier" },
  ];
  const groups = ["New", "Earlier"];
  return (
    <View style={{ position: "absolute", top: 0, left: 0, right: 0, bottom: 0, backgroundColor: PAPER }}>
      <View style={{ paddingTop: insetTop + 4, paddingHorizontal: 18, paddingBottom: 14, backgroundColor: PAPER, flexDirection: "row", alignItems: "center", gap: 13, ...shadow({ y: 4, blur: 14, opacity: 0.1, elevation: 4 }), zIndex: 10 } as any}>
        <Press scale={0.9} onPress={onBack}>
          <Pill radius={999} style={{ width: 40, height: 40, alignItems: "center", justifyContent: "center" }}><Icon n="arrowL" s={18} c={INK} /></Pill>
        </Press>
        <View>
          <Label c={aA(accentDeep, 0.9)}>For you</Label>
          <Text style={{ fontFamily: serif(500), fontSize: 22, color: INK, marginTop: 1 }}>A few quiet notes</Text>
        </View>
      </View>
      <ScrollView contentContainerStyle={{ paddingHorizontal: 18, paddingBottom: 130 }} showsVerticalScrollIndicator={false}>
        {groups.map((g) => {
          const gi = items.filter((n) => n.grp === g);
          if (!gi.length) return null;
          return (
            <View key={g} style={{ marginTop: 18 }}>
              <View style={{ marginBottom: 6 }}><Label>{g}</Label></View>
              <View style={cardStyle({ paddingVertical: 4, paddingHorizontal: 16 })}>
                {gi.map((n, i) => (
                  <Press key={i} scale={0.99}>
                    <View style={{ flexDirection: "row", alignItems: "flex-start", gap: 13, paddingVertical: 14, borderTopWidth: i ? 1 : 0, borderTopColor: HAIR }}>
                      <GlossIcon c1={n.c1} c2={n.c2} size={40} radius={13}><Icon n={n.ic} s={18} c="#FFF" sw={1.9} /></GlossIcon>
                      <View style={{ flex: 1 }}>
                        <Text style={{ fontFamily: sans(700), fontSize: 14.5, color: INK, lineHeight: 20 }}>{n.t}</Text>
                        <Text style={{ fontFamily: serif(400), fontSize: 13.5, color: GRAY, marginTop: 2, lineHeight: 19 }}>{n.s}</Text>
                        <Text style={{ fontFamily: mono(500), fontSize: 9.5, letterSpacing: 0.6, textTransform: "uppercase", color: aA(GRAY, 0.8), marginTop: 5 }}>{n.now}</Text>
                      </View>
                      {n.unread && <View style={{ width: 8, height: 8, borderRadius: 999, marginTop: 6, backgroundColor: accent }} />}
                    </View>
                  </Press>
                ))}
              </View>
            </View>
          );
        })}
        <Text style={{ textAlign: "center", marginTop: 26, fontFamily: serif(400, true), fontSize: 14, color: aA(GRAY, 0.9) }}>that's everything, for now</Text>
      </ScrollView>
    </View>
  );
}
