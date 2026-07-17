// config.ts — where the app talks to the backend, and the birth profile the daily
// endpoints run on. ONE place to change the base URL and (for now) the seed profile.
//
// Dev loop: we run the FastAPI backend locally (uvicorn --host 0.0.0.0 --port 8000) so
// edits show instantly. The web preview reaches it at the machine's LAN IP; a phone on the
// same Wi-Fi reaches the same IP. For release, flip USE_LOCAL to false → the live Render
// backend. (Render is already current; local is just the fast edit loop.)

const LAN_LOCAL = "http://192.168.18.21:8000";      // this machine on the LAN (uvicorn 0.0.0.0:8000)
const RENDER = "https://myastroapi.onrender.com";   // live production backend

// USE_LOCAL = true points the app at a PRIVATE LAN IP. That only resolves from a device on the
// same Wi-Fi as the dev machine, with uvicorn running. On anyone else's phone every call fails
// — which is exactly how a tester got a Reveal built from the offline placeholder and reported
// it as "not accurate and too generic". Default to Render so the app works on any phone,
// anywhere; flip to true only while actively editing the backend locally.
export const USE_LOCAL = true;
export const API_BASE = USE_LOCAL ? LAN_LOCAL : RENDER;

// Render's free tier spins down when idle. A MEASURED cold start took 74s, so the old 25s
// timeout guaranteed a failure on the first call of the day. warmUp() (client.ts) is fired at
// launch to absorb that during onboarding, but the first real call can still land mid-wake.
export const API_TIMEOUT_MS = 90000;

// Chart maths is fast; only the cold start is slow. Once warm, a stuck request should fail
// quickly rather than hang a user for 90 seconds.
export const API_TIMEOUT_WARM_MS = 25000;

// The standard birth-profile shape the backend expects (/kundli/compute, /dashboard/*, …).
export type Profile = {
  name: string;
  date: string;   // YYYY-MM-DD
  time: string;   // HH:MM (24h). A NOON PLACEHOLDER when birth_time_known is false.
  place: string;
  lat: number;
  lon: number;
  tz: string;     // IANA, e.g. "Asia/Kolkata"
  gender?: string;
  // The birth-time tier. BOTH flags must be sent — they are not the same question, and the
  // backend derives time_precision / houses_reliable / divisionals_reliable from them
  // (shared/astro/kundli.py):
  //   birth_time_known=false            -> 'unknown'     : Moon-based output only. NO rising, NO houses.
  //   birth_time_known=true,  exact=false -> 'approximate': Lagna sign usually OK, divisionals NOT.
  //   birth_time_known=true,  exact=true  -> 'exact'      : everything, incl. D9/D60.
  // BOTH ARE REQUIRED ON PURPOSE — do not make them optional again.
  //
  // Omitting birth_time_known is DANGEROUS: it defaults to True server-side, so a user who
  // said "I don't know my time" gets handed a rising sign computed off the noon placeholder,
  // i.e. invented precision presented as fact. That bug shipped once already, precisely
  // because these were optional and the schema in SYSTEM_REFERENCE.md went unread.
  //
  // Required means TypeScript now refuses to build any profile that forgets them. The
  // contract is enforced by the compiler instead of by someone remembering the docs.
  birth_time_known: boolean;
  exact_time: boolean;
};

// Seed profile — used until onboarding captures the real one (see profile.ts). This is a
// real, valid chart so every daily endpoint returns real math today.
export const SEED_PROFILE: Profile = {
  name: "Aarav",
  date: "1998-08-14",
  time: "04:20",
  place: "Jaipur, India",
  lat: 26.9124,
  lon: 75.7873,
  tz: "Asia/Kolkata",
  gender: "male",
  birth_time_known: true,   // a real, fully-known birth time, so every tier is exercised
  exact_time: true,
};
