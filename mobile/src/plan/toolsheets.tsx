// toolsheets.tsx — the Plan tool bottom-sheets (astro-plan.tsx): Muhurat, Calendar Doctor,
// Ask the Moment, Time Capsule + the shared Casting loader.
import React, { useEffect, useRef, useState } from "react";
import { View, Text, TextInput } from "react-native";
import Animated, { FadeIn } from "react-native-reanimated";
import { Mood } from "../theme";
import { MUHURAT, CAL_DOCTOR, ASK_MOMENT, TIME_CAPSULE } from "../theme.demo";
import { INK, INK2, GRAY, WASH, HAIR, ORANGE, aA, sans, serif, mono, shadow } from "../ui/palette";
import { askQuick, planMuhurta } from "../api/plan";
import { Press, Pill, Label } from "../ui/atoms";
import { Icon } from "../ui/Icon";
import { useSpin, useGlowPulse } from "../ui/motion";

function Casting({ mood, label, size = 84 }: any) {
  const { accent, accentDeep, glow } = mood;
  const spinA = useSpin(1);
  const spinB = useSpin(1.4);
  const coreA = useGlowPulse(1.2);
  return (
    <View style={{ alignItems: "center", gap: 14, paddingTop: 22, paddingBottom: 10 }}>
      <View style={{ width: size, height: size }}>
        <Animated.View style={[{ position: "absolute", width: size, height: size, borderRadius: 999, borderWidth: 2, borderColor: aA(accent, 0.28), borderTopColor: accentDeep }, spinA]} />
        <Animated.View style={[{ position: "absolute", top: 14, left: 14, width: size - 28, height: size - 28, borderRadius: 999, borderWidth: 2, borderColor: aA(accent, 0.2), borderBottomColor: accent }, spinB]} />
        <View style={{ position: "absolute", top: 0, left: 0, right: 0, bottom: 0, alignItems: "center", justifyContent: "center" }}>
          <Animated.View style={[{ width: 8, height: 8, borderRadius: 999, backgroundColor: accentDeep }, coreA]} />
        </View>
      </View>
      {label ? <Text style={{ fontFamily: mono(500), fontSize: 10.5, letterSpacing: 1.1, textTransform: "uppercase", color: GRAY }}>{label}</Text> : null}
    </View>
  );
}

