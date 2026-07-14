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

export const AHEAD = [
  { day: "TUE", date: 17, mood: "Capable",  status: "good"      as const, good: "10:20a", avoid: "4:00p" },
  { day: "WED", date: 18, mood: "Restless", status: "difficult" as const, good: "8:10a",  avoid: "1:30p" },
  { day: "THU", date: 19, mood: "Warm",     status: "good"      as const, good: "11:40a", avoid: "6:15p" },
  { day: "FRI", date: 20, mood: "Quiet",    status: "neutral"   as const, good: "9:00a",  avoid: "3:45p" },
  { day: "SAT", date: 21, mood: "Upbeat",   status: "good"      as const, good: "12:10p", avoid: "7:00p" },
];

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

// DAY_LINE — the warm one-liner in the greeting.
export const DAY_LINE: Record<string, string> = {
  Settled: "A calm, homebound day.", Guarded: "A day to hold a little back.",
  Bold: "A day with some fire in it.", Tender: "A soft, feeling day.",
  Restless: "A busy, restless day.", Capable: "A steady, get-things-done day.",
  Warm: "A warm, social day.", Deep: "A quiet, inward day.",
  Wandering: "An open, drifting day.", Driven: "A focused, push-ahead day.",
  Upbeat: "A light, easy day.", Quiet: "A slow, restful day.",
};

