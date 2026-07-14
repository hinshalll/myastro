// astro-today.tsx — the Today screen pieces, in the ASTROLO-clean language. Persistent top
// cluster (avatar left, bell, Diya chip right), all titled cards one-per-line, the floating
// Moon companion, and the five-tab bottom nav. Reads atoms from window.__astroUI.
;(function () {
const U = (window as any).__astroUI;
const { useState, useRef, useEffect, useMemo, aA, PAPER, WASH, INK, INK2, GRAY, HAIR, ORANGE, SANS, SERIF, MONO,
  pill, card, Label, Icon, I, Flame, GlossIcon, Press, MoodEmblem, MoonGloss, Ganesha, MOOD, PERSONAL, DAY_LINE, AHEAD, ECL, MIR, CHECKIN, CLOCK, ALMANAC, FOCUS, READ_CHIPS, HORA, LIFE_AREAS, FESTIVAL, NAME, DATE, rise } = U;

// ===== persistent TOP CLUSTER — avatar (You) left · Diya chip (Wallet) right =====
function TopCluster({ mood, bal, bump, alert, onProfile, onWallet, onBell }: any) {
  const { accent, accentDeep, glow } = mood;
  const [floats, setFloats] = useState<number[]>([]);
  const last = useRef(bump).current;
  useEffect(() => { if (bump && bump !== last) { const id = Date.now(); setFloats((f) => [...f, id]); setTimeout(() => setFloats((f) => f.filter((x) => x !== id)), 800); } }, [bump]);
  return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
      <Press scale={0.94} onClick={onProfile}><div style={{ width: 44, height: 44, borderRadius: 999, background: `linear-gradient(145deg, ${glow}, ${accentDeep})`, padding: 2, boxShadow: `0 3px 10px -2px ${aA(accentDeep, 0.5)}` }}><div style={{ width: "100%", height: "100%", borderRadius: 999, background: WASH, display: "flex", alignItems: "center", justifyContent: "center", border: "2px solid #FFF" }}><span style={{ fontFamily: SERIF, fontWeight: 600, fontSize: 18, color: INK }}>{NAME[0]}</span></div></div></Press>
      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
        <Press scale={0.9} onClick={onBell}><div style={{ ...pill(999), width: 42, height: 42, display: "flex", alignItems: "center", justifyContent: "center", position: "relative" }}><Icon n="bell" s={17} c={INK} sw={1.8} />{alert && <div style={{ position: "absolute", top: 9, right: 10, width: 7, height: 7, borderRadius: 999, background: ORANGE, border: "1.5px solid #FFF" }} />}</div></Press>
        <Press scale={0.94} onClick={onWallet}><div style={{ ...pill(999), padding: "9px 14px", display: "flex", alignItems: "center", gap: 6, position: "relative" }}><Flame s={15} c={glow} /><span style={{ fontFamily: SANS, fontWeight: 800, fontSize: 15, color: INK }}>{bal}</span>{floats.map((id) => (<span key={id} style={{ position: "absolute", top: -2, right: 12, fontFamily: SANS, fontWeight: 800, fontSize: 13, color: accentDeep, animation: "coinUp .8s ease-out forwards", pointerEvents: "none" }}>+1</span>))}</div></Press>
      </div>
    </div>
  );
}

// ===== LIVING SKY HEADER — time-aware (dawn/noon/dusk/night), tonight's Moon phase,
// the greeting, the personal line, and a bell. "It is this moment."
function nowH() { const d = new Date(); let h = d.getHours() + d.getMinutes() / 60; return h; }
// four time-of-day skies — each a full little scene. The header can PREVIEW any of them
// (tap the card to cycle dawn → day → dusk → night, then back to live).
const SKIES: any = {
  dawn:  { greet: "Good morning",   grad: "linear-gradient(165deg, #F9CD9C 0%, #FBE3C6 54%, #FDF4E9 100%)", ink: "#3A2A18", sub: "#8A6A48", cel: "sun",  sunC: ["#FFF6DA", "#FFCD82"], glowC: "rgba(255,193,116,0.68)", stars: 0, clouds: 2, label: "Dawn" },
  day:   { greet: "Good afternoon", grad: "linear-gradient(165deg, #A6D0F2 0%, #CDE5F6 54%, #EEF6FC 100%)", ink: "#25384B", sub: "#5C7793", cel: "sun",  sunC: ["#FFFCF0", "#FFE29A"], glowC: "rgba(255,212,116,0.62)", stars: 0, clouds: 3, label: "Day" },
  dusk:  { greet: "Good evening",   grad: "linear-gradient(165deg, #E89A76 0%, #C489AE 52%, #9A82C6 100%)", ink: "#FFF6EF", sub: "rgba(255,246,239,0.85)", cel: "moon", glowC: "rgba(255,224,188,0.5)",  stars: 6,  clouds: 1, label: "Dusk" },
  night: { greet: "Good night",     grad: "linear-gradient(170deg, #1F2A4E 0%, #2F3B64 52%, #424E7A 100%)", ink: "#F4EFFA", sub: "rgba(244,239,250,0.8)",  cel: "moon", glowC: "rgba(182,192,255,0.42)", stars: 16, clouds: 0, label: "Night" },
};
function skyNameFor(h: number) { if (h >= 5 && h < 8) return "dawn"; if (h >= 8 && h < 17) return "day"; if (h >= 17 && h < 20) return "dusk"; return "night"; }
// a small moon showing a phase (waxing gibbous demo): lit disc + offset soft shadow
function PhaseMoon({ mood, size = 46 }: any) {
  const { moon, accentDeep } = mood; const body = moon || "#EAE0CC";
  return (
    <div style={{ width: size, height: size, position: "relative", borderRadius: 999, overflow: "hidden", boxShadow: `0 0 ${size * 0.5}px ${aA("#FFF6DC", 0.5)}, inset -2px -2px 6px ${aA(accentDeep, 0.35)}`, background: `radial-gradient(circle at 38% 32%, #FFFDF6 0%, ${body} 60%, #D8CAB0 100%)` }}>
      <div style={{ position: "absolute", left: "12%", top: "26%", width: "20%", height: "20%", borderRadius: 999, background: aA(accentDeep, 0.12) }} />
      <div style={{ position: "absolute", left: "50%", top: "55%", width: "16%", height: "16%", borderRadius: 999, background: aA(accentDeep, 0.1) }} />
      {/* shadow carving the phase */}
      <div style={{ position: "absolute", top: -1, bottom: -1, left: "-34%", width: "100%", borderRadius: 999, background: "radial-gradient(circle at 70% 50%, rgba(20,24,46,0.0) 40%, rgba(20,24,46,0.55) 62%)" }} />
    </div>
  );
}
function LivingSkyHeader({ mood, delay, onBell }: any) {
  const liveName = useMemo(() => skyNameFor(nowH()), []);
  const seq = ["dawn", "day", "dusk", "night"];
  const [ov, setOv] = useState<string | null>(null);
  const name = ov || liveName;
  const sky = SKIES[name];
  const dark = name === "night" || name === "dusk";
  const greet = name === "day" && !ov && nowH() < 12 ? "Good morning" : sky.greet;
  const stars = useMemo(() => { let s = 7; const r = () => { s = (s * 9301 + 49297) % 233280; return s / 233280; }; return Array.from({ length: 18 }, () => ({ x: r() * 100, y: r() * 60, sz: 1 + r() * 1.7, lo: 0.12 + r() * 0.2, hi: 0.55 + r() * 0.45, d: 2.4 + r() * 3 })); }, []);
  const clouds = useMemo(() => { let s = 41; const r = () => { s = (s * 9301 + 49297) % 233280; return s / 233280; }; return Array.from({ length: 3 }, (_, i) => ({ y: 8 + r() * 30, w: 56 + r() * 44, o: 0.4 + r() * 0.4, d: 34 + r() * 22, dl: -i * 12, start: 4 + r() * 60 })); }, []);
  const cycle = () => { const nn = seq[(seq.indexOf(name) + 1) % 4]; setOv(nn === liveName ? null : nn); };
  return (
    <div onClick={cycle} style={{ ...rise(delay), position: "relative", borderRadius: 26, overflow: "hidden", padding: "18px 18px 20px", background: sky.grad, boxShadow: `0 14px 30px -16px ${aA("#1A1408", 0.3)}, inset 0 1px 0 ${aA("#FFF", 0.4)}`, cursor: "pointer", transition: "background .7s ease" }}>
      {/* celestial scene */}
      <div style={{ position: "absolute", inset: 0, pointerEvents: "none", overflow: "hidden" }}>
        {dark && stars.slice(0, sky.stars).map((st: any, i: number) => (<div key={i} style={{ position: "absolute", left: `${st.x}%`, top: `${st.y}%`, width: st.sz, height: st.sz, borderRadius: 999, background: "#FFF", ["--lo" as any]: st.lo, ["--hi" as any]: st.hi, animation: `twinkle ${st.d}s ease-in-out ${-i * 0.3}s infinite` } as any} />))}
        {sky.clouds > 0 && clouds.slice(0, sky.clouds).map((cl: any, i: number) => (<div key={i} style={{ position: "absolute", top: `${cl.y}%`, left: `${cl.start}%`, width: cl.w, height: cl.w * 0.4, borderRadius: 999, background: aA("#FFF", cl.o), filter: "blur(7px)", animation: `cloudDrift ${cl.d}s ease-in-out ${cl.dl}s infinite` }} />))}
        <div style={{ position: "absolute", right: 18, top: 22, animation: "floatY 7s ease-in-out infinite" }}>
          {sky.cel === "moon"
            ? <PhaseMoon mood={mood} size={44} />
            : <div style={{ width: 44, height: 44, borderRadius: 999, background: `radial-gradient(circle at 40% 38%, ${sky.sunC[0]} 0%, ${sky.sunC[1]} 52%, ${aA(sky.sunC[1], 0)} 74%)`, boxShadow: `0 0 34px ${sky.glowC}` }} />}
        </div>
      </div>
      {/* greeting */}
      <div style={{ position: "relative", marginTop: 22, zIndex: 2 }}>
        <span style={{ fontFamily: MONO, fontSize: 10.5, fontWeight: 600, letterSpacing: 1.6, textTransform: "uppercase", color: sky.sub }}>{DATE}</span>
        <div style={{ fontFamily: SERIF, fontSize: 27, fontWeight: 500, color: sky.ink, letterSpacing: -0.5, marginTop: 3, maxWidth: 216 }}>{greet}, <span style={{ fontStyle: "italic" }}>{NAME}</span></div>
        {FESTIVAL && (<div style={{ display: "inline-flex", alignItems: "center", gap: 6, marginTop: 9, padding: "5px 12px", borderRadius: 999, background: aA("#FFF", dark ? 0.18 : 0.55), backdropFilter: "blur(6px)" }}><span style={{ fontSize: 12 }}>🪔</span><span style={{ fontFamily: SERIF, fontSize: 14, fontWeight: 500, fontStyle: "italic", color: sky.ink }}>{FESTIVAL}</span></div>)}
        {HORA && (<div style={{ display: "flex", alignItems: "center", gap: 7, marginTop: 10 }}>
          <span style={{ width: 6, height: 6, borderRadius: 999, flexShrink: 0, background: !dark ? "#3E9C7A" : "#8FE0BF", boxShadow: `0 0 7px ${aA(!dark ? "#3E9C7A" : "#8FE0BF", 0.9)}`, animation: "glowPulse 2.6s ease-in-out infinite", ["--gc" as any]: aA("#8FE0BF", 0.5) } as any} />
          <span style={{ fontFamily: SERIF, fontStyle: "italic", fontSize: 15, lineHeight: 1.4, color: sky.sub, maxWidth: 224, textWrap: "pretty" } as any}>{HORA}</span>
        </div>)}
      </div>
    </div>
  );
}

// ===== floating MOON companion (every screen but chat) — small, cute, cozy =====
function MoonFAB({ mood, insight, onTap }: any) {
  const { glow, accentDeep } = mood;
  const [poke, setPoke] = useState(false);
  return (
    <div style={{ position: "absolute", right: 14, bottom: 94, zIndex: 50 }}>
      <div style={{ position: "relative" }}>
        <Press scale={0.9} onClick={onTap}>
          <div onPointerDown={() => { setPoke(true); setTimeout(() => setPoke(false), 460); }}
            style={{ width: 68, height: 72, position: "relative", animation: "floatY 6s ease-in-out infinite" }}>
            {/* soft warm glow */}
            <div style={{ position: "absolute", inset: -6, borderRadius: 999, background: `radial-gradient(circle at 50% 42%, ${aA(glow, insight ? 0.5 : 0.3)}, ${aA(glow, 0)} 70%)`, animation: `haloBreathe ${insight ? 3 : 4.8}s ease-in-out infinite` }} />
            {/* the companion — the art already is a chat bubble */}
            <img src="chatfab.png" alt="Talk to your guide" draggable={false}
              style={{ position: "relative", width: "100%", height: "100%", objectFit: "contain", filter: `drop-shadow(0 6px 12px ${aA("#1A1408", 0.28)})`, transform: poke ? "scale(1.08) rotate(-3deg)" : "none", transition: "transform .46s cubic-bezier(.34,1.5,.5,1)" }} />
          </div>
        </Press>
        {/* unread notification dot — a fresh message from your guide */}
        {insight && (
          <div style={{ position: "absolute", right: 4, top: 2, zIndex: 3, pointerEvents: "none" }}>
            <div style={{ position: "absolute", inset: -4, borderRadius: 999, background: aA("#E5484D", 0.4), animation: "pulseRing 1.8s ease-out infinite" }} />
            <div style={{ position: "relative", width: 13, height: 13, borderRadius: 999, background: "#E5484D", border: "2px solid #FFF", boxShadow: `0 1px 4px ${aA("#1A1408", 0.4)}` }} />
          </div>
        )}
      </div>
    </div>
  );
}

// ===== ECLIPSE heads-up (conditional, first) =====
// solar vs lunar eclipse — two distinct little celestial glyphs
function EclipseGlyph({ type }: any) {
  if (type === "solar") {
    return (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <defs>
          <radialGradient id="eclSun" cx="46%" cy="44%" r="62%">
            <stop offset="0" stopColor="#FFF6DC" /><stop offset="0.6" stopColor="#FFD684" /><stop offset="1" stopColor="#F4A83C" />
          </radialGradient>
        </defs>
        <g stroke="#FFECB8" strokeWidth="1.5" strokeLinecap="round" opacity="0.92">
          <path d="M12 1.6v2.1" /><path d="M12 20.3v2.1" /><path d="M1.6 12h2.1" /><path d="M20.3 12h2.1" />
          <path d="M4.3 4.3l1.5 1.5" /><path d="M18.2 18.2l1.5 1.5" /><path d="M4.3 19.7l1.5-1.5" /><path d="M18.2 5.8l1.5-1.5" />
        </g>
        <circle cx="12" cy="12" r="7" fill="url(#eclSun)" />
        <circle cx="15.4" cy="9.2" r="6" fill="#2C2A46" />
      </svg>
    );
  }
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
      <defs>
        <radialGradient id="eclMoon" cx="40%" cy="38%" r="66%">
          <stop offset="0" stopColor="#F5F0FC" /><stop offset="1" stopColor="#CEC6E6" />
        </radialGradient>
      </defs>
      <circle cx="12" cy="12" r="8" fill="url(#eclMoon)" />
      <circle cx="16.2" cy="13.2" r="7.6" fill="#B5462F" opacity="0.6" />
      <circle cx="9.3" cy="9.8" r="1.2" fill="#C7BEDC" opacity="0.85" />
      <circle cx="10.6" cy="14.4" r="0.9" fill="#C7BEDC" opacity="0.7" />
    </svg>
  );
}
function EclipseCard({ mood, delay, onOpen, type, onToggleType }: any) {
  const { accent, accentDeep, glow } = mood;
  const t = type || ECL.type;
  const tile = t === "solar" ? ["#F6B24A", "#CE7C1B"] : ["#8385C8", "#4B4B88"];
  return (
    <Press scale={0.99} onClick={onOpen} style={{ ...rise(delay), marginBottom: 14 }}>
      <div style={{ ...card({ padding: "14px 16px", display: "flex", alignItems: "center", gap: 13, border: `1px solid ${aA(accent, 0.25)}` }) }}>
        <div onPointerDown={(e: any) => e.stopPropagation()} onClick={(e: any) => { e.stopPropagation(); onToggleType && onToggleType(); }} style={{ position: "relative", cursor: "pointer", flexShrink: 0 }} title="tap to switch">
          <GlossIcon c1={tile[0]} c2={tile[1]} size={42} radius={13}><EclipseGlyph type={t} /></GlossIcon>
          <div style={{ position: "absolute", right: -5, bottom: -5, width: 18, height: 18, borderRadius: 999, background: "#FFF", border: `1px solid ${HAIR}`, display: "flex", alignItems: "center", justifyContent: "center", boxShadow: `0 1px 3px ${aA("#1A1408", 0.22)}` }}><Icon n="sync" s={11} c={accentDeep} sw={2} /></div>
        </div>
        <div style={{ flex: 1 }}>
          <Label c={aA(accentDeep, 0.9)}>Heads up</Label>
          <div style={{ fontFamily: SERIF, fontSize: 17, fontWeight: 500, color: INK, marginTop: 2 }}>A {t} eclipse in {ECL.inDays} days</div>
          <div style={{ fontFamily: SANS, fontSize: 12.5, color: GRAY, marginTop: 2, lineHeight: 1.4 }}>{ECL.short ? ECL.short[t] : ""}</div>
        </div>
        <Icon n="chevR" s={17} c={GRAY} />
      </div>
    </Press>
  );
}

