// precision.ts — what the app is ALLOWED to show, based on how well we know the birth time.
//
// This is an honesty layer, not a paywall. Vedic astrology genuinely cannot produce some
// things without the birth minute, and inventing them is the worst thing this app could do:
// the whole product rests on the reading feeling true. Verified against the live backend —
// the SAME person resolves to Cancer / Virgo / Libra rising at exact / approximate / unknown.
// A wrong time does not give a slightly-off answer, it gives a different chart.
//
// THE RULES (mirror of shared/astro/kundli.py — keep the two in sync):
//   unknown     : no birth time. Moon-based output ONLY. No rising, no houses, no divisionals.
//   approximate : a time, unconfirmed. Rising + houses OK. Divisionals (D9/D60) NOT.
//   exact       : everything.
//
// Prefer the flags the SERVER returns (time_precision / houses_reliable / divisionals_reliable)
// whenever you have a response in hand — the server is the authority. Use these local helpers
// to gate UI *before* a call, or when rendering purely from the stored profile.
import { Profile } from "./config";

export type Precision = "exact" | "approximate" | "unknown";

export function precisionOf(p: Profile | null | undefined): Precision {
  if (!p || p.birth_time_known === false) return "unknown";
  return p.exact_time ? "exact" : "approximate";
}

/** Ascendant + the twelve houses need a known time at all. */
export function housesReliable(p: Profile | null | undefined): boolean {
  return precisionOf(p) !== "unknown";
}

/** Divisional charts (D9 Navamsa, D60...) need the EXACT minute. Navamsa drives marriage
 *  and partnership readings, so this is the flag that gates a whole feature area, not a detail. */
export function divisionalsReliable(p: Profile | null | undefined): boolean {
  return precisionOf(p) === "exact";
}

/** Does this profile have room to improve? Drives the "add your time" nudges. */
export function canSharpen(p: Profile | null | undefined): boolean {
  return precisionOf(p) !== "exact";
}

/**
 * One warm line explaining what is missing and why, or null when nothing is.
 * Voice rule: never scold, never nag, never imply they did something wrong. A missing birth
 * time is extremely common and completely fine — the chart is still rich without it.
 */
export function precisionNote(p: Profile | null | undefined): string | null {
  switch (precisionOf(p)) {
    case "unknown":
      return "Your birth time isn't set, so this reads from your Moon. Add your time whenever you find it and your rising sign and houses open up.";
    case "approximate":
      return "This reads from a rough birth time, which covers your rising sign and houses. The finer marriage and career readings need the exact minute.";
    default:
      return null;
  }
}

/** Short label for chips/badges. */
export function precisionLabel(p: Profile | null | undefined): string {
  switch (precisionOf(p)) {
    case "unknown": return "Moon-led chart";
    case "approximate": return "Rough birth time";
    default: return "Exact birth time";
  }
}
