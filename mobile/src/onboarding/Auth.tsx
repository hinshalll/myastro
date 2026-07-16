// Auth.tsx — Step 5 Sign-up, plus Login (returning users) and Done ("You're all set").
// Ported from screens/onboarding/onboarding-reveal.tsx. The name is already captured in the
// Reveal, so Sign-up only needs email + password (+ Apple/Google).
// WIRE: providers + email/password currently just advance (matches the prototype). Real
//   Supabase auth (@supabase/supabase-js) + POST /me/profiles with the captured `data` is the
//   next pass — see MOBILE_API_MAP.md (Onboarding).
import React, { useEffect, useMemo, useRef, useState } from "react";
import { View, Text, TextInput, Platform } from "react-native";
import Animated from "react-native-reanimated";
import Svg, { Circle, Path } from "react-native-svg";
import { serif, sans, mono, aA, shadow } from "../ui/palette";
import { useSpin } from "../ui/motion";
import {
  P, OScreen, StepChrome, PrimaryButton, TextLink, Field, PasswordField, ProviderButton, Rise, useTopPad, androidLift,
} from "./kit";
import { NatalWheel, Halo, buildChart } from "./Reveal";
import type { OnbData } from "./data";
import {
  DEV_CODE, VERIFY_IS_FAKED, sendCode, checkCode, isIndianPhone, shouldAskForPhone, shouldOfferPhone, isTruecallerAvailable,
} from "./verify";

const firstName = (data: OnbData, fallback = "friend") => (data.name || "").trim().split(" ")[0] || fallback;