// ===== READ · PLAN sub-tab switcher (pinned at top of Today, under the cluster) =====
function SubTabs({ mood, value, onChange }: any) {
  const { accent, accentDeep, glow } = mood;
  const tabs = ["Read", "Plan"];
  return (
    <div style={{ display: "flex", padding: 4, borderRadius: 999, background: WASH, border: `1px solid ${HAIR}`, boxShadow: `inset 0 1px 2px ${aA("#1A1408", 0.05)}` }}>
      {tabs.map((t) => { const on = value === t; return (
        <Press key={t} scale={0.97} onClick={() => onChange(t)} style={{ flex: 1 }}>
          <div style={{ padding: "9px 0", borderRadius: 999, textAlign: "center", background: on ? "#FFF" : "transparent", boxShadow: on ? `0 3px 10px -4px ${aA("#1A1408", 0.28)}, inset 0 1px 1px #FFF` : "none", transition: "background .2s" }}>
            <span style={{ fontFamily: SANS, fontSize: 14, fontWeight: on ? 800 : 700, color: on ? INK : GRAY, letterSpacing: 0.2 }}>{t}</span>
          </div>
        </Press>
      ); })}
    </div>
  );
}

// ===== TODAY reading (the hero) — mood word + sentence + personal + chips + timing + why? =====
function ReadingCard({ mood, delay, onCycle, onShare, onTiming }: any) {
  const { accent, accentDeep, glow } = mood;
  const [whyOpen, setWhyOpen] = useState(false);
  const chips = (READ_CHIPS as any)[mood.key] || { good: [], easy: [] };
  const GOODC = "#2E7D5B", EASYC = "#B4503E";
  const Chip = ({ label, tone }: any) => (
    <div style={{ display: "inline-flex", alignItems: "center", gap: 6, padding: "6px 12px 6px 10px", borderRadius: 999, background: tone === "good" ? "rgba(62,156,122,0.11)" : "rgba(198,90,74,0.09)", border: `1px solid ${tone === "good" ? "rgba(62,156,122,0.30)" : "rgba(198,90,74,0.26)"}` }}>
      <span style={{ width: 5, height: 5, borderRadius: 999, flexShrink: 0, background: tone === "good" ? GOODC : EASYC }} />
      <span style={{ fontFamily: SANS, fontWeight: 700, fontSize: 12.5, color: tone === "good" ? GOODC : EASYC }}>{label}</span>
    </div>
  );
  return (
    <div style={{ ...card({ padding: 20, marginBottom: 24, background: `linear-gradient(165deg, #FFFFFF 0%, ${aA(glow, 0.07)} 100%)` }), ...rise(delay) }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div style={{ flex: 1, paddingRight: 14 }}>
          <div style={{ marginBottom: 9 }}><Label c={aA(accentDeep, 0.9)}>Today's reading</Label></div>
          <Press onClick={onCycle} scale={0.96} style={{ display: "inline-block" }}><span style={{ fontFamily: SERIF, fontSize: 48, fontWeight: 500, color: INK, letterSpacing: -1.4, lineHeight: 1 }}>{mood.key}</span></Press>
        </div>
        <MoodEmblem mood={mood} size={60} />
      </div>
      <div style={{ fontFamily: SERIF, fontSize: 18, lineHeight: 1.45, color: INK2, marginTop: 14, textWrap: "pretty" } as any}>{mood.forecast.mood}</div>
      {PERSONAL[mood.key] && (
        <div style={{ display: "flex", gap: 10, alignItems: "flex-start", marginTop: 14 }}>
          <div style={{ width: 7, height: 7, borderRadius: 999, background: accent, marginTop: 7, flexShrink: 0 }} />
          <span style={{ fontFamily: SERIF, fontStyle: "italic", fontSize: 15.5, lineHeight: 1.45, color: INK2, textWrap: "pretty" } as any}>{PERSONAL[mood.key]}</span>
        </div>
      )}
      {/* good-for / go-easy chip rows */}
      <div style={{ marginTop: 16, paddingTop: 16, borderTop: `1px solid ${HAIR}`, display: "flex", flexDirection: "column", gap: 12 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" }}>
          <span style={{ fontFamily: MONO, fontSize: 9, fontWeight: 700, letterSpacing: 0.8, textTransform: "uppercase", color: GOODC, width: 50, flexShrink: 0 }}>Good<br />for</span>
          {chips.good.map((c: string) => <Chip key={c} label={c} tone="good" />)}
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" }}>
          <span style={{ fontFamily: MONO, fontSize: 9, fontWeight: 700, letterSpacing: 0.8, textTransform: "uppercase", color: EASYC, width: 50, flexShrink: 0 }}>Go<br />easy</span>
          {chips.easy.map((c: string) => <Chip key={c} label={c} tone="easy" />)}
        </div>
      </div>
      {chips.offDay && (<div style={{ fontFamily: SERIF, fontStyle: "italic", fontSize: 14, color: GRAY, marginTop: 12 }}>a low-key day for you, keep it light</div>)}
      {/* footer: the day's single timing nugget → jumps to Plan / My Day */}
      <Press scale={0.98} onClick={onTiming} style={{ marginTop: 16 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 11, padding: "12px 14px", borderRadius: 14, background: aA(accent, 0.07), border: `1px solid ${aA(accent, 0.18)}` }}>
          <Icon n="clock" s={17} c={accentDeep} sw={1.9} />
          <div style={{ flex: 1, minWidth: 0 }}><span style={{ fontFamily: SANS, fontSize: 13, fontWeight: 700, color: INK }}>Strongest window today</span><span style={{ fontFamily: SANS, fontSize: 13, fontWeight: 700, color: accentDeep }}>  ·  11:40–12:30</span></div>
          <Icon n="chevR" s={16} c={accentDeep} />
        </div>
      </Press>
      <div style={{ display: "flex", alignItems: "center", gap: 10, marginTop: 14 }}>
        <Press onClick={() => setWhyOpen((v: boolean) => !v)} scale={0.97} style={{ flex: 1 }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 8, padding: "13px 18px", borderRadius: 14, background: INK, boxShadow: `0 8px 18px -8px ${aA(INK, 0.55)}` }}><span style={{ fontFamily: SANS, fontSize: 13.5, fontWeight: 700, color: "#FFF", letterSpacing: 0.2 }}>{whyOpen ? "close" : "why this?"}</span><div style={{ transform: whyOpen ? "rotate(180deg)" : "none", transition: "transform .25s", display: "flex" }}><Icon n="chevD" s={14} c="#FFF" /></div></div>
        </Press>
        <Press scale={0.94} onClick={onShare}><div style={{ ...pill(14), width: 48, height: 48, display: "flex", alignItems: "center", justifyContent: "center" }}><Icon n="share" s={18} c={INK} /></div></Press>
      </div>
      {/* why — inline accordion, grounded in the actual planet / nakshatra / day-star */}
      <div style={{ overflow: "hidden", maxHeight: whyOpen ? 260 : 0, opacity: whyOpen ? 1 : 0, transition: "max-height .32s ease, opacity .28s ease, margin-top .32s ease", marginTop: whyOpen ? 14 : 0 }}>
        <div style={{ padding: 15, borderRadius: 14, background: WASH, border: `1px solid ${HAIR}` }}>
          <span style={{ fontFamily: SERIF, fontSize: 15.5, lineHeight: 1.55, color: INK2, textWrap: "pretty" } as any}>{mood.forecast.why}</span>
        </div>
      </div>
    </div>
  );
}

// ===== GOOD & BAD TIMES — compact strip (opens the full-day sheet) =====
function GoodBadStrip({ mood, delay, onOpen }: any) {
  const { accent, accentDeep, glow } = mood;
  // live dot when the current time falls inside a window
  const inWindow = useMemo(() => { let h = nowH(); return (h >= 11.66 && h <= 12.5) || (h >= 9 && h <= 10.5); }, []);
  return (
    <>
      <div style={{ marginBottom: 10, ...rise(delay) }}><Label>Good & bad times</Label></div>
      <Press scale={0.985} onClick={onOpen} style={{ ...rise(delay + 20), marginBottom: 24 }}>
        <div style={{ ...pill(18), padding: "13px 15px", display: "flex", alignItems: "center", gap: 13 }}>
          <GlossIcon c1={glow} c2={accentDeep}><Icon n="clock" s={19} c="#FFF" sw={1.8} /></GlossIcon>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 7 }}>
              <span style={{ fontFamily: SANS, fontWeight: 800, fontSize: 14.5, color: INK }}>Strongest 11:40–12:30</span>
              {inWindow && <span style={{ width: 7, height: 7, borderRadius: 999, background: "#3E9C7A", boxShadow: "0 0 0 3px rgba(62,156,122,0.18)", animation: "glowPulse 2.4s ease-in-out infinite", ["--gc" as any]: "rgba(62,156,122,0.5)" } as any} />}
            </div>
            <div style={{ fontFamily: SANS, fontSize: 12.5, color: GRAY, marginTop: 2 }}>Best to hold off 9:00–10:30</div>
          </div>
          <Icon n="chevR" s={18} c={GRAY} />
        </div>
      </Press>
    </>
  );
}

