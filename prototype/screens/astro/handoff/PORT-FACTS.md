# ASTROLO — Port Facts Sheet

Answers the porting questions directly. Pair this with `SOURCE-DUMP.md` (all code),
`PORT-TO-RN.md` (deep per-screen spec + RN mapping), `../../FEATURES.md` (content/behaviour
source of truth), and `shots/` (19 screenshots). Everything runs at `screens/astro/`.

---

## 1. Does `Home.html` run fully standalone?

**No — it is a runtime-Babel prototype, not a bundle.** It needs four external things plus its
own sibling files. There is **no `package.json`, no build step, no bundler config** — Babel
transpiles the `.ts`/`.tsx` in the browser on load.

**External (CDN, hard requirement — needs internet):**
- `react@18.3.1` (unpkg, UMD, `react.development.js`, with integrity hash)
- `react-dom@18.3.1` (unpkg, UMD, with integrity hash)
- `@babel/standalone@7.29.0` (unpkg, with integrity hash) — transpiles the script tags
  (`data-presets="typescript"` for `theme.ts`; `data-presets="react,typescript"` for the rest)
- **Google Fonts** via `<link>`: `Manrope` (400,500,600,700,800), `Newsreader`
  (italic+roman, optical size 6..72, 400,500), `Spline Sans Mono` (500,600)

**Local siblings (same folder, relative `src`), in load order:**
`theme.ts` → `astro.tsx` → `astro-today.tsx` → `astro-plan.tsx` → `astro-screens.tsx`, then an
inline bootstrap: `ReactDOM.createRoot(#root).render(<window.AstroApp/>)`.

**Local images (relative `src`):** `chatfab.png`, `chatsage1.png`, `chatsage2.png`,
`chatsage3.png`, `sage2.png`. (`sage1.png` is present but **unused**.)

**Self-contained in `Home.html` itself:** all CSS (one `<style>` block: reset, the phone
`#frame`/`#screen`/`#notch`/`#statusbar` chrome, and **every `@keyframes`** — see §5), and a
tiny `fit()` script that scales the 412×892 frame to the viewport. The status-bar battery/signal
glyphs are inline SVG. No other inline data.

> The phone frame (`#frame`, `#notch`, `#statusbar`, the 9:41 clock) is **presentation chrome for
> the web preview** — drop it on the native port; the OS provides the real status bar.

---

## 2. Every asset it loads

### Images (PNG, local, transparent) — the Sage companion art
| File | Dimensions | Used by | Meaning |
|---|---|---|---|
| `chatfab.png` | 351×373 | `MoonFAB` (`astro-today.tsx`) | floating companion button, every screen but Chat; art already reads as a chat bubble |
| `chatsage1.png` | 407×411 | `ChatScreen` header | **idle** state (before you speak) |
| `chatsage2.png` | 420×418 | `ChatScreen` header | **thinking** state (while replying) |
| `chatsage3.png` | 425×425 | `ChatScreen` header | **delivered** state (after a reply) |
| `sage2.png` | 234×294 | `JournalScreen` done view | Sage holding a heart, with the warm reply |
| `sage1.png` | 280×282 | — | **present but unused**; safe to drop |

The three `chatsage*` files are **stacked and cross-faded by opacity** (all three mounted; the
active one at opacity 1). Keep the exact files + relative paths on port
(`require('./chatsage1.png')`, or Expo Asset). The companion is a **cute sage** — no face-swaps,
no moon, despite the component still being named `MoonFAB` internally.

### Icons — NOT an icon library
All icons are **inline hand-authored SVG**, no font/package:
- `PATHS` map in `astro.tsx` — ~40 stroked glyphs (Ionicons-*shaped* geometry: bell, share,
  chevrons, clock, mic, send, trash, pause, check, close, plus, arrows, compass, wand, scan,
  capsule, calendar, today/timeline/people/rituals/readings tab marks, heart, work, coin, sun,
  moonp, leaf, target, spark, sync, user, ring). Rendered by the `Icon` component.
- Custom one-off SVGs: `Flame`, `MoodSigil` (**12** per-mood celestial line-marks),
  `MoonGloss`, `PhaseMoon` (the sky moon), `EclipseGlyph` (solar/lunar), the big **`SkyScene`**
  (the living-sky window in My Day), and `Ganesha` (**unused** legacy).
- **Port recommendation:** render these with `react-native-svg`, copying the `d` paths 1:1
  (fastest, pixel-faithful). `@expo/vector-icons` Ionicons is a close substitute for the `PATHS`
  set if you'd rather use a library, but the custom art (`MoodSigil`, `SkyScene`, `Flame`,
  `EclipseGlyph`) must be `react-native-svg` regardless.

