// plan.ts — on-demand Plan-tab tool calls (fired when the user taps, not on mount).
// All stateless (profile / location in the body, no auth).
import { apiPost, localDateISO } from "./client";
import { getProfile } from "./profile";
import { getCurrentPlace } from "./place";

// ---- Ask the Moment (instant, no-AI Tara-Bala yes/no) → /dashboard/decide-quick ----
export type QuickAnswer = { verdict: string; why: string };
export async function askQuick(question: string): Promise<QuickAnswer> {
  const r: any = await apiPost("/dashboard/decide-quick", { profile: getProfile(), question });
  return { verdict: r.verdict || "Proceed gently", why: r.reason || r.why || "" };
}

// ---- Find a good day (Muhurat) → /dashboard/muhurta ----
export type MuhurtaResult = { date: string; time: string; note: string };
const MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const WD = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
function fmtDate(iso: string): string {
  const [y, m, d] = (iso || "").split("-").map(Number);
  const wd = WD[new Date(y, (m || 1) - 1, d).getDay()];
  return `${wd}, ${d} ${MON[(m || 1) - 1]}`;
}
function to12(s: string): string { const [h, m] = (s || "0:0").split(":").map(Number); const ap = h < 12 ? "am" : "pm"; let h12 = h % 12; if (h12 === 0) h12 = 12; return `${h12}:${String(m || 0).padStart(2, "0")}${ap}`; }

export async function planMuhurta(eventType: string, days = 30): Promise<MuhurtaResult[]> {
  // WHERE THEY ARE, not where they were born — a muhurta window is cut from local sunrise, so
  // picking a wedding time off the birth city's sunrise is simply the wrong time. See place.ts.
  const p = getCurrentPlace();
  const start = localDateISO(p.tz);
  const end = addDaysISO(start, days);
  const r: any = await apiPost("/dashboard/muhurta", {
    event_type: eventType, start_date: start, end_date: end,
    lat: p.lat, lon: p.lon, tz: p.tz, top_n: 3,
  });
  return (r.recommendations || []).map((rec: any) => ({
    date: fmtDate(rec.date),
    time: `${to12(rec.start)} – ${to12(rec.end)}`,
    note: rec.window_clear ? `${rec.window} window, clear of Rahu Kaal` : `${rec.window || "a"} window · ${rec.nakshatra || ""}`.trim(),
  }));
}

function addDaysISO(iso: string, n: number): string {
  const [y, m, d] = iso.split("-").map(Number);
  const dt = new Date(y, (m || 1) - 1, d + n);
  return `${dt.getFullYear()}-${String(dt.getMonth() + 1).padStart(2, "0")}-${String(dt.getDate()).padStart(2, "0")}`;
}
