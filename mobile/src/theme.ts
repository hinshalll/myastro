// theme.ts — ASTROLO design DATA + tokens, ported 1:1 from the web prototype.
// Plain data only, no React. Numbers are unit-less points. The canvas stays white; the
// day's MOOD only tints accents (see src/ui/palette.ts for the visual constants).
//
// Ported verbatim from prototype/screens/astro/theme.ts. Legacy/unused exports from the
// prototype (the ivory THEME object, MOON_CFG/MOON_READING/WATER_SURFACE/MOON_STATIONS —
// never read by the live UI per handoff/PORT-TO-RN.md) are intentionally omitted.

export type MoodKey =
  | "Settled" | "Guarded" | "Bold" | "Tender" | "Restless" | "Capable"
  | "Warm" | "Deep" | "Wandering" | "Driven" | "Upbeat" | "Quiet";

export interface MotionFeel {
  breathe: number;   // sec, sigil breath + glow pulse
  orbit: number;     // sec, base orbital period (smaller = livelier)
  twinkle: number;   // sec, star shimmer base
  spring: number;    // interactive return stiffness multiplier (1 = base)
  wobble: number;    // 0..1 idle wander amplitude
  drag: number;      // wheel spin friction (higher = settles faster)
}
export interface Forecast { mood: string; opportunity: string; caution: string; action: string; why: string; }

export interface Mood {
  key: MoodKey;
  vibe: string;
  accent: string;     // the mood color (chips, glow, diya)
  accentDeep: string; // darker variant for accent text / linework
  glow: string;       // soft luminous tint for halos
  wash: string;       // very faint tint (rgba, ~0.05; legacy, barely used)
  moon: string;       // moon body tint
  feel: MotionFeel;
  forecast: Forecast;
}

// ─────────────────────────────────────────────────────────────────────────────
// DEMO-DATA GUARD — see DEMO_DATA_LEDGER.md
//
// The fakes themselves live in `theme.demo.ts`, which THROWS at import in a production
// build. This file holds only the guard used at call sites, plus the design system.
//
// The danger it fixes: demo data looks exactly like real data. Nothing goes red. Forget to pass
// `live` and the app confidently shows Aarav's chart to a real person and nobody notices — the
// same silent-plausible-wrong failure as the birth_time_known bug. Vigilance does not scale;
// a thrown error does.
//
// prod → throw. An unwired screen must break the build, not lie to a user.
// dev  → keep working (the port stays usable) but SAY SO ON SCREEN. A console.warn is not a
//        giveaway: nobody testing on a phone reads the Metro log, so a silent dev fallback is
//        still a screen quietly telling a lie. Every fallback notifies subscribers, and
//        <DemoBadge/> (ui/DemoBadge.tsx) renders the running list right on top of the app.
// ─────────────────────────────────────────────────────────────────────────────
type DemoListener = (seen: string[]) => void;
const __DEMO_LISTENERS = new Set<DemoListener>();
const __DEMO_WARNED = new Set<string>();   // console: once per key, ever
let __DEMO_CURRENT = new Set<string>();    // what is fake as of the LAST render pass
let __DEMO_PENDING = new Set<string>();    // what this render pass has reported so far
let __DEMO_STICKY = new Set<string>();     // module-load facts; not tied to a render
let __DEMO_FLUSHING = false;

// WHY THE LEDGER IS PER-RENDER, NOT CUMULATIVE.
//
// A card falls back for the ~300ms before loadToday() resolves, then re-renders with the real
// reading. A cumulative ledger counts that flash forever, so the badge sat at "7 FAKE SOURCES"
// while only 2 were still fake. A guard that always screams is a guard nobody reads — it becomes
// wallpaper, and then it is worse than nothing, because it looks like cover.
//
// So each render pass rebuilds the list from scratch: fallbacks that fired this pass are the
// ones actually on screen. React re-renders the whole Read tree when `today` lands, so a slot
// that went live simply stops reporting and drops off. Flushed on a microtask, which is after
// the synchronous render burst but before paint.
function __flushSoon() {
  if (__DEMO_FLUSHING) return;
  __DEMO_FLUSHING = true;
  Promise.resolve().then(() => {
    __DEMO_FLUSHING = false;
    const next = new Set([...__DEMO_STICKY, ...__DEMO_PENDING]);
    __DEMO_PENDING = new Set();
    const changed = next.size !== __DEMO_CURRENT.size || [...next].some((k) => !__DEMO_CURRENT.has(k));
    __DEMO_CURRENT = next;
    if (changed) {
      const snapshot = demoLedger();
      __DEMO_LISTENERS.forEach((fn) => fn(snapshot));
    }
  });
}

