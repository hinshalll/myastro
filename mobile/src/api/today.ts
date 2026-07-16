// today.ts — adapters for the Today → Read tab. Each maps a backend response to the exact
// shape the existing components consume, so the UI stays 1:1 while the DATA becomes real.
//
// Endpoints (all stateless — profile in the body, no auth):
//   /dashboard/today      → the reading + Love/Work/Money (reconciled together)
//   /dashboard/hora       → the header's live "good stretch for…" line + moon phase + festival
//   /dashboard/day-alerts → the eclipse heads-up + the Chandra Sandhi low-window
//   /rituals/today        → today's ritual
import { apiGet, apiPost, hasAuthToken, localDateISO } from "./client";
import { getProfile } from "./profile";
import { getCurrentPlace } from "./place";

// ---------- shapes the components consume ----------
export type LiveArea = {
  tone: string;      // good | mixed | low | steady
  line: string;      // the short row line
  detail: string;    // the sheet body
  why: string;       // the astrology, plain
  planet: string;    // karaka (honest, no score)
  houses: string;    // "7th & 5th" — the domain's significator houses, from the server
  inFocus: boolean;  // is the transiting Moon actually lighting this domain up today?
  link?: { tab: string; label: string };
};
export type LiveReading = {
  vibeWord: string;          // resolves to one of the 12 frontend mood keys (colours + emblem)
  mood: string;              // the one-line reading
  why: string;               // "why this?"
  good: string[];            // Good-for chips
  easy: string[];            // Go-easy chips
  opportunity: string;
  caution: string;
  action: string;
  sanskrit: string;
  offDay: boolean;           // Chandrashtama → low-key day note
  moonSign: string;
  moonNakshatra: string;
};
export type LiveEclipse = {
  type: "solar" | "lunar";
  inDays: number;
  short: string;      // the card line
  full: string;       // the sheet body (a fuller read, never an echo of `short`)
  sutakNote: string;  // "Sutak traditionally begins about 12 hours before, around 11 Aug 12:00."
  dateLabel: string;  // "12 August" — display-ready, already in the user's own timezone
  sanskrit: string;
} | null;
// The Moon crossing a sign boundary: a real, dated low window (at most one a day).
export type LiveSandhi = {
  start: string;      // "6:12pm"
  end: string;        // "9:32pm"
  fromSign: string;
  toSign: string;
  note: string;
  why: string;
  sanskrit: string;
} | null;
export type LiveHora = { line?: string; planet?: string; moonPhase?: any; festival?: any } | null;
export type LiveRitual = { title: string; sub: string; planet?: string; mantra?: string; why?: string } | null;

export type LiveWindow = { start: number; end: number; q: string; name: string; tip: string };
export type PlanTiming = { windows: LiveWindow[]; sunrise: number; strongWindow: string; summary: string } | null;
export type PanchangDay = { day: string; date: string; quality: string; note: string };

export type TodayRead = {
  reading: LiveReading;
  lifeAreas: { love: LiveArea; work: LiveArea; money: LiveArea };
  eclipse: LiveEclipse;
  sandhi: LiveSandhi;
  hora: LiveHora;
  ritual: LiveRitual;
  personal: string | null;      // the earned "you usually…" line; null until there IS a pattern
  timing: PlanTiming;           // Plan slider windows + strongest window (shared with Read footer)
  panchang: PanchangDay[];      // Plan → My Panchang strip (today + next 2)
};

// ---------- individual adapters ----------
export async function fetchReadingBundle(): Promise<Pick<TodayRead, "reading" | "lifeAreas">> {
  const r: any = await apiPost("/dashboard/today", { profile: getProfile() });
  const rd = r.reading || {};
  const la = r.life_areas || {};
  return {
    reading: {
      vibeWord: rd.vibe_word || "Deep",
      mood: rd.mood || "",
      why: rd.why || "",
      good: rd.good_for || [],
      easy: rd.go_easy || [],
      opportunity: rd.opportunity || "",
      caution: rd.caution || "",
      action: rd.action || "",
      sanskrit: rd.sanskrit || "",
      offDay: !!rd.chandrashtama,
      moonSign: rd.moon_sign || "",
      moonNakshatra: rd.moon_nakshatra || "",
    },
    lifeAreas: { love: area(la.love), work: area(la.work), money: area(la.money) },
  };
}

