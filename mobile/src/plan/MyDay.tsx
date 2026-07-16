// MyDay.tsx — the schedule (astro-plan.tsx MyDay): live status, the SkyScene slider,
// add-a-task with auto-placement, and the placed-task list.
import React, { useEffect, useRef, useState } from "react";
import { View, Text, TextInput } from "react-native";
import Animated from "react-native-reanimated";
import { Mood } from "../theme";
import { DAY_CLOCK } from "../theme.demo";
import { INK, GRAY, WASH, HAIR, aA, sans, serif, cardStyle, shadow } from "../ui/palette";
import { Press, Label } from "../ui/atoms";
import { Icon } from "../ui/Icon";
import { useRiseIn, useGlowPulse, useSpin } from "../ui/motion";
import { SkyScene } from "./SkyScene";
import { nowH, fmtH, qFill } from "./util";

const W_DEMO = DAY_CLOCK.windows;
const SR_DEMO = DAY_CLOCK.sunrise || 6;
const span = 24;

function Spinner({ accent, accentDeep, size = 24 }: any) {
  const spin = useSpin(0.9);
  return (
    <View style={{ width: size, height: size }}>
      <Animated.View style={[{ position: "absolute", width: size, height: size, borderRadius: 999, borderWidth: 2, borderColor: aA(accent, 0.3), borderTopColor: accentDeep }, spin]} />
    </View>
  );
}

