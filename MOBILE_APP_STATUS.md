# Mobile App (Expo RN) — Status, Map & Next Steps

> Canonical doc for the `mobile/` Expo React Native app. Claude Code hand-ported the
> ASTROLO web prototype (`prototype/screens/astro/`) to Expo RN. **The whole frontend is
> built and verified 1:1 on web.** This file is the single source of truth for what's
> where, how to run it, the gotchas already solved, and what to do next. Keep it in sync.

---

## 1. Status — DONE + verified 1:1 on web (matches prototype `handoff/shots/`)

- **Read sub-tab** (shots 01–03): TopCluster, LivingSkyHeader (time-aware sky), EclipseCard,
  ReadingCard (hero), LifeAreas, JournalCard (the Mirror), RitualPill, CheckIn sheet+chip,
  MoonFAB (the **Sage**), BottomNav, SubTabs, EclipseSheet, AreaSheet.
- **Plan sub-tab** (shot 05): MyDay + the **SkyScene living-sky drag slider** (signature
  feature — drag to scrub the day, sun/moon arc, settle-to-now 560ms), AskMomentCard,
  MyPanchang, tool sheets (Muhurat / Calendar Doctor / Ask the Moment / Time Capsule).
- **Overlays**: ChatScreen (shot 09, 3-state Sage crossfade + **KIRAN 1800-599-0019 distress
  guard, VERIFIED firing**), WalletScreen (10/11), DecodeScreen (12), NotifScreen (14),
  JournalScreen (15, ruled page + voice overlay + sage2 done view), MonthScreen (full calendar).
- Mood engine works: tapping the mood word re-tints all accents; background stays white.
- **Placeholders (intentionally "coming soon", NOT built):** Timeline (= The Path, build LAST
  per PATH_TAB_SPEC.md), People, Rituals, and the You/profile area.

Everything is demo data right now (from `mobile/src/theme.ts`). Nothing talks to the backend yet.

---

## 2. Stack + EXACT pinned versions (do NOT bump)

- Expo **SDK 54** (React 19.1.0 / RN 0.81.5). Matches the user's Expo Go. Do not upgrade the SDK.
- **react-native-reanimated = 4.1.0 (exact)** and **react-native-worklets = 0.5.1 (exact)**.
  ⚠️ These MUST stay pinned. Expo Go SDK 54's *native* worklets is 0.5.1; if npm pulls the
  newer 4.1.7 / 0.8.3, the phone red-screens with `installTurboModule called with 1 arguments
  (expected 0)`. `expo install --fix` does NOT catch this (worklets is transitive). babel plugin
  = `react-native-worklets/plugin` (must be LAST in babel.config.js).
- react-native-gesture-handler 2.28, react-native-svg 15.12, expo-linear-gradient, expo-blur,
  expo-haptics, expo-font + @expo-google-fonts/{hanken-grotesk,newsreader,spline-sans-mono},
  react-native-safe-area-context. `babel-preset-expo` installed explicitly (Metro needs it).
- Web preview deps: react-dom, react-native-web, @expo/metro-runtime.

---

## 3. How to run

**On the phone (native — the real target):** `cd mobile && npx expo start --clear` then scan the
QR in **Expo Go (SDK 54)**. The `--clear` matters after any dep change.

