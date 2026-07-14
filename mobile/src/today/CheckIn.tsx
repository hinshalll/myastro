// CheckIn.tsx — the daily check-in (astro-today.tsx CheckInSheet + CheckInChip).
import React, { useEffect, useState } from "react";
import { View, Text } from "react-native";
import Animated, { FadeIn } from "react-native-reanimated";
import { LinearGradient } from "expo-linear-gradient";
import { Mood, CHECKIN_REFLECTION } from "../theme";
import { INK, INK2, GRAY, WASH, HAIR, aA, sans, serif } from "../ui/palette";
import { Press, Pill, Label, RadialGlow } from "../ui/atoms";
import { Flame } from "../ui/Icon";
import { useRiseIn } from "../ui/motion";

function ChipRow({ items, onPick }: { items: string[]; onPick: (w: string) => void }) {
  return (
    <View style={{ flexDirection: "row", flexWrap: "wrap", gap: 8 }}>
      {items.map((w) => (
        <Press key={w} scale={0.95} onPress={() => onPick(w)}>
          <Pill radius={999} style={{ paddingVertical: 10, paddingHorizontal: 17 }}>
            <Text style={{ fontFamily: sans(700), fontSize: 14, color: INK }}>{w}</Text>
          </Pill>
        </Press>
      ))}
    </View>
  );
}

export function CheckInSheet({ mood, onEarn, onClose }: { mood: Mood; onEarn: (n: number) => void; onClose: (done: boolean) => void }) {
  const { accent, accentDeep, glow } = mood;
  const [mSel, setMSel] = useState<string | null>(null);
  const [eSel, setESel] = useState<string | null>(null);
  const both = !!(mSel && eSel);
  const reflection = both ? CHECKIN_REFLECTION(mSel!, eSel!, mood.key) : "";
  useEffect(() => {
    if (both) { onEarn(1); const t = setTimeout(() => onClose(true), 2600); return () => clearTimeout(t); }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mSel, eSel]);

  return (
    <View>
      <View style={{ flexDirection: "row", alignItems: "center", justifyContent: "space-between" }}>
        <Label c={aA(accentDeep, 0.9)}>Check in</Label>
        <View style={{ flexDirection: "row", alignItems: "center", gap: 5 }}>
          <Flame s={13} c={accent} />
          <Text style={{ fontFamily: sans(700), fontSize: 12, color: GRAY }}>12 days in a row</Text>
        </View>
      </View>
      <Text style={{ fontFamily: serif(500), fontSize: 24, color: INK, marginTop: 6, letterSpacing: -0.3 }}>
        {both ? "Thanks for checking in." : !mSel ? "How are you today?" : "And your energy?"}
      </Text>

      {!mSel && (
        <Animated.View entering={FadeIn.duration(250)} style={{ marginTop: 18 }}>
          <ChipRow items={["calm", "tender", "sharp", "heavy", "wired"]} onPick={setMSel} />
        </Animated.View>
      )}

      {mSel && !eSel && (
        <Animated.View entering={FadeIn.duration(250)} style={{ marginTop: 18 }}>
          <View style={{ flexDirection: "row", alignItems: "center", gap: 8, marginBottom: 10 }}>
            <LinearGradient colors={[accent, accentDeep]} start={{ x: 0, y: 0 }} end={{ x: 0, y: 1 }} style={{ paddingVertical: 5, paddingHorizontal: 12, borderRadius: 999 }}>
              <Text style={{ fontFamily: sans(700), fontSize: 13, color: "#FFF" }}>{mSel}</Text>
            </LinearGradient>
            <Press scale={0.9} onPress={() => setMSel(null)}><Text style={{ fontFamily: sans(700), fontSize: 12, color: GRAY }}>change</Text></Press>
          </View>
          <ChipRow items={["low", "steady", "bright", "restless"]} onPick={setESel} />
        </Animated.View>
      )}

      {both && (
        <Animated.View entering={FadeIn.duration(300)} style={{ marginTop: 16 }}>
          <View style={{ flexDirection: "row", gap: 7 }}>
            <LinearGradient colors={[accent, accentDeep]} start={{ x: 0, y: 0 }} end={{ x: 0, y: 1 }} style={{ paddingVertical: 6, paddingHorizontal: 14, borderRadius: 999 }}>
              <Text style={{ fontFamily: sans(700), fontSize: 13.5, color: "#FFF" }}>{mSel}</Text>
            </LinearGradient>
            <View style={{ paddingVertical: 6, paddingHorizontal: 14, borderRadius: 999, backgroundColor: aA(accent, 0.14), borderWidth: 1, borderColor: aA(accentDeep, 0.3) }}>
              <Text style={{ fontFamily: sans(700), fontSize: 13.5, color: accentDeep }}>{eSel}</Text>
            </View>
          </View>
          <View style={{ marginTop: 13, padding: 15, borderRadius: 14, backgroundColor: WASH }}>
            <Text style={{ fontFamily: serif(400, true), fontSize: 16, lineHeight: 23, color: INK2 }}>{reflection}</Text>
          </View>
          <View style={{ flexDirection: "row", alignItems: "center", gap: 7, marginTop: 14, justifyContent: "center" }}>
            <Flame s={15} c={glow} />
            <Text style={{ fontFamily: sans(800), fontSize: 13, color: accentDeep }}>+1 diya lit</Text>
          </View>
        </Animated.View>
      )}

      {!both && (
        <Press scale={0.98} onPress={() => onClose(false)} style={{ marginTop: 20 }}>
          <View style={{ paddingVertical: 13, borderRadius: 13, alignItems: "center", backgroundColor: WASH, borderWidth: 1, borderColor: HAIR }}>
            <Text style={{ fontFamily: sans(700), fontSize: 14, color: GRAY }}>Ask me later</Text>
          </View>
        </Press>
      )}
    </View>
  );
}

export function CheckInChip({ mood, delay = 0, onOpen }: any) {
  const { accentDeep, glow } = mood;
  const riseA = useRiseIn(delay);
  return (
    <Animated.View style={[{ marginBottom: 14 }, riseA]}>
      <Press scale={0.98} onPress={onOpen}>
        <Pill radius={999} style={{ paddingVertical: 11, paddingHorizontal: 16, flexDirection: "row", alignItems: "center", gap: 11 }}>
          <View style={{ width: 30, height: 30, borderRadius: 999, alignItems: "center", justifyContent: "center", overflow: "hidden" }}>
            <LinearGradient colors={[glow, accentDeep]} start={{ x: 0.15, y: 0 }} end={{ x: 0.85, y: 1 }} style={{ position: "absolute", top: 0, left: 0, right: 0, bottom: 0 } as any} />
            <View style={{ position: "absolute", top: 0, left: 0, right: 0, bottom: 0, alignItems: "center", justifyContent: "center" }}>
              <Flame s={14} c="#FFF" />
            </View>
          </View>
          <Text style={{ flex: 1, fontFamily: sans(800), fontSize: 14.5, color: INK }}>How are you today?</Text>
          <Icon2 accentDeep={accentDeep} />
        </Pill>
      </Press>
    </Animated.View>
  );
}

import { Icon } from "../ui/Icon";
function Icon2({ accentDeep }: { accentDeep: string }) { return <Icon n="chevR" s={17} c={accentDeep} sw={1.9} />; }
