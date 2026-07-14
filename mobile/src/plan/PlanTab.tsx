// PlanTab.tsx — the Plan sub-tab body (astro-plan.tsx PlanTab) + AskMomentCard + MyPanchang.
import React from "react";
import { View, Text } from "react-native";
import Animated from "react-native-reanimated";
import { LinearGradient } from "expo-linear-gradient";
import { Mood, ASK_MOMENT, PANCHANG_SOON } from "../theme";
import { INK, INK2, GRAY, WASH, HAIR, aA, sans, serif, cardStyle, shadow } from "../ui/palette";
import { Press, Pill, Label, GlossIcon } from "../ui/atoms";
import { Icon } from "../ui/Icon";
import { useRiseIn } from "../ui/motion";
import { MyDay } from "./MyDay";
import { qColor, qWord } from "./util";

function AskMomentCard({ mood, delay, onAsk }: any) {
  const { accent, accentDeep, glow } = mood;
  const riseA = useRiseIn(delay);
  const samples = (ASK_MOMENT.samples || []).slice(0, 3);
  return (
    <Animated.View style={[{ marginBottom: 14 }, riseA]}>
      <View style={cardStyle({ padding: 18, overflow: "hidden", borderColor: aA(accent, 0.24) })}>
        <LinearGradient colors={[aA(accent, 0.12), aA(glow, 0.05)]} start={{ x: 0.1, y: 0 }} end={{ x: 0.9, y: 1 }} style={{ position: "absolute", top: 0, left: 0, right: 0, bottom: 0 } as any} />
        <View style={{ flexDirection: "row", alignItems: "center", justifyContent: "space-between" }}>
          <View style={{ flex: 1, paddingRight: 12 }}>
            <Label c={aA(accentDeep, 0.9)}>Ask the Moment</Label>
            <Text style={{ fontFamily: serif(500), fontSize: 21, color: INK, marginTop: 2, letterSpacing: -0.3 }}>Ask, and the sky answers — now</Text>
          </View>
          <GlossIcon c1={"#8E7BD6"} c2={"#5C4FB0"} size={42} radius={13}><Icon n="wand" s={19} c="#FFF" sw={1.8} /></GlossIcon>
        </View>
        <Text style={{ fontFamily: sans(400), fontSize: 12.5, color: GRAY, marginTop: 6 }}>a yes / no or this-or-that, cast for this exact moment</Text>
        <View style={{ flexDirection: "row", flexWrap: "wrap", gap: 8, marginTop: 14 }}>
          {samples.map((s: string) => (
            <Press key={s} scale={0.95} onPress={() => onAsk(s)}>
              <View style={{ paddingVertical: 9, paddingHorizontal: 14, borderRadius: 999, backgroundColor: "#FFF", borderWidth: 1, borderColor: aA(accent, 0.28), ...shadow({ y: 4, blur: 10, opacity: 0.28, color: accentDeep, elevation: 2 }) } as any}>
                <Text style={{ fontFamily: sans(700), fontSize: 13, color: INK }}>{s}</Text>
              </View>
            </Press>
          ))}
        </View>
        <Press scale={0.98} onPress={() => onAsk("")} style={{ marginTop: 12 }}>
          <View style={{ flexDirection: "row", alignItems: "center", gap: 8, paddingVertical: 12, paddingHorizontal: 15, borderRadius: 14, backgroundColor: aA("#FFF", 0.72), borderWidth: 1, borderColor: aA(accentDeep, 0.42), borderStyle: "dashed" }}>
            <Icon n="wand" s={15} c={accentDeep} sw={1.9} />
            <Text style={{ fontFamily: sans(400), fontSize: 13.5, color: GRAY }}>…or type your own question</Text>
          </View>
        </Press>
      </View>
    </Animated.View>
  );
}

