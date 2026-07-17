// Reveal.tsx — Step 4, the free payoff + the app's first-impression showpiece.
// Ported from screens/onboarding/onboarding-reveal.tsx. Three acts, all frame-driven:
//   ACT 1-2 · form — a real natal wheel (react-native-svg) draws itself, then the three
//             luminaries (Sun gold, Moon violet, Rising plum) cast out to their seats;
//             the finished wheel shrinks + rises away.
//   ACT 3   · read — the wheel returns small + calm; a mood headline, then the triad as
//             glossy emblem tiles (each lights its wheel marker), then the violet proof line.
//
// WIRED to POST /chart/reveal: every placement, wheel angle and line is the user's REAL
//   sidereal chart. There is NO offline chart any more and there must never be one again;
//   see emptyChart() below for what was here and what it got wrong.
import React, { useEffect, useMemo, useRef, useState } from "react";
import { View, Text, Pressable } from "react-native";
import Animated, { useSharedValue, useAnimatedStyle, withTiming, Easing } from "react-native-reanimated";
import { LinearGradient } from "expo-linear-gradient";
import Svg, { G, Circle, Line, Path, Text as SvgText } from "react-native-svg";
import { serif, sans, mono, aA, shadow } from "../ui/palette";
import { RadialGlow } from "../ui/atoms";
import { useHalo } from "../ui/motion";
import { P, OScreen, StepChrome, PrimaryButton, useRaf, useTopPad } from "./kit";
import type { OnbData } from "./data";
import { buildProfileFromData } from "./data";
import { fetchReveal, RevealBundle } from "../api/reveal";

const clamp01 = (v: number) => Math.max(0, Math.min(1, v));
const easeOut = (t: number) => 1 - Math.pow(1 - t, 3);

// ---- tiny mock chart engine (deterministic from birth data) — WIRE to real ephemeris ----
/**
 * An EMPTY wheel: rings and zodiac, no placements. `ang: null` markers are skipped by
 * NatalWheel, so nothing is asserted until the real chart lands.
 *
 * ─────────────────────────────────────────────────────────────────────────────
 * WHAT USED TO BE HERE, AND WHY IT IS GONE.
 *
 * buildChart(data) invented an entire chart offline and the Reveal showed it silently
 * whenever /chart/reveal was unreachable — which was ALWAYS on a tester's phone, because
 * the app pointed at a private LAN IP (see api/config.ts). Measured against the real
 * engine over 8 birthdays, it got the Sun sign wrong 6/8, the Moon nakshatra 8/8, and the
 * rising sign 8/8:
 *   • the Sun came from the WESTERN tropical date ranges. This app is SIDEREAL. They sit
 *     ~24 degrees apart, so it usually named the next sign along.
 *   • the Moon's nakshatra and the rising sign were a hash of birth day + month + THE
 *     NUMBER OF LETTERS IN THE USER'S NAME, drawn from just 8 of the 27 birth-stars.
 *   • the wheel's marker angles came from that same hash.
 *   • the proof line was one sentence, identical for every human being alive.
 * That is what "not accurate, and too generic" was. It was not the astrology; it was a
 * placeholder wearing the astrology's clothes.
 *
 * The Reveal now waits for the real chart. The forming animation IS the loading state, and
 * it simply keeps forming until the sky arrives. Nothing here may ever guess again.
 * ─────────────────────────────────────────────────────────────────────────────
 */
export function emptyChart() {
  return {
    mood: "", first: "", hasRising: false, insights: [] as any[], proofLine: "",
    markers: [
      { kind: "sun", ang: null, color: P.gold, glow: P.goldGlow },
      { kind: "moon", ang: null, color: P.violet, glow: P.violetGlow },
      { kind: "rise", ang: null, color: P.plum, glow: P.violetGlow },
    ],
  };
}

