# ASTROLO — Port-to-React-Native Spec (deep, per-feature)

> **Read this with the screenshots in `handoff/shots/` open beside you.** This document
> describes every screen and component precisely enough to **rebuild the exact look**
> even where a 1:1 code port isn't possible. It is generated from the real source
> (`Home.html`, `theme.ts`, `astro.tsx`, `astro-today.tsx`, `astro-plan.tsx`,
> `astro-screens.tsx`). Where code and this doc disagree, **the code wins** — reread it.
>
> Companion docs: **`HANDOFF.md`** (data models = backend contract, endpoint list,
> prototype-shortcuts-to-undo) and **`FRONTEND-EXPLAINER.md`** (short overview).
>
> Target: **React Native + Expo**, Android first, iOS later, one codebase. The web
> prototype is written so its STRUCTURE maps 1:1 to RN (View/Text/Pressable, flexbox,
> numeric units, state-driven motion). It is NOT a fake RN shim — it's real web React.

---

## 0. The package you were handed

| File | What it is |
|---|---|
| `Home.html` | Phone-frame host: loads React 18 + Babel + the 4 script files, draws the 412×892 bezel. **In RN this whole file is replaced by the device + a navigator.** |
| `theme.ts` | ALL design tokens + ALL app data/content (no React). Your backend contract. |
| `astro.tsx` | Shared design system (palette, `Icon`, `Press`, `Sheet`, `GlossIcon`, helpers). |
| `astro-today.tsx` | The Read sub-tab cards + persistent chrome (TopCluster, MoonFAB, BottomNav, SubTabs). |
| `astro-plan.tsx` | The Plan sub-tab: MyDay + the living-sky slider, Panchang, Month, tool sheets. |
| `astro-screens.tsx` | Chat, Wallet, Decode, Notifications, Journal, detail sheets, and **`AstroApp`** (the container that wires all navigation + shared state). |
| `handoff/shots/*.png` | 19 screenshots, one per screen/state (referenced throughout). |
| `chatfab.png`, `chatsage1/2/3.png`, `sage2.png` | The **Sage** companion art (see §11). |

**Load / dependency order (must preserve as import order in RN):**
`theme.ts` → `astro.tsx` → `astro-today.tsx` → `astro-plan.tsx` → `astro-screens.tsx`.
In the web build each file is an IIFE that reads globals off `window` (`__astroUI`,
`__astroToday`, `__astroPlan`) and attaches its own. **In RN, convert these to normal ES
module imports** — the sharing graph is already laid out by that order.

---

## 1. Design system — exact tokens (`astro.tsx`)

**This is "ASTROLO-clean white": a bright white app where only small accents carry the
day's mood colour.** (Note: `theme.ts` also exports a warm-ivory `THEME` object — that is
**legacy/reference, NOT used by the live UI**. Match `astro.tsx`, not `THEME`.)

### Palette (constants)
```
PAPER   #FFFFFF   screen background, cards
WASH    #F4F4F6   insets, textarea fills, secondary chips
INK     #0C0B0A   primary text, solid CTAs
INK2    #3A3733   secondary text / body serif
GRAY    #9A958C   tertiary text, captions, inactive icons
HAIR    rgba(12,11,10,0.07)   hairline borders
ORANGE  #DF6B35   alert/notification dot, "avoid" accents
```
Helper `aA(hex, alpha)` → `rgba()` string. Used everywhere for tinting.

### Fonts — IMPORTANT discrepancy to fix on port
- The code references: **SANS = 'Hanken Grotesk'**, **SERIF = 'Newsreader'**, **MONO = 'Spline Sans Mono'**.
- But `Home.html` only `<link>`s **Manrope, Newsreader, Spline Sans Mono** — Hanken Grotesk is **not loaded**, so on web the sans text currently falls back to the system sans.
- **On port, load all three intended families via `expo-font`: Hanken Grotesk (400/500/600/700/800), Newsreader (400/500 + italic), Spline Sans Mono (500/600).** Newsreader is the display/editorial serif (mood word, greetings, headings, body reads); Hanken Grotesk is UI/labels/buttons; Spline Sans Mono is the tiny UPPERCASE tracked labels + times.

### Surfaces (two helpers everything is built from)
- **`pill(radius=999, extra)`** — the soft glossy pill/button surface:
  - `background: linear-gradient(180deg, #FFFFFF 0%, #F1F1F3 100%)`
  - `border: 1px solid rgba(0,0,0,0.05)`
  - `boxShadow: inset 0 1px 0 #FFFFFF, 0 1px 2px rgba(26,20,8,0.04), 0 6px 16px -8px rgba(26,20,8,0.14)`
  - RN: LinearGradient + `borderRadius` + layered shadow (iOS `shadow*`, Android `elevation` ~2; the inset highlight → a 1px top border of `#FFF`).
