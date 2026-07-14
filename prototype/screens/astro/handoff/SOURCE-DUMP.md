# ASTROLO — Complete Source Dump

Every runtime file, full path + complete untruncated contents. Load/execution order is the
order below (it is also the \`<script>\` order in Home.html). Fences are \`~~~\` because the
code uses backtick template literals throughout.

The 6 image assets are binary (PNG) and cannot be inlined here — copy them from
\`screens/astro/\`: chatfab.png, chatsage1.png, chatsage2.png, chatsage3.png, sage2.png
(referenced), sage1.png (present, unused). See PORT-FACTS.md for dimensions + usage.


---

## `screens/astro/Home.html`  
_81 lines_

~~~html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>ASTROLO — Home</title>
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400;1,6..72,500&family=Spline+Sans+Mono:wght@500;600&display=swap" rel="stylesheet" />
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; -webkit-font-smoothing: antialiased; text-rendering: optimizeLegibility; }
  html, body { width: 100%; height: 100%; }
  body { background: #14151A; display: flex; align-items: center; justify-content: center; min-height: 100vh; padding: 18px; font-family: 'Manrope', sans-serif; }
  #frame { width: 412px; height: 892px; position: relative; border-radius: 54px; padding: 11px; background: linear-gradient(160deg, #2a2c32, #141519 60%); transform-origin: center center;
    box-shadow: 0 0 0 2px #000, 0 50px 120px rgba(0,0,0,0.7), inset 0 1px 1px rgba(255,255,255,0.12); }
  #screen { width: 100%; height: 100%; position: relative; border-radius: 44px; overflow: hidden; background: #FFFFFF; }
  #statusbar { position: absolute; top: 0; left: 0; right: 0; height: 52px; z-index: 60; display: flex; align-items: center; justify-content: space-between; padding: 0 30px 0 32px; pointer-events: none; font-weight: 700; font-size: 14px; color: #11121A; }
  #statusbar .r { display: flex; align-items: center; gap: 6px; }
  #notch { position: absolute; top: 12px; left: 50%; transform: translateX(-50%); width: 118px; height: 30px; background: #000; border-radius: 999px; z-index: 61; }
  #screen ::-webkit-scrollbar { width: 0; height: 0; display: none; }

  @keyframes floatY { 0%,100%{ transform: translateY(0);} 50%{ transform: translateY(-7px);} }
  @keyframes spinSlow { to { transform: rotate(360deg); } }
  @keyframes twinkle { 0%,100%{ opacity: var(--lo,.3);} 50%{ opacity: var(--hi,.95);} }
  @keyframes cloudDrift { 0%,100%{ transform: translateX(0);} 50%{ transform: translateX(26px);} }
  @keyframes dropIn { from { opacity: 0; transform: translateX(-50%) translateY(-8px); } to { opacity: 1; transform: translateX(-50%) translateY(0); } }
  @keyframes bar { 0%,100%{ transform: scaleY(0.28); } 50%{ transform: scaleY(1); } }
  @keyframes breathe { 0%,100%{ transform: scale(1); } 50%{ transform: scale(1.07); } }
  @keyframes blink { 0%,100%{ opacity: 0.25; transform: translateY(0); } 50%{ opacity: 0.85; transform: translateY(-2px); } }
  @keyframes sound { 0%,100%{ transform: scaleY(0.5); } 50%{ transform: scaleY(1.3); } }
  @keyframes shimmer { from { background-position: -160% 0; } to { background-position: 260% 0; } }
  @keyframes sheen { from { background-position: 200% 0; } to { background-position: -120% 0; } }
  @keyframes riseIn { from { opacity: 0; transform: translateY(18px); } to { opacity: 1; transform: none; } }
  @keyframes popIn { from { opacity: 0; transform: scale(.86); } to { opacity: 1; transform: none; } }
  @keyframes glowPulse { 0%,100%{ box-shadow: 0 0 14px 0 var(--gc, rgba(255,180,90,.5)); } 50%{ box-shadow: 0 0 26px 4px var(--gc, rgba(255,180,90,.7)); } }
  @keyframes coinUp { from { opacity: 1; transform: translateY(0);} to { opacity: 0; transform: translateY(-26px);} }
  @keyframes sheetUp { from { transform: translateY(100%);} to { transform: translateY(0);} }
  @keyframes fadeIn { from { opacity: 0;} to { opacity: 1;} }
  @keyframes skyShoot { 0%,88%{ opacity: 0; transform: translate(0,0);} 90%{ opacity: 1;} 100%{ opacity: 0; transform: translate(-58px,34px);} }
  @keyframes skyBird { 0%{ transform: translate(0,0);} 50%{ transform: translate(150px,-8px);} 100%{ transform: translate(300px,-2px);} }
  @keyframes fireflyGlow { 0%,100%{ opacity: 0; } 50%{ opacity: 0.9; } }
  @keyframes flameFlicker { 0%,100%{ transform: scaleY(1) scaleX(1); opacity: .95; } 30%{ transform: scaleY(1.14) scaleX(.92); opacity: 1; } 60%{ transform: scaleY(.9) scaleX(1.06); opacity: .82; } }
  @keyframes incenseRise { 0%{ opacity: 0; transform: translateY(2px) scaleX(1); } 40%{ opacity: .5; } 100%{ opacity: 0; transform: translateY(-16px) scaleX(1.5); } }
  @keyframes trunkSway { 0%,100%{ transform: rotate(0deg); } 50%{ transform: rotate(2.4deg); } }
  @keyframes peekIn { 0%{ opacity: 0; transform: translateY(6px) scale(.9); } 12%,80%{ opacity: 1; transform: none; } 100%{ opacity: 0; transform: translateY(-4px) scale(.96); } }
  @keyframes haloBreathe { 0%,100%{ opacity: .5; transform: scale(1); } 50%{ opacity: .82; transform: scale(1.08); } }
  @keyframes pulseRing { 0%{ opacity: .5; transform: scale(1); } 100%{ opacity: 0; transform: scale(2.4); } }
  @keyframes sparkle { 0%,100%{ opacity: 0; transform: scale(.4) rotate(0deg); } 50%{ opacity: 1; transform: scale(1) rotate(90deg); } }
  @keyframes orbGlow { 0%,100%{ opacity: .35; transform: scale(1); } 50%{ opacity: .7; transform: scale(1.12); } }
  @media (prefers-reduced-motion: reduce){ * { animation: none !important; } }
</style>
</head>
<body>
  <div id="frame">
    <div id="screen">
      <div id="notch"></div>
      <div id="statusbar"><span>9:41</span><span class="r">
        <svg width="18" height="12" viewBox="0 0 18 12"><rect x="0" y="7" width="3" height="5" rx="1" fill="#11121A"/><rect x="5" y="4" width="3" height="8" rx="1" fill="#11121A"/><rect x="10" y="1.5" width="3" height="10.5" rx="1" fill="#11121A"/><rect x="14.5" y="0" width="3" height="12" rx="1" fill="#11121A" opacity=".4"/></svg>
        <svg width="24" height="12" viewBox="0 0 24 12"><rect x="0.5" y="0.5" width="19" height="11" rx="3" stroke="#11121A" stroke-opacity=".5"/><rect x="2" y="2" width="14" height="8" rx="1.5" fill="#11121A"/><rect x="21" y="4" width="1.5" height="4" rx=".75" fill="#11121A" opacity=".6"/></svg>
      </span></div>
      <div id="root"></div>
    </div>
  </div>
  <script>
    function fit(){ var f=document.getElementById('frame'); var s=Math.min(window.innerWidth/412, window.innerHeight/892, 1); f.style.transform='scale('+s+')'; }
    window.addEventListener('resize', fit); fit();
  </script>
  <script src="https://unpkg.com/react@18.3.1/umd/react.development.js" integrity="sha384-hD6/rw4ppMLGNu3tX5cjIb+uRZ7UkRJ6BPkLpg4hAu/6onKUg4lLsHAs9EBPT82L" crossorigin="anonymous"></script>
  <script src="https://unpkg.com/react-dom@18.3.1/umd/react-dom.development.js" integrity="sha384-u6aeetuaXnQ38mYT8rp6sbXaQe3NL9t+IBXmnYxwkUI2Hw4bsp2Wvmx4yRQF1uAm" crossorigin="anonymous"></script>
  <script src="https://unpkg.com/@babel/standalone@7.29.0/babel.min.js" integrity="sha384-m08KidiNqLdpJqLq95G/LEi8Qvjl/xUYll3QILypMoQ65QorJ9Lvtp2RXYGBFj1y" crossorigin="anonymous"></script>
  <script type="text/babel" data-presets="typescript" src="theme.ts"></script>
  <script type="text/babel" data-presets="react,typescript" src="astro.tsx"></script>
  <script type="text/babel" data-presets="react,typescript" src="astro-today.tsx"></script>
  <script type="text/babel" data-presets="react,typescript" src="astro-plan.tsx"></script>
  <script type="text/babel" data-presets="react,typescript" src="astro-screens.tsx"></script>
  <script type="text/babel" data-presets="react,typescript">
    ReactDOM.createRoot(document.getElementById("root")).render(<window.AstroApp />);
  </script>
</body>
</html>

~~~

---

## `screens/astro/theme.ts`  
_531 lines_

~~~ts
// theme.ts, ASTROLO design tokens. LIGHT "paper" system.
// The canvas is a constant warm ivory; the day's MOOD only tints ACCENTS (the Sky
// Wheel glow, linework highlights, chips, the diya), never the whole background.
// Plain data only, no React. Numbers are unit-less so they port straight to RN points.

type MoodKey =
  | "Settled" | "Guarded" | "Bold" | "Tender" | "Restless" | "Capable"
  | "Warm" | "Deep" | "Wandering" | "Driven" | "Upbeat" | "Quiet";

interface MotionFeel {
  breathe: number;   // sec, kolam core breath + glow pulse
  orbit: number;     // sec, base orbital period of the grahas (smaller = livelier)
  twinkle: number;   // sec, dust-mote / star shimmer base
  spring: number;    // interactive return stiffness multiplier (1 = base)
  wobble: number;    // 0..1 idle wander amplitude
  drag: number;      // wheel spin friction (higher = settles faster)
}
interface Forecast { mood: string; opportunity: string; caution: string; action: string; why: string; }

interface Mood {
  key: MoodKey;
  vibe: string;
  accent: string;     // the mood color, reads on ivory (chips, glow, diya)
  accentDeep: string; // darker variant for accent text / linework on paper
  glow: string;       // soft luminous tint for the wheel halo
  wash: string;       // VERY faint top-corner tint on the paper (rgba, ~0.05)
  moon: string;       // moon body tint
  feel: MotionFeel;
  forecast: Forecast;
}

const THEME = {
  // constant light canvas, warm white, monochrome-editorial -------------------------
  paper: "#F1EBDF",        // warm white page
  paperHi: "#F8F3EA",      // lighter top wash
  paperLo: "#E8E0D1",      // slightly deeper bottom
  card: "#F7F2E8",         // card fill, barely lifted off the page
  cardAlt: "#EFE8DA",      // alt / inset fill
  cardLine: "rgba(28,22,15,0.13)",   // hairline border
  cardLineStrong: "rgba(28,22,15,0.26)",
  shadow: "rgba(40,30,16,0.10)",
  shadowSoft: "rgba(40,30,16,0.05)",
  ink: "#1C1610",          // near-black, warm, primary text
  inkSoft: "#5C5142",      // secondary
  inkFaint: "#9A8E7B",     // tertiary / mono captions
  gold: "#9A7736",         // used sparingly now
  goldSoft: "#C9B versterkt",
  line: "rgba(28,22,15,0.16)",       // hairline rule on paper
  lineFaint: "rgba(28,22,15,0.09)",

  space: { xxs: 4, xs: 8, sm: 12, md: 16, lg: 22, xl: 30, xxl: 42, huge: 56 },
  radius: { xs: 8, sm: 12, md: 16, lg: 20, xl: 26, pill: 999 },
  font: {
    display: "'Newsreader', Georgia, serif",
    ui: "'Hanken Grotesk', system-ui, sans-serif",
    mono: "'Spline Sans Mono', ui-monospace, monospace",
  },
  // wider scale, Co-Star-style contrast between giant display and tiny mono
  size: { micro: 10, label: 11, body: 15, lead: 17, title: 20, h2: 26, h1: 34, hero: 52, giant: 76, mega: 104 },
  weight: { reg: "400", med: "500", semi: "600", bold: "700" },
  screen: { w: 390, h: 844 },
} as any;
THEME.inkFaint = "#9A8E7B";
THEME.goldSoft = "#C9B27E";

// 12 moods, accent + motion personality only. Forecast copy stays warm, plain English.
const MOODS: Mood[] = [
  { key: "Settled", vibe: "A soft, homeward kind of day.",
    accent: "#C2724E", accentDeep: "#9E5635", glow: "#E7A578", wash: "rgba(194,114,78,0.06)", moon: "#F0DFC8",
    feel: { breathe: 6.5, orbit: 30, twinkle: 5.5, spring: 0.9, wobble: 0.16, drag: 2.4 },
    forecast: { mood: "Your heart leans toward home and familiar faces.", opportunity: "A good day to tidy one corner of your life.", caution: "A low mood may drift in. It is the day, not you.", action: "Call someone who feels like home.", why: "The moon sits close to your house of comfort today, so the pull is inward and gentle. Nothing dramatic overhead, just a quiet tide asking you to rest." } },
  { key: "Guarded", vibe: "Keep a little back for yourself today.",
    accent: "#5E7C92", accentDeep: "#43606F", glow: "#9DBDD0", wash: "rgba(94,124,146,0.06)", moon: "#E2EAF0",
    feel: { breathe: 7.5, orbit: 36, twinkle: 6.5, spring: 0.8, wobble: 0.10, drag: 2.8 },
    forecast: { mood: "You may feel like protecting your soft parts.", opportunity: "A good time to set one honest boundary.", caution: "Do not read silence as rejection today.", action: "Say no to one thing without explaining.", why: "A careful planet holds a tight angle to your moon, which can feel like a closed door. It is not coldness, it is the sky asking you to choose where your energy goes." } },
  { key: "Bold", vibe: "The day leans forward. So can you.",
    accent: "#D9482E", accentDeep: "#B23420", glow: "#F58A6A", wash: "rgba(217,72,46,0.06)", moon: "#F6DCCF",
    feel: { breathe: 4.2, orbit: 17, twinkle: 3.6, spring: 1.35, wobble: 0.28, drag: 1.5 },
    forecast: { mood: "There is heat in you that wants a direction.", opportunity: "Ask for the thing you have been circling.", caution: "Speed can turn into snapping. Aim before you fire.", action: "Send the message you keep rewriting.", why: "A fiery planet lights up your house of will today, lending courage and a short fuse in equal measure. Point it at something worth the spark." } },
  { key: "Tender", vibe: "Be soft with yourself first.",
    accent: "#D06A8C", accentDeep: "#AC4E6E", glow: "#F2A6C0", wash: "rgba(208,106,140,0.06)", moon: "#F7E0E9",
    feel: { breathe: 7.0, orbit: 32, twinkle: 6.0, spring: 0.85, wobble: 0.14, drag: 2.6 },
    forecast: { mood: "Feelings sit close to the surface today.", opportunity: "Let someone see how you actually are.", caution: "You may take a small thing to heart. Breathe.", action: "Write down one kind thing about yourself.", why: "A gentle planet brushes your moon, opening the heart wide. Beautiful for closeness, a little raw for criticism. Handle yourself like something precious." } },
  { key: "Restless", vibe: "A lot wants to move at once.",
    accent: "#E0982A", accentDeep: "#B5781A", glow: "#FAC768", wash: "rgba(224,152,42,0.07)", moon: "#F6E7C8",
    feel: { breathe: 3.6, orbit: 13, twinkle: 2.8, spring: 1.5, wobble: 0.32, drag: 1.2 },
    forecast: { mood: "Your mind is jumping ahead of your feet.", opportunity: "Channel the buzz into one small finish.", caution: "Scattered energy starts ten things, ends none.", action: "Pick one task and close it fully.", why: "A quick planet runs fast through your sky today, quickening thoughts and fingers. Useful, if you give it a single track to run on." } },
  { key: "Capable", vibe: "Quietly, you can handle this.",
    accent: "#2E9C7E", accentDeep: "#1F7660", glow: "#74D6BB", wash: "rgba(46,156,126,0.06)", moon: "#D7EFE6",
    feel: { breathe: 5.5, orbit: 24, twinkle: 4.6, spring: 1.05, wobble: 0.18, drag: 2.2 },
    forecast: { mood: "A steady competence is humming under you.", opportunity: "Tackle the thing you have been avoiding.", caution: "Do not pile on more just because you can.", action: "Do the hard task first, before noon.", why: "The sun supports your most disciplined planet today, the sky's version of a firm hand on your back. Real work goes smoothly. Use the window." } },
  { key: "Warm", vibe: "Let the good in. It is allowed.",
    accent: "#D98A2B", accentDeep: "#B26C18", glow: "#F8BC63", wash: "rgba(217,138,43,0.06)", moon: "#F6E6C8",
    feel: { breathe: 6.0, orbit: 26, twinkle: 5.0, spring: 1.0, wobble: 0.18, drag: 2.3 },
    forecast: { mood: "There is sweetness available if you reach.", opportunity: "Say yes to a small invitation.", caution: "Comfort can tip into one too many. Enjoy, lightly.", action: "Share food or a laugh with someone.", why: "The great benefic warms your house of joy today, widening the heart and the appetite. A generous sky. Let it be generous to you." } },
  { key: "Deep", vibe: "There is something underneath. Look.",
    accent: "#5B4FC4", accentDeep: "#43399E", glow: "#9A8CF0", wash: "rgba(91,79,196,0.06)", moon: "#E2DEF6",
    feel: { breathe: 8.0, orbit: 38, twinkle: 7.0, spring: 0.75, wobble: 0.12, drag: 3.0 },
    forecast: { mood: "You feel pulled below the surface today.", opportunity: "A good day for honest, private thinking.", caution: "Do not mistake intensity for truth. Sit with it.", action: "Spend ten quiet minutes with no screen.", why: "The moon dips into your hidden house, where the deeper currents live. Heavy is not bad here, it is just deep. Let yourself go down, and come back." } },
  { key: "Wandering", vibe: "No need to land anywhere yet.",
    accent: "#7B7FD0", accentDeep: "#5C60AE", glow: "#AEB2F0", wash: "rgba(123,127,208,0.06)", moon: "#E5E6F7",
    feel: { breathe: 8.5, orbit: 42, twinkle: 7.5, spring: 0.7, wobble: 0.24, drag: 3.2 },
    forecast: { mood: "Your attention drifts, and that is fine today.", opportunity: "Let yourself follow a curious thread.", caution: "Plans may feel slippery. Hold them loosely.", action: "Take the long way somewhere on purpose.", why: "The moon floats between signs today, that in-between hum. Direction is foggy, imagination is wide open. Wander on purpose, not by accident." } },
  { key: "Driven", vibe: "Point the engine somewhere true.",
    accent: "#D45A2A", accentDeep: "#AD4318", glow: "#F59364", wash: "rgba(212,90,42,0.06)", moon: "#F6DECF",
    feel: { breathe: 4.0, orbit: 15, twinkle: 3.2, spring: 1.4, wobble: 0.26, drag: 1.4 },
    forecast: { mood: "You want to build, push, get somewhere.", opportunity: "Make real progress on the big thing.", caution: "Driven can forget to be kind. Check in once.", action: "Block one hour for the goal that matters.", why: "Two strong planets line up in your house of action, a rare clean runway. Ambition has fuel today. Spend it on what you actually want." } },
  { key: "Upbeat", vibe: "The day is grinning. Grin back.",
    accent: "#E2654A", accentDeep: "#BC4830", glow: "#F89A7E", wash: "rgba(226,101,74,0.06)", moon: "#F7E0D6",
    feel: { breathe: 4.6, orbit: 18, twinkle: 3.4, spring: 1.3, wobble: 0.26, drag: 1.6 },
    forecast: { mood: "Lightness comes easily to you today.", opportunity: "Reach out, the timing is friendly.", caution: "Do not promise more than tomorrow can keep.", action: "Do one thing purely because it is fun.", why: "The moon meets the great benefic in a bright corner of your sky, the closest thing to a good mood on tap. Ride it, just leave room for the comedown." } },
  { key: "Quiet", vibe: "Nothing to prove today.",
    accent: "#7C8AA0", accentDeep: "#5C6A80", glow: "#AEBDD0", wash: "rgba(124,138,160,0.06)", moon: "#E6ECF3",
    feel: { breathe: 9.0, orbit: 46, twinkle: 8.0, spring: 0.65, wobble: 0.08, drag: 3.4 },
    forecast: { mood: "A stillness wants to settle over you.", opportunity: "Rest counts as productive today.", caution: "Forcing output now will only cost you later.", action: "Cancel one thing and protect the gap.", why: "The moon wanes in a slow part of your chart, dimming the noise. This is a recovery day in disguise. Let it be small." } },
];

const MOOD_BY_KEY: Record<string, Mood> = {};
MOODS.forEach((m) => { MOOD_BY_KEY[m.key] = m; });

// As you spin the Sky Wheel, the moon's position reads out in warm plain English.
// 12 stations around the wheel, no Sanskrit, the Vedic structure is in the GEOMETRY.
const MOON_STATIONS: string[] = [
  "rising over a calm, homeward stretch",
  "crossing a patient, building patch of sky",
  "moving through a bright, talkative stretch",
  "settling into a tender, close part of the sky",
  "passing a warm, generous corner",
  "entering a careful, tidy stretch",
  "drifting through a soft, balancing patch",
  "diving into a deep, private stretch",
  "wandering a wide, open corner of sky",
  "climbing a steep, ambitious stretch",
  "skating across a light, social patch",
  "sinking into a slow, restful corner",
];

const AHEAD = [
  { day: "TUE", date: 17, mood: "Capable",  status: "good"      as const, good: "10:20a", avoid: "4:00p" },
  { day: "WED", date: 18, mood: "Restless", status: "difficult" as const, good: "8:10a",  avoid: "1:30p" },
  { day: "THU", date: 19, mood: "Warm",     status: "good"      as const, good: "11:40a", avoid: "6:15p" },
  { day: "FRI", date: 20, mood: "Quiet",    status: "neutral"   as const, good: "9:00a",  avoid: "3:45p" },
  { day: "SAT", date: 21, mood: "Upbeat",   status: "good"      as const, good: "12:10p", avoid: "7:00p" },
];

const CHECKIN_REFLECTIONS: Record<string, string> = {
  calm:   "Calm is a good place to make decisions from. Stay here a beat longer.",
  tender: "Tender is not weak. It just means something matters to you today.",
  sharp:  "Sharp can cut clean or cut careless. Aim it at a problem, not a person.",
  heavy:  "Heavy, on a slow day. Be gentle, this is the day passing through you.",
  wired:  "Wired with nowhere to put it can fray. Pick one thing and pour it in.",
};

(window as any).THEME = THEME;
(window as any).MOODS = MOODS;
(window as any).MOOD_BY_KEY = MOOD_BY_KEY;
(window as any).MOON_STATIONS = MOON_STATIONS;

// The Day's Water, each mood describes how the surface behaves, in plain warm words.
// (kept for reference; the live hero is now the Mood Moon below)
const WATER_SURFACE: Record<string, string> = {
  Settled: "still", Guarded: "calm", Bold: "bright", Tender: "soft", Restless: "quick",
  Capable: "smooth", Warm: "golden", Deep: "deep", Wandering: "drifting", Driven: "moving",
  Upbeat: "dancing", Quiet: "glassy",
};
(window as any).WATER_SURFACE = WATER_SURFACE;

// THE MOOD MOON, the living sky hero. In Vedic astrology the Moon (Chandra) governs the
// mind & mood, so the day's feeling is read in the Moon's phase, colour, halo & weather.
// Each mood reshapes it: illum 0..1 (0 new → 1 full), waxing side, halo/cloud/star levels.
interface MoonCfg { illum: number; waxing: boolean; halo: number; cloud: number; star: number; shoot: boolean; }
const MOON_CFG: Record<string, MoonCfg> = {
  Settled:   { illum: 1.00, waxing: true,  halo: 0.55, cloud: 0.35, star: 0.35, shoot: false },
  Guarded:   { illum: 0.66, waxing: false, halo: 0.32, cloud: 0.70, star: 0.20, shoot: false },
  Bold:      { illum: 0.94, waxing: true,  halo: 0.95, cloud: 0.18, star: 0.45, shoot: true  },
  Tender:    { illum: 0.74, waxing: true,  halo: 0.78, cloud: 0.30, star: 0.45, shoot: false },
  Restless:  { illum: 0.46, waxing: true,  halo: 0.42, cloud: 0.85, star: 0.55, shoot: true  },
  Capable:   { illum: 0.92, waxing: false, halo: 0.52, cloud: 0.12, star: 0.40, shoot: false },
  Warm:      { illum: 1.00, waxing: true,  halo: 0.85, cloud: 0.25, star: 0.35, shoot: false },
  Deep:      { illum: 0.20, waxing: false, halo: 0.62, cloud: 0.40, star: 0.62, shoot: false },
  Wandering: { illum: 0.62, waxing: true,  halo: 0.50, cloud: 0.78, star: 0.50, shoot: false },
  Driven:    { illum: 0.40, waxing: true,  halo: 0.72, cloud: 0.20, star: 0.45, shoot: true  },
  Upbeat:    { illum: 0.96, waxing: true,  halo: 0.74, cloud: 0.22, star: 0.62, shoot: true  },
  Quiet:     { illum: 0.14, waxing: false, halo: 0.34, cloud: 0.45, star: 0.30, shoot: false },
};
// The Moon's state read out in warm, plain English (no Sanskrit).
const MOON_READING: Record<string, string> = {
  Settled:   "full and warm, sitting low and close",
  Guarded:   "bright, but half-veiled in cloud",
  Bold:      "large and burning low on the sky",
  Tender:    "soft, haloed in rose",
  Restless:  "darting behind quick clouds",
  Capable:   "clear, steady, and sure",
  Warm:      "golden, and generous tonight",
  Deep:      "deep in shadow, a rim of light",
  Wandering: "hazy, drifting without anchor",
  Driven:    "rising fast with a trail of light",
  Upbeat:    "bright, and dancing with sparks",
  Quiet:     "a thin, quiet sliver",
};
(window as any).MOON_CFG = MOON_CFG;
(window as any).MOON_READING = MOON_READING;

// ECLIPSE — the rare "heads up". The backend sends one of these (or null on ordinary days).
// All fields are plain data the card + popup fill from. Voice: warm, calm, plain English.
const ECLIPSE: any = {
  type: "solar",            // "solar" | "lunar"
  inDays: 3,                // countdown
  date: "21 August",        // human date
  // Sutak caution window: ~12h before solar, ~9h before lunar
  sutakDate: "20 August",
  sutakTime: "11:30pm",
  sutakHours: 12,
  sanskrit: "सूर्य ग्रहण",  // सूर्य ग्रहण solar · चन्द्र ग्रहण lunar
  // guidance, keyed by type
  short: {
    solar: "A good week to pause big new beginnings and keep things low-key.",
    lunar: "A time for rest and gentle routines, since feelings can run high.",
  },
  full: {
    solar: "Traditionally a time to pause new beginnings, keep things low-key, and turn inward.",
    lunar: "Emotions can run high, so it's a time for rest, reflection, and gentle routines.",
  },
};
(window as any).ECLIPSE = ECLIPSE;

// MIRROR — the private journal where the user writes to the Moon. All plain data the card
// + writing flow fill from. Voice: gentle, warm, unhurried. Never advice unless asked.
const MIRROR: any = {
  // rotating invitations on the Today card (the app picks one)
  invites: [
    "Anything on your heart tonight?",
    "Tell Sage about your day.",
    "What's sitting with you right now?",
    "How are you, really, tonight?",
    "Anything you want to set down?",
  ],
  // soft placeholders inside the writing space
  placeholders: [
    "Whatever it is, you can say it here. It's just me, and I'm listening.",
    "Start anywhere. There's no right way to do this.",
    "Pour it out. I'm here, and I'm not going anywhere.",
  ],
  // the Moon's single warm line back, chosen by the feeling of the entry.
  // (demo buckets; the real app classifies tone server-side.)
  responses: {
    heavy:   "That sounds heavy. You don't have to carry it alone tonight.",
    happy:   "I'm glad. Hold onto this one.",
    tender:  "Thank you for trusting me with that. I've got it now.",
    tired:   "You've done enough for today. Let it rest here with me.",
    return:  "You've been here before, and you came through it. You will again.",
  },
  // distress: extra gentleness + a quiet, caring pointer to help (never clinical)
  distress: {
    line: "I'm really glad you told me. You matter, and you don't have to sit with this alone.",
    help: "If things feel too heavy, talking to someone can help. KIRAN, a free helpline, is there any time at 1800-599-0019.",
  },
};
(window as any).MIRROR = MIRROR;

// PERSONAL_LINES, the app fills this from the user's OWN history (recent pattern/trend).
// Warm, quietly knowing, never clinical. For a brand-new user with no history yet, the
// app passes null and the line gracefully collapses. (Demo: keyed by today's mood.)
const PERSONAL_LINES: Record<string, string> = {
  Settled:   "You usually soften on days like this, let yourself.",
  Guarded:   "Last few guarded days, you pulled back and felt better for it.",
  Bold:      "When the sky runs hot, you tend to move fast, aim first.",
  Tender:    "You feel these days deeply. That's not a flaw of yours.",
  Restless:  "You usually run scattered on days like this, so pick one thing.",
  Capable:   "Your best work tends to land on mornings like this one.",
  Warm:      "You open up easily on warm days, someone will be glad you did.",
  Deep:      "You usually run low on days like this, so go gentle with yourself.",
  Wandering: "You drift on days like this, and you always find your way back.",
  Driven:    "When you lock in like today, you tend to forget to rest.",
  Upbeat:    "These bright days lift you fast, just leave room for the dip after.",
  Quiet:     "You've been needing a slow day. This is the one.",
};
(window as any).PERSONAL_LINES = PERSONAL_LINES;

// CHECKIN_REFLECTION — compares how the user feels to the DAY'S actual energy (the sky),
// per the spec: if their weight matches a heavy sky it's "real, not random"; if it clashes
// with an open sky it's "coming from you, not the sky." Instant, no AI. Plain + warm.
// dayTone: the sky's weight for each of the 12 moods.
const DAY_TONE: Record<string, "low" | "open" | "high"> = {
  Settled: "low", Guarded: "low", Tender: "low", Deep: "low", Quiet: "low",
  Warm: "open", Capable: "open", Wandering: "open",
  Bold: "high", Restless: "high", Driven: "high", Upbeat: "high",
};
function CHECKIN_REFLECTION(moodSel: string, energySel: string, dayKey: string): string {
  const day = DAY_TONE[dayKey] || "open";
  const heavyMood = moodSel === "heavy";
  const chargedMood = moodSel === "sharp" || moodSel === "wired";
  const softMood = moodSel === "tender";
  const calmMood = moodSel === "calm";
  const lowEnergy = energySel === "low";
  const highEnergy = energySel === "restless" || energySel === "bright";

  if (heavyMood || (calmMood && lowEnergy && false)) {
    if (day === "low") return "The sky is heavy today too, so this weight is real, not random. Be gentle, and let it be slow.";
    return "The day itself is fairly open, so this weight is coming from you, not the sky. Worth a gentle look at what's underneath.";
  }
  if (chargedMood || (highEnergy && !calmMood)) {
    if (day === "high") return "The day is buzzing right along with you. Don't fight it, pick one thing and pour it all in.";
    if (day === "low") return "You're running hotter than the day around you. Burn a little of it off before it frays the evening.";
    return "The day is calmer than you are. That edge is yours today, so spend it on a task, not a person.";
  }
  if (softMood) {
    if (day === "low") return "The sky is soft today too, so the tenderness fits. Let someone be gentle with you.";
    return "You're more open than the day is. Keep a little back for yourself, and protect the soft parts.";
  }
  if (calmMood) {
    if (day === "high") return "You're steadier than the day around you. Nice, let that calm lead while everything else rushes.";
    if (day === "low") return "You and the day are in step, both slow and easy. A good place to simply rest.";
    return "Calm, on an open day. These are clear conditions, a good moment to make any decision you've been holding.";
  }
  // low energy on a low day, etc — gentle default
  if (lowEnergy && day === "low") return "Low, on a slow day. The sky agrees with you, so don't push. Small is enough today.";
  return "Noted. Whatever today holds, you've already done the kind thing by checking in.";
}


// DAY_LINE, the warm one-liner in the greeting, e.g. "A warm, social day." Plain English.
const DAY_LINE: Record<string, string> = {
  Settled: "A calm, homebound day.", Guarded: "A day to hold a little back.",
  Bold: "A day with some fire in it.", Tender: "A soft, feeling day.",
  Restless: "A busy, restless day.", Capable: "A steady, get-things-done day.",
  Warm: "A warm, social day.", Deep: "A quiet, inward day.",
  Wandering: "An open, drifting day.", Driven: "A focused, push-ahead day.",
  Upbeat: "A light, easy day.", Quiet: "A slow, restful day.",
};
(window as any).DAY_LINE = DAY_LINE;
(window as any).AHEAD = AHEAD;
(window as any).CHECKIN_REFLECTIONS = CHECKIN_REFLECTIONS;
(window as any).CHECKIN_REFLECTION = CHECKIN_REFLECTION;

// DAY CLOCK — today's windows from sunrise to sunrise. Hours are decimal on a 6..30 scale
// (6 = 6am today, 30 = 6am tomorrow), so the ribbon is one continuous day. `q` is quality:
// best | good | neutral | hold | rest. Real timings come from the backend (sunrise/sunset +
// muhurta math for the user's place). `tip` is one warm plain line.
const DAY_CLOCK = {
  sunrise: 6, // am
  windows: [
    { name: "Early calm", start: 6, end: 9, q: "neutral", tip: "a slow, gentle start" },
    { name: "Rahu Kaal", start: 9, end: 10.5, q: "hold", tip: "hold big decisions, let it pass" },
    { name: "Building", start: 10.5, end: 11.8, q: "good", tip: "good for steady work" },
    { name: "Abhijit", start: 11.8, end: 12.6, q: "best", tip: "the day's strongest 48 minutes" },
    { name: "Open afternoon", start: 12.6, end: 15, q: "good", tip: "good for important talks" },
    { name: "Ordinary hours", start: 15, end: 16.5, q: "neutral", tip: "fine for everyday things" },
    { name: "Warm evening", start: 16.5, end: 18, q: "good", tip: "a kind window for people" },
    { name: "Wind down", start: 18, end: 19.5, q: "hold", tip: "ease off, don't push" },
    { name: "Night", start: 19.5, end: 30, q: "rest", tip: "rest, the day is done" },
  ],
  bestName: "Abhijit", avoidName: "Rahu Kaal",
};
(window as any).DAY_CLOCK = DAY_CLOCK;

// TODAY AT A GLANCE — the day's almanac in plain words (backend fills per day/place).
const ALMANAC = {
  nakshatra: "Rohini", nakFlavor: "a warm, settling star",
  tithi: "Shukla Saptami", tithiNote: "the waxing seventh",
  special: "Sarvartha Siddhi", specialNote: "good for new starts",
  festival: null as string | null,
  best90: "4:10 to 5:40pm",
};
(window as any).ALMANAC = ALMANAC;

// IN FOCUS — set only when one life area is genuinely active today, else null. No permanent
// love/work/money block, no percentages, ever.
const FOCUS = { area: "Work", to: "Timeline", line: "Work in focus today" };
(window as any).FOCUS = FOCUS;

// LIFE AREAS — Love · Work · Money, one honest line each, naming the planet, NO scores.
// Per-mood so it never contradicts the reading (backend computes together via /dashboard/today).
const LIFE_AREAS: Record<string, { love: string; work: string; money: string }> = {
  Settled:   { love: "warm and easy at home, Venus is with you", work: "steady, unhurried progress, Saturn steadies you", money: "a calm day for money, nothing to chase" },
  Guarded:   { love: "keep a little back, Venus asks for care", work: "guard your focus, Saturn wants boundaries", money: "hold the big spends, the flow's mixed" },
  Bold:      { love: "make the first move, Venus is bright", work: "a day to push and ask, the Sun backs you", money: "fine for a bold call, just not a gamble" },
  Tender:    { love: "closeness comes easy, Venus is soft", work: "be gentle with feedback, Saturn feels heavy", money: "steady, let big money wait a day" },
  Restless:  { love: "give each other room, Venus is fidgety", work: "short tasks win, focus is scattered", money: "skip impulse buys, the itch is restless" },
  Capable:   { love: "show up in small ways, Venus is quiet", work: "a strong day to finish things, Saturn rewards you", money: "good for money talks, you're clear-headed" },
  Warm:      { love: "reach out, Venus opens doors", work: "people go your way today, the Sun warms it", money: "generous flow, just don't overdo it" },
  Deep:      { love: "honest talk lands well, Venus goes deep", work: "reflection over action, Saturn turns inward", money: "hold the big spends, the flow's mixed" },
  Wandering: { love: "let plans stay loose, Venus roams", work: "explore, don't commit, focus drifts", money: "wait on decisions, the picture's unclear" },
  Driven:    { love: "don't rush closeness, Venus takes a back seat", work: "big goals move today, the Sun drives you", money: "a fair day to invest, stay measured" },
  Upbeat:    { love: "light and playful, Venus sparkles", work: "momentum is easy, ride it", money: "flow's good, watch small leaks" },
  Quiet:     { love: "small gestures over grand ones, Venus rests", work: "an easy day, save the big push", money: "rest the wallet too, no big moves" },
};
(window as any).LIFE_AREAS = LIFE_AREAS;

// LIFE_AREA_META — per-area constants the row's sheet adds on top of the day's `line`.
// Area-constant + sentiment-neutral on purpose, so `detail` can never contradict the mood line
// (backend replaces with /dashboard/life-areas → { line, detail, why, planet, link } per row).
// link.tab is shown ONLY because that destination (a real tab) exists; drop link when it doesn't.
const LIFE_AREA_META: Record<string, { planet: string; houses: string; detail: string; why: string; link: { label: string; tab: string } }> = {
  Love: {
    planet: "Venus", houses: "7th & 5th",
    detail: "Venus, your love marker, colours the people closest to you today. Meet them where they are and let the easy moments land. The harder conversation will keep for a clearer day, there's no need to force it now.",
    why: "Venus is your love marker, and today the Moon is passing through your partnership area, which softens how you reach for the people you care about.",
    link: { label: "See People", tab: "People" },
  },
  Work: {
    planet: "Saturn", houses: "10th & 6th",
    detail: "Saturn steadies your work today and rewards patient, honest effort over rushing. Pick the one thing that matters most and give it your full attention, rather than scattering across ten small tasks.",
    why: "Saturn rules your house of work and discipline, and the Sun is lighting your sector of daily effort, so slow and steady carries you furthest right now.",
    link: { label: "See your Timeline", tab: "Timeline" },
  },
  Money: {
    planet: "Jupiter", houses: "2nd & 11th",
    detail: "Jupiter is watching your money houses today, so let the day's tone set the size of your moves. Small, sensible steps are fine; keep the bigger commitments for a window that feels clearer.",
    why: "Jupiter rules your gains and growth, and today it's aspecting your houses of money and income, which is why the timing of a bigger spend matters more than usual.",
    link: { label: "See your Timeline", tab: "Timeline" },
  },
};
(window as any).LIFE_AREA_META = LIFE_AREA_META;

// FESTIVAL — a warm one-line wish woven into the header when present, else null.
const FESTIVAL = null as string | null; // e.g. "Happy Makar Sankranti"
(window as any).FESTIVAL = FESTIVAL;

// READING CHIPS — short "good for" / "go easy on" tags per mood (2–3 each), plain words.
// The hero card shows these as chips; the deeper reason lives in mood.forecast.why.
const READ_CHIPS: Record<string, { good: string[]; easy: string[]; offDay?: boolean }> = {
  Settled:   { good: ["home things", "tidying up"], easy: ["big launches", "crowds"] },
  Guarded:   { good: ["boundaries", "saying no"], easy: ["oversharing", "new deals"], offDay: true },
  Bold:      { good: ["asking", "starting"], easy: ["snapping", "rushing"] },
  Tender:    { good: ["closeness", "honesty"], easy: ["criticism", "big crowds"] },
  Restless:  { good: ["short tasks", "errands"], easy: ["signing", "long meetings"], offDay: true },
  Capable:   { good: ["hard tasks", "money talks", "finishing"], easy: ["overloading"] },
  Warm:      { good: ["people", "invitations"], easy: ["overdoing it"] },
  Deep:      { good: ["reflection", "planning"], easy: ["signing", "travel"] },
  Wandering: { good: ["exploring", "ideas"], easy: ["firm plans", "deadlines"], offDay: true },
  Driven:    { good: ["big goals", "building"], easy: ["forcing", "skipping rest"] },
  Upbeat:    { good: ["reaching out", "fun"], easy: ["overpromising"] },
  Quiet:     { good: ["rest", "small things"], easy: ["big pushes", "decisions"], offDay: true },
};
(window as any).READ_CHIPS = READ_CHIPS;

// PLANETARY HOUR line — the greeting's quiet one-liner for the current hora (plain English).
const HORA_LINE = "a good stretch for money and focus right now";
(window as any).HORA_LINE = HORA_LINE;

// ============================ PLAN TAB DATA ============================
// MY PANCHANG — today + next 2 days inline, each softly coloured good/mixed/low for you.
const PANCHANG_SOON = [
  { day: "Today",    date: "1 Jul", quality: "good"  as const, note: "a settling, homeward day", good: "11:40a–12:30p", low: "9:00–10:30a" },
  { day: "Tomorrow", date: "2 Jul", quality: "mixed" as const, note: "bright morning, tired evening", good: "8:10–9:30a", low: "4:00–5:15p" },
  { day: "Thu",      date: "3 Jul", quality: "low"   as const, note: "a low-key day, keep it light", good: "12:10–1:00p", low: "6:30–7:45p" },
];
(window as any).PANCHANG_SOON = PANCHANG_SOON;

// MONTH — a calendar month, each day coloured good/mixed/low, with marks (festival/moon/
// grahan/dasha) + the user's own planned tasks. Backend fills real values per user/place.
function buildMonth() {
  const marks: Record<number, any> = {
    4:  { kind: "moon", label: "Full moon" },
    9:  { kind: "task", label: "Send the pitch" },
    12: { kind: "festival", label: "Guru Purnima" },
    18: { kind: "grahan", label: "Chandra Grahan" },
    19: { kind: "moon", label: "New moon" },
    24: { kind: "dasha", label: "Jupiter dasha begins" },
    27: { kind: "task", label: "Call mom" },
  };
  let s = 5;
  const r = () => { s = (s * 9301 + 49297) % 233280; return s / 233280; };
  const days = Array.from({ length: 31 }, (_, i) => {
    const n = i + 1;
    const q = r();
    const quality = n <= 3 ? (["good", "mixed", "low"][i] as any) : (q < 0.42 ? "good" : q < 0.75 ? "mixed" : "low");
    return { n, quality, mark: marks[n] || null };
  });
  return { name: "July 2026", startWeekday: 3, days }; // 1 Jul 2026 is a Wednesday (idx 3, Sun=0)
}
const MONTH = buildMonth();
(window as any).MONTH = MONTH;

// A tapped calendar day → why + that day's good times (backend fills; demo generator).
function dayDetail(n: number) {
  const d = MONTH.days[n - 1] || MONTH.days[0];
  const why = d.quality === "good" ? "The Moon sits kindly for you, and no rough angles cut across the day."
    : d.quality === "low" ? "A heavier angle passes overhead, so it's a day to keep low-key."
    : "A mixed day, bright in parts and slow in others. Lean on the good hours.";
  return { ...d, why, good: "11:40a – 12:30p", low: "9:00 – 10:30a" };
}
(window as any).dayDetail = dayDetail;

// FIND A GOOD DAY (Muhurat) — pick an event → top few dates + exact times ahead.
const MUHURAT = {
  events: ["Travel", "Buy something", "Start a job", "Start a business", "Sign papers", "Wedding", "Naming", "Invest", "Ask for a raise"],
  // demo results keyed loosely; the backend returns real muhurat windows per event/place.
  results: {
    default: [
      { date: "Sat, 5 Jul", time: "7:20 – 9:05am", note: "the strongest window this week" },
      { date: "Tue, 8 Jul", time: "11:48am – 12:36pm", note: "short but very clean" },
      { date: "Fri, 11 Jul", time: "4:10 – 5:40pm", note: "good, with the Moon on your side" },
    ],
  },
};
(window as any).MUHURAT = MUHURAT;

// CHECK MY PLANS (Calendar Doctor) — reads upcoming events, flags weak-window ones, offers
// a better slot. Demo events (the real app reads the phone calendar with permission).
const CAL_DOCTOR = [
  { title: "Salary talk with boss", when: "Today, 9:40am", status: "weak", why: "sits in a hold-off stretch", better: "move to 11:50am" },
  { title: "Coffee with Riya", when: "Today, 5:00pm", status: "ok", why: "a warm, easy window", better: null },
  { title: "Sign the lease", when: "Tomorrow, 4:30pm", status: "weak", why: "a tired part of the day", better: "move to 8:30am" },
  { title: "Gym", when: "Tomorrow, 7:00am", status: "ok", why: "fine for everyday things", better: null },
];
(window as any).CAL_DOCTOR = CAL_DOCTOR;

// ASK THE MOMENT — one-shot oracle. Sample questions double as a guide.
const ASK_MOMENT = {
  samples: ["Will I get the job?", "Should I send this text?", "Should I take the offer?"],
  // demo answers; the real app casts a chart for the exact instant.
  answers: [
    { verdict: "Yes", why: "The hour leans your way, and the Moon backs a clear move right now." },
    { verdict: "Wait", why: "A passing angle muddies this moment. Give it an hour and ask again." },
    { verdict: "Lean B", why: "The second path sits in a cleaner part of the sky for you today." },
  ],
};
(window as any).ASK_MOMENT = ASK_MOMENT;

// TIME CAPSULE — write to your future self; the sky delivers it. Moments + demo shelf.
const TIME_CAPSULE = {
  moments: ["your next birthday", "your next Dasha chapter", "the next time Jupiter favours you"],
  shelf: [
    { note: "Remember why you started this.", to: "your next birthday", on: "14 Aug 2026", state: "sealed" as const },
    { note: "You were braver than you thought.", to: "a hard day last spring", on: "20 Mar 2026", state: "landed" as const },
  ],
};
(window as any).TIME_CAPSULE = TIME_CAPSULE;

~~~

---

## `screens/astro/astro.tsx`  
_274 lines_

~~~tsx
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

~~~

---

## `screens/astro/astro-today.tsx`  
_711 lines_

~~~tsx
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

~~~

---

## `screens/astro/astro-plan.tsx`  
_559 lines_

~~~tsx
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

~~~

---

## `screens/astro/astro-screens.tsx`  
_602 lines_

~~~tsx
// astro-screens.tsx — Chat with the Moon, Diyas wallet, Decode (Readings) hub, tab
// placeholders, the detail sheets (eclipse / ritual / journal / full timing), and the
// AstroApp container that wires navigation + shared balance. ASTROLO-clean language throughout.
;(function () {
const U = (window as any).__astroUI;
const T = (window as any).__astroToday;
const P = (window as any).__astroPlan;
const { useState, useRef, useEffect, aA, PAPER, WASH, INK, INK2, GRAY, HAIR, ORANGE, SANS, SERIF, MONO,
  pill, card, Label, Icon, Flame, GlossIcon, Press, MoodEmblem, MoonGloss, Ganesha, Sheet, MOOD, CYCLE, ECL, MIR, NAME, DATE, DAY_LINE, rise } = U;
const { TopCluster, LivingSkyHeader, MoonFAB, SubTabs, EclipseCard, ReadingCard, LifeAreas, CheckInSheet, CheckInChip, RitualPill, JournalCard, BottomNav } = T;
const { PlanTab, MonthScreen, MuhuratSheet, CalendarDoctorSheet, AskMomentSheet, TimeCapsuleSheet, WhySheet } = P;

// a plain back-button header used by the sub-screens (Chat, Wallet)
function BackBar({ onBack, chip, bal, mood, onWallet }: any) {
  const { accent, accentDeep, glow } = mood;
  return (
    <div style={{ position: "absolute", top: 52, left: 18, right: 18, zIndex: 10, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
      <Press scale={0.9} onClick={onBack}><div style={{ ...pill(999), width: 42, height: 42, display: "flex", alignItems: "center", justifyContent: "center" }}><Icon n="arrowL" s={19} c={INK} /></div></Press>
      {chip && <Press scale={0.94} onClick={onWallet}><div style={{ ...pill(999), padding: "9px 14px", display: "flex", alignItems: "center", gap: 6 }}><Flame s={15} c={glow} /><span style={{ fontFamily: SANS, fontWeight: 800, fontSize: 15, color: INK }}>{bal}</span></div></Press>}
    </div>
  );
}

// ===================== CHAT WITH THE MOON =====================
// A living, proactive conversation. The Moon opens with one of three warm, specific
// openers (a pattern it noticed · a look-back · a gentle nudge), the input really works
// (contextual warm replies + a typing beat), and hard moments get a gentle, safe reply.
const MOON_OPENERS = [
  { kind: "a pattern I noticed", lines: [`Hey ${NAME}. I've been noticing something — you tend to feel lighter on the days you write to me in the morning. Today's a soft one, so maybe start there?`], chips: ["Tell me more", "Maybe later"] },
  { kind: "looking back", lines: [`Hi ${NAME}. A week ago you were dreading that conversation at work. I've been wondering — how did it land?`], chips: ["It went okay", "Still on my mind"] },
  { kind: "just checking in", lines: [`Hey ${NAME}. It's been a couple of quiet days. No agenda, I just wanted you to know I'm here. How are you, really?`], chips: ["I'm alright", "Not my best"] },
];
const REPLY = {
  low: ["That sounds heavy, and I'm glad you told me. You don't have to carry today all at once — just the next hour.", "I hear you. With your Moon where it is right now, these days ask more of you than usual. Go slow, it's allowed.", "Thank you for being honest with me. Let's keep today small and kind. What would feel like a little relief?"],
  high: ["I love hearing that. Hold onto this one — days like this are worth remembering.", "That makes me happy. The sky's with you today, so let it carry you a little further.", "Beautiful. Let yourself enjoy it fully, no guilt attached."],
  ask: ["With the day this tender, I'd wait until late morning — things land softer then.", "It's a mixed moment. You can move ahead, just gently and without forcing it.", "The timing's a little rushed right now. Give it an hour and it eases."],
  warm: ["I'm here. Tell me more whenever you're ready.", "That tracks with how the day's moving. What's underneath it, do you think?", "Mm. Sit with that for a second — I'm not going anywhere.", "I understand. Want to just talk it through, no fixing?"],
};
const DISTRESS = ["kill myself", "end it", "suicide", "don't want to be here", "dont want to be here", "hurt myself", "no reason to live", "can't go on", "cant go on", "want to die", "worthless"];
function pickReply(text: string, i: number) {
  const t = text.toLowerCase();
  if (DISTRESS.some((w) => t.includes(w))) return { safe: true, t: "I'm really glad you told me, and I don't want you to be alone with this. Please reach out to someone who can sit with you right now — in India you can call KIRAN at 1800-599-0019, any time, free. I'm here too, and I'm not going anywhere." };
  if (/\b(low|tired|heavy|sad|down|anxious|stressed|awful|exhausted|lonely|hurt)\b/.test(t)) return { t: REPLY.low[i % REPLY.low.length] };
  if (/\b(good|great|happy|excited|wonderful|amazing|better|grateful|calm)\b/.test(t)) return { t: REPLY.high[i % REPLY.high.length] };
  if (t.includes("?") || /^should i|^is it|^can i|^will /.test(t)) return { t: REPLY.ask[i % REPLY.ask.length] };
  return { t: REPLY.warm[i % REPLY.warm.length] };
}
function ChatScreen({ mood, seed, opener = 0, onBack }: any) {
  const { accent, accentDeep, glow } = mood;
  const op = MOON_OPENERS[opener % MOON_OPENERS.length];
  const seedMsgs = seed ? [{ me: true, t: seed }, { me: false, t: "Good question to bring me. With the day this tender, I'd wait until late morning — the words will land softer then." }] : [];
  const [msgs, setMsgs] = useState<any[]>([
    { me: false, t: op.lines[0], kind: op.kind },
    ...seedMsgs,
  ]);
  const [chips, setChips] = useState<string[]>(seed ? [] : op.chips);
  const [draft, setDraft] = useState("");
  const [typing, setTyping] = useState(false);
  const [listening, setListening] = useState(false);
  const scrollRef = useRef<any>(null);
  const cnt = useRef(0);
  const userSpoke = msgs.some((m: any) => m.me);
  // three-state companion: idle before you speak, thinking while replying, delivered after
  const sageImg = typing ? "chatsage2.png" : (userSpoke ? "chatsage3.png" : "chatsage1.png");
  useEffect(() => { const el = scrollRef.current; if (el) el.scrollTop = el.scrollHeight; }, [msgs, typing]);

  const send = (raw: string) => {
    const text = raw.trim(); if (!text || typing) return;
    setChips([]); setDraft(""); setListening(false);
    setMsgs((m: any[]) => [...m, { me: true, t: text }]);
    setTyping(true);
    const r = pickReply(text, cnt.current++);
    setTimeout(() => { setTyping(false); setMsgs((m: any[]) => [...m, { me: false, t: r.t, safe: r.safe }]); }, 950 + Math.min(text.length * 12, 700));
  };

  return (
    <div style={{ position: "absolute", inset: 0, background: PAPER, display: "flex", flexDirection: "column" }}>
      {/* glowing phase-moon header */}
      <div style={{ paddingTop: 40, paddingBottom: 11, display: "flex", flexDirection: "column", alignItems: "center", borderBottom: `1px solid ${HAIR}`, background: `radial-gradient(120% 90% at 50% -10%, ${aA(glow, 0.16)}, ${aA(glow, 0)} 70%)` }}>
        <Press scale={0.9} onClick={onBack} style={{ position: "absolute", left: 18, top: 48 }}><div style={{ ...pill(999), width: 42, height: 42, display: "flex", alignItems: "center", justifyContent: "center" }}><Icon n="arrowL" s={19} c={INK} /></div></Press>
        <div style={{ position: "relative", width: 92, height: 92, display: "flex", alignItems: "center", justifyContent: "center" }}>
          {/* soft aura */}
          <div style={{ position: "absolute", inset: 8, borderRadius: 999, background: `radial-gradient(circle at 50% 46%, ${aA(glow, 0.4)}, ${aA(glow, 0)} 66%)`, animation: "haloBreathe 5s ease-in-out infinite" }} />
          {/* the sage with the crystal ball */}
          <div style={{ position: "relative", width: 86, height: 87, animation: "floatY 6s ease-in-out infinite" }}>
            {["chatsage1.png", "chatsage2.png", "chatsage3.png"].map((src) => (
              <img key={src} src={src} alt="" draggable={false} style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "contain", filter: `drop-shadow(0 6px 12px ${aA("#1A1408", 0.22)})`, opacity: src === sageImg ? 1 : 0, transition: "opacity .18s ease" }} />
            ))}
          </div>
        </div>
        <div style={{ fontFamily: SERIF, fontSize: 18, fontWeight: 500, color: INK, marginTop: 3 }}>Sage</div>
        <div style={{ fontFamily: SANS, fontSize: 12, color: GRAY, marginTop: 1 }}>your guide · always private</div>
      </div>
      {/* conversation */}
      <div ref={scrollRef} style={{ flex: 1, overflowY: "auto", padding: "18px 18px 8px", display: "flex", flexDirection: "column", gap: 11, scrollBehavior: "smooth" }}>
        {msgs.map((m: any, i: number) => (
          <div key={i} style={{ alignSelf: m.me ? "flex-end" : "flex-start", maxWidth: "83%", animation: `riseIn .45s ease both` }}>
            {m.kind && <div style={{ fontFamily: MONO, fontSize: 9.5, letterSpacing: 1, textTransform: "uppercase", color: aA(accentDeep, 0.85), marginBottom: 5, marginLeft: 4, display: "flex", alignItems: "center", gap: 5 }}><span style={{ width: 4, height: 4, borderRadius: 999, background: glow, boxShadow: `0 0 5px ${glow}` }} />{m.kind}</div>}
            <div style={m.me
              ? { background: INK, color: "#FFF", borderRadius: "20px 20px 6px 20px", padding: "11px 15px", fontFamily: SANS, fontSize: 14.5, lineHeight: 1.45, fontWeight: 500 }
              : m.safe
                ? { background: aA(accent, 0.08), border: `1px solid ${aA(accent, 0.3)}`, borderRadius: "20px 20px 20px 6px", padding: "13px 16px", color: INK, fontFamily: SERIF, fontSize: 15.5, lineHeight: 1.5 }
                : { ...pill(20), borderRadius: "20px 20px 20px 6px", padding: "12px 16px", color: INK, fontFamily: SERIF, fontSize: 15.5, lineHeight: 1.45 }}>{m.t}</div>
          </div>
        ))}
        {typing && (<div style={{ alignSelf: "flex-start", ...pill(20), borderRadius: "20px 20px 20px 6px", padding: "13px 17px", display: "flex", gap: 5, animation: "riseIn .3s ease both" }}>
          {[0, 1, 2].map((d) => (<div key={d} style={{ width: 6, height: 6, borderRadius: 999, background: aA(INK, 0.4), animation: `blink 1.2s ease-in-out ${d * 0.18}s infinite` }} />))}
        </div>)}
        {chips.length > 0 && !typing && (<div style={{ alignSelf: "flex-start", display: "flex", gap: 8, marginTop: 2, flexWrap: "wrap", animation: "riseIn .5s ease .2s both" }}>
          {chips.map((c) => (<Press key={c} scale={0.95} onClick={() => send(c)}><div style={{ padding: "8px 14px", borderRadius: 999, background: "#FFF", border: `1px solid ${aA(accentDeep, 0.3)}`, fontFamily: SANS, fontSize: 13, fontWeight: 700, color: accentDeep }}>{c}</div></Press>))}
        </div>)}
      </div>
      {/* input */}
      <div style={{ padding: "6px 16px 26px" }}>
        {listening && (<div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 6, marginBottom: 9, animation: "fadeIn .3s ease both" }}>
          {[0, 1, 2, 3, 4].map((b) => (<div key={b} style={{ width: 3, borderRadius: 999, background: accentDeep, height: 8 + (b % 3) * 7, animation: `sound 0.9s ease-in-out ${b * 0.12}s infinite` }} />))}
          <span style={{ fontFamily: SANS, fontSize: 12, color: accentDeep, fontStyle: "italic", marginLeft: 4 }}>listening…</span>
        </div>)}
        <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "5px 6px 5px 16px", ...pill(999) }}>
          <input value={draft} onChange={(e: any) => setDraft(e.target.value)} onKeyDown={(e: any) => { if (e.key === "Enter") send(draft); }} placeholder="Tell Sage…" style={{ flex: 1, border: "none", outline: "none", background: "transparent", fontFamily: SANS, fontSize: 14.5, color: INK, padding: "9px 0" }} />
          <Press scale={0.9} onClick={() => setListening((v) => !v)}><div style={{ width: 38, height: 38, borderRadius: 999, flexShrink: 0, display: "flex", alignItems: "center", justifyContent: "center", background: listening ? accentDeep : aA(accent, 0.12) }}><Icon n="mic" s={18} c={listening ? "#FFF" : accentDeep} sw={1.8} /></div></Press>
          <Press scale={0.9} onClick={() => send(draft)}><div style={{ width: 38, height: 38, borderRadius: 999, flexShrink: 0, display: "flex", alignItems: "center", justifyContent: "center", background: draft.trim() ? INK : aA(INK, 0.35) }}><Icon n="send" s={17} c="#FFF" sw={1.8} /></div></Press>
        </div>
      </div>
    </div>
  );
}