// ---- luminary glyphs (centered at 0,0, drawn on the wheel + inside gloss tiles) ----
function MarkerGlyph({ kind, color }: { kind: string; color: string }) {
  if (kind === "sun") return (
    <G>
      <Circle r={3.1} fill="none" stroke={color} strokeWidth={1.5} />
      {Array.from({ length: 8 }).map((_, i) => { const ang = (i / 8) * Math.PI * 2; return <Line key={i} x1={Math.cos(ang) * 4.8} y1={Math.sin(ang) * 4.8} x2={Math.cos(ang) * 6.8} y2={Math.sin(ang) * 6.8} stroke={color} strokeWidth={1.3} strokeLinecap="round" />; })}
    </G>
  );
  if (kind === "moon") return <Path d="M3.4 -5.4 A6 6 0 1 0 3.4 5.4 A4.6 4.6 0 1 1 3.4 -5.4 Z" fill={color} />;
  return <Path d="M0 -6 L5.6 5 L-5.6 5 Z" fill={color} />; // rising
}

// ============================ THE NATAL WHEEL =======================================
function NatalWheel({ chart, prog, size, lit = 0 }: { chart: any; prog: number; size: number; lit?: number }) {
  const [, tick] = useState(0);
  const st = useRef({ t: Math.random() * 8 }).current;
  useRaf((dt: number) => { st.t += Math.min(dt, 32) / 1000; tick((n) => (n + 1) & 1023); });
  const settled = prog >= 1;
  const cx = size / 2, cy = size / 2;
  const R = size * 0.40, R2 = size * 0.285;
  const polar = (r: number, ang: number) => { const rad = (ang - 90) * Math.PI / 180; return [cx + r * Math.cos(rad), cy + r * Math.sin(rad)]; };
  const big = size > 180;

  const ringP = clamp01(prog / 0.26), ring2P = clamp01((prog - 0.08) / 0.24);
  const ringLen = 2 * Math.PI * R, ring2Len = 2 * Math.PI * R2;
  const ZG = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"];
  const drift = settled ? st.t * 2.4 : 0;
  const coreP = 0.5 + Math.sin(st.t * 2) * 0.5;

  const innerStars = useMemo(() => { let s = 41; const r = () => { s = (s * 9301 + 49297) % 233280; return s / 233280; };
    return Array.from({ length: 6 }, () => ({ ang: r() * 360, rad: 0.2 + r() * 0.6, ph: r() * 6, sp: 1.4 + r() * 1.4 })); }, []);

  const md = chart.markers.map((m: any, k: number) => {
    if (m.ang == null) return null;
    const start = 0.44 + k * 0.16, dur = 0.32;
    const t = settled ? 1 : clamp01((prog - start) / dur);
    const [mx, my] = polar(R * easeOut(t), m.ang);
    const isLit = k < lit;
    const present = settled ? (isLit ? 1 : 0) : clamp01((t - 0.9) / 0.1);
    return { m, k, t, mx, my, isLit, present };
  }).filter(Boolean) as any[];
  const pairs: any[] = [];
  for (let i = 0; i < md.length; i++) for (let j = i + 1; j < md.length; j++) pairs.push([md[i], md[j]]);

  return (
    <Svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
      {/* decorative rings + spokes + zodiac — drifts slowly once settled */}
      <G rotation={drift} originX={cx} originY={cy}>
        <Circle cx={cx} cy={cy} r={R} fill={aA(P.violet, 0.03)} opacity={ringP} />
        <Circle cx={cx} cy={cy} r={R} fill="none" stroke={aA(P.violet, 0.30)} strokeWidth={1.1}
          strokeDasharray={ringLen} strokeDashoffset={ringLen * (1 - ringP)} strokeLinecap="round" rotation={-90} originX={cx} originY={cy} />
        <Circle cx={cx} cy={cy} r={R2} fill="none" stroke={aA(P.violet, 0.16)} strokeWidth={1}
          strokeDasharray={ring2Len} strokeDashoffset={ring2Len * (1 - ring2P)} rotation={-90} originX={cx} originY={cy} />
        {Array.from({ length: 12 }).map((_, i) => {
          const p = settled ? 1 : clamp01((prog - 0.14 - i * 0.02) / 0.2);
          const [ax, ay] = polar(R2, i * 30), [bx, by] = polar(R, i * 30);
          return <Line key={i} x1={ax} y1={ay} x2={ax + (bx - ax) * p} y2={ay + (by - ay) * p} stroke={aA(P.violet, 0.13)} strokeWidth={0.8} />;
        })}
        {big && Array.from({ length: 36 }).map((_, i) => {
          const major = i % 3 === 0;
          const [ax, ay] = polar(R, i * 10), [bx, by] = polar(R - (major ? 7 : 4), i * 10);
          const p = settled ? 1 : clamp01((prog - 0.12 - i * 0.004) / 0.3);
          return <Line key={"t" + i} x1={ax} y1={ay} x2={bx} y2={by} stroke={aA(P.violet, major ? 0.34 : 0.16)} strokeWidth={major ? 1 : 0.6} opacity={p} strokeLinecap="round" />;
        })}
        {big && ZG.map((g, i) => { const [gx, gy] = polar(R + size * 0.058, i * 30); const p = clamp01((prog - 0.3 - i * 0.015) / 0.3);
          return <SvgText key={i} x={gx} y={gy} fill={aA(P.violetDeep, 0.5)} opacity={p} fontSize={size * 0.05} textAnchor="middle" alignmentBaseline="central">{g}</SvgText>; })}
        {innerStars.map((s2, i) => { const [sx, sy] = polar(R2 * s2.rad, s2.ang); const tw = 0.15 + (0.5 + 0.5 * Math.sin(st.t * s2.sp + s2.ph)) * 0.45;
          return <Circle key={i} cx={sx} cy={sy} r={1} fill={i % 2 ? P.gold : P.violet} opacity={settled ? tw : tw * ringP} />; })}
      </G>

      {/* aspect threads between luminaries */}
      {pairs.map(([A, B]: any) => {
        const op = A.present * B.present;
        if (op <= 0.02) return null;
        const shim = 0.55 + 0.45 * Math.sin(st.t * 1.5 + A.k * 2);
        return <Line key={A.k + "x" + B.k} x1={A.mx} y1={A.my} x2={B.mx} y2={B.my} stroke={aA(P.violet, (0.10 + 0.12 * shim) * op)} strokeWidth={settled ? 0.8 : 1} />;
      })}
      {/* the three luminaries — cast out from the core to their seats */}
      {md.map(({ m, k, t, mx, my, isLit }: any) => {
        if (t <= 0) return null;
        const land = clamp01((t - 0.68) / 0.32);
        const scale = 1 + Math.sin(land * Math.PI) * 0.32;
        const pingOn = !settled && t > 0.55 && t < 1;
        const pingP = clamp01((t - 0.55) / 0.45);
        const haloA = isLit ? 0.26 : (settled ? 0.14 : 0.2 * t);
        return (
          <G key={k} opacity={clamp01(t * 1.6)}>
            {pingOn ? <Circle cx={mx} cy={my} r={5 + pingP * 15} fill="none" stroke={aA(m.glow, 0.55 * (1 - pingP))} strokeWidth={1.3} /> : null}
            <Circle cx={mx} cy={my} r={isLit ? 13 : 10} fill={aA(m.glow, haloA)} />
            <G x={mx} y={my} scale={scale}><MarkerGlyph kind={m.kind} color={m.color} /></G>
          </G>
        );
      })}

      {/* breathing core */}
      <Circle cx={cx} cy={cy} r={size * 0.052 + coreP * 2} fill={aA(P.violetGlow, 0.3 * (settled ? 1 : ringP))} />
      <Circle cx={cx} cy={cy} r={size * 0.026} fill={P.violet} opacity={settled ? 1 : ringP} />
    </Svg>
  );
}

