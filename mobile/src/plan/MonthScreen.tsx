// MonthScreen.tsx — full-screen month calendar (astro-plan.tsx MonthScreen).
import React, { useState } from "react";
import { View, Text, ScrollView } from "react-native";
import Animated from "react-native-reanimated";
import { Mood, MONTH, dayDetail } from "../theme";
import { PAPER, INK, INK2, GRAY, WASH, HAIR, aA, sans, serif, mono } from "../ui/palette";
import { Press, Pill, Label } from "../ui/atoms";
import { Icon } from "../ui/Icon";
import { Sheet } from "../ui/Sheet";
import { useRiseIn } from "../ui/motion";
import { qColor, qWord } from "./util";

const MARK_C: any = { moon: "#7C8AA0", festival: "#D98A2B", grahan: "#5B4FC4", dasha: "#2E9C7E", task: "#C2724E" };

export function MonthScreen({ mood, onBack, insetTop = 44 }: any) {
  const { accent, accentDeep } = mood;
  const [sel, setSel] = useState<number | null>(null);
  const M = MONTH;
  const detail = sel != null ? dayDetail(sel) : null;
  const rise0 = useRiseIn(0);
  const cells: any[] = [];
  for (let i = 0; i < M.startWeekday; i++) cells.push(null);
  M.days.forEach((d: any) => cells.push(d));

  return (
    <View style={{ position: "absolute", top: 0, left: 0, right: 0, bottom: 0, backgroundColor: PAPER }}>
      <View style={{ position: "absolute", top: insetTop + 4, left: 18, right: 18, zIndex: 10, flexDirection: "row", alignItems: "center", justifyContent: "space-between" }}>
        <Press scale={0.9} onPress={onBack}><Pill radius={999} style={{ width: 42, height: 42, alignItems: "center", justifyContent: "center" }}><Icon n="arrowL" s={19} c={INK} /></Pill></Press>
        <Press scale={0.95}><Pill radius={999} style={{ paddingVertical: 9, paddingHorizontal: 14, flexDirection: "row", alignItems: "center", gap: 7 }}><Icon n="sync" s={15} c={accentDeep} sw={1.9} /><Text style={{ fontFamily: sans(700), fontSize: 12.5, color: INK }}>Sync good days</Text></Pill></Press>
      </View>
      <ScrollView contentContainerStyle={{ paddingTop: insetTop + 60, paddingHorizontal: 16, paddingBottom: 40 }} showsVerticalScrollIndicator={false}>
        <Animated.View style={rise0}>
          <Label c={aA(accentDeep, 0.9)}>Your Panchang</Label>
          <Text style={{ fontFamily: serif(500), fontSize: 30, color: INK, letterSpacing: -0.6, marginTop: 2 }}>{M.name}</Text>
        </Animated.View>
        {/* weekday header */}
        <View style={{ flexDirection: "row", marginTop: 18 }}>
          {["S", "M", "T", "W", "T", "F", "S"].map((d, i) => <View key={i} style={{ width: `${100 / 7}%`, alignItems: "center" }}><Text style={{ fontFamily: mono(600), fontSize: 10, color: GRAY }}>{d}</Text></View>)}
        </View>
        {/* grid */}
        <View style={{ flexDirection: "row", flexWrap: "wrap", marginTop: 8 }}>
          {cells.map((d, i) => (
            <View key={i} style={{ width: `${100 / 7}%`, padding: 3 }}>
              {d === null ? <View style={{ aspectRatio: 1 }} /> : (
                <Press scale={0.92} onPress={() => setSel(d.n)}>
                  <View style={{ aspectRatio: 1, borderRadius: 12, alignItems: "center", justifyContent: "center", backgroundColor: d.quality === "good" ? aA(accent, 0.12) : d.quality === "low" ? WASH : "#FFF", borderWidth: 1, borderColor: sel === d.n ? accentDeep : d.quality === "good" ? aA(accent, 0.28) : HAIR }}>
                    <Text style={{ fontFamily: serif(500), fontSize: 15, color: d.quality === "low" ? GRAY : INK }}>{d.n}</Text>
                    <View style={{ position: "absolute", bottom: 5, flexDirection: "row", gap: 2 }}>
                      <View style={{ width: 4, height: 4, borderRadius: 999, backgroundColor: qColor(d.quality) }} />
                      {d.mark && <View style={{ width: 4, height: 4, borderRadius: 999, backgroundColor: MARK_C[d.mark.kind] || GRAY }} />}
                    </View>
                  </View>
                </Press>
              )}
            </View>
          ))}
        </View>
        {/* legend */}
        <View style={{ flexDirection: "row", flexWrap: "wrap", gap: 12, marginTop: 18, paddingVertical: 14, paddingHorizontal: 16, borderRadius: 16, backgroundColor: WASH, borderWidth: 1, borderColor: HAIR }}>
          {[["Festival", MARK_C.festival], ["Full / new moon", MARK_C.moon], ["Grahan", MARK_C.grahan], ["Dasha change", MARK_C.dasha], ["Your task", MARK_C.task]].map(([l, c]: any) => (
            <View key={l} style={{ flexDirection: "row", alignItems: "center", gap: 6 }}><View style={{ width: 7, height: 7, borderRadius: 999, backgroundColor: c }} /><Text style={{ fontFamily: sans(600), fontSize: 11.5, color: INK2 }}>{l}</Text></View>
          ))}
        </View>
      </ScrollView>

      <Sheet open={sel != null} onClose={() => setSel(null)}>
        {detail && (
          <View>
            <Label c={aA(accentDeep, 0.9)}>{M.name.split(" ")[0]} {detail.n}</Label>
            <View style={{ flexDirection: "row", alignItems: "center", gap: 9, marginTop: 6 }}>
              <View style={{ width: 10, height: 10, borderRadius: 999, backgroundColor: qColor(detail.quality) }} />
              <Text style={{ fontFamily: serif(500), fontSize: 23, color: INK }}>{qWord(detail.quality)}</Text>
            </View>
            {detail.mark && (
              <View style={{ alignSelf: "flex-start", flexDirection: "row", alignItems: "center", gap: 6, marginTop: 10, paddingVertical: 5, paddingHorizontal: 11, borderRadius: 999, backgroundColor: WASH, borderWidth: 1, borderColor: HAIR }}>
                <View style={{ width: 6, height: 6, borderRadius: 999, backgroundColor: MARK_C[detail.mark.kind] || GRAY }} />
                <Text style={{ fontFamily: sans(700), fontSize: 12.5, color: INK }}>{detail.mark.label}</Text>
              </View>
            )}
            <Text style={{ fontFamily: serif(400), fontSize: 16, lineHeight: 24, color: INK2, marginTop: 14 }}>{detail.why}</Text>
            <View style={{ flexDirection: "row", gap: 10, marginTop: 16 }}>
              <View style={{ flex: 1, paddingVertical: 11, paddingHorizontal: 13, borderRadius: 13, backgroundColor: aA(accent, 0.08), borderWidth: 1, borderColor: aA(accent, 0.2) }}><Label c={accentDeep}>Good times</Label><Text style={{ fontFamily: serif(500), fontSize: 15, color: INK, marginTop: 4 }}>{detail.good}</Text></View>
              <View style={{ flex: 1, paddingVertical: 11, paddingHorizontal: 13, borderRadius: 13, backgroundColor: WASH, borderWidth: 1, borderColor: HAIR }}><Label>Hold off</Label><Text style={{ fontFamily: serif(500), fontSize: 15, color: INK, marginTop: 4 }}>{detail.low}</Text></View>
            </View>
          </View>
        )}
      </Sheet>
    </View>
  );
}
