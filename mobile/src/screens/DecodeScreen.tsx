// DecodeScreen.tsx — the Readings hub (astro-screens.tsx DecodeScreen). Bottom-nav centre destination.
import React from "react";
import { View, Text, ScrollView } from "react-native";
import Animated from "react-native-reanimated";
import { LinearGradient } from "expo-linear-gradient";
import { Mood } from "../theme";
import { getFirstName } from "../api/profile";
import { PAPER, INK, GRAY, HAIR, aA, sans, serif, mono, cardStyle, shadow } from "../ui/palette";
import { Press, Pill, Label, GlossIcon } from "../ui/atoms";
import { Icon, Flame } from "../ui/Icon";
import { TopCluster } from "../today/chrome";
import { useRiseIn, useFloatY } from "../ui/motion";

export function DecodeScreen({ mood, bal, onWallet, onProfile, onBell, insetTop = 44 }: any) {
  const { accent, accentDeep, glow } = mood;
  const rise0 = useRiseIn(0), rise80 = useRiseIn(80);
  const floatA = useFloatY(5);

  const Row = ({ glyph, title, sub, price }: any) => (
    <Press scale={0.985} style={{ marginBottom: 10 }}>
      <Pill radius={18} style={{ paddingVertical: 13, paddingHorizontal: 15, flexDirection: "row", alignItems: "center", gap: 13 }}>
        <GlossIcon c1={glow} c2={accentDeep} size={42} radius={13}><Text style={{ fontSize: 19, color: "#FFF" }}>{glyph}</Text></GlossIcon>
        <View style={{ flex: 1 }}>
          <Text style={{ fontFamily: serif(500), fontSize: 16.5, color: INK }}>{title}</Text>
          <Text style={{ fontFamily: sans(400), fontSize: 12, color: GRAY, marginTop: 1 }}>{sub}</Text>
        </View>
        {price ? (
          <View style={{ flexDirection: "row", alignItems: "center", gap: 3, paddingVertical: 5, paddingHorizontal: 10, borderRadius: 999, backgroundColor: aA(accent, 0.1), borderWidth: 1, borderColor: aA(accent, 0.24) }}>
            <Flame s={11} c={glow} /><Text style={{ fontFamily: mono(600), fontSize: 11.5, color: accentDeep }}>{price}</Text>
          </View>
        ) : <Icon n="chevR" s={16} c={GRAY} />}
      </Pill>
    </Press>
  );
  const tools = [["✦", "Numerology", "your numbers", "#7B7FD0", "#5C60AE"], ["☍", "Palmistry", "read your palm", "#2E9C7E", "#1F7660"], ["◑", "Face Reading", "read your face", "#D06A8C", "#AC4E6E"], ["✷", "Tarot", "pull a card", "#E0982A", "#B5781A"]];

  return (
    <View style={{ position: "absolute", top: 0, left: 0, right: 0, bottom: 0, backgroundColor: PAPER }}>
      <View style={{ position: "absolute", top: insetTop + 4, left: 18, right: 18, zIndex: 10 }}>
        <TopCluster mood={mood} bal={bal} bump={0} alert onProfile={onProfile} onWallet={onWallet} onBell={onBell} />
      </View>
      <ScrollView contentContainerStyle={{ paddingTop: insetTop + 56, paddingHorizontal: 18, paddingBottom: 130 }} showsVerticalScrollIndicator={false}>
        <Animated.View style={rise0}>
          <Label c={aA(accentDeep, 0.9)}>Readings & Tools</Label>
          <Text style={{ fontFamily: serif(500), fontSize: 32, color: INK, letterSpacing: -0.8, marginTop: 3 }}>Decode</Text>
          <Text style={{ fontFamily: serif(400, true), fontSize: 15, color: GRAY, marginTop: 4 }}>Everything your chart can tell you, in one place.</Text>
        </Animated.View>
        {/* kundli anchor */}
        <Animated.View style={[cardStyle({ padding: 20, marginTop: 18 }), rise80]}>
          <View style={{ flexDirection: "row", gap: 16, alignItems: "center" }}>
            <Animated.View style={[{ width: 72, height: 72, borderRadius: 999, backgroundColor: accentDeep, ...shadow({ y: 8, blur: 22, opacity: 0.5, color: accentDeep, elevation: 6 }) } as any, floatA]}>
              <View style={{ width: 72, height: 72, borderRadius: 999, overflow: "hidden", alignItems: "center", justifyContent: "center" }}>
                <LinearGradient colors={[glow, accent, accentDeep]} locations={[0, 0.55, 1]} start={{ x: 0.15, y: 0 }} end={{ x: 0.85, y: 1 }} style={{ position: "absolute", top: 0, left: 0, right: 0, bottom: 0 } as any} />
                <View style={{ position: "absolute", top: 0, left: 0, right: 0, height: "46%" }}><LinearGradient colors={[aA("#FFF", 0.4), aA("#FFF", 0)]} start={{ x: 0, y: 0 }} end={{ x: 0, y: 1 }} style={{ flex: 1 }} /></View>
                <View style={{ position: "absolute", top: 0, left: 0, right: 0, bottom: 0, alignItems: "center", justifyContent: "center" }}>
                  <Text style={{ fontSize: 34, color: "#FFFDF8" }}>♋</Text>
                </View>
              </View>
            </Animated.View>
            <View style={{ flex: 1 }}>
              <Label c={aA(accentDeep, 0.9)}>Your kundli</Label>
              <Text style={{ fontFamily: serif(500), fontSize: 21, color: INK, marginTop: 3 }}>{getFirstName()}</Text>
              <Text style={{ fontFamily: sans(400), fontSize: 12, color: GRAY, marginTop: 2 }}>14 Aug 1998 · 4:20 am · Jaipur</Text>
              <Press scale={0.96} style={{ marginTop: 11, alignSelf: "flex-start" }}>
                <View style={{ flexDirection: "row", alignItems: "center", gap: 6 }}><Text style={{ fontFamily: sans(700), fontSize: 12.5, color: accentDeep }}>Open full chart</Text><Icon n="arrowR" s={13} c={accentDeep} sw={2} /></View>
              </Press>
            </View>
          </View>
          <View style={{ flexDirection: "row", gap: 8, marginTop: 16, paddingTop: 15, borderTopWidth: 1, borderTopColor: HAIR }}>
            {[["Lagna", "Libra", "ascendant"], ["Rashi", "Cancer", "moon sign"], ["Nakshatra", "Pushya", "birth star"]].map(([k, v, sub]) => (
              <View key={k} style={{ flex: 1, alignItems: "center" }}>
                <Text style={{ fontFamily: mono(600), fontSize: 8.5, letterSpacing: 0.6, textTransform: "uppercase", color: accentDeep }}>{k}</Text>
                <Text style={{ fontFamily: serif(500), fontSize: 16.5, color: INK, marginTop: 3 }}>{v}</Text>
                <Text style={{ fontFamily: sans(400), fontSize: 9.5, color: GRAY, marginTop: 1 }}>{sub}</Text>
              </View>
            ))}
          </View>
        </Animated.View>

        <View style={{ marginHorizontal: 2, marginTop: 26, marginBottom: 11 }}><Label>In-depth readings</Label></View>
        <Row glyph="✦" title="Full Life Reading" sub="your whole chart, read in depth" price="60" />
        <Row glyph="❤" title="Marriage Reading" sub="love, timing, and the person" price="60" />
        <Row glyph="✶" title="Career & Purpose" sub="where your work wants to go" price="45" />
        <View style={{ marginHorizontal: 2, marginTop: 26, marginBottom: 11 }}><Label>Matching & timing</Label></View>
        <Row glyph="⚯" title="Kundli Matching" sub="check two charts together" />
        <Row glyph="☼" title="Auspicious Days" sub="find a good day to begin" />
        <View style={{ marginHorizontal: 2, marginTop: 26, marginBottom: 11 }}><Label>Explore yourself</Label></View>
        <View style={{ flexDirection: "row", flexWrap: "wrap", gap: 10 }}>
          {tools.map(([g, t, sub, c1, c2]: any) => (
            <Press key={t} scale={0.97} style={{ width: "48%" }}>
              <Pill radius={18} style={{ padding: 16 }}>
                <GlossIcon c1={c1} c2={c2} size={38} radius={12}><Text style={{ fontSize: 18, color: "#FFF" }}>{g}</Text></GlossIcon>
                <Text style={{ fontFamily: serif(500), fontSize: 16, color: INK, marginTop: 11 }}>{t}</Text>
                <Text style={{ fontFamily: sans(400), fontSize: 11.5, color: GRAY, marginTop: 1 }}>{sub}</Text>
              </Pill>
            </Press>
          ))}
        </View>
        <Text style={{ textAlign: "center", fontFamily: serif(400, true), fontSize: 13.5, color: GRAY, marginTop: 16 }}>Try each once for free, then they cost a few Diyas.</Text>
      </ScrollView>
    </View>
  );
}