- **`card(extra)`** — soft white card: `background #FFF`, `borderRadius 22`, `border 1px solid HAIR`, `boxShadow 0 1px 2px rgba(26,20,8,0.03), 0 14px 30px -18px rgba(26,20,8,0.16)`.

### `Label`
Tiny uppercase section label: Hanken, `fontSize 11.5`, `fontWeight 700`, `letterSpacing 1.6`, `textTransform uppercase`, default colour GRAY (often passed `aA(accentDeep,0.9)`). Used above nearly every card.

### `GlossIcon({c1,c2,size=36,radius=11})`
The colourful glossy rounded-square icon tile seen on almost every row: a `linear-gradient(160deg, c1, c2)` square, a top 45%-height white highlight overlay, `boxShadow inset 0 1px 1px rgba(255,255,255,.6), 0 3px 8px -3px c2@.7`, an icon centered inside. **This is a core repeated motif — build it once.**

### `Icon({n, s=20, c=INK, sw=1.7})`
Inline SVG line-icon set; `PATHS` in `astro.tsx` holds ~40 named glyphs (bell, share, chevR/D/U, plus, sync, capsule, compass, wand, scan, arrowR/L, close, check, mic, send, trash, pause, clock, today, timeline, people, rituals, readings, heart, work, coin, spark, sun, moonp, leaf, target, cal, user, ring). RN: `react-native-svg` `<Path stroke=… strokeWidth=… strokeLinecap="round" strokeLinejoin="round"/>` — paths port verbatim. Also `Flame` (filled teardrop, the diya symbol) and `MoodSigil` (12 per-mood line marks, see §4).

### `Press({onClick, scale=0.97})`
Tap wrapper: scales to `scale` on pointer-down, back on up/leave, `transition transform .12s`. **RN: `Pressable` with an Animated/Reanimated scale on `pressIn`/`pressOut`.** Every tappable in the app uses this — do NOT use web `:active`.

### `Sheet({open, onClose})` — the bottom-sheet
- Dim backdrop `rgba(12,11,10,0.4)` (fade in .25s), tap to close.
- Panel: bottom-anchored, `maxHeight 84%`, `overflowY auto`, `background #FFF`, `borderRadius 30px 30px 0 0`, top shadow, padding `14px 22px 30px`, slides up `translateY(100%)→0` over `.42s cubic-bezier(.2,.85,.25,1)`.
- A 38×4 grey grab-handle centered at top.
- **RN: use `@gorhom/bottom-sheet` (or Reanimated + PanGestureHandler); support swipe-down-to-close.** All "detail" content opens here. The ONLY full-screen push from Today is the Month calendar.

---

## 2. Motion catalog (every animation + RN mapping)

All keyframes live in `Home.html`'s `<style>`. All are **decorative loops or state-driven
eases** — no layout-coupled hacks. `@media (prefers-reduced-motion: reduce)` disables all;
**honour `AccessibilityInfo.isReduceMotionEnabled` in RN.** Map each to a
`react-native-reanimated` `withRepeat(withTiming/withSpring)` loop.

| Keyframe | Effect | Where | Typical duration |
|---|---|---|---|
| `floatY` | translateY 0→-7→0 | mood emblem, Sage FAB, book emblem, wallet flame, kundli emblem | 5–7s |
| `breathe` | scale 1→1.07→1 | mood sigil inside emblem | `mood.feel.breathe` (3.6–9s) |
| `haloBreathe` | opacity+scale pulse | glows behind FAB, chat head, journal done | 5s |
| `glowPulse` | boxShadow pulse (`--gc`) | live dots, casting core, wallet aura, current clock segment | 2.4–4s |
| `sheen` | diagonal white sweep | mood emblem, "best" clock segment | 4–5s linear |
| `twinkle` | opacity `--lo`→`--hi` | header stars, sky-scene stars | 2.4–6s |
| `cloudDrift` | translateX 0→26→0 | header + sky-scene clouds | 26–34s |
| `riseIn` | opacity+translateY(18→0) | card entrance (via `rise(delayMs)` stagger) | .6s cubic-bezier(.2,.85,.25,1) |
| `popIn` | opacity+scale(.86→1) | sealed capsule badge | .5s spring-ish |
| `fadeIn` | opacity 0→1 | sheet content, reveal blocks | .25–.4s |
| `sheetUp` | translateY(100%→0) | bottom-sheet | .42s |
| `coinUp` | translateY 0→-26, fade | "+1" diya float on the chip | .8s |
| `spinSlow` | rotate 360 | casting rings, sun rays | 1–40s linear |
| `blink` | opacity+y | chat typing dots | 1.2s staggered |
| `sound` / `bar` | scaleY pulse | chat & journal voice waveform bars | .7–.9s |
| `skyShoot` | shooting star streak | sky-scene deep night | 7s |
| `skyBird` | translateX arc | sky-scene daytime bird | 30s |
| `fireflyGlow` | opacity pulse | sky-scene village lights (night) | 3–5s |
| `pulseRing` | scale 1→2.4 fade | FAB unread ring, MyDay status ring | 1.8–2.4s |