function __recordDemo(where: string) {
  __DEMO_PENDING.add(where);
  if (!__DEMO_WARNED.has(where)) {
    __DEMO_WARNED.add(where);
    console.warn(`[Myastro:DEMO] "${where}" is showing FAKE data (no live value passed).`);
  }
  __flushSoon();
}

/**
 * Called by theme.demo.ts at import, so the badge shows even for screens that never fall back.
 * Sticky: a module import is a fact about the BUILD, not about this render, so it can't be
 * rebuilt each pass like a fallback can.
 */
export function markDemoModuleLoaded() {
  __DEMO_STICKY.add("theme.demo module imported");
  __flushSoon();
}

/**
 * Wrap a FALLBACK. Fires only when `live` was absent and we actually fell back to fake data —
 * which is precisely the condition worth screaming about. Prefer this over `live || DEMO`.
 *
 *   const reading = demoFallback("read.reading", live, DEMO_READING);
 *
 * `sticky` for fakes that are a fact about the SESSION rather than about one render — the seed
 * profile is read inside an async loader, not during render, so a per-render ledger would drop
 * it on the next flush while it is still very much fake. Clear it with clearDemoFact() at the
 * moment it stops being true.
 */
export function demoFallback<T>(where: string, live: T | null | undefined, fake: T, opts?: { sticky?: boolean }): T {
  if (live !== null && live !== undefined) return live;
  if (!__DEV__) {
    throw new Error(
      `[Myastro] "${where}" fell back to demo data in a production build (live was missing). ` +
      `Showing fabricated content to a user is never acceptable — render an error state instead.`
    );
  }
  if (opts?.sticky) __DEMO_STICKY.add(where);
  __recordDemo(where);
  return fake;
}

/**
 * Call once at the TOP of the app's render body (AstroApp does).
 *
 * Without this the ledger can only ever grow: __flushSoon fires from __recordDemo, so a pass in
 * which NOTHING falls back schedules no flush at all, and the list from the loading flash sticks
 * forever. That is precisely the pass we care about — it is the good news. This gives the ledger
 * a heartbeat: React renders top-down, so scheduling here means the microtask lands after the
 * whole subtree has reported, and whatever went live simply stops reporting and drops off.
 */
export function demoTick(): void {
  if (__DEV__) __flushSoon();
}

/** The paired release for a sticky fact: call it the moment the thing stops being fake. */
export function clearDemoFact(where: string): void {
  if (!__DEV__) return;
  __DEMO_STICKY.delete(where);
  __DEMO_PENDING.delete(where);
  __DEMO_CURRENT.delete(where);
  const snapshot = demoLedger();
  __DEMO_LISTENERS.forEach((fn) => fn(snapshot));
}

/** Dev helper: what is fake RIGHT NOW (as of the last render pass). */
export function demoLedger(): string[] {
  return [...__DEMO_CURRENT].sort();
}

/** Subscribe to the demo ledger (used by <DemoBadge/>). Returns an unsubscribe. */
export function subscribeDemo(fn: DemoListener): () => void {
  __DEMO_LISTENERS.add(fn);
  return () => { __DEMO_LISTENERS.delete(fn); };
}

// 12 moods, accent + motion personality only. Forecast copy stays warm, plain English.

export const MOODS: Mood[] = [
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

export const MOOD_BY_KEY: Record<string, Mood> = {};
MOODS.forEach((m) => { MOOD_BY_KEY[m.key] = m; });

// The mood-cycle order used by the preview tap + the app container.
export const CYCLE: MoodKey[] = ["Settled", "Bold", "Tender", "Restless", "Capable", "Warm", "Deep", "Wandering", "Driven", "Upbeat", "Quiet", "Guarded"];

// CHECKIN_REFLECTION — compares how the user feels to the DAY'S actual energy (the sky).
const DAY_TONE: Record<string, "low" | "open" | "high"> = {
  Settled: "low", Guarded: "low", Tender: "low", Deep: "low", Quiet: "low",
  Warm: "open", Capable: "open", Wandering: "open",
  Bold: "high", Restless: "high", Driven: "high", Upbeat: "high",
};
export function CHECKIN_REFLECTION(moodSel: string, energySel: string, dayKey: string): string {
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
  if (lowEnergy && day === "low") return "Low, on a slow day. The sky agrees with you, so don't push. Small is enough today.";
  return "Noted. Whatever today holds, you've already done the kind thing by checking in.";
}