// ============================ STEP 5 — SIGN UP ====================================
// Phone-first in India, Google/email-first everywhere else. The order is a DEFAULT, never a
// gate: both paths are always reachable, so a wrong guess costs one tap (see verify.ts).
export function SignUp({ data, step, onBack, onDone, onGoogle, onPhone }: any) {
  const top = useTopPad(20);
  const first = firstName(data);
  const [phone, setPhone] = useState("");
  const [email, setEmail] = useState("");
  const [pwd, setPwd] = useState("");
  const [emailMode, setEmailMode] = useState(!shouldAskForPhone());
  const [tc, setTc] = useState(false);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  // In the dev build this flips true for Truecaller users and they never see OtpStep.
  useEffect(() => { isTruecallerAvailable().then(setTc).catch(() => {}); }, []);

  const e164 = "+91" + phone.replace(/\D/g, "").slice(0, 10);
  const phoneReady = isIndianPhone(e164);
  const emailReady = /.+@.+\..+/.test(email) && pwd.length >= 6;

  const goPhone = async () => {
    if (!phoneReady || busy) return;
    setBusy(true); setErr(null);
    const r = await sendCode(e164);
    setBusy(false);
    if (r.ok) onPhone ? onPhone(e164) : onDone();
    else setErr(r.error || "Couldn't send the code.");
  };

  return (
    <OScreen crown={0.18} scroll keyboard stars>
      <View style={{ flexGrow: 1, paddingTop: top, paddingBottom: 34, paddingHorizontal: 26 }}>
        <StepChrome step={step} onBack={onBack} />
        <View style={{ height: 30 }} />
        <Rise delay={120} dist={12}><Text style={{ fontFamily: mono(500), fontSize: 10.5, letterSpacing: 2.4, textTransform: "uppercase", color: P.violet, marginBottom: 12 }}>One last thing</Text></Rise>
        <Rise delay={200} dist={14}><Text style={{ fontFamily: serif(500), fontSize: 32, lineHeight: 36, color: P.ink, letterSpacing: -0.5 }}>Keep your chart safe, {first}.</Text></Rise>
        <Rise delay={300} dist={12}><Text style={{ fontFamily: sans(400), fontSize: 15, lineHeight: 23, color: P.inkMid, marginTop: 10 }}>So your readings, your journal, and your streak are always here when you come back.</Text></Rise>

        {!emailMode ? (
          <>
            {/* INDIA = ONE DOOR: the phone, and nothing beside it.
                Google is deliberately absent here. A second door on this screen is what
                creates duplicate accounts (Truecaller Monday + Google Friday = two accounts
                and a "you lost my chart" report), and it is also what forces an awkward
                "now add your number" chase later. One door means we have the number at the
                door, 100% coverage, and the duplicate bug cannot physically happen.
                Truecaller makes it a single tap, so requiring it costs almost no friction.
                Email is NOT dropped — it is asked on the NEXT screen (AddEmail), where
                Google returns as a one-tap way to FILL a verified email rather than as a
                way in. See AUTH_OTP_PLAN.md "THE IDENTITY MODEL". */}
            {tc ? (
              <Rise delay={400} dist={14} style={{ marginTop: 30 }}>
                <ProviderButton kind="truecaller" label="Continue with Truecaller" onPress={onDone} />
              </Rise>
            ) : (
              <Rise delay={400} dist={14} style={{ marginTop: 30 }}>
                <PhoneField value={phone} onChange={(v: string) => { setPhone(v); setErr(null); }} />
                {err ? <ErrLine text={err} /> : null}
                <View style={{ marginTop: 16 }}>
                  <PrimaryButton label={busy ? "Sending…" : "Send me a code"} disabled={!phoneReady || busy} onPress={goPhone} />
                </View>
              </Rise>
            )}
            {/* the escape hatch — small, but ALWAYS there, so a wrong region hint costs one tap */}
            <Rise delay={520} dist={12} style={{ alignItems: "center", marginTop: 20 }}>
              <TextLink label="I don't have an Indian number" onPress={() => setEmailMode(true)} color={P.inkMid} />
            </Rise>
          </>
        ) : (
          <>
            <Rise delay={400} dist={14} style={{ marginTop: 30 }}>
              <ProviderButton kind="google" label="Continue with Google" onPress={onGoogle || onDone} />
            </Rise>
            <Rise delay={500} dist={12} style={{ flexDirection: "row", alignItems: "center", gap: 12, marginTop: 22 }}>
              <View style={{ flex: 1, height: 1, backgroundColor: P.line }} />
              <Text style={{ fontFamily: mono(500), fontSize: 10.5, letterSpacing: 1.5, textTransform: "uppercase", color: P.inkFaint }}>or</Text>
              <View style={{ flex: 1, height: 1, backgroundColor: P.line }} />
            </Rise>
            <Rise delay={600} dist={12} style={{ marginTop: 22 }}>
              <Field label="Your email" value={email} onChange={setEmail} placeholder="you@email.com" keyboardType="email-address" autoCapitalize="none" />
              <View style={{ marginTop: 14 }}><PasswordField label="Create a password" value={pwd} onChange={setPwd} placeholder="At least 6 characters" /></View>
              <View style={{ marginTop: 16 }}><PrimaryButton label="Create my account" disabled={!emailReady} onPress={() => emailReady && onDone()} /></View>
              {/* The mirror of the India escape link. ALWAYS offered, never gated on the region
                  hint — the hint is wrong often enough (it read Asia/Calcutta on a real Indian
                  device in testing) that hiding this would lock an Indian user out of the phone
                  path with no way back. */}
              {shouldOfferPhone() ? (
                <View style={{ alignItems: "center", marginTop: 16 }}>
                  <TextLink label="I have an Indian number" onPress={() => setEmailMode(false)} color={P.inkMid} />
                </View>
              ) : null}
            </Rise>
          </>
        )}

        <View style={{ flex: 1, minHeight: 20 }} />
        <View style={{ alignItems: "center", marginTop: 22 }}>
          <Text style={{ fontFamily: sans(400), fontSize: 12, lineHeight: 19, color: P.inkFaint, textAlign: "center" }}>
            By continuing you agree to our <Text style={{ fontFamily: sans(500), color: P.inkMid }}>Terms</Text> and <Text style={{ fontFamily: sans(500), color: P.inkMid }}>Privacy Policy</Text>.
          </Text>
        </View>
      </View>
    </OScreen>
  );
}

// a quiet inline error line (violet-free: errors read warm, not alarming)
function ErrLine({ text }: { text: string }) {
  return <Text style={{ fontFamily: sans(500), fontSize: 12.5, lineHeight: 18, color: P.warn, marginTop: 10 }}>{text}</Text>;
}

