// ─────────────────────────────────────────────────────────────────────────────
// web/shared/api.js
// ONE place where every API call lives. If the backend changes shape, edit
// here only. Each function returns a Promise that resolves to the parsed
// JSON (or rejects with a useful error).
//
// Every page imports just the functions it needs from this file.
// ─────────────────────────────────────────────────────────────────────────────

import { API_BASE } from "./config.js";

// ── low-level wrapper ────────────────────────────────────────────────────────

async function _post(path, body) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${text}`);
  }
  return res.json();
}

async function _get(path) {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}

// ── Profiles ─────────────────────────────────────────────────────────────────

export async function geocode(place) {
  const res = await fetch(`${API_BASE}/api/v1/profiles/geocode?place=${encodeURIComponent(place)}`);
  if (!res.ok) {
    if (res.status === 404) return null;
    throw new Error(`${res.status} ${res.statusText}`);
  }
  return res.json();   // {lat, lon, name, tz}
}

export const validateProfile = (profile) => _post("/api/v1/profiles/validate", profile);

// ── Kundli ───────────────────────────────────────────────────────────────────

export const kundliFree = (profile) => _post("/api/v1/kundli/free", profile);

export async function kundliPremium({ profile, theme, chart_style, language, include_western }) {
  // Returns the PDF blob directly so the caller can offer download.
  const res = await fetch(`${API_BASE}/api/v1/kundli/premium`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ profile, theme, chart_style, language, include_western }),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${text}`);
  }
  return res.blob();
}

// ── Palm ─────────────────────────────────────────────────────────────────────

export async function palmAnalyze(profile, imageFile) {
  const fd = new FormData();
  fd.append("image", imageFile);
  fd.append("profile_json", JSON.stringify(profile));
  const res = await fetch(`${API_BASE}/api/v1/palm/analyze`, {
    method: "POST",
    body: fd,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${text}`);
  }
  return res.json();
}

// ── Tarot ────────────────────────────────────────────────────────────────────

export const tarotDraw = ({ spread, question, profile = null }) =>
  _post("/api/v1/tarot/draw", { spread, question, profile });

// ── Numerology ───────────────────────────────────────────────────────────────

export const numerologyProfile = ({ full_name, dob, system = "chaldean" }) =>
  _post("/api/v1/numerology/profile", { full_name, dob, system });

// ── Horoscopes ───────────────────────────────────────────────────────────────

export const horoscopeVedic = ({ profile, timeframe = "day" }) =>
  _post("/api/v1/horoscopes/vedic", { profile, timeframe });

// ── Consultation Chat ────────────────────────────────────────────────────────

export const consultationAsk = ({ profile, question, history = [] }) =>
  _post("/api/v1/consultation/ask", { profile, question, history });

// ── Oracle (6 sub-features) ──────────────────────────────────────────────────

export const oracleDeepAnalysis = ({ profile, include_d60 = false }) =>
  _post("/api/v1/oracle/deep-analysis", { profile, include_d60 });

export const oracleMatchmaking = ({ boy, girl }) =>
  _post("/api/v1/oracle/matchmaking", { boy, girl });

export const oracleMarriage = ({ boy, girl }) =>
  _post("/api/v1/oracle/marriage", { boy, girl });

export const oracleGochara = ({ profile }) =>
  _post("/api/v1/oracle/gochara", { profile });

export const oracleCompare = ({ profiles, criteria }) =>
  _post("/api/v1/oracle/compare", { profiles, criteria });

export const oraclePrashna = ({ question, asker_lat, asker_lon, asker_tz, asker_place }) =>
  _post("/api/v1/oracle/prashna", { question, asker_lat, asker_lon, asker_tz, asker_place });
