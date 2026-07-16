// theme.demo.ts — PLACEHOLDER DATA ONLY. Nothing real lives here.
//
// ─────────────────────────────────────────────────────────────────────────────
// READ THIS BEFORE IMPORTING ANYTHING FROM THIS FILE.
//
// Every constant below is fake, ported from the ASTROLO design prototype so unwired
// screens still render during the port. It is Aarav's day, not the user's.
//
// WHY THIS FILE EXISTS AT ALL: demo data looks exactly like real data. Nothing goes
// red. Forget to pass `live` and the app confidently shows a stranger's chart to a
// real person and nobody notices — the same silent/plausible/wrong failure as the
// birth_time_known bug that fabricated a rising sign. Vigilance does not scale. A
// thrown error does.
//
// So: importing this module is ITSELF the error signal.
//   • dev  → works, so the port stays usable, and the app shows a DEMO badge on screen.
//   • prod → throws at startup. An unwired screen breaks the build instead of lying.
//
// That gives us the ledger for free: `grep -rl "theme.demo" src/` IS the list of
// screens that are not wired yet, and it can never drift out of date.
//
// DEFINITION OF DONE for wiring a screen: this import is DELETED from it.
// See DEMO_DATA_LEDGER.md.
// ─────────────────────────────────────────────────────────────────────────────
import { markDemoModuleLoaded } from "./theme";

if (!__DEV__) {
  throw new Error(
    "[Myastro] theme.demo.ts was imported in a production build. Fake placeholder data " +
    "must never ship. Run `grep -rl \"theme.demo\" src/` to see which screens are still " +
    "unwired, wire them against src/api/*, and delete the import. See DEMO_DATA_LEDGER.md."
  );
}
markDemoModuleLoaded();

// ============================ TODAY / READ ============================

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

// PLANETARY HOUR line — the greeting's quiet one-liner for the current hora.
export const HORA_LINE = "a good stretch for money and focus right now";

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

