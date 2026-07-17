// client.ts — the one fetch wrapper every API call goes through.
// Adds the base URL, JSON headers, a timeout, optional auth token (for JWT endpoints later),
// and normalizes errors into ApiError so screens can show a friendly message.
import { API_BASE, API_TIMEOUT_MS, API_TIMEOUT_WARM_MS } from "./config";

// Render's free tier sleeps when idle and a measured cold start took 74s. Rather than design
// the app around that error, we absorb it: warmUp() is fired once at launch, so the server is
// waking while the user is still typing their name, and is warm by the time onboarding asks
// for a chart. Until a call succeeds we allow the long cold timeout; after that a stuck
// request should fail fast instead of hanging someone for 90 seconds.
let _warm = false;

export function warmUp(): void {
  if (_warm) return;
  // Fire and forget. A 404 still proves the server is awake, which is all we need.
  fetch(`${API_BASE}/openapi.json`, { method: "GET" })
    .then(() => { _warm = true; })
    .catch(() => { /* offline; the real call will report it honestly */ });
}

let _token: string | null = null;
// Onboarding/auth will call this after Supabase sign-in so /me, /planner, /wallet, /memory work.
export function setAuthToken(token: string | null): void {
  _token = token;
}

/**
 * Is anyone signed in? Use this to SKIP a JWT-gated call rather than fire it and eat a 401.
 * The distinction matters for honesty, not just noise: "signed out" and "the server said no"
 * are different states, and only the second is an error worth showing.
 */
export function hasAuthToken(): boolean {
  return !!_token;
}

export class ApiError extends Error {
  status: number;
  body: any;
  constructor(status: number, message: string, body?: any) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.body = body;
  }
}

async function request<T>(path: string, init: RequestInit, timeout?: number): Promise<T> {
  const ctrl = new AbortController();
  const ms = timeout ?? (_warm ? API_TIMEOUT_WARM_MS : API_TIMEOUT_MS);
  const timer = setTimeout(() => ctrl.abort(), ms);
  try {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      Accept: "application/json",
      ...((init.headers as Record<string, string>) || {}),
    };
    if (_token) headers.Authorization = `Bearer ${_token}`;
    const res = await fetch(`${API_BASE}${path}`, { ...init, headers, signal: ctrl.signal });
    _warm = true;                 // it answered, so it is awake
    const text = await res.text();
    const data = text ? safeJson(text) : null;
    if (!res.ok) {
      const msg = (data && (data.detail || data.message)) || `Request failed (${res.status})`;
      throw new ApiError(res.status, typeof msg === "string" ? msg : `Request failed (${res.status})`, data);
    }
    return data as T;
  } catch (e: any) {
    if (e?.name === "AbortError") throw new ApiError(0, "That took too long to load. Give it a moment and try again.");
    if (e instanceof ApiError) throw e;
    throw new ApiError(0, e?.message || "Could not reach the server.");
  } finally {
    clearTimeout(timer);
  }
}

function safeJson(text: string): any {
  try { return JSON.parse(text); } catch { return null; }
}

export function apiPost<T>(path: string, body?: any, timeout?: number): Promise<T> {
  return request<T>(path, { method: "POST", body: JSON.stringify(body ?? {}) }, timeout);
}

export function apiGet<T>(path: string, timeout?: number): Promise<T> {
  return request<T>(path, { method: "GET" }, timeout);
}

// today's date in the device's local time as YYYY-MM-DD (endpoints that need an explicit date).
/**
 * Today's date (YYYY-MM-DD) AT A GIVEN PLACE.
 *
 * Pass the SAME tz you send as lat/lon/tz, so the date and the sky always describe the same
 * place. Getting the date from the device while getting sunrise from somewhere else is how you
 * ask the engine for today's date under yesterday's sky — which is what shipped: device date +
 * BIRTH-place sunrise. See api/place.ts + TODAY_TAB_AUDIT.md.
 *
 * Omit tz only where the date is genuinely about the user's own wall clock rather than a
 * calculation (e.g. the evening check-in window).
 */
export function localDateISO(tz?: string): string {
  const d = new Date();
  if (tz) {
    try {
      // en-CA renders as YYYY-MM-DD, which is exactly the wire format the backend wants.
      return new Intl.DateTimeFormat("en-CA", {
        timeZone: tz, year: "numeric", month: "2-digit", day: "2-digit",
      }).format(d);
    } catch {
      // unknown tz string — fall back to the device clock rather than fail the request
    }
  }
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${d.getFullYear()}-${m}-${day}`;
}
