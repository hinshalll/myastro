// ChatScreen.tsx — Chat with Sage (astro-screens.tsx ChatScreen). Proactive opener, working
// input with keyword replies + typing beat, 3-state Sage crossfade, and the KIRAN distress
// guard (MUST survive the port; server-authoritative in production).
import React, { useEffect, useRef, useState } from "react";
import { View, Text, Image, Pressable, ScrollView, TextInput, KeyboardAvoidingView, Platform } from "react-native";
import Animated, { FadeIn, useSharedValue, useAnimatedStyle, withTiming } from "react-native-reanimated";
import { Mood } from "../theme";
import { getFirstName } from "../api/profile";
import { PAPER, INK, GRAY, HAIR, aA, sans, serif, mono } from "../ui/palette";
import { Press, Pill } from "../ui/atoms";
import { Icon } from "../ui/Icon";
import { useFloatY, useHalo, useReduceMotion } from "../ui/motion";
import { isDistress } from "../safety";

const sage1 = require("../assets/chatsage1.png");
const sage2 = require("../assets/chatsage2.png");
const sage3 = require("../assets/chatsage3.png");

// A FUNCTION, not a const array. As a module-scope array with `${NAME}` baked in, the demo name
// "Aarav" was frozen at import and greeted every real user by the wrong name — the most visible
// fake in the app. Taking the name at call time means it follows the real profile.
// NOTE: the openers themselves are still placeholder copy (they claim memories we do not have
// yet). This screen stays unwired until the RAG/memory path lands — see DEMO_DATA_LEDGER.md.
const openersFor = (n: string) => [
  { kind: "a pattern I noticed", lines: [`Hey ${n}. I've been noticing something. You tend to feel lighter on the days you write to me in the morning. Today's a soft one, so maybe start there?`], chips: ["Tell me more", "Maybe later"] },
  { kind: "looking back", lines: [`Hi ${n}. A week ago you were dreading that conversation at work. I've been wondering, how did it land?`], chips: ["It went okay", "Still on my mind"] },
  { kind: "just checking in", lines: [`Hey ${n}. It's been a couple of quiet days. No agenda, I just wanted you to know I'm here. How are you, really?`], chips: ["I'm alright", "Not my best"] },
];
const REPLY = {
  low: ["That sounds heavy, and I'm glad you told me. You don't have to carry today all at once — just the next hour.", "I hear you. With your Moon where it is right now, these days ask more of you than usual. Go slow, it's allowed.", "Thank you for being honest with me. Let's keep today small and kind. What would feel like a little relief?"],
  high: ["I love hearing that. Hold onto this one — days like this are worth remembering.", "That makes me happy. The sky's with you today, so let it carry you a little further.", "Beautiful. Let yourself enjoy it fully, no guilt attached."],
  ask: ["With the day this tender, I'd wait until late morning — things land softer then.", "It's a mixed moment. You can move ahead, just gently and without forcing it.", "The timing's a little rushed right now. Give it an hour and it eases."],
  warm: ["I'm here. Tell me more whenever you're ready.", "That tracks with how the day's moving. What's underneath it, do you think?", "Mm. Sit with that for a second — I'm not going anywhere.", "I understand. Want to just talk it through, no fixing?"],
};
function pickReply(text: string, i: number): { t: string; safe?: boolean } {
  const t = text.toLowerCase();
  if (isDistress(text)) return { safe: true, t: "I'm really glad you told me, and I don't want you to be alone with this. Please reach out to someone who can sit with you right now — in India you can call KIRAN at 1800-599-0019, any time, free. I'm here too, and I'm not going anywhere." };
  if (/\b(low|tired|heavy|sad|down|anxious|stressed|awful|exhausted|lonely|hurt)\b/.test(t)) return { t: REPLY.low[i % REPLY.low.length] };
  if (/\b(good|great|happy|excited|wonderful|amazing|better|grateful|calm)\b/.test(t)) return { t: REPLY.high[i % REPLY.high.length] };
  if (t.includes("?") || /^should i|^is it|^can i|^will /.test(t)) return { t: REPLY.ask[i % REPLY.ask.length] };
  return { t: REPLY.warm[i % REPLY.warm.length] };
}

function SageImg({ src, active }: { src: any; active: boolean }) {
  const o = useSharedValue(active ? 1 : 0);
  useEffect(() => { o.value = withTiming(active ? 1 : 0, { duration: 180 }); }, [active]);
  const a = useAnimatedStyle(() => ({ opacity: o.value }));
  return <Animated.Image source={src} resizeMode="contain" style={[{ position: "absolute", top: 0, left: 0, right: 0, bottom: 0, width: "100%", height: "100%" }, a]} />;
}

