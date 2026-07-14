// chrome.tsx — persistent Today chrome (astro-today.tsx): TopCluster, MoonFAB (the Sage),
// SubTabs (Read/Plan), BottomNav.
import React, { useEffect, useRef, useState } from "react";
import { View, Text, Image, Pressable, StyleSheet } from "react-native";
import Animated, { useSharedValue, useAnimatedStyle, withTiming, withSequence } from "react-native-reanimated";
import { LinearGradient } from "expo-linear-gradient";
import { BlurView } from "expo-blur";
import { Mood, NAME } from "../theme";
import { INK, GRAY, WASH, HAIR, ORANGE, aA, sans, serif, shadow } from "../ui/palette";
import { Press, Pill, RadialGlow } from "../ui/atoms";
import { Icon, Flame } from "../ui/Icon";
import { useFloatY, useHalo, usePulseRing } from "../ui/motion";

const chatfab = require("../assets/chatfab.png");

// a "+1" that floats up + fades each time `bump` increments (coinUp)
function Coin({ color }: { color: string }) {
  const v = useSharedValue(0);
  useEffect(() => { v.value = withTiming(1, { duration: 800 }); }, []);
  const a = useAnimatedStyle(() => ({ opacity: 1 - v.value, transform: [{ translateY: -26 * v.value }] }));
  return (
    <Animated.View style={[{ position: "absolute", top: -2, right: 12 }, a]} pointerEvents="none">
      <Text style={{ fontFamily: sans(800), fontSize: 13, color }}>+1</Text>
    </Animated.View>
  );
}
function CoinFloat({ bump, color }: { bump: number; color: string }) {
  const [ids, setIds] = useState<number[]>([]);
  const prev = useRef(bump);
  useEffect(() => {
    if (bump !== prev.current) {
      prev.current = bump;
      const id = Date.now();
      setIds((a) => [...a, id]);
      setTimeout(() => setIds((a) => a.filter((x) => x !== id)), 800);
    }
  }, [bump]);
  return <>{ids.map((id) => <Coin key={id} color={color} />)}</>;
}

export function TopCluster({ mood, bal, bump, alert, onProfile, onWallet, onBell }: any) {
  const { accentDeep, glow } = mood;
  return (
    <View style={{ flexDirection: "row", alignItems: "center", justifyContent: "space-between" }}>
      <Press scale={0.94} onPress={onProfile}>
        <LinearGradient
          colors={[glow, accentDeep]} start={{ x: 0.1, y: 0 }} end={{ x: 0.9, y: 1 }}
          style={{ width: 44, height: 44, borderRadius: 999, padding: 2, ...shadow({ y: 3, blur: 10, opacity: 0.4, color: accentDeep, elevation: 4 }) } as any}
        >
          <View style={{ flex: 1, borderRadius: 999, backgroundColor: WASH, alignItems: "center", justifyContent: "center", borderWidth: 2, borderColor: "#FFF" }}>
            <Text style={{ fontFamily: serif(600), fontSize: 18, color: INK }}>{NAME[0]}</Text>
          </View>
        </LinearGradient>
      </Press>
      <View style={{ flexDirection: "row", alignItems: "center", gap: 10 }}>
        <Press scale={0.9} onPress={onBell}>
          <Pill radius={999} style={{ width: 42, height: 42, alignItems: "center", justifyContent: "center" }}>
            <Icon n="bell" s={17} c={INK} sw={1.8} />
            {alert && <View style={{ position: "absolute", top: 9, right: 10, width: 7, height: 7, borderRadius: 999, backgroundColor: ORANGE, borderWidth: 1.5, borderColor: "#FFF" }} />}
          </Pill>
        </Press>
        <Press scale={0.94} onPress={onWallet}>
          <Pill radius={999} style={{ paddingVertical: 9, paddingHorizontal: 14, flexDirection: "row", alignItems: "center", gap: 6 }}>
            <Flame s={15} c={glow} />
            <Text style={{ fontFamily: sans(800), fontSize: 15, color: INK }}>{bal}</Text>
            <CoinFloat bump={bump} color={accentDeep} />
          </Pill>
        </Press>
      </View>
    </View>
  );
}