// ===== CHECK IN — an auto-rising POPUP (bottom-sheet content) + a slim reachable chip =====
function CheckInSheet({ mood, onEarn, onClose }: any) {
  const { accent, accentDeep, glow } = mood;
  const [mSel, setMSel] = useState<string | null>(null);
  const [eSel, setESel] = useState<string | null>(null);
  const both = mSel && eSel;
  const reflection = both ? CHECKIN(mSel, eSel, mood.key) : "";
  useEffect(() => { if (both) { onEarn(1); const t = setTimeout(() => onClose(true), 2600); return () => clearTimeout(t); } }, [mSel, eSel]);

  const ChipRow = ({ items, onPick, tone }: any) => (
    <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
      {items.map((w: string) => (
        <Press key={w} onClick={() => onPick(w)} scale={0.95}>
          <div style={{ padding: "10px 17px", borderRadius: 999, ...pill(999) }}><span style={{ fontFamily: SANS, fontWeight: 700, fontSize: 14, color: INK }}>{w}</span></div>
        </Press>
      ))}
    </div>
  );

  return (
    <div>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <Label c={aA(accentDeep, 0.9)}>Check in</Label>
        <div style={{ display: "flex", alignItems: "center", gap: 5 }}><Flame s={13} c={accent} /><span style={{ fontFamily: SANS, fontWeight: 700, fontSize: 12, color: GRAY }}>12 days in a row</span></div>
      </div>
      <div style={{ fontFamily: SERIF, fontSize: 24, fontWeight: 500, color: INK, marginTop: 6, letterSpacing: -0.3 }}>{both ? "Thanks for checking in." : !mSel ? "How are you today?" : "And your energy?"}</div>

      {!mSel && (<div style={{ marginTop: 18, animation: "fadeIn .25s ease both" }}><ChipRow items={["calm", "tender", "sharp", "heavy", "wired"]} onPick={(w: string) => setMSel(w)} /></div>)}

      {mSel && !eSel && (<div style={{ marginTop: 18, animation: "fadeIn .25s ease both" }}>
        <div style={{ marginBottom: 10, display: "flex", alignItems: "center", gap: 8 }}>
          <div style={{ padding: "5px 12px", borderRadius: 999, background: `linear-gradient(180deg, ${accent}, ${accentDeep})` }}><span style={{ fontFamily: SANS, fontWeight: 700, fontSize: 13, color: "#FFF" }}>{mSel}</span></div>
          <Press scale={0.9} onClick={() => setMSel(null)}><span style={{ fontFamily: SANS, fontSize: 12, fontWeight: 700, color: GRAY }}>change</span></Press>
        </div>
        <ChipRow items={["low", "steady", "bright", "restless"]} onPick={(w: string) => setESel(w)} />
      </div>)}

      {both && (<div style={{ marginTop: 16, animation: "fadeIn .3s ease both" }}>
        <div style={{ display: "flex", gap: 7 }}>
          <div style={{ padding: "6px 14px", borderRadius: 999, background: `linear-gradient(180deg, ${accent}, ${accentDeep})` }}><span style={{ fontFamily: SANS, fontWeight: 700, fontSize: 13.5, color: "#FFF" }}>{mSel}</span></div>
          <div style={{ padding: "6px 14px", borderRadius: 999, background: aA(accent, 0.14), border: `1px solid ${aA(accentDeep, 0.3)}` }}><span style={{ fontFamily: SANS, fontWeight: 700, fontSize: 13.5, color: accentDeep }}>{eSel}</span></div>
        </div>
        <div style={{ marginTop: 13, padding: 15, borderRadius: 14, background: WASH }}><span style={{ fontFamily: SERIF, fontStyle: "italic", fontSize: 16, lineHeight: 1.45, color: INK2 } as any}>{reflection}</span></div>
        <div style={{ display: "flex", alignItems: "center", gap: 7, marginTop: 14, justifyContent: "center" }}><Flame s={15} c={glow} /><span style={{ fontFamily: SANS, fontSize: 13, fontWeight: 800, color: accentDeep }}>+1 diya lit</span></div>
      </div>)}

      {!both && (<Press scale={0.98} onClick={() => onClose(false)} style={{ marginTop: 20 }}>
        <div style={{ padding: "13px 0", borderRadius: 13, textAlign: "center", background: WASH, border: `1px solid ${HAIR}` }}><span style={{ fontFamily: SANS, fontSize: 14, fontWeight: 700, color: GRAY }}>Ask me later</span></div>
      </Press>)}
    </div>
  );
}

