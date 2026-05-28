import type { Vibe } from './theme';

export type DayForecast = {
  wkd: string;
  dt: number;
  vibe: Vibe;
  word: string;
  line: string;
  op: string;
  caution: string;
  why: string;
  sanskrit: string;
};

export const SEVEN_DAYS: DayForecast[] = [
  {
    wkd: 'Fri', dt: 25, vibe: 'good',
    word: 'Magnetic',
    line: 'People keep finding their way to you. Say the harder thing.',
    op: 'Send the half-finished idea.',
    caution: 'Reply when annoyed.',
    why: "Moon in a warm, expressive star (Magha) + Venus in a sweet angle — warmth radiates and lands well.",
    sanskrit: 'चन्द्रः मघा-नक्षत्रे, शुक्रः त्रिकोणे',
  },
  {
    wkd: 'Sat', dt: 26, vibe: 'good',
    word: 'Rested',
    line: 'A slow morning is doing more for you than a busy one would.',
    op: 'Cook. Call someone. Read.',
    caution: 'Over-plan the day.',
    why: 'Moon trines your natal Jupiter — wide, easy, settled.',
    sanskrit: 'गुरु-त्रिकोणः',
  },
  {
    wkd: 'Sun', dt: 27, vibe: 'good',
    word: 'Open',
    line: 'Easy to be honest today. Two people will notice.',
    op: 'Say the thing you almost said yesterday.',
    caution: 'Mistake softness for weakness.',
    why: 'Venus on your Ascendant — receptive, warm, well-met.',
    sanskrit: 'शुक्रः लग्ने',
  },
  {
    wkd: 'Mon', dt: 28, vibe: 'neutral',
    word: 'Steady',
    line: 'Nothing huge. A good day for finishing the small thing.',
    op: 'Close two open tabs in your week.',
    caution: 'Wait for a sign before acting.',
    why: 'Mercury direct in a stable sign — small admin moves well.',
    sanskrit: 'बुधः स्थिर-राशौ',
  },
  {
    wkd: 'Tue', dt: 29, vibe: 'tough',
    word: 'Edgy',
    line: 'Something small will sting. It will pass.',
    op: 'Walk before you reply.',
    caution: 'Send the message before 4 pm.',
    why: 'Mars on your Moon, fast aspect — a 36-hour edge.',
    sanskrit: 'मङ्गलः चन्द्रे',
  },
  {
    wkd: 'Wed', dt: 30, vibe: 'neutral',
    word: 'Quiet',
    line: 'Take the long way. Talk less than usual.',
    op: 'Be alone for two unhurried hours.',
    caution: 'Big asks. Big announcements.',
    why: 'Moon waning into the reflective house — soft signal day.',
    sanskrit: 'क्षीण-चन्द्रः',
  },
  {
    wkd: 'Thu', dt: 31, vibe: 'good',
    word: 'Clear',
    line: "The fog lifts. Decide the thing you've been turning over.",
    op: 'Pick the harder, truer option.',
    caution: 'Keep waiting for certainty.',
    why: 'Sun-Saturn alignment — sober clarity, durable choices.',
    sanskrit: 'रवि-शनि-योगः',
  },
];

// ─── People ───
export type Person = {
  id: string;
  name: string;
  rel: string;
  weather: string;
  source: 'friend' | 'manual';
  tier: 'close' | 'acquaintance' | '—';
  initials: string;
};

export const PEOPLE: Person[] = [
  { id: 'maya',   name: 'Maya',   rel: 'partner',    weather: 'tender', source: 'friend', tier: 'close',        initials: 'M' },
  { id: 'amma',   name: 'Amma',   rel: 'mother',     weather: 'steady', source: 'friend', tier: 'close',        initials: 'A' },
  { id: 'sam',    name: 'Sam',    rel: 'sister',     weather: 'spicy',  source: 'friend', tier: 'close',        initials: 'S' },
  { id: 'priya',  name: 'Priya',  rel: 'best friend',weather: 'warm',   source: 'friend', tier: 'close',        initials: 'P' },
  { id: 'arjun',  name: 'Arjun',  rel: 'colleague',  weather: 'cool',   source: 'friend', tier: 'acquaintance', initials: 'A' },
  { id: 'rohit',  name: 'Rohit',  rel: 'matchmaking',weather: '—',      source: 'manual', tier: '—',            initials: 'R' },
  { id: 'ishaan', name: 'Ishaan', rel: 'nephew',     weather: '—',      source: 'manual', tier: '—',            initials: 'I' },
];

// ─── Explore tiles ───
export type ExploreTile = {
  id: string;
  title: string;
  sub: string;
  quota: string;
  premium: boolean;
};

export const EXPLORE: ExploreTile[] = [
  { id: 'tarot',      title: 'Pick a card',    sub: 'Quick yes/no for the day', quota: '1/day',  premium: false },
  { id: 'numerology', title: 'Your numbers',   sub: 'What today vibrates at',   quota: 'free',   premium: false },
  { id: 'palm',       title: 'Read your palm', sub: 'Camera scan',              quota: '1 free', premium: true  },
  { id: 'face',       title: 'Read your face', sub: 'Camera scan',              quota: '1 free', premium: true  },
  { id: 'best-time',  title: 'Best time for…', sub: 'Pick event → best dates',  quota: 'free',   premium: false },
];

export const MOST_ASKED = [
  'Is this job change a good move?',
  'Will the trip be safe?',
  'When will I meet someone?',
];