// DAY CLOCK — today's windows from sunrise to sunrise (decimal 6..30 scale).
export const DAY_CLOCK = {
  sunrise: 6,
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

// TODAY AT A GLANCE — the day's almanac in plain words.
export const ALMANAC = {
  nakshatra: "Rohini", nakFlavor: "a warm, settling star",
  tithi: "Shukla Saptami", tithiNote: "the waxing seventh",
  special: "Sarvartha Siddhi", specialNote: "good for new starts",
  festival: null as string | null,
  best90: "4:10 to 5:40pm",
};

// IN FOCUS — set only when one life area is genuinely active today, else null.
export const FOCUS = { area: "Work", to: "Timeline", line: "Work in focus today" } as { area: string; to: string; line: string } | null;

// LIFE AREAS — Love · Work · Money, one honest line each, naming the planet, NO scores.
export const LIFE_AREAS: Record<string, { love: string; work: string; money: string }> = {
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

// LIFE_AREA_META — per-area constants the row's sheet adds on top of the day's line.
export const LIFE_AREA_META: Record<string, { planet: string; houses: string; detail: string; why: string; link: { label: string; tab: string } }> = {
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

// FESTIVAL — a warm one-line wish woven into the header when present, else null.
export const FESTIVAL = null as string | null;

// READING CHIPS — short "good for" / "go easy on" tags per mood (2–3 each).
export const READ_CHIPS: Record<string, { good: string[]; easy: string[]; offDay?: boolean }> = {
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

// PERSONAL_LINES — the app fills this from the user's OWN history. null collapses gracefully.
export const PERSONAL_LINES: Record<string, string> = {
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

// PLANETARY HOUR line — the greeting's quiet one-liner for the current hora.
export const HORA_LINE = "a good stretch for money and focus right now";

// ECLIPSE — the rare "heads up". Backend sends one of these (or null on ordinary days).
export const ECLIPSE: any = {
  type: "solar",
  inDays: 3,
  date: "21 August",
  sutakDate: "20 August",
  sutakTime: "11:30pm",
  sutakHours: 12,
  sanskrit: "सूर्य ग्रहण",
  short: {
    solar: "A good week to pause big new beginnings and keep things low-key.",
    lunar: "A time for rest and gentle routines, since feelings can run high.",
  },
  full: {
    solar: "Traditionally a time to pause new beginnings, keep things low-key, and turn inward.",
    lunar: "Emotions can run high, so it's a time for rest, reflection, and gentle routines.",
  },
};

// MIRROR — the private journal where the user writes to Sage.
export const MIRROR: any = {
  invites: [
    "Anything on your heart tonight?",
    "Tell Sage about your day.",
    "What's sitting with you right now?",
    "How are you, really, tonight?",
    "Anything you want to set down?",
  ],
  placeholders: [
    "Whatever it is, you can say it here. It's just me, and I'm listening.",
    "Start anywhere. There's no right way to do this.",
    "Pour it out. I'm here, and I'm not going anywhere.",
  ],
  responses: {
    heavy:   "That sounds heavy. You don't have to carry it alone tonight.",
    happy:   "I'm glad. Hold onto this one.",
    tender:  "Thank you for trusting me with that. I've got it now.",
    tired:   "You've done enough for today. Let it rest here with me.",
    return:  "You've been here before, and you came through it. You will again.",
  },
  distress: {
    line: "I'm really glad you told me. You matter, and you don't have to sit with this alone.",
    help: "If things feel too heavy, talking to someone can help. KIRAN, a free helpline, is there any time at 1800-599-0019.",
  },
};

// ============================ PLAN TAB DATA ============================
export const PANCHANG_SOON = [
  { day: "Today",    date: "1 Jul", quality: "good"  as const, note: "a settling, homeward day", good: "11:40a–12:30p", low: "9:00–10:30a" },
  { day: "Tomorrow", date: "2 Jul", quality: "mixed" as const, note: "bright morning, tired evening", good: "8:10–9:30a", low: "4:00–5:15p" },
  { day: "Thu",      date: "3 Jul", quality: "low"   as const, note: "a low-key day, keep it light", good: "12:10–1:00p", low: "6:30–7:45p" },
];

// MONTH — a calendar month, each day coloured good/mixed/low, with marks + planned tasks.
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
  return { name: "July 2026", startWeekday: 3, days };
}
export const MONTH = buildMonth();

export function dayDetail(n: number) {
  const d = MONTH.days[n - 1] || MONTH.days[0];
  const why = d.quality === "good" ? "The Moon sits kindly for you, and no rough angles cut across the day."
    : d.quality === "low" ? "A heavier angle passes overhead, so it's a day to keep low-key."
    : "A mixed day, bright in parts and slow in others. Lean on the good hours.";
  return { ...d, why, good: "11:40a – 12:30p", low: "9:00 – 10:30a" };
}

// FIND A GOOD DAY (Muhurat).
export const MUHURAT = {
  events: ["Travel", "Buy something", "Start a job", "Start a business", "Sign papers", "Wedding", "Naming", "Invest", "Ask for a raise"],
  results: {
    default: [
      { date: "Sat, 5 Jul", time: "7:20 – 9:05am", note: "the strongest window this week" },
      { date: "Tue, 8 Jul", time: "11:48am – 12:36pm", note: "short but very clean" },
      { date: "Fri, 11 Jul", time: "4:10 – 5:40pm", note: "good, with the Moon on your side" },
    ],
  },
};

// CHECK MY PLANS (Calendar Doctor).
export const CAL_DOCTOR = [
  { title: "Salary talk with boss", when: "Today, 9:40am", status: "weak", why: "sits in a hold-off stretch", better: "move to 11:50am" },
  { title: "Coffee with Riya", when: "Today, 5:00pm", status: "ok", why: "a warm, easy window", better: null },
  { title: "Sign the lease", when: "Tomorrow, 4:30pm", status: "weak", why: "a tired part of the day", better: "move to 8:30am" },
  { title: "Gym", when: "Tomorrow, 7:00am", status: "ok", why: "fine for everyday things", better: null },
];

// ASK THE MOMENT — one-shot oracle.
export const ASK_MOMENT = {
  samples: ["Will I get the job?", "Should I send this text?", "Should I take the offer?"],
  answers: [
    { verdict: "Yes", why: "The hour leans your way, and the Moon backs a clear move right now." },
    { verdict: "Wait", why: "A passing angle muddies this moment. Give it an hour and ask again." },
    { verdict: "Lean B", why: "The second path sits in a cleaner part of the sky for you today." },
  ],
};

// TIME CAPSULE — write to your future self.
export const TIME_CAPSULE = {
  moments: ["your next birthday", "your next Dasha chapter", "the next time Jupiter favours you"],
  shelf: [
    { note: "Remember why you started this.", to: "your next birthday", on: "14 Aug 2026", state: "sealed" as const },
    { note: "You were braver than you thought.", to: "a hard day last spring", on: "20 Mar 2026", state: "landed" as const },
  ],
};

// Demo identity (backend fills NAME/DATE from the profile + system date on wire-up).
export const NAME = "Aarav";
export const DATE = "Tuesday, 17 June";