**On web (Claude Code's verification target):** preview_start with launch.json config name
**`mobile-web`** (`npx expo start --web --port 8081`, cwd `mobile`) → open http://localhost:8081.
Resize the Browser pane to `mobile` for accurate layout. First web bundle takes ~1 min.
Force a rebuild by curling `http://localhost:8081/index.bundle?platform=web&dev=true`.

---

## 4. File map (`mobile/`)

```
App.tsx                     loads fonts, wraps <AstroApp/> in GestureHandlerRootView +
                            SafeAreaProvider + a dev ErrorBoundary (prints real crash msg)
babel.config.js             babel-preset-expo + react-native-worklets/plugin (LAST)
src/
  theme.ts                  ALL demo data + tokens (the frontend's data CONTRACT). MOODS,
                            MOOD_BY_KEY, CYCLE, DAY_CLOCK, LIFE_AREAS, LIFE_AREA_META, READ_CHIPS,
                            PERSONAL_LINES, ECLIPSE, MIRROR, PANCHANG_SOON, MONTH, MUHURAT,
                            CAL_DOCTOR, ASK_MOMENT, TIME_CAPSULE, CHECKIN_REFLECTION, NAME, DATE…
  safety.ts                 KIRAN guard: DISTRESS list + isDistress(). Shared by Chat + Journal.
  AstroApp.tsx              the container. ALL navigation is state-driven (tab/sub/screen/sheet
                            useState — NO React Navigation). bal/bump/wrote/checkin/eclType state.
                            Renders overlays as early returns; sheets at the bottom.
  ui/
    palette.ts              colors + aA() + font helpers sans()/serif()/mono() + shadow strings
                            + cardStyle(). NOTE: fonts need exact per-weight family names.
    motion.ts               every Home.html @keyframes as a reanimated hook (useFloatY, useBreathe,
                            useHalo, useTwinkle, useCloudDrift, useSpin, useGlowPulse, usePulseRing,
                            useSheen, useRiseIn) + useReduceMotion.
    Icon.tsx                PATHS icon set + <Icon> + <Flame> (react-native-svg).
    atoms.tsx               Press (Animated Pressable), Pill (glossy gradient), Label, GlossIcon,
                            RadialGlow.
    mood.tsx                MoodSigil×12, MoodEmblem, PhaseMoon, EclipseGlyph.
    Sheet.tsx               bottom sheet (reanimated slide-up + swipe-down + tap-scrim close).
    BackBar.tsx             back-button header for overlays.
    useAppFonts.ts          loads the 3 google-font families.
  today/
    chrome.tsx              TopCluster (+CoinFloat), MoonFAB (Sage), SubTabs, BottomNav (frosted).
    LivingSkyHeader.tsx     time-of-day sky card (dawn/day/dusk/night), stars/clouds/sun/moon.
    read.tsx                EclipseCard, ReadingCard, LifeAreas, JournalCard, RitualPill.
    CheckIn.tsx             CheckInSheet + CheckInChip.
    sheets.tsx              EclipseSheet + AreaSheet.
  plan/
    SkyScene.tsx            the signature living-sky drag slider (svg scene + Pan + RAF settle).
    MyDay.tsx               schedule + status pill + add-task + SkyScene.
    PlanTab.tsx             PlanTab + AskMomentCard + MyPanchang.
    toolsheets.tsx          Muhurat / CalendarDoctor / AskMoment / TimeCapsule + Casting loader.
    MonthScreen.tsx         full-screen month calendar + day sheet.
    util.ts                 nowH/fmtH/qFill/qColor/qWord.
  screens/
    ChatScreen.tsx          Chat with Sage (openers, pickReply keyword buckets, KIRAN guard).
    WalletScreen.tsx        Diyas wallet.
    DecodeScreen.tsx        Readings hub (kundli anchor + readings + tools grid).
    NotifScreen.tsx         notifications.
    JournalScreen.tsx       the Mirror (ruled page + voice overlay + sage2 done view + KIRAN guard).
  assets/                   chatfab.png, chatsage1/2/3.png, sage2.png, sage1.png(unused).
```

---

## 5. Gotchas already solved (don't re-hit these)

1. **Worklets crash** — see §2. Pin reanimated 4.1.0 + worklets 0.5.1.
2. **`babel-preset-expo` missing** — Metro transform fails until it's an explicit devDep.
3. **GlossIcon icons invisible on web** — react-native-web paints `position:absolute` siblings
   ABOVE `position:static` children regardless of DOM order, so an icon placed after the absolute
   gradient layers is buried. FIX (applied to GlossIcon + BottomNav readings button + CheckInChip
   dot + Decode kundli emblem): wrap the icon child in
   `<View style={{position:'absolute',inset:0,alignItems:'center',justifyContent:'center'}}>`.
   MoodEmblem already did this. (Renders fine on native either way; this is a web-fidelity fix.)
4. **Event-as-onPress-arg crash** — `onTap={goChat}` passed the click EVENT as goChat's `seed`
   arg → rendered an event object as a React child → crash. Rule: never pass a state-setter /
   arg-taking fn directly as `onPress`/`onTap`; wrap it `() => fn()`. goChat also guards non-string.
5. **Recoverable web-only console error** — a React-19 + reanimated-4-web artifact ("Objects are
   not valid as a React child" with an event-like object) fires once on load from `entering=
   {FadeIn}` layout animations; React retries and the app renders fine. Web-dev-only, NOT on
   native. Do not rabbit-hole.
6. **Fonts** — RN needs the exact per-weight family name (sans(700) etc.), not fontWeight.
7. **lineHeight** — web multipliers (1.45) converted to absolute points per-usage.
8. **Shadows (IMPORTANT, fixed 2026-07-14)** — do NOT use RN `boxShadow` strings for shadows:
   on the phone (Expo Go/native) they render as hard, opaque SQUARES, and any `0 0 Npx` "glow"
   becomes a square halo, and a drop shadow on a rounded tile with `overflow:'hidden'` is
   clipped to a square. Use the `shadow({ y, blur, opacity, color, elevation })` helper in
   `ui/palette.ts` instead — it emits a real CSS box-shadow on web and `shadow*`+`elevation`
   on native (soft, rounded, transparent everywhere). For a rounded tile that needs
   `overflow:'hidden'`, put `shadow()` on a NON-clipping OUTER wrapper (give it the tile's
   solid `backgroundColor` so iOS casts a rounded shape) and clip the gloss on an inner view —
   this is done for GlossIcon, MoodEmblem, the Readings nav button, the sky header, the kundli
   emblem, the SkyScene frame, and the Wallet Plus card. Round "glows" (moon/sun) use
   `RadialGlow` (react-native-svg), and ring effects (`0 0 0 3px`) become a wrapper circle.
9. **`filter: drop-shadow` on images (fixed 2026-07-14)** — RN 0.81 (New Arch) DOES support CSS
   `filter` natively, so `filter:drop-shadow` on the Sage PNGs traced their irregular / rounded
   chat-bubble alpha and cast a squarish shadow on the phone. Removed it from the Sage FAB and
   the Chat + Mirror sage images; the round glow halos already behind them give the lift (the
   FAB got a small dark `RadialGlow` ground shadow). Rule: don't use `filter:drop-shadow` for a
   soft round shadow — it follows the image's real (often square-ish) shape.
10. **Input focus outline / "golden border" (fixed 2026-07-14)** — react-native-web draws a focus
    outline on inputs via a stylesheet rule inline `outlineWidth:0` can't beat; it showed as a
    square gold border poking past the rounded Mirror page. Fixed once, globally, with a web-only
    `<style>` injected in `App.tsx` (`input:focus,textarea:focus{outline:none!important}`). Also
    set `underlineColorAndroid="transparent"` on every TextInput for the Android underline.
11. **Keyboard covering inputs (fixed 2026-07-14)** — full-screen input screens (Chat, Mirror)
    are wrapped in `KeyboardAvoidingView behavior={ios?'padding':'height'}`; bottom sheets lift by
    the keyboard height via a `Keyboard` listener in `ui/Sheet.tsx` (`kb` shared value subtracted
    from the panel translateY). Assumes Expo Go is NOT auto-resizing the window (matches device
    behavior seen). Needs on-device confirmation.

---

## 6. NEXT — wire the live backend (decided strategy)

**Wire the Today tab to the live Render APIs FIRST (one full vertical slice), NOT finish all
screens first.** Rationale: Today is the daily-driver; wiring one tab end-to-end solves every
integration problem once (auth, API client, shape mismatches, loading/error states, base URL),
after which the rest is fast. Avoids a 100%-fake app that hits all integration snags at the end.

**Frontend ↔ backend edit workflow (the seam):**
- Frontend edits → `mobile/src/`. The data CONTRACT (expected shapes) = `mobile/src/theme.ts`.
- Backend edits → `features/*/api.py` + `shared/*` (already live on Render; see SYSTEM_REFERENCE.md,
  TODAY_FUNCTIONING.md, FEATURE_SPEC.md).
- **Reconciliation seam (to build):** `mobile/src/api/` = a fetch client (base URL = Render) +
  one adapter fn per endpoint that maps the backend response into the shape the components already
  use. Mismatches get fixed in the adapter (or the endpoint). Then swap theme.ts demo data for
  real fetches; add loading/error states. Keep the KIRAN guard server-authoritative.
- **To build:** `MOBILE_API_MAP.md` — a table: each Today UI element → endpoint → request →
  response shape → how it maps. Single source of truth for the contract.

**Then:** Chat (real AI+RAG endpoint, keep KIRAN server-side), Decode (real kundli), then build +
wire the remaining tabs (Timeline/People/Rituals/You).

**Immediate step on resume:** confirm the phone boots (user runs `npx expo start --clear` + reload
in Expo Go). Once green, build `mobile/src/api/` + `MOBILE_API_MAP.md` and wire the Today Read tab.
