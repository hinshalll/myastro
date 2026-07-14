# Start-here prompt for Claude Code — port ASTROLO to React Native + Expo

> Give Claude Code the whole `screens/astro/` folder (source + the 6 PNGs + this `handoff/`
> folder). If you're pasting instead of pointing it at the repo, paste `SOURCE-DUMP.md` (all
> code) and attach the screenshots in `handoff/shots/` (at least `01-today-read-top`,
> `02-today-read-reading`, `05-plan-myday`, `09-chat`). Then paste everything below the line.

---

You are porting an existing, finished mobile-app front-end called **ASTROLO** from a web
React prototype to **React Native + Expo** (Android first, iOS later, one codebase). This is
a **faithful port, not a redesign.** Do not invent features, screens, copy, colours, or
layout. Match the prototype exactly. Where a web technique can't port 1:1, **recreate the
same visual and interaction result** using the RN equivalent named in the docs.

## What ASTROLO is
A warm, premium Vedic-astrology app with a gentle, personal voice (the companion is a cute
sage called **Sage**). It is a clean **white** app; a single daily **mood** (one of 12) tints
only small accents (icons, glows, chips, the diya) — never the white background. It is
deliberately alive: ambient motion, a draggable "living sky", satisfying micro-interactions.

## What I'm giving you
Source (read in this exact order — later files depend on earlier ones):
1. `theme.ts` — all design tokens + all app data/content (no React).
2. `astro.tsx` — the shared design system (palette, Icon set, Press, Sheet, GlossIcon, helpers).
3. `astro-today.tsx` — the Read sub-tab cards + persistent chrome (top cluster, Sage FAB, bottom nav, Read/Plan switcher).
4. `astro-plan.tsx` — the Plan sub-tab: My Day + the living-sky slider, Panchang, Month, tool sheets.
5. `astro-screens.tsx` — Chat, Wallet, Decode, Notifications, Journal, detail sheets, and `AstroApp` (the container that wires all navigation + shared state).
6. `Home.html` — the web host (phone frame + script loading + all @keyframes). In RN this file is replaced by the device + a navigator; **the `<style>` keyframes are your motion source of truth**.

(All six are also concatenated, full and untruncated, in `handoff/SOURCE-DUMP.md`.)

Docs (read fully before writing code):
- `handoff/PORT-FACTS.md` — **read this first**: whether the prototype is standalone, the full asset list, the type/icon/library facts (incl. a font-loading mismatch to resolve), the real-vs-faked-data map, and the animation catalog.
- `handoff/PORT-TO-RN.md` — **the deep, per-feature spec**: exact tokens, the motion catalog, and every screen/component with its exact visuals, interactions, and RN mapping. Your primary build guide.
- `FEATURES.md` (in `screens/`) — the **content/behaviour/voice/economy source of truth**: what each feature *is*, with exact copy, design-independent.
- `HANDOFF.md` + `FRONTEND-EXPLAINER.md` (in `screens/astro/`) — the data-model → backend contract and a short orientation.

Images: `chatfab.png`, `chatsage1.png`, `chatsage2.png`, `chatsage3.png`, `sage2.png` — the
Sage companion art (`sage1.png` is present but unused). Keep these files and their relative references.

Screenshots: `handoff/shots/*.png` — one per screen/state (numbered 01–19). **Treat these as
the visual ground truth.** If your output doesn't look like the screenshot, the output is wrong.

## Hard rules for the port
1. **Primitives:** `div`→`View`, text→`Text`, `img`→`Image`, inputs→`TextInput`, `onClick`→`onPress`. Every tappable uses a `Pressable` with a subtle scale on pressIn/pressOut (the prototype's `Press`, scale ~0.97) — never web `:active`.
2. **Layout:** flexbox only (the prototype already is). Numeric units are already points. Drop the 412×892 frame; use the real screen + `SafeAreaView`.
3. **State-driven, not imperative:** all interactivity is React state/hooks in the source — keep it that way. No DOM/imperative hacks. (The prototype shares modules via `window.*` globals purely as a browser shim — replace with real ES imports.)
4. **Styling:** convert inline style objects to `StyleSheet`-shaped objects (camelCase, numbers). Recreate the two core surfaces — `pill()` (glossy white gradient pill) and `card()` (soft white card) — as shared helpers/components, plus `GlossIcon` (the colourful glossy icon tile). Gradients → `expo-linear-gradient`; shadows → iOS `shadow*` + Android `elevation`; blur (nav bar, scrims) → `expo-blur`.
5. **Motion:** every `@keyframes` in `Home.html` → a `react-native-reanimated` loop (the PORT-FACTS + PORT-TO-RN motion catalogs map each one). Respect `AccessibilityInfo.isReduceMotionEnabled`. Annotate each micro-interaction with a `// MOTION:` comment.
6. **The living-sky slider (My Day) is the signature feature** — build it with `react-native-svg` (the scene) + `react-native-gesture-handler` PanGestureHandler (the drag mapping X→time) + Reanimated (the release ease back to "now"). Get this one right; it's what makes the app feel alive. See PORT-TO-RN §7.1.
7. **Icons:** the prototype's line-icon paths port straight into `react-native-svg` `<Path>`. Where cleaner, `@expo/vector-icons` (Ionicons) is an acceptable substitute for the generic `PATHS` glyphs — but the custom art (`MoodSigil` ×12, `SkyScene`, `Flame`, `EclipseGlyph`) must stay `react-native-svg`.
8. **Bottom-sheets** → `@gorhom/bottom-sheet` (swipe-down-to-close). Full-screen overlays (chat/wallet/month/journal/notifications) → stack screens. Navigation currently lives in `AstroApp` as state; recreate the same nav map with a real navigator (React Navigation) — see PORT-TO-RN §4.
9. **Fonts:** load **Hanken Grotesk** (UI), **Newsreader** (display/serif), **Spline Sans Mono** (tiny labels) via `expo-font`. Note the prototype's HTML only loaded Manrope by mistake; the code intends Hanken Grotesk — use Hanken Grotesk. (PORT-FACTS §3.)
10. **Keep the mood system intact:** 12 moods tint only accents; the page stays white. Don't repaint backgrounds on mood change.
11. **Keep the safety guard:** the Chat + Journal distress-keyword check that surfaces the KIRAN helpline (1800-599-0019) must remain, and should be server-authoritative in production.
12. **Don't build the backend or the unbuilt screens.** Timeline / People / Rituals / You are "coming soon" placeholders; leave them so. Keep the demo data from `theme.ts` as the seed — real endpoints get wired later (see HANDOFF.md + FEATURES.md §9).

## How to work
- First read the docs + source, then restate the file/module structure you'll create and the Expo dependencies you'll add, and list anything genuinely ambiguous. Wait for my OK before writing all the screens if the app is large.
- Build shared atoms first (theme tokens, `pill`/`card`/`GlossIcon`/`Icon`/`Press`/`Sheet`), then the persistent chrome, then Read, then Plan (incl. the sky slider), then the overlays and sheets.
- Match each screen to its screenshot. Call out any place where an RN limitation forces a visual compromise, and propose the closest alternative.
- Deliverables: the Expo project (TypeScript), a `theme.ts` of tokens, and a short note of any spot that needs a human decision.

Begin by reading `handoff/PORT-FACTS.md` then `handoff/PORT-TO-RN.md` in full, then tell me your planned module structure and the Expo packages you'll install.