// the floating Sage companion (every screen but Chat)
export function MoonFAB({ mood, insight, onTap }: any) {
  const { glow } = mood;
  const floatA = useFloatY(6);
  const haloA = useHalo(insight ? 3 : 4.8);
  const ringA = usePulseRing(1.8);
  const poke = useSharedValue(0);
  const pokeA = useAnimatedStyle(() => ({ transform: [{ scale: 1 + 0.08 * poke.value }, { rotate: `${-3 * poke.value}deg` }] }));
  return (
    <View style={{ position: "absolute", right: 14, bottom: 94, zIndex: 50 }}>
      <View>
        <Pressable
          onPress={onTap}
          onPressIn={() => { poke.value = withSequence(withTiming(1, { duration: 120 }), withTiming(0, { duration: 340 })); }}
        >
          <Animated.View style={[{ width: 68, height: 72 }, floatA]}>
            <Animated.View style={[{ position: "absolute", left: -6, top: -4, width: 80, height: 80 }, haloA]} pointerEvents="none">
              <RadialGlow color={glow} size={80} opacity={insight ? 0.5 : 0.3} />
            </Animated.View>
            {/* soft ROUND ground shadow — replaces a filter:drop-shadow that traced the
                square-ish chat-bubble PNG and cast a squarish shadow on the phone */}
            <RadialGlow color="#1A1408" size={62} opacity={0.2} style={{ position: "absolute", left: 3, top: 18 }} />
            <Animated.View style={[{ width: "100%", height: "100%" }, pokeA]}>
              <Image source={chatfab} resizeMode="contain" style={{ width: "100%", height: "100%" }} />
            </Animated.View>
          </Animated.View>
        </Pressable>
        {insight && (
          <View style={{ position: "absolute", right: 4, top: 2 }} pointerEvents="none">
            <Animated.View style={[{ position: "absolute", left: -4, top: -4, width: 21, height: 21, borderRadius: 999, backgroundColor: aA("#E5484D", 0.4) }, ringA]} />
            <View style={{ width: 13, height: 13, borderRadius: 999, backgroundColor: "#E5484D", borderWidth: 2, borderColor: "#FFF", ...shadow({ y: 1, blur: 4, opacity: 0.4, elevation: 2 }) } as any} />
          </View>
        )}
      </View>
    </View>
  );
}

export function SubTabs({ value, onChange }: { value: string; onChange: (v: string) => void }) {
  const tabs = ["Read", "Plan"];
  return (
    <View style={{ flexDirection: "row", padding: 4, borderRadius: 999, backgroundColor: WASH, borderWidth: 1, borderColor: HAIR }}>
      {tabs.map((t) => {
        const on = value === t;
        return (
          <Press key={t} scale={0.97} onPress={() => onChange(t)} style={{ flex: 1 }}>
            <View style={{ paddingVertical: 9, borderRadius: 999, alignItems: "center", backgroundColor: on ? "#FFF" : "transparent", ...(on ? shadow({ y: 2, blur: 8, opacity: 0.16, elevation: 2 }) : null) } as any}>
              <Text style={{ fontFamily: sans(on ? 800 : 700), fontSize: 14, color: on ? INK : GRAY, letterSpacing: 0.2 }}>{t}</Text>
            </View>
          </Press>
        );
      })}
    </View>
  );
}

export function BottomNav({ mood, active, onTab }: any) {
  const { accent, accentDeep, glow } = mood;
  const Side = ({ label, ic }: { label: string; ic: string }) => {
    const on = active === label;
    return (
      <Pressable onPress={() => onTab(label)} style={{ flex: 1, alignItems: "center", gap: 5, paddingTop: 4 }}>
        <Icon n={ic} s={22} c={on ? INK : GRAY} sw={on ? 2 : 1.7} />
        <Text style={{ fontFamily: sans(on ? 800 : 600), fontSize: 10, color: on ? INK : GRAY }}>{label}</Text>
      </Pressable>
    );
  };
  const onR = active === "Readings";
  return (
    <BlurView intensity={24} tint="light" style={{ position: "absolute", bottom: 0, left: 0, right: 0, borderTopWidth: 1, borderTopColor: HAIR, paddingTop: 10, paddingHorizontal: 8, paddingBottom: 18, flexDirection: "row", alignItems: "flex-start", zIndex: 40, backgroundColor: aA("#FFFFFF", 0.82) }}>
      <Side label="Today" ic="today" />
      <Side label="Timeline" ic="timeline" />
      <View style={{ flex: 1, alignItems: "center" }}>
        <Press scale={0.92} onPress={() => onTab("Readings")}>
          {/* outer wrapper carries the rounded shadow (no clip); inner clips the gloss */}
          <View style={{ width: 56, height: 56, borderRadius: 999, marginTop: -26, backgroundColor: accentDeep, ...shadow({ y: 9, blur: 22, opacity: 0.5, color: accentDeep, elevation: 8 }) } as any}>
            <View style={{ width: 56, height: 56, borderRadius: 999, overflow: "hidden", borderWidth: 3, borderColor: "#FFF", alignItems: "center", justifyContent: "center" }}>
              <LinearGradient colors={[glow, accent, accentDeep]} locations={[0, 0.54, 1]} start={{ x: 0.15, y: 0 }} end={{ x: 0.85, y: 1 }} style={StyleSheet.absoluteFill as any} />
              <View style={{ position: "absolute", top: 0, left: 0, right: 0, height: "46%" }}>
                <LinearGradient colors={[aA("#FFF", 0.42), aA("#FFF", 0)]} start={{ x: 0, y: 0 }} end={{ x: 0, y: 1 }} style={{ flex: 1 }} />
              </View>
              <View style={{ position: "absolute", top: 0, left: 0, right: 0, bottom: 0, alignItems: "center", justifyContent: "center" }}>
                <Icon n="readings" s={23} c="#FFF" sw={1.9} />
              </View>
            </View>
          </View>
        </Press>
        <Text style={{ fontFamily: sans(onR ? 800 : 600), fontSize: 10, color: onR ? INK : GRAY, marginTop: 5 }}>Readings</Text>
      </View>
      <Side label="People" ic="people" />
      <Side label="Rituals" ic="rituals" />
    </BlurView>
  );
}
