# The Path — full spec for the Timeline tab (build this LAST)

> **Why this file exists:** the Path is the app's most ambitious screen and it will be built
> **after the entire rest of the frontend is finished** (user's call, 2026-06-26). This file holds
> the complete vision + the buildable technical plan so that even after a chat compaction, a cold
> reader knows exactly **what** to build and **how**. Nothing here is throwaway: every visual element
> is computed from the real frozen Vedic engine.
>
> Tab is currently labelled **"Timeline"**; the screen's working name is **"The Path"** (warmer, no
> jargon). Name not finally locked. Voice: warm, plain, no em dashes, no astrology-jargon, no AI-slop.

---

## 1. The one idea that makes it 10X (and uncopyable)

The Path is a **vertical, one-way-scrollable map of your whole life**, past to future, that you can
**pinch-zoom into**. The further you zoom in, the closer in time you get; the closest you can zoom is
**the current month**, where the map hands off to the Today tab.

The reason this is not gimmick: **Vedic dasha is already a fractal of nested time.** Your life is
periods inside periods:

- **Mahadasha** — 6 to 20 years (the big lands of the map)
- **Antardasha** — months to ~2 years (sub-regions inside each land)
- **Pratyantardasha** — weeks to months (local areas; the deepest zoom, ~current month)

So **zoom level === dasha level.** Zoom out = your life as a chain of lands. Pinch in = a land opens
into its sub-chapters. Pinch in again = down to this month. One continuous gesture takes the user from
"who am I across 80 years" to "what is today." **This screen is the spine of the whole app:** Today is
the Path zoomed all the way in; identity is the Path zoomed all the way out.

---

## 2. The visual world

A winding path (a river/road) running vertically. The user travels down it.

- **Each Mahadasha is a biome, colored by that planet's classical nature** (the planet's character is
  the art direction, so it is authentic *and* beautiful):
  - Jupiter → wide, golden, expansive land
  - Saturn → slow grey mountains, austere
  - Venus → soft rose valley
  - Mars → rugged red terrain
  - Moon → silver coast / water
  - Sun → bright highland
  - Mercury → green, quick, varied
  - Rahu/Ketu → dim, mysterious, edge-of-map terrain
- **"You are here"** glows on the path at the present moment. The floating **Sage companion can live
  at this spot** when the user is on this tab.
- **The future is under fog** (Clash-of-Clans fog-of-war). The big terrain ahead is visible (a Saturn
  range is coming) but not fake daily detail. **This is the falsifiability rule made visual: the
  future is terrain and weather, never fixed events.** It also makes scrolling forward feel like
  exploring.
- **The past is fully lit, and it is the user's to fill** (see Proof pins, §3).
- **A living sky above the path:** the real current Moon phase + a soft planetary starfield, shifting
  subtly as you move through time. Premium, calm, never busy.

---

## 3. How the life-domains live on the map (Sade Sati, Career, Love, Money)

Do **not** cram these as separate lists. They are **lenses** over the one map (like Google Maps'
traffic/terrain toggles). Same path, different thread revealed:

- **Love lens** → stretches where relationship periods light up (Venus/Jupiter sub-periods, 7th-lord
  windows) bloom warm over the path.
- **Career lens** → 10th-house / Saturn / Sun windows raise little summit-flags.
- **Money lens** → 2nd / 11th-house periods glow.
- **Sade Sati** → NOT a lens, a **weather front.** A band of mist that rolls across the ~7.5-year
  stretch of path, in three shades for **rising / peak / setting.** A storm system crossing your land,
  calm and explainable, never the doom other apps sell.
- **Milestone nodes** on the path = real transitions: every dasha change; the **Saturn return** as a
  literal mountain pass; the **Jupiter return** as a golden archway (~every 12 years); eclipses as
  markers. Tap a node → a short, warm card about that turning point.

So one map; the user taps "Love" or "Career" to watch that thread of their life glow along the whole
journey. No rashifal app has this.

### The unforgettable part: the Proof, as memory-pins
The lit past is **theirs to annotate.** Tap any past spot → "what happened to you around here?" → they
log a memory (a breakup, a job, a move) and we show what the sky was doing then. Over months their
past path fills with **their own pins** — their actual life mapped onto the chart. This is:
- the skeptic-converter (their own life is the evidence),
- an emotional moat (you do not delete an app that holds your life story),
- and retention (they return to add pins).
Backed by `/companion/proof` (already live).

---