function area(a: any): LiveArea {
  return {
    tone: a?.tone || "steady",
    line: a?.line || "",
    detail: a?.detail || "",
    why: a?.why || "",
    planet: a?.planet || "",
    houses: a?.houses || "",
    inFocus: !!a?.in_focus,
    link: a?.link,
  };
}

// NB: every function below uses getCurrentPlace(), NOT getProfile(). Hora, Rahu Kaal, muhurta
// and the day's tithi are cut from LOCAL SUNRISE, which belongs to where the user is standing —
// the birth place belongs to the natal chart alone. Sending the birth place here gave a
// Shimla-born Chennai resident "better for patient work than for new beginnings" during what was
// really one of their best windows. See api/place.ts + TODAY_TAB_AUDIT.md.
export async function fetchHora(): Promise<LiveHora> {
  const p = getCurrentPlace();
  const r: any = await apiPost("/dashboard/hora", { lat: p.lat, lon: p.lon, tz: p.tz });
  return { line: r.hora?.line, planet: r.hora?.planet, moonPhase: r.moon_phase, festival: r.festival };
}

// Returns BOTH of the day's heads-up cards. The eclipse's sutak window and the sandhi
// block were being dropped on the floor here, which is why tapping the card could only
// ever show demo detail — the real detail never made it out of the adapter.
export async function fetchDayAlerts(): Promise<{ eclipse: LiveEclipse; sandhi: LiveSandhi }> {
  const p = getCurrentPlace();
  const r: any = await apiPost("/dashboard/day-alerts", { date: localDateISO(p.tz), tz: p.tz, lat: p.lat, lon: p.lon });

  const e = r.eclipse;
  const eclipse: LiveEclipse = !e || !e.present ? null : {
    type: /surya|solar/i.test(e.type || "") ? "solar" : "lunar",
    inDays: e.days_until ?? 0,
    short: e.short || e.why || "",
    full: e.why || "",
    sutakNote: e.sutak_note || "",
    dateLabel: longDate(e.date),
    sanskrit: e.sanskrit || "",
  };

  const s = r.chandra_sandhi;
  const sandhi: LiveSandhi = !s || !s.present ? null : {
    start: to12(s.start), end: to12(s.end),
    fromSign: s.from_sign || "", toSign: s.to_sign || "",
    note: s.note || "", why: s.why || "", sanskrit: s.sanskrit || "",
  };

  return { eclipse, sandhi };
}

/**
 * The reading's personal line ("You usually run low on days like this") from /memory/today.
 *
 * This is the ONE line in the app that claims to know the user's own history, so it is the one
 * that must never be faked: the demo constant asserted a remembered pattern to someone who had
 * never checked in once. It is earned, not decorative. The engine only unlocks a pattern after
 * ~30 check-ins (a gentler trend note fires from 3), so a new user correctly gets nothing here
 * and the card collapses — which is exactly what the original design intended with "null
 * collapses gracefully".
 *
 * JWT-gated. Signed out → we don't call at all: there is no history to have a pattern in.
 * The date must be the user's CURRENT day, because the server would otherwise derive it from
 * the BIRTH profile's timezone (see daily_moon_forecast's default) and score the wrong day for
 * anyone who has moved.
 */
export async function fetchPersonalLine(): Promise<string | null> {
  if (!hasAuthToken()) return null;
  const p = getCurrentPlace();
  const r: any = await apiGet(`/memory/today?date=${encodeURIComponent(localDateISO(p.tz))}`);
  return (r?.personal_note || "").trim() || null;
}

export async function fetchRitualToday(): Promise<LiveRitual> {
  // `profile` is the BIRTH chart (the remedy comes from the natal chart = bucket A), but the
  // date/tz are bucket D: the WEEKDAY decides which planet's remedy is offered, so it has to be
  // the user's weekday. Without these the server fell back to its own UTC day.
  const here = getCurrentPlace();
  const r: any = await apiPost("/rituals/today", {
    profile: getProfile(), date: localDateISO(here.tz), tz: here.tz,
  });
  const rit = r.ritual;
  if (!rit) return null;
  return { title: rit.action || "Today's ritual", sub: rit.tip || rit.why || "", planet: rit.planet, mantra: rit.mantra, why: rit.why };
}

const MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const MON_LONG = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
function hm(s: string): number { const [h, m] = (s || "0:0").split(":").map(Number); return (h || 0) + (m || 0) / 60; }
function to12(s: string): string { const [h, m] = (s || "0:0").split(":").map(Number); const ap = h < 12 ? "am" : "pm"; let h12 = h % 12; if (h12 === 0) h12 = 12; return `${h12}:${String(m || 0).padStart(2, "0")}${ap}`; }
function prettyDate(iso: string): string { const [, m, d] = (iso || "").split("-").map(Number); return `${d} ${MON[(m || 1) - 1]}`; }
function longDate(iso: string): string { const [, m, d] = (iso || "").split("-").map(Number); return m ? `${d} ${MON_LONG[m - 1]}` : ""; }

export async function fetchTiming(): Promise<PlanTiming> {
  const p = getCurrentPlace();
  const r: any = await apiPost("/dashboard/timing", { date: localDateISO(p.tz), lat: p.lat, lon: p.lon, tz: p.tz });
  const SR = hm(r.sunrise || "06:00");
  // Make the 16 choghadiya slots a monotonic run from sunrise across midnight (the slider maps
  // time linearly from sunrise to sunrise+24), so night/after-midnight slots sit after the day.
  let prev = SR;
  const windows: LiveWindow[] = (r.choghadiya || []).map((c: any) => {
    let s = hm(c.start), e = hm(c.end);
    while (s < prev - 1e-6) s += 24;
    while (e < s - 1e-6) e += 24;
    prev = e;
    return { start: s, end: e, q: c.quality, name: c.name, tip: c.tip };
  });
  const ab = (r.good || [])[0];
  return {
    windows,
    sunrise: SR,
    strongWindow: ab ? `${to12(ab.start)}–${to12(ab.end)}` : "",
    summary: r.summary || "",
  };
}

export async function fetchPanchang(days = 3): Promise<PanchangDay[]> {
  // BOTH, and they are not the same place: `profile` is the BIRTH chart (chandrashtama and any
  // natal comparison need the natal Moon), while lat/lon/tz must be WHERE THEY ARE — the day's
  // tithi/nakshatra are read at LOCAL sunrise.
  const here = getCurrentPlace();
  const r: any = await apiPost("/dashboard/panchang", { profile: getProfile(), lat: here.lat, lon: here.lon, tz: here.tz, days });
  return (r.days || []).map((d: any, i: number) => ({
    day: i === 0 ? "Today" : i === 1 ? "Tomorrow" : (d.weekday || ""),
    date: prettyDate(d.date),
    quality: d.band,                       // good | mixed | low  → qColor/qWord handle these
    note: d.label || [d.tithi, d.nakshatra].filter(Boolean).join(" · "),
  }));
}

// ---------- the one loader the Today tab calls (Read + Plan daily data) ----------
// The reading bundle is REQUIRED: if it throws, the Today tab renders its error state rather
// than a demo reading (see AstroApp's todayErr). The extras are best-effort and each degrades
// to null, which the cards read as "there is nothing to show today" — a card that hides is
// honest; a card that invents an eclipse is not.
export async function loadToday(): Promise<TodayRead> {
  const [bundle, hora, alerts, ritual, timing, panchang, personal] = await Promise.all([
    fetchReadingBundle(),
    fetchHora().catch(() => null),
    fetchDayAlerts().catch(() => ({ eclipse: null, sandhi: null })),
    fetchRitualToday().catch(() => null),
    fetchTiming().catch(() => null),
    fetchPanchang(3).catch(() => []),
    fetchPersonalLine().catch(() => null),
  ]);
  return { ...bundle, hora, eclipse: alerts.eclipse, sandhi: alerts.sandhi, ritual, timing, panchang, personal };
}
