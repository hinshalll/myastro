// astro-plan.tsx — the PLAN sub-tab of Today: My Day (inline schedule + add-a-task),
// My Panchang (today+2 → full-screen month), and the four tool entries that open
// bottom-sheets: Find a good day (Muhurat), Check my plans (Calendar Doctor), Ask the
// Moment, Time Capsule. Same ASTROLO-clean language; reads atoms from window.__astroUI.
;(function () {
const U = (window as any).__astroUI;
const T = (window as any).__astroToday;
const { useState, useRef, useEffect, useMemo, aA, PAPER, WASH, INK, INK2, GRAY, HAIR, ORANGE, SANS, SERIF, MONO,
  pill, card, Label, Icon, Flame, GlossIcon, Press, MoonGloss, MOOD, MONTH, dayDetail, PANCHANG_SOON,
  MUHURAT, CAL_DOCTOR, ASK_MOMENT, TIME_CAPSULE, CLOCK, rise } = U;
const { nowH, fmtH, qFill } = T;

const qColor = (q: string, mood: any) => q === "good" ? "#3E9C7A" : q === "mixed" ? "#E0A23C" : q === "low" ? "#8E93B0" : "#8E93B0";
const qWord = (q: string) => q === "good" ? "good day" : q === "mixed" ? "mixed day" : "low-key day";

// a shared "the sky is working" loader — used wherever the app has to compute/think
function Casting({ mood, size = 84, label }: any) {
  const { accent, accentDeep, glow } = mood;
  return (<div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 14, padding: "22px 0 10px", animation: "fadeIn .3s ease both" }}>
    <div style={{ width: size, height: size, position: "relative" }}>
      <div style={{ position: "absolute", inset: 0, borderRadius: 999, border: `2px solid ${aA(accent, 0.28)}`, borderTopColor: accentDeep, animation: "spinSlow 1s linear infinite" }} />
      <div style={{ position: "absolute", inset: 14, borderRadius: 999, border: `2px solid ${aA(accent, 0.2)}`, borderBottomColor: accent, animation: "spinSlow 1.4s linear infinite reverse" }} />
      <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center" }}><div style={{ width: 8, height: 8, borderRadius: 999, background: accentDeep, animation: "glowPulse 1.2s ease-in-out infinite", ["--gc" as any]: aA(glow, 0.6) } as any} /></div>
    </div>
    {label && <div style={{ fontFamily: MONO, fontSize: 10.5, letterSpacing: 1.1, textTransform: "uppercase", color: GRAY }}>{label}</div>}
  </div>);
}