// slim reachable chip shown at the top of Read when the check-in was dismissed
function CheckInChip({ mood, delay, onOpen }: any) {
  const { accent, accentDeep, glow } = mood;
  return (
    <Press scale={0.98} onClick={onOpen} style={{ ...rise(delay), marginBottom: 14 }}>
      <div style={{ ...pill(999), padding: "11px 16px", display: "flex", alignItems: "center", gap: 11 }}>
        <div style={{ width: 30, height: 30, borderRadius: 999, flexShrink: 0, background: `linear-gradient(155deg, ${glow}, ${accentDeep})`, display: "flex", alignItems: "center", justifyContent: "center", boxShadow: `inset 0 1px 1px ${aA("#FFF", 0.5)}` }}><Flame s={14} c="#FFF" /></div>
        <span style={{ flex: 1, fontFamily: SANS, fontWeight: 800, fontSize: 14.5, color: INK }}>How are you today?</span>
        <Icon n="chevR" s={17} c={accentDeep} sw={1.9} />
      </div>
    </Press>
  );
}

// ===== SHOULD I, RIGHT NOW (inline verdict) =====
function ShouldICard({ mood, delay, onTalk }: any) {
  const { accent, accentDeep } = mood;
  const [q, setQ] = useState("");
  const [ans, setAns] = useState<any>(null);
  const verdicts = [
    { v: "Yes", line: "The timing is with you. Move while it feels this clear.", why: "The hour is clean and your ruling Moon is steady, a friendly window for action." },
    { v: "Wait", line: "It's a mixed moment. Let the better hour come to you, it will today.", why: "A rough angle is passing overhead. It clears soon, so there's no need to force it now." },
    { v: "Proceed gently", line: "You can move ahead, just gently and without forcing it.", why: "The day is soft, not sharp. Small steady steps land better than big ones right now." },
  ];
  const ask = () => setAns(verdicts[(q.trim().length || 1) % 3]);
  const vc = ans ? (ans.v === "Yes" ? "#2F8E66" : ans.v === "Wait" ? "#B5781A" : accentDeep) : accentDeep;
  return (
    <>
      <div style={{ marginBottom: 10, ...rise(delay) }}><Label>In the moment</Label></div>
      <div style={{ ...card({ padding: 18, marginBottom: 12 }), ...rise(delay + 20) }}>
        <span style={{ fontFamily: SERIF, fontSize: 19, fontWeight: 500, color: INK }}>Should I, right now?</span>
        <div style={{ fontFamily: SANS, fontSize: 13, color: GRAY, marginTop: 3 }}>a read on the timing of this moment</div>
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginTop: 13, padding: "4px 5px 4px 15px", borderRadius: 999, ...pill(999) }}>
          <input value={q} onChange={(e: any) => setQ(e.target.value)} onKeyDown={(e: any) => { if (e.key === "Enter") ask(); }} placeholder="Should I send this text?" style={{ flex: 1, border: "none", outline: "none", background: "transparent", fontFamily: SANS, fontSize: 14, color: INK, padding: "8px 0" }} />
          <Press scale={0.9} onClick={ask}><div style={{ background: INK, borderRadius: 999, width: 38, height: 38, display: "flex", alignItems: "center", justifyContent: "center" }}><Icon n="arrowR" s={16} c="#FFF" sw={2} /></div></Press>
        </div>
        {ans && (<div style={{ marginTop: 14, animation: "fadeIn .3s ease both" }}>
          <div style={{ fontFamily: SERIF, fontSize: 26, fontWeight: 500, color: vc, letterSpacing: -0.5 }}>{ans.v}.</div>
          <div style={{ fontFamily: SERIF, fontSize: 15.5, lineHeight: 1.45, color: INK2, marginTop: 6, textWrap: "pretty" } as any}>{ans.line}</div>
          <div style={{ fontFamily: SANS, fontSize: 12.5, lineHeight: 1.5, color: GRAY, marginTop: 8 }}>{ans.why}</div>
          <div style={{ fontFamily: SANS, fontSize: 11.5, color: GRAY, marginTop: 8, fontStyle: "italic" }}>This reads the timing of the moment, not the choice itself.</div>
          <Press scale={0.96} onClick={() => onTalk(q || "Should I, right now?")} style={{ display: "inline-block", marginTop: 13 }}><div style={{ display: "flex", alignItems: "center", gap: 7, padding: "9px 15px", borderRadius: 999, background: aA(accent, 0.12), border: `1px solid ${aA(accent, 0.28)}` }}><span style={{ fontFamily: SANS, fontSize: 13, fontWeight: 700, color: accentDeep }}>Talk it through</span><Icon n="arrowR" s={14} c={accentDeep} sw={1.9} /></div></Press>
        </div>)}
      </div>
    </>
  );
}

