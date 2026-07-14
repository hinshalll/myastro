# ASTROLO — How the frontend was built (quick explainer for Claude Code)

A phone-sized React prototype (astrology app). One HTML entry + 4 script files, no
bundler. Here's how the notable bits actually work — enough to understand it, not a
full spec (that comes later, for the RN+Expo port).

## Setup
- `Home.html` draws the phone frame and loads React 18 + Babel, then the 4 files **in
  order**: `theme.ts` → `astro.tsx` → `astro-today.tsx` → `astro-plan.tsx` →
  `astro-screens.tsx`. Each is an IIFE that hangs its exports on `window`
  (`__astroUI`, `__astroToday`, `__astroPlan`, `AstroApp`) so the next file can read
  them. No imports.
- **`theme.ts` = all data + copy** (nothing visual). **`astro.tsx` = the design
  system** (palette, `Icon`, `Press`, `Sheet`, `GlossIcon`, helpers). The other three
  build screens. `astro-screens.tsx`'s `AstroApp` is the container that holds all
  state and wires navigation.

## The mood engine (the core idea)
The day has one of **12 moods** (Deep, Warm, Bold…). Each mood in `theme.ts` carries
its own accent colors (`accent`/`accentDeep`/`glow`), a motion personality, and all
its copy. **The whole UI tints off the current mood** — emblems, glows, chips, the
diya — while the page itself stays clean white. Navigation/state is plain React
`useState` in `AstroApp` (tabs, sub-tabs, overlays, sheets, diya balance). No router.

## Scenario-based image swapping
Images aren't static — they change with context by cross-fading PNGs:
- **Chat "Sage" avatar has 3 states.** In `ChatScreen` a variable picks the file:
  `typing ? chatsage2.png (thinking) : userSpoke ? chatsage3.png (delivered) :
  chatsage1.png (idle)`. All three are stacked and we fade opacity between them, so it
  looks like the sage reacts as you talk.
- **Floating companion** (`MoonFAB`) uses `chatfab.png` with a breathing glow and a
  poke-wiggle on tap; an unread dot (pulsing ring) appears when there's a message.
- **Journal done-state** shows `sage2.png` (sage holding a heart) with the warm reply.

## The "living sky" (time-aware visuals + the slider)
Two related things:
- **Header sky** (`LivingSkyHeader`): reads the real clock (`nowH()`) and renders
  dawn / day / dusk / night — different gradient, sun-or-moon, clouds, stars. (There's
  a dev tap-to-preview that cycles the four; production just shows live.)
- **My Day "Living Sky" slider** (`SkyScene` in `astro-plan.tsx`): the signature
  interaction. You **drag across the sky** and the entire atmosphere morphs through the
  day — sky colors interpolate, the sun/moon arc along a sine path, stars/clouds/birds/
  village-lights fade by time of day. It's a pointer-drag mapped to a time value
  (`f = (viewT - sunrise) / 24`); releasing **eases back to "now"** via a small
  requestAnimationFrame tween. Below it, a **quality strip** paints the whole day
  (green=good, amber=hold, grey=rest) with a fixed "now" marker and an hour axis.

## Animations
All keyframes live in `Home.html`'s `<style>` (floatY, twinkle, cloudDrift, breathe,
glowPulse, sheen, riseIn, sheetUp, spinSlow, blink…). Cards stagger in with a
`rise(delayMs)` helper. `Press` gives every tappable a subtle scale-down. Bottom
sheets slide up (`Sheet`), the diya chip floats a "+1" when you earn, and multi-step
flows (Ask the Moment, Time Capsule) run a fake "casting/sealing" spinner before the
result. Everything respects `prefers-reduced-motion`.

## Interactions worth knowing
- **Diyas (🪔)** = soft currency in `AstroApp` state; earned by gentle actions
  (check-in +1, ritual +2, journal +1) via `earn()`, spent on readings.
- **Check-in** is a two-step chip picker (mood → energy) that returns an instant warm
  reflection computed client-side (no AI) by comparing how you feel to the day's tone.
- **Chat** classifies your text by keywords into warm/low/high/ask replies, with a
  typing beat — and a **distress keyword guard** that surfaces the KIRAN helpline.
  (These are prototype stand-ins for a real LLM; keep the safety guard.)
- **Sheets** (eclipse, life-area, muhurat, calendar-doctor, ask, time-capsule) are
  bottom-sheet modals reading their content from `theme.ts` tables.

## What's real vs faked
Interactions are real (drag, taps, state, earning, check-in logic). The **data and
"intelligence" are demo** — timings, panchang, month calendar, chat/ask verdicts,
voice recording, and the Decode readings are hardcoded or template-based, ready to be
swapped for backend calls. Timeline / People / Rituals / You are "coming soon"
placeholders.

*Files to read for the truth: `theme.ts`, `astro.tsx`, `astro-today.tsx`,
`astro-plan.tsx`, `astro-screens.tsx`.*
