// place.ts — WHERE THE USER IS NOW. Not where they were born.
//
// THE RULE (Vedic, not preference):
//   BIRTH place  -> the natal chart. Fixed forever. Never changes when they travel. (profile.ts)
//   CURRENT place -> every daily/transit reading. Changes when they move. (this file)
//
// Hora, Rahu Kaal, muhurta windows and the day's tithi/nakshatra are all cut from LOCAL
// SUNRISE, and sunrise belongs to where you are standing. Using the birth place for these was a
// real shipped bug — proven live at the same instant:
//     Shimla  (birth)   -> Saturn  "better for patient work than for new beginnings"
//     Chennai (current) -> Jupiter "one of the day's best stretches, good for a fresh start"
// Opposite advice, delivered confidently, to anyone who moved city. Most Indians do not live in
// their birth city, so this was never an edge case. See TODAY_TAB_AUDIT.md.
//
// This module is the ONE place that answers "where are they now", so the question can never be
// half-answered: fix it here and every daily endpoint follows.
import { getProfile } from "./profile";

export type Loc = { lat: number; lon: number; tz: string; label?: string };

let _current: Loc | null = null;

/** Set once we actually know (onboarding's "where do you live now", or the You tab). */
export function setCurrentPlace(loc: Loc): void {
  _current = loc;
}

// A timezone IS a place — IANA names are literally cities. This gives us "where are they" for
// free: no permission, no network, no GPS, no question asked. We only need the zones a Myastro
// user could plausibly be in (India + the diaspora), not all ~400.
//
// Coordinates are the zone's reference city. Good enough on purpose: what sunrise cares about is
// roughly where on Earth you are. Being 200km out costs a minute or two. Being in the wrong
// COUNTRY costs twelve hours.
const TZ_CITY: Record<string, Loc> = {
  "Asia/Kolkata":        { lat: 22.5726, lon: 88.3639, tz: "Asia/Kolkata",        label: "Kolkata" },
  "Asia/Calcutta":       { lat: 22.5726, lon: 88.3639, tz: "Asia/Kolkata",        label: "Kolkata" },
  "Asia/Dubai":          { lat: 25.2048, lon: 55.2708, tz: "Asia/Dubai",          label: "Dubai" },
  "Asia/Singapore":      { lat:  1.3521, lon: 103.8198, tz: "Asia/Singapore",     label: "Singapore" },
  "Asia/Kathmandu":      { lat: 27.7172, lon: 85.3240, tz: "Asia/Kathmandu",      label: "Kathmandu" },
  "Asia/Colombo":        { lat:  6.9271, lon: 79.8612, tz: "Asia/Colombo",        label: "Colombo" },
  "Asia/Karachi":        { lat: 24.8607, lon: 67.0011, tz: "Asia/Karachi",        label: "Karachi" },
  "Asia/Dhaka":          { lat: 23.8103, lon: 90.4125, tz: "Asia/Dhaka",          label: "Dhaka" },
  "Asia/Tokyo":          { lat: 35.6762, lon: 139.6503, tz: "Asia/Tokyo",         label: "Tokyo" },
  "Asia/Hong_Kong":      { lat: 22.3193, lon: 114.1694, tz: "Asia/Hong_Kong",     label: "Hong Kong" },
  "Europe/London":       { lat: 51.5074, lon: -0.1278, tz: "Europe/London",       label: "London" },
  "Europe/Dublin":       { lat: 53.3498, lon: -6.2603, tz: "Europe/Dublin",       label: "Dublin" },
  "Europe/Berlin":       { lat: 52.5200, lon: 13.4050, tz: "Europe/Berlin",       label: "Berlin" },
  "Europe/Paris":        { lat: 48.8566, lon:  2.3522, tz: "Europe/Paris",        label: "Paris" },
  "Europe/Amsterdam":    { lat: 52.3676, lon:  4.9041, tz: "Europe/Amsterdam",    label: "Amsterdam" },
  "Europe/Zurich":       { lat: 47.3769, lon:  8.5417, tz: "Europe/Zurich",       label: "Zurich" },
  "America/New_York":    { lat: 40.7128, lon: -74.0060, tz: "America/New_York",   label: "New York" },
  "America/Chicago":     { lat: 41.8781, lon: -87.6298, tz: "America/Chicago",    label: "Chicago" },
  "America/Denver":      { lat: 39.7392, lon: -104.9903, tz: "America/Denver",    label: "Denver" },
  "America/Phoenix":     { lat: 33.4484, lon: -112.0740, tz: "America/Phoenix",   label: "Phoenix" },
  "America/Los_Angeles": { lat: 34.0522, lon: -118.2437, tz: "America/Los_Angeles", label: "Los Angeles" },
  "America/Toronto":     { lat: 43.6532, lon: -79.3832, tz: "America/Toronto",    label: "Toronto" },
  "America/Vancouver":   { lat: 49.2827, lon: -123.1207, tz: "America/Vancouver", label: "Vancouver" },
  "Australia/Sydney":    { lat: -33.8688, lon: 151.2093, tz: "Australia/Sydney",  label: "Sydney" },
  "Australia/Melbourne": { lat: -37.8136, lon: 144.9631, tz: "Australia/Melbourne", label: "Melbourne" },
  "Australia/Perth":     { lat: -31.9505, lon: 115.8605, tz: "Australia/Perth",   label: "Perth" },
  "Pacific/Auckland":    { lat: -36.8485, lon: 174.7633, tz: "Pacific/Auckland",  label: "Auckland" },
};

