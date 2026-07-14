// JournalScreen.tsx — the Mirror (astro-screens.tsx JournalScreen): private writing page,
// voice overlay (faked), and the sage2 "done" view. Distress guard wired into save().
import React, { useEffect, useRef, useState } from "react";
import { View, Text, Image, TextInput, Pressable, KeyboardAvoidingView, Platform } from "react-native";
import Animated, { FadeIn } from "react-native-reanimated";
import { LinearGradient } from "expo-linear-gradient";
import { BlurView } from "expo-blur";
import Svg, { Defs, LinearGradient as SvgLinear, Stop, Path } from "react-native-svg";
import { Mood, DATE, MIRROR } from "../theme";
import { PAPER, INK, GRAY, WASH, HAIR, aA, sans, serif, mono, shadow } from "../ui/palette";
import { Press, Pill, Label, RadialGlow } from "../ui/atoms";
import { Icon } from "../ui/Icon";
import { useFloatY, useHalo, useGlowPulse } from "../ui/motion";
import { isDistress } from "../safety";

const sage2 = require("../assets/sage2.png");

function Crescent({ accent }: { accent: string }) {
  return (
    <Svg width={26} height={26} viewBox="0 0 24 24" fill="none">
      <Defs><SvgLinear id="jrnCr" x1="0" y1="0" x2="1" y2="1"><Stop offset="0" stopColor="#FFF6E4" /><Stop offset="1" stopColor={accent} /></SvgLinear></Defs>
      <Path d="M18.4 4.3 A9 9 0 1 0 19.8 16.6 A7 7 0 1 1 18.4 4.3 Z" fill="url(#jrnCr)" />
    </Svg>
  );
}