export function MyDay({ mood, delay = 0, live }: { mood: Mood; delay?: number; live?: any }) {
  const { accent, accentDeep } = mood;
  const riseA = useRiseIn(delay);
  // live timing (choghadiya windows + sunrise) drives the slider; fall back to demo when absent
  const W = live && live.windows && live.windows.length ? live.windows : W_DEMO;
  const SR = live ? live.sunrise : SR_DEMO;
  const dotA = useGlowPulse(2.4);
  const [now, setNow] = useState(() => { let h = nowH(); if (h < SR) h += 24; return h; });
  const [tasks, setTasks] = useState<any[]>([{ text: "Send the pitch", win: 3, done: false }]);
  const [draft, setDraft] = useState("");
  const [previewT, setPreviewT] = useState<number | null>(null);
  useEffect(() => { const id = setInterval(() => { let h = nowH(); if (h < SR) h += 24; setNow(h); }, 20000); return () => clearInterval(id); }, []);

  const bestWindowIdx = () => {
    const up = W.map((w: any, i: number) => ({ w, i })).filter(({ w }: any) => w.end > now && (w.q === "best" || w.q === "good"));
    if (up.length) { const b = up.find(({ w }: any) => w.q === "best") || up[0]; return b.i; }
    const any = W.map((w: any, i: number) => ({ w, i })).find(({ w }: any) => w.q === "best" || w.q === "good");
    return any ? any.i : 0;
  };
  const addTask = () => {
    const t = draft.trim(); if (!t) return;
    const born = Date.now();
    setTasks((a) => [...a, { text: t, win: bestWindowIdx(), done: false, born, placing: true }]);
    setDraft("");
    setTimeout(() => setTasks((a) => a.map((x) => (x.born === born ? { ...x, placing: false } : x))), 1300);
  };
  const toggle = (i: number) => setTasks((a) => a.map((t, k) => (k === i ? { ...t, done: !t.done } : t)));

  const nowWin = W.find((w: any) => now >= w.start && now < w.end) || W[0] || ({} as any);
  const nextStrong = W.find((w: any) => w.start > now && (w.q === "best" || w.q === "good"));
  const goodNow = nowWin.q === "best" || nowWin.q === "good";
  const mins = nextStrong ? Math.round((nextStrong.start - now) * 60) : 0;
  const statusBig = goodNow ? "A good window, right now" : "Best to hold a little";
  const statusSub = goodNow
    ? `clear sailing till ${fmtH(nowWin.end)}`
    : nextStrong ? `a stronger window opens at ${fmtH(nextStrong.start)}${mins > 0 && mins < 180 ? ` · in ${mins} min` : ""}` : "a quiet stretch, nothing to push";

  return (
    <Animated.View style={[{ marginBottom: 14 }, riseA]}>
      <View style={cardStyle({ padding: 18 })}>
        <View style={{ flexDirection: "row", alignItems: "center", justifyContent: "space-between" }}>
          <View>
            <Label c={aA(accentDeep, 0.9)}>My Day</Label>
            <Text style={{ fontFamily: serif(500), fontSize: 20, color: INK, marginTop: 2 }}>Schedule today</Text>
          </View>
          <Text style={{ fontFamily: sans(700), fontSize: 12, color: GRAY }}>{tasks.length ? `${tasks.filter((t) => !t.done).length} to do` : "open day"}</Text>
        </View>

        {/* live status */}
        <View style={{ flexDirection: "row", alignItems: "center", gap: 11, marginTop: 15, paddingVertical: 12, paddingHorizontal: 14, borderRadius: 16, backgroundColor: goodNow ? "rgba(62,156,122,0.09)" : aA(accent, 0.07), borderWidth: 1, borderColor: goodNow ? "rgba(62,156,122,0.26)" : aA(accent, 0.2) }}>
          <View style={{ width: 10, height: 10, alignItems: "center", justifyContent: "center" }}>
            <Animated.View style={[{ position: "absolute", width: 18, height: 18, borderRadius: 999, borderWidth: 2, borderColor: goodNow ? "#3E9C7A" : accentDeep }, dotA]} />
            <View style={{ width: 10, height: 10, borderRadius: 999, backgroundColor: goodNow ? "#3E9C7A" : accentDeep }} />
          </View>
          <View style={{ flex: 1 }}>
            <Text style={{ fontFamily: sans(800), fontSize: 14, color: INK }}>{statusBig}</Text>
            <Text style={{ fontFamily: serif(400), fontSize: 13, color: goodNow ? "#2E7D5B" : accentDeep, marginTop: 1 }}>{statusSub}</Text>
          </View>
        </View>

        {/* living sky slider */}
        <View style={{ marginTop: 18 }}>
          <SkyScene mood={mood} W={W} SR={SR} span={span} now={now} previewT={previewT} setPreviewT={setPreviewT} tasks={tasks} />
        </View>

        {/* add a task */}
        <View style={{ flexDirection: "row", alignItems: "center", gap: 8, marginTop: 16, paddingLeft: 15, paddingRight: 5, paddingVertical: 4, borderRadius: 999, backgroundColor: "#FFF", borderWidth: 1, borderColor: "rgba(0,0,0,0.05)", ...shadow({ y: 6, blur: 16, opacity: 0.12, elevation: 2 }) } as any}>
          <TextInput value={draft} onChangeText={setDraft} onSubmitEditing={addTask} placeholder="add a task, we'll place it well" placeholderTextColor={GRAY} underlineColorAndroid="transparent" style={{ flex: 1, fontFamily: sans(400), fontSize: 14, color: INK, paddingVertical: 8, outlineWidth: 0 } as any} />
          <Press scale={0.9} onPress={addTask}>
            <View style={{ backgroundColor: INK, borderRadius: 999, width: 36, height: 36, alignItems: "center", justifyContent: "center" }}>
              <Icon n="plus" s={17} c="#FFF" sw={2.2} />
            </View>
          </Press>
        </View>

        {/* placed tasks */}
        {tasks.length > 0 && (
          <View style={{ marginTop: 14, gap: 9 }}>
            {tasks.map((t, i) => { const w = W[t.win] || W[0]; return (
              <View key={i} style={{ flexDirection: "row", alignItems: "center", gap: 11 }}>
                {t.placing ? (
                  <Spinner accent={accent} accentDeep={accentDeep} size={24} />
                ) : (
                  <Press scale={0.9} onPress={() => toggle(i)}>
                    <View style={{ width: 24, height: 24, borderRadius: 999, alignItems: "center", justifyContent: "center", backgroundColor: t.done ? aA(accent, 0.16) : WASH, borderWidth: 1, borderColor: t.done ? aA(accentDeep, 0.35) : HAIR }}>
                      {t.done && <Icon n="check" s={13} c={accentDeep} sw={2.6} />}
                    </View>
                  </Press>
                )}
                <View style={{ flex: 1 }}>
                  <Text style={{ fontFamily: sans(700), fontSize: 14, color: t.done ? GRAY : INK, textDecorationLine: t.done ? "line-through" : "none" }}>{t.text}</Text>
                  <Text style={{ fontFamily: sans(400), fontSize: 11.5, color: t.placing ? accentDeep : GRAY, marginTop: 1, fontStyle: t.placing ? "italic" : "normal" }}>{t.placing ? "finding the best time…" : `${fmtH(w.start)} · ${w.name} · reminder 15 min before`}</Text>
                </View>
                {!t.placing && <View style={{ width: 8, height: 8, borderRadius: 999, backgroundColor: qFill(w.q) }} />}
              </View>
            ); })}
          </View>
        )}
      </View>
    </Animated.View>
  );
}