// PhoneField — fixed +91 prefix beside the input. Only India is offered a phone field at all,
// so this is a label rather than a country picker; when a second country is ever supported it
// becomes a Dropdown here and nothing else on the screen changes.
function PhoneField({ value, onChange }: any) {
  const [foc, setFoc] = useState(false);
  return (
    <View style={{ width: "100%" }}>
      <Text style={{ fontFamily: mono(500), fontSize: 10, letterSpacing: 1.6, textTransform: "uppercase", color: foc ? P.violet : P.inkFaint, marginBottom: 8 }}>Your number</Text>
      {/* androidLift: never toggle elevation on a TextInput's parent — it re-attaches the view
          and drops the keyboard. See kit.tsx. */}
      <View style={{ borderRadius: 14, backgroundColor: foc ? P.paper : P.field, borderWidth: 1.5, borderColor: foc ? P.violet : P.line, paddingHorizontal: 16, flexDirection: "row", alignItems: "center", gap: 10,
        ...(foc ? androidLift({ y: 6, blur: 18, opacity: 0.26, color: P.violet, elevation: 2 }) : null) } as any}>
        <Text style={{ fontFamily: sans(600), fontSize: 17, color: P.inkSoft }}>+91</Text>
        <View style={{ width: 1, height: 22, backgroundColor: P.line }} />
        <TextInput
          value={value}
          onChangeText={(v: string) => onChange(v.replace(/\D/g, "").slice(0, 10))}
          placeholder="98765 43210"
          placeholderTextColor={P.inkFaint}
          keyboardType="phone-pad"
          onFocus={() => setFoc(true)}
          onBlur={() => setFoc(false)}
          style={{ flex: 1, height: 54, fontFamily: sans(500), fontSize: 17, letterSpacing: 0.5, color: P.ink, ...(Platform.OS === "web" ? { outlineWidth: 0 } : null) } as any}
          underlineColorAndroid="transparent"
        />
      </View>
    </View>
  );
}

// ============================ OTP — the 6-digit code ==============================
// Real screen, permanent. Only verify.ts underneath it is faked today.
export function OtpStep({ phone, step, onBack, onDone }: any) {
  const top = useTopPad(20);
  const [code, setCode] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [secs, setSecs] = useState(30);
  const ref = useRef<TextInput>(null);

  useEffect(() => { const t = setInterval(() => setSecs((s) => (s > 0 ? s - 1 : 0)), 1000); return () => clearInterval(t); }, []);

  const submit = async (c: string) => {
    if (c.length !== 6 || busy) return;
    setBusy(true); setErr(null);
    const r = await checkCode(phone, c);
    setBusy(false);
    if (r.ok) onDone();
    else { setErr(r.error || "That code isn't right."); setCode(""); }
  };

  const resend = async () => { setErr(null); setSecs(30); await sendCode(phone); };

  return (
    <OScreen crown={0.18} scroll keyboard stars>
      <View style={{ flexGrow: 1, paddingTop: top, paddingBottom: 34, paddingHorizontal: 26 }}>
        <StepChrome step={step} onBack={onBack} />
        <View style={{ height: 30 }} />
        <Rise delay={120} dist={12}><Text style={{ fontFamily: mono(500), fontSize: 10.5, letterSpacing: 2.4, textTransform: "uppercase", color: P.violet, marginBottom: 12 }}>Check your messages</Text></Rise>
        <Rise delay={200} dist={14}><Text style={{ fontFamily: serif(500), fontSize: 32, lineHeight: 36, color: P.ink, letterSpacing: -0.5 }}>Enter your code.</Text></Rise>
        <Rise delay={300} dist={12}>
          <Text style={{ fontFamily: sans(400), fontSize: 15, lineHeight: 23, color: P.inkMid, marginTop: 10 }}>
            We sent six digits to <Text style={{ fontFamily: sans(600), color: P.ink }}>{phone}</Text>.
          </Text>
        </Rise>

        <Rise delay={420} dist={14} style={{ marginTop: 32 }}>
          <CodeBoxes value={code} onPress={() => ref.current?.focus()} err={!!err} />
          {/* one real input behind the boxes: the OS keyboard + SMS autofill both need a genuine
              TextInput, and six separate inputs fight each other over focus on Android */}
          <TextInput
            ref={ref}
            value={code}
            onChangeText={(v) => { const d = v.replace(/\D/g, "").slice(0, 6); setCode(d); setErr(null); if (d.length === 6) submit(d); }}
            keyboardType="number-pad"
            textContentType="oneTimeCode"
            autoComplete="sms-otp"
            maxLength={6}
            autoFocus
            style={{ position: "absolute", opacity: 0, height: 1, width: 1 }}
          />
          {err ? <ErrLine text={err} /> : null}
          {VERIFY_IS_FAKED ? (
            <View style={{ marginTop: 14, paddingVertical: 10, paddingHorizontal: 14, borderRadius: 12, backgroundColor: P.violetTintSoft, borderWidth: 1, borderColor: aA(P.violet, 0.18) }}>
              <Text style={{ fontFamily: sans(500), fontSize: 12.5, lineHeight: 18, color: P.violetDeep }}>
                Dev build: no SMS is sent yet. Enter {DEV_CODE} to continue.
              </Text>
            </View>
          ) : null}
          <View style={{ marginTop: 18 }}>
            <PrimaryButton label={busy ? "Checking…" : "Verify"} disabled={code.length !== 6 || busy} onPress={() => submit(code)} />
          </View>
          <View style={{ alignItems: "center", marginTop: 14 }}>
            {secs > 0
              ? <Text style={{ fontFamily: sans(400), fontSize: 13, color: P.inkFaint }}>Resend in {secs}s</Text>
              : <TextLink label="Send it again" onPress={resend} color={P.violet} strong />}
          </View>
        </Rise>

        <View style={{ flex: 1, minHeight: 20 }} />
      </View>
    </OScreen>
  );
}