// ============================ DAY VISUAL · A — LIVING SKY ============================
// A framed window into the sky. Drag and the whole atmosphere moves through the day —
// sunrise-peach → midday-blue → golden-dusk → starry-night — the sun/moon arcing across.
// A slim strip below paints the WHOLE day's quality at a glance; a marker shows the hour.
function SkyScene({ mood, W, SR, span, now, previewT, setPreviewT, tasks }: any) {
  const { accent, accentDeep, glow } = mood;
  const ref = useRef<any>(null);
  const rafRef = useRef<any>(0);
  const viewT = previewT != null ? previewT : now;
  const f = Math.max(0, Math.min(1, (viewT - SR) / span));
  const fNow = Math.max(0, Math.min(1, (now - SR) / span));
  const shortH = (h: number) => { h = ((h % 24) + 24) % 24; const ap = h < 12 ? "am" : "pm"; let hr = Math.round(h) % 12; if (hr === 0) hr = 12; return hr + ap; };
  const dragging = previewT != null;
  const lerpHex = (a: string, b: string, t: number) => { const pa = [1, 3, 5].map((i) => parseInt(a.slice(i, i + 2), 16)); const pb = [1, 3, 5].map((i) => parseInt(b.slice(i, i + 2), 16)); const c = pa.map((v, i) => Math.round(v + (pb[i] - v) * t)); return `rgb(${c[0]},${c[1]},${c[2]})`; };
  const SKY = [{ f: 0, top: "#F7B98A", bot: "#FCE4C8" }, { f: .12, top: "#AED7F0", bot: "#E9F6FB" }, { f: .32, top: "#7FBFEC", bot: "#DCEFFB" }, { f: .52, top: "#EBD299", bot: "#FBEFCF" }, { f: .64, top: "#E89A62", bot: "#F6CB9C" }, { f: .74, top: "#7A5E92", bot: "#C98B94" }, { f: .86, top: "#2E3157", bot: "#4B4270" }, { f: 1, top: "#2A2B50", bot: "#4A4472" }];
  let si = 0; while (si < SKY.length - 1 && f > SKY[si + 1].f) si++;
  const sa = SKY[si], sb = SKY[Math.min(si + 1, SKY.length - 1)]; const stt = sb.f === sa.f ? 0 : (f - sa.f) / (sb.f - sa.f);
  const topC = lerpHex(sa.top, sb.top, stt), botC = lerpHex(sa.bot, sb.bot, stt);
  const nightAmt = Math.max(0, Math.min(1, (f - 0.66) / 0.16));
  const dayAmt = 1 - nightAmt;
  const moonAmt = Math.max(0, Math.min(1, (f - 0.66) / 0.08));
  const sunAmt = 1 - moonAmt;
  const arc = Math.sin(Math.max(0, Math.min(1, f)) * Math.PI);   // 0 at horizon, 1 at zenith
  const bx = 20 + f * 260, by = 100 - arc * 66;
  const lowAmt = 1 - arc;                                        // how near the horizon (dawn/dusk)
  const horizonWarm = lowAmt * dayAmt;                           // warm band strength
  const hillBack = lerpHex("#C4C7D4", "#20223E", nightAmt);
  const hillFront = lerpHex("#A7ACBF", "#141530", nightAmt);
  const arcCol = (q: string) => q === "best" ? "#3E9C7A" : q === "good" ? "#6FB894" : q === "neutral" ? "#E0A23C" : "#8E93B0";
  const totalDur = W.reduce((s: number, w: any) => s + (w.end - w.start), 0) || span;
  const previewWin = previewT != null ? (W.find((w: any) => previewT >= w.start && previewT < w.end) || W[W.length - 1]) : null;
  const stars = [[24, 20, .9], [52, 13, .7], [80, 26, 1], [112, 16, .8], [140, 30, .7], [172, 13, .95], [200, 24, .75], [228, 12, .9], [256, 27, .8], [276, 18, .7], [38, 42, .6], [128, 46, .55], [210, 44, .6], [164, 38, .5], [92, 48, .5]];
  const lights = [[44, 103], [96, 105], [150, 102], [206, 105], [258, 103]];

  const settle = (fromT: number) => {
    cancelAnimationFrame(rafRef.current);
    const start = performance.now(), dur = 560, target = now;
    const tick = (t: number) => { const k = Math.min(1, (t - start) / dur); const e = 1 - Math.pow(1 - k, 3);
      if (k < 1) { setPreviewT(fromT + (target - fromT) * e); rafRef.current = requestAnimationFrame(tick); } else setPreviewT(null); };
    rafRef.current = requestAnimationFrame(tick);
  };
  useEffect(() => () => cancelAnimationFrame(rafRef.current), []);
  const dragTo = (clientX: number) => { const el = ref.current; if (!el) return; const r = el.getBoundingClientRect(); const frac = Math.max(0, Math.min(1, (clientX - r.left) / r.width)); setPreviewT(SR + frac * span); };
  const release = () => { const from = previewT != null ? previewT : now; settle(from); };

  return (
    <div ref={ref} style={{ position: "relative", touchAction: "none", cursor: dragging ? "grabbing" : "grab", userSelect: "none" }}
      onPointerDown={(e: any) => { cancelAnimationFrame(rafRef.current); e.currentTarget.setPointerCapture?.(e.pointerId); dragTo(e.clientX); }}
      onPointerMove={(e: any) => { if (e.buttons) dragTo(e.clientX); }}
      onPointerUp={release} onPointerCancel={release}>
      <div style={{ borderRadius: 18, overflow: "hidden", border: `1px solid ${HAIR}`, boxShadow: `inset 0 -18px 30px -20px rgba(0,0,0,0.3), 0 6px 16px -12px rgba(0,0,0,0.4)` }}>
        <svg width="100%" viewBox="0 0 300 116" style={{ display: "block" }}>
          <defs>
            <linearGradient id="skg" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor={topC} /><stop offset="100%" stopColor={botC} /></linearGradient>
            <radialGradient id="milky" cx="50%" cy="50%" r="50%"><stop offset="0%" stopColor="rgba(224,228,255,0.5)" /><stop offset="100%" stopColor="rgba(224,228,255,0)" /></radialGradient>
            <radialGradient id="sunGlow" cx="50%" cy="50%" r="50%"><stop offset="0%" stopColor={`rgba(255,206,110,${0.92 * sunAmt})`} /><stop offset="55%" stopColor={`rgba(255,180,90,${0.35 * sunAmt})`} /><stop offset="100%" stopColor="rgba(255,255,255,0)" /></radialGradient>
            <radialGradient id="moonGlow" cx="50%" cy="50%" r="50%"><stop offset="0%" stopColor={`rgba(228,232,255,${0.72 * moonAmt})`} /><stop offset="100%" stopColor="rgba(228,232,255,0)" /></radialGradient>
            <linearGradient id="warmBand" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="rgba(255,150,70,0)" /><stop offset="100%" stopColor={`rgba(255,138,64,${0.5 * horizonWarm})`} /></linearGradient>
          </defs>
          <rect x="0" y="0" width="300" height="116" fill="url(#skg)" />
          {/* milky-way band + stars (night) */}
          <ellipse cx="150" cy="40" rx="190" ry="17" fill="url(#milky)" transform="rotate(-11 150 40)" opacity={nightAmt * 0.5} />
          <g opacity={nightAmt}>{stars.map((s, i) => (<circle key={i} cx={s[0]} cy={s[1]} r={(i % 3 === 0 ? 1.5 : 1) * (s[2] as number)} fill="#FFF" className="skyStar" style={{ ["--lo" as any]: 0.25, ["--hi" as any]: 0.95, animation: `twinkle ${2.4 + (i % 4) * 0.7}s ease-in-out ${i * 0.31}s infinite` }} />))}</g>
          {/* shooting star (deep night) */}
          {nightAmt > 0.45 && (<g style={{ animation: "skyShoot 7s ease-in 2s infinite" }}><line x1="250" y1="20" x2="262" y2="14" stroke="#FFF" strokeWidth="1.4" strokeLinecap="round" /><circle cx="262" cy="14" r="1.6" fill="#FFF" /></g>)}
          {/* sun rays (day, behind body) */}
          <g opacity={sunAmt * 0.5 * arc} style={{ transformOrigin: `${bx}px ${by}px`, animation: "spinSlow 40s linear infinite" }}>
            {Array.from({ length: 12 }).map((_, i) => { const a = i * 30 * Math.PI / 180; return (<line key={i} x1={bx + Math.cos(a) * 13} y1={by + Math.sin(a) * 13} x2={bx + Math.cos(a) * 19} y2={by + Math.sin(a) * 19} stroke="rgba(255,206,120,0.85)" strokeWidth="1.4" strokeLinecap="round" />); })}
          </g>
          {/* body glow + body (drawn before hills so it rises/sets behind them) */}
          <circle cx={bx} cy={by} r="30" fill="url(#sunGlow)" />
          <circle cx={bx} cy={by} r="30" fill="url(#moonGlow)" />
          {sunAmt > 0.02 && (<g opacity={sunAmt}><circle cx={bx} cy={by} r="10.5" fill="#FFD152" /><circle cx={bx - 2.6} cy={by - 3} r="4.6" fill="rgba(255,244,200,0.85)" /></g>)}
          {moonAmt > 0.02 && (<g opacity={moonAmt}><circle cx={bx} cy={by} r="10" fill="#ECE7D6" /><circle cx={bx + 3.4} cy={by - 2} r="9" fill={botC} opacity="0.92" /><circle cx={bx - 3.2} cy={by + 2.4} r="1.5" fill="rgba(120,110,95,0.35)" /><circle cx={bx - 1} cy={by - 3} r="1.1" fill="rgba(120,110,95,0.3)" /></g>)}
          {/* clouds (day) */}
          <g opacity={dayAmt * 0.85}>
            <g className="skyCloud" style={{ animation: "cloudDrift 26s ease-in-out infinite" }}><ellipse cx="70" cy="34" rx="20" ry="7" fill="rgba(255,255,255,0.82)" /><ellipse cx="86" cy="31" rx="14" ry="6" fill="rgba(255,255,255,0.82)" /></g>
            <g className="skyCloud" style={{ animation: "cloudDrift 34s ease-in-out 3s infinite" }}><ellipse cx="212" cy="24" rx="17" ry="6" fill="rgba(255,255,255,0.7)" /><ellipse cx="226" cy="27" rx="12" ry="5" fill="rgba(255,255,255,0.7)" /></g>
          </g>
          {/* bird (day) */}
          <g opacity={dayAmt * 0.5} style={{ animation: "skyBird 30s linear infinite" }}><path d="M-14,30 q4,-4 8,0 q4,-4 8,0" fill="none" stroke="rgba(60,60,70,0.75)" strokeWidth="1.3" strokeLinecap="round" /></g>
          {/* warm horizon band */}
          <rect x="0" y="78" width="300" height="38" fill="url(#warmBand)" />
          {/* hills */}
          <path d="M0,92 C60,84 110,90 160,86 C210,82 260,90 300,86 L300,116 L0,116 Z" fill={hillBack} opacity="0.9" />
          <path d="M0,101 C50,95 100,103 150,99 C200,95 252,104 300,100 L300,116 L0,116 Z" fill={hillFront} />
          {/* village lights (night) */}
          <g opacity={nightAmt}>{lights.map((p, i) => (<circle key={i} cx={p[0]} cy={p[1]} r="1.2" fill="#FFCF85" style={{ animation: `fireflyGlow ${3 + (i % 3)}s ease-in-out ${i * 0.5}s infinite` }} />))}</g>
        </svg>
      </div>
      {/* whole-day quality strip — with a clear NOW marker + an hour axis */}
      <div style={{ position: "relative", marginTop: 26, height: 12, display: "flex", gap: 2, borderRadius: 999 }}>
        {W.map((w: any, i: number) => { const fw = (w.end - w.start) / totalDur * 100; const cur = now >= w.start && now < w.end; return (
          <div key={i} title={w.name} style={{ width: `${fw}%`, background: arcCol(w.q), opacity: cur ? 1 : 0.68, borderRadius: 3, boxShadow: cur ? `0 0 6px ${aA(accent, 0.7)}` : "none" }} />
        ); })}
        {tasks.filter((t: any) => !t.done && !t.placing).map((t: any, i: number) => { const w = W[t.win] || W[0]; const mid = ((w.start + w.end) / 2 - SR) / span * 100; return (<div key={i} style={{ position: "absolute", top: -3, left: `calc(${mid}% - 3px)`, width: 6, height: 6, borderRadius: 999, background: INK, border: "1.5px solid #FFF" }} />); })}
        {/* fixed NOW marker — always visible, labelled, in the accent colour */}
        <div style={{ position: "absolute", top: -22, left: `${fNow * 100}%`, transform: "translateX(-50%)", display: "flex", flexDirection: "column", alignItems: "center", zIndex: 3, opacity: dragging ? 0.35 : 1, transition: "opacity .2s" }}>
          <span style={{ fontFamily: MONO, fontSize: 8.5, letterSpacing: 0.6, textTransform: "uppercase", color: accentDeep, fontWeight: 700, marginBottom: 2, whiteSpace: "nowrap" }}>now · {shortH(now)}</span>
        </div>
        <div style={{ position: "absolute", top: -5, left: `calc(${fNow * 100}% - 6px)`, width: 12, height: 12, borderRadius: 999, background: accent, border: "2px solid #FFF", boxShadow: `0 0 0 3px ${aA(accent, 0.28)}, 0 1px 3px ${aA("#1A1408", 0.3)}`, zIndex: 3, opacity: dragging ? 0.35 : 1, transition: "opacity .2s" }} />
        {/* the moving drag handle (only while dragging) */}
        {dragging && (<>
          <div style={{ position: "absolute", top: -8, left: `calc(${f * 100}% - 1px)`, width: 2, height: 22, background: INK, borderRadius: 2 }} />
          <div style={{ position: "absolute", top: -6, left: `calc(${f * 100}% - 6px)`, width: 0, height: 0, borderLeft: "6px solid transparent", borderRight: "6px solid transparent", borderTop: `7px solid ${INK}` }} />
        </>)}
      </div>
      {/* hour axis */}
      <div style={{ position: "relative", height: 13, marginTop: 6 }}>
        {[0, 0.25, 0.5, 0.75, 1].map((fr, i, arr) => (
          <span key={i} style={{ position: "absolute", left: `${fr * 100}%`, transform: i === 0 ? "translateX(0)" : i === arr.length - 1 ? "translateX(-100%)" : "translateX(-50%)", fontFamily: MONO, fontSize: 9, letterSpacing: 0.4, color: aA(GRAY, 0.85) }}>{shortH(SR + fr * span)}</span>
        ))}
      </div>
      <div style={{ marginTop: 7, textAlign: "center", minHeight: 18 }}>
        {previewWin
          ? (<span style={{ fontFamily: SANS, fontSize: 12.5, color: INK }}><b style={{ color: accentDeep }}>{fmtH(previewT as number)}</b> · {previewWin.name} — {previewWin.tip}</span>)
          : (<span style={{ fontFamily: SANS, fontSize: 12, color: GRAY, fontStyle: "italic" }}>drag across the sky to watch your day pass</span>)}
      </div>
    </div>
  );
}

