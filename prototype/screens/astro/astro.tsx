// astro.tsx — ASTROLO shared design system, "ASTROLO-clean white" language.
// Clean WHITE, airy, premium. Soft gradient pills with glossy colorful icon tiles,
// solid-black CTAs, serif + sans type mix, gray tracked labels, soft shadows, generous
// whitespace. Mood only tints small accents + glossy emblems; the app stays white.
// This file exports the atoms; astro-today.tsx + astro-screens.tsx build the screens.
//
// PORT: div->View, span->Text, onClick->onPress, gradients/shadows -> RN equivalents,
// CSS keyframes -> reanimated loops. State-driven; no render-loop deps.
;(function () {
const { useState, useRef, useEffect, useMemo } = React;

function aA(hex: string, al: number) { const h = (hex || "#000").replace("#", ""); const n = parseInt(h.length === 3 ? h.split("").map((c) => c + c).join("") : h, 16); return `rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},${al})`; }

// ---- palette: ASTROLO-clean white ----
const PAPER = "#FFFFFF", WASH = "#F4F4F6", INK = "#0C0B0A", INK2 = "#3A3733", GRAY = "#9A958C", HAIR = "rgba(12,11,10,0.07)", ORANGE = "#DF6B35";
const SANS = "'Hanken Grotesk', sans-serif", SERIF = "'Newsreader', serif", MONO = "'Spline Sans Mono', monospace";

// soft ASTROLO pill surface (light gradient + layered soft shadow + top highlight)
const pill = (r = 999, extra: any = {}) => ({
  background: `linear-gradient(180deg, #FFFFFF 0%, #F1F1F3 100%)`,
  borderRadius: r, border: `1px solid ${aA("#000", 0.05)}`,
  boxShadow: `inset 0 1px 0 #FFFFFF, 0 1px 2px ${aA("#1A1408", 0.04)}, 0 6px 16px -8px ${aA("#1A1408", 0.14)}`,
  ...extra,
});
// soft white card
const card = (extra: any = {}) => ({ background: PAPER, borderRadius: 22, border: `1px solid ${HAIR}`, boxShadow: `0 1px 2px ${aA("#1A1408", 0.03)}, 0 14px 30px -18px ${aA("#1A1408", 0.16)}`, ...extra });
const Label = ({ children, c = GRAY }: any) => (<span style={{ fontFamily: SANS, fontSize: 11.5, fontWeight: 700, letterSpacing: 1.6, textTransform: "uppercase", color: c }}>{children}</span>);

// Ionicons-shaped glyph set
const PATHS: any = {
  bell: ["M6 9a6 6 0 0 1 12 0c0 5 1.5 6 2 7H4c.5-1 2-2 2-7Z", "M9.5 20a2.5 2.5 0 0 0 5 0"],
  share: ["M12 14V4", "M8.5 7.5 12 4l3.5 3.5", "M6 11v7a1 1 0 0 0 1 1h10a1 1 0 0 0 1-1v-7"],
  chevR: ["M9.5 6 15 12l-5.5 6"],
  chevD: ["M6 9.5 12 15l6-5.5"],
  chevU: ["M6 14.5 12 9l6 5.5"],
  plus: ["M12 5v14", "M5 12h14"],
  sync: ["M4 11a8 8 0 0 1 13.5-4.5L20 9", "M20 4v5h-5", "M20 13a8 8 0 0 1-13.5 4.5L4 15", "M4 20v-5h5"],
  capsule: ["M8 3h8a2 2 0 0 1 2 2v6l-6 10-6-10V5a2 2 0 0 1 2-2Z", "M6 9h12"],
  compass: ["M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18Z", "M15.5 8.5l-2 5-5 2 2-5 5-2Z"],
  wand: ["M5 19 16 8", "M17 4l1.2 2.8L21 8l-2.8 1.2L17 12l-1.2-2.8L13 8l2.8-1.2L17 4Z", "M6 14l1 1"],
  scan: ["M4 8V5a1 1 0 0 1 1-1h3", "M16 4h3a1 1 0 0 1 1 1v3", "M20 16v3a1 1 0 0 1-1 1h-3", "M8 20H5a1 1 0 0 1-1-1v-3", "M8 12h8"],
  arrowR: ["M4 12h15", "M14 7l5 5-5 5"],
  arrowL: ["M19 12H4", "M10 7l-5 5 5 5"],
  close: ["M6 6l12 12", "M18 6 6 18"],
  check: ["M5 12.5 9.5 17 19 7"],
  mic: ["M12 3a2.6 2.6 0 0 0-2.6 2.6v5.2a2.6 2.6 0 0 0 5.2 0V5.6A2.6 2.6 0 0 0 12 3Z", "M6 11a6 6 0 0 0 12 0", "M12 17v3.5"],
  send: ["M4 12 20 4l-6 16-3-7-7-1Z"],
  trash: ["M4 7h16", "M9 7V5a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2", "M6 7l1 13a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1l1-13", "M10 11v6", "M14 11v6"],
  pause: ["M9 5v14", "M15 5v14"],
  clock: ["M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18Z", "M12 7v5l3 2"],
  today: ["M3 11l9-7 9 7v8a1 1 0 0 1-1 1h-5v-6h-6v6H4a1 1 0 0 1-1-1z"],
  timeline: ["M5 5h14", "M5 12h14", "M5 19h9"],
  people: ["M9 11a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z", "M3 20c0-3 2.7-5 6-5s6 2 6 5", "M17 11a2.6 2.6 0 1 0 0-5.2", "M16.5 15c2.6 0 4.5 1.8 4.5 4.5"],
  rituals: ["M12 3c3.5 3.8 5 6 5 9a5 5 0 0 1-10 0c0-2 1-3 2.4-4.2"],
  readings: ["M3 3h18v18H3z", "M12 3 21 12 12 21 3 12Z", "M3 3 21 21", "M21 3 3 21"],
  heart: ["M12 20s-7-4.6-9.2-9C1.3 7.8 3 5 6 5c2 0 3 1.3 3.6 2.3C10.2 6.3 11.2 5 13.2 5"],
  work: ["M4 8h16v11a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1z", "M9 8V6a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2"],
  coin: ["M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18Z", "M12 7v10", "M9.5 9.5h4a1.6 1.6 0 0 1 0 3.2h-3a1.6 1.6 0 0 0 0 3.2h4"],
  spark: ["M12 3v18", "M3 12h18", "M6 6l12 12", "M18 6 6 18"],
  user: ["M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8Z", "M5 20a7 7 0 0 1 14 0"],
  ring: ["M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18Z"],
  sun: ["M12 5a7 7 0 1 0 0 14 7 7 0 0 0 0-14Z", "M12 1v2", "M12 21v2", "M4.2 4.2l1.4 1.4", "M18.4 18.4l1.4 1.4", "M1 12h2", "M21 12h2", "M4.2 19.8l1.4-1.4", "M18.4 5.6l1.4-1.4"],
  moonp: ["M20 14.5A8 8 0 0 1 9.5 4 7 7 0 1 0 20 14.5Z"],
  leaf: ["M5 19c0-8 6-13 14-13 0 8-5 14-14 13Z", "M5 19c3-4 6-6 9-7"],
  target: ["M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18Z", "M12 16a4 4 0 1 0 0-8 4 4 0 0 0 0 8Z", "M12 12h.01"],
  cal: ["M4 6a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v13a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1z", "M4 9h16", "M8 3v4", "M16 3v4"],
};
const Icon = ({ d, n, s = 20, c = INK, sw = 1.7 }: any) => { const paths = n ? (PATHS[n] || []) : (Array.isArray(d) ? d : [d]); return (<svg width={s} height={s} viewBox="0 0 24 24" fill="none">{paths.map((p: string, i: number) => <path key={i} d={p} stroke={c} strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round" />)}</svg>); };
const I = Icon;
const Flame = ({ s = 14, c = "#fff" }: any) => (<svg width={s} height={s * 1.15} viewBox="0 0 24 28"><path d="M12 2c4.4 5 6.6 8 6.6 12.2A6.6 6.6 0 0 1 5.4 14.2C5.4 11.4 7 9.6 9 8.2 10 9.6 10.8 10 12 8.6c.6-1.6.4-3.8 0-6.6Z" fill={c} /></svg>);

// little glossy icon tile (ASTROLO's colorful rounded-square app icons)
function GlossIcon({ c1, c2, size = 36, radius = 11, children }: any) {
  return (
    <div style={{ width: size, height: size, borderRadius: radius, flexShrink: 0, position: "relative", overflow: "hidden",
      background: `linear-gradient(160deg, ${c1}, ${c2})`, boxShadow: `inset 0 1px 1px ${aA("#FFF", 0.6)}, 0 3px 8px -3px ${aA(c2, 0.7)}`, display: "flex", alignItems: "center", justifyContent: "center" }}>
      <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: "45%", background: `linear-gradient(180deg, ${aA("#FFF", 0.4)}, ${aA("#FFF", 0)})` }} />
      {children}
    </div>
  );
}

// press wrapper (subtle scale)
function Press({ children, onClick, scale = 0.97, style = {} }: any) {
  const [d, setD] = useState(false);
  return (<div onClick={onClick} onPointerDown={() => setD(true)} onPointerUp={() => setD(false)} onPointerLeave={() => setD(false)} style={{ transform: d ? `scale(${scale})` : "none", transition: "transform .12s ease", cursor: "pointer", ...style }}>{children}</div>);
}

// 12 per-mood celestial sigils — a unique line-mark for each day's character, drawn white
// on the glossy tile. Relevant to the mood's feeling. PORT: plain SVG, no deps.
function MoodSigil({ k }: any) {
  const S = "#FFFDF8";
  const g = (children: any) => (<g stroke={S} strokeWidth="1.3" fill="none" strokeLinecap="round" strokeLinejoin="round">{children}</g>);
  switch (k) {
    case "Settled": return g(<>
      <path d="M5.5 12.5 L12 7 L18.5 12.5" /><path d="M7.4 11.4 V17.5 H16.6 V11.4" />
      <circle cx="12" cy="3.9" r="1" fill={S} stroke="none" />
    </>);
    case "Guarded": return (<g>
      <path d="M15.8 5.2 A7 7 0 1 0 17 15.7 A5.3 5.3 0 1 1 15.8 5.2 Z" fill={S} opacity="0.92" />
      <path d="M4 14.4 H13.5" stroke={S} strokeWidth="1.3" strokeLinecap="round" /><path d="M6 17.4 H15.5" stroke={S} strokeWidth="1.3" strokeLinecap="round" opacity="0.6" />
    </g>);
    case "Bold": return g(<>
      <path d="M8 15.2 Q12 3.8 16 15.2" /><path d="M10 15.2 Q12 9 14 15.2" /><path d="M6.4 17.6 H17.6" />
    </>);
    case "Tender": return g(<>
      <path d="M12 4 C12 4 6.6 11 6.6 14.6 A5.4 5.4 0 0 0 17.4 14.6 C17.4 11 12 4 12 4 Z" />
      <path d="M9.5 14.7 A2.6 2.6 0 0 0 12 17.1" opacity="0.65" />
    </>);
    case "Restless": return (<g>
      <circle cx="15.2" cy="8.8" r="2.6" fill={S} />
      <path d="M13 10.8 L5 18" stroke={S} strokeWidth="1.3" strokeLinecap="round" />
      <path d="M15.6 12 L9.6 18" stroke={S} strokeWidth="1.3" strokeLinecap="round" opacity="0.6" />
      <path d="M11 9.8 L6.2 14.4" stroke={S} strokeWidth="1.3" strokeLinecap="round" opacity="0.45" />
    </g>);
    case "Capable": return g(<>
      <path d="M4 17.4 L9.4 9 L13 14 L16 10 L20 17.4 Z" /><circle cx="16.4" cy="5.4" r="1" fill={S} stroke="none" />
    </>);
    case "Warm": return g(<>
      <circle cx="12" cy="12" r="3.5" />
      <path d="M12 3.6 V6 M12 18 V20.4 M3.6 12 H6 M18 12 H20.4 M6.2 6.2 L7.8 7.8 M16.2 16.2 L17.8 17.8 M17.8 6.2 L16.2 7.8 M7.8 16.2 L6.2 17.8" />
    </>);
    case "Deep": return (<g fill="none" stroke={S} strokeWidth="1.3">
      <circle cx="12" cy="12" r="8" opacity="0.3" /><circle cx="12" cy="12" r="5.2" opacity="0.55" /><circle cx="12" cy="12" r="2.6" opacity="0.85" /><circle cx="12" cy="12" r="1.2" fill={S} stroke="none" />
    </g>);
    case "Wandering": return (<g>
      <path d="M4.5 16 C7.5 16 7.5 8 10.5 8 C13.5 8 13.5 16 16.5 16 C18.5 16 18.5 12.5 19.4 12.2" stroke={S} strokeWidth="1.3" fill="none" strokeLinecap="round" />
      <circle cx="19.4" cy="12.1" r="1" fill={S} stroke="none" />
    </g>);
    case "Driven": return g(<>
      <path d="M12 18 V7" /><path d="M7.6 11.4 L12 6.4 L16.4 11.4" /><circle cx="12" cy="4" r="0.9" fill={S} stroke="none" />
    </>);
    case "Upbeat": return g(<>
      <path d="M12 5 C12.6 9.5 14.5 11.4 19 12 C14.5 12.6 12.6 14.5 12 19 C11.4 14.5 9.5 12.6 5 12 C9.5 11.4 11.4 9.5 12 5 Z" />
      <circle cx="18.4" cy="6" r="0.8" fill={S} stroke="none" /><circle cx="6" cy="17.6" r="0.7" fill={S} stroke="none" opacity="0.7" />
    </>);
    case "Quiet": return (<g>
      <path d="M14.5 5 A7.4 7.4 0 1 0 14.5 19 A9.2 9.2 0 0 1 14.5 5 Z" fill={S} />
      <circle cx="7" cy="7" r="0.8" fill={S} />
    </g>);
    default: return g(<><path d="M6 15 L12 8 L18 14" /><circle cx="12" cy="8" r="1.6" fill={S} stroke="none" /></>);
  }
}

// glossy celestial emblem — a rounded-square mood tile carrying the day's sigil, float + sheen.
function MoodEmblem({ mood, size = 60, radius = 18 }: any) {
  const { accent, accentDeep, glow } = mood;
  return (
    <div style={{ width: size, height: size, position: "relative", animation: "floatY 5s ease-in-out infinite" }}>
      <div style={{ position: "absolute", inset: -6, borderRadius: radius + 4, background: `radial-gradient(circle, ${aA(glow, 0.4)}, ${aA(glow, 0)} 70%)` }} />
      <div style={{ width: size, height: size, borderRadius: radius, position: "relative", overflow: "hidden", background: `linear-gradient(155deg, ${glow}, ${accent} 55%, ${accentDeep})`, boxShadow: `inset 0 1px 2px ${aA("#FFF", 0.5)}, 0 8px 20px -6px ${aA(accentDeep, 0.6)}` }}>
        <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: "46%", background: `linear-gradient(180deg, ${aA("#FFF", 0.45)}, ${aA("#FFF", 0)})` }} />
        <div style={{ position: "absolute", inset: 0, animation: "sheen 5s linear infinite", background: `linear-gradient(105deg, transparent 35%, ${aA("#FFF", 0.35)} 50%, transparent 65%)`, backgroundSize: "260% 100%" }} />
        <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center" }}>
          <div style={{ width: size * 0.66, height: size * 0.66, animation: `breathe ${(mood.feel && mood.feel.breathe) || 6}s ease-in-out infinite` }}>
            <svg width="100%" height="100%" viewBox="0 0 24 24" fill="none"><MoodSigil k={mood.key} /></svg>
          </div>
        </div>
      </div>
    </div>
  );
}

// the glossy Moon — the companion (a real crescent-lit sphere, distinct from the star emblem).
function MoonGloss({ mood, size = 56 }: any) {
  const { accent, accentDeep, glow, moon } = mood; const body = moon || "#EADFC8";
  return (
    <div style={{ width: size, height: size, position: "relative" }}>
      <div style={{ position: "absolute", inset: 0, borderRadius: 999, overflow: "hidden",
        background: `radial-gradient(circle at 36% 30%, #FFFDF8 0%, ${body} 32%, ${accent} 70%, ${accentDeep} 100%)`,
        boxShadow: `inset -${size * 0.1}px -${size * 0.11}px ${size * 0.22}px ${aA(accentDeep, 0.55)}, inset ${size * 0.07}px ${size * 0.08}px ${size * 0.16}px ${aA("#FFF", 0.55)}` }}>
        <div style={{ position: "absolute", left: "44%", top: "40%", width: "34%", height: "30%", borderRadius: 999, background: `radial-gradient(circle, ${aA(accentDeep, 0.18)}, ${aA(accentDeep, 0)} 70%)` }} />
        <div style={{ position: "absolute", left: "24%", top: "20%", width: "26%", height: "20%", borderRadius: 999, background: `radial-gradient(circle, ${aA("#FFF", 0.85)}, ${aA("#FFF", 0)} 70%)`, filter: "blur(1.5px)" }} />
      </div>
    </div>
  );
}

// ============================ GANESHA — the companion ============================
// The guide: Ganesha (remover of obstacles, invoked at beginnings) drawn as warm gold
// line-art in the app's hand-drawn celestial language — serene, reverent, never slapstick.
// Layered <g> groups so trunk sways, aura breathes, a diya flickers, incense rises.
// `full` shows the seated body (chat header); default is the head medallion (FAB).
function Ganesha({ size = 44, mood, full = false }: any) {
  const { accent, accentDeep, glow } = mood;
  const gold = "#B77E2E", goldD = "#8A5A22", goldL = "#E7B24E";
  const vb = full ? "0 0 100 128" : "2 2 96 92";
  const stroke = { fill: "none", stroke: gold, strokeWidth: 2.2, strokeLinecap: "round" as const, strokeLinejoin: "round" as const };
  const thin = { ...stroke, strokeWidth: 1.6 };
  return (
    <svg width={size} height={size * (full ? 1.28 : 0.958)} viewBox={vb} style={{ display: "block", overflow: "visible" }}>
      <defs>
        <linearGradient id="gnGold" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor={goldL} /><stop offset="100%" stopColor={goldD} /></linearGradient>
        <radialGradient id="gnHalo" cx="50%" cy="45%" r="55%"><stop offset="0%" stopColor={aA(glow, 0.5)} /><stop offset="100%" stopColor={aA(glow, 0)} /></radialGradient>
        <radialGradient id="gnFlame" cx="50%" cy="70%" r="60%"><stop offset="0%" stopColor="#FFE9A8" /><stop offset="55%" stopColor="#FFB24D" /><stop offset="100%" stopColor="#E4791F" /></radialGradient>
      </defs>
      {/* aura */}
      <circle cx="50" cy={full ? 46 : 50} r={full ? 40 : 42} fill="url(#gnHalo)" style={{ transformOrigin: "50px 48px", animation: "haloBreathe 5s ease-in-out infinite" }} />
      {/* lotus pedestal (chat only) — iconic, clean, drawn behind the deity */}
      {full && (<g fill={aA(goldL, 0.07)} stroke={gold} strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round">
        <path d="M50 92 C45 100 45 110 50 113 C55 110 55 100 50 92 Z" />
        <path d="M50 113 C42 107 36 101 32 103 C34 109 42 113 50 113 Z" />
        <path d="M50 113 C58 107 64 101 68 103 C66 109 58 113 50 113 Z" />
        <path d="M50 113 C40 111 30 109 23 112 C30 117 42 117 50 113 Z" />
        <path d="M50 113 C60 111 70 109 77 112 C70 117 58 117 50 113 Z" />
      </g>)}
      {/* the deity — breathes gently */}
      <g style={{ transformOrigin: "50px 48px", animation: "breathe 5.5s ease-in-out infinite" }}>
        {/* crown (mukut) */}
        <path {...stroke} d="M36 24 L41 11 L46 20 L50 6 L54 20 L59 11 L64 24 Z" fill="url(#gnGold)" fillOpacity="0.14" />
        <circle cx="50" cy="8.5" r="2" fill={goldL} />
        {/* ears */}
        <path {...stroke} d="M37 30 C15 25 11 57 33 63 C37 54 38 40 37 30 Z" fill={aA(goldL, 0.06)} />
        <path {...stroke} d="M63 30 C85 25 89 57 67 63 C63 54 62 40 63 30 Z" fill={aA(goldL, 0.06)} />
        {/* inner-ear lines */}
        <path {...thin} d="M33 36 C24 36 22 52 32 57" />
        <path {...thin} d="M67 36 C76 36 78 52 68 57" />
        {/* face */}
        <path {...stroke} d="M37 30 C40 23 60 23 63 30 C68 44 64 60 50 66 C36 60 32 44 37 30 Z" fill={aA(goldL, 0.05)} />
        {/* tilak */}
        <path {...thin} d="M50 28 L50 39" />
        <circle cx="50" cy="32" r="1.4" fill={goldD} />
        {/* serene eyes (downcast) */}
        <path {...thin} d="M40 45 C43 42 47 42 49 45" />
        <path {...thin} d="M51 45 C53 42 57 42 60 45" />
        {/* tusks — one full, one broken (Ekadanta) */}
        <path {...thin} d="M44 63 C43 67 43 70 45 72" />
        <path {...thin} d="M56 63 C57 66 57 68 56 69" />
      </g>
      {/* trunk — curls to one side, sways softly, own pivot near the brow */}
      <path {...stroke} strokeWidth="2.6" d="M50 57 C50 66 47 72 43 77 C38 82 40 90 47 89 C52 88 52 83 49 82" fill="none" style={{ transformOrigin: "50px 57px", animation: "trunkSway 4.5s ease-in-out infinite" }} />
      {/* soft incense wisps rising beside the head (chat only) */}
      {full && (<g>
        <path d="M31 66 C28 57 34 53 31 44" fill="none" stroke={aA("#C9A15A", 0.45)} strokeWidth="1.3" strokeLinecap="round" style={{ transformOrigin: "31px 66px", animation: "incenseRise 3.4s ease-out infinite" }} />
        <path d="M69 66 C72 57 66 53 69 44" fill="none" stroke={aA("#C9A15A", 0.45)} strokeWidth="1.3" strokeLinecap="round" style={{ transformOrigin: "69px 66px", animation: "incenseRise 3.4s ease-out .7s infinite" }} />
      </g>)}
    </svg>
  );
}


function Sheet({ open, onClose, children }: any) {
  if (!open) return null;
  return (
    <div style={{ position: "absolute", inset: 0, zIndex: 80 }}>
      <div onClick={onClose} style={{ position: "absolute", inset: 0, background: aA("#0C0B0A", 0.4), animation: "fadeIn .25s ease" }} />
      <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, maxHeight: "84%", overflowY: "auto", background: PAPER, borderRadius: "30px 30px 0 0", border: `1px solid ${HAIR}`, boxShadow: `0 -16px 40px -16px ${aA("#1A1408", 0.4)}`, padding: "14px 22px 30px", animation: "sheetUp .42s cubic-bezier(.2,.85,.25,1)" }}>
        <div style={{ width: 38, height: 4, borderRadius: 999, background: aA("#0C0B0A", 0.14), margin: "0 auto 18px" }} />
        {children}
      </div>
    </div>
  );
}