// pulsing halo behind the wheel/emblem
function Halo({ size, opacity = 0.4 }: { size: number; opacity?: number }) {
  const halo = useHalo(6);
  return (
    <Animated.View pointerEvents="none" style={[{ position: "absolute", width: size, height: size, alignItems: "center", justifyContent: "center" }, halo]}>
      <RadialGlow color={P.violetGlow} size={size} opacity={opacity} />
    </Animated.View>
  );
}

// glossy colorful emblem tile — the app's signature icon language
function GlossTile({ kind, on }: { kind: string; on: boolean }) {
  const G_: any = { sun: ["#FFD684", "#E5852B"], moon: ["#CBB6F2", "#7B57D4"], rise: ["#ECB7D3", "#9A57A6"] };
  const [c1, c2] = G_[kind] || G_.moon;
  const v = useSharedValue(on ? 1 : 0);
  useEffect(() => { v.value = withTiming(on ? 1 : 0, { duration: 500, easing: Easing.out(Easing.cubic) }); }, [on]);
  const a = useAnimatedStyle(() => ({ opacity: 0.35 + 0.65 * v.value, transform: [{ scale: 0.9 + 0.1 * v.value }] }));
  return (
    <Animated.View style={[{ width: 46, height: 46, borderRadius: 14, overflow: "hidden" }, a]}>
      <LinearGradient colors={[c1, c2]} start={{ x: 0.1, y: 0 }} end={{ x: 0.9, y: 1 }} style={{ position: "absolute", top: 0, left: 0, right: 0, bottom: 0 }} />
      <View pointerEvents="none" style={{ position: "absolute", top: 0, left: 0, right: 0, height: "46%" }}>
        <LinearGradient colors={[aA("#FFFFFF", 0.42), aA("#FFFFFF", 0)]} start={{ x: 0, y: 0 }} end={{ x: 0, y: 1 }} style={{ flex: 1 }} />
      </View>
      <View style={{ position: "absolute", top: 0, left: 0, right: 0, bottom: 0, alignItems: "center", justifyContent: "center" }}>
        <Svg width={26} height={26} viewBox="-10 -10 20 20"><MarkerGlyph kind={kind} color="#FFFDF8" /></Svg>
      </View>
    </Animated.View>
  );
}