export function MuhuratSheet({ mood }: { mood: Mood }) {
  const { accent, accentDeep, glow } = mood;
  const [pick, setPick] = useState<string | null>(null);
  const [custom, setCustom] = useState("");
  const [loading, setLoading] = useState(false);
  const [res, setRes] = useState<any[]>([]);
  const choose = async (e: string) => {
    setPick(e); setLoading(true);
    try { setRes(await planMuhurta(e)); } catch { setRes([]); }
    setLoading(false);
  };
  const go = () => { const t = custom.trim(); if (t) choose(t); };
  const shown = res.length ? res : (MUHURAT.results as any).default;  // fall back to demo on error
  return (
    <View>
      <Label c={aA(accentDeep, 0.9)}>Find a good day</Label>
      <Text style={{ fontFamily: serif(500), fontSize: 22, color: INK, marginTop: 6 }}>{pick ? `Best times to ${pick.toLowerCase()}` : "What's it for?"}</Text>
      {!pick ? (
        <>
          <View style={{ flexDirection: "row", flexWrap: "wrap", gap: 8, marginTop: 16 }}>
            {MUHURAT.events.slice(0, 6).map((e: string) => (
              <Press key={e} scale={0.95} onPress={() => choose(e)}>
                <Pill radius={999} style={{ paddingVertical: 9, paddingHorizontal: 15 }}><Text style={{ fontFamily: sans(700), fontSize: 13.5, color: INK }}>{e}</Text></Pill>
              </Press>
            ))}
          </View>
          <Text style={{ fontFamily: mono(500), fontSize: 9.5, letterSpacing: 0.8, textTransform: "uppercase", color: GRAY, marginTop: 18, marginBottom: 8 }}>or type your own</Text>
          <View style={{ flexDirection: "row", alignItems: "center", gap: 8, paddingLeft: 16, paddingRight: 5, paddingVertical: 4, borderRadius: 999, backgroundColor: "#FFF", borderWidth: 1, borderColor: "rgba(0,0,0,0.05)", ...shadow({ y: 6, blur: 16, opacity: 0.12, elevation: 2 }) } as any}>
            <TextInput value={custom} onChangeText={setCustom} onSubmitEditing={go} placeholder="e.g. move house, launch, propose" placeholderTextColor={GRAY} underlineColorAndroid="transparent" style={{ flex: 1, fontFamily: sans(400), fontSize: 14, color: INK, paddingVertical: 9, outlineWidth: 0 } as any} />
            <Press scale={0.9} onPress={go}><View style={{ backgroundColor: custom.trim() ? INK : "#D9D5CE", borderRadius: 999, width: 38, height: 38, alignItems: "center", justifyContent: "center" }}><Icon n="arrowR" s={17} c="#FFF" sw={2.2} /></View></Press>
          </View>
        </>
      ) : loading ? (
        <Casting mood={mood} label="reading the days ahead" />
      ) : (
        <>
          <View style={{ marginTop: 16, gap: 10 }}>
            {shown.map((r: any, i: number) => (
              <View key={i} style={{ flexDirection: "row", alignItems: "center", gap: 13, paddingVertical: 13, paddingHorizontal: 15, borderRadius: 16, backgroundColor: i === 0 ? aA(accent, 0.08) : WASH, borderWidth: 1, borderColor: i === 0 ? aA(accent, 0.24) : HAIR }}>
                <View style={{ width: 34, height: 34, borderRadius: 10, backgroundColor: accentDeep, alignItems: "center", justifyContent: "center" }}><Text style={{ fontFamily: serif(600), fontSize: 15, color: "#FFF" }}>{i + 1}</Text></View>
                <View style={{ flex: 1 }}>
                  <Text style={{ fontFamily: serif(500), fontSize: 16, color: INK }}>{r.date}</Text>
                  <Text style={{ fontFamily: sans(700), fontSize: 12.5, color: accentDeep, marginTop: 1 }}>{r.time}</Text>
                  <Text style={{ fontFamily: sans(400), fontSize: 11.5, color: GRAY, marginTop: 1 }}>{r.note}</Text>
                </View>
              </View>
            ))}
          </View>
          <Press scale={0.97} onPress={() => setPick(null)} style={{ marginTop: 14, alignSelf: "flex-start" }}><Text style={{ fontFamily: sans(700), fontSize: 12.5, color: accentDeep }}>← pick something else</Text></Press>
        </>
      )}
    </View>
  );
}

export function CalendarDoctorSheet({ mood }: { mood: Mood }) {
  const { accentDeep } = mood;
  const [fixed, setFixed] = useState<number[]>([]);
  const [scanning, setScanning] = useState(true);
  useEffect(() => { const id = setTimeout(() => setScanning(false), 1700); return () => clearTimeout(id); }, []);
  return (
    <View>
      <Label c={aA(accentDeep, 0.9)}>Check my plans</Label>
      <Text style={{ fontFamily: serif(500), fontSize: 22, color: INK, marginTop: 6 }}>Your next few events</Text>
      {scanning ? (
        <Casting mood={mood} label="checking your calendar" />
      ) : (
        <>
          <Text style={{ fontFamily: sans(400), fontSize: 12.5, color: GRAY, marginTop: 3 }}>we checked them against your good and bad times</Text>
          <View style={{ marginTop: 16, gap: 10 }}>
            {CAL_DOCTOR.map((e: any, i: number) => {
              const weak = e.status === "weak" && !fixed.includes(i);
              return (
                <View key={i} style={{ paddingVertical: 13, paddingHorizontal: 15, borderRadius: 16, backgroundColor: weak ? aA(ORANGE, 0.07) : WASH, borderWidth: 1, borderColor: weak ? aA(ORANGE, 0.3) : HAIR }}>
                  <View style={{ flexDirection: "row", alignItems: "center", gap: 10 }}>
                    <View style={{ width: 8, height: 8, borderRadius: 999, backgroundColor: fixed.includes(i) ? "#3E9C7A" : e.status === "weak" ? ORANGE : "#3E9C7A" }} />
                    <View style={{ flex: 1 }}>
                      <Text style={{ fontFamily: sans(700), fontSize: 14.5, color: INK }}>{e.title}</Text>
                      <Text style={{ fontFamily: sans(400), fontSize: 12, color: GRAY, marginTop: 1 }}>{fixed.includes(i) ? "moved to a better time" : `${e.when} · ${e.why}`}</Text>
                    </View>
                  </View>
                  {weak && (
                    <Press scale={0.97} onPress={() => setFixed((f) => [...f, i])} style={{ marginTop: 11 }}>
                      <View style={{ paddingVertical: 9, borderRadius: 11, alignItems: "center", backgroundColor: INK }}><Text style={{ fontFamily: sans(700), fontSize: 12.5, color: "#FFF" }}>{e.better}</Text></View>
                    </Press>
                  )}
                </View>
              );
            })}
          </View>
        </>
      )}
    </View>
  );
}