// ============================ ADD EMAIL (after the phone) =========================
// The number got them in the door; this gets the recovery key. Kept as its OWN screen and
// NOT bolted onto signup on purpose: asking for everything at once is the form nobody fills.
//
// Two things worth knowing about this screen:
//  1. Google here is NOT a login. They are already authenticated by phone. This is identity
//     LINKING onto the existing account — one tap for a *verified* email plus their name and
//     avatar, instead of making them type an address we then cannot trust. The schema's
//     on_auth_user_created trigger fills blanks only, so this can never fork the account.
//  2. "Later" is real. Hard-blocking someone who has ALREADY signed in is how you lose people
//     at the last inch; we re-ask on next open instead. We get the email from nearly everyone
//     by asking twice politely, and lose real users by demanding it once.
//
// Why email matters enough to have its own screen: the real risk is not a forgotten password,
// it is a LOST PHONE. New number, lost SIM, Truecaller uninstalled -> the OTP goes to a dead
// number and the whole chart is gone. The verified email is the only way back in.
export function AddEmail({ data, step, onBack, onDone, onSkip, onGoogle }: any) {
  const top = useTopPad(20);
  const first = firstName(data);
  const [email, setEmail] = useState("");
  const ready = /.+@.+\..+/.test(email);
  return (
    <OScreen crown={0.18} scroll keyboard stars>
      <View style={{ flexGrow: 1, paddingTop: top, paddingBottom: 34, paddingHorizontal: 26 }}>
        <StepChrome step={step} onBack={onBack} />
        <View style={{ height: 30 }} />
        <Rise delay={120} dist={12}><Text style={{ fontFamily: mono(500), fontSize: 10.5, letterSpacing: 2.4, textTransform: "uppercase", color: P.violet, marginBottom: 12 }}>Almost there</Text></Rise>
        <Rise delay={200} dist={14}><Text style={{ fontFamily: serif(500), fontSize: 32, lineHeight: 36, color: P.ink, letterSpacing: -0.5 }}>One way back in, {first}.</Text></Rise>
        <Rise delay={300} dist={12}>
          <Text style={{ fontFamily: sans(400), fontSize: 15, lineHeight: 23, color: P.inkMid, marginTop: 10 }}>
            If you ever change your number, this is how we find your chart again. We won't send you anything you didn't ask for.
          </Text>
        </Rise>

        <Rise delay={400} dist={14} style={{ marginTop: 30 }}>
          <ProviderButton kind="google" label="Use my Google email" onPress={onGoogle || onDone} />
        </Rise>

        <Rise delay={500} dist={12} style={{ flexDirection: "row", alignItems: "center", gap: 12, marginTop: 22 }}>
          <View style={{ flex: 1, height: 1, backgroundColor: P.line }} />
          <Text style={{ fontFamily: mono(500), fontSize: 10.5, letterSpacing: 1.5, textTransform: "uppercase", color: P.inkFaint }}>or</Text>
          <View style={{ flex: 1, height: 1, backgroundColor: P.line }} />
        </Rise>

        <Rise delay={600} dist={12} style={{ marginTop: 22 }}>
          <Field label="Your email" value={email} onChange={setEmail} placeholder="you@email.com" keyboardType="email-address" autoCapitalize="none" />
          <View style={{ marginTop: 16 }}><PrimaryButton label="Save it" disabled={!ready} onPress={() => ready && onDone()} /></View>
          <View style={{ alignItems: "center", marginTop: 16 }}>
            <TextLink label="Later" onPress={onSkip || onDone} color={P.inkMid} />
          </View>
        </Rise>

        <View style={{ flex: 1, minHeight: 20 }} />
      </View>
    </OScreen>
  );
}

