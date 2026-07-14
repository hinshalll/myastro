// WalletScreen.tsx — Diyas wallet (astro-screens.tsx WalletScreen): hero, earn, buy, Plus, history.
import React from "react";
import { View, Text, ScrollView } from "react-native";
import Animated from "react-native-reanimated";
import { LinearGradient } from "expo-linear-gradient";
import { Mood } from "../theme";
import { PAPER, INK, GRAY, WASH, HAIR, aA, sans, serif, mono, cardStyle, shadow } from "../ui/palette";
import { Press, Pill, Label, RadialGlow } from "../ui/atoms";
import { Icon, Flame } from "../ui/Icon";
import { BackBar } from "../ui/BackBar";
import { useRiseIn, useFloatY, useGlowPulse } from "../ui/motion";

export function WalletScreen({ mood, bal, onBack, insetTop = 44 }: any) {
  const { accent, accentDeep, glow } = mood;
  const bright = Math.min(1, 0.4 + bal / 500);
  const rise0 = useRiseIn(0), rise80 = useRiseIn(80), rise140 = useRiseIn(140), rise200 = useRiseIn(200), rise260 = useRiseIn(260);
  const floatA = useFloatY(5);
  const auraA = useGlowPulse(4);
  const earn = [["Daily check-in", "+1", true], ["Today's ritual", "+2", false], ["A journal note", "+1", false], ["7-day streak", "+10", false], ["Invite a friend", "+25", false]] as any[];
  const buy = [["Glow", "₹99", "110", false], ["Blaze", "₹299", "380", true], ["Festival", "₹799", "1,150", false]] as any[];
  const hist = [["Today's ritual", "+2"], ["Daily check-in", "+1"], ["Full Life Reading", "−60"], ["7-day streak", "+10"], ["Compatibility unlock", "−30"]];
  return (
    <View style={{ position: "absolute", top: 0, left: 0, right: 0, bottom: 0, backgroundColor: PAPER }}>
      <BackBar onBack={onBack} mood={mood} insetTop={insetTop} />
      <ScrollView contentContainerStyle={{ paddingTop: insetTop + 52, paddingHorizontal: 18, paddingBottom: 40 }} showsVerticalScrollIndicator={false}>
        {/* hero */}
        <Animated.View style={[{ alignItems: "center", marginBottom: 24 }, rise0]}>
          <View style={{ width: 92, height: 92, alignItems: "center", justifyContent: "center" }}>
            <Animated.View style={[{ position: "absolute", width: 92, height: 92, borderRadius: 999, backgroundColor: aA(glow, 0.3 + bright * 0.3) }, auraA]} />
            <Animated.View style={floatA}><Flame s={64} c={glow} /></Animated.View>
          </View>
          <View style={{ flexDirection: "row", alignItems: "baseline", gap: 8, marginTop: 8 }}>
            <Text style={{ fontFamily: serif(600), fontSize: 52, color: INK, letterSpacing: -1.5 }}>{bal}</Text>
            <Text style={{ fontFamily: serif(400, true), fontSize: 22, color: accentDeep }}>🪔 lit</Text>
          </View>
        </Animated.View>
        {/* earn */}
        <Animated.View style={[cardStyle({ paddingVertical: 16, paddingHorizontal: 18, marginBottom: 14 }), rise80]}>
          <View style={{ flexDirection: "row", alignItems: "center", justifyContent: "space-between", marginBottom: 4 }}>
            <Label c={aA(accentDeep, 0.9)}>Light a diya by doing good</Label>
            <Text style={{ fontFamily: sans(700), fontSize: 11, color: GRAY }}>3 of 5 today</Text>
          </View>
          {earn.map(([l, amt, done]: any, i: number) => (
            <View key={i} style={{ flexDirection: "row", alignItems: "center", gap: 12, paddingVertical: 11, borderTopWidth: i ? 1 : 0, borderTopColor: HAIR }}>
              <View style={{ width: 26, height: 26, borderRadius: 999, alignItems: "center", justifyContent: "center", backgroundColor: done ? aA(accent, 0.14) : WASH, borderWidth: 1, borderColor: done ? aA(accent, 0.3) : HAIR }}>{done ? <Icon n="check" s={13} c={accentDeep} sw={2.4} /> : <Flame s={12} c={glow} />}</View>
              <Text style={{ flex: 1, fontFamily: sans(600), fontSize: 14, color: done ? GRAY : INK, textDecorationLine: done ? "line-through" : "none" }}>{l}</Text>
              <Text style={{ fontFamily: mono(600), fontSize: 12.5, color: done ? GRAY : accentDeep }}>{amt}</Text>
            </View>
          ))}
        </Animated.View>
        {/* buy */}
        <Animated.View style={[{ marginBottom: 14 }, rise140]}>
          <View style={{ paddingLeft: 4, marginBottom: 9 }}><Label>Buy diyas</Label></View>
          <View style={{ flexDirection: "row", gap: 10 }}>
            {buy.map(([n, p, coins, best]: any) => (
              <Pill key={n} radius={18} style={{ flex: 1, paddingVertical: 16, paddingHorizontal: 8, alignItems: "center", gap: 6, borderColor: best ? aA(accent, 0.5) : "rgba(0,0,0,0.05)" }}>
                {best && <View style={{ position: "absolute", top: -8, paddingVertical: 2, paddingHorizontal: 8, borderRadius: 999, backgroundColor: accentDeep }}><Text style={{ fontFamily: mono(600), fontSize: 8, letterSpacing: 0.5, textTransform: "uppercase", color: "#FFF" }}>best value</Text></View>}
                <Flame s={20} c={glow} />
                <Text style={{ fontFamily: sans(800), fontSize: 14, color: INK }}>{n}</Text>
                <Text style={{ fontFamily: serif(600), fontSize: 17, color: INK }}>{coins}🪔</Text>
                <View style={{ marginTop: 2, paddingVertical: 6, width: "100%", borderRadius: 10, backgroundColor: INK, alignItems: "center" }}><Text style={{ fontFamily: sans(700), fontSize: 12, color: "#FFF" }}>{p}</Text></View>
              </Pill>
            ))}
          </View>
        </Animated.View>
        {/* go plus — outer wrapper holds the rounded shadow, inner clips the gradient */}
        <Animated.View style={[{ borderRadius: 22, marginBottom: 14, backgroundColor: "#0C0B0A", ...shadow({ y: 16, blur: 40, opacity: 0.42, color: "#000", elevation: 6 }) } as any, rise200]}>
          <View style={{ borderRadius: 22, overflow: "hidden", padding: 20 }}>
          <LinearGradient colors={["#211B12", "#0C0B0A"]} start={{ x: 0.15, y: 0 }} end={{ x: 0.85, y: 1 }} style={{ position: "absolute", top: 0, left: 0, right: 0, bottom: 0 } as any} />
          <RadialGlow color={glow} size={160} opacity={0.4} style={{ position: "absolute", top: -40, right: -30 }} />
          <Label c={glow}>ASTROLO Plus</Label>
          <Text style={{ fontFamily: serif(500), fontSize: 21, color: "#FBF4E8", marginTop: 9, lineHeight: 27 }}>Unlimited chat, every Pattern, 25% off everything.</Text>
          <Text style={{ fontFamily: sans(400), fontSize: 12.5, color: aA("#FBF4E8", 0.6), marginTop: 8 }}>couple, family & deep Patterns · cross-reference free</Text>
          <View style={{ flexDirection: "row", alignItems: "center", justifyContent: "space-between", marginTop: 16 }}>
            <View style={{ flexDirection: "row", alignItems: "baseline", gap: 5 }}>
              <Text style={{ fontFamily: serif(600), fontSize: 24, color: "#FBF4E8" }}>₹199</Text>
              <Text style={{ fontFamily: sans(400), fontSize: 11, color: aA("#FBF4E8", 0.5) }}>/mo</Text>
            </View>
            <Press scale={0.95}><View style={{ paddingVertical: 10, paddingHorizontal: 16, borderRadius: 999, backgroundColor: glow }}><Text style={{ fontFamily: sans(800), fontSize: 13, color: "#211B12" }}>7-day free trial</Text></View></Press>
          </View>
          </View>
        </Animated.View>
        {/* history */}
        <Animated.View style={[cardStyle({ paddingVertical: 16, paddingHorizontal: 18 }), rise260]}>
          <View style={{ marginBottom: 4 }}><Label>History</Label></View>
          {hist.map(([w, amt]: any, i: number) => (
            <View key={i} style={{ flexDirection: "row", alignItems: "center", gap: 10, paddingVertical: 11, borderTopWidth: i ? 1 : 0, borderTopColor: HAIR }}>
              <Text style={{ flex: 1, fontFamily: sans(600), fontSize: 14, color: INK }}>{w}</Text>
              <Text style={{ fontFamily: mono(600), fontSize: 13, color: amt[0] === "+" ? accentDeep : GRAY }}>{amt}</Text>
              <Flame s={12} c={amt[0] === "+" ? glow : GRAY} />
            </View>
          ))}
        </Animated.View>
      </ScrollView>
    </View>
  );
}
