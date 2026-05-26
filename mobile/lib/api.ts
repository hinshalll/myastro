// Thin client for the Myastro FastAPI backend.
//
// Hosted on Render (free tier) so the app works anywhere — not just on the
// same Wi-Fi as the dev PC. For local backend dev, swap API_BASE back to the
// LAN address (e.g. 'http://192.168.18.21:8000').
export const API_BASE = 'https://myastroapi.onrender.com';

export type Planet = {
  name: string;
  sign: string;
  house: number | null;
  nakshatra: string;
  nakshatra_lord: string;
  degree: string;
  retrograde: boolean;
};

export type ChartResult = {
  ok: boolean;
  moon: Planet | null;
  sun: Planet | null;
  ascendant_sign: string | null;
  ascendant_nakshatra: string | null;
  planets: Planet[];
  time_precision: 'exact' | 'approximate' | 'unknown';
  houses_reliable: boolean;
  divisionals_reliable: boolean;
};

export type BirthProfile = {
  name: string;
  date: string;          // 'YYYY-MM-DD'
  time?: string | null;  // 'HH:MM' or null/omitted if unknown
  birth_time_known?: boolean;
  exact_time?: boolean;
  place?: string;
  lat: number;
  lon: number;
  tz: string;            // e.g. 'Asia/Kolkata'
  gender?: string;
};

// Default 65s: Render's free instance "sleeps" after ~15 min idle, and the
// first request after that takes ~50s to wake. Generous timeout avoids a
// false failure on that cold start.
async function post<T>(path: string, body: unknown, timeoutMs = 65000): Promise<T> {
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), timeoutMs);
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      signal: ctrl.signal,
    });
    if (!res.ok) {
      const text = await res.text().catch(() => '');
      throw new Error(`Backend ${res.status}: ${text || res.statusText}`);
    }
    return (await res.json()) as T;
  } finally {
    clearTimeout(t);
  }
}

export function computeChart(profile: BirthProfile, chartStyle = 'north_indian') {
  return post<ChartResult>('/kundli/compute', { profile, chart_style: chartStyle });
}

export async function healthCheck(): Promise<boolean> {
  try {
    const ctrl = new AbortController();
    const t = setTimeout(() => ctrl.abort(), 6000);
    const res = await fetch(`${API_BASE}/`, { signal: ctrl.signal });
    clearTimeout(t);
    return res.ok;
  } catch {
    return false;
  }
}