// ===== FOR TODAY pills: good times + ritual =====
function ForToday({ mood, delay, onTiming, onRitual }: any) {
  const { accent, accentDeep, glow } = mood;
  return (
    <>
      <div style={{ marginBottom: 10, ...rise(delay) }}><Label>For today</Label></div>
      <div style={{ display: "flex", flexDirection: "column", gap: 11, marginBottom: 24 }}>
        <Press scale={0.985} onClick={onTiming} style={rise(delay + 20)}>
          <div style={{ ...pill(18), padding: "13px 15px", display: "flex", alignItems: "center", gap: 13 }}>
            <GlossIcon c1={glow} c2={accentDeep}><Icon n="clock" s={19} c="#FFF" sw={1.8} /></GlossIcon>
            <div style={{ flex: 1 }}><div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 15.5, color: INK }}>good times today <span style={{ fontWeight: 600, color: GRAY }}>· best 11:40am</span></div><div style={{ fontFamily: SANS, fontSize: 12.5, color: GRAY, marginTop: 1 }}>strong window near midday, soft dip mid-morning</div></div>
            <Icon n="chevR" s={18} c={GRAY} />
          </div>
        </Press>
        <Press scale={0.985} onClick={onRitual} style={rise(delay + 60)}>
          <div style={{ ...pill(18), padding: "13px 15px", display: "flex", alignItems: "center", gap: 13 }}>
            <GlossIcon c1={"#F5B642"} c2={"#C77A1E"}><Flame s={19} c="#FFF" /></GlossIcon>
            <div style={{ flex: 1 }}><div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 15.5, color: INK }}>today's ritual <span style={{ fontWeight: 600, color: GRAY }}>· +2 🪔</span></div><div style={{ fontFamily: SANS, fontSize: 12.5, color: GRAY, marginTop: 1 }}>light a lamp at dusk, a good day for Saturn</div></div>
            <Icon n="chevR" s={18} c={GRAY} />
          </div>
        </Press>
      </div>
    </>
  );
}