// one luminary as a card row: emblem + role label (+ degree) + serif sign + line
function LumCardRow({ ins, marker, on, divider }: any) {
  const deg = marker && marker.ang != null ? Math.round(marker.ang % 30) : null;
  const role = ins.icon === "sun" ? "The core" : ins.icon === "moon" ? "Inner tide" : (/rising/i.test(ins.title) ? "The rising" : "Your time");
  const v = useSharedValue(on ? 1 : 0);
  useEffect(() => { v.value = withTiming(on ? 1 : 0, { duration: 550, easing: Easing.out(Easing.cubic) }); }, [on]);
  const a = useAnimatedStyle(() => ({ opacity: v.value, transform: [{ translateY: (1 - v.value) * 10 }] }));
  return (
    <View>
      <Animated.View style={[{ flexDirection: "row", alignItems: "flex-start", gap: 14, paddingVertical: 18 }, a]}>
        <GlossTile kind={ins.icon} on={on} />
        <View style={{ flex: 1, minWidth: 0, paddingTop: 1 }}>
          <Text style={{ fontFamily: mono(600), fontSize: 9.5, letterSpacing: 1.8, textTransform: "uppercase", color: P.inkFaint }}>{role}{deg != null ? `  ·  ${deg}°` : ""}</Text>
          <Text style={{ fontFamily: serif(500), fontSize: 18, color: P.ink, letterSpacing: -0.2, lineHeight: 22, marginTop: 3 }}>{ins.title}</Text>
          <Text style={{ fontFamily: sans(400), fontSize: 13, lineHeight: 20, color: P.inkMid, marginTop: 5 }}>{ins.line}</Text>
        </View>
      </Animated.View>
      {divider ? <View style={{ height: 1, backgroundColor: P.line, marginLeft: 60 }} /> : null}
    </View>
  );
}