// ===================== DIYAS WALLET =====================
function WalletScreen({ mood, bal, onBack }: any) {
  const { accent, accentDeep, glow } = mood;
  const bright = Math.min(1, 0.4 + bal / 500);
  const earn = [["Daily check-in", "+1", true], ["Today's ritual", "+2", false], ["A journal note", "+1", false], ["7-day streak", "+10", false], ["Invite a friend", "+25", false]];
  const buy = [["Glow", "₹99", "110", false], ["Blaze", "₹299", "380", true], ["Festival", "₹799", "1,150", false]];
  const hist = [["Today's ritual", "+2"], ["Daily check-in", "+1"], ["Full Life Reading", "−60"], ["7-day streak", "+10"], ["Compatibility unlock", "−30"]];
  return (
    <div style={{ position: "absolute", inset: 0, background: PAPER, overflowY: "auto" }}>
      <BackBar onBack={onBack} mood={mood} />
      <div style={{ padding: "104px 18px 40px" }}>
        {/* hero */}
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", marginBottom: 24, ...rise(0) }}>
          <div style={{ position: "relative", width: 92, height: 92, display: "flex", alignItems: "center", justifyContent: "center" }}>
            <div style={{ position: "absolute", inset: -14, borderRadius: 999, "--gc": aA(glow, 0.3 + bright * 0.4), animation: "glowPulse 4s ease-in-out infinite" } as any} />
            <div style={{ animation: "floatY 5s ease-in-out infinite" }}><Flame s={64} c={glow} /></div>
          </div>
          <div style={{ display: "flex", alignItems: "baseline", gap: 8, marginTop: 8 }}><span style={{ fontFamily: SERIF, fontSize: 52, fontWeight: 600, color: INK, letterSpacing: -1.5 }}>{bal}</span><span style={{ fontFamily: SERIF, fontStyle: "italic", fontSize: 22, color: accentDeep }}>🪔 lit</span></div>
        </div>
        {/* earn */}
        <div style={{ ...card({ padding: "16px 18px", marginBottom: 14 }), ...rise(80) }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 4 }}><Label c={aA(accentDeep, 0.9)}>Light a diya by doing good</Label><span style={{ fontFamily: SANS, fontSize: 11, fontWeight: 700, color: GRAY }}>3 of 5 today</span></div>
          {earn.map(([l, amt, done]: any, i) => (
            <div key={i} style={{ display: "flex", alignItems: "center", gap: 12, padding: "11px 0", borderTop: i ? `1px solid ${HAIR}` : "none" }}>
              <div style={{ width: 26, height: 26, borderRadius: 999, flexShrink: 0, display: "flex", alignItems: "center", justifyContent: "center", background: done ? aA(accent, 0.14) : WASH, border: `1px solid ${done ? aA(accent, 0.3) : HAIR}` }}>{done ? <Icon n="check" s={13} c={accentDeep} sw={2.4} /> : <Flame s={12} c={glow} />}</div>
              <span style={{ flex: 1, fontFamily: SANS, fontSize: 14, fontWeight: 600, color: done ? GRAY : INK, textDecoration: done ? "line-through" : "none" }}>{l}</span>
              <span style={{ fontFamily: MONO, fontSize: 12.5, fontWeight: 600, color: done ? GRAY : accentDeep }}>{amt}</span>
            </div>
          ))}
        </div>
        {/* buy */}
        <div style={{ marginBottom: 14, ...rise(140) }}>
          <div style={{ paddingLeft: 4, marginBottom: 9 }}><Label>Buy diyas</Label></div>
          <div style={{ display: "flex", gap: 10 }}>
            {buy.map(([n, p, coins, best]: any) => (
              <div key={n} style={{ flex: 1, position: "relative", ...pill(18), padding: "16px 8px", display: "flex", flexDirection: "column", alignItems: "center", gap: 6, border: `1px solid ${best ? aA(accent, 0.5) : aA("#000", 0.05)}` }}>
                {best && <div style={{ position: "absolute", top: -8, left: "50%", transform: "translateX(-50%)", whiteSpace: "nowrap", padding: "2px 8px", borderRadius: 999, background: accentDeep }}><span style={{ fontFamily: MONO, fontSize: 8, fontWeight: 600, letterSpacing: 0.5, textTransform: "uppercase", color: "#FFF" }}>best value</span></div>}
                <Flame s={20} c={glow} /><span style={{ fontFamily: SANS, fontSize: 14, fontWeight: 800, color: INK }}>{n}</span>
                <span style={{ fontFamily: SERIF, fontSize: 17, fontWeight: 600, color: INK }}>{coins}🪔</span>
                <div style={{ marginTop: 2, padding: "6px 0", width: "100%", borderRadius: 10, background: INK, textAlign: "center" }}><span style={{ fontFamily: SANS, fontSize: 12, fontWeight: 700, color: "#FFF" }}>{p}</span></div>
              </div>
            ))}
          </div>
        </div>
        {/* go plus — dark glossy */}
        <div style={{ borderRadius: 22, overflow: "hidden", position: "relative", background: `linear-gradient(155deg, #211B12, #0C0B0A)`, padding: "20px 20px 18px", marginBottom: 14, boxShadow: `0 18px 40px -20px ${aA("#000", 0.6)}`, ...rise(200) }}>
          <div style={{ position: "absolute", top: -40, right: -30, width: 160, height: 160, borderRadius: 999, background: `radial-gradient(circle, ${aA(glow, 0.4)}, ${aA(glow, 0)} 70%)` }} />
          <Label c={glow}>ASTROLO Plus</Label>
          <div style={{ fontFamily: SERIF, fontSize: 21, fontWeight: 500, color: "#FBF4E8", marginTop: 9, lineHeight: 1.3 }}>Unlimited chat, every Pattern, 25% off everything.</div>
          <div style={{ fontFamily: SANS, fontSize: 12.5, color: aA("#FBF4E8", 0.6), marginTop: 8 }}>couple, family & deep Patterns · cross-reference free</div>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginTop: 16 }}>
            <div style={{ display: "flex", alignItems: "baseline", gap: 5 }}><span style={{ fontFamily: SERIF, fontSize: 24, fontWeight: 600, color: "#FBF4E8" }}>₹199</span><span style={{ fontFamily: SANS, fontSize: 11, color: aA("#FBF4E8", 0.5) }}>/mo</span></div>
            <Press scale={0.95}><div style={{ padding: "10px 16px", borderRadius: 999, background: glow }}><span style={{ fontFamily: SANS, fontSize: 13, fontWeight: 800, color: "#211B12" }}>7-day free trial</span></div></Press>
          </div>
        </div>
        {/* history */}
        <div style={{ ...card({ padding: "16px 18px" }), ...rise(260) }}>
          <div style={{ marginBottom: 4 }}><Label>History</Label></div>
          {hist.map(([w, amt]: any, i) => (
            <div key={i} style={{ display: "flex", alignItems: "center", gap: 10, padding: "11px 0", borderTop: i ? `1px solid ${HAIR}` : "none" }}>
              <span style={{ flex: 1, fontFamily: SANS, fontSize: 14, fontWeight: 600, color: INK }}>{w}</span>
              <span style={{ fontFamily: MONO, fontSize: 13, fontWeight: 600, color: (amt[0] === "+") ? accentDeep : GRAY }}>{amt}</span>
              <Flame s={12} c={(amt[0] === "+") ? glow : GRAY} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ===================== DECODE (Readings hub) =====================
const RASHI_GLYPH: any = { Cancer: "♋", Libra: "♎", Aries: "♈", Taurus: "♉", Gemini: "♊", Leo: "♌", Virgo: "♍", Scorpio: "♏", Sagittarius: "♐", Capricorn: "♑", Aquarius: "♒", Pisces: "♓" };
function DecodeScreen({ mood, bal, onWallet, onProfile, onBell }: any) {
  const { accent, accentDeep, glow } = mood;
  const Section = ({ children }: any) => (<div style={{ margin: "26px 2px 11px" }}><Label>{children}</Label></div>);
  const Row = ({ glyph, title, sub, price }: any) => (
    <Press scale={0.985} style={{ marginBottom: 10 }}>
      <div style={{ ...pill(18), padding: "13px 15px", display: "flex", alignItems: "center", gap: 13 }}>
        <GlossIcon c1={glow} c2={accentDeep} size={42} radius={13}><span style={{ fontSize: 19, color: "#FFF" }}>{glyph}</span></GlossIcon>
        <div style={{ flex: 1 }}><div style={{ fontFamily: SERIF, fontSize: 16.5, fontWeight: 500, color: INK }}>{title}</div><div style={{ fontFamily: SANS, fontSize: 12, color: GRAY, marginTop: 1 }}>{sub}</div></div>
        {price ? (<div style={{ display: "flex", alignItems: "center", gap: 3, padding: "5px 10px", borderRadius: 999, background: aA(accent, 0.1), border: `1px solid ${aA(accent, 0.24)}` }}><Flame s={11} c={glow} /><span style={{ fontFamily: MONO, fontSize: 11.5, fontWeight: 600, color: accentDeep }}>{price}</span></div>) : <Icon n="chevR" s={16} c={GRAY} />}
      </div>
    </Press>
  );
  const tools = [["✦", "Numerology", "your numbers", "#7B7FD0", "#5C60AE"], ["☍", "Palmistry", "read your palm", "#2E9C7E", "#1F7660"], ["◑", "Face Reading", "read your face", "#D06A8C", "#AC4E6E"], ["✷", "Tarot", "pull a card", "#E0982A", "#B5781A"]];
  return (
    <div style={{ position: "absolute", inset: 0, background: PAPER, overflowY: "auto" }}>
      <div style={{ position: "absolute", top: 52, left: 18, right: 18, zIndex: 10 }}><TopCluster mood={mood} bal={bal} bump={0} alert={true} onProfile={onProfile} onWallet={onWallet} onBell={onBell} /></div>
      <div style={{ padding: "108px 18px 130px" }}>
        <div style={rise(0)}>
          <Label c={aA(accentDeep, 0.9)}>Readings & Tools</Label>
          <div style={{ fontFamily: SERIF, fontSize: 32, fontWeight: 500, color: INK, letterSpacing: -0.8, marginTop: 3 }}>Decode</div>
          <div style={{ fontFamily: SERIF, fontStyle: "italic", fontSize: 15, color: GRAY, marginTop: 4 }}>Everything your chart can tell you, in one place.</div>
        </div>
        {/* kundli anchor */}
        <div style={{ ...card({ padding: 20, marginTop: 18 }), ...rise(80) }}>
          <div style={{ display: "flex", gap: 16, alignItems: "center" }}>
            <div style={{ width: 72, height: 72, borderRadius: 999, flexShrink: 0, position: "relative", overflow: "hidden", background: `linear-gradient(155deg, ${glow}, ${accent} 55%, ${accentDeep})`, boxShadow: `inset 0 1px 2px ${aA("#FFF", 0.5)}, 0 8px 20px -6px ${aA(accentDeep, 0.6)}`, display: "flex", alignItems: "center", justifyContent: "center", animation: "floatY 5s ease-in-out infinite" }}>
              <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: "46%", background: `linear-gradient(180deg, ${aA("#FFF", 0.4)}, ${aA("#FFF", 0)})` }} />
              <span style={{ fontSize: 34, color: "#FFFDF8", lineHeight: 1 }}>{RASHI_GLYPH.Cancer}</span>
            </div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <Label c={aA(accentDeep, 0.9)}>Your kundli</Label>
              <div style={{ fontFamily: SERIF, fontSize: 21, fontWeight: 500, color: INK, marginTop: 3 }}>{NAME}</div>
              <div style={{ fontFamily: SANS, fontSize: 12, color: GRAY, marginTop: 2 }}>14 Aug 1998 · 4:20 am · Jaipur</div>
              <Press scale={0.96} style={{ display: "inline-block", marginTop: 11 }}><div style={{ display: "flex", alignItems: "center", gap: 6 }}><span style={{ fontFamily: SANS, fontSize: 12.5, fontWeight: 700, color: accentDeep }}>Open full chart</span><Icon n="arrowR" s={13} c={accentDeep} sw={2} /></div></Press>
            </div>
          </div>
          <div style={{ display: "flex", gap: 8, marginTop: 16, paddingTop: 15, borderTop: `1px solid ${HAIR}` }}>
            {[["Lagna", "Libra", "ascendant"], ["Rashi", "Cancer", "moon sign"], ["Nakshatra", "Pushya", "birth star"]].map(([k, v, sub]) => (
              <div key={k} style={{ flex: 1, textAlign: "center" }}>
                <div style={{ fontFamily: MONO, fontSize: 8.5, fontWeight: 600, letterSpacing: 0.6, textTransform: "uppercase", color: accentDeep }}>{k}</div>
                <div style={{ fontFamily: SERIF, fontSize: 16.5, fontWeight: 500, color: INK, marginTop: 3 }}>{v}</div>
                <div style={{ fontFamily: SANS, fontSize: 9.5, color: GRAY, marginTop: 1 }}>{sub}</div>
              </div>
            ))}
          </div>
        </div>
        <Section>In-depth readings</Section>
        <Row glyph="✦" title="Full Life Reading" sub="your whole chart, read in depth" price="60" />
        <Row glyph="❤" title="Marriage Reading" sub="love, timing, and the person" price="60" />
        <Row glyph="✶" title="Career & Purpose" sub="where your work wants to go" price="45" />
        <Section>Matching & timing</Section>
        <Row glyph="⚯" title="Kundli Matching" sub="check two charts together" />
        <Row glyph="☼" title="Auspicious Days" sub="find a good day to begin" />
        <Section>Explore yourself</Section>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 10 }}>
          {tools.map(([g, t, sub, c1, c2]: any) => (
            <Press key={t} scale={0.97} style={{ width: "calc(50% - 5px)" }}>
              <div style={{ ...pill(18), padding: 16, boxSizing: "border-box" }}>
                <GlossIcon c1={c1} c2={c2} size={38} radius={12}><span style={{ fontSize: 18, color: "#FFF" }}>{g}</span></GlossIcon>
                <div style={{ fontFamily: SERIF, fontSize: 16, fontWeight: 500, color: INK, marginTop: 11 }}>{t}</div>
                <div style={{ fontFamily: SANS, fontSize: 11.5, color: GRAY, marginTop: 1 }}>{sub}</div>
              </div>
            </Press>
          ))}
        </div>
        <div style={{ textAlign: "center", fontFamily: SERIF, fontStyle: "italic", fontSize: 13.5, color: GRAY, marginTop: 16 }}>Try each once for free, then they cost a few Diyas.</div>
      </div>
    </div>
  );
}

