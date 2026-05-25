// Thin client for the Myastro FastAPI backend.
//
// During local development the phone reaches this computer over Wi-Fi using its
// LAN IP (the same address Expo uses). When we later host on Render, only
// API_BASE changes — nothing else.

export const API_BASE = 'http://192.168.18.21:8000';

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

async function post<T>(path: string, body: unknown, timeoutMs = 20000): Promise<T> {
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
