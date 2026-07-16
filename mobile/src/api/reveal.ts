// reveal.ts — the free onboarding Reveal, from the REAL sidereal chart.
// POST /chart/reveal { profile } -> the exact bundle the Reveal screen renders (mood word,
// Sun/Moon/Rising placements with ecliptic longitudes for the wheel angles, three warm
// insight lines, and a personal proof line). No AI. See features/chart/service.reveal.
import { apiPost } from "./client";
import { Profile } from "./config";

export type RevealMarker = { sign: string; nakshatra?: string; deg: number; lon: number; house?: number };
export type RevealInsight = { icon: "sun" | "moon" | "rise"; role: string; title: string; deg: number | null; line: string };
export type RevealBundle = {
  ok: boolean;
  first: string;
  mood: string;
  has_rising: boolean;
  sun: RevealMarker;
  moon: RevealMarker;
  rising: { sign: string; deg: number; lon: number } | null;
  insights: RevealInsight[];
  proof: string;
  precision_note: string | null;
};

export async function fetchReveal(profile: Profile): Promise<RevealBundle | null> {
  try {
    // The profile already carries the honest tier from buildProfileFromData (both
    // birth_time_known AND exact_time) — pass it straight through.
    //
    // It used to send `birth_time_known: !!profile.exact_time`, which conflated two different
    // questions and demoted every "I know it roughly" user to unknown, stripping the Lagna
    // sign they are legitimately entitled to (approximate time -> Lagna sign usually OK; it
    // is the DIVISIONALS that need the exact minute). See shared/astro/kundli.py.
    const r: any = await apiPost("/chart/reveal", { profile });
    if (!r || !r.ok) return null;
    return r as RevealBundle;
  } catch {
    return null;
  }
}