// six boxes that mirror the hidden input
function CodeBoxes({ value, onPress, err }: any) {
  const cells = Array.from({ length: 6 });
  return (
    <View style={{ flexDirection: "row", gap: 8 }} onTouchEnd={onPress}>
      {cells.map((_, i) => {
        const ch = value[i] || "";
        const active = i === value.length;
        return (
          <View key={i} style={{ flex: 1, height: 58, borderRadius: 12, alignItems: "center", justifyContent: "center",
            backgroundColor: ch ? P.paper : P.field, borderWidth: 1.5,
            borderColor: err ? P.warn : ch || active ? P.violet : P.line }}>
            <Text style={{ fontFamily: serif(500), fontSize: 24, color: P.ink }}>{ch}</Text>
          </View>
        );
      })}
    </View>
  );
}

// ============================ LOGIN (returning users) =============================
export function Login({ onBack, onDone, onFresh, onGoogle }: any) {
  const top = useTopPad(20);
  const [email, setEmail] = useState("");
  const [pwd, setPwd] = useState("");
  const ready = /.+@.+\..+/.test(email) && pwd.length >= 1;
  return (
    <OScreen crown={0.16} scroll keyboard>
      <View style={{ flexGrow: 1, paddingTop: top, paddingBottom: 34, paddingHorizontal: 26 }}>
        <StepChrome step={0} total={5} onBack={onBack} />
        <View style={{ height: 22 }} />
        <Rise delay={120} dist={12}><Text style={{ fontFamily: mono(500), fontSize: 10.5, letterSpacing: 2.4, textTransform: "uppercase", color: P.violet, marginBottom: 12 }}>Welcome back</Text></Rise>
        <Rise delay={200} dist={14}><Text style={{ fontFamily: serif(500), fontSize: 34, lineHeight: 38, color: P.ink, letterSpacing: -0.5 }}>Good to see you again.</Text></Rise>

        <Rise delay={300} dist={14} style={{ marginTop: 34 }}>
          {/* Apple Sign-In deferred to the iOS build (see MOBILE_APP_BLUEPRINT.md). Android = Google + email. */}
          <ProviderButton kind="google" label="Continue with Google" onPress={onGoogle || onDone} />
        </Rise>

        <Rise delay={420} dist={12} style={{ flexDirection: "row", alignItems: "center", gap: 12, marginTop: 22 }}>
          <View style={{ flex: 1, height: 1, backgroundColor: P.line }} />
          <Text style={{ fontFamily: mono(500), fontSize: 10.5, letterSpacing: 1.5, textTransform: "uppercase", color: P.inkFaint }}>or</Text>
          <View style={{ flex: 1, height: 1, backgroundColor: P.line }} />
        </Rise>

        <Rise delay={560} dist={12} style={{ marginTop: 22 }}>
          <Field label="Email" value={email} onChange={setEmail} placeholder="you@email.com" keyboardType="email-address" autoCapitalize="none" />
          <View style={{ marginTop: 14 }}><PasswordField label="Password" value={pwd} onChange={setPwd} placeholder="Your password" /></View>
          <View style={{ marginTop: 16 }}><PrimaryButton label="Log in" disabled={!ready} onPress={() => ready && onDone()} /></View>
          {/* NOT a "Forgot password?" link. Sending a code to your email IS what a forgot-password
              flow is, so this ONE button is the login method, the recovery path, and the
              forgot-password flow at once. Also: most users here never set a password (they
              arrive via Truecaller/Google), so a "forgot" link would be nonsense to them, while
              "email me a code" always works. See AUTH_OTP_PLAN.md "THE IDENTITY MODEL". */}
          <View style={{ alignItems: "center", marginTop: 16 }}>
            <TextLink label="Email me a code instead" onPress={() => {}} color={P.violet} strong />
          </View>
        </Rise>

        <View style={{ flex: 1, minHeight: 20 }} />
        <View style={{ flexDirection: "row", alignItems: "center", justifyContent: "center", marginTop: 22 }}>
          <Text style={{ fontFamily: sans(400), fontSize: 13.5, color: P.inkMid }}>New here? </Text>
          <TextLink label="Create an account" onPress={onFresh} color={P.violet} strong />
        </View>
      </View>
    </OScreen>
  );
}