// ===================== tab placeholder =====================
function Placeholder({ mood, label, bal, onProfile, onWallet, onBell }: any) {
  const { accent, accentDeep, glow } = mood;
  return (
    <div style={{ position: "absolute", inset: 0, background: PAPER }}>
      <div style={{ position: "absolute", top: 52, left: 18, right: 18, zIndex: 10 }}><TopCluster mood={mood} bal={bal} bump={0} alert={true} onProfile={onProfile} onWallet={onWallet} onBell={onBell} /></div>
      <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 14 }}>
        <MoodEmblem mood={mood} size={64} />
        <div style={{ fontFamily: SERIF, fontSize: 26, fontWeight: 500, color: INK }}>{label}</div>
        <div style={{ fontFamily: SANS, fontSize: 14, color: GRAY }}>coming soon</div>
      </div>
    </div>
  );
}

// ===================== detail sheets =====================
function EclipseSheet({ mood, type }: any) {
  const { accentDeep } = mood;
  const t = type || ECL.type;
  const sanskrit = t === "solar" ? "सूर्य ग्रहण" : "चन्द्र ग्रहण";
  return (<div>
    <Label c={aA(accentDeep, 0.9)}>Heads up</Label>
    <div style={{ fontFamily: SERIF, fontSize: 24, fontWeight: 500, color: INK, marginTop: 6 }}>A {t} eclipse on {ECL.date}</div>
    <div style={{ fontFamily: SERIF, fontSize: 16, lineHeight: 1.5, color: INK2, marginTop: 12, textWrap: "pretty" } as any}>{ECL.full ? ECL.full[t] : ""}</div>
    <div style={{ marginTop: 16, padding: 15, borderRadius: 14, background: WASH }}><Label>Caution window</Label><div style={{ fontFamily: SANS, fontSize: 13.5, lineHeight: 1.5, color: INK2, marginTop: 6 }}>The Sutak window begins about {ECL.sutakHours} hours before, around {ECL.sutakDate}, {ECL.sutakTime}.</div></div>
    <div style={{ textAlign: "center", marginTop: 14, fontFamily: SERIF, fontSize: 16, color: GRAY }}>{sanskrit}</div>
  </div>);
}
function RitualSheet({ mood, onDone }: any) {
  const { accent, accentDeep } = mood;
  const steps = ["Find a small lamp or candle as the light fades.", "Light it, and sit for a moment.", "Breathe slowly for one minute, eyes soft.", "When you're ready, let the day go."];
  return (<div>
    <Label c={aA(accentDeep, 0.9)}>Today's ritual</Label>
    <div style={{ fontFamily: SERIF, fontSize: 22, fontWeight: 500, color: INK, marginTop: 6 }}>Light a lamp at dusk</div>
    <div style={{ display: "flex", flexDirection: "column", gap: 10, marginTop: 16 }}>
      {steps.map((s, i) => (<div key={i} style={{ display: "flex", gap: 12, alignItems: "flex-start" }}><div style={{ width: 24, height: 24, flexShrink: 0, borderRadius: 999, background: aA(accent, 0.12), border: `1px solid ${aA(accent, 0.3)}`, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: MONO, fontSize: 11, fontWeight: 600, color: accentDeep }}>{i + 1}</div><span style={{ fontFamily: SERIF, fontSize: 15.5, lineHeight: 1.45, color: INK }}>{s}</span></div>))}
    </div>
    <Press scale={0.97} onClick={onDone} style={{ marginTop: 20 }}><div style={{ padding: "14px 0", borderRadius: 14, textAlign: "center", background: INK, boxShadow: `0 10px 20px -8px ${aA(INK, 0.5)}` }}><span style={{ fontFamily: SANS, fontSize: 14.5, fontWeight: 700, color: "#FFF" }}>Done · +2 diyas</span></div></Press>
  </div>);
}
// short Work / Money sheet (a placeholder for the fuller "Path" later)
// single-area sheet — Love / Work / Money alike. Adds the fuller "what it means today",
// a plain-astrology "why?", and ONE contextual link (only because its tab exists).
function AreaSheet({ mood, area, onGo }: any) {
  const { accent, accentDeep, glow } = mood;
  const la = ((window as any).LIFE_AREAS || {})[mood.key] || {};
  const meta = ((window as any).LIFE_AREA_META || {})[area] || {};
  const line = area === "Love" ? la.love : area === "Work" ? la.work : la.money;
  const col = area === "Love" ? ["#E48AA6", "#C55C7E"] : area === "Work" ? ["#6E86C4", "#4C63A0"] : ["#5FA97E", "#3E8060"];
  const ic = area === "Love" ? "heart" : area === "Work" ? "work" : "coin";
  const [why, setWhy] = useState(false);
  return (<div>
    <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
      <GlossIcon c1={col[0]} c2={col[1]} size={40} radius={13}><Icon n={ic} s={19} c="#FFF" sw={1.9} /></GlossIcon>
      <div>
        <div style={{ display: "flex", alignItems: "baseline", gap: 8 }}>
          <span style={{ fontFamily: SERIF, fontSize: 23, fontWeight: 500, color: INK, letterSpacing: -0.3 }}>{area} today</span>
          <span style={{ fontFamily: MONO, fontSize: 10, letterSpacing: 0.7, textTransform: "uppercase", color: accentDeep }}>· {meta.planet}</span>
        </div>
        <div style={{ fontFamily: MONO, fontSize: 9.5, letterSpacing: 0.5, textTransform: "uppercase", color: GRAY, marginTop: 2 }}>{meta.houses} house</div>
      </div>
    </div>

    <div style={{ fontFamily: SERIF, fontSize: 17, lineHeight: 1.5, color: INK, marginTop: 16, textWrap: "pretty" } as any}>{line}</div>
    <div style={{ fontFamily: SANS, fontSize: 10.5, letterSpacing: 1, textTransform: "uppercase", color: GRAY, margin: "18px 0 7px" }}>What it means today</div>
    <div style={{ fontFamily: SERIF, fontSize: 15.5, lineHeight: 1.62, color: INK2, textWrap: "pretty" } as any}>{meta.detail}</div>

    {/* plain-astrology why?, inline accordion */}
    <Press scale={0.98} onClick={() => setWhy((w: boolean) => !w)} style={{ marginTop: 18 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 7, padding: "10px 13px", borderRadius: 12, background: aA(accentDeep, 0.06), border: `1px solid ${aA(accentDeep, 0.14)}`, width: "fit-content" }}>
        <span style={{ fontFamily: SANS, fontSize: 13, fontWeight: 700, color: accentDeep }}>why?</span>
        <div style={{ transform: why ? "rotate(180deg)" : "none", transition: "transform .25s", display: "flex" }}><Icon n="chevD" s={13} c={accentDeep} /></div>
      </div>
    </Press>
    <div style={{ maxHeight: why ? 200 : 0, opacity: why ? 1 : 0, overflow: "hidden", transition: "max-height .35s ease, opacity .3s ease" }}>
      <div style={{ fontFamily: SERIF, fontStyle: "italic", fontSize: 14.5, lineHeight: 1.6, color: GRAY, marginTop: 12, textWrap: "pretty" } as any}>{meta.why}</div>
    </div>

    {/* ONE contextual link, only because this tab exists */}
    {meta.link && (
      <Press scale={0.98} onClick={() => onGo(meta.link.tab)} style={{ marginTop: 22 }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "14px 16px", borderRadius: 14, background: `linear-gradient(150deg, ${aA(accent, 0.1)}, ${aA(glow, 0.04)})`, border: `1px solid ${aA(accent, 0.22)}` }}>
          <span style={{ fontFamily: SANS, fontSize: 14, fontWeight: 700, color: INK }}>{meta.link.label}</span>
          <Icon n="chevR" s={16} c={accentDeep} />
        </div>
      </Press>
    )}
  </div>);
}