### Fonts (Google Fonts) — see the mismatch note in §3
`Newsreader` (serif), `Spline Sans Mono` (mono), `Manrope` (loaded sans).

---

## 3. Facts sheet

**Type families + weights + roles:**
- **Serif — `Newsreader`** (400, 500; roman + italic; optical size). Role: display, headlines,
  mood words, forecast sentences, quotes, most "feeling" copy. (Code const `SERIF`.)
- **Mono — `Spline Sans Mono`** (500, 600). Role: small tracked/uppercase labels, dates, times,
  axis ticks, "kind" tags. (Code const `MONO`.)
- **Sans — DECISION NEEDED.** The code const `SANS = "'Hanken Grotesk', sans-serif"` (UI text,
  buttons, chips, nav labels), **but `Home.html` loads `Manrope`, not Hanken Grotesk**, and sets
  `body { font-family: 'Manrope' }`. So today the sans text asks for Hanken Grotesk, doesn't get
  it, and falls back to the platform sans (with Manrope only where inheritance reaches). **On
  port, pick one:** either bundle **Hanken Grotesk** (matches the code's intent) or change `SANS`
  to **Manrope** (matches what was actually loading). Recommend Hanken Grotesk — it was the
  intended UI face. Load fonts with `expo-font` / `@expo-google-fonts`.

**Icon library:** none — inline SVG (see §2).

**npm libraries / imports:** **only React 18.3.1 + ReactDOM 18.3.1 + Babel-standalone 7.29.0**,
all via CDN at runtime. No router, no state manager, no UI kit, **no animation library** — all
motion is CSS `@keyframes` + React state + one `requestAnimationFrame` spring in `SkyScene`.
Globals are shared by assigning to `window` (`window.__astroUI`, `window.__astroToday`,
`window.__astroPlan`, `window.AstroApp`, and the `theme.ts` data on `window.*`) — a browser
shim; **on port, replace with real ES module imports.**

**Suggested RN/Expo target libs:** React Navigation (the 5 tabs + the full-screen overlays:
Chat, Wallet, Month, Journal, Notifications), `react-native-reanimated` (the keyframe loops +
the drag-scrub spring), `react-native-svg` (all icons/art), `expo-font`,
`expo-linear-gradient` (the many CSS gradients), `expo-haptics` (My Day / Day-clock ticks —
code currently calls `navigator.vibrate`), and a bottom-sheet lib (or a Reanimated sheet) for
the `Sheet` component.

**Real vs faked / placeholder data — ALL content is mock.** Nothing talks to a server.
- **Hardcoded content** (in `theme.ts`): the 12 moods + forecasts + chips + personal lines +
  life-area lines, `DAY_LINE`, `ECLIPSE`, `ALMANAC`, `FOCUS`, `AHEAD`, `DAY_CLOCK`,
  `PANCHANG_SOON`, `MONTH`, `MUHURAT`, `CAL_DOCTOR`, `ASK_MOMENT`, `TIME_CAPSULE`, `MIRROR`.
  Demo user is **"Aarav", "Tuesday, 17 June"**; balance starts at **108**.
- **Faked logic (deterministic, not real astrology / not AI):** check-in reflection
  (`CHECKIN_REFLECTION` rule table), Ask-the-Moment verdict (indexed by question length),
  Muhurat results (static list + fake "casting" delay), Calendar Doctor (static events + fake
  "scanning" delay), the mood-word cycle, the eclipse solar/lunar toggle, the "+1 diya" earns.
- **Faked interactions:** **chat replies** are a keyword classifier (`pickReply` → low/high/ask/
  warm buckets), **not an LLM**; **voice** everywhere (journal mic, chat mic) is fake — the
  journal's `sendRec` just inserts a canned sentence; "Sync good days", "Open full chart",
  Decode reading tiles, buy/Plus buttons, and the avatar/You tab are **non-functional stubs**.
- **Genuinely live (from the device clock):** the Living-Sky header time-of-day (dawn/day/dusk/
  night), My Day's "now" marker + live status line + the sky scrubber's default position, and
  the Good-&-bad live dot. These recompute from `new Date()`.
- **Safety path (must survive the port, not cosmetic):** both the **chat** (`DISTRESS` keyword
  list) and the **journal** (`MIRROR.distress`) route crisis language to a gentle, non-clinical
  reply pointing to **KIRAN, 1800-599-0019**. Keep this; verify the number per market.

---

## 4. Animations (won't show up in static code review)

All are CSS `@keyframes` (defined in `Home.html`) unless noted. Feel overall: **soft, slow,
calm.** Ambient loops use `ease-in-out`; entrances use a smooth decel `cubic-bezier(.2,.85,.25,1)`;
pops use a gentle spring `cubic-bezier(.34,1.5,.5,1)`. A `@media (prefers-reduced-motion: reduce)`
disables **all** of it.

**Ambient loops (infinite):**
- `floatY` — gentle 7px vertical bob, **5–6s**. The Sage FAB, mood emblems, the journal book,
  the wallet flame, the chat sage, the Decode medallion.
- `breathe` — scale 1→1.07, **5–5.5s**. Mood sigil inside the emblem.
- `haloBreathe` — glow halo opacity+scale, **5–6s**. Companion / chat aura / journal glow.
- `glowPulse` — box-shadow bloom, **2.4–4s**. Live "you are here"/status dots, casting core,
  sealed capsule, wallet hero.
- `twinkle` — star opacity flicker, **2.4–5s** (staggered). Night-sky stars (header + SkyScene).
- `cloudDrift` — clouds translateX, **26–34s**. Header + SkyScene day clouds.
- `sheen` / `shimmer` — a moving diagonal highlight, **4–5s** linear. Emblem gloss, the "best"
  window on the day-clock.
- `spinSlow` — rotation, **1–1.5s** (casting rings) up to **40s** (sun rays).
- `skyShoot` (**7s**) shooting star at night · `skyBird` (**30s** linear) bird across the day ·
  `fireflyGlow` (**3–5s**) village lights at dusk/night — all in `SkyScene`.
- `flameFlicker`, `trunkSway`, `incenseRise`, `orbGlow`, `sparkle`, `peekIn` — defined; tied to
  legacy/optional bits (e.g. `trunkSway`/`incenseRise` belong to the unused `Ganesha`).

**Entrances / transitions (one-shot):**
- `riseIn` — cards fade + rise 18px on mount, **0.6s**, **staggered** by a `delay` prop (the
  `rise(ms)` helper) so a screen assembles top-to-bottom.
- `sheetUp` — bottom-sheets slide up from the bottom, **0.42s** decel; scrim uses `fadeIn` 0.25s.
- `fadeIn` — sheet contents, reflections, revealed rows, **0.25–0.4s**.
- `popIn` — the **sealed** Time-Capsule badge, **0.5s** with spring overshoot.
- `coinUp` — a "+1" floats up ~26px and fades on the Diya chip when a coin is earned, **0.8s**.
- `pulseRing` — the companion's unread dot emits an expanding ring, **1.8s**.
- `blink` — chat typing-indicator dots, **1.2s** staggered.
- `sound` / `bar` — voice waveform bars scaleY, **0.7–0.9s** staggered (chat + journal record).

**Interactive / state-driven (JS, not keyframes):**
- **Press feedback** (`Press` component): `transform: scale(0.9–0.99)` on pointer-down, **0.12s
  ease** — used on nearly every tappable.
- **My Day sky scrubber** (`SkyScene`): drag the framed sky → the whole scene **crossfades**
  through the day's gradient and the **sun/moon arc** moves (position from a `sin` arc); on
  release, a **`requestAnimationFrame` spring** eases the preview back to "now" over **~560ms**
  (cubic ease-out). The quality strip + hour labels update live.
- **Reading "why this?"** — inline accordion, `max-height` **0.32s** ease.
- **Check-in** — auto-collapses ~**2.6s** after both chips are picked (a `setTimeout`), with the
  reflection fading in first.
- **Living-Sky header** — tap cycles dawn→day→dusk→night previews (state swap, `background`
  transitions **0.7s**).
- **Chat sage** — the 3 PNG states cross-fade by opacity **0.18s** as `typing`/`userSpoke` flip.
- **Eclipse** — tap the glyph swaps solar⇄lunar (state; content updates instantly).

---

## 5. What to hand over / how to consume

1. **`SOURCE-DUMP.md`** — all six runtime files, full contents (Q: "every file, untruncated").
2. **The six PNGs** in `screens/astro/` (five used + `sage1` unused) — binary, copy as-is.
3. **This file (`PORT-FACTS.md`)** — standalone status, assets, facts, animations.
4. **`PORT-TO-RN.md`** — the deep per-screen spec with tag→RN-primitive mapping and the exact
   layout/behaviour of every screen; **`shots/` (19 PNGs)** — one per screen/state.
5. **`../../FEATURES.md`** — the content/behaviour/voice/economy source of truth (what each
   feature *is*, with exact copy), design-independent.

If Claude Code has the repo directly, it can read the real files under `screens/astro/` instead
of the dump — they are identical. The dump exists for copy-paste handoff.
