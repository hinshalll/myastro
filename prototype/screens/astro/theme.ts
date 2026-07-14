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
