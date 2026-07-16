# Auth + OTP Plan — Myastro mobile (canonical)

> ## ⚡ STATE AS OF 2026-07-16 — read this box first, the sections below are the reasoning trail
>
> **DECIDED:** India = **the phone is the ONE door** (Google deliberately NOT beside it). Email is
> asked on the **next** screen (`AddEmail`), where Google returns as one-tap *verified-email
> autofill*, not a login. International = Google/email only, **no phone ever**.
> **Truecaller at the dev build** (free, incl. its free drop-call + OTP fallbacks).
> **DROPPED: WhatsApp** (not dominant outside India/Brazil/Indonesia → forces an SMS fallback
> anyway = the expensive thing we were avoiding). **DROPPED: TextBee, 2Factor (₹600 min).**
> **HanuOTP** (₹0.25, ₹100 min) is the paid fallback ONLY if Truecaller's free path fails Play
> review. **Do not recharge anything.**
>
> **BUILT + browser-verified:** `onboarding/verify.ts` (**the client seam** — the only file that
> changes when we leave Expo Go; faked today, `DEV_CODE="123456"`), phone screen (+91), 6-digit
> `OtpStep`, `AddEmail`, mirrored escape links. `shared/sms/` backend seam (`send_sms`, textbee +
> console adapters, 9/9 routing cases) — built, **now unused**, kept because it costs nothing and
> makes a future sender swap one env var.
>
> **Supabase schema DONE + verified live** (`supabase/schema.sql`, additive + re-runnable):
> phone/phone_verified/full_name/avatar_url/timezone/signup_method/consent_at/consent_version/
> last_seen_at on `app_users`, partial unique index on phone, `owner_contacts` view
> (service-role only), and `on_auth_user_created`/`on_auth_user_updated` triggers whose
> **fill-blanks-only `on conflict` makes duplicate accounts structurally impossible**.
>
> **Android bugs FIXED — one root cause: `elevation`.** `shadow()` = `boxShadow` on web but
> `elevation` on Android. Toggling it on a TextInput's parent re-attaches the ViewGroup and
> drops the keyboard (the <0.5s deselect blocker); under a translucent bg it bleeds through as
> the grey chip rectangle. Fix = `androidLift()` in `kit.tsx`. **Never toggle elevation on or
> near a TextInput on Android; never put elevation over a translucent background.**
>
> **NEXT:** wire the profile save to `/me/profiles`; Truecaller + Google at the dev build
> (§ STAGE 2). Related: `TODAY_TAB_AUDIT.md`, `LOCATION_TIME_AUDIT.md`, `DEMO_DATA_LEDGER.md`.

> Everything about accounts, phone-OTP, user-data collection, and the current open bugs.
> Written 2026-07-16. Read this + `memory/project_onboarding_auth.md` on resume.

## Device / testing
- **User tests on ANDROID** (Expo Go over Wi-Fi to the local backend). NOT iOS. Never call it iOS.
- Apple Sign-In is deferred to the future iOS build (documented in `MOBILE_APP_BLUEPRINT.md`).

