// SkyScene.tsx — THE signature feature (astro-plan.tsx SkyScene): a framed window into the
// sky you drag horizontally to scrub the whole day. Sky gradient + sun/moon arc update live;
// release eases back to "now" (560ms). react-native-svg scene + gesture-handler Pan.
import React, { useEffect, useRef } from "react";
import { View, Text } from "react-native";
import { Gesture, GestureDetector } from "react-native-gesture-handler";
import { runOnJS } from "react-native-reanimated";
import Svg, { Defs, LinearGradient as SvgLinear, RadialGradient, Stop, Rect, Ellipse, G, Circle, Line, Path } from "react-native-svg";
import { Mood } from "../theme";
import { INK, GRAY, aA, sans, mono, shadow } from "../ui/palette";

const clamp = (v: number, a: number, b: number) => Math.max(a, Math.min(b, v));
function fmtH(h: number) { const x = ((h % 24) + 24) % 24; let hr = Math.floor(x); const m = Math.round((x - hr) * 60); const ap = hr < 12 ? "am" : "pm"; let h12 = hr % 12; if (h12 === 0) h12 = 12; return `${h12}:${String(m).padStart(2, "0")}${ap}`; }
function lerpHex(a: string, b: string, t: number) {
  const pa = [1, 3, 5].map((i) => parseInt(a.slice(i, i + 2), 16));
  const pb = [1, 3, 5].map((i) => parseInt(b.slice(i, i + 2), 16));
  const c = pa.map((v, i) => Math.round(v + (pb[i] - v) * t));
  return `rgb(${c[0]},${c[1]},${c[2]})`;
}
const SKY = [
  { f: 0, top: "#F7B98A", bot: "#FCE4C8" }, { f: 0.12, top: "#AED7F0", bot: "#E9F6FB" },
  { f: 0.32, top: "#7FBFEC", bot: "#DCEFFB" }, { f: 0.52, top: "#EBD299", bot: "#FBEFCF" },
  { f: 0.64, top: "#E89A62", bot: "#F6CB9C" }, { f: 0.74, top: "#7A5E92", bot: "#C98B94" },
  { f: 0.86, top: "#2E3157", bot: "#4B4270" }, { f: 1, top: "#2A2B50", bot: "#4A4472" },
];
const STARS: number[][] = [[24, 20, .9], [52, 13, .7], [80, 26, 1], [112, 16, .8], [140, 30, .7], [172, 13, .95], [200, 24, .75], [228, 12, .9], [256, 27, .8], [276, 18, .7], [38, 42, .6], [128, 46, .55], [210, 44, .6], [164, 38, .5], [92, 48, .5]];
const LIGHTS: number[][] = [[44, 103], [96, 105], [150, 102], [206, 105], [258, 103]];
const arcCol = (q: string) => q === "best" ? "#3E9C7A" : q === "good" ? "#6FB894" : q === "neutral" ? "#E0A23C" : "#8E93B0";