export function JournalScreen({ mood, onBack, onSave, onTalk, insetTop = 44 }: any) {
  const { accent, accentDeep, glow } = mood;
  const [text, setText] = useState("");
  const [done, setDone] = useState<string | null>(null);
  const [rec, setRec] = useState(false);
  const [paused, setPaused] = useState(false);
  const [secs, setSecs] = useState(0);
  const ph = useRef((MIRROR.placeholders || ["Say it here."])[0]).current;
  const floatA = useFloatY(5);
  const haloA = useHalo(6);
  const micHaloA = useGlowPulse(1.8);

  useEffect(() => { if (!rec || paused) return; const id = setInterval(() => setSecs((s) => s + 1), 1000); return () => clearInterval(id); }, [rec, paused]);
  const startRec = () => { setSecs(0); setPaused(false); setRec(true); };
  const sendRec = () => { const vn = "I've been carrying a lot this week, and saying it out loud helps more than I expected."; setText((t) => (t ? t + " " : "") + vn); setRec(false); };
  const mmss = `${String(Math.floor(secs / 60)).padStart(2, "0")}:${String(secs % 60).padStart(2, "0")}`;
  const save = () => {
    if (!text.trim()) return;
    // safety: crisis language routes to the gentle KIRAN pointer (never removed)
    const resp = isDistress(text) ? `${MIRROR.distress.line} ${MIRROR.distress.help}` : (MIRROR.responses || {}).tender || "Thank you for trusting me with that.";
    setDone(resp);
    onSave && onSave();
  };

  return (
    <KeyboardAvoidingView style={{ flex: 1, backgroundColor: PAPER }} behavior={Platform.OS === "ios" ? "padding" : "height"}>
      <LinearGradient colors={[aA(glow, 0.16), PAPER, PAPER]} locations={[0, 0.34, 1]} start={{ x: 0, y: 0 }} end={{ x: 0, y: 1 }} style={{ position: "absolute", top: 0, left: 0, right: 0, bottom: 0 } as any} />
      <RadialGlow color={glow} size={280} opacity={0.32} style={{ position: "absolute", top: -70, alignSelf: "center" }} />
      {/* header */}
      <View style={{ paddingTop: insetTop + 6, paddingHorizontal: 18, paddingBottom: 8, flexDirection: "row", alignItems: "center", justifyContent: "space-between" }}>
        <Press scale={0.9} onPress={onBack}>
          <Pill radius={999} style={{ width: 42, height: 42, alignItems: "center", justifyContent: "center" }}><Icon n={done ? "close" : "arrowL"} s={19} c={INK} /></Pill>
        </Press>
        <Label c={aA(accentDeep, 0.9)}>The Mirror</Label>
        <View style={{ width: 42 }} />
      </View>

      {done ? (
        <View style={{ flex: 1, alignItems: "center", justifyContent: "center", paddingHorizontal: 30 }}>
          <View style={{ width: 118, height: 140, alignItems: "center", justifyContent: "center" }}>
            <Animated.View style={[{ position: "absolute", width: 104, height: 104, borderRadius: 999, backgroundColor: aA(glow, 0.26) }, haloA]} />
            <Animated.View style={[{ width: 118, height: 140 }, floatA]}>
              <Image source={sage2} resizeMode="contain" style={{ width: "100%", height: "100%" }} />
            </Animated.View>
          </View>
          <Text style={{ fontFamily: serif(400, true), fontSize: 22, color: INK, marginTop: 24, lineHeight: 33, textAlign: "center" }}>{done}</Text>
          <Text style={{ fontFamily: mono(500), fontSize: 10, letterSpacing: 1.2, textTransform: "uppercase", color: GRAY, marginTop: 20 }}>you wrote today</Text>
          <Press scale={0.97} onPress={() => onTalk("")} style={{ marginTop: 26 }}>
            <Pill radius={999} style={{ flexDirection: "row", alignItems: "center", gap: 8, paddingVertical: 12, paddingHorizontal: 20 }}>
              <Text style={{ fontFamily: sans(700), fontSize: 14, color: INK }}>talk about it?</Text>
              <Icon n="arrowR" s={15} c={accentDeep} sw={2} />
            </Pill>
          </Press>
        </View>
      ) : (
        <>
          <View style={{ paddingHorizontal: 22, paddingTop: 14 }}>
            <View style={{ flexDirection: "row", alignItems: "center", gap: 9 }}>
              <Crescent accent={accent} />
              <Text style={{ fontFamily: mono(500), fontSize: 10, letterSpacing: 1.2, textTransform: "uppercase", color: aA(accentDeep, 0.8) }}>{DATE}</Text>
            </View>
            <Text style={{ fontFamily: serif(500), fontSize: 27, color: INK, letterSpacing: -0.4, marginTop: 12 }}>What's on your mind?</Text>
            <Text style={{ fontFamily: serif(400, true), fontSize: 14.5, color: aA(accentDeep, 0.85), marginTop: 6 }}>no pressure, no one else sees this</Text>
          </View>
          {/* ruled cream page */}
          <View style={{ flex: 1, marginHorizontal: 18, marginTop: 16, borderTopLeftRadius: 20, borderTopRightRadius: 20, backgroundColor: "#FFFDFB", borderWidth: 1, borderBottomWidth: 0, borderColor: HAIR, overflow: "hidden" }}>
            <View style={{ position: "absolute", top: 0, left: 0, right: 0, bottom: 0 }} pointerEvents="none">
              {Array.from({ length: 14 }).map((_, i) => <View key={i} style={{ position: "absolute", left: 0, right: 0, top: 16 + i * 34, height: 1, backgroundColor: aA(accentDeep, 0.07) }} />)}
            </View>
            <TextInput value={text} onChangeText={setText} placeholder={ph} placeholderTextColor={aA(GRAY, 0.8)} multiline underlineColorAndroid="transparent" style={{ flex: 1, padding: 16, paddingTop: 16, fontFamily: serif(400), fontSize: 18, lineHeight: 34, color: INK, textAlignVertical: "top", outlineWidth: 0 } as any} />
          </View>
          <View style={{ paddingHorizontal: 18, paddingTop: 12, paddingBottom: 30, flexDirection: "row", alignItems: "center", gap: 12, backgroundColor: "#FFFBF6", borderTopWidth: 1, borderTopColor: HAIR }}>
            <Press scale={0.92} onPress={startRec}>
              <View style={{ width: 50, height: 50, borderRadius: 999, alignItems: "center", justifyContent: "center", backgroundColor: aA(accent, 0.12), borderWidth: 1, borderColor: aA(accent, 0.3) }}><Icon n="mic" s={21} c={accentDeep} sw={1.8} /></View>
            </Press>
            <Press scale={0.98} onPress={save} style={{ flex: 1 }}>
              <View style={{ paddingVertical: 15, borderRadius: 999, alignItems: "center", backgroundColor: text.trim() ? INK : WASH, ...(text.trim() ? shadow({ y: 9, blur: 20, opacity: 0.38, color: INK, elevation: 4 }) : null) } as any}>
                <Text style={{ fontFamily: sans(700), fontSize: 14.5, color: text.trim() ? "#FFF" : GRAY }}>Leave it with me</Text>
              </View>
            </Press>
          </View>
        </>
      )}

      {/* voice overlay */}
      {rec && (
        <Animated.View entering={FadeIn.duration(300)} style={{ position: "absolute", top: 0, left: 0, right: 0, bottom: 0, zIndex: 20, alignItems: "center", justifyContent: "center" }}>
          <BlurView intensity={30} tint="dark" style={{ position: "absolute", top: 0, left: 0, right: 0, bottom: 0, backgroundColor: aA("#141410", 0.4) }} />
          <Text style={{ fontFamily: mono(500), fontSize: 10.5, letterSpacing: 1.4, textTransform: "uppercase", color: aA("#FFF", 0.75) }}>{paused ? "paused" : "listening"}</Text>
          <View style={{ width: 116, height: 116, marginVertical: 22, alignItems: "center", justifyContent: "center" }}>
            {!paused && <Animated.View style={[{ position: "absolute", width: 116, height: 116, borderRadius: 999, backgroundColor: aA(glow, 0.4) }, micHaloA]} />}
            <View style={{ width: 78, height: 78, borderRadius: 999, alignItems: "center", justifyContent: "center", backgroundColor: accentDeep, ...shadow({ y: 12, blur: 30, opacity: 0.5, color: accentDeep, elevation: 6 }) } as any}><Icon n="mic" s={30} c="#FFF" sw={1.7} /></View>
          </View>
          <View style={{ flexDirection: "row", alignItems: "center", gap: 4, height: 40 }}>
            {[0.5, 0.8, 0.4, 1, 0.6, 0.9, 0.35, 0.75, 0.55, 0.95, 0.45, 0.7, 0.85].map((h, i) => <View key={i} style={{ width: 4, height: 34 * h, borderRadius: 2, backgroundColor: aA("#FFF", 0.9) }} />)}
          </View>
          <Text style={{ fontFamily: mono(500), fontSize: 15, letterSpacing: 1, color: "#FFF", marginTop: 18 }}>{mmss}</Text>
          <View style={{ flexDirection: "row", alignItems: "center", gap: 22, marginTop: 30 }}>
            <Press scale={0.9} onPress={() => setRec(false)}><View style={{ width: 54, height: 54, borderRadius: 999, alignItems: "center", justifyContent: "center", backgroundColor: aA("#FFF", 0.14), borderWidth: 1, borderColor: aA("#FFF", 0.3) }}><Icon n="trash" s={21} c="#FFF" sw={1.8} /></View></Press>
            <Press scale={0.92} onPress={() => setPaused((p) => !p)}><View style={{ width: 66, height: 66, borderRadius: 999, alignItems: "center", justifyContent: "center", backgroundColor: "#FFF", ...shadow({ y: 8, blur: 20, opacity: 0.28, elevation: 5 }) } as any}><Icon n={paused ? "mic" : "pause"} s={26} c={INK} sw={2} /></View></Press>
            <Press scale={0.9} onPress={sendRec}><View style={{ width: 54, height: 54, borderRadius: 999, alignItems: "center", justifyContent: "center", backgroundColor: accentDeep, ...shadow({ y: 8, blur: 20, opacity: 0.5, color: accentDeep, elevation: 5 }) } as any}><Icon n="check" s={23} c="#FFF" sw={2.4} /></View></Press>
          </View>
          <View style={{ flexDirection: "row", gap: 42, marginTop: 11 }}>
            <Text style={{ fontFamily: sans(400), fontSize: 11, color: aA("#FFF", 0.65) }}>delete</Text>
            <Text style={{ fontFamily: sans(400), fontSize: 11, color: aA("#FFF", 0.65) }}>{paused ? "resume" : "pause"}</Text>
            <Text style={{ fontFamily: sans(400), fontSize: 11, color: aA("#FFF", 0.65) }}>done</Text>
          </View>
        </Animated.View>
      )}
    </KeyboardAvoidingView>
  );
}