**Entrance stagger:** `rise(d)` = `riseIn .6s … {d}ms both`. Cards are given increasing
delays (40, 100, 150, 200, 250, 300…) so a screen assembles top-to-bottom. **Base the
end-state on the visible style and animate FROM hidden**, so reduced-motion/no-JS shows content.

**Interactive (state-driven, not keyframes):**
- **Press scale** (§1).
- **The living-sky drag** (MyDay `SkyScene`) — a pointer/`PanGestureHandler` maps X→time; on release a `requestAnimationFrame` cubic ease returns to "now" over 560ms (port to `withTiming(now, {duration:560, easing: cubic})`).
- **Check-in / Ask / Capsule phase machines** — `setTimeout`-driven fake "casting/sealing" then result (replace delays with real API calls; keep the animation).
- **Clock "you-are-here" marker** — `setInterval` updates position; `transition: left 1s linear`. Haptic tick (`navigator.vibrate(8)`) when it crosses a window → **`expo-haptics` `impactAsync(Light)`**.

---

## 3. The mood engine (the core concept)

The day has exactly one of **12 mood keys**: `Settled, Guarded, Bold, Tender, Restless,
Capable, Warm, Deep, Wandering, Driven, Upbeat, Quiet`. Each mood object (`theme.ts` →
`MOODS` / `MOOD_BY_KEY`) carries:
```
key, vibe (one-liner),
accent, accentDeep, glow  → the three colours everything tints from
wash                      → a ~5% tint (legacy; barely used now)
moon                      → moon-body tint
feel { breathe, orbit, twinkle, spring, wobble, drag }  → motion personality (sec / multipliers)
forecast { mood, opportunity, caution, action, why }    → the reading copy
```
Example — **Deep** (the prototype's default): `accent #5B4FC4`, `accentDeep #43399E`,
`glow #9A8CF0`, `moon #E2DEF6`, `feel.breathe 8`. Full palette for all 12 is in `theme.ts`
(each has warm or cool accents matching its feeling; Bold/Driven/Upbeat run hot & fast,
Deep/Quiet/Wandering run cool & slow).

**Rule: the page stays white; the mood only tints accents** — the `GlossIcon` tiles, the
mood emblem, glows, chips' left dots, the diya flame, the elevated Readings nav button,
the reading-card's faint top gradient, sheet accent text. Swapping mood must NEVER repaint
the white background.

**`MoodEmblem`** (the day's glyph, top-right of the reading card, and on placeholders):
a floating glossy rounded-square (`linear-gradient(155deg, glow, accent 55%, accentDeep)`)
with a top white highlight, a looping `sheen`, and the mood's **`MoodSigil`** (a unique
white line-mark per mood — e.g. Deep = concentric circles, Warm = sun, Tender = flame/heart,
Bold = mountain peaks) `breathe`-ing inside. See shot `12-decode.png` (kundli) and the
reading card in `02`.

**Prototype shortcut:** tapping the giant mood word cycles all 12 (for preview). In
production the mood comes from the backend (`/dashboard/today`) — remove the cycle.

---

## 4. Global state + navigation (`AstroApp`)

`AstroApp` (bottom of `astro-screens.tsx`) holds everything; there is **no router** — nav is
conditional rendering off state. Port to a real navigator but preserve this map.

State:
- `moodIdx` → current mood (default **Deep**); `cycle()` advances (preview only).
- `tab` ∈ `Today | Timeline | People | Rituals | Readings` (bottom nav).
- `sub` ∈ `Read | Plan` (Today only; pinned switcher).
- `screen` ∈ `null | chat | wallet | month | journal | notif` → **full-screen overlays** (early-return above tabs).
- `sheet` ∈ `null | eclipse | area | muhurat | doctor | ask | capsule` → bottom-sheets.
- `bal` (diyas, starts **108**), `bump` (fires the +1 float), `earn(n)` = add + bump.
- `wrote` (journaled today), `checkinOpen` (auto-true ~650ms after load), `checkinDone`, `eclType` (solar/lunar), `askSeed`, `chatSeed`, `areaKey`, `showEclipse`.

Navigation intents: `goWallet`, `goChat(seed)`, `goPlan` (sets sub=Plan), `profile()`
(**no-op — You area not built**). Overlays render `<MoonFAB>` too (except chat).

**Diyas (🪔)** = the soft-currency. Earned by gentle acts (check-in +1, ritual +2, journal
+1 — wired via `earn`), spent on readings (Decode prices). Wallet buy/subscribe is static.

---

## 5. Persistent chrome (on most screens)

### TopCluster (`astro-today.tsx`) — shots 01, 12
Row, space-between. **Left:** 44×44 round avatar — a `linear-gradient(145deg, glow, accentDeep)`
ring (2px pad) around a WASH circle with the user's initial in Newsreader; tap → profile
(not built). **Right group (gap 10):** a 42×42 `pill` **bell** button (ORANGE unread dot top-right
when `alert`) → Notifications; then the **Diya chip** — a `pill` pill with `Flame(glow)` +
balance in Hanken 800. When `bump` changes, a `+1` in accentDeep floats up (`coinUp .8s`).
Tap chip → Wallet. On Today it sits under the greeting; on other screens it's pinned at `top:52`.

### MoonFAB — the Sage companion (`astro-today.tsx`) — every screen except Chat; shots 01–19 (bottom-right)
`position:absolute right:14 bottom:94 z:50`. A 68×72 **`chatfab.png`** (the cute sage —
the art already reads as a chat bubble), `floatY 6s`, with a soft radial `glow` halo behind
(`haloBreathe`; brighter when `insight`). Poke (pointer-down) → `scale(1.08) rotate(-3deg)`
spring for 460ms. When `insight` (new message): a 13px red `#E5484D` dot top-right with a
`pulseRing` halo. Tap → Chat. **It is a celestial guide, never a face/pet.**

### BottomNav (`astro-today.tsx`) — shots 01, 05, 12
Frosted bar (`rgba(255,255,255,0.92)` + `backdrop-blur(16px)` → **`expo-blur`**), top hairline,
`padding 10px 8px 18px`. Five slots: **Today · Timeline · [Readings] · People · Rituals**.
Side tabs = line `Icon` (22px) + 10px label, INK when active else GRAY. **Center "Readings"
is elevated**: a 56×56 round glossy button (`linear-gradient(155deg, glow, accent 54%,
accentDeep)`, 3px white border, drop shadow, top highlight) floated up `marginTop:-26` with
the `readings` glyph (a kundli-diamond) in white; label below. This is the Decode hub — the
"heart of the app," visually the hero of the nav.

### SubTabs (Read · Plan) (`astro-today.tsx`) — shots 01, 05
Pinned under the cluster on Today only. A WASH pill track (inset shadow) with two segments;
the active one gets a white raised pill (shadow + top highlight), Hanken 800 INK vs GRAY.
Screen opens on **Read**.

---

## 6. READ sub-tab (top→bottom)

Pinned header (never scrolls): TopCluster + SubTabs, on white with a soft bottom shadow.
Then a scroll body (`padding 10px 18px 130px`). Order below. Shots 01–04.

### 6.1 CheckInChip (only when the check-in was dismissed) — shot 01
A slim `pill` row: a 30px round mood-gradient dot with `Flame`, "How are you today?", chevron.
Opens the check-in sheet. (When not dismissed, the check-in auto-rises as a sheet instead.)

### 6.2 LivingSkyHeader — shots 01, 02 (top)
A 26-radius rounded card whose whole scene is **time-of-day aware** (`nowH()` picks
dawn/day/dusk/night from `SKIES`):
- Each sky = a full gradient + ink/subtext colours + celestial body + star/cloud counts.
  - dawn `linear-gradient(165deg,#F9CD9C,#FBE3C6,#FDF4E9)` sun; day blue sky sun; **dusk
    `#E89A76→#C489AE→#9A82C6` moon** (this is what shots show — "Good evening, Aarav"); night
    `#1F2A4E→#2F3B64→#424E7A` moon + 16 stars.
- Contents (z-above scene): the DATE in mono uppercase; greeting "Good evening, *Aarav*"
  (Newsreader 27, name italic); an optional festival pill; and the **planetary-hour line**
  (`HORA_LINE`) with a pulsing green dot — "a good stretch for money and focus right now."
- Sun = radial-gradient disc + glow; **`PhaseMoon`** = a lit disc with an offset soft-shadow
  carving the phase (demo waxing-gibbous). Stars `twinkle`, clouds `cloudDrift`, body `floatY`.
- **Prototype shortcut:** tapping the card cycles dawn→day→dusk→night to preview; production
  renders only the live one. **The notification bell lives in the TopCluster, not here.**

### 6.3 EclipseCard (conditional — only when an eclipse is near) — shots 01, 02
A `card` row with an accent-tinted border. **Left:** a `GlossIcon` (solar = gold `#F6B24A→#CE7C1B`,
lunar = indigo `#8385C8→#4B4B88`) holding a distinct **`EclipseGlyph`** — solar = rayed gold sun
with a dark bite; lunar = pale moon with a red-brown shadow + craters — plus a small `sync`
badge. **Body:** `Label "Heads up"`, "A {type} eclipse in 3 days", one calming line from
`ECL.short[type]`, chevron. Tap the card → EclipseSheet (§8). **Prototype shortcut:** tapping
the glyph tile toggles solar↔lunar (preview both). Production: render only when `ECLIPSE != null`.

### 6.4 ReadingCard — THE hero — shot 02
The most important card. `card` with a faint `glow@0.07` top gradient. Contents in order:
1. `Label "Today's reading"`, then the **mood word** in Newsreader **48px** (tap cycles — preview).
2. `MoodEmblem` (60px) top-right.
3. The day's sentence — `forecast.mood`, Newsreader 18, INK2.
4. **Personal line** (only if `PERSONAL_LINES[mood]` exists) — an accent dot + italic
   Newsreader 15.5 that "knows the user." Collapses gracefully when null.
5. A hairline, then two **chip rows**: **Good for** (green `#2E7D5B`, tint bg + dot) and
   **Go easy** (red `#B4503E`) — 2–3 chips each from `READ_CHIPS[mood]`. Mono side-labels.
6. On off-days, an italic "a low-key day for you, keep it light."
7. **Strongest-window nugget** — an accent-tinted row: clock icon + "Strongest window today
   · 11:40–12:30" + chevron → **jumps to Plan / My Day** (`goPlan`).
8. Footer: a wide solid-black **"why this?"** button (toggles an inline accordion revealing
   `forecast.why`) + a 48×48 `pill` **share** button.
NOTE: `11:40–12:30` is hardcoded here (and in several unused timing components) — when you
wire `DAY_CLOCK`, centralize this string so nothing contradicts.

### 6.5 LifeAreas — Love · Work · Money — shot 03
`Label "Today across your life"`, then a `card` holding three rows (hairline between). Each:
a `GlossIcon` (Love pink `#E48AA6→#C55C7E` heart, Work blue `#6E86C4→#4C63A0` briefcase, Money
green `#5FA97E→#3E8060` coin), the label, a one-line honest read from `LIFE_AREAS[mood]`
(**names the planet, NO scores/percentages ever**), chevron. Each row → **AreaSheet** (§8).

### 6.6 JournalCard — "The Mirror" — shot 03
A cozy invitation `card` with a `glow@0.12` diagonal wash + a low-right radial glow pocket
and a floating **open-book + ribbon-bookmark SVG emblem** (`floatY`, its own glow). Shows
`Label "The Mirror"`, a rotating invite (Newsreader 24, e.g. "Anything on your heart
tonight?"), an italic sub "set it down here, just for you," and two faint ruled lines. Once
written today, it flips to "You wrote today. I'm holding it for you." + "add a little more."
Tap → JournalScreen (§10). **The emblem is a book/diary — deliberately NOT the Sage or a moon.**

### 6.7 RitualPill — shot 03 (bottom)
`Label "Today's ritual"`, then a `pill` row: a warm `GlossIcon` (`#F5B642→#C77A1E`) with
`Flame`, "light a lamp at dusk · +2 🪔", a one-line reason, and a "Begin →" that **deep-links
to the Rituals tab** (the full step-by-step lives there, not here).

> Components present in `astro-today.tsx` but **NOT mounted in the current Read flow**
> (dead code you can ignore or repurpose): `GoodBadStrip`, `ShouldICard`, `ForToday`,
> `DayClock`, `InFocusChip`, `TodayGlance`, `LookingAhead`. They're fully built if a future
> spec wants them, but the shipped Read = SkyHeader → Eclipse → Reading → LifeAreas →
> Journal → Ritual.

---

## 7. PLAN sub-tab (`astro-plan.tsx`)

No greeting header. Two labelled groups: **"Today"** (MyDay + Ask the Moment) and **"Plan
ahead"** (My Panchang + three tool entries). Shots 05–07.

### 7.1 MyDay + the Living-Sky slider — THE signature feature — shot 05
A `card`:
- Header: `Label "My Day"`, "Schedule today", and a to-do count.
- **Live status pill** — green-tinted when a good window is open now ("A good window, right
  now · clear sailing till 12:30pm"), else accent-tinted ("Best to hold a little · a stronger
  window opens at 11:40am · in 35 min"). Computed from `DAY_CLOCK` vs `nowH()`. A double-ring
  pulsing dot.
- **`SkyScene`** — the star of the app. A framed 300×116 SVG "window into the sky" you
  **drag horizontally to scrub the whole day**. As you drag:
  - Sky gradient interpolates through 8 stops sunrise-peach → midday-blue → golden-dusk →
    starry-night (`lerpHex` between stops by fraction `f=(viewT-sunrise)/24`).
  - A sun **or** moon body arcs along a sine path (`by = 100 - sin(f·π)·66`), crossfading
    at dusk; sun has spinning rays + glow, moon has a shadow-bite + craters + glow.
  - Day layers: drifting clouds + a gliding bird + a warm horizon band near sunrise/sunset.
  - Night layers: a milky-way ellipse, twinkling stars, a periodic shooting star, and
    village lights (`fireflyGlow`) on the hills.
  - Release → eases back to "now" (560ms cubic).
  - Below the frame: a **whole-day quality strip** (segments coloured best `#3E9C7A` /
    good `#6FB894` / neutral `#E0A23C` / hold-rest `#8E93B0`, the current one glowing), a
    **fixed accent "NOW · 3pm" marker** with dot, task dots, an **hour axis (am/pm labels)**,
    and a caption that reads the dragged time ("**2:14pm** · Open afternoon — good for
    important talks") or "drag across the sky to watch your day pass."
  - **RN port:** `react-native-svg` for the scene (paths/gradients port 1:1),
    `PanGestureHandler` for the drag mapping X→`viewT`, Reanimated for the release ease. This
    is the piece to get right — it's what makes the app feel alive.
- **Add-a-task**: a `pill` input ("add a task, we'll place it well") + black + button. On
  add, a spinner "finding the best time…" for 1.3s, then the task **drops onto the best
  upcoming good/best window** (never a hold/rest one) with "8:00am · Building · reminder 15
  min before." Tasks tick off; a quality dot shows each task's window. (Local state — persist
  + real reminders on port.)

### 7.2 AskMomentCard — shot 06
A prominent accent-tinted `card`: `Label "Ask the Moment"`, "Ask, and the sky answers — now",
a wand `GlossIcon` (`#8E7BD6→#5C4FB0`), a sub line, 3 tappable sample-question chips
(white, accent border), and a dashed "…or type your own question" row. Any tap → opens the
**AskMomentSheet** pre-seeded (§8).

### 7.3 MyPanchang — shot 06
A `card`: header + a purple `cal` GlossIcon, then **today + next 2 days** rows, each with a
day/date, a **semantic quality dot** (good green / mixed amber / low grey, with a soft ring),
a "good/mixed/low-key day" word + note. A **"Open full Panchang →"** link → MonthScreen.

### 7.4 Tool entries — shot 07
Three `pill` rows (each a `GlossIcon` + title + one-line description + chevron):
**Find a good day** (compass), **Check my plans** (scan), **Time Capsule** (capsule). Each →
its bottom-sheet (§8).

---

## 8. Bottom-sheets (open over any screen)

All use `Sheet` (§1). Content specs:

- **EclipseSheet** (shot 18) — `Label "Heads up"`, "A {type} eclipse on 21 August",
  `ECL.full[type]`, a WASH "Caution window" block ("The Sutak window begins about 12 hours
  before, around 20 August, 11:30pm"), and the Sanskrit name centered (`सूर्य ग्रहण` solar /
  `चन्द्र ग्रहण` lunar). Fills from `ECLIPSE`.
- **AreaSheet** (shot 19) — Love/Work/Money detail. `GlossIcon` + "{Area} today · {Planet}"
  + "{houses} house", the day's one-line, a "What it means today" paragraph (`LIFE_AREA_META
  [area].detail`), a **"why?"** accordion (`.why`), and **one** contextual link at the foot
  ("See People" / "See your Timeline") shown ONLY because that tab exists.
- **MuhuratSheet** — "What's it for?" → 6 event chips + a "type your own" input → a `Casting`
  loader (1.4s) → top-3 dates with exact times (from `MUHURAT`). "pick something else" resets.
- **CalendarDoctorSheet** — opens on a `Casting` "checking your calendar" (1.7s) → a list of
  upcoming events (`CAL_DOCTOR`); weak-window ones are ORANGE-tinted with a black "move to
  11:50am" button that marks them fixed.
- **AskMomentSheet** — three phases: **ask** (input + sample chips + black "Cast") → **casting**
  (dual spinning rings, 1.4s) → **done** (the quoted question, a huge verdict in Newsreader
  40 — Yes green / Wait amber / Lean B accent — a warm "why", a "one-time read" note, and
  "Talk it through →" that hands the question to Chat + "Ask again"). From `ASK_MOMENT`.
- **TimeCapsuleSheet** (shot 08) — **write** (textarea + "Pick a date" + 3 "or pick a moment"
  options + a "Seal it" CTA + a shelf of sealed/landed capsules) → **sealing** (a 2s glowing
  spinner "sealing it to the sky…") → **sealed** (a `popIn` glowing capsule + "Sealed." +
  "The sky will bring it back to you {when}."). From `TIME_CAPSULE`.
- **WhySheet / GoodBadSheet / TimingSheet** — defined; GoodBad/Timing not mounted in the
  current flow (the reading's why is an inline accordion). Keep for reference.

---

## 9. Chat — "Sage" (`astro-screens.tsx` `ChatScreen`) — shot 09

A full-screen conversation, proactive and personal.
- **Header:** a glowing radial top, a back button, and the **Sage avatar (86×87, `floatY`)**
  with a `haloBreathe` aura. The avatar is **3 stacked PNGs that crossfade by state**:
  `chatsage1.png` (idle, before you speak) · `chatsage2.png` (thinking, while replying) ·
  `chatsage3.png` (delivered, after). Name "Sage", "your guide · always private."
- **Opener:** one of 3 warm, specific openers (`MOON_OPENERS`, picked by day-of-month) with
  a mono "kind" tag (a pattern I noticed / looking back / just checking in) and 2 suggestion
  chips. If seeded from "Talk it through", it starts with that Q + a grounded reply.
- **Bubbles:** user = solid INK, right-aligned, `20 20 6 20` radius; Sage = `pill`, left,
  `20 20 20 6`; safety replies = accent-tinted. `riseIn` on each.
- **Input:** a `pill` with a text field ("Tell Sage…"), a mic toggle (fake "listening…"
  waveform), and a send button. `pickReply()` classifies the text (low / high / question /
  warm) into a templated reply with a typing-dots beat.
- **SAFETY (keep on port, make server-authoritative):** a `DISTRESS` keyword list triggers a
  gentle, non-clinical reply pointing to **KIRAN 1800-599-0019**. This must never be removed.
- **Port note:** replies are keyword templates (prototype) → swap for your LLM; keep the
  distress guard as a hard check. Voice is faked → wire real mic + STT.

---

## 10. The Mirror — Journal (`astro-screens.tsx` `JournalScreen`) — shot 15

Full-screen, cozy. A top `glow` wash, a back/close button, `Label "The Mirror"`.
- **Writing view:** a crescent-moon date chip, "What's on your mind?", "no pressure, no one
  else sees this", and a **ruled cream page** (repeating-linear-gradient lines) holding a
  transparent multiline input (Newsreader 18, 34px line-height). Bottom bar: a round mic
  button + a full-width **"Leave it with me"** CTA (black when there's text). **No Sage on
  the writing page — it feels private/unwatched.**
- **Voice overlay** (mic tap): a blurred scrim, a breathing mic halo, a live waveform, a
  mm:ss timer, and three controls — delete · pause/resume · send. (Faked; sends canned text.)
- **Done view:** the **`sage2.png`** sage (holding a heart, `floatY` + halo) with a warm
  italic response (`MIRROR.responses`, tuned to the entry's feeling — comfort if heavy, a
  quiet smile if happy), "you wrote today", and a "talk about it?" → Chat. Earns +1 diya.
- Never lists past entries — this is for setting things down. Port: persist entries,
  classify tone server-side, run the distress guard.

---

## 11. Diyas Wallet (`astro-screens.tsx` `WalletScreen`) — shots 10, 11

Full-screen scroll under a BackBar.
- **Hero:** a big `Flame(glow, 64)` with a `glowPulse` aura that **brightens with balance**
  (`bright = min(1, 0.4 + bal/500)`), then the balance in Newsreader 52 + "🪔 lit".
- **Earn** `card`: "Light a diya by doing good" + "3 of 5 today"; rows — Daily check-in +1
  (done ✓), Today's ritual +2, A journal note +1, 7-day streak +10, Invite a friend +25.
- **Buy** three `pill` tiles: Glow ₹99→110 · **Blaze ₹299→380 (best value badge)** · Festival
  ₹799→1,150. (Static — wire IAP.)
- **ASTROLO Plus** — a dark glossy card (`#211B12→#0C0B0A`, glow corner): "Unlimited chat,
  every Pattern, 25% off everything", "₹199/mo", "7-day free trial" pill.
- **History** `card`: ledger rows (Today's ritual +2, Full Life Reading −60, …) with mono
  ± amounts and a flame.

---

## 12. Decode / Readings hub (`astro-screens.tsx` `DecodeScreen`) — shots 12, 13

The bottom-nav center destination — the traditional-kundli hub. Full-screen scroll, TopCluster pinned.
- Title block: `Label "Readings & Tools"`, "**Decode**" (Newsreader 32), italic subtitle.
- **Your Kundli** anchor `card`: a 72px round mood-gradient emblem with the Rashi glyph
  (`♋`), the name, "14 Aug 1998 · 4:20 am · Jaipur", "Open full chart →" (not wired), and a
  3-stat strip (**Lagna** Libra / **Rashi** Cancer / **Nakshatra** Pushya, each with a mono
  label + Newsreader value + tiny gloss).
- **In-depth readings** rows (priced in diyas): Full Life 60 · Marriage 60 · Career 45.
- **Matching & timing** rows: Kundli Matching · Auspicious Days.
- **Explore yourself** 2-col grid of `pill` tiles with glyph GlossIcons: Numerology ✦ ·
  Palmistry ☍ · Face Reading ◑ · Tarot ✷. Footer: "Try each once for free, then they cost a
  few Diyas." All rows are display-only in the prototype (wire to real readings).

---

## 13. Notifications (`astro-screens.tsx` `NotifScreen`) — shot 14

Its own full screen (opened from the bell). A sticky back header ("For you / A few quiet
notes"), then **New** and **Earlier** groups in `card`s: each item a `GlossIcon` + a warm
title + a serif subline + a mono timestamp + an unread accent dot. Ends "that's everything,
for now." (Demo items — feed a real endpoint.)

## 14. Placeholders — NOT built
`Timeline`, `People`, `Rituals` tabs + the `You`/profile area render a centered `MoodEmblem`
+ label + "coming soon." These are the next screens to design. Deep-links already point here
(RitualPill→Rituals, AreaSheet→People/Timeline).

---

## 15. Images / assets (`screens/astro/*.png`)
| File | Used by | Meaning |
|---|---|---|
| `chatfab.png` | MoonFAB | the floating **Sage** companion (already chat-bubble-shaped) |
| `chatsage1/2/3.png` | ChatScreen header | idle / thinking / delivered states |
| `sage2.png` | JournalScreen done view | Sage holding a heart |
Keep these files + relative paths on port (`require('./chatsage1.png')` etc.). `sage1.png`
may exist unused. The companion is a **cute sage** — no face-swaps, no moon.

---

## 16. React Native + Expo mapping (cheat sheet)
- `div`→`View`, text-bearing `span`/`div`→`Text`, `img`→`Image`, `input`/`textarea`→`TextInput`, `onClick`→`onPress`. `Press`→`Pressable` + Reanimated scale on pressIn/out.
- CSS gradients → `expo-linear-gradient` (and `react-native-svg` `<LinearGradient>`/`<RadialGradient>` inside SVG scenes). `box-shadow` → iOS `shadowColor/Opacity/Radius/Offset` + Android `elevation`; inset highlights → a thin top border.
- `backdrop-filter: blur` (nav bar, voice overlay, dim scrims) → `expo-blur` `<BlurView>`.
- All `@keyframes` → `react-native-reanimated` `withRepeat`/`withTiming`/`withSequence` loops (see §2). Respect `AccessibilityInfo.isReduceMotionEnabled`.
- The **SkyScene** drag → `react-native-gesture-handler` `PanGestureHandler` feeding the same `f=(viewT-SR)/span` math; the SVG scene → `react-native-svg` (paths/gradients copy over). Release ease → Reanimated `withTiming(now,{duration:560})`.
- Bottom-sheets → `@gorhom/bottom-sheet` (swipe-to-close). Full-screen overlays (chat/wallet/month/journal/notif) → stack screens.
- Haptics (`navigator.vibrate`) → `expo-haptics`. Fonts → `expo-font` (load Hanken Grotesk, Newsreader, Spline Sans Mono — see §1). Numbers are already unit-less/points. Drop the 412×892 frame; use the device screen + `SafeAreaView`. Replace the `window.__astro*` global sharing with ES module imports.
- Persist what's currently local (diyas, tasks, wrote, capsule shelf, checkin) via your store/backend.

---

## 17. Prototype shortcuts to undo when wiring the backend
(Full list + data shapes in **`HANDOFF.md`**.) In short: remove the mood tap-to-cycle and the
sky-header tap-to-cycle and the eclipse tile toggle (all preview toys); centralize the
hardcoded `11:40–12:30` on `DAY_CLOCK`; replace keyword chat/ask/verdicts with real logic/LLM;
wire real mic/STT; persist MyDay tasks + Time Capsule + Wallet history; replace `buildMonth()`
seeded-RNG with real day qualities; feed identity (`NAME`/`DATE`) from profile + system date;
**keep the KIRAN distress guard** and make it server-authoritative.

---

*This spec is generated from source. If anything here disagrees with the code, trust the code
and regenerate. Screenshots in `handoff/shots/` are the visual ground truth.*