// ===== THE DAY'S CLOCK — the signature live timing ribbon (sunrise → sunrise) =====
function fmtH(h: number) { const x = ((h % 24) + 24) % 24; let hr = Math.floor(x); const m = Math.round((x - hr) * 60); const ap = hr < 12 ? "am" : "pm"; let h12 = hr % 12; if (h12 === 0) h12 = 12; return `${h12}:${String(m).padStart(2, "0")}${ap}`; }
// quality → semantic fill (matches My Panchang dots: green good, amber hold, grey rest)
function qFill(q: string, mood: any) {
  if (q === "best") return `linear-gradient(180deg, #58C598, #2F8E66)`;
  if (q === "good") return "#8FCFB0";
  if (q === "hold") return "#E7B24E";
  if (q === "rest") return "#9BA0BC";
  return "#E3E1DC"; // neutral / ordinary
}
function DayClock({ mood, delay }: any) {
  const { accent, accentDeep, glow } = mood;
  const W = CLOCK.windows || [];
  const SR = CLOCK.sunrise || 6;             // ribbon spans SR .. SR+24
  const span = 24;
  const [now, setNow] = useState(() => { let h = nowH(); if (h < SR) h += 24; return h; });
  const [open, setOpen] = useState(false);
  const prevSeg = useRef(-1);
  useEffect(() => {
    const id = setInterval(() => { let h = nowH(); if (h < SR) h += 24; setNow(h); }, 15000);
    return () => clearInterval(id);
  }, []);
  const xOf = (t: number) => Math.max(0, Math.min(100, ((t - SR) / span) * 100));
  const cur = W.find((w: any) => now >= w.start && now < w.end) || W[0];
  const curIdx = W.indexOf(cur);
  // haptic tick when the marker crosses into a new window
  useEffect(() => { if (prevSeg.current !== -1 && prevSeg.current !== curIdx) { try { (navigator as any).vibrate && (navigator as any).vibrate(8); } catch (_) {} } prevSeg.current = curIdx; }, [curIdx]);

  const best = W.find((w: any) => w.q === "best");
  const avoid = W.find((w: any) => w.name === CLOCK.avoidName) || W.find((w: any) => w.q === "hold");
  // the live line
  let bold = "", soft = "";
  if (cur && (cur.q === "best" || cur.q === "good")) { bold = "Right now, a good window."; soft = `Clear sailing till ${fmtH(cur.end)}.`; }
  else if (cur && cur.q === "rest") { bold = "Winding down."; soft = "Rest easy. The day is done."; }
  else { const ng = W.find((w: any) => w.start > now && (w.q === "best" || w.q === "good")); if (ng) { const mins = Math.round((ng.start - now) * 60); bold = "Hold a bit."; soft = `A stronger window opens at ${fmtH(ng.start)} (in ${mins} min).`; } else { bold = "A quiet stretch."; soft = "Nothing pressing right now."; } }

  return (
    <>
      <div style={{ marginBottom: 10, ...rise(delay) }}><Label>The day's clock</Label></div>
      <div style={{ ...card({ padding: 18, marginBottom: 24 }), ...rise(delay + 20) }}>
        {/* live line */}
        <div style={{ display: "flex", alignItems: "flex-start", gap: 9 }}>
          <div style={{ width: 8, height: 8, borderRadius: 999, marginTop: 6, background: (cur && (cur.q === "best" || cur.q === "good")) ? "#2F8E66" : (cur && cur.q === "hold") ? ORANGE : GRAY, boxShadow: `0 0 0 4px ${aA((cur && (cur.q === "best" || cur.q === "good")) ? "#2F8E66" : (cur && cur.q === "hold") ? ORANGE : GRAY, 0.16)}`, animation: "glowPulse 2.6s ease-in-out infinite", ["--gc" as any]: aA(accent, 0.4) } as any} />
          <div style={{ flex: 1 }}>
            <span style={{ fontFamily: SERIF, fontSize: 18, fontWeight: 600, color: INK, letterSpacing: -0.2 }}>{bold} </span>
            <span style={{ fontFamily: SERIF, fontSize: 18, fontWeight: 400, color: INK2 }}>{soft}</span>
          </div>
        </div>

        {/* the ribbon */}
        <Press scale={0.995} onClick={() => setOpen((o) => !o)} style={{ marginTop: 16 }}>
          <div style={{ position: "relative", paddingTop: 14 }}>
            {/* segments */}
            <div style={{ display: "flex", gap: 2, height: 30, borderRadius: 9, overflow: "hidden" }}>
              {W.map((w: any, i: number) => (
                <div key={i} style={{ flex: (w.end - w.start), position: "relative", background: qFill(w.q, mood), animation: i === curIdx ? "glowPulse 2.4s ease-in-out infinite" : "none", ["--gc" as any]: aA(glow, 0.6) } as any}>
                  {w.q === "best" && <div style={{ position: "absolute", inset: 0, animation: "sheen 4s linear infinite", background: `linear-gradient(105deg, transparent 35%, ${aA("#FFF", 0.5)} 50%, transparent 65%)`, backgroundSize: "260% 100%" }} />}
                </div>
              ))}
            </div>
            {/* you-are-here marker */}
            <div style={{ position: "absolute", top: 8, bottom: 0, left: `${xOf(now)}%`, width: 2, marginLeft: -1, background: INK, borderRadius: 2, transition: "left 1s linear" }}>
              <div style={{ position: "absolute", top: -7, left: "50%", marginLeft: -5, width: 10, height: 10, borderRadius: 999, background: INK, border: "2px solid #FFF", boxShadow: `0 0 0 3px ${aA(INK, 0.12)}` }} />
            </div>
            {/* sunrise / noon / sunrise ticks */}
            <div style={{ display: "flex", justifyContent: "space-between", marginTop: 7 }}>
              <span style={{ fontFamily: MONO, fontSize: 9, color: GRAY }}>{fmtH(SR)}</span>
              <span style={{ fontFamily: MONO, fontSize: 9, color: GRAY }}>noon</span>
              <span style={{ fontFamily: MONO, fontSize: 9, color: GRAY }}>{fmtH(SR + 12)}</span>
              <span style={{ fontFamily: MONO, fontSize: 9, color: GRAY }}>dawn</span>
            </div>
          </div>
        </Press>

        {/* best + avoid summary */}
        <div style={{ display: "flex", gap: 10, marginTop: 14 }}>
          {best && (<div style={{ flex: 1, padding: "10px 12px", borderRadius: 13, background: aA(accent, 0.08), border: `1px solid ${aA(accent, 0.2)}` }}>
            <div style={{ display: "flex", alignItems: "center", gap: 6 }}><div style={{ width: 6, height: 6, borderRadius: 999, background: accent }} /><span style={{ fontFamily: SANS, fontWeight: 800, fontSize: 12.5, color: INK }}>{best.name}</span></div>
            <div style={{ fontFamily: SANS, fontSize: 12, color: INK2, marginTop: 3 }}>{fmtH(best.start)}–{fmtH(best.end)}</div>
            <div style={{ fontFamily: SANS, fontSize: 11, color: GRAY, marginTop: 2 }}>{best.tip}</div>
          </div>)}
          {avoid && (<div style={{ flex: 1, padding: "10px 12px", borderRadius: 13, background: WASH, border: `1px solid ${HAIR}` }}>
            <div style={{ display: "flex", alignItems: "center", gap: 6 }}><div style={{ width: 6, height: 6, borderRadius: 999, background: GRAY }} /><span style={{ fontFamily: SANS, fontWeight: 800, fontSize: 12.5, color: INK }}>{avoid.name}</span></div>
            <div style={{ fontFamily: SANS, fontSize: 12, color: INK2, marginTop: 3 }}>{fmtH(avoid.start)}–{fmtH(avoid.end)}</div>
            <div style={{ fontFamily: SANS, fontSize: 11, color: GRAY, marginTop: 2 }}>{avoid.tip}</div>
          </div>)}
        </div>

        {/* expand: full window list */}
        {open && (<div style={{ marginTop: 14, paddingTop: 14, borderTop: `1px solid ${HAIR}`, display: "flex", flexDirection: "column", gap: 11, animation: "fadeIn .3s ease both" }}>
          {W.map((w: any, i: number) => (
            <div key={i} style={{ display: "flex", alignItems: "center", gap: 11 }}>
              <div style={{ width: 10, height: 10, borderRadius: 3, flexShrink: 0, background: qFill(w.q, mood) }} />
              <div style={{ width: 96, flexShrink: 0, fontFamily: SANS, fontWeight: 700, fontSize: 13, color: INK }}>{w.name}</div>
              <div style={{ width: 96, flexShrink: 0, fontFamily: MONO, fontSize: 11, color: GRAY }}>{fmtH(w.start)}</div>
              <div style={{ flex: 1, fontFamily: SANS, fontSize: 12, color: INK2, textAlign: "right" }}>{w.tip}</div>
            </div>
          ))}
        </div>)}
        <div style={{ textAlign: "center", marginTop: 12 }}><span style={{ fontFamily: SANS, fontSize: 11.5, fontWeight: 700, color: GRAY }}>{open ? "tap to close" : "tap for the full day"}</span></div>
      </div>
    </>
  );
}

// ===== IN FOCUS chip (conditional) =====
function InFocusChip({ mood, delay, onGo }: any) {
  const { accent, accentDeep, glow } = mood;
  if (!FOCUS) return null;
  return (
    <Press scale={0.98} onClick={() => onGo(FOCUS.to)} style={{ ...rise(delay), marginBottom: 24 }}>
      <div style={{ ...pill(999), padding: "11px 16px", display: "flex", alignItems: "center", gap: 11 }}>
        <GlossIcon c1={glow} c2={accentDeep} size={30} radius={9}><Icon n="target" s={16} c="#FFF" sw={1.8} /></GlossIcon>
        <span style={{ flex: 1, fontFamily: SANS, fontWeight: 800, fontSize: 14.5, color: INK }}>{FOCUS.line}</span>
        <Icon n="arrowR" s={17} c={accentDeep} sw={1.9} />
      </div>
    </Press>
  );
}