function MyPanchang({ mood, delay, onMonth }: any) {
  const { accent, accentDeep } = mood;
  const riseA = useRiseIn(delay);
  return (
    <Animated.View style={[{ marginBottom: 14 }, riseA]}>
      <View style={cardStyle({ padding: 18 })}>
        <View style={{ flexDirection: "row", alignItems: "center", justifyContent: "space-between" }}>
          <View>
            <Label c={aA(accentDeep, 0.9)}>My Panchang</Label>
            <Text style={{ fontFamily: serif(500), fontSize: 20, color: INK, marginTop: 2 }}>Your next few days</Text>
          </View>
          <GlossIcon c1={"#C9A6E8"} c2={"#7E54A0"}><Icon n="cal" s={19} c="#FFF" sw={1.8} /></GlossIcon>
        </View>
        <View style={{ marginTop: 14, gap: 10 }}>
          {PANCHANG_SOON.map((d: any, i: number) => (
            <View key={i} style={{ flexDirection: "row", alignItems: "center", gap: 12, paddingVertical: 11, paddingHorizontal: 13, borderRadius: 14, backgroundColor: WASH, borderWidth: 1, borderColor: HAIR }}>
              <View style={{ width: 78 }}>
                <Text style={{ fontFamily: sans(800), fontSize: 13, color: INK }}>{d.day}</Text>
                <Text style={{ fontFamily: sans(400), fontSize: 9.5, color: GRAY }}>{d.date}</Text>
              </View>
              <View style={{ width: 15, height: 15, borderRadius: 999, backgroundColor: aA(qColor(d.quality), 0.16), alignItems: "center", justifyContent: "center" }}>
                <View style={{ width: 9, height: 9, borderRadius: 999, backgroundColor: qColor(d.quality) }} />
              </View>
              <View style={{ flex: 1 }}>
                <Text style={{ fontFamily: serif(400), fontSize: 15, color: INK }}>{qWord(d.quality)}</Text>
                <Text style={{ fontFamily: sans(400), fontSize: 11.5, color: GRAY, marginTop: 1 }}>{d.note}</Text>
              </View>
            </View>
          ))}
        </View>
        <Press scale={0.98} onPress={onMonth} style={{ marginTop: 13, alignSelf: "flex-start" }}>
          <View style={{ flexDirection: "row", alignItems: "center", gap: 6 }}>
            <Text style={{ fontFamily: sans(700), fontSize: 12.5, color: accentDeep }}>Open full Panchang</Text>
            <Icon n="arrowR" s={13} c={accentDeep} sw={2} />
          </View>
        </Press>
      </View>
    </Animated.View>
  );
}

export function PlanTab({ mood, onMonth, onTool }: { mood: Mood; onMonth: () => void; onTool: (k: string, seed?: string) => void }) {
  const { accent, accentDeep, glow } = mood;
  const Entry = ({ ic, c1, c2, title, sub, onPress }: any) => (
    <Press scale={0.985} onPress={onPress} style={{ marginBottom: 10 }}>
      <Pill radius={18} style={{ paddingVertical: 14, paddingHorizontal: 15, flexDirection: "row", alignItems: "center", gap: 13 }}>
        <GlossIcon c1={c1} c2={c2} size={42} radius={13}><Icon n={ic} s={19} c="#FFF" sw={1.8} /></GlossIcon>
        <View style={{ flex: 1 }}>
          <Text style={{ fontFamily: serif(500), fontSize: 16.5, color: INK }}>{title}</Text>
          <Text style={{ fontFamily: sans(400), fontSize: 12, color: GRAY, marginTop: 1 }}>{sub}</Text>
        </View>
        <Icon n="chevR" s={17} c={GRAY} />
      </Pill>
    </Press>
  );
  return (
    <View>
      <View style={{ marginHorizontal: 2, marginBottom: 12 }}><Label>Today</Label></View>
      <MyDay mood={mood} delay={0} />
      <AskMomentCard mood={mood} delay={60} onAsk={(seed: string) => onTool("ask", seed)} />
      <View style={{ marginHorizontal: 2, marginTop: 24, marginBottom: 12 }}><Label>Plan ahead</Label></View>
      <MyPanchang mood={mood} delay={120} onMonth={onMonth} />
      <Entry ic="compass" c1={glow} c2={accentDeep} title="Find a good day" sub="the best dates and times for something that matters" onPress={() => onTool("muhurat")} />
      <Entry ic="scan" c1={"#2E9C7E"} c2={"#1F7660"} title="Check my plans" sub="we'll check your calendar against your good and bad times" onPress={() => onTool("doctor")} />
      <Entry ic="capsule" c1={"#D98A2B"} c2={"#B26C18"} title="Time Capsule" sub="write to your future self, the sky delivers it" onPress={() => onTool("capsule")} />
    </View>
  );
}