## Auth model (decided)
- **Phone number = PRIMARY** login/signup. **Email = secondary/optional.**
- Google sign-in = the social option — native Google Sign-In (`@react-native-google-signin`) + Supabase `signInWithIdToken`; deferred to a **dev build** (Expo Go can't run it). Steps to hand the user later.
- Foundation ready: `mobile/.env` has `EXPO_PUBLIC_SUPABASE_URL` + `EXPO_PUBLIC_SUPABASE_ANON_KEY` (public-safe); `@supabase/supabase-js` + `@react-native-async-storage/async-storage` installed. Supabase project live (`hmspryhmyhegraqccnsh`), keys in backend `.streamlit/secrets.toml`.

## 🚪 ONE DOOR PER SEGMENT — FINAL 2026-07-16 (built + verified in the browser)

**India: the phone is the ONLY door. Google is not offered beside it.** International: Google/email only, no phone, ever.

A second door on the signup screen is what creates every problem we kept circling:
- **Duplicates.** Truecaller Monday + Google Friday = two accounts and a "you lost my chart" report. With one door it cannot physically happen.
- **The awkward chase.** "Do they add the number later?" only exists as a question because a second door let them in without one. One door = we have the number at the door = **100% phone coverage**, which was the original goal.
- **It is what India expects.** Swiggy, Zomato, Cred, PhonePe, Zepto: number, OTP, in. Nobody is confused by it.
- **Truecaller makes it one tap**, so requiring it costs almost no friction. That is what the native SDK actually buys.

**Email is NOT dropped — it moves to the NEXT screen (`AddEmail`).** "Remove Google" meant remove it as a *door*, not remove email from the product. We still collect every address. And **Google returns on that screen** as a one-tap way to fill a *verified* email (plus name + avatar) rather than as a way in — on an already-authenticated account that is identity LINKING, which `on_auth_user_created`'s fill-blanks-only `on conflict` already handles safely. `AddEmail` has a real **"Later"**: hard-blocking someone who has already signed in loses people at the last inch; we re-ask on next open.

**Escape hatches, mirrored, always present:** India screen carries a small "I don't have an Indian number"; the international screen carries "I have an Indian number". The region hint only chooses which door **leads**; both always exist, so a wrong hint costs one tap.

### Region detection — what actually works (learned the hard way)
`deviceLooksIndian()` in `mobile/src/onboarding/verify.ts` is an **OR of several signals**, deliberately. Ranking a single "best" signal was wrong twice in testing:
- **regionCode first was WRONG.** `regionCode` comes from the LANGUAGE setting, not location. Huge numbers of Indian users run "English (United States)" and report `US` while sitting in Mumbai. The real test device reported exactly that: `navigator.language: "en-US"`, yet `languages` included `en-IN` and the timezone was `Asia/Calcutta`. Trusting regionCode alone shipped the international path to an Indian user.
- **Matching only `Asia/Kolkata` was WRONG.** `Asia/Calcutta` is the legacy IANA alias real devices still report.

So: India if **any** locale's regionCode is `IN`, **or** the timezone is IST (both spellings), **or** currency is INR. Timezone tracks where you *are*; language tracks what you *prefer*.
**Dev build upgrade:** SIM country (`getSimCountryIso`) is the strongest signal — it reads the SIM CARD itself, so a VPN cannot move it and it is ready before the screen paints. Try it first, but **keep the fallbacks** (wifi-only tablets have no SIM country). Never geo-IP. Never GPS.

### Status
Built and walked end to end in the browser: phone (+91, leads) → OTP (wrong code rejected, `123456` accepted) → AddEmail → done. Only `verify.ts` is faked.

---

## 🧭 THE IDENTITY MODEL — how the best apps do it (review this, then we finalise)

**The one idea: an account is not a login method.** One door, several keys. The account is the door (one user, one chart, one history); Truecaller / Google / email+password / SMS OTP are just keys. Any key opens the same door. Supabase already models this natively (`auth.users` = the person, `auth.identities` = their keys), so we get it free instead of inventing it.

This dissolves the "if they have a password, then how OTP?" knot: **password and OTP are two keys to the same door.** Have a password → use it, skip the OTP. No password → use the OTP. They never compete.

### The fact that drives the whole design
**Google does not give you the phone number.** There is no phone scope for normal apps: Google returns email, name, picture, nothing else. Truecaller is the mirror image — verified **phone + name**, but no verified email. So **whichever key a user arrives with, something is always missing.** Collecting it afterwards is not a workaround, it is the standard pattern.

### Progressive profiling (the leading pattern)
Never a big form. Ask one thing at a time, later, with a reason attached:
- arrived via **Google** → *"Add your number so you never lose your chart."* → verify (Truecaller one-tap, else OTP)
- arrived via **Truecaller** → *"Add your email so you can get in from anywhere."* (Truecaller sometimes returns an email; if it does, skip the ask)

**ASK, DO NOT BLOCK.** Small "Later", re-ask on next open. Hard-blocking someone who has *already signed in* behind a phone form is how you lose users at the last inch. Asking twice politely gets the number from nearly everyone; demanding it once loses real people.

### Password: offered, never demanded, never at signup
- **No password at signup.** It would add a form immediately after a one-tap Truecaller login, destroying the exact magic the native SDK was added to buy. Violates the cozy/least-clutter rule.
- **`You → Account → Set a password`.** Optional, quiet. One Supabase call (`updateUser({ password })`). After that, email+password login works on the same account.
- Every stored password is a liability (breach surface, support tickets, "I forgot"). Most users neither set one nor need one.

### "Forgot password" is NOT a feature — it IS email OTP
Sending a code to your email to get back in *is literally what a forgot-password flow is*. So we do **not** build a "Forgot password?" link. We build **"Email me a code instead"** on the login screen — one button that is simultaneously a login method, the forgot-password path, and account recovery. Three jobs, one thing, no dead ends.
Also note: Truecaller / Google / phone **cannot be forgotten**. A password is the only key a human can lose. The more passwordless we are, the less any of this matters.

### The real risk is NOT a forgotten password — it is a lost phone
New number, lost SIM, Truecaller uninstalled → phone OTP goes to a dead number → locked out of their whole chart forever. A password would not save them (they would have to remember it). **The verified email is the safety net.** That is the actual reason we always collect it: not data hoarding, it is the only route back in when the phone dies.

### Identity linking — the bug that will bite us
User signs up with Truecaller Monday, returns Friday, taps "Continue with Google" because it is nearer the top → **two accounts, chart "gone"**, and they will report that the app lost their data. **Fix:** when a new key arrives carrying an email/phone that already exists on a verified account, ATTACH it to that account instead of creating a new one. Supabase auto-links matching *verified* emails; the phone↔Google case we handle explicitly. Most important thing in the whole auth story, and invisible when it works.

### The flow
- **Signup** (after the Reveal): Truecaller one-tap / phone → Google → small "use email instead". Order flips on device region (`expo-localization` regionCode): `IN` leads with phone; elsewhere leads with Google/email and **never shows a phone field**.
- **Then** fill the one gap (above), skippable.
- **Login:** Truecaller / Google / email → password if set, else "email me a code".
- **International:** no phone, ever. Email OTP (free, global) or Google. Truecaller cannot serve them and paid international SMS is Rs 1–8.7/msg for users we do not have. Accepted cost: **we will not have phone numbers for international users.** At launch that is ~0 users for an India-first Vedic app; revisit behind the seam if it stops being 0.

### What we collect (and nothing more)
Phone (verified), email (verified), name, birth details (that is the product, not surveillance), timezone/locale, push token, consent timestamps (DPDP). **Not** contacts, not location history. Data minimisation is also less to secure.

---

## ✅✅ THE STAGED PLAN — FINAL 2026-07-16 (read this first; it supersedes everything below)

Two stages, because **Truecaller is a native SDK and cannot run in Expo Go**, and we are not ready to leave Expo Go yet.

### Why this split works
The OTP-code flow needs **no native module**, because the SMS is sent **server-side**. The app only ever calls `POST /auth/otp/send` and never learns who delivered it. So Stage 1 runs happily in Expo Go, and swapping the sender later needs **no app rebuild**. Truecaller is the only piece that forces a dev build, because it is a client-side SDK.

### STAGE 1 — NOW (Expo Go): our own phone → OTP screens, TextBee as the sender
- **Our UI:** phone entry (country picker, defaulted from `expo-localization` `getLocales()[0].regionCode`) → 6-digit code screen.
- **Session:** **Supabase Phone Auth** owns code generation + verification + the JWT (`signInWithOtp` → `verifyOtp`). `/me/*` already requires a Supabase JWT, so this must stay Supabase-owned.
- **Delivery:** Supabase **Send-SMS Auth Hook** → our backend → `send_otp(phone, code)` seam → **TextBee** adapter (sends from the owner's own Android phone via the TextBee gateway app). **Free.**
- **TextBee API key lives on the BACKEND ONLY**, never in the app (same rule as `SUPABASE_SERVICE_ROLE_KEY`).
- **Scope: dev only.** TextBee sends from a personal SIM, so carriers will rate-limit or block it at real volume, and the owner's phone must be powered on and online. Fine while the owner is the only tester; **never ship it**.
- **Gate:** `+91` → SMS OTP. Anything else → **email OTP (Supabase, free, global) or Google**, and we collect no phone number. See the international section below.

### STAGE 2 — LATER (dev build): Truecaller one-tap + Google
Trigger: whenever we build the first dev build. **Google Sign-In already needs one, so both land together.** Nothing in Stage 1 is thrown away (see below).

**Truecaller (free, India-only, no usage limits)**
1. Register the app at `developer.truecaller.com` → get the **partner/app key**. Free.
2. Add the SDK. Official: `truecaller/react-native-sdk`. For Expo, `@dhana-cs/react-native-truecaller` ships a **config plugin** that patches AndroidManifest automatically; `@ajitpatel28/react-native-truecaller` also works via `expo prebuild`. Put the key in `app.json` via the plugin, then `npx expo prebuild` + EAS/local build.
3. Flow: call the SDK's **`isUsable()`** on the auth screen.
   - usable → **one tap, no OTP at all**, free. Best path, ~180M+ Indian users.
   - not usable, `+91` → Truecaller's **own free drop-call fallback** (background missed call); if permissions are refused it falls back to Truecaller's own free OTP. India only.
   - not `+91` → email/Google. Truecaller cannot serve them anyway.
4. **`isUsable()` + the typed country code do ALL the gating.** No geo-IP, no VPN problem, no NRI or tourist edge case.
5. **RISK to verify at Play review:** the drop-call fallback needs phone/call permissions, and Google Play restricts those behind a Permissions Declaration. If that gets hairy, keep our Stage 1 OTP screens and plug in **HanuOTP** (₹0.25) as the paid fallback. This is why we keep the seam.
6. Notes: does **not** work on emulators (real device only). An iOS SDK exists (`truecaller/ios-sdk`) but is irrelevant until the iOS build.

**Google Sign-In**
1. Native `@react-native-google-signin/google-signin` + Supabase `signInWithIdToken`. **Cannot run in Expo Go** — this is the other reason for the dev build.
2. Google Cloud console → OAuth client IDs (Android needs the **SHA-1** of the EAS/local signing keystore; get it from `eas credentials`). Add a **Web** client ID too, which is what Supabase wants.
3. Supabase dashboard → Auth → Providers → Google → paste the Web client ID + secret.
4. Add the config plugin + `webClientId` to `app.json`, rebuild.
5. **Apple stays dropped** until an iOS build exists.

### What carries over from Stage 1 (nothing is wasted)
- The **phone + OTP screens are probably permanent, not throwaway.** Truecaller's own fallback UI is off-brand (it will not match our design), and it carries the Play permission risk above. The likely end state is: Truecaller one-tap as the fast path, **our** screens as the fallback, with the sender swapped TextBee → HanuOTP.
- The **`send_otp()` seam** makes the sender swap one file + one env var, with zero app changes.
- Supabase Phone Auth, the `phone` column, RLS and the email path are all stage-independent.

### Provider decision if/when we need a paid sender
**HanuOTP** (₹0.25 → ₹0.16 at 1k, min recharge ₹100, published tier table, no DLT). **Do NOT recharge now** — TextBee is free for dev and Truecaller's fallback is free at launch. Only pay if Truecaller's drop-call path fails Play review or proves unreliable. Full comparison below.

---

## Earlier decision detail (superseded in sequencing, still correct on the provider maths)

**WhatsApp: DROPPED. TextBee: DROPPED. International SMS: never built.**

Why WhatsApp died: it is only dominant in India/Brazil/Indonesia. In the US (iMessage/SMS), Japan (LINE), Korea (Kakao), China (WeChat) and Russia (Telegram) it is not the default. So a WhatsApp-only OTP would fail a large share of international users, which forces an SMS fallback anyway, which is the expensive thing we were trying to avoid. Two integrations to end up paying the ₹1–8.7/message bill regardless. Correct call to kill it.

**PROVIDER = HanuOTP** (`hanuotp.in`). Verified from their published tier table:
| | HanuOTP | blacksms.in | Fast2SMS | 2Factor |
|---|---|---|---|---|
| no-DLT OTP price | **₹0.25** (100–999), ₹0.16 (1k+), ₹0.15 (10k+), ₹0.14 (100k+) | ₹0.09–0.30 *(claimed)* | **₹5.00** ("Quick SMS" = the only true no-DLT route) | ₹0.15 |
| minimum | **₹100** | ₹10 *(claimed)* | ₹100 | **₹600** ❌ |
| evidence | published tier table | own marketing only | published | published |

- **Fast2SMS is disqualified**: its no-DLT OTP path *is* the "Quick SMS" route at **₹5/SMS**, which routes internationally into India and advertises ignoring consent. 20x HanuOTP and exactly the traffic TRAI blocks. Its ₹0.25 rate is the **DLT** route, which defeats the purpose.
- **2Factor disqualified**: ₹600 minimum.
- **blacksms** may be cheaper but every figure is self-published with no tier table; HanuOTP's ₹100 entry is low enough that this is not worth the risk. Revisit later if volume justifies it.

**GATING = the country code of the number typed, NOT the user's detected location.** Detecting location is a guess; the number is a fact. Geo-gating actively *causes* the bug we are avoiding: an American in Mumbai geo-resolves to India, so we would try to SMS a +1 number at ₹1+; and an NRI in London on a +91 number would be wrongly blocked from the cheap route that works fine for them.
- `+91` → SMS OTP via HanuOTP (₹0.25).
- anything else → **no SMS ever**. Email OTP (Supabase, free, global) or Google.

**Device region is a DEFAULT, never a gate.** Use `expo-localization` → `getLocales()[0].regionCode` (free, offline, instant, no permission, works in Expo Go) to pick which signup path leads: region `IN` → phone-first with an "use email instead" link; anything else → email/Google-first with a small "have an Indian number?" link. Both paths always reachable, so a wrong guess costs one tap and breaks nothing. Do NOT use geo-IP (network call, VPN-defeatable, no benefit here).

**Still build the seam** (`send_otp(phone, code)` behind one backend entry point) — not for TextBee any more, but so HanuOTP → blacksms/anything is one file + one env var, and so the app never knows the provider.

**BLOCKER: needs the user's HanuOTP account + ₹100 recharge + API key** before the adapter can be written and tested for real.

## OTP delivery — THE ORIGINAL PLAN (SUPERSEDED — kept for history)
- **WhatsApp OTP by DEFAULT.** On the phone step, send the OTP over **WhatsApp ONLY**. Do NOT offer an upfront channel choice.
- **Fallback, kept minimal:** AFTER the WhatsApp OTP is sent, if the user has no WhatsApp, show a small secondary **"I don't use WhatsApp"** path → fall back to SMS via **textbee.dev** (sends SMS from the OWNER's personal Android phone via the TextBee gateway app). Keep these AS FEW AS POSSIBLE (owner's own number = cost/deliverability/rate limits). So design to MAXIMISE WhatsApp completion: WhatsApp is default + primary, the "no WhatsApp" link is small/secondary, and we push WhatsApp first (e.g. "resend on WhatsApp" before ever falling back).
- **Why WhatsApp:** SMS to Indian numbers legally requires **DLT/PE registration** (TRAI) on any Indian route — unavoidable + a hassle. WhatsApp Business messages are NOT under the SMS-DLT regime → **no DLT**, cheaper (~₹0.11–0.15 per auth message), better delivery. **textbee.dev** is the free/cheap workaround (P2P SMS from the owner's own SIM, so no DLT) but limited — hence WhatsApp-first.

## "Without DLT" — what it actually means (researched 2026-07-16)

There are **two different things** sold as "no DLT", and only one is safe:

1. **Send under the PROVIDER's registration (legit, cheap).** You skip DLT because the provider already registered *their own* header and templates. Fast2SMS documents this plainly: they offer "two Sender IDs with four predefined message templates" and "the message is sent through the provider's default sender ID". 2Factor, Message Central Verify Now and (presumably) blacksms.in are this category. **Cost ~₹0.15–0.30/OTP.** Trade-off: a generic sender ID, not `MYASTRO`, and fixed template wording. For OTP that is completely fine, and it can stay this way forever.
2. **International grey routes (avoid).** Fast2SMS's "Quick SMS" route openly "relies on international service routes to send SMS to Indian numbers" at **₹5/SMS**, and advertises sending "to DND and non-DND numbers without requiring customer consent". That is 10x the price *and* it is exactly the traffic TRAI has been blocking. Never use this.

So DLT never disappears. It either sits with us or with the provider. Sitting with the provider is the cheap, legitimate answer.

## International OTP — the ~50 paise target is impossible

Real 2026 per-message costs: **USA ≈ $0.011–0.013 (₹1.0–1.2)**, **UAE ≈ $0.099 (₹8.7)**, blended global mix **$0.034–0.052 (₹3–4.5)**. No provider on earth sends international SMS for 50 paise. Note the irony: Twilio charges **$0.114 (≈₹10)** to deliver *into* India, while local Indian providers do it for ₹0.15. India is the cheapest country to send to locally and one of the most expensive to send to from abroad. That is precisely why you use a local provider for India and never try to make one provider do both.

**Therefore: we never build international SMS.** The three-layer answer covers everyone:
- **WhatsApp = primary, for EVERY country.** No DLT anywhere, ~₹0.11–0.15 flat, one integration, global. This is the unlock: WhatsApp does not care what country the number is from.
- **SMS fallback = +91 only.** TextBee now (free), a ₹0.15 provider at launch.
- **Non-+91 user without WhatsApp = email OTP.** Supabase does this free, globally, today, with zero setup. That is the escape hatch, and it costs nothing.

Do NOT gate signup by "is the user in India" — you cannot detect it reliably (VPNs, NRIs on Indian numbers abroad, foreigners in India). Route on the **country code of the number they typed**, which is a fact rather than a guess.

## TextBee now, swap later — the switching cost is ~zero IF we build the seam

The answer to "how hard is it to switch later": **trivial, provided delivery lives behind one interface on the backend.** This repo already does exactly this twice — the ephemeris adapter (the app never calls `swe` directly) and the AI task ladders with fallback. OTP delivery gets the same treatment:

- The app only ever calls our backend. It never knows who sent the message.
- One `send_otp(phone, code)` entry point routes on country code and dispatches to a provider module.
- Switching TextBee → 2Factor = add one file, change one env var. **Zero app changes, zero re-testing of the UI.**

**Decision: use TextBee now (free, fine for dev), build the seam immediately, pick the paid provider at launch with real data.** Because of the seam this choice is low-stakes and reversible, so it is not worth agonising over now.

**Provider shortlist for launch:** **2Factor.in** — ₹0.15/OTP pay-as-you-go, no monthly minimum, established, and it publishes an international price list if ever needed. **blacksms.in** claims ₹0.09–0.30 with a **₹10 minimum recharge** and 2–4h KYC, which is attractive, but every one of those figures comes from blacksms's own marketing pages (their site is largely "BLACKSMS vs <competitor>" SEO pages), so treat it as unverified until we test it with a ₹10 recharge. That ₹10 entry cost makes it cheap to verify for real.

## Implementation approach
- **Supabase Phone Auth** owns OTP generation + verification + session: `supabase.auth.signInWithOtp({ phone })` → `supabase.auth.verifyOtp({ phone, token })`.
- **WhatsApp delivery** via Supabase **"Send SMS" Auth Hook**: Supabase calls the hook with `{ phone, otp }`; the hook delivers the code over WhatsApp instead of SMS. Provider options:
  - **Meta WhatsApp Cloud API** (recommended for cost — no monthly fee, ~₹0.11/auth msg; needs a Meta Business account + business verification + an approved `authentication` template), or
  - a **BSP** (AiSensy / Interakt / Gupshup / MSG91) — easier guided setup, usually a small monthly fee.
- **textbee.dev fallback:** the hook (or backend) calls the TextBee API to send the OTP SMS from the owner's phone (TextBee app installed on owner's Android + API key). Only used when the user has no WhatsApp.
- **Owner setup tasks (only the user can do):** (a) WhatsApp Business API sender (Meta Cloud API or a BSP) + approved auth template; (b) TextBee app on their Android + API key. Claude wires the Supabase hook + the app's phone/OTP screens.

## Onboarding flow change for phone-primary
- Current: welcome → name → place → time → reveal → **signup(email)** → done.
- New: the **signup step becomes phone → OTP** (WhatsApp), email optional. Login = phone → OTP. Redesign `mobile/src/onboarding/Auth.tsx` (SignUp/Login) to phone-primary. Build the phone-number + OTP-entry screens (can build UI + Supabase calls now; WhatsApp delivery needs the hook/setup).

## User-data collection + storage (SAFE PRACTICE — the standard we follow)
- Store PII (phone in E.164, email, name, birth details) in **Supabase Postgres**.
- **Row Level Security (RLS)** on every user table so each user reads/writes ONLY their own rows (already the pattern for profiles / checkins / journal / etc.).
- **`service_role` key = SERVER-ONLY, never in the app.** App uses the anon key + the user's JWT (RLS-scoped). Supabase encrypts at rest + TLS in transit.
- **Owner views all contacts** via the Supabase dashboard (Table editor — you're the project owner) or a service-role admin path server-side (auth-gated to owner). NEVER expose a "list all users" endpoint to the app.
- Verified phone → stored by Supabase in `auth.users.phone`; **mirror it to the user's `profiles`/`app_users` row** for easy querying + a contacts view.
- **Need to add a phone column** — current `profiles` (ProfileIn) + `app_users` have NO phone field yet. Add `phone` (+ maybe `phone_verified`) and, if wanted, a `contacts` admin view.
- Data minimisation + consent (privacy policy/terms already on the signup screen). India **DPDP Act**: consent, purpose limitation, deletion rights.

## FIXED 2026-07-16 — both Android bugs had ONE root cause: `elevation`

**Diagnosis.** `shadow()` (`mobile/src/ui/palette.ts:64`) returns `boxShadow` on web but on native returns `elevation` — and on Android `elevation` is the only part it actually paints. That single prop caused both bugs:

1. **Input focus (the blocker).** `Field` toggled `shadow({... elevation: 2 })` onto the View that **directly wraps the TextInput** whenever `foc` flipped true. Changing elevation makes Android re-attach that view's native ViewGroup, which clears the focused EditText and drops the keyboard. Loop: tap → focus → `setFoc(true)` → elevation 0→2 → re-attach → blur → `setFoc(false)` → elevation gone. That's the sub-0.5s deselect.
   - *Proof by elimination:* on tap the ONLY thing that ran was `setFoc(true)`, and of everything it restyled (label colour, background, border colour) all are pure paint except the shadow. Web was unaffected because `boxShadow` is paint-only, which is exactly why focus held 12s+ in the browser.
   - *Control:* the Today Chat + Journal inputs DID work on device, and both have a **static** container with no focus state and no elevation toggle.
2. **Selected-chip grey rectangle.** The active `SoftChip` put an elevation shadow under a **translucent** background (`aA(violet, 0.09)`), so the shadow bled through the chip as a grey inner rounded rect.

**Fix.** `androidLift()` in `kit.tsx` — returns `shadow()` on iOS/web, `null` on Android. Applied to every place elevation toggles or sits near an input: `Field` focus ring, `SoftChip` active, `TimeOption` active/inactive, and the place-suggestion panel (which mounts beside the focused place input, so an elevation there would knock the keyboard down mid-search). Active chip/card backgrounds also swapped from translucent `aA(violet, .09/.07)` to their opaque twins `P.violetTint` (#F2EFF6) / `P.violetTintSoft` (#F5F3F8) — identical to the eye over the white page, but no bleed. On Android the violet border + tint carry the focused/selected state; iOS and web keep the soft glow. Also made `OScreen`'s `KeyboardAvoidingView` iOS-only (it had no behavior on Android, so it only ever caused extra re-renders).

**Verified:** typecheck clean; web preview unchanged (Welcome + Step 1 + Male chip render identical, no console errors); LocationIQ place suggestions confirmed live. **Android device confirmation still pending** — that's the one thing web can't prove.

**Follow-up:** `Rise` still renders statically on native (`kit.tsx`) from the earlier, unsuccessful focus-steal theory. Now that the real cause is fixed, restore the staggered native entrance and re-test on device — it was never the culprit (the animation finishes ~1s after mount, long before the tap).

## OPEN BUGS
- None known on Android pending the device re-test above.

## Reveal (settled — do NOT re-add AI)
- The Reveal is **PRE-WRITTEN from verified atoms, NO AI** (user rule: AI only with RAG; the reveal has no RAG so no AI). `features/chart/service.py::reveal()` composes real Sun/Moon/Rising + `SIGN_ESSENCE` + the Moon's `NAKSHATRA` body + shadow. Spot-checked vs multiple live sources (Bharani, Cancer) — holds up. Scary-accurate comes from the nakshatra **shadow**, not a model. Each line matched to its card. No jargon, no em dashes.