// ============================ MY DAY — schedule ============================
function MyDay({ mood, delay }: any) {
  const { accent, accentDeep, glow } = mood;
  const W = CLOCK.windows || [];
  const SR = CLOCK.sunrise || 6, span = 24;
  const [now, setNow] = useState(() => { let h = nowH(); if (h < SR) h += 24; return h; });
  const [tasks, setTasks] = useState<any[]>([{ text: "Send the pitch", win: 3, done: false }]);
  const [draft, setDraft] = useState("");
  const [previewT, setPreviewT] = useState<number | null>(null);
  const arcRef = useRef<any>(null);
  useEffect(() => { const id = setInterval(() => { let h = nowH(); if (h < SR) h += 24; setNow(h); }, 20000); return () => clearInterval(id); }, []);
  const xOf = (t: number) => Math.max(0, Math.min(100, ((t - SR) / span) * 100));

  const bestWindowIdx = () => {
    // prefer an upcoming "best", then "good", never "hold"/"rest"
    const up = W.map((w: any, i: number) => ({ w, i })).filter(({ w }: any) => w.end > now && (w.q === "best" || w.q === "good"));
    if (up.length) { const b = up.find(({ w }: any) => w.q === "best") || up[0]; return b.i; }
    const any = W.map((w: any, i: number) => ({ w, i })).find(({ w }: any) => w.q === "best" || w.q === "good");
    return any ? any.i : 0;
  };
  const addTask = () => { const t = draft.trim(); if (!t) return; const born = Date.now(); setTasks((a) => [...a, { text: t, win: bestWindowIdx(), done: false, born, placing: true }]); setDraft(""); setTimeout(() => setTasks((a) => a.map((x) => x.born === born ? { ...x, placing: false } : x)), 1300); };
  const toggle = (i: number) => setTasks((a) => a.map((t, k) => k === i ? { ...t, done: !t.done } : t));

  const nowWin = W.find((w: any) => now >= w.start && now < w.end) || W[0] || {};
  const nextStrong = W.find((w: any) => w.start > now && (w.q === "best" || w.q === "good"));
  const goodNow = nowWin.q === "best" || nowWin.q === "good";
  const mins = nextStrong ? Math.round((nextStrong.start - now) * 60) : 0;
  const statusBig = goodNow ? "A good window, right now" : "Best to hold a little";
  const statusSub = goodNow
    ? `clear sailing till ${fmtH(nowWin.end)}`
    : nextStrong ? `a stronger window opens at ${fmtH(nextStrong.start)}${mins > 0 && mins < 180 ? ` · in ${mins} min` : ""}` : "a quiet stretch, nothing to push";

  return (
    <div style={{ ...card({ padding: 18, marginBottom: 14 }), ...rise(delay) }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div><Label c={aA(accentDeep, 0.9)}>My Day</Label><div style={{ fontFamily: SERIF, fontSize: 20, fontWeight: 500, color: INK, marginTop: 2 }}>Schedule today</div></div>
        <span style={{ fontFamily: SANS, fontSize: 12, fontWeight: 700, color: GRAY }}>{tasks.length ? `${tasks.filter((t) => !t.done).length} to do` : "open day"}</span>
      </div>

      {/* live status */}
      <div style={{ display: "flex", alignItems: "center", gap: 11, marginTop: 15, padding: "12px 14px", borderRadius: 16, background: goodNow ? "rgba(62,156,122,0.09)" : aA(accent, 0.07), border: `1px solid ${goodNow ? "rgba(62,156,122,0.26)" : aA(accent, 0.2)}` }}>
        <div style={{ position: "relative", width: 10, height: 10, flexShrink: 0 }}>
          <div style={{ position: "absolute", inset: 0, borderRadius: 999, background: goodNow ? "#3E9C7A" : accentDeep }} />
          <div style={{ position: "absolute", inset: -4, borderRadius: 999, border: `2px solid ${goodNow ? "#3E9C7A" : accentDeep}`, opacity: 0.4, animation: "glowPulse 2.4s ease-in-out infinite", ["--gc" as any]: aA(goodNow ? "#3E9C7A" : accentDeep, 0.4) } as any} />
        </div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ fontFamily: SANS, fontSize: 14, fontWeight: 800, color: INK }}>{statusBig}</div>
          <div style={{ fontFamily: SERIF, fontSize: 13, color: goodNow ? "#2E7D5B" : accentDeep, marginTop: 1 }}>{statusSub}</div>
        </div>
      </div>

      {/* the day as a living sky — drag to scrub through the hours */}
      <div style={{ marginTop: 18 }}>
        <SkyScene mood={mood} W={W} SR={SR} span={span} now={now} previewT={previewT} setPreviewT={setPreviewT} tasks={tasks} />
      </div>

      {/* add a task */}
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginTop: 16, padding: "4px 5px 4px 15px", borderRadius: 999, ...pill(999) }}>
        <input value={draft} onChange={(e: any) => setDraft(e.target.value)} onKeyDown={(e: any) => { if (e.key === "Enter") addTask(); }} placeholder="add a task, we'll place it well" style={{ flex: 1, border: "none", outline: "none", background: "transparent", fontFamily: SANS, fontSize: 14, color: INK, padding: "8px 0" }} />
        <Press scale={0.9} onClick={addTask}><div style={{ background: INK, borderRadius: 999, width: 36, height: 36, display: "flex", alignItems: "center", justifyContent: "center" }}><Icon n="plus" s={17} c="#FFF" sw={2.2} /></div></Press>
      </div>

      {/* placed tasks */}
      {tasks.length > 0 && (<div style={{ marginTop: 14, display: "flex", flexDirection: "column", gap: 9 }}>
        {tasks.map((t, i) => { const w = W[t.win] || W[0]; return (
          <div key={i} style={{ display: "flex", alignItems: "center", gap: 11, animation: t.placing ? "fadeIn .3s ease both" : "none" }}>
            {t.placing ? (
              <div style={{ width: 24, height: 24, flexShrink: 0, position: "relative" }}><div style={{ position: "absolute", inset: 0, borderRadius: 999, border: `2px solid ${aA(accent, 0.3)}`, borderTopColor: accentDeep, animation: "spinSlow .9s linear infinite" }} /></div>
            ) : (
              <Press scale={0.9} onClick={() => toggle(i)}><div style={{ width: 24, height: 24, borderRadius: 999, flexShrink: 0, display: "flex", alignItems: "center", justifyContent: "center", background: t.done ? aA(accent, 0.16) : WASH, border: `1px solid ${t.done ? aA(accentDeep, 0.35) : HAIR}` }}>{t.done && <Icon n="check" s={13} c={accentDeep} sw={2.6} />}</div></Press>
            )}
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ fontFamily: SANS, fontSize: 14, fontWeight: 700, color: t.done ? GRAY : INK, textDecoration: t.done ? "line-through" : "none" }}>{t.text}</div>
              <div style={{ fontFamily: SANS, fontSize: 11.5, color: t.placing ? accentDeep : GRAY, marginTop: 1, fontStyle: t.placing ? "italic" : "normal" }}>{t.placing ? "finding the best time…" : `${fmtH(w.start)} · ${w.name} · reminder 15 min before`}</div>
            </div>
            {!t.placing && <div style={{ width: 8, height: 8, borderRadius: 999, flexShrink: 0, background: qFill(w.q, mood) }} />}
          </div>
        ); })}
      </div>)}
    </div>
  );
}