// ProofPanel — the "it knows me" line. This is the emotional peak of the whole onboarding, so
// it gets to be a place rather than a stray centred paragraph: a soft violet wash, a little
// constellation drawn above it, and the line set left-aligned in big serif italic so it reads
// like something written to you. Left-aligned on purpose — the hero above is centred, and the
// switch is what stops the screen feeling like one long tube of middle-aligned text.
function ProofPanel({ text, up }: { text: string; up: boolean }) {
  const v = useSharedValue(0);
  useEffect(() => { if (up) v.value = withTiming(1, { duration: 700, easing: Easing.out(Easing.cubic) }); }, [up]);
  const a = useAnimatedStyle(() => ({ opacity: v.value, transform: [{ translateY: (1 - v.value) * 16 }] }));
  return (
    <Animated.View style={[{ marginTop: 30, borderRadius: 24, overflow: "hidden", borderWidth: 1, borderColor: aA(P.violet, 0.15) }, a]}>
      <LinearGradient colors={["#F8F5FC", "#EEE8F8"]} start={{ x: 0, y: 0 }} end={{ x: 1, y: 1 }}
        style={{ position: "absolute", top: 0, left: 0, right: 0, bottom: 0 }} />
      <View style={{ paddingVertical: 26, paddingHorizontal: 24 }}>
        <Svg width={44} height={13} viewBox="0 0 44 13" style={{ marginBottom: 15 }}>
          <Line x1={2} y1={9} x2={15} y2={3} stroke={aA(P.violet, 0.38)} strokeWidth={0.9} />
          <Line x1={15} y1={3} x2={29} y2={10} stroke={aA(P.violet, 0.38)} strokeWidth={0.9} />
          <Line x1={29} y1={10} x2={42} y2={4} stroke={aA(P.violet, 0.38)} strokeWidth={0.9} />
          <Circle cx={2} cy={9} r={1.5} fill={aA(P.violet, 0.75)} />
          <Circle cx={15} cy={3} r={2.3} fill={P.gold} />
          <Circle cx={29} cy={10} r={1.5} fill={aA(P.violet, 0.75)} />
          <Circle cx={42} cy={4} r={1.9} fill={aA(P.violet, 0.75)} />
        </Svg>
        <Text style={{ fontFamily: serif(500, true), fontSize: 21, lineHeight: 32, color: P.violetDeep, letterSpacing: -0.2 }}>{text}</Text>
      </View>
    </Animated.View>
  );
}

// map the backend /chart/reveal bundle -> the shape the wheel + cards consume
export function adaptReveal(b: RevealBundle) {
  return {
    mood: b.mood,
    first: b.first,
    hasRising: b.has_rising,
    insights: b.insights.map((i) => ({ icon: i.icon, title: i.title, line: i.line })),
    proofLine: b.proof,
    markers: [
      { kind: "sun", ang: b.sun.lon, color: P.gold, glow: P.goldGlow },
      { kind: "moon", ang: b.moon.lon, color: P.violet, glow: P.violetGlow },
      { kind: "rise", ang: b.rising ? b.rising.lon : null, color: P.plum, glow: P.violetGlow },
    ],
  };
}

