// verify.ts — THE CLIENT SEAM for proving a phone number is yours.
//
// This file is the ONLY thing that changes when we leave Expo Go. Every screen that
// imports it (PhoneStep, OtpStep) stays byte-for-byte identical, because they only
// ever call these four functions and never learn how verification actually happens.
//
//   TODAY (Expo Go)  — faked. sendCode() pretends, checkCode() accepts DEV_CODE.
//                      Nothing is sent, nothing costs money, the flow is fully walkable.
//   DEV BUILD        — isTruecallerAvailable() becomes the SDK's isUsable(): Truecaller
//                      users get one tap and never see OtpStep at all. Everyone else on
//                      +91 falls to Truecaller's own free drop-call, and only if THAT is
//                      unavailable do we send a real code (HanuOTP, ~Rs 0.25) through the
//                      backend's send_otp() seam.
//   NON-INDIA        — never reaches here. See shouldAskForPhone().
//
// Why fake it rather than wire TextBee now: TextBee exists only so Expo Go can verify a
// phone, and Truecaller/Google replace it the moment the dev build lands. Building real
// SMS sending today is work with a known expiry date. The screens are not — they almost
// certainly survive, because Truecaller's own fallback UI is off-brand and its drop-call
// needs restricted Play permissions. So: build the screens for real, fake only this.

import { getLocales } from "expo-localization";

export const DEV_CODE = "123456";

/** Flip to false the moment real verification lands. Keeps the fake impossible to ship by accident. */
export const VERIFY_IS_FAKED = true;

export type VerifyResult = { ok: boolean; error?: string };

/** '+91' + 10 digits. The gate is the number they TYPED, never their detected location. */
export function isIndianPhone(e164: string): boolean {
  return /^\+91\d{10}$/.test((e164 || "").trim());
}

/** Loose E.164 for any country, so non-India numbers still validate before we refuse to SMS them. */
export function isE164(e164: string): boolean {
  return /^\+[1-9]\d{7,14}$/.test((e164 || "").trim());
}

/**
 * Which signup path leads. A DEFAULT, never a gate — both paths stay reachable, so a wrong
 * guess costs one tap and breaks nothing (that is the whole reason we do not geo-IP).
 *
 * Uses the device timezone rather than expo-localization purely to avoid adding a dependency
 * for a hint. If we ever need the real region code, expo-localization getLocales()[0].regionCode
 * is the correct source — but it must stay a default too.
 */
/**
 * Does this device look Indian? Available the instant the app opens — offline, no permission,
 * no network, no user input — so it can pick the door BEFORE they type anything.
 *
 * ANY signal saying India wins. This is an OR on purpose, and the ordering of a "best" signal
 * is a trap we already fell into twice in testing:
 *
 *  - Ranking regionCode first was WRONG. `regionCode` comes from the LANGUAGE setting, not
 *    from location. A great many Indian users run their phone as "English (United States)",
 *    which reports regionCode "US" while they are sitting in Mumbai. The real device tested
 *    here reported exactly that: navigator.language "en-US", yet languages included "en-IN"
 *    and the timezone was Asia/Calcutta. Trusting regionCode alone would ship the
 *    international path to an Indian user.
 *  - Matching only "Asia/Kolkata" was WRONG. "Asia/Calcutta" is the legacy IANA alias and is
 *    what real devices (Windows especially) still report.
 *
 * Timezone is the stronger location signal (it tracks where you ARE — often set by the
 * network); language tracks what you PREFER. So we accept either, plus any secondary locale.
 *
 * Being wrong is cheap by design: this only chooses what LEADS, never what exists
 * (see shouldOfferPhone), so a false negative costs one tap.
 */
export function deviceLooksIndian(): boolean {
  // 1) ANY locale pointing at India — catches "en-US, en-IN" (primary US, but India present).
  try {
    if (getLocales().some((l) => (l?.regionCode || "").toUpperCase() === "IN")) return true;
  } catch {
    // fall through
  }
  // 2) IST timezone — where they physically are, both IANA spellings.
  try {
    const tz = Intl.DateTimeFormat().resolvedOptions().timeZone || "";
    if (tz === "Asia/Kolkata" || tz === "Asia/Calcutta") return true;
  } catch {
    // fall through
  }
  // 3) currency/language hints as a last resort (e.g. a device set to hi/ta/te/bn + INR).
  try {
    const l = getLocales()[0];
    if ((l?.currencyCode || "").toUpperCase() === "INR") return true;
  } catch {
    // fall through
  }
  return false;
}

/**
 * DEV BUILD UPGRADE — read the SIM's registered country (getSimCountryIso via
 * react-native-device-info, or Truecaller's own profile). It is the strongest signal
 * available because it reads the SIM CARD ITSELF, not the number they type and not the
 * network they are on, so a VPN cannot move it and it is ready before the screen paints.
 *
 * Not usable in Expo Go (native module), hence the regionCode above for now. When it lands,
 * try SIM first and fall back to regionCode — do NOT delete the fallback, since wifi-only
 * tablets and eSIM-less devices have no SIM country at all.
 *
 * It still stays a DEFAULT, not a gate (see shouldOfferPhone).
 */

/**
 * Which path leads. A DEFAULT, NEVER A GATE — see shouldOfferPhone().
 * India leads with the phone field; everyone else leads with Google/email.
 */
export function shouldAskForPhone(): boolean {
  return deviceLooksIndian();
}

/**
 * Whether the phone path is REACHABLE AT ALL. Always true, deliberately.
 *
 * This is the difference between a default and a gate, and it is the whole reason we do not
 * geo-detect. The timezone hint WILL be wrong sometimes (VPNs, travellers, an Indian phone
 * set to another region, and the Calcutta/Kolkata split above, which bit us in testing). If a
 * wrong hint could HIDE the phone path, an Indian user would be silently locked out of the
 * cheap route with no way back. So the hint only chooses what leads; the other path is always
 * one tap away, and a non-Indian who takes it gets an honest message from sendCode() rather
 * than a dead end.
 */
export function shouldOfferPhone(): boolean {
  return true;
}

/**
 * True when Truecaller can verify this device in one tap.
 * Expo Go: always false (the native SDK is not in the binary).
 * Dev build: replace the body with the SDK's isUsable().
 */
export async function isTruecallerAvailable(): Promise<boolean> {
  return false;
}

/** One-tap Truecaller. Unreachable until the dev build; kept so the screen's branch exists now. */
export async function verifyWithTruecaller(): Promise<VerifyResult> {
  return { ok: false, error: "Truecaller needs the dev build" };
}

/** Ask for a code to be sent. Faked today — see the header. */
export async function sendCode(phoneE164: string): Promise<VerifyResult> {
  if (!isE164(phoneE164)) return { ok: false, error: "That number doesn't look right." };
  if (!isIndianPhone(phoneE164)) {
    // Deliberate: paid international SMS is Rs 1-8.7 a message for users we do not have yet.
    return { ok: false, error: "We can only text Indian numbers right now. Use email instead." };
  }
  await new Promise((r) => setTimeout(r, 650)); // let the button's sending state be visible
  return { ok: true };
}

/** Check the code. Faked today: accepts DEV_CODE only. */
export async function checkCode(phoneE164: string, code: string): Promise<VerifyResult> {
  await new Promise((r) => setTimeout(r, 450));
  if ((code || "").trim() === DEV_CODE) return { ok: true };
  return { ok: false, error: "That code isn't right. Try again." };
}