// ===== RITUAL (slim nudge → deep-links to Rituals tab) =====
function RitualPill({ mood, delay, onBegin }: any) {
  return (
    <>
      <div style={{ marginBottom: 10, ...rise(delay) }}><Label>Today's ritual</Label></div>
      <Press scale={0.985} onClick={onBegin} style={{ ...rise(delay + 20), marginBottom: 24 }}>
        <div style={{ ...pill(18), padding: "13px 15px", display: "flex", alignItems: "center", gap: 13 }}>
          <GlossIcon c1={"#F5B642"} c2={"#C77A1E"}><Flame s={19} c="#FFF" /></GlossIcon>
          <div style={{ flex: 1 }}><div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 15.5, color: INK }}>light a lamp at dusk <span style={{ fontWeight: 600, color: GRAY }}>· +2 🪔</span></div><div style={{ fontFamily: SANS, fontSize: 12.5, color: GRAY, marginTop: 1 }}>breathe slowly for one minute, a good day for Saturn</div></div>
          <div style={{ display: "flex", alignItems: "center", gap: 5 }}><span style={{ fontFamily: SANS, fontSize: 13, fontWeight: 700, color: mood.accentDeep }}>Begin</span><Icon n="arrowR" s={14} c={mood.accentDeep} sw={2} /></div>
        </div>
      </Press>
    </>
  );
}

// ===== TODAY AT A GLANCE — collapsible almanac =====
function TodayGlance({ mood, delay }: any) {
  const { accent, accentDeep, glow } = mood;
  const [open, setOpen] = useState(false);
  const A = ALMANAC;
  const rows = [
    { ic: "moonp", c1: "#9FB0E0", c2: "#5566A8", k: `Moon in ${A.nakshatra}`, v: A.nakFlavor },
    { ic: "cal", c1: "#C9A6E8", c2: "#7E54A0", k: A.tithi, v: A.tithiNote },
    A.special ? { ic: "spark", c1: glow, c2: accentDeep, k: A.special, v: A.specialNote } : null,
    A.festival ? { ic: "leaf", c1: "#9FD8A8", c2: "#3E9C7A", k: A.festival, v: "a festival day" } : null,
    { ic: "clock", c1: "#F3C36B", c2: "#C77A1E", k: "Your strongest 90", v: A.best90 },
  ].filter(Boolean) as any[];
  return (
    <div style={{ ...card({ padding: 16, marginBottom: 24 }), ...rise(delay) }}>
      <Press scale={0.99} onClick={() => setOpen((o) => !o)}>
        <div style={{ display: "flex", alignItems: "center", gap: 11 }}>
          <GlossIcon c1={"#9FB0E0"} c2={"#5566A8"} size={36} radius={11}><Icon n="moonp" s={18} c="#FFF" sw={1.8} /></GlossIcon>
          <div style={{ flex: 1 }}>
            <Label>Today at a glance</Label>
            <div style={{ fontFamily: SERIF, fontSize: 16, color: INK, marginTop: 2 }}>Moon in {ALMANAC.nakshatra}, {ALMANAC.nakFlavor}</div>
          </div>
          <div style={{ transform: open ? "rotate(180deg)" : "none", transition: "transform .25s" }}><Icon n="chevD" s={18} c={GRAY} /></div>
        </div>
      </Press>
      {open && (<div style={{ marginTop: 14, paddingTop: 14, borderTop: `1px solid ${HAIR}`, display: "flex", flexDirection: "column", gap: 13, animation: "fadeIn .3s ease both" }}>
        {rows.map((r, i) => (
          <div key={i} style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <GlossIcon c1={r.c1} c2={r.c2} size={32} radius={10}><Icon n={r.ic} s={16} c="#FFF" sw={1.8} /></GlossIcon>
            <div style={{ flex: 1 }}><div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 14, color: INK }}>{r.k}</div><div style={{ fontFamily: SANS, fontSize: 12.5, color: GRAY, marginTop: 1 }}>{r.v}</div></div>
          </div>
        ))}
        <div style={{ fontFamily: SANS, fontSize: 11.5, color: GRAY, fontStyle: "italic", marginTop: 2 }}>light to read, nice to share</div>
      </div>)}
    </div>
  );
}

// ===== TODAY ACROSS YOUR LIFE — Love · Work · Money (three slim rows, no scores) =====
function LifeAreas({ mood, delay, onArea }: any) {
  const { accent, accentDeep, glow } = mood;
  const la = (LIFE_AREAS as any)[mood.key] || {};
  const rows = [
    { k: "Love", v: la.love, c1: "#E48AA6", c2: "#C55C7E" },
    { k: "Work", v: la.work, c1: "#6E86C4", c2: "#4C63A0" },
    { k: "Money", v: la.money, c1: "#5FA97E", c2: "#3E8060" },
  ];
  return (
    <>
      <div style={{ marginBottom: 10, ...rise(delay) }}><Label>Today across your life</Label></div>
      <div style={{ ...card({ padding: 6 }), ...rise(delay + 20), marginBottom: 24 }}>
        {rows.map((r, i) => (
          <Press key={r.k} scale={0.985} onClick={() => onArea(r.k)}>
            <div style={{ display: "flex", alignItems: "center", gap: 13, padding: "12px 12px", borderTop: i ? `1px solid ${HAIR}` : "none" }}>
              <GlossIcon c1={r.c1} c2={r.c2} size={34} radius={11}><Icon n={r.k === "Love" ? "heart" : r.k === "Work" ? "work" : "coin"} s={16} c="#FFF" sw={1.9} /></GlossIcon>
              <div style={{ width: 46, flexShrink: 0 }}><span style={{ fontFamily: SANS, fontSize: 13.5, fontWeight: 800, color: INK }}>{r.k}</span></div>
              <div style={{ flex: 1, minWidth: 0 }}><span style={{ fontFamily: SERIF, fontSize: 14.5, lineHeight: 1.38, color: INK2, textWrap: "pretty" } as any}>{r.v}</span></div>
              <Icon n="chevR" s={15} c={GRAY} />
            </div>
          </Press>
        ))}
      </div>
    </>
  );
}