function Dot({ delay }: { delay: number }) {
  const reduce = useReduceMotion();
  const o = useSharedValue(0.25);
  useEffect(() => {
    if (reduce) return;
    const loop = () => { o.value = withTiming(0.85, { duration: 400 }, () => { o.value = withTiming(0.25, { duration: 400 }); }); };
    const id = setInterval(loop, 1200);
    const t = setTimeout(loop, delay);
    return () => { clearInterval(id); clearTimeout(t); };
  }, [reduce]);
  const a = useAnimatedStyle(() => ({ opacity: o.value }));
  return <Animated.View style={[{ width: 6, height: 6, borderRadius: 999, backgroundColor: aA(INK, 0.4) }, a]} />;
}
function TypingDots() {
  return (
    <View style={{ flexDirection: "row", gap: 5 }}>
      {[0, 216, 432].map((d, i) => <Dot key={i} delay={d} />)}
    </View>
  );
}

export function ChatScreen({ mood, seed, opener = 0, onBack, insetTop }: any) {
  const { accent, accentDeep, glow } = mood;
  const floatA = useFloatY(6);
  const haloA = useHalo(5);
  const OPENERS = React.useMemo(() => openersFor(getFirstName()), []);
  const op = OPENERS[opener % OPENERS.length];
  const seedMsgs = seed ? [{ me: true, t: seed }, { me: false, t: "Good question to bring me. With the day this tender, I'd wait until late morning — the words will land softer then." }] : [];
  const [msgs, setMsgs] = useState<any[]>([{ me: false, t: op.lines[0], kind: op.kind }, ...seedMsgs]);
  const [chips, setChips] = useState<string[]>(seed ? [] : op.chips);
  const [draft, setDraft] = useState("");
  const [typing, setTyping] = useState(false);
  const [listening, setListening] = useState(false);
  const scrollRef = useRef<ScrollView>(null);
  const cnt = useRef(0);
  const userSpoke = msgs.some((m) => m.me);
  const sageState = typing ? "thinking" : userSpoke ? "delivered" : "idle";
  useEffect(() => { const id = setTimeout(() => scrollRef.current?.scrollToEnd({ animated: true }), 60); return () => clearTimeout(id); }, [msgs, typing]);

  const send = (raw: string) => {
    const text = raw.trim(); if (!text || typing) return;
    setChips([]); setDraft(""); setListening(false);
    setMsgs((m) => [...m, { me: true, t: text }]);
    setTyping(true);
    const r = pickReply(text, cnt.current++);
    setTimeout(() => { setTyping(false); setMsgs((m) => [...m, { me: false, t: r.t, safe: r.safe }]); }, 950 + Math.min(text.length * 12, 700));
  };

  return (
    <KeyboardAvoidingView style={{ flex: 1, backgroundColor: PAPER }} behavior={Platform.OS === "ios" ? "padding" : "height"}>
      {/* header */}
      <View style={{ paddingTop: insetTop + 8, paddingBottom: 11, alignItems: "center", borderBottomWidth: 1, borderBottomColor: HAIR, backgroundColor: aA(glow, 0.04) }}>
        <View style={{ position: "absolute", left: 18, top: insetTop + 4 }}>
          <Press scale={0.9} onPress={onBack}>
            <Pill radius={999} style={{ width: 42, height: 42, alignItems: "center", justifyContent: "center" }}><Icon n="arrowL" s={19} c={INK} /></Pill>
          </Press>
        </View>
        <View style={{ width: 92, height: 92, alignItems: "center", justifyContent: "center" }}>
          <Animated.View style={[{ position: "absolute", width: 76, height: 76, borderRadius: 999, backgroundColor: aA(glow, 0.28) }, haloA]} />
          <Animated.View style={[{ width: 86, height: 87 }, floatA]}>
            <SageImg src={sage1} active={sageState === "idle"} />
            <SageImg src={sage2} active={sageState === "thinking"} />
            <SageImg src={sage3} active={sageState === "delivered"} />
          </Animated.View>
        </View>
        <Text style={{ fontFamily: serif(500), fontSize: 18, color: INK, marginTop: 3 }}>Sage</Text>
        <Text style={{ fontFamily: sans(400), fontSize: 12, color: GRAY, marginTop: 1 }}>your guide · always private</Text>
      </View>

      {/* conversation */}
      <ScrollView ref={scrollRef} style={{ flex: 1 }} contentContainerStyle={{ padding: 18, gap: 11 }} showsVerticalScrollIndicator={false}>
        {msgs.map((m, i) => (
          <Animated.View key={i} entering={FadeIn.duration(450)} style={{ alignSelf: m.me ? "flex-end" : "flex-start", maxWidth: "83%" }}>
            {m.kind && (
              <View style={{ flexDirection: "row", alignItems: "center", gap: 5, marginBottom: 5, marginLeft: 4 }}>
                <View style={{ width: 4, height: 4, borderRadius: 999, backgroundColor: glow }} />
                <Text style={{ fontFamily: mono(500), fontSize: 9.5, letterSpacing: 1, textTransform: "uppercase", color: aA(accentDeep, 0.85) }}>{m.kind}</Text>
              </View>
            )}
            {m.me ? (
              <View style={{ backgroundColor: INK, borderRadius: 20, borderBottomRightRadius: 6, paddingVertical: 11, paddingHorizontal: 15 }}>
                <Text style={{ fontFamily: sans(500), fontSize: 14.5, lineHeight: 21, color: "#FFF" }}>{m.t}</Text>
              </View>
            ) : m.safe ? (
              <View style={{ backgroundColor: aA(accent, 0.08), borderWidth: 1, borderColor: aA(accent, 0.3), borderRadius: 20, borderBottomLeftRadius: 6, paddingVertical: 13, paddingHorizontal: 16 }}>
                <Text style={{ fontFamily: serif(400), fontSize: 15.5, lineHeight: 23, color: INK }}>{m.t}</Text>
              </View>
            ) : (
              <Pill radius={20} style={{ borderBottomLeftRadius: 6, paddingVertical: 12, paddingHorizontal: 16 }}>
                <Text style={{ fontFamily: serif(400), fontSize: 15.5, lineHeight: 22, color: INK }}>{m.t}</Text>
              </Pill>
            )}
          </Animated.View>
        ))}
        {typing && (
          <Animated.View entering={FadeIn.duration(300)} style={{ alignSelf: "flex-start" }}>
            <Pill radius={20} style={{ borderBottomLeftRadius: 6, paddingVertical: 13, paddingHorizontal: 17 }}><TypingDots /></Pill>
          </Animated.View>
        )}
        {chips.length > 0 && !typing && (
          <Animated.View entering={FadeIn.duration(500)} style={{ alignSelf: "flex-start", flexDirection: "row", gap: 8, flexWrap: "wrap", marginTop: 2 }}>
            {chips.map((c) => (
              <Press key={c} scale={0.95} onPress={() => send(c)}>
                <View style={{ paddingVertical: 8, paddingHorizontal: 14, borderRadius: 999, backgroundColor: "#FFF", borderWidth: 1, borderColor: aA(accentDeep, 0.3) }}>
                  <Text style={{ fontFamily: sans(700), fontSize: 13, color: accentDeep }}>{c}</Text>
                </View>
              </Press>
            ))}
          </Animated.View>
        )}
      </ScrollView>

      {/* input */}
      <View style={{ paddingHorizontal: 16, paddingTop: 6, paddingBottom: 26 }}>
        {listening && (
          <View style={{ flexDirection: "row", alignItems: "center", justifyContent: "center", gap: 6, marginBottom: 9 }}>
            {[0, 1, 2, 3, 4].map((b) => <View key={b} style={{ width: 3, borderRadius: 999, backgroundColor: accentDeep, height: 8 + (b % 3) * 7 }} />)}
            <Text style={{ fontFamily: sans(400), fontSize: 12, color: accentDeep, fontStyle: "italic", marginLeft: 4 }}>listening…</Text>
          </View>
        )}
        <Pill radius={999} style={{ flexDirection: "row", alignItems: "center", gap: 8, paddingLeft: 16, paddingRight: 6, paddingVertical: 5 }}>
          <TextInput value={draft} onChangeText={setDraft} onSubmitEditing={() => send(draft)} placeholder="Tell Sage…" placeholderTextColor={GRAY} underlineColorAndroid="transparent" style={{ flex: 1, fontFamily: sans(400), fontSize: 14.5, color: INK, paddingVertical: 9, outlineWidth: 0 } as any} />
          <Press scale={0.9} onPress={() => setListening((v) => !v)}>
            <View style={{ width: 38, height: 38, borderRadius: 999, alignItems: "center", justifyContent: "center", backgroundColor: listening ? accentDeep : aA(accent, 0.12) }}><Icon n="mic" s={18} c={listening ? "#FFF" : accentDeep} sw={1.8} /></View>
          </Press>
          <Press scale={0.9} onPress={() => send(draft)}>
            <View style={{ width: 38, height: 38, borderRadius: 999, alignItems: "center", justifyContent: "center", backgroundColor: draft.trim() ? INK : aA(INK, 0.35) }}><Icon n="send" s={17} c="#FFF" sw={1.8} /></View>
          </Press>
        </Pill>
      </View>
    </KeyboardAvoidingView>
  );
}