const CYCLE = ["Settled", "Bold", "Tender", "Restless", "Capable", "Warm", "Deep", "Wandering", "Driven", "Upbeat", "Quiet", "Guarded"];
const rise = (d: number) => ({ animation: `riseIn .6s cubic-bezier(.2,.85,.25,1) ${d}ms both` });

(window as any).__astroUI = {
  useState, useRef, useEffect, useMemo, aA,
  PAPER, WASH, INK, INK2, GRAY, HAIR, ORANGE, SANS, SERIF, MONO,
  pill, card, Label, Icon, I, Flame, GlossIcon, Press, MoodEmblem, MoonGloss, Ganesha, Sheet, CYCLE, rise,
  MOOD: (window as any).MOOD_BY_KEY, PERSONAL: (window as any).PERSONAL_LINES || {}, DAY_LINE: (window as any).DAY_LINE || {},
  AHEAD: (window as any).AHEAD || [], ECL: (window as any).ECLIPSE || {}, MIR: (window as any).MIRROR || {},
  CHECKIN: (window as any).CHECKIN_REFLECTION || (() => "Thanks for checking in."),
  CLOCK: (window as any).DAY_CLOCK || { windows: [] }, ALMANAC: (window as any).ALMANAC || {}, FOCUS: (window as any).FOCUS || null,
  LIFE_AREAS: (window as any).LIFE_AREAS || {}, LIFE_META: (window as any).LIFE_AREA_META || {}, FESTIVAL: (window as any).FESTIVAL || null,
  READ_CHIPS: (window as any).READ_CHIPS || {}, HORA: (window as any).HORA_LINE || "",
  PANCHANG_SOON: (window as any).PANCHANG_SOON || [], MONTH: (window as any).MONTH || { days: [] }, dayDetail: (window as any).dayDetail || (() => ({})),
  MUHURAT: (window as any).MUHURAT || { events: [], results: {} }, CAL_DOCTOR: (window as any).CAL_DOCTOR || [],
  ASK_MOMENT: (window as any).ASK_MOMENT || { samples: [], answers: [] }, TIME_CAPSULE: (window as any).TIME_CAPSULE || { moments: [], shelf: [] },
  NAME: "Aarav", DATE: "Tuesday, 17 June",
};
})();