const normTz = (t: string) => (t === "Asia/Calcutta" ? "Asia/Kolkata" : t);

/**
 * Where to compute today's sky.
 *
 * 1. An explicit place the user gave us always wins.
 * 2. If the device timezone MATCHES the birth timezone, use the BIRTH PLACE. This is the
 *    important subtlety: within one zone the tz cannot locate them (all of India is
 *    Asia/Kolkata), and swapping a Shimla-born Shimla-living user to "Kolkata" because that is
 *    the zone's reference city would move them 1,500km for nothing. Their birth city is the
 *    better guess when we have no evidence they left.
 * 3. If the device timezone DIFFERS, they have definitively left the zone, so the birth place is
 *    now catastrophically wrong (India→America = 12 hours). The zone's city is far closer.
 *
 * Residual error we accept: a same-country move (Shimla→Chennai, ~22 min of sunrise) is
 * invisible to this, because the timezone is identical. Only asking can fix that, and it is a
 * couple of minutes rather than half a day — so we do not nag the whole userbase for it.
 */
export function getCurrentPlace(): Loc {
  if (_current) return _current;
  const p = getProfile();
  const birth: Loc = { lat: p.lat, lon: p.lon, tz: p.tz, label: p.place };

  const dev = deviceTz();
  if (!dev || !p.tz) return birth;
  if (normTz(dev) === normTz(p.tz)) return birth;      // same zone → birth city is the best guess

  const zoneCity = TZ_CITY[dev] || TZ_CITY[normTz(dev)];
  return zoneCity || birth;                            // unknown zone → birth is still safer than nothing
}

/** True once the user has actually told us where they live (vs us assuming the birth place). */
export function hasCurrentPlace(): boolean {
  return _current !== null;
}

/**
 * "Thursday, 16 July" for the place we are computing the sky FOR.
 *
 * Bucket D. Must use getCurrentPlace().tz rather than the device clock, so the day the header
 * NAMES is the same day the reading DESCRIBES. Even when nothing in the maths changes, the
 * label does: an instant that is Thursday in Kolkata is still Wednesday in Los Angeles.
 */
export function currentDateLabel(now: Date = new Date()): string {
  const tz = getCurrentPlace().tz;
  try {
    return new Intl.DateTimeFormat("en-US", {
      timeZone: tz, weekday: "long", day: "numeric", month: "long",
    }).format(now);
  } catch {
    return new Intl.DateTimeFormat("en-US", { weekday: "long", day: "numeric", month: "long" }).format(now);
  }
}

/**
 * The hour (0-23.99) at the place we compute for. Drives the sky scene (dawn/day/dusk/night)
 * and the greeting, so it must match the reading's day — otherwise the header says
 * "Good morning" over an evening reading.
 */
export function currentHour(now: Date = new Date()): number {
  const tz = getCurrentPlace().tz;
  try {
    const p = new Intl.DateTimeFormat("en-US", {
      timeZone: tz, hour: "2-digit", minute: "2-digit", hourCycle: "h23",
    }).formatToParts(now);
    const h = Number(p.find((x) => x.type === "hour")?.value);
    const m = Number(p.find((x) => x.type === "minute")?.value);
    if (!Number.isNaN(h) && !Number.isNaN(m)) return h + m / 60;
  } catch {
    // fall through
  }
  return now.getHours() + now.getMinutes() / 60;
}

/** The device's timezone — where they physically are, per the OS. */
export function deviceTz(): string | null {
  try {
    return Intl.DateTimeFormat().resolvedOptions().timeZone || null;
  } catch {
    return null;
  }
}

/**
 * Cheap, permission-free signal that our assumed location is WRONG: the device's timezone does
 * not match the place we are computing from. It cannot tell us where they are (a timezone is not
 * a coordinate), only that we should ask.
 *
 * Deliberately NOT a silent switch — we ask ("Looks like you're in New York. Use it for today's
 * readings?") and never guess a lat/lon from a timezone. No GPS: a scary permission for
 * something a one-tap question answers better.
 */
export function looksLikeTheyMoved(): boolean {
  const dev = deviceTz();
  if (!dev) return false;
  const here = getCurrentPlace().tz;
  if (!here) return false;
  if (dev === here) return false;
  // Asia/Calcutta and Asia/Kolkata are the same place under two IANA spellings; real devices
  // report either. Treat them as equal rather than nagging every Indian user forever.
  const norm = (t: string) => (t === "Asia/Calcutta" ? "Asia/Kolkata" : t);
  return norm(dev) !== norm(here);
}