// warm notifications — its own screen, opened from the top-bar bell
function NotifScreen({ mood, onBack }: any) {
  const { accent, accentDeep, glow } = mood;
  const items = [
    { ic: "moon", c1: glow, c2: accentDeep, t: "I've been thinking about you", s: "a small pattern from your last few days", now: "just now", unread: true, grp: "New" },
    { ic: "clock", c1: "#6E86C4", c2: "#4C63A0", t: "Your strong window opens at 11:40", s: "good for the pitch you noted", now: "2h ago", unread: true, grp: "New" },
    { ic: "flame", c1: "#D98A2B", c2: "#B26C18", t: "12-day streak, gently held", s: "check in today to keep it warm", now: "5h ago", unread: false, grp: "Earlier" },
  ];
  const groups = ["New", "Earlier"];
  return (
    <div style={{ position: "absolute", inset: 0, background: PAPER, overflowY: "auto" }}>
      {/* pinned header with back */}
      <div style={{ position: "sticky", top: 0, zIndex: 10, padding: "56px 18px 14px", background: PAPER, display: "flex", alignItems: "center", gap: 13, boxShadow: `0 6px 14px -12px ${aA("#1A1408", 0.35)}` }}>
        <Press scale={0.9} onClick={onBack}><div style={{ width: 40, height: 40, borderRadius: 999, ...pill(999), display: "flex", alignItems: "center", justifyContent: "center" }}><Icon n="arrowL" s={18} c={INK} /></div></Press>
        <div>
          <Label c={aA(accentDeep, 0.9)}>For you</Label>
          <div style={{ fontFamily: SERIF, fontSize: 22, fontWeight: 500, color: INK, marginTop: 1 }}>A few quiet notes</div>
        </div>
      </div>
      <div style={{ padding: "8px 18px 130px" }}>
        {groups.map((g) => { const gi = items.filter((n) => n.grp === g); if (!gi.length) return null; return (
          <div key={g} style={{ marginTop: 18 }}>
            <div style={{ marginBottom: 6 }}><Label>{g}</Label></div>
            <div style={{ ...card({ padding: "4px 16px" }) }}>
              {gi.map((n, i) => (
                <Press key={i} scale={0.99}>
                  <div style={{ display: "flex", alignItems: "flex-start", gap: 13, padding: "14px 0", borderTop: i ? `1px solid ${HAIR}` : "none" }}>
                    <GlossIcon c1={n.c1} c2={n.c2} size={40} radius={13}><Icon n={n.ic} s={18} c="#FFF" sw={1.9} /></GlossIcon>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontFamily: SANS, fontSize: 14.5, fontWeight: 700, color: INK, lineHeight: 1.35, textWrap: "pretty" } as any}>{n.t}</div>
                      <div style={{ fontFamily: SERIF, fontSize: 13.5, color: GRAY, marginTop: 2, lineHeight: 1.4 }}>{n.s}</div>
                      <div style={{ fontFamily: MONO, fontSize: 9.5, letterSpacing: 0.6, textTransform: "uppercase", color: aA(GRAY, 0.8), marginTop: 5 }}>{n.now}</div>
                    </div>
                    {n.unread && <div style={{ width: 8, height: 8, borderRadius: 999, flexShrink: 0, marginTop: 6, background: accent, boxShadow: `0 0 6px ${aA(accent, 0.7)}` }} />}
                  </div>
                </Press>
              ))}
            </div>
          </div>
        ); })}
        <div style={{ textAlign: "center", marginTop: 26, fontFamily: SERIF, fontStyle: "italic", fontSize: 14, color: aA(GRAY, 0.9) }}>that's everything, for now</div>
      </div>
    </div>
  );
}