// the gold ceremonial seal ring (slow counter-rotation)
function SealRing({ size = 176 }: { size?: number }) {
  const spin = useSpin(90);
  const r = size / 2 - 4;
  return (
    <Animated.View pointerEvents="none" style={[{ position: "absolute", width: size, height: size }, spin]}>
      <Svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <Circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke={aA(P.gold, 0.34)} strokeWidth={1} strokeDasharray={[2, 9]} strokeLinecap="round" />
      </Svg>
    </Animated.View>
  );
}

// ============================ DONE (lands in the app) =============================
export function Done({ data, onEnter, onReplay }: any) {
  const top = useTopPad(0);
  const first = firstName(data);
  const chart = useMemo(() => buildChart(data), [data]);
  return (
    <OScreen crown={0.24}>
      <View style={{ flex: 1, alignItems: "center", justifyContent: "center", paddingTop: top, paddingHorizontal: 34 }}>
        {/* the living emblem, sealed */}
        <Rise delay={150} dist={0}>
          <View style={{ width: 176, height: 176, alignItems: "center", justifyContent: "center" }}>
            <Halo size={198} opacity={0.36} />
            <SealRing size={176} />
            <NatalWheel chart={chart} prog={1} size={150} lit={3} />
            {/* saved badge */}
            <View style={{ position: "absolute", right: 16, bottom: 16, width: 36, height: 36, borderRadius: 999, alignItems: "center", justifyContent: "center", borderWidth: 2.5, borderColor: P.paper, backgroundColor: P.violet, ...shadow({ y: 8, blur: 20, opacity: 0.5, color: P.violetDeep, elevation: 5 }) } as any}>
              <Svg width={18} height={18} viewBox="0 0 24 24" fill="none"><Path d="M5 12.5 10 17.5 19.5 7" stroke="#fff" strokeWidth={2.6} strokeLinecap="round" strokeLinejoin="round" /></Svg>
            </View>
          </View>
        </Rise>

        <Rise delay={520} dist={12}><Text style={{ fontFamily: mono(500), fontSize: 10.5, letterSpacing: 2.6, textTransform: "uppercase", color: P.violet, marginTop: 32 }}>Your chart is sealed</Text></Rise>
        <Rise delay={660} dist={14}><Text style={{ fontFamily: serif(500), fontSize: 31, lineHeight: 35, color: P.ink, marginTop: 8, textAlign: "center", letterSpacing: -0.4 }}>You're all set, {first}.</Text></Rise>
        <Rise delay={800} dist={12}><Text style={{ fontFamily: sans(400), fontSize: 15.5, lineHeight: 23, color: P.inkMid, marginTop: 12, textAlign: "center", maxWidth: 290 }}>It's saved to the sky and to your phone. Today is already waiting for you.</Text></Rise>

        <Rise delay={1020} dist={14} style={{ marginTop: 40, width: "100%", maxWidth: 300 }}>
          <PrimaryButton label="Enter" onPress={onEnter} />
          <View style={{ alignItems: "center", marginTop: 14 }}><TextLink label="Replay onboarding" onPress={onReplay} color={P.inkFaint} /></View>
        </Rise>
      </View>
    </OScreen>
  );
}