// ===== JOURNAL (the Mirror) — a pretty, cozy invitation; no controls on its face =====
function JournalCard({ mood, delay, written, onOpen }: any) {
  const { accent, accentDeep, glow } = mood;
  const invite = useRef((MIR.invites || ["What's on your mind?"])[0]).current;
  return (
    <Press scale={0.99} onClick={onOpen} style={{ ...rise(delay), marginBottom: 24 }}>
      <div style={{ ...card({ padding: 22, background: `linear-gradient(158deg, #FFFDFB 0%, ${aA(glow, 0.12)} 100%)` }), position: "relative", overflow: "hidden" }}>
        {/* cozy ambient glow, low-right — a warm little pocket of night sky */}
        <div style={{ position: "absolute", right: -26, bottom: -30, width: 160, height: 160, borderRadius: 999, background: `radial-gradient(circle, ${aA(glow, 0.3)}, ${aA(glow, 0)} 70%)`, pointerEvents: "none" }} />
        {/* an open journal + ribbon bookmark — the cozy diary this card is */}
        <div style={{ position: "absolute", right: 16, bottom: 16, pointerEvents: "none" }}>
          <div style={{ position: "relative", width: 56, height: 56, animation: "floatY 6s ease-in-out infinite" }}>
            <div style={{ position: "absolute", inset: -12, borderRadius: 999, background: `radial-gradient(circle, ${aA(glow, 0.5)}, ${aA(glow, 0)} 70%)` }} />
            <svg width="56" height="56" viewBox="0 0 28 28" fill="none" style={{ position: "relative" }}>
              <defs><linearGradient id="mirBook" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stopColor="#FFFDF8" /><stop offset="1" stopColor={aA(glow, 0.55)} /></linearGradient></defs>
              <path d="M14 8.5 C11 6.8 8 6.8 5 7.6 L5 20.2 C8 19.4 11 19.4 14 21 Z" fill="url(#mirBook)" stroke={accentDeep} strokeWidth="0.9" strokeLinejoin="round" />
              <path d="M14 8.5 C17 6.8 20 6.8 23 7.6 L23 20.2 C20 19.4 17 19.4 14 21 Z" fill="url(#mirBook)" stroke={accentDeep} strokeWidth="0.9" strokeLinejoin="round" />
              <path d="M14 8.5 L14 21" stroke={accentDeep} strokeWidth="0.9" strokeLinecap="round" />
              <g stroke={aA(accentDeep, 0.5)} strokeWidth="0.7" strokeLinecap="round">
                <path d="M7 10.6 L11.4 9.9" /><path d="M7 12.8 L11.4 12.1" /><path d="M7 15 L10.8 14.4" />
                <path d="M16.6 9.9 L21 10.6" /><path d="M16.6 12.1 L21 12.8" />
              </g>
              <path d="M18.4 7 L18.4 15 L19.9 13.4 L21.4 15 L21.4 7 Z" fill={accent} stroke={aA("#FFF", 0.6)} strokeWidth="0.4" />
            </svg>
            <div style={{ position: "absolute", left: -6, top: 2, width: 3, height: 3, borderRadius: 999, background: accentDeep, opacity: 0.5, boxShadow: `0 0 5px ${aA(accentDeep, 0.5)}` }} />
          </div>
        </div>
        <div style={{ position: "relative" }}>
          <Label c={aA(accentDeep, 0.9)}>The Mirror</Label>
          {!written
            ? (<>
                <div style={{ fontFamily: SERIF, fontSize: 24, fontWeight: 500, color: INK, marginTop: 9, letterSpacing: -0.3, maxWidth: 210, lineHeight: 1.2 }}>{invite}</div>
                <div style={{ fontFamily: SERIF, fontStyle: "italic", fontSize: 14.5, color: aA(accentDeep, 0.85), marginTop: 9 }}>set it down here, just for you</div>
                {/* faint ruled lines — a cozy page waiting */}
                <div style={{ marginTop: 16, display: "flex", flexDirection: "column", gap: 9, maxWidth: 200 }}>
                  <div style={{ height: 1.5, borderRadius: 2, background: aA(accentDeep, 0.14), width: "82%" }} />
                  <div style={{ height: 1.5, borderRadius: 2, background: aA(accentDeep, 0.1), width: "58%" }} />
                </div>
              </>)
            : (<>
                <div style={{ fontFamily: SERIF, fontStyle: "italic", fontSize: 19, color: INK, marginTop: 9, maxWidth: 220, lineHeight: 1.35 }}>You wrote today. I'm holding it for you.</div>
                <div style={{ display: "inline-flex", alignItems: "center", gap: 5, marginTop: 12, fontFamily: SANS, fontSize: 12.5, fontWeight: 700, color: accentDeep }}>add a little more<Icon n="chevR" s={13} c={accentDeep} /></div>
              </>)}
        </div>
      </div>
    </Press>
  );
}

// ===== LOOKING AHEAD =====
function LookingAhead({ mood, delay, onWeek }: any) {
  const { accent, accentDeep, glow } = mood;
  const [sel, setSel] = useState<number | null>(null);
  const sc = (s: string) => s === "good" ? "#3E9C7A" : s === "difficult" ? ORANGE : GRAY;
  const cur = sel != null ? AHEAD[sel] : null;
  return (
    <>
      <div style={{ marginBottom: 10, ...rise(delay) }}><Label>Looking ahead</Label></div>
      <div style={{ display: "flex", gap: 10, ...rise(delay + 20) }}>
        {AHEAD.slice(0, 4).map((d: any, i: number) => { const dm = MOOD[d.mood] || mood; const on = sel === i; return (
          <Press key={i} scale={0.95} onClick={() => setSel(on ? null : i)} style={{ flex: 1 }}><div style={{ ...pill(16), padding: "12px 4px", textAlign: "center", border: `1px solid ${on ? aA(accentDeep, 0.3) : aA("#000", 0.05)}` }}><span style={{ fontFamily: MONO, fontSize: 9, fontWeight: 600, letterSpacing: 1, color: GRAY }}>{d.day}</span><div style={{ fontFamily: SERIF, fontSize: 19, fontWeight: 500, color: INK, margin: "2px 0 7px" }}>{d.date}</div><div style={{ width: 26, height: 26, margin: "0 auto", borderRadius: 8, background: `linear-gradient(155deg, ${dm.glow}, ${dm.accentDeep})`, boxShadow: `inset 0 1px 1px ${aA("#FFF", 0.5)}` }} /><div style={{ width: 5, height: 5, borderRadius: 999, background: sc(d.status), margin: "8px auto 0" }} /></div></Press>
        ); })}
      </div>
      {cur && (<div style={{ marginTop: 12, padding: 14, borderRadius: 16, background: WASH, animation: "fadeIn .3s ease both" }}>
        <span style={{ fontFamily: SERIF, fontSize: 17, fontWeight: 500, color: INK }}>{cur.mood}</span>
        <span style={{ fontFamily: SANS, fontSize: 13, color: GRAY }}>  ·  {(DAY_LINE as any)[cur.mood] || ""}</span>
        <div style={{ fontFamily: SANS, fontSize: 12.5, color: GRAY, marginTop: 4 }}>good {cur.good} · ease off {cur.avoid}</div>
      </div>)}
      <Press scale={0.98} onClick={onWeek} style={{ display: "inline-block", marginTop: 12 }}><span style={{ fontFamily: SANS, fontSize: 12.5, fontWeight: 700, color: accentDeep }}>see your full week on the Timeline →</span></Press>
    </>
  );
}

// ===== BOTTOM NAV — Today · Timeline · [Readings, elevated center] · People · Rituals =====
function BottomNav({ mood, active, onTab }: any) {
  const { accent, accentDeep, glow } = mood;
  const Side = ({ label, ic }: any) => { const on = active === label; return (
    <div onClick={() => onTab(label)} style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", gap: 5, cursor: "pointer", paddingTop: 4 }}>
      <Icon n={ic} s={22} c={on ? INK : GRAY} sw={on ? 2 : 1.7} />
      <span style={{ fontFamily: SANS, fontSize: 10, fontWeight: on ? 800 : 600, color: on ? INK : GRAY }}>{label}</span>
    </div>
  ); };
  const onR = active === "Readings";
  return (
    <div style={{ position: "absolute", bottom: 0, left: 0, right: 0, background: aA("#FFFFFF", 0.92), backdropFilter: "blur(16px)", WebkitBackdropFilter: "blur(16px)", borderTop: `1px solid ${HAIR}`, padding: "10px 8px 18px", display: "flex", alignItems: "flex-start", zIndex: 40 }}>
      <Side label="Today" ic="today" />
      <Side label="Timeline" ic="timeline" />
      {/* elevated glossy center — the Decode/Readings hub, the heart of the app */}
      <div onClick={() => onTab("Readings")} style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", cursor: "pointer" }}>
        <Press scale={0.92}>
          <div style={{ width: 56, height: 56, borderRadius: 999, marginTop: -26, position: "relative", overflow: "hidden", background: `linear-gradient(155deg, ${glow}, ${accent} 54%, ${accentDeep})`, border: "3px solid #FFF", boxShadow: `0 10px 22px -6px ${aA(accentDeep, 0.6)}, inset 0 1px 2px ${aA("#FFF", 0.55)}`, display: "flex", alignItems: "center", justifyContent: "center" }}>
            <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: "46%", background: `linear-gradient(180deg, ${aA("#FFF", 0.42)}, ${aA("#FFF", 0)})` }} />
            <Icon n="readings" s={23} c="#FFF" sw={1.9} />
          </div>
        </Press>
        <span style={{ fontFamily: SANS, fontSize: 10, fontWeight: onR ? 800 : 600, color: onR ? INK : GRAY, marginTop: 5 }}>Readings</span>
      </div>
      <Side label="People" ic="people" />
      <Side label="Rituals" ic="rituals" />
    </div>
  );
}

(window as any).__astroToday = { TopCluster, LivingSkyHeader, MoonFAB, SubTabs, EclipseCard, ReadingCard, LifeAreas, GoodBadStrip, DayClock, CheckInSheet, CheckInChip, ShouldICard, ForToday, RitualPill, InFocusChip, TodayGlance, JournalCard, LookingAhead, BottomNav, nowH, fmtH, qFill };
})();