// ============================ MY PANCHANG — today+2 + month link ============================
function MyPanchang({ mood, delay, onMonth }: any) {
  const { accent, accentDeep, glow } = mood;
  return (
    <div style={{ ...card({ padding: 18, marginBottom: 14 }), ...rise(delay) }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div><Label c={aA(accentDeep, 0.9)}>My Panchang</Label><div style={{ fontFamily: SERIF, fontSize: 20, fontWeight: 500, color: INK, marginTop: 2 }}>Your next few days</div></div>
        <GlossIcon c1={"#C9A6E8"} c2={"#7E54A0"}><Icon n="cal" s={19} c="#FFF" sw={1.8} /></GlossIcon>
      </div>
      <div style={{ marginTop: 14, display: "flex", flexDirection: "column", gap: 10 }}>
        {PANCHANG_SOON.map((d: any, i: number) => (
          <div key={i} style={{ display: "flex", alignItems: "center", gap: 12, padding: "11px 13px", borderRadius: 14, background: WASH, border: `1px solid ${HAIR}` }}>
            <div style={{ width: 78, flexShrink: 0, paddingRight: 8, whiteSpace: "nowrap" }}><div style={{ fontFamily: SANS, fontSize: 13, fontWeight: 800, color: INK }}>{d.day}</div><div style={{ fontFamily: MONO, fontSize: 9.5, color: GRAY }}>{d.date}</div></div>
            <div style={{ width: 9, height: 9, borderRadius: 999, flexShrink: 0, background: qColor(d.quality, mood), boxShadow: `0 0 0 3px ${aA(qColor(d.quality, mood), 0.16)}` }} />
            <div style={{ flex: 1, minWidth: 0 }}><div style={{ fontFamily: SERIF, fontSize: 15, color: INK }}>{qWord(d.quality)}</div><div style={{ fontFamily: SANS, fontSize: 11.5, color: GRAY, marginTop: 1 }}>{d.note}</div></div>
          </div>
        ))}
      </div>
      <Press scale={0.98} onClick={onMonth} style={{ display: "inline-block", marginTop: 13 }}><div style={{ display: "flex", alignItems: "center", gap: 6 }}><span style={{ fontFamily: SANS, fontSize: 12.5, fontWeight: 700, color: accentDeep }}>Open full Panchang</span><Icon n="arrowR" s={13} c={accentDeep} sw={2} /></div></Press>
    </div>
  );
}

// ============================ FULL-SCREEN MONTH ============================
const MARK_C: any = { moon: "#7C8AA0", festival: "#D98A2B", grahan: "#5B4FC4", dasha: "#2E9C7E", task: "#C2724E" };
function MonthScreen({ mood, onBack }: any) {
  const { accent, accentDeep, glow } = mood;
  const [sel, setSel] = useState<number | null>(null);
  const M = MONTH;
  const detail = sel != null ? dayDetail(sel) : null;
  const cells: any[] = [];
  for (let i = 0; i < M.startWeekday; i++) cells.push(null);
  M.days.forEach((d: any) => cells.push(d));
  return (
    <div style={{ position: "absolute", inset: 0, background: PAPER, overflowY: "auto" }}>
      <div style={{ position: "absolute", top: 52, left: 18, right: 18, zIndex: 10, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <Press scale={0.9} onClick={onBack}><div style={{ ...pill(999), width: 42, height: 42, display: "flex", alignItems: "center", justifyContent: "center" }}><Icon n="arrowL" s={19} c={INK} /></div></Press>
        <Press scale={0.95}><div style={{ ...pill(999), padding: "9px 14px", display: "flex", alignItems: "center", gap: 7 }}><Icon n="sync" s={15} c={accentDeep} sw={1.9} /><span style={{ fontFamily: SANS, fontSize: 12.5, fontWeight: 700, color: INK }}>Sync good days</span></div></Press>
      </div>
      <div style={{ padding: "108px 16px 40px" }}>
        <div style={rise(0)}><Label c={aA(accentDeep, 0.9)}>Your Panchang</Label><div style={{ fontFamily: SERIF, fontSize: 30, fontWeight: 500, color: INK, letterSpacing: -0.6, marginTop: 2 }}>{M.name}</div></div>
        {/* weekday header */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(7,1fr)", gap: 6, marginTop: 18 }}>
          {["S", "M", "T", "W", "T", "F", "S"].map((d, i) => <div key={i} style={{ textAlign: "center", fontFamily: MONO, fontSize: 10, fontWeight: 600, color: GRAY }}>{d}</div>)}
        </div>
        {/* grid */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(7,1fr)", gap: 6, marginTop: 8 }}>
          {cells.map((d, i) => d === null
            ? <div key={i} />
            : (<Press key={i} scale={0.92} onClick={() => setSel(d.n)}>
                <div style={{ aspectRatio: "1 / 1", borderRadius: 12, position: "relative", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", background: d.quality === "good" ? aA(accent, 0.12) : d.quality === "low" ? WASH : "#FFF", border: `1px solid ${sel === d.n ? accentDeep : d.quality === "good" ? aA(accent, 0.28) : HAIR}` }}>
                  <span style={{ fontFamily: SERIF, fontSize: 15, fontWeight: 500, color: d.quality === "low" ? GRAY : INK }}>{d.n}</span>
                  <div style={{ position: "absolute", bottom: 5, display: "flex", gap: 2 }}>
                    <div style={{ width: 4, height: 4, borderRadius: 999, background: qColor(d.quality, mood) }} />
                    {d.mark && <div style={{ width: 4, height: 4, borderRadius: 999, background: MARK_C[d.mark.kind] || GRAY }} />}
                  </div>
                </div>
              </Press>)
          )}
        </div>
        {/* legend */}
        <div style={{ display: "flex", flexWrap: "wrap", gap: 12, marginTop: 18, padding: "14px 16px", borderRadius: 16, background: WASH, border: `1px solid ${HAIR}` }}>
          {[["Festival", MARK_C.festival], ["Full / new moon", MARK_C.moon], ["Grahan", MARK_C.grahan], ["Dasha change", MARK_C.dasha], ["Your task", MARK_C.task]].map(([l, c]: any) => (
            <div key={l} style={{ display: "flex", alignItems: "center", gap: 6 }}><div style={{ width: 7, height: 7, borderRadius: 999, background: c }} /><span style={{ fontFamily: SANS, fontSize: 11.5, fontWeight: 600, color: INK2 }}>{l}</span></div>
          ))}
        </div>
      </div>
      {/* tapped-day sheet */}
      <U.Sheet open={sel != null} onClose={() => setSel(null)}>
        {detail && (<div>
          <Label c={aA(accentDeep, 0.9)}>{M.name.split(" ")[0]} {detail.n}</Label>
          <div style={{ display: "flex", alignItems: "center", gap: 9, marginTop: 6 }}>
            <div style={{ width: 10, height: 10, borderRadius: 999, background: qColor(detail.quality, mood) }} />
            <span style={{ fontFamily: SERIF, fontSize: 23, fontWeight: 500, color: INK }}>{qWord(detail.quality)}</span>
          </div>
          {detail.mark && <div style={{ display: "inline-flex", alignItems: "center", gap: 6, marginTop: 10, padding: "5px 11px", borderRadius: 999, background: WASH, border: `1px solid ${HAIR}` }}><div style={{ width: 6, height: 6, borderRadius: 999, background: MARK_C[detail.mark.kind] || GRAY }} /><span style={{ fontFamily: SANS, fontSize: 12.5, fontWeight: 700, color: INK }}>{detail.mark.label}</span></div>}
          <div style={{ fontFamily: SERIF, fontSize: 16, lineHeight: 1.5, color: INK2, marginTop: 14, textWrap: "pretty" } as any}>{detail.why}</div>
          <div style={{ display: "flex", gap: 10, marginTop: 16 }}>
            <div style={{ flex: 1, padding: "11px 13px", borderRadius: 13, background: aA(accent, 0.08), border: `1px solid ${aA(accent, 0.2)}` }}><Label c={accentDeep}>Good times</Label><div style={{ fontFamily: SERIF, fontSize: 15, color: INK, marginTop: 4 }}>{detail.good}</div></div>
            <div style={{ flex: 1, padding: "11px 13px", borderRadius: 13, background: WASH, border: `1px solid ${HAIR}` }}><Label>Hold off</Label><div style={{ fontFamily: SERIF, fontSize: 15, color: INK, marginTop: 4 }}>{detail.low}</div></div>
          </div>
        </div>)}
      </U.Sheet>
    </div>
  );
}

// ============================ ASK THE MOMENT — prominent card ============================
function AskMomentCard({ mood, delay, onAsk }: any) {
  const { accent, accentDeep, glow } = mood;
  const samples = (ASK_MOMENT.samples || []).slice(0, 3);
  return (
    <div style={{ ...card({ padding: 18, marginBottom: 14 }), background: `linear-gradient(158deg, ${aA(accent, 0.12)}, ${aA(glow, 0.05)})`, border: `1px solid ${aA(accent, 0.24)}`, ...rise(delay) }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div><Label c={aA(accentDeep, 0.9)}>Ask the Moment</Label><div style={{ fontFamily: SERIF, fontSize: 21, fontWeight: 500, color: INK, marginTop: 2, letterSpacing: -0.3 }}>Ask, and the sky answers — now</div></div>
        <GlossIcon c1={"#8E7BD6"} c2={"#5C4FB0"}><Icon n="wand" s={19} c="#FFF" sw={1.8} /></GlossIcon>
      </div>
      <div style={{ fontFamily: SANS, fontSize: 12.5, color: GRAY, marginTop: 6 }}>a yes / no or this-or-that, cast for this exact moment</div>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginTop: 14 }}>
        {samples.map((s: string) => (
          <Press key={s} scale={0.95} onClick={() => onAsk(s)}>
            <div style={{ padding: "9px 14px", borderRadius: 999, background: "#FFF", border: `1px solid ${aA(accent, 0.28)}`, boxShadow: `0 4px 10px -6px ${aA(accentDeep, 0.4)}` }}>
              <span style={{ fontFamily: SANS, fontSize: 13, fontWeight: 700, color: INK }}>{s}</span>
            </div>
          </Press>
        ))}
      </div>
      <Press scale={0.98} onClick={() => onAsk("")} style={{ marginTop: 12 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "12px 15px", borderRadius: 14, background: aA("#FFF", 0.72), border: `1px dashed ${aA(accentDeep, 0.42)}` }}>
          <Icon n="wand" s={15} c={accentDeep} sw={1.9} />
          <span style={{ fontFamily: SANS, fontSize: 13.5, color: GRAY }}>…or type your own question</span>
        </div>
      </Press>
    </div>
  );
}

// ============================ PLAN TAB (inline body) ============================
function PlanTab({ mood, onMonth, onTool }: any) {
  const { accent, accentDeep, glow } = mood;
  const Entry = ({ ic, c1, c2, title, sub, onClick }: any) => (
    <Press scale={0.985} onClick={onClick} style={{ marginBottom: 10 }}>
      <div style={{ ...pill(18), padding: "14px 15px", display: "flex", alignItems: "center", gap: 13 }}>
        <GlossIcon c1={c1} c2={c2} size={42} radius={13}><Icon n={ic} s={19} c="#FFF" sw={1.8} /></GlossIcon>
        <div style={{ flex: 1 }}><div style={{ fontFamily: SERIF, fontSize: 16.5, fontWeight: 500, color: INK }}>{title}</div><div style={{ fontFamily: SANS, fontSize: 12, color: GRAY, marginTop: 1 }}>{sub}</div></div>
        <Icon n="chevR" s={17} c={GRAY} />
      </div>
    </Press>
  );
  return (
    <div>
      <div style={{ margin: "2px 2px 12px" }}><Label>Today</Label></div>
      <MyDay mood={mood} delay={0} />
      <AskMomentCard mood={mood} delay={60} onAsk={(seed: string) => onTool("ask", seed)} />
      <div style={{ margin: "24px 2px 12px" }}><Label>Plan ahead</Label></div>
      <MyPanchang mood={mood} delay={120} onMonth={onMonth} />
      <Entry ic="compass" c1={glow} c2={accentDeep} title="Find a good day" sub="the best dates and times for something that matters" onClick={() => onTool("muhurat")} />
      <Entry ic="scan" c1={"#2E9C7E"} c2={"#1F7660"} title="Check my plans" sub="we'll check your calendar against your good and bad times" onClick={() => onTool("doctor")} />
      <Entry ic="capsule" c1={"#D98A2B"} c2={"#B26C18"} title="Time Capsule" sub="write to your future self, the sky delivers it" onClick={() => onTool("capsule")} />
    </div>
  );
}

// ============================ TOOL SHEETS ============================
function MuhuratSheet({ mood }: any) {
  const { accent, accentDeep, glow } = mood;
  const [pick, setPick] = useState<string | null>(null);
  const [custom, setCustom] = useState("");
  const [loading, setLoading] = useState(false);
  const res = (MUHURAT.results as any).default;
  const choose = (e: string) => { setPick(e); setLoading(true); setTimeout(() => setLoading(false), 1400); };
  const go = () => { const t = custom.trim(); if (t) choose(t); };
  return (<div>
    <Label c={aA(accentDeep, 0.9)}>Find a good day</Label>
    <div style={{ fontFamily: SERIF, fontSize: 22, fontWeight: 500, color: INK, marginTop: 6 }}>{pick ? `Best times to ${pick.toLowerCase()}` : "What's it for?"}</div>
    {!pick ? (<>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginTop: 16 }}>
        {MUHURAT.events.slice(0, 6).map((e: string) => (<Press key={e} scale={0.95} onClick={() => choose(e)}><div style={{ padding: "9px 15px", borderRadius: 999, ...pill(999) }}><span style={{ fontFamily: SANS, fontWeight: 700, fontSize: 13.5, color: INK }}>{e}</span></div></Press>))}
      </div>
      <div style={{ fontFamily: MONO, fontSize: 9.5, letterSpacing: 0.8, textTransform: "uppercase", color: GRAY, margin: "18px 0 8px" }}>or type your own</div>
      <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "4px 5px 4px 16px", ...pill(999) }}>
        <input value={custom} onChange={(e: any) => setCustom(e.target.value)} onKeyDown={(e: any) => { if (e.key === "Enter") go(); }} placeholder="e.g. move house, launch, propose" style={{ flex: 1, border: "none", outline: "none", background: "transparent", fontFamily: SANS, fontSize: 14, color: INK, padding: "9px 0" }} />
        <Press scale={0.9} onClick={go}><div style={{ background: custom.trim() ? INK : "#D9D5CE", borderRadius: 999, width: 38, height: 38, display: "flex", alignItems: "center", justifyContent: "center", transition: "background .2s" }}><Icon n="arrowR" s={17} c="#FFF" sw={2.2} /></div></Press>
      </div>
    </>) : loading ? (
      <Casting mood={mood} label="reading the days ahead" />
    ) : (<>
      <div style={{ marginTop: 16, display: "flex", flexDirection: "column", gap: 10 }}>
        {res.map((r: any, i: number) => (
          <div key={i} style={{ display: "flex", alignItems: "center", gap: 13, padding: "13px 15px", borderRadius: 16, background: i === 0 ? aA(accent, 0.08) : WASH, border: `1px solid ${i === 0 ? aA(accent, 0.24) : HAIR}` }}>
            <div style={{ width: 34, height: 34, borderRadius: 10, flexShrink: 0, background: `linear-gradient(155deg, ${glow}, ${accentDeep})`, display: "flex", alignItems: "center", justifyContent: "center", boxShadow: `inset 0 1px 1px ${aA("#FFF", 0.5)}` }}><span style={{ fontFamily: SERIF, fontSize: 15, fontWeight: 600, color: "#FFF" }}>{i + 1}</span></div>
            <div style={{ flex: 1 }}><div style={{ fontFamily: SERIF, fontSize: 16, fontWeight: 500, color: INK }}>{r.date}</div><div style={{ fontFamily: SANS, fontSize: 12.5, color: accentDeep, fontWeight: 700, marginTop: 1 }}>{r.time}</div><div style={{ fontFamily: SANS, fontSize: 11.5, color: GRAY, marginTop: 1 }}>{r.note}</div></div>
          </div>
        ))}
      </div>
      <Press scale={0.97} onClick={() => setPick(null)} style={{ display: "inline-block", marginTop: 14 }}><span style={{ fontFamily: SANS, fontSize: 12.5, fontWeight: 700, color: accentDeep }}>← pick something else</span></Press>
    </>)}
  </div>);
}

function CalendarDoctorSheet({ mood }: any) {
  const { accent, accentDeep, glow } = mood;
  const [fixed, setFixed] = useState<number[]>([]);
  const [scanning, setScanning] = useState(true);
  useEffect(() => { const id = setTimeout(() => setScanning(false), 1700); return () => clearTimeout(id); }, []);
  return (<div>
    <Label c={aA(accentDeep, 0.9)}>Check my plans</Label>
    <div style={{ fontFamily: SERIF, fontSize: 22, fontWeight: 500, color: INK, marginTop: 6 }}>Your next few events</div>
    {scanning ? (
      <Casting mood={mood} label="checking your calendar" />
    ) : (<>
    <div style={{ fontFamily: SANS, fontSize: 12.5, color: GRAY, marginTop: 3 }}>we checked them against your good and bad times</div>
    <div style={{ marginTop: 16, display: "flex", flexDirection: "column", gap: 10 }}>
      {CAL_DOCTOR.map((e: any, i: number) => { const weak = e.status === "weak" && !fixed.includes(i); return (
        <div key={i} style={{ padding: "13px 15px", borderRadius: 16, background: weak ? aA(ORANGE, 0.07) : WASH, border: `1px solid ${weak ? aA(ORANGE, 0.3) : HAIR}` }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <div style={{ width: 8, height: 8, borderRadius: 999, flexShrink: 0, background: fixed.includes(i) ? "#3E9C7A" : e.status === "weak" ? ORANGE : "#3E9C7A" }} />
            <div style={{ flex: 1, minWidth: 0 }}><div style={{ fontFamily: SANS, fontSize: 14.5, fontWeight: 700, color: INK }}>{e.title}</div><div style={{ fontFamily: SANS, fontSize: 12, color: GRAY, marginTop: 1 }}>{fixed.includes(i) ? "moved to a better time" : `${e.when} · ${e.why}`}</div></div>
          </div>
          {weak && (<Press scale={0.97} onClick={() => setFixed((f) => [...f, i])} style={{ marginTop: 11 }}><div style={{ padding: "9px 0", borderRadius: 11, textAlign: "center", background: INK }}><span style={{ fontFamily: SANS, fontSize: 12.5, fontWeight: 700, color: "#FFF" }}>{e.better}</span></div></Press>)}
        </div>
      ); })}
    </div>
    </>)}
  </div>);
}

function AskMomentSheet({ mood, onTalk, seed }: any) {
  const { accent, accentDeep, glow } = mood;
  const [q, setQ] = useState(seed || "");
  const [phase, setPhase] = useState<"ask" | "casting" | "done">("ask");
  const [ans, setAns] = useState<any>(null);
  const cast = () => { if (!q.trim()) return; setPhase("casting"); setTimeout(() => { setAns(ASK_MOMENT.answers[(q.trim().length) % ASK_MOMENT.answers.length]); setPhase("done"); }, 1400); };
  const reset = () => { setPhase("ask"); setAns(null); setQ(""); };
  const vc = ans ? (ans.verdict === "Yes" ? "#2F8E66" : ans.verdict === "Wait" ? "#B5781A" : accentDeep) : accentDeep;
  return (<div>
    <Label c={aA(accentDeep, 0.9)}>Ask the Moment</Label>
    {phase !== "done" && (<>
      <div style={{ fontFamily: SERIF, fontSize: 22, fontWeight: 500, color: INK, marginTop: 6 }}>Ask, and the sky answers for right now</div>
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginTop: 14, padding: "4px 5px 4px 15px", borderRadius: 999, ...pill(999) }}>
        <input value={q} onChange={(e: any) => setQ(e.target.value)} placeholder="type your question…" style={{ flex: 1, border: "none", outline: "none", background: "transparent", fontFamily: SANS, fontSize: 14, color: INK, padding: "9px 0" }} />
      </div>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 7, marginTop: 12 }}>
        {ASK_MOMENT.samples.map((s: string) => (<Press key={s} scale={0.95} onClick={() => setQ(s)}><div style={{ padding: "7px 13px", borderRadius: 999, background: WASH, border: `1px solid ${HAIR}` }}><span style={{ fontFamily: SANS, fontSize: 12.5, fontWeight: 600, color: INK2 }}>{s}</span></div></Press>))}
      </div>
      <Press scale={0.97} onClick={cast} style={{ marginTop: 18 }}><div style={{ padding: "14px 0", borderRadius: 14, textAlign: "center", background: q.trim() ? INK : WASH, boxShadow: q.trim() ? `0 10px 20px -8px ${aA(INK, 0.5)}` : "none" }}><span style={{ fontFamily: SANS, fontSize: 14.5, fontWeight: 700, color: q.trim() ? "#FFF" : GRAY }}>{phase === "casting" ? "casting…" : "Cast"}</span></div></Press>
      {phase === "casting" && (<div style={{ display: "flex", justifyContent: "center", marginTop: 20 }}><div style={{ width: 90, height: 90, position: "relative" }}>
        <div style={{ position: "absolute", inset: 0, borderRadius: 999, border: `2px solid ${aA(accent, 0.3)}`, borderTopColor: accentDeep, animation: "spinSlow 1s linear infinite" }} />
        <div style={{ position: "absolute", inset: 16, borderRadius: 999, border: `2px solid ${aA(accent, 0.2)}`, borderBottomColor: accent, animation: "spinSlow 1.4s linear infinite reverse" }} />
        <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center" }}><div style={{ width: 8, height: 8, borderRadius: 999, background: accentDeep, animation: "glowPulse 1.2s ease-in-out infinite", ["--gc" as any]: aA(glow, 0.6) } as any} /></div>
      </div></div>)}
    </>)}
    {phase === "done" && ans && (<div style={{ animation: "fadeIn .4s ease both" }}>
      <div style={{ fontFamily: SANS, fontSize: 13.5, color: GRAY, marginTop: 8, fontStyle: "italic" }}>“{q}”</div>
      <div style={{ fontFamily: SERIF, fontSize: 40, fontWeight: 500, color: vc, letterSpacing: -1, marginTop: 10 }}>{ans.verdict}.</div>
      <div style={{ fontFamily: SERIF, fontSize: 16, lineHeight: 1.5, color: INK2, marginTop: 8, textWrap: "pretty" } as any}>{ans.why}</div>
      <div style={{ fontFamily: SANS, fontSize: 11.5, color: GRAY, marginTop: 10, fontStyle: "italic" }}>a one-time read for this exact moment</div>
      <div style={{ display: "flex", gap: 10, marginTop: 18 }}>
        <Press scale={0.97} onClick={() => onTalk(q)} style={{ flex: 1 }}><div style={{ padding: "13px 0", borderRadius: 13, textAlign: "center", background: INK }}><span style={{ fontFamily: SANS, fontSize: 13.5, fontWeight: 700, color: "#FFF" }}>Talk it through →</span></div></Press>
        <Press scale={0.95} onClick={reset}><div style={{ ...pill(13), padding: "13px 16px" }}><span style={{ fontFamily: SANS, fontSize: 13.5, fontWeight: 700, color: INK }}>Ask again</span></div></Press>
      </div>
    </div>)}
  </div>);
}

