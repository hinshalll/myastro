// checkin.ts — the evening check-in: save it, and read the real streak.
//
// This is the feature the whole "memory" side of the app is built on. The pattern engine
// (features/memory/service.py) correlates a DAY's energy against that day's sky and only
// unlocks a pattern after ~30 check-ins. Until this posts, that engine is being fed nothing
// and every check-in the user makes is discarded the moment the sheet closes.
//
// The app deliberately does NOT compute the sky and send it: the server derives astro_state
// from the user's own profile + the date (features/me/service.py::_astro_state). The client is
// not a trusted source of astrology, only of what the human said.
import { apiGet, apiPost, hasAuthToken, localDateISO } from "./client";

export type CheckinResult = { ok: boolean; streak: number | null };

/**
 * Save tonight's check-in. The DATE is the DEVICE's date on purpose, matching
 * checkInWindowOpen(): "how did your day go?" is about the day this person just lived, in the
 * timezone they are standing in. The birth timezone belongs to the natal chart alone.
 *
 * Returns ok:false rather than throwing — a failed save must be reported to the user honestly,
 * never swallowed behind a "+1 diya lit" that implies it was kept.
 */
export async function saveCheckin(mood: string, energy: string): Promise<CheckinResult> {
  if (!hasAuthToken()) return { ok: false, streak: null };
  try {
    const r: any = await apiPost("/me/checkins", { date: localDateISO(), mood, energy });
    return { ok: true, streak: r?.streak?.count ?? null };
  } catch {
    return { ok: false, streak: null };
  }
}

/** The real "N days in a row", or null when there is nothing true to show. */
export async function fetchCheckinStreak(): Promise<number | null> {
  if (!hasAuthToken()) return null;
  try {
    const r: any = await apiGet("/me/streaks/checkin");
    const n = r?.count;
    return typeof n === "number" && n > 0 ? n : null;
  } catch {
    return null;
  }
}