function JournalScreen({ mood, onBack, onSave, onTalk }: any) {
  const { accent, accentDeep, glow } = mood;
  const [text, setText] = useState(""); const [done, setDone] = useState<string | null>(null);
  const [rec, setRec] = useState(false); const [paused, setPaused] = useState(false); const [secs, setSecs] = useState(0);
  const ph = useRef((MIR.placeholders || ["Say it here."])[0]).current;
  useEffect(() => { if (!rec || paused) return; const id = setInterval(() => setSecs((s) => s + 1), 1000); return () => clearInterval(id); }, [rec, paused]);
  const startRec = () => { setSecs(0); setPaused(false); setRec(true); };
  const sendRec = () => { const vn = "I've been carrying a lot this week, and saying it out loud helps more than I expected."; setText((t) => (t ? t + " " : "") + vn); setRec(false); };
  const mmss = `${String(Math.floor(secs / 60)).padStart(2, "0")}:${String(secs % 60).padStart(2, "0")}`;
  const save = () => { if (!text.trim()) return; setDone((MIR.responses || {}).tender || "Thank you for trusting me with that."); onSave && onSave(); };
  return (
    <div style={{ position: "absolute", inset: 0, background: `linear-gradient(180deg, ${aA(glow, 0.16)} 0%, ${PAPER} 34%, ${PAPER} 100%)`, display: "flex", flexDirection: "column", overflow: "hidden" }}>
      {/* cozy ambient glow, top */}
      <div style={{ position: "absolute", top: -70, left: "50%", marginLeft: -140, width: 280, height: 220, borderRadius: 999, background: `radial-gradient(circle, ${aA(glow, 0.32)}, ${aA(glow, 0)} 70%)`, pointerEvents: "none" }} />
      <div style={{ position: "relative", padding: "54px 18px 8px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <Press scale={0.9} onClick={onBack}><div style={{ ...pill(999), width: 42, height: 42, display: "flex", alignItems: "center", justifyContent: "center" }}><Icon n={done ? "close" : "arrowL"} s={19} c={INK} /></div></Press>
        <Label c={aA(accentDeep, 0.9)}>The Mirror</Label>
        <div style={{ width: 42 }} />
      </div>

      {done ? (
        <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "0 30px", textAlign: "center" }}>
          <div style={{ position: "relative", width: 118, height: 140, animation: "floatY 5s ease-in-out infinite" }}>
            <div style={{ position: "absolute", inset: 18, borderRadius: 999, background: `radial-gradient(circle at 50% 46%, ${aA(glow, 0.36)}, ${aA(glow, 0)} 70%)`, animation: "haloBreathe 6s ease-in-out infinite" }} />
            <img src="sage2.png" alt="" draggable={false} style={{ position: "relative", width: "100%", height: "100%", objectFit: "contain", filter: `drop-shadow(0 6px 14px ${aA("#1A1408", 0.18)})` }} />
          </div>
          <div style={{ fontFamily: SERIF, fontStyle: "italic", fontSize: 22, color: INK, marginTop: 24, lineHeight: 1.5, textWrap: "pretty" } as any}>{done}</div>
          <div style={{ fontFamily: MONO, fontSize: 10, letterSpacing: 1.2, textTransform: "uppercase", color: GRAY, marginTop: 20 }}>you wrote today</div>
          <Press scale={0.97} onClick={() => onTalk("")} style={{ marginTop: 26 }}><div style={{ display: "flex", alignItems: "center", gap: 8, padding: "12px 20px", borderRadius: 999, ...pill(999) }}><span style={{ fontFamily: SANS, fontSize: 14, fontWeight: 700, color: INK }}>talk about it?</span><Icon n="arrowR" s={15} c={accentDeep} sw={2} /></div></Press>
        </div>
      ) : (
        <>
          <div style={{ position: "relative", padding: "14px 22px 0" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 9 }}>
              <div style={{ position: "relative", width: 26, height: 26 }}>
                <svg width="26" height="26" viewBox="0 0 24 24" fill="none"><defs><linearGradient id="jrnCr" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stopColor="#FFF6E4" /><stop offset="1" stopColor={accent} /></linearGradient></defs><path d="M18.4 4.3 A9 9 0 1 0 19.8 16.6 A7 7 0 1 1 18.4 4.3 Z" fill="url(#jrnCr)" /></svg>
              </div>
              <span style={{ fontFamily: MONO, fontSize: 10, letterSpacing: 1.2, textTransform: "uppercase", color: aA(accentDeep, 0.8) }}>{DATE}</span>
            </div>
            <div style={{ fontFamily: SERIF, fontSize: 27, fontWeight: 500, color: INK, letterSpacing: -0.4, marginTop: 12 }}>What's on your mind?</div>
            <div style={{ fontFamily: SERIF, fontStyle: "italic", fontSize: 14.5, color: aA(accentDeep, 0.85), marginTop: 6 }}>no pressure, no one else sees this</div>
          </div>
          {/* cozy ruled page holding the textarea */}
          <div style={{ position: "relative", flex: 1, margin: "16px 18px 0", borderRadius: "20px 20px 0 0", background: "linear-gradient(180deg, #FFFDFB, #FFFBF6)", border: `1px solid ${HAIR}`, borderBottom: "none", boxShadow: `0 -2px 24px -12px ${aA(accentDeep, 0.3)}, inset 0 1px 0 #FFF`, overflow: "hidden" }}>
            <div style={{ position: "absolute", inset: 0, backgroundImage: `repeating-linear-gradient(to bottom, transparent, transparent 33px, ${aA(accentDeep, 0.07)} 33px, ${aA(accentDeep, 0.07)} 34px)`, pointerEvents: "none" }} />
            <textarea autoFocus value={text} onChange={(e: any) => setText(e.target.value)} placeholder={ph} style={{ position: "relative", width: "100%", height: "100%", boxSizing: "border-box", padding: "16px 22px", resize: "none", border: "none", outline: "none", background: "transparent", color: INK, fontFamily: SERIF, fontSize: 18, lineHeight: "34px" }} />
          </div>
          <div style={{ position: "relative", padding: "12px 18px 30px", display: "flex", alignItems: "center", gap: 12, background: "#FFFBF6", borderTop: `1px solid ${HAIR}` }}>
            <Press scale={0.92} onClick={startRec}><div style={{ width: 50, height: 50, borderRadius: 999, flexShrink: 0, display: "flex", alignItems: "center", justifyContent: "center", background: aA(accent, 0.12), border: `1px solid ${aA(accent, 0.3)}` }}><Icon n="mic" s={21} c={accentDeep} sw={1.8} /></div></Press>
            <Press scale={0.98} onClick={save} style={{ flex: 1 }}><div style={{ padding: "15px 0", borderRadius: 999, textAlign: "center", background: text.trim() ? INK : WASH, boxShadow: text.trim() ? `0 10px 20px -8px ${aA(INK, 0.5)}` : "none" }}><span style={{ fontFamily: SANS, fontSize: 14.5, fontWeight: 700, color: text.trim() ? "#FFF" : GRAY }}>Leave it with me</span></div></Press>
          </div>
        </>
      )}

      {/* voice recording overlay */}
      {rec && (
        <div style={{ position: "absolute", inset: 0, zIndex: 20, background: `linear-gradient(180deg, ${aA(accentDeep, 0.14)}, rgba(20,16,12,0.5))`, backdropFilter: "blur(10px)", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", animation: "fadeIn .3s ease both" }}>
          <div style={{ fontFamily: MONO, fontSize: 10.5, letterSpacing: 1.4, textTransform: "uppercase", color: aA("#FFF", 0.75) }}>{paused ? "paused" : "listening"}</div>
          {/* breathing mic halo */}
          <div style={{ position: "relative", width: 116, height: 116, margin: "22px 0 8px", display: "flex", alignItems: "center", justifyContent: "center" }}>
            {!paused && <div style={{ position: "absolute", inset: 0, borderRadius: 999, background: aA(glow, 0.4), animation: "glowPulse 1.8s ease-in-out infinite", ["--gc" as any]: aA(glow, 0.5) } as any} />}
            <div style={{ width: 78, height: 78, borderRadius: 999, background: `radial-gradient(circle at 40% 34%, ${glow}, ${accentDeep})`, display: "flex", alignItems: "center", justifyContent: "center", boxShadow: `0 12px 30px -8px ${aA(accentDeep, 0.7)}` }}><Icon n="mic" s={30} c="#FFF" sw={1.7} /></div>
          </div>
          {/* live waveform */}
          <div style={{ display: "flex", alignItems: "center", gap: 4, height: 40, marginTop: 6 }}>
            {[0.5, 0.8, 0.4, 1, 0.6, 0.9, 0.35, 0.75, 0.55, 0.95, 0.45, 0.7, 0.85].map((h, i) => (
              <div key={i} style={{ width: 4, height: 34, borderRadius: 2, background: aA("#FFF", 0.9), transformOrigin: "center", transform: `scaleY(${h})`, animation: paused ? "none" : `bar ${0.7 + (i % 4) * 0.18}s ease-in-out ${i * 0.05}s infinite` }} />
            ))}
          </div>
          <div style={{ fontFamily: MONO, fontSize: 15, letterSpacing: 1, color: "#FFF", marginTop: 18 }}>{mmss}</div>
          {/* controls: delete · pause/resume · send */}
          <div style={{ display: "flex", alignItems: "center", gap: 22, marginTop: 30 }}>
            <Press scale={0.9} onClick={() => setRec(false)}><div style={{ width: 54, height: 54, borderRadius: 999, display: "flex", alignItems: "center", justifyContent: "center", background: aA("#FFF", 0.14), border: `1px solid ${aA("#FFF", 0.3)}` }}><Icon n="trash" s={21} c="#FFF" sw={1.8} /></div></Press>
            <Press scale={0.92} onClick={() => setPaused((p) => !p)}><div style={{ width: 66, height: 66, borderRadius: 999, display: "flex", alignItems: "center", justifyContent: "center", background: "#FFF", boxShadow: `0 8px 20px -6px ${aA("#000", 0.4)}` }}><Icon n={paused ? "mic" : "pause"} s={26} c={INK} sw={2} /></div></Press>
            <Press scale={0.9} onClick={sendRec}><div style={{ width: 54, height: 54, borderRadius: 999, display: "flex", alignItems: "center", justifyContent: "center", background: `linear-gradient(155deg, ${glow}, ${accentDeep})`, boxShadow: `0 8px 20px -6px ${aA(accentDeep, 0.7)}` }}><Icon n="check" s={23} c="#FFF" sw={2.4} /></div></Press>
          </div>
          <div style={{ display: "flex", gap: 42, marginTop: 11 }}>
            <span style={{ fontFamily: SANS, fontSize: 11, color: aA("#FFF", 0.65) }}>delete</span>
            <span style={{ fontFamily: SANS, fontSize: 11, color: aA("#FFF", 0.65) }}>{paused ? "resume" : "pause"}</span>
            <span style={{ fontFamily: SANS, fontSize: 11, color: aA("#FFF", 0.65) }}>done</span>
          </div>
        </div>
      )}
    </div>
  );
}
function TimingSheet({ mood }: any) {
  const { accentDeep } = mood;
  const wins = [["Best", "11:40a – 12:30p", "important talks", "#3E9C7A"], ["Good", "2:00 – 3:15p", "steady work", accentDeep], ["Neutral", "3:15 – 6:00p", "ordinary tasks", GRAY], ["Ease off", "9:00 – 10:30a", "hold big decisions", "#C9954A"], ["Avoid", "6:30 – 7:15p", "rest, don't push", ORANGE]];
  return (<div>
    <Label c={aA(accentDeep, 0.9)}>Good times today</Label>
    <div style={{ fontFamily: SERIF, fontSize: 22, fontWeight: 500, color: INK, marginTop: 6, marginBottom: 4 }}>The day's windows</div>
    {wins.map(([k, t, note, c]: any, i) => (
      <div key={i} style={{ display: "flex", alignItems: "center", gap: 12, padding: "13px 0", borderTop: i ? `1px solid ${HAIR}` : "none" }}>
        <div style={{ width: 8, height: 8, borderRadius: 999, background: c, flexShrink: 0 }} />
        <div style={{ width: 62, flexShrink: 0 }}><span style={{ fontFamily: MONO, fontSize: 10, fontWeight: 600, letterSpacing: 1, textTransform: "uppercase", color: c }}>{k}</span></div>
        <div style={{ flex: 1 }}><div style={{ fontFamily: SERIF, fontSize: 15.5, color: INK }}>{t}</div><div style={{ fontFamily: SANS, fontSize: 12, color: GRAY }}>{note}</div></div>
      </div>
    ))}
  </div>);
}

// ===================== APP CONTAINER =====================
function AstroApp() {
  const [moodIdx, setMoodIdx] = useState(CYCLE.indexOf("Deep"));
  const mood = MOOD[CYCLE[moodIdx]] || MOOD["Deep"];
  const cycle = () => setMoodIdx((i: number) => (i + 1) % CYCLE.length);
  const [tab, setTab] = useState("Today");          // Today | Timeline | People | Rituals | Readings
  const [sub, setSub] = useState("Read");           // Read | Plan (Today only)
  const [screen, setScreen] = useState<string | null>(null); // chat | wallet | month (full overlay)
  const [sheet, setSheet] = useState<string | null>(null);
  const [areaKey, setAreaKey] = useState("Love");
  const [askSeed, setAskSeed] = useState("");
  const [bal, setBal] = useState(108);
  const [bump, setBump] = useState(0);
  const [wrote, setWrote] = useState(false);
  const [chatSeed, setChatSeed] = useState("");
  const [showEclipse, setShowEclipse] = useState(true);
  const [checkinOpen, setCheckinOpen] = useState(false);   // rises just after first open of the day
  const [checkinDone, setCheckinDone] = useState(false);
  const [eclType, setEclType] = useState(ECL.type || "solar");
  const earn = (n: number) => { setBal((b) => b + n); setBump((k) => k + 1); };
  useEffect(() => { const t = setTimeout(() => setCheckinOpen(true), 650); return () => clearTimeout(t); }, []);

  const goWallet = () => setScreen("wallet");
  const goChat = (seed = "") => { setChatSeed(seed); setSheet(null); setScreen("chat"); };
  const profile = () => {};   // You area not built yet
  const goPlan = () => { setSub("Plan"); };

  // overlay sub-screens (chat / wallet / month) sit above everything
  if (screen === "chat") return (<div style={{ position: "absolute", inset: 0 }}><ChatScreen mood={mood} seed={chatSeed} opener={new Date().getDate() % 3} onBack={() => { setChatSeed(""); setScreen(null); }} /></div>);
  if (screen === "wallet") return (<div style={{ position: "absolute", inset: 0 }}><WalletScreen mood={mood} bal={bal} onBack={() => setScreen(null)} /><MoonFAB mood={mood} insight={true} onTap={() => goChat()} /></div>);
  if (screen === "month") return (<div style={{ position: "absolute", inset: 0 }}><MonthScreen mood={mood} onBack={() => setScreen(null)} /></div>);
  if (screen === "journal") return (<div style={{ position: "absolute", inset: 0 }}><JournalScreen mood={mood} onBack={() => setScreen(null)} onSave={() => { setWrote(true); earn(1); }} onTalk={(q: string) => goChat(q)} /></div>);
  if (screen === "notif") return (<div style={{ position: "absolute", inset: 0 }}><NotifScreen mood={mood} onBack={() => setScreen(null)} /></div>);

  return (
    <div style={{ position: "absolute", inset: 0, background: PAPER, fontFamily: SANS }}>
      {/* ---- TODAY (Read · Plan) ---- */}
      {tab === "Today" && (
        <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column" }}>
          {/* pinned header: cluster + Read/Plan switcher */}
          <div style={{ padding: "56px 18px 12px", background: PAPER, zIndex: 20, boxShadow: `0 6px 14px -10px ${aA("#1A1408", 0.3)}` }}>
            <TopCluster mood={mood} bal={bal} bump={bump} alert={true} onProfile={profile} onWallet={goWallet} onBell={() => setScreen("notif")} />
            <div style={{ marginTop: 14 }}><SubTabs mood={mood} value={sub} onChange={setSub} /></div>
          </div>
          {/* scroll body */}
          <div style={{ flex: 1, overflowY: "auto" }}>
            <div style={{ padding: "10px 18px 130px" }}>
              {sub === "Read" ? (
                <>
                  {!checkinDone && !checkinOpen && <CheckInChip mood={mood} delay={0} onOpen={() => setCheckinOpen(true)} />}
                  <div style={{ marginBottom: 22 }}><LivingSkyHeader mood={mood} delay={40} onBell={() => {}} /></div>
                  {showEclipse && <EclipseCard mood={mood} delay={100} type={eclType} onToggleType={() => setEclType((t: string) => t === "solar" ? "lunar" : "solar")} onOpen={() => setSheet("eclipse")} />}
                  <ReadingCard mood={mood} delay={150} onCycle={cycle} onShare={() => {}} onTiming={goPlan} />
                  <LifeAreas mood={mood} delay={200} onArea={(k: string) => { setAreaKey(k); setSheet("area"); }} />
                  <JournalCard mood={mood} delay={250} written={wrote} onOpen={() => setScreen("journal")} />
                  <RitualPill mood={mood} delay={300} onBegin={() => setTab("Rituals")} />
                </>
              ) : (
                <PlanTab mood={mood} onMonth={() => setScreen("month")} onTool={(k: string, seed = "") => { setAskSeed(seed); setSheet(k); }} />
              )}
            </div>
          </div>
        </div>
      )}
      {tab === "Readings" && <DecodeScreen mood={mood} bal={bal} onWallet={goWallet} onProfile={profile} onBell={() => setScreen("notif")} />}
      {tab === "Timeline" && <Placeholder mood={mood} label="Timeline" bal={bal} onProfile={profile} onWallet={goWallet} onBell={() => setScreen("notif")} />}
      {tab === "People" && <Placeholder mood={mood} label="People" bal={bal} onProfile={profile} onWallet={goWallet} onBell={() => setScreen("notif")} />}
      {tab === "Rituals" && <Placeholder mood={mood} label="Rituals" bal={bal} onProfile={profile} onWallet={goWallet} onBell={() => setScreen("notif")} />}

      {/* floating Moon companion + bottom nav (every tab) */}
      <MoonFAB mood={mood} insight={true} onTap={() => goChat()} />
      <BottomNav mood={mood} active={tab} onTab={(t: string) => { setTab(t); }} />

      {/* the daily check-in POPUP (auto-rises on Today) */}
      <Sheet open={checkinOpen && tab === "Today"} onClose={() => setCheckinOpen(false)}>
        <CheckInSheet mood={mood} onEarn={earn} onClose={(done: boolean) => { setCheckinOpen(false); if (done) setCheckinDone(true); }} />
      </Sheet>

      {/* sheets */}
      <Sheet open={sheet === "eclipse"} onClose={() => setSheet(null)}><EclipseSheet mood={mood} type={eclType} /></Sheet>
      <Sheet open={sheet === "area"} onClose={() => setSheet(null)}><AreaSheet mood={mood} area={areaKey} onGo={(tab: string) => { setSheet(null); setTab(tab); }} /></Sheet>
      <Sheet open={sheet === "muhurat"} onClose={() => setSheet(null)}><MuhuratSheet mood={mood} /></Sheet>
      <Sheet open={sheet === "doctor"} onClose={() => setSheet(null)}><CalendarDoctorSheet mood={mood} /></Sheet>
      <Sheet open={sheet === "ask"} onClose={() => setSheet(null)}><AskMomentSheet mood={mood} seed={askSeed} onTalk={(q: string) => goChat(q)} /></Sheet>
      <Sheet open={sheet === "capsule"} onClose={() => setSheet(null)}><TimeCapsuleSheet mood={mood} /></Sheet>
    </div>
  );
}

(window as any).AstroApp = AstroApp;
})();

~~~