export function AskMomentSheet({ mood, onTalk, seed }: { mood: Mood; onTalk: (q: string) => void; seed?: string }) {
  const { accent, accentDeep } = mood;
  const [q, setQ] = useState(seed || "");
  const [phase, setPhase] = useState<"ask" | "casting" | "done">("ask");
  const [ans, setAns] = useState<any>(null);
  const cast = async () => {
    if (!q.trim()) return;
    setPhase("casting");
    try { setAns(await askQuick(q.trim())); }
    catch { setAns({ verdict: "Proceed gently", why: "I couldn't reach the sky just now — give it a moment and ask again." }); }
    setPhase("done");
  };
  const reset = () => { setPhase("ask"); setAns(null); setQ(""); };
  const vc = ans ? (ans.verdict === "Yes" ? "#2F8E66" : ans.verdict === "Wait" ? "#B5781A" : accentDeep) : accentDeep;
  return (
    <View>
      <Label c={aA(accentDeep, 0.9)}>Ask the Moment</Label>
      {phase !== "done" && (
        <>
          <Text style={{ fontFamily: serif(500), fontSize: 22, color: INK, marginTop: 6 }}>Ask, and the sky answers for right now</Text>
          <View style={{ flexDirection: "row", alignItems: "center", gap: 8, marginTop: 14, paddingLeft: 15, paddingRight: 5, paddingVertical: 4, borderRadius: 999, backgroundColor: "#FFF", borderWidth: 1, borderColor: "rgba(0,0,0,0.05)", ...shadow({ y: 6, blur: 16, opacity: 0.12, elevation: 2 }) } as any}>
            <TextInput value={q} onChangeText={setQ} placeholder="type your question…" placeholderTextColor={GRAY} underlineColorAndroid="transparent" style={{ flex: 1, fontFamily: sans(400), fontSize: 14, color: INK, paddingVertical: 9, outlineWidth: 0 } as any} />
          </View>
          <View style={{ flexDirection: "row", flexWrap: "wrap", gap: 7, marginTop: 12 }}>
            {ASK_MOMENT.samples.map((s: string) => (
              <Press key={s} scale={0.95} onPress={() => setQ(s)}>
                <View style={{ paddingVertical: 7, paddingHorizontal: 13, borderRadius: 999, backgroundColor: WASH, borderWidth: 1, borderColor: HAIR }}><Text style={{ fontFamily: sans(600), fontSize: 12.5, color: INK2 }}>{s}</Text></View>
              </Press>
            ))}
          </View>
          <Press scale={0.97} onPress={cast} style={{ marginTop: 18 }}>
            <View style={{ paddingVertical: 14, borderRadius: 14, alignItems: "center", backgroundColor: q.trim() ? INK : WASH, ...(q.trim() ? shadow({ y: 9, blur: 20, opacity: 0.38, color: INK, elevation: 4 }) : null) } as any}>
              <Text style={{ fontFamily: sans(700), fontSize: 14.5, color: q.trim() ? "#FFF" : GRAY }}>{phase === "casting" ? "casting…" : "Cast"}</Text>
            </View>
          </Press>
          {phase === "casting" && <Casting mood={mood} size={90} />}
        </>
      )}
      {phase === "done" && ans && (
        <Animated.View entering={FadeIn.duration(400)}>
          <Text style={{ fontFamily: sans(400), fontSize: 13.5, color: GRAY, marginTop: 8, fontStyle: "italic" }}>“{q}”</Text>
          <Text style={{ fontFamily: serif(500), fontSize: 40, color: vc, letterSpacing: -1, marginTop: 10 }}>{ans.verdict}.</Text>
          <Text style={{ fontFamily: serif(400), fontSize: 16, lineHeight: 24, color: INK2, marginTop: 8 }}>{ans.why}</Text>
          <Text style={{ fontFamily: sans(400), fontSize: 11.5, color: GRAY, marginTop: 10, fontStyle: "italic" }}>a one-time read for this exact moment</Text>
          <View style={{ flexDirection: "row", gap: 10, marginTop: 18 }}>
            <Press scale={0.97} onPress={() => onTalk(q)} style={{ flex: 1 }}>
              <View style={{ paddingVertical: 13, borderRadius: 13, alignItems: "center", backgroundColor: INK }}><Text style={{ fontFamily: sans(700), fontSize: 13.5, color: "#FFF" }}>Talk it through →</Text></View>
            </Press>
            <Press scale={0.95} onPress={reset}>
              <Pill radius={13} style={{ paddingVertical: 13, paddingHorizontal: 16 }}><Text style={{ fontFamily: sans(700), fontSize: 13.5, color: INK }}>Ask again</Text></Pill>
            </Press>
          </View>
        </Animated.View>
      )}
    </View>
  );
}