function TimeCapsuleSheet({ mood }: any) {
  const { accent, accentDeep, glow } = mood;
  const [note, setNote] = useState("");
  const [when, setWhen] = useState<string | null>(null);
  const [phase, setPhase] = useState<"write" | "sealing" | "sealed">("write");
  const seal = () => { if (!note.trim() || !when) return; setPhase("sealing"); setTimeout(() => setPhase("sealed"), 2000); };
  if (phase === "sealing") return (<div style={{ textAlign: "center", padding: "26px 0 18px" }}>
    <div style={{ width: 92, height: 92, margin: "0 auto", position: "relative" }}>
      <div style={{ position: "absolute", inset: 0, borderRadius: 999, border: `2px solid ${aA(accent, 0.25)}`, borderTopColor: accentDeep, animation: "spinSlow 1.1s linear infinite" }} />
      <div style={{ position: "absolute", inset: 10, borderRadius: 999, border: `2px solid ${aA(glow, 0.3)}`, borderBottomColor: glow, animation: "spinSlow 1.5s linear infinite reverse" }} />
      <div style={{ position: "absolute", inset: 22, borderRadius: 999, background: `radial-gradient(circle at 40% 34%, ${glow}, ${accentDeep})`, display: "flex", alignItems: "center", justifyContent: "center", animation: "glowPulse 1.6s ease-in-out infinite", ["--gc" as any]: aA(glow, 0.6) } as any}><Icon n="capsule" s={24} c="#FFF" sw={1.7} /></div>
    </div>
    <div style={{ fontFamily: SERIF, fontStyle: "italic", fontSize: 17, color: INK, marginTop: 22 }}>sealing it to the sky…</div>
  </div>);
  if (phase === "sealed") return (<div style={{ textAlign: "center", padding: "14px 0 6px" }}>
    <div style={{ width: 76, height: 76, margin: "0 auto", position: "relative" }}>
      <div style={{ position: "absolute", inset: 0, borderRadius: 999, background: `radial-gradient(circle at 40% 34%, ${glow}, ${accentDeep})`, boxShadow: `0 10px 30px -8px ${aA(accentDeep, 0.6)}`, display: "flex", alignItems: "center", justifyContent: "center", animation: "popIn .5s cubic-bezier(.34,1.5,.5,1) both" }}><Icon n="capsule" s={34} c="#FFF" sw={1.6} /></div>
      <div style={{ position: "absolute", inset: -8, borderRadius: 999, ["--gc" as any]: aA(glow, 0.5), animation: "glowPulse 3s ease-in-out infinite" } as any} />
    </div>
    <div style={{ fontFamily: SERIF, fontSize: 21, fontWeight: 500, color: INK, marginTop: 18 }}>Sealed.</div>
    <div style={{ fontFamily: SERIF, fontStyle: "italic", fontSize: 15, color: GRAY, marginTop: 6, padding: "0 20px" }}>The sky will bring it back to you {when}.</div>
  </div>);
  return (<div>
    <Label c={aA(accentDeep, 0.9)}>Time Capsule</Label>
    <div style={{ fontFamily: SERIF, fontSize: 22, fontWeight: 500, color: INK, marginTop: 6 }}>Write to your future self</div>
    <textarea value={note} onChange={(e: any) => setNote(e.target.value)} placeholder="what do you want them to remember?" rows={4} style={{ width: "100%", boxSizing: "border-box", marginTop: 14, padding: 15, resize: "none", border: `1px solid ${HAIR}`, borderRadius: 16, outline: "none", background: WASH, color: INK, fontFamily: SERIF, fontSize: 16, lineHeight: 1.55 }} />
    <div style={{ marginTop: 14, marginBottom: 8 }}><Label>Deliver on</Label></div>
    <Press scale={0.98} onClick={() => setWhen("on a date you pick")}><div style={{ ...pill(13), padding: "12px 15px", display: "flex", alignItems: "center", gap: 11, marginBottom: 10, border: when === "on a date you pick" ? `1px solid ${aA(accentDeep, 0.4)}` : pill(13).border }}><Icon n="cal" s={18} c={accentDeep} sw={1.8} /><span style={{ flex: 1, fontFamily: SANS, fontSize: 14, fontWeight: 700, color: INK }}>Pick a date</span>{when === "on a date you pick" && <Icon n="check" s={16} c={accentDeep} sw={2.4} />}</div></Press>
    <div style={{ fontFamily: SANS, fontSize: 12, color: GRAY, margin: "2px 2px 8px" }}>or pick a moment:</div>
    <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
      {TIME_CAPSULE.moments.map((m: string) => { const on = when === m; return (
        <Press key={m} scale={0.98} onClick={() => setWhen(m)}><div style={{ padding: "12px 15px", borderRadius: 13, background: on ? aA(accent, 0.1) : WASH, border: `1px solid ${on ? aA(accentDeep, 0.35) : HAIR}`, display: "flex", alignItems: "center", gap: 10 }}><div style={{ width: 7, height: 7, borderRadius: 999, background: on ? accentDeep : GRAY }} /><span style={{ flex: 1, fontFamily: SERIF, fontSize: 15, color: INK }}>{m}</span>{on && <Icon n="check" s={15} c={accentDeep} sw={2.4} />}</div></Press>
      ); })}
    </div>
    <Press scale={0.97} onClick={seal} style={{ marginTop: 18 }}><div style={{ padding: "14px 0", borderRadius: 14, textAlign: "center", background: (note.trim() && when) ? INK : WASH, boxShadow: (note.trim() && when) ? `0 10px 20px -8px ${aA(INK, 0.5)}` : "none" }}><span style={{ fontFamily: SANS, fontSize: 14.5, fontWeight: 700, color: (note.trim() && when) ? "#FFF" : GRAY }}>Seal it</span></div></Press>
    {TIME_CAPSULE.shelf.length > 0 && (<div style={{ marginTop: 20, paddingTop: 16, borderTop: `1px solid ${HAIR}` }}>
      <Label>Your shelf</Label>
      <div style={{ marginTop: 10, display: "flex", flexDirection: "column", gap: 9 }}>
        {TIME_CAPSULE.shelf.map((c: any, i: number) => (
          <div key={i} style={{ display: "flex", alignItems: "center", gap: 11 }}>
            <div style={{ width: 30, height: 30, borderRadius: 9, flexShrink: 0, display: "flex", alignItems: "center", justifyContent: "center", background: c.state === "landed" ? `linear-gradient(155deg, ${glow}, ${accentDeep})` : WASH, border: c.state === "landed" ? "none" : `1px solid ${HAIR}` }}><Icon n="capsule" s={15} c={c.state === "landed" ? "#FFF" : GRAY} sw={1.7} /></div>
            <div style={{ flex: 1, minWidth: 0 }}><div style={{ fontFamily: SERIF, fontSize: 14, color: INK, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{c.state === "landed" ? c.note : "a sealed note"}</div><div style={{ fontFamily: SANS, fontSize: 11, color: GRAY, marginTop: 1 }}>{c.state === "landed" ? `arrived ${c.on}` : `for ${c.to}`}</div></div>
            {c.state === "sealed" && <span style={{ fontFamily: MONO, fontSize: 9, letterSpacing: 0.8, textTransform: "uppercase", color: GRAY }}>sealed</span>}
          </div>
        ))}
      </div>
    </div>)}
  </div>);
}

// ===== the compact "why?" sheet (Read hero) and the full good/bad-times sheet =====
function WhySheet({ mood }: any) {
  const { accentDeep } = mood;
  return (<div>
    <Label c={aA(accentDeep, 0.9)}>Why today feels like this</Label>
    <div style={{ fontFamily: SERIF, fontSize: 23, fontWeight: 500, color: INK, marginTop: 6 }}>{mood.key}</div>
    <div style={{ fontFamily: SERIF, fontSize: 16.5, lineHeight: 1.55, color: INK2, marginTop: 12, textWrap: "pretty" } as any}>{mood.forecast.why}</div>
    <div style={{ marginTop: 16, padding: 15, borderRadius: 14, background: WASH }}><Label>One thing to do</Label><div style={{ fontFamily: SERIF, fontSize: 15.5, lineHeight: 1.5, color: INK, marginTop: 5 }}>{mood.forecast.action}</div></div>
  </div>);
}

function GoodBadSheet({ mood, onPlan }: any) {
  const { accent, accentDeep, glow } = mood;
  const wins = [["Best", "11:40a – 12:30p", "important talks", "#3E9C7A"], ["Good", "2:00 – 3:15p", "steady work", accentDeep], ["Ordinary", "3:15 – 6:00p", "everyday things", GRAY], ["Hold off", "9:00 – 10:30a", "big decisions", "#C9954A"], ["Avoid", "6:30 – 7:15p", "rest, don't push", ORANGE]];
  return (<div>
    <Label c={aA(accentDeep, 0.9)}>Good & bad times today</Label>
    <div style={{ fontFamily: SERIF, fontSize: 22, fontWeight: 500, color: INK, marginTop: 6, marginBottom: 4 }}>The whole day</div>
    {wins.map(([k, t, note, c]: any, i) => (
      <div key={i} style={{ display: "flex", alignItems: "center", gap: 12, padding: "13px 0", borderTop: i ? `1px solid ${HAIR}` : "none" }}>
        <div style={{ width: 8, height: 8, borderRadius: 999, background: c, flexShrink: 0 }} />
        <div style={{ width: 64, flexShrink: 0 }}><span style={{ fontFamily: MONO, fontSize: 10, fontWeight: 600, letterSpacing: 0.8, textTransform: "uppercase", color: c }}>{k}</span></div>
        <div style={{ flex: 1 }}><div style={{ fontFamily: SERIF, fontSize: 15.5, color: INK }}>{t}</div><div style={{ fontFamily: SANS, fontSize: 12, color: GRAY }}>{note}</div></div>
      </div>
    ))}
    <Press scale={0.98} onClick={onPlan} style={{ marginTop: 16 }}><div style={{ padding: "13px 0", borderRadius: 13, textAlign: "center", background: INK, boxShadow: `0 10px 20px -8px ${aA(INK, 0.5)}` }}><span style={{ fontFamily: SANS, fontSize: 14, fontWeight: 700, color: "#FFF" }}>Plan your day →</span></div></Press>
  </div>);
}

(window as any).__astroPlan = { PlanTab, MonthScreen, MuhuratSheet, CalendarDoctorSheet, AskMomentSheet, TimeCapsuleSheet, WhySheet, GoodBadSheet };
})();
