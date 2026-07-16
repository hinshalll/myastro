// data.ts — the onboarding data shape + pure helpers shared across the flow.
// No React, no imports from the screen modules, so it's the safe shared bottom of the
// dependency graph (Onboarding, steps, Reveal, Auth all import from here — no cycles).
import { Profile } from "../api/config";
import { Place } from "../api/geo";

// The whole product of onboarding — the profile payload we capture. `birthPlace` carries
// the geocoder's lat/lon/tz so the chart is real.
export type OnbData = {
  name: string;
  gender: string | null;
  dobD: number | null;
  dobM: number | null;
  dobY: number | null;
  birthPlace: Place | null;
  birthTimePrecision: "exact" | "approximate" | "unknown" | null;
  birthTime: string | null; // "HH:MM" 24h
  partOfDay: string | null;
};

export const emptyData: OnbData = {
  name: "", gender: null, dobD: null, dobM: null, dobY: null,
  birthPlace: null, birthTimePrecision: null, birthTime: null, partOfDay: null,
};

// clean a verbose geocoder label ("Jaipur, 302001, Jaipur Municipal Corporation, Rajasthan,
// India") -> "Jaipur, Rajasthan". Keeps the exact locality the user picked + its region (drops
// the postcode/country noise) so a TIGHT pick (a neighbourhood, a village) still reads clearly.
// The precise lat/lon is always stored regardless — tighter is better for the chart.
export function shortLabel(label: string): string {
  const parts = (label || "").split(",").map((s) => s.trim()).filter(Boolean);
  if (parts.length <= 2) return parts.join(", ");
  return `${parts[0]}, ${parts[parts.length - 2]}`;
}

// OnbData -> the backend Profile shape (config.ts). Returns null if birth date/place are
// missing (e.g. the returning-user login path, which has no captured data).
export function buildProfileFromData(data: OnbData): Profile | null {
  if (!data.dobY || !data.dobM || !data.dobD || !data.birthPlace) return null;
  const pad = (n: number) => String(n).padStart(2, "0");
  return {
    name: (data.name || "").trim() || "Friend",
    date: `${data.dobY}-${pad(data.dobM)}-${pad(data.dobD)}`,
    time: data.birthTime || "12:00",   // placeholder; inert when birth_time_known is false
    place: shortLabel(data.birthPlace.label),
    lat: data.birthPlace.lat,
    lon: data.birthPlace.lon,
    tz: data.birthPlace.tz || "Asia/Kolkata",
    gender: data.gender ? data.gender.toLowerCase() : undefined,
    ...timeTier(data),
  };
}

// The birth-time tier, honestly derived. MUST send birth_time_known — see config.ts. We only
// claim a time is "known" when we actually hold a clock time: picking "I know it roughly" and
// then skipping the part-of-day leaves birthTime null, and calling that approximate would hand
// the engine a noon placeholder dressed up as real input.
export function timeTier(data: OnbData): { birth_time_known: boolean; exact_time: boolean } {
  const haveClockTime = !!data.birthTime;
  const known = data.birthTimePrecision !== "unknown" && data.birthTimePrecision !== null && haveClockTime;
  return { birth_time_known: known, exact_time: known && data.birthTimePrecision === "exact" };
}