## 4. The "even crazier" layer (all still 2.5D, all Skia-buildable)

- **2.5D parallax depth** — foreground terrain, mid-ground path, distant drifting starfield. Looks 3D,
  costs almost nothing, no real 3D engine.
- **Fly-to animation** — tap a node and the camera glides along the path to it (like scrolling to a
  base in Clash of Clans).
- **Seasons of your life** — the light shifts: dawn over a hopeful upcoming period, dusk over a hard
  past one. Driven by the real period quality, not random.

---

## 5. Tech + build method (the important practical part)

**Stack:** `@shopify/react-native-skia` (the map canvas: paths, gradients, images, shaders, parallax —
GPU-accelerated, runs on the UI thread at 60fps even on cheap Android) + `react-native-reanimated` +
`react-native-gesture-handler` (pinch-zoom / pan / momentum, all on the UI thread). Confirmed June
2026: this combo does infinite zoomable/pannable canvases at 60fps; Skia animations on Android are
~200% faster post-Fabric; **Skia works in Expo Go (since SDK 46)** so it does not break the Expo Go
test workflow.

**Method that makes building fast (the unlock):** `react-native-skia` also runs on **web** with the
**same code.** So build the map as an **Expo web** target first (where the engine can be rendered,
clicked, and screenshotted during development), polish it there, then the identical code runs in Expo
Go on the phone unchanged. Iterate on web → free on native.

**Hard engineering rules:**
1. **2.5D, not true 3D, for v1.** Real 3D (three.js / expo-gl) on a ₹10,000 Android phone = jank +
   battery drain (the core market). Skia parallax looks ~90% as magical at ~10% of the risk. Revisit
   true 3D only post-launch if it is worth it.
2. **A "lite" fallback.** On low-end devices or with reduced-motion on, fall back to a simple vertical
   chapter-list of the same data. Nobody gets a broken experience.
3. **Design tools cannot build this.** Claude Design / Stitch can only mock the *look* of static
   frames (whole-life view, one-chapter view, this-month view) as an art moodboard. The zoom / parallax
   / gesture / data engine is hand-coded. Do not try to "port" a design-tool output here.

---

## 6. Staged build plan (each stage is visible + verified before the next)

1. **Thin slice:** vertical path + real dasha biomes (from `/kundli/dasha-timeline`) + "you are here"
   marker + basic pan & pinch-zoom. Running on web and phone. Proves the concept.
2. **Zoom-into-dasha-levels** (Maha → Antar → Pratyantar as you pinch in).
3. **Fog over the future.**
4. **Parallax depth + living sky.**
5. **Milestone nodes** (dasha changes, Saturn/Jupiter returns, eclipses).
6. **The lenses** (Love / Career / Money).
7. **Sade Sati weather front.**
8. **The Proof memory-pins.**
9. **Lite fallback** + reduced-motion.

---

## 7. Backend data sources

| Need | Source | Status |
|---|---|---|
| Mahadasha chapters (lands), per birth-time tier | `POST /kundli/dasha-timeline` (`dates_exact` flag) | **live** |
| Antardasha / Pratyantardasha (zoom levels) | engine `get_antardasha_table` / `_vimshottari_timeline` in `shared/astro/*` | engine has it; **may need a thin endpoint** |
| Whole-life sequence (past + future lands) | engine `build_lifetime_dasha_sequence` | engine has it; **may need a thin endpoint** |
| Sade Sati phases (the weather front) | engine `sade_sati_timeline` / `_sade_sati_phase` in `shared/astro/astro_calc.py` + `kundli.py` | engine has it; **needs a thin endpoint** |
| The Proof (past spot → what the sky was doing) | `POST /companion/proof` | **live** |
| Love / Career / Money lens windows | derive from dasha + house lords (Venus/7th, Saturn-Sun/10th, Jupiter/2nd-11th); reuse `build_event_timing_atlas` if suitable | **to confirm / build a small endpoint** |
| Daily hand-off (zoomed all the way in) | `POST /dashboard/forecast` (Today) | **live** |

**Framing rule (engrave in every label):** chapters, themes, and **windows/periods**, never a fixed
date, never vague "seasons of life." Future = terrain under fog.

---

## 8. Timing + identity
- **Build order: LAST**, after the entire rest of the frontend is finished and wired.
- Tab label today = "Timeline"; screen working-name = **"The Path."** Decide the final name before
  shipping. The Path quietly becomes the backbone tying Today (zoomed in) to the whole life (zoomed
  out).