export function SkyScene({ mood, W, SR, span, now, previewT, setPreviewT, tasks }: any) {
  const { accent, accentDeep } = mood;
  const frameW = useRef(1);
  const stripW = useRef(1);
  const rafRef = useRef<number>(0);
  const viewT = previewT != null ? previewT : now;
  const f = clamp((viewT - SR) / span, 0, 1);
  const fNow = clamp((now - SR) / span, 0, 1);
  const dragging = previewT != null;

  let si = 0; while (si < SKY.length - 1 && f > SKY[si + 1].f) si++;
  const sa = SKY[si], sb = SKY[Math.min(si + 1, SKY.length - 1)];
  const stt = sb.f === sa.f ? 0 : (f - sa.f) / (sb.f - sa.f);
  const topC = lerpHex(sa.top, sb.top, stt), botC = lerpHex(sa.bot, sb.bot, stt);
  const nightAmt = clamp((f - 0.66) / 0.16, 0, 1);
  const dayAmt = 1 - nightAmt;
  const moonAmt = clamp((f - 0.66) / 0.08, 0, 1);
  const sunAmt = 1 - moonAmt;
  const arc = Math.sin(clamp(f, 0, 1) * Math.PI);
  const bx = 20 + f * 260, by = 100 - arc * 66;
  const lowAmt = 1 - arc;
  const horizonWarm = lowAmt * dayAmt;
  const hillBack = lerpHex("#C4C7D4", "#20223E", nightAmt);
  const hillFront = lerpHex("#A7ACBF", "#141530", nightAmt);
  const totalDur = W.reduce((s: number, w: any) => s + (w.end - w.start), 0) || span;
  const previewWin = previewT != null ? (W.find((w: any) => previewT >= w.start && previewT < w.end) || W[W.length - 1]) : null;
  const shortH = (h: number) => { h = ((h % 24) + 24) % 24; const ap = h < 12 ? "am" : "pm"; let hr = Math.round(h) % 12; if (hr === 0) hr = 12; return hr + ap; };

  const cancelRaf = () => { if (rafRef.current) cancelAnimationFrame(rafRef.current); };
  const settle = (fromT: number) => {
    cancelRaf();
    const start = Date.now(), dur = 560, target = now;
    const tick = () => {
      const k = Math.min(1, (Date.now() - start) / dur);
      const e = 1 - Math.pow(1 - k, 3);
      if (k < 1) { setPreviewT(fromT + (target - fromT) * e); rafRef.current = requestAnimationFrame(tick); }
      else setPreviewT(null);
    };
    rafRef.current = requestAnimationFrame(tick);
  };
  useEffect(() => () => cancelRaf(), []);
  const dragSky = (x: number) => { const frac = clamp(x / frameW.current, 0, 1); setPreviewT(SR + frac * span); };
  const dragStrip = (x: number) => { const frac = clamp(x / stripW.current, 0, 1); setPreviewT(SR + frac * span); };
  const release = () => { settle(previewT != null ? previewT : now); };

  // drag the sky window itself… (horizontal only, so a vertical swipe scrolls the page)
  const skyPan = Gesture.Pan()
    .activeOffsetX([-8, 8])
    .failOffsetY([-14, 14])
    .onBegin(() => { runOnJS(cancelRaf)(); })
    .onStart((e) => { runOnJS(dragSky)(e.x); })
    .onUpdate((e) => { runOnJS(dragSky)(e.x); })
    .onEnd(() => { runOnJS(release)(); });
  // …or scrub along the timeline strip below it
  const stripPan = Gesture.Pan()
    .activeOffsetX([-8, 8])
    .failOffsetY([-14, 14])
    .onBegin(() => { runOnJS(cancelRaf)(); })
    .onStart((e) => { runOnJS(dragStrip)(e.x); })
    .onUpdate((e) => { runOnJS(dragStrip)(e.x); })
    .onEnd(() => { runOnJS(release)(); });

  return (
    <View>
      <GestureDetector gesture={skyPan}>
        {/* aspectRatio makes the frame scale to the full card width (no empty sides), and
            keeps the 300:116 viewBox filling it edge-to-edge with no distortion. The outer
            view holds the rounded shadow; the inner one clips the sky. */}
        <View style={{ width: "100%", aspectRatio: 300 / 116, borderRadius: 18, backgroundColor: botC, ...shadow({ y: 6, blur: 18, opacity: 0.3, elevation: 4 }) } as any}>
          <View
            onLayout={(ev) => { frameW.current = ev.nativeEvent.layout.width; }}
            style={{ flex: 1, borderRadius: 18, overflow: "hidden", borderWidth: 1, borderColor: "rgba(12,11,10,0.07)" }}
          >
          <Svg width="100%" height="100%" viewBox="0 0 300 116" preserveAspectRatio="xMidYMid slice">
            <Defs>
              <SvgLinear id="skg" x1="0" y1="0" x2="0" y2="1"><Stop offset="0" stopColor={topC} /><Stop offset="1" stopColor={botC} /></SvgLinear>
              <RadialGradient id="milky" cx="50%" cy="50%" r="50%"><Stop offset="0" stopColor="rgba(224,228,255,0.5)" /><Stop offset="1" stopColor="rgba(224,228,255,0)" /></RadialGradient>
              <RadialGradient id="sunG" cx="50%" cy="50%" r="50%"><Stop offset="0" stopColor="rgb(255,206,110)" stopOpacity={0.92 * sunAmt} /><Stop offset="0.55" stopColor="rgb(255,180,90)" stopOpacity={0.35 * sunAmt} /><Stop offset="1" stopColor="rgb(255,255,255)" stopOpacity={0} /></RadialGradient>
              <RadialGradient id="moonG" cx="50%" cy="50%" r="50%"><Stop offset="0" stopColor="rgb(228,232,255)" stopOpacity={0.72 * moonAmt} /><Stop offset="1" stopColor="rgb(228,232,255)" stopOpacity={0} /></RadialGradient>
              <SvgLinear id="warmBand" x1="0" y1="0" x2="0" y2="1"><Stop offset="0" stopColor="rgb(255,150,70)" stopOpacity={0} /><Stop offset="1" stopColor="rgb(255,138,64)" stopOpacity={0.5 * horizonWarm} /></SvgLinear>
            </Defs>
            <Rect x="0" y="0" width="300" height="116" fill="url(#skg)" />
            <Ellipse cx="150" cy="40" rx="190" ry="17" fill="url(#milky)" transform="rotate(-11 150 40)" opacity={nightAmt * 0.5} />
            <G opacity={nightAmt}>{STARS.map((s, i) => <Circle key={i} cx={s[0]} cy={s[1]} r={(i % 3 === 0 ? 1.5 : 1) * s[2]} fill="#FFF" opacity={0.8} />)}</G>
            {/* sun rays */}
            <G opacity={sunAmt * 0.5 * arc}>
              {Array.from({ length: 12 }).map((_, i) => { const a = i * 30 * Math.PI / 180; return <Line key={i} x1={bx + Math.cos(a) * 13} y1={by + Math.sin(a) * 13} x2={bx + Math.cos(a) * 19} y2={by + Math.sin(a) * 19} stroke="rgba(255,206,120,0.85)" strokeWidth={1.4} strokeLinecap="round" />; })}
            </G>
            <Circle cx={bx} cy={by} r={30} fill="url(#sunG)" />
            <Circle cx={bx} cy={by} r={30} fill="url(#moonG)" />
            {sunAmt > 0.02 && <G opacity={sunAmt}><Circle cx={bx} cy={by} r={10.5} fill="#FFD152" /><Circle cx={bx - 2.6} cy={by - 3} r={4.6} fill="rgba(255,244,200,0.85)" /></G>}
            {moonAmt > 0.02 && <G opacity={moonAmt}><Circle cx={bx} cy={by} r={10} fill="#ECE7D6" /><Circle cx={bx + 3.4} cy={by - 2} r={9} fill={botC} opacity={0.92} /><Circle cx={bx - 3.2} cy={by + 2.4} r={1.5} fill="rgba(120,110,95,0.35)" /><Circle cx={bx - 1} cy={by - 3} r={1.1} fill="rgba(120,110,95,0.3)" /></G>}
            {/* clouds (day) */}
            <G opacity={dayAmt * 0.85}>
              <G><Ellipse cx="70" cy="34" rx="20" ry="7" fill="rgba(255,255,255,0.82)" /><Ellipse cx="86" cy="31" rx="14" ry="6" fill="rgba(255,255,255,0.82)" /></G>
              <G><Ellipse cx="212" cy="24" rx="17" ry="6" fill="rgba(255,255,255,0.7)" /><Ellipse cx="226" cy="27" rx="12" ry="5" fill="rgba(255,255,255,0.7)" /></G>
            </G>
            {/* warm horizon band */}
            <Rect x="0" y="78" width="300" height="38" fill="url(#warmBand)" />
            {/* hills */}
            <Path d="M0,92 C60,84 110,90 160,86 C210,82 260,90 300,86 L300,116 L0,116 Z" fill={hillBack} opacity={0.9} />
            <Path d="M0,101 C50,95 100,103 150,99 C200,95 252,104 300,100 L300,116 L0,116 Z" fill={hillFront} />
            {/* village lights (night) */}
            <G opacity={nightAmt}>{LIGHTS.map((p, i) => <Circle key={i} cx={p[0]} cy={p[1]} r={1.2} fill="#FFCF85" />)}</G>
          </Svg>
          </View>
        </View>
      </GestureDetector>

      {/* whole-day quality strip — also draggable to scrub the day. The wrapper's padding
          (cancelled by an equal negative margin) enlarges the touch target without moving it. */}
      <GestureDetector gesture={stripPan}>
        <View style={{ marginTop: 12, paddingTop: 14, paddingBottom: 14, marginBottom: -14 }}>
          <View onLayout={(ev) => { stripW.current = ev.nativeEvent.layout.width; }} style={{ position: "relative", height: 14, flexDirection: "row", gap: 2 }}>
            {W.map((w: any, i: number) => { const fw = (w.end - w.start) / totalDur * 100; const cur = now >= w.start && now < w.end; return (
              <View key={i} style={{ width: `${fw}%` as any, backgroundColor: arcCol(w.q), opacity: cur ? 1 : 0.6, borderRadius: 4 }} />
            ); })}
            {tasks.filter((t: any) => !t.done && !t.placing).map((t: any, i: number) => { const w = W[t.win] || W[0]; const mid = ((w.start + w.end) / 2 - SR) / span * 100; return (
              <View key={i} style={{ position: "absolute", top: -3, left: `${mid}%` as any, marginLeft: -3, width: 6, height: 6, borderRadius: 999, backgroundColor: INK, borderWidth: 1.5, borderColor: "#FFF" }} />
            ); })}
            {/* NOW label */}
            <View style={{ position: "absolute", top: -22, left: `${fNow * 100}%` as any, transform: [{ translateX: -20 }], opacity: dragging ? 0.35 : 1, alignItems: "center", width: 40 }}>
              <Text style={{ fontFamily: mono(600), fontSize: 8.5, letterSpacing: 0.6, textTransform: "uppercase", color: accentDeep }}>now · {shortH(now)}</Text>
            </View>
            {/* NOW dot + soft halo ring (a wrapper circle, not a square boxShadow) */}
            <View style={{ position: "absolute", top: -2, left: `${fNow * 100}%` as any, marginLeft: -9, width: 18, height: 18, borderRadius: 999, backgroundColor: aA(accent, 0.24), alignItems: "center", justifyContent: "center", opacity: dragging ? 0.35 : 1 }}>
              <View style={{ width: 12, height: 12, borderRadius: 999, backgroundColor: accent, borderWidth: 2, borderColor: "#FFF" }} />
            </View>
            {dragging && (
              <View style={{ position: "absolute", top: -6, left: `${f * 100}%` as any, marginLeft: -1, width: 2, height: 26, backgroundColor: INK, borderRadius: 2 }} />
            )}
          </View>
        </View>
      </GestureDetector>

      {/* hour axis */}
      <View style={{ position: "relative", height: 13, marginTop: 6 }}>
        {[0, 0.25, 0.5, 0.75, 1].map((fr, i, arr) => (
          <Text key={i} style={{ position: "absolute", left: `${fr * 100}%` as any, transform: [{ translateX: i === 0 ? 0 : i === arr.length - 1 ? -34 : -17 }], fontFamily: mono(500), fontSize: 9, letterSpacing: 0.4, color: aA(GRAY, 0.85), width: 34, textAlign: i === arr.length - 1 ? "right" : "left" }}>{shortH(SR + fr * span)}</Text>
        ))}
      </View>

      <View style={{ marginTop: 7, alignItems: "center", minHeight: 18 }}>
        {previewWin ? (
          <Text style={{ fontFamily: sans(400), fontSize: 12.5, color: INK }}><Text style={{ fontFamily: sans(700), color: accentDeep }}>{fmtH(previewT as number)}</Text> · {previewWin.name} — {previewWin.tip}</Text>
        ) : (
          <Text style={{ fontFamily: sans(400), fontSize: 12, color: GRAY, fontStyle: "italic" }}>drag across the sky to watch your day pass</Text>
        )}
      </View>
    </View>
  );
}

export { fmtH };