// ============================ STEP 4 — THE REVEAL ==================================
export function Reveal({ data, step, onBack, onNext }: any) {
  const top = useTopPad(6);
  // NO placeholder chart. This screen makes its first, biggest promise about who someone is,
  // so it waits for the real sidereal chart (POST /chart/reveal) rather than guessing. The
  // ~3.4s forming animation is the loading state; if the sky is slow the wheel just keeps
  // forming, which is honest and reads as intent rather than as a spinner.
  const [chart, setChart] = useState<any>(null);
  const [err, setErr] = useState(false);
  const [tries, setTries] = useState(0);
  useEffect(() => {
    let alive = true;
    const profile = buildProfileFromData(data);
    if (!profile) { setErr(true); return; }
    setErr(false);
    fetchReveal(profile)
      .then((b) => { if (!alive) return; if (b) setChart(adaptReveal(b)); else setErr(true); })
      .catch(() => { if (alive) setErr(true); });
    return () => { alive = false; };
  }, [tries]);
  const [phase, setPhase] = useState("form");
  const [prog, setProg] = useState(0);
  const [closing, setClosing] = useState(false);
  const closingRef = useRef(false);
  const [shown, setShown] = useState(0);

  // ACT 1: drive prog 0->1 over ~3.4s, but STALL just short of full until the real chart is
  // in hand. The bar completing is a promise that there is something to show.
  useRaf((dt: number) => {
    setProg((p) => Math.min(chart ? 1 : 0.92, p + (Math.min(dt, 32) / 1000) / 3.4));
  }, phase === "form" && !closing && !err);

  // ACT 2: at prog=1, shrink away, then switch to read. The phase-advance timeout must NOT be
  // torn down by the `closing` re-render — keep the ref guard (a fixed bug in the prototype).
  useEffect(() => {
    if (prog >= 1 && chart && !closingRef.current && phase === "form") {
      closingRef.current = true; setClosing(true);
      const t = setTimeout(() => setPhase("read"), 560);
      return () => clearTimeout(t);
    }
  }, [prog, phase, chart]);

  // ACT 3: stagger the reading in (insights + proof + cta)
  useEffect(() => {
    if (phase !== "read" || !chart) return;
    let i = 0; const total = chart.insights.length + 2;
    const iv = setInterval(() => { i += 1; setShown(i); if (i >= total) clearInterval(iv); }, 560);
    return () => clearInterval(iv);
  }, [phase, chart]);

  // shrink/fade the forming group as it closes
  const closeV = useSharedValue(0);
  useEffect(() => { if (closing) closeV.value = withTiming(1, { duration: 550, easing: Easing.bezier(0.5, 0, 0.2, 1) }); }, [closing]);
  const closeStyle = useAnimatedStyle(() => ({ opacity: 1 - closeV.value, transform: [{ translateY: -150 * closeV.value }, { scale: 1 - 0.5 * closeV.value }] }));

  const LOADING_LINES = ["Reading the sky at your first breath…", "Placing your Sun, Moon and rising…", "Finding the shape of you…"];
  const li = Math.min(LOADING_LINES.length - 1, Math.floor(prog * LOADING_LINES.length));

  // ---------- couldn't read the sky ----------
  // An error, not a guess. This screen tells someone who they are, so the one thing it must
  // never do is make something up to fill the silence.
  if (err && !chart) {
    return (
      <OScreen crown={0.3} stars>
        <View style={{ flex: 1, alignItems: "center", justifyContent: "center", paddingHorizontal: 40 }}>
          <Halo size={200} opacity={0.3} />
          <Text style={{ fontFamily: serif(500), fontSize: 26, lineHeight: 34, color: P.ink, textAlign: "center", letterSpacing: -0.4 }}>
            We couldn't read your sky just yet.
          </Text>
          <Text style={{ fontFamily: sans(400), fontSize: 14.5, lineHeight: 22, color: P.inkSoft, textAlign: "center", marginTop: 12 }}>
            Your chart needs a connection to work out. Nothing is lost, your details are still here.
          </Text>
          <Pressable onPress={() => { setErr(false); setProg(0); setTries((n) => n + 1); }} style={{ marginTop: 26 }}>
            <View style={{ paddingVertical: 14, paddingHorizontal: 34, borderRadius: 999, backgroundColor: P.violetDeep }}>
              <Text style={{ fontFamily: sans(800), fontSize: 15, color: "#FFF" }}>Try again</Text>
            </View>
          </Pressable>
        </View>
      </OScreen>
    );
  }

  // ---------- ACT 1 + 2 : forming ----------
  if (phase === "form" || !chart) {
    return (
      <OScreen crown={0.3} stars>
        <Animated.View style={[{ flex: 1, alignItems: "center", justifyContent: "center", paddingHorizontal: 34 }, closeStyle]}>
          <View style={{ alignItems: "center", justifyContent: "center" }}>
            <Halo size={348} opacity={0.42} />
            {/* no chart yet = rings only. The placements appear when they are REAL. */}
            <NatalWheel chart={chart ?? emptyChart()} prog={prog} size={316} />
          </View>
          <View style={{ height: 30, marginTop: 30, width: "100%", alignItems: "center" }}>
            <Text style={{ fontFamily: serif(500, true), fontSize: 20, color: P.ink, textAlign: "center" }}>{LOADING_LINES[li]}</Text>
          </View>
          <View style={{ width: 132, height: 3, borderRadius: 2, backgroundColor: P.line, marginTop: 22, overflow: "hidden" }}>
            <LinearGradient colors={[P.violet, P.plum]} start={{ x: 0, y: 0 }} end={{ x: 1, y: 0 }} style={{ height: "100%", width: `${prog * 100}%`, borderRadius: 2 }} />
          </View>
        </Animated.View>
      </OScreen>
    );
  }

  // ---------- ACT 3 : the reading ----------
  const litCount = Math.min(shown, chart.markers.length);
  const proofUp = shown >= chart.insights.length + 1;
  const ctaUp = shown >= chart.insights.length + 2;

  return (
    <OScreen crown={0.14} scroll stars>
      <View style={{ flexGrow: 1, paddingTop: top, paddingBottom: 30, paddingHorizontal: 24 }}>
        <StepChrome step={step} onBack={onBack} />

        {/* HERO — the wheel you just watched form, now calm, given room to actually be looked at */}
        <View style={{ alignItems: "center", marginTop: 18 }}>
          <View style={{ width: 172, height: 172, alignItems: "center", justifyContent: "center" }}>
            <Halo size={216} opacity={0.36} />
            <NatalWheel chart={chart} prog={1} size={162} lit={litCount} />
          </View>
          <View style={{ flexDirection: "row", alignItems: "center", gap: 8, marginTop: 22 }}>
            <View style={{ width: 5, height: 5, borderRadius: 999, backgroundColor: aA(P.violet, 0.75) }} />
            <Text style={{ fontFamily: mono(500), fontSize: 10.5, letterSpacing: 2.6, textTransform: "uppercase", color: P.inkFaint }}>Here you are</Text>
            <View style={{ width: 5, height: 5, borderRadius: 999, backgroundColor: aA(P.violet, 0.75) }} />
          </View>
          <Text style={{ fontFamily: serif(500), fontSize: 33, color: P.ink, marginTop: 14, letterSpacing: -0.5, textAlign: "center", lineHeight: 39 }}>
            A <Text style={{ fontFamily: serif(500, true) }}>{chart.mood.toLowerCase()}</Text> soul, {chart.first}.
          </Text>
        </View>

        {/* THE TRIAD — one soft white card, glossy emblems, rows with room to breathe */}
        <View style={{ marginTop: 38, paddingHorizontal: 18, paddingVertical: 4, backgroundColor: P.paper, borderRadius: 22, borderWidth: 1, borderColor: P.line, ...shadow({ y: 16, blur: 40, opacity: 0.16, elevation: 3 }) } as any}>
          {chart.insights.map((ins: any, i: number) => (
            <LumCardRow key={i} ins={ins} marker={chart.markers[i]} on={shown > i} divider={i < chart.insights.length - 1} />
          ))}
        </View>

        {/* THE PROOF — the "it knows me" moment */}
        <ProofPanel text={chart.proofLine} up={proofUp} />

        <View style={{ flex: 1, minHeight: 30 }} />

        {/* CTA */}
        <View style={{ opacity: ctaUp ? 1 : 0, marginTop: 30 }}>
          <Text style={{ fontFamily: sans(400), fontSize: 13, lineHeight: 20, color: P.inkMid, textAlign: "center", marginBottom: 14 }}>This is just the first thread. Save your chart to keep pulling it.</Text>
          <PrimaryButton label="This is me →" onPress={onNext} />
        </View>
      </View>
    </OScreen>
  );
}

// re-export for Done (Auth.tsx echoes the wheel)
export { NatalWheel, Halo };
