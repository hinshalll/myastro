// profile.ts — the single source of the current birth profile.
//
// Onboarding calls setProfile() with the real captured data; everything downstream reads
// getProfile() and never hard-codes a chart. This is the seam.
import { SEED_PROFILE, Profile } from "./config";
import { demoFallback, clearDemoFact } from "../theme";

let _profile: Profile = SEED_PROFILE;

const SEED_FLAG = "profile · Aarav's chart, NOT yours";

/**
 * The current birth profile.
 *
 * THE SEED IS THE MOST DANGEROUS FAKE IN THE APP, and it needed its own guard because none of
 * the others could catch it. Every other demo constant is a fabricated STRING, so it shows up
 * as a missing `live` value and demoFallback fires. The seed fabricates the PERSON. The maths
 * that runs on it is real, the backend returns a genuine chart, nothing is null, no fallback
 * triggers — the app just renders a flawless reading for a man born in Jaipur in 1998 and
 * hands it to whoever is holding the phone.
 *
 * It is reachable today: buildProfileFromData() returns null on the returning-user LOGIN path
 * (no captured onboarding data), and App.tsx does `if (p) setProfile(p)`. So a returning user
 * who logs in keeps the seed and reads Aarav's day as their own. The real fix is loading the
 * saved profile from GET /me/profiles at login (task #54). Until that lands this must be
 * IMPOSSIBLE TO MISS rather than invisible:
 *   dev  → names itself on the DEMO badge.
 *   prod → throws, so the reading fails honestly instead of impersonating a stranger.
 */
export function getProfile(): Profile {
  if (_profile === SEED_PROFILE) {
    // sticky: read inside async loaders, not during render, so a per-render ledger would drop
    // it while it is still fake. Released by setProfile().
    return demoFallback(SEED_FLAG, null, SEED_PROFILE, { sticky: true });
  }
  return _profile;
}

export function setProfile(p: Profile): void {
  _profile = p;
  clearDemoFact(SEED_FLAG);   // it stopped being a stranger's chart the moment this ran
}

/** Whether we have a real (onboarded) profile yet. Onboarding flips this by calling setProfile. */
export function hasRealProfile(): boolean {
  return _profile !== SEED_PROFILE;
}

// The user's display first name (from the captured profile). For the Today greeting, avatar
// initial, Sage openers, etc. Falls back to "friend" if somehow empty.
//
// Reads _profile directly, NOT getProfile(): this is called during render, and a name is not
// astrology. Greeting a signed-out user "Good morning, friend" is honest; throwing mid-render
// (or blaming the DEMO badge on a greeting) is not. The badge fires on the reading instead,
// which is the claim that actually matters.
export function getFirstName(): string {
  const n = (_profile === SEED_PROFILE ? "" : _profile.name || "").trim().split(" ")[0];
  return n || "friend";
}