export function TimeCapsuleSheet({ mood }: { mood: Mood }) {
  const { accent, accentDeep, glow } = mood;
  const [note, setNote] = useState("");
  const [when, setWhen] = useState<string | null>(null);
  const [phase, setPhase] = useState<"write" | "sealing" | "sealed">("write");
  const seal = () => { if (!note.trim() || !when) return; setPhase("sealing"); setTimeout(() => setPhase("sealed"), 2000); };
  const sealSpin = useSpin(1.1);

  if (phase === "sealing") {
    return (
      <View style={{ alignItems: "center", paddingTop: 26, paddingBottom: 18 }}>
        <View style={{ width: 92, height: 92 }}>
          <Animated.View style={[{ position: "absolute", width: 92, height: 92, borderRadius: 999, borderWidth: 2, borderColor: aA(accent, 0.25), borderTopColor: accentDeep }, sealSpin]} />
          <View style={{ position: "absolute", top: 22, left: 22, width: 48, height: 48, borderRadius: 999, backgroundColor: accentDeep, alignItems: "center", justifyContent: "center" }}><Icon n="capsule" s={24} c="#FFF" sw={1.7} /></View>
        </View>
        <Text style={{ fontFamily: serif(400, true), fontSize: 17, color: INK, marginTop: 22 }}>sealing it to the sky…</Text>
      </View>
    );
  }
  if (phase === "sealed") {
    return (
      <Animated.View entering={FadeIn.duration(400)} style={{ alignItems: "center", paddingTop: 14, paddingBottom: 6 }}>
        <View style={{ width: 76, height: 76, borderRadius: 999, backgroundColor: accentDeep, alignItems: "center", justifyContent: "center", ...shadow({ y: 10, blur: 30, opacity: 0.5, color: accentDeep, elevation: 6 }) } as any}><Icon n="capsule" s={34} c="#FFF" sw={1.6} /></View>
        <Text style={{ fontFamily: serif(500), fontSize: 21, color: INK, marginTop: 18 }}>Sealed.</Text>
        <Text style={{ fontFamily: serif(400, true), fontSize: 15, color: GRAY, marginTop: 6, paddingHorizontal: 20, textAlign: "center" }}>The sky will bring it back to you {when}.</Text>
      </Animated.View>
    );
  }
  return (
    <View>
      <Label c={aA(accentDeep, 0.9)}>Time Capsule</Label>
      <Text style={{ fontFamily: serif(500), fontSize: 22, color: INK, marginTop: 6 }}>Write to your future self</Text>
      <TextInput value={note} onChangeText={setNote} placeholder="what do you want them to remember?" placeholderTextColor={GRAY} multiline underlineColorAndroid="transparent" style={{ marginTop: 14, padding: 15, minHeight: 100, borderWidth: 1, borderColor: HAIR, borderRadius: 16, backgroundColor: WASH, color: INK, fontFamily: serif(400), fontSize: 16, lineHeight: 24, textAlignVertical: "top", outlineWidth: 0 } as any} />
      <View style={{ marginTop: 14, marginBottom: 8 }}><Label>Deliver on</Label></View>
      <Press scale={0.98} onPress={() => setWhen("on a date you pick")}>
        <Pill radius={13} style={{ paddingVertical: 12, paddingHorizontal: 15, flexDirection: "row", alignItems: "center", gap: 11, marginBottom: 10, borderColor: when === "on a date you pick" ? aA(accentDeep, 0.4) : "rgba(0,0,0,0.05)" }}>
          <Icon n="cal" s={18} c={accentDeep} sw={1.8} />
          <Text style={{ flex: 1, fontFamily: sans(700), fontSize: 14, color: INK }}>Pick a date</Text>
          {when === "on a date you pick" && <Icon n="check" s={16} c={accentDeep} sw={2.4} />}
        </Pill>
      </Press>
      <Text style={{ fontFamily: sans(400), fontSize: 12, color: GRAY, marginHorizontal: 2, marginBottom: 8 }}>or pick a moment:</Text>
      <View style={{ gap: 8 }}>
        {TIME_CAPSULE.moments.map((m: string) => {
          const on = when === m;
          return (
            <Press key={m} scale={0.98} onPress={() => setWhen(m)}>
              <View style={{ paddingVertical: 12, paddingHorizontal: 15, borderRadius: 13, backgroundColor: on ? aA(accent, 0.1) : WASH, borderWidth: 1, borderColor: on ? aA(accentDeep, 0.35) : HAIR, flexDirection: "row", alignItems: "center", gap: 10 }}>
                <View style={{ width: 7, height: 7, borderRadius: 999, backgroundColor: on ? accentDeep : GRAY }} />
                <Text style={{ flex: 1, fontFamily: serif(400), fontSize: 15, color: INK }}>{m}</Text>
                {on && <Icon n="check" s={15} c={accentDeep} sw={2.4} />}
              </View>
            </Press>
          );
        })}
      </View>
      <Press scale={0.97} onPress={seal} style={{ marginTop: 18 }}>
        <View style={{ paddingVertical: 14, borderRadius: 14, alignItems: "center", backgroundColor: note.trim() && when ? INK : WASH, ...(note.trim() && when ? shadow({ y: 9, blur: 20, opacity: 0.38, color: INK, elevation: 4 }) : null) } as any}>
          <Text style={{ fontFamily: sans(700), fontSize: 14.5, color: note.trim() && when ? "#FFF" : GRAY }}>Seal it</Text>
        </View>
      </Press>
      {TIME_CAPSULE.shelf.length > 0 && (
        <View style={{ marginTop: 20, paddingTop: 16, borderTopWidth: 1, borderTopColor: HAIR }}>
          <Label>Your shelf</Label>
          <View style={{ marginTop: 10, gap: 9 }}>
            {TIME_CAPSULE.shelf.map((c: any, i: number) => (
              <View key={i} style={{ flexDirection: "row", alignItems: "center", gap: 11 }}>
                <View style={{ width: 30, height: 30, borderRadius: 9, alignItems: "center", justifyContent: "center", backgroundColor: c.state === "landed" ? accentDeep : WASH, borderWidth: c.state === "landed" ? 0 : 1, borderColor: HAIR }}><Icon n="capsule" s={15} c={c.state === "landed" ? "#FFF" : GRAY} sw={1.7} /></View>
                <View style={{ flex: 1 }}>
                  <Text numberOfLines={1} style={{ fontFamily: serif(400), fontSize: 14, color: INK }}>{c.state === "landed" ? c.note : "a sealed note"}</Text>
                  <Text style={{ fontFamily: sans(400), fontSize: 11, color: GRAY, marginTop: 1 }}>{c.state === "landed" ? `arrived ${c.on}` : `for ${c.to}`}</Text>
                </View>
                {c.state === "sealed" && <Text style={{ fontFamily: mono(500), fontSize: 9, letterSpacing: 0.8, textTransform: "uppercase", color: GRAY }}>sealed</Text>}
              </View>
            ))}
          </View>
        </View>
      )}
    </View>
  );
}
