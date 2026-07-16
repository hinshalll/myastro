// geo.ts — place autocomplete for onboarding (public, no auth). /geo/search →
// { results: [{ label, lat, lon, tz }] }. The user types a city, taps a result, and we
// capture lat/lon/tz for the birth profile.
import { apiPost } from "./client";

export type Place = { label: string; lat: number; lon: number; tz: string };

export async function searchPlaces(query: string): Promise<Place[]> {
  const q = (query || "").trim();
  if (q.length < 2) return [];
  const r: any = await apiPost("/geo/search", { query: q });
  return (r.results || []).map((p: any) => ({ label: p.label, lat: p.lat, lon: p.lon, tz: p.tz }));
}
