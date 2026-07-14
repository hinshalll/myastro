# ASTROLO — Frontend Handoff (for Claude Code)

> **What this is.** A working, phone-sized React prototype of ASTROLO, an astrology
> app. This document is generated **from the actual source code** (not memory), so it
> reflects exactly what exists today. Its job: let Claude Code wire this frontend to a
> real backend, and let a later tool port it to React Native + Expo.
>
> **How to trust this doc.** Every feature below names the component, the file it lives
> in, and — crucially — flags whether its data/logic is **REAL (interactive)** or
> **DEMO (hardcoded / faked, replace with backend)**. When in doubt, the code wins.

---

## 0. Answering "can you remember everything we changed?"

No — and neither should you rely on chat memory. Over a long project, earlier
iterations, placeholder swaps, and image changes get trimmed from context. The
**single source of truth is the code in `screens/astro/`.** This doc was produced by
reading all five source files top to bottom. If you ever need to re-verify what an
app does, do the same: read the files, don't recall the conversation.

---

## 1. Architecture & how it runs

**Entry:** `screens/astro/Home.html`. It draws the phone frame (412×892 device
bezel, notch, status bar) and a `#root`, then loads React 18 + Babel standalone and
the four app scripts **in this order** (order matters — each attaches globals the
next one reads):

| # | File | Exposes on `window` | Role |
|---|------|--------------------|------|
| 1 | `theme.ts` | `THEME`, `MOODS`, all data tables | Design tokens + ALL app data/content |
| 2 | `astro.tsx` | `__astroUI` | Shared atoms: palette, `Icon`, `Press`, `Sheet`, `MoodEmblem`, `MoonGloss`, `Ganesha`, helpers |
| 3 | `astro-today.tsx` | `__astroToday` | Today screen pieces (header, reading, clock, nav…) |
| 4 | `astro-plan.tsx` | `__astroPlan` | Plan sub-tab: My Day, Panchang, Month, tool sheets |
| 5 | `astro-screens.tsx` | `AstroApp` | Chat, Wallet, Decode, Journal, Notifications, sheets, **the app container that wires it all** |

All files are IIFEs (`;(function(){ … })()`) that read prior globals and export
their own. Babel transpiles inline with `data-presets`. **No bundler, no imports.**

**Why split like this:** each `<script type="text/babel">` gets its own scope, so
components are shared via `window.__astroUI` / `__astroToday` / `__astroPlan`. Keep
this pattern if you stay in HTML; collapse to real ES modules when porting to RN.

**Scaling:** `Home.html`'s `fit()` scales the 412×892 frame to the viewport. In RN
this whole concept disappears — the device *is* the frame.

---

## 2. Design system ("ASTROLO-clean white")

Two token sources exist; **`astro.tsx`'s palette is the one the live UI uses.**
`theme.ts`'s `THEME` (a warm-ivory "paper" system) is **legacy/reference** — the app
moved to clean white. Don't wire `THEME.paper` etc. into new UI; match `astro.tsx`.

**Live palette (`astro.tsx`):**
- `PAPER #FFFFFF` (bg), `WASH #F4F4F6` (insets), `INK #0C0B0A` (text),
  `INK2 #3A3733` (secondary), `GRAY #9A958C` (tertiary), `HAIR rgba(12,11,10,.07)`
  (hairlines), `ORANGE #DF6B35` (alert accent).
- Fonts: **Newsreader** (serif, display/editorial), **Hanken Grotesk** (sans, UI),
  **Spline Sans Mono** (mono, tiny tracked labels). Loaded in `Home.html`'s `<link>`.
- Helpers: `aA(hex, alpha)` → rgba string. `pill(radius, extra)` → the soft glossy
  pill surface (gradient + layered shadow + top highlight). `card(extra)` → white card.
- `GlossIcon` = the small colorful rounded-square icon tile (glossy app-icon look).
- `Press` = tap wrapper with subtle scale-down. `Icon n="name"` = line-icon set
  (paths in `PATHS`). `Sheet` = bottom-sheet modal.

**Motion:** all keyframes live in `Home.html`'s `<style>` (floatY, twinkle,
cloudDrift, breathe, glowPulse, sheen, riseIn, popIn, sheetUp, spinSlow, sound,
blink, skyShoot, haloBreathe, pulseRing, etc). `rise(delayMs)` staggers card
entrances. `@media (prefers-reduced-motion: reduce)` kills all of it.

**The mood system (central concept):** the day has one of **12 moods** (Settled,
Guarded, Bold, Tender, Restless, Capable, Warm, Deep, Wandering, Driven, Upbeat,
Quiet). Each mood carries an `accent`/`accentDeep`/`glow` color, a motion
personality (`feel`), forecast copy, a moon config, sigil, chips, life-area lines,
etc. **The mood only tints accents** (emblems, glows, chips, the diya) — the page
stays white. Everything visual keys off `mood.accent*`.

---

## 3. Global state & navigation (`AstroApp`, bottom of `astro-screens.tsx`)

`AstroApp` holds all app state:

- `moodIdx` → current mood (defaults to **"Deep"**). `cycle()` advances it.
  **DEMO:** tapping the big reading word cycles through all 12 moods so you can
  preview them. **In production the mood is chosen by the backend for the day** — remove
  the tap-to-cycle, set mood from `/dashboard/today`.
- `tab` → `Today | Timeline | People | Rituals | Readings` (bottom nav).
- `sub` → `Read | Plan` (only within Today).
- `screen` → full-screen overlays that sit above tabs: `chat | wallet | month |
  journal | notif`. These `return` early before the tab render.
- `sheet` → which bottom-sheet is open: `eclipse | area | muhurat | doctor | ask |
  capsule`.
- `bal` (Diyas balance, starts **108**), `bump` (triggers the +1 float animation),
  `earn(n)` → adds to balance + bumps.
- `wrote` (has the user journaled today), `checkinOpen`/`checkinDone`,
  `eclType` (solar/lunar), `askSeed`, `chatSeed`, `areaKey`.

**Diyas ("🪔") = the app's soft currency.** Earned by doing gentle things
(check-in +1, ritual +2, journal +1 — these are **wired**), spent on readings.
The Wallet's buy/subscribe UI is **static/DEMO**.

**Navigation is plain React state, no router.** Overlays are conditional early
returns; tabs are conditional blocks; sheets are `<Sheet open=…>`. Port to a real
navigator (React Navigation) in RN.

---

## 4. Data models (all in `theme.ts`) — REAL vs DEMO

Everything the UI shows comes from these tables. **This is your backend contract.**
Each is attached to `window`. Replace the demo values with API responses of the same
shape.

| Export | Shape (abridged) | Feeds | Status |
|--------|------------------|-------|--------|
| `MOODS` / `MOOD_BY_KEY` | `{key, vibe, accent, accentDeep, glow, moon, feel, forecast:{mood,opportunity,caution,action,why}}` ×12 | the whole mood system, reading card, why-sheet | **Content is fixed; backend picks WHICH mood is today** |
| `DAY_LINE` | `mood → "A warm, social day."` | greeting sub-line, looking-ahead | fixed copy |
| `PERSONAL_LINES` | `mood → one line from the user's own history` | reading card's personal bullet | **DEMO keyed by mood — real app derives from user history; pass null if new user (line collapses)** |
| `READ_CHIPS` | `mood → {good:[], easy:[], offDay?}` | reading card good-for/go-easy chips | fixed per mood |
| `HORA_LINE` | one string | greeting's planetary-hour line | **DEMO single value — backend computes per hora** |
| `DAY_CLOCK` | `{sunrise, windows:[{name,start,end,q,tip}], bestName, avoidName}` q∈best/good/neutral/hold/rest, times decimal 6..30 | **The Day's Clock, My Day sky, all timing** | **DEMO — backend: sunrise/sunset + muhurta math per user/place** |
| `ALMANAC` | `{nakshatra,nakFlavor,tithi,tithiNote,special,specialNote,festival,best90}` | Today at a Glance | **DEMO per day/place** |
| `ECLIPSE` | `{type,inDays,date,sutakDate,sutakTime,sutakHours,sanskrit,short:{solar,lunar},full:{…}}` | eclipse card + sheet | **DEMO — backend sends this or null on ordinary days** |
| `MIRROR` | `{invites:[], placeholders:[], responses:{}, distress:{line,help}}` | journal / Mirror flow | copy fixed; **tone classification is server-side in real app** |
| `FOCUS` | `{area,to,line}` or null | "In focus today" chip | **DEMO — set only when one life area is genuinely active** |
| `LIFE_AREAS` | `mood → {love,work,money}` one line each, NO scores | Today Across Your Life rows | **per-mood; backend computes together** |
| `LIFE_AREA_META` | `area → {planet,houses,detail,why,link:{label,tab}}` | the area sheet | **`link` shown only if that tab exists** |
| `FESTIVAL` | string or null | greeting festival pill | DEMO |
| `AHEAD` | `[{day,date,mood,status,good,avoid}]` ×5 | Looking Ahead strip | DEMO |
| `PANCHANG_SOON` | `[{day,date,quality,note,good,low}]` ×3 | My Panchang card | DEMO |
| `MONTH` / `buildMonth()` | `{name,startWeekday,days:[{n,quality,mark}]}` | full-month calendar | **DEMO via seeded RNG — replace with real per-day qualities + marks** |
| `dayDetail(n)` | `{n,quality,mark,why,good,low}` | tapped calendar day sheet | DEMO generator |
| `MUHURAT` | `{events:[], results:{default:[{date,time,note}]}}` | Find a Good Day | **DEMO — backend returns real windows per event/place** |
| `CAL_DOCTOR` | `[{title,when,status,why,better}]` | Check My Plans | **DEMO — real app reads phone calendar w/ permission** |
| `ASK_MOMENT` | `{samples:[], answers:[{verdict,why}]}` | Ask the Moment | **DEMO — real app casts a chart for the instant** |
| `TIME_CAPSULE` | `{moments:[], shelf:[{note,to,on,state}]}` | Time Capsule | DEMO |
| `CHECKIN_REFLECTION(mood,energy,dayKey)` | fn → string | check-in response | **REAL client-side logic (instant, no AI)**, uses `DAY_TONE` |
| `MOON_CFG` / `MOON_READING` / `MOON_STATIONS` / `WATER_SURFACE` | moon phase configs & readouts | **mostly legacy/reference** — live header uses its own `PhaseMoon` | reference |

Also demo identity in `astro.tsx.__astroUI`: `NAME:"Aarav"`, `DATE:"Tuesday, 17
June"`. Wire these to the real user/profile + today's date.

---

## 5. Screen-by-screen

### 5.1 TODAY → READ (`AstroApp` + `astro-today.tsx`)
The home surface. Pinned header (never scrolls): **TopCluster** + **SubTabs**.
Scrolling body, in order:

1. **TopCluster** — avatar (opens *You*, **not built**, `profile()` is a no-op),
   bell (opens Notifications screen), and the **Diya chip** (balance → Wallet). The
   `+1` coin float fires when `bump` changes. `alert` shows the bell's red dot.
2. **CheckInChip** — only if the check-in was dismissed; re-opens it.
3. **LivingSkyHeader** — time-aware sky scene (dawn/day/dusk/night) chosen from the
   real clock (`nowH()`), with sun/phase-moon, drifting clouds, twinkling stars,
   the greeting ("Good morning, *Aarav*"), festival pill (if any), and the hora
   line. **DEMO affordance:** tapping the card cycles dawn→day→dusk→night to preview
   each sky; in production just render the live one (keep `skyNameFor`, drop the
   `ov` override + `cycle`). `PhaseMoon` shows a fixed waxing-gibbous demo phase —
   feed real illumination.
4. **EclipseCard** — only when `showEclipse` and an eclipse is near. Distinct
   solar/lunar glyph. **DEMO:** tapping the little tile toggles solar/lunar (a
   preview toy). Opens the EclipseSheet. Backend: show only when `ECLIPSE != null`.
5. **ReadingCard** (the hero) — mood word (giant serif), the day's sentence, the
   personal-history bullet, **good-for / go-easy chips** (semantic green/red dots),
   an off-day note, the **strongest-window** nugget (jumps to Plan), a black
   **"why this?"** button (inline accordion with `mood.forecast.why`), and share.
   Tapping the mood word `cycle()`s moods — **DEMO only.**
6. **LifeAreas** — Love / Work / Money, one honest line each, **no scores ever**.
   Each row opens the **AreaSheet**.
7. **JournalCard** (The Mirror) — a cozy diary invitation (open-book illustration,
   ambient glow, ruled lines). Shows a written-state once `wrote` is true. Opens the
   full **JournalScreen**.
8. **RitualPill** — the day's ritual nudge; deep-links to the Rituals tab.

> Note: several timing components (**ReadingCard**, **GoodBadStrip**, **ForToday**,
> **DayClock**, **TimingSheet**, **GoodBadSheet**) exist and some are **not currently
> mounted** in the Read flow (only ReadingCard, LifeAreas, Journal, Ritual are). They
> all hardcode the same window **"11:40–12:30"** — when you wire `DAY_CLOCK`,
> centralize this so they never disagree.

### 5.2 TODAY → PLAN (`astro-plan.tsx` → `PlanTab`)
1. **MyDay** — schedule for today. Live status ("A good window, right now" vs "Best
   to hold a little") computed from `DAY_CLOCK` vs `nowH()`. **The signature piece is
   the Living Sky (`SkyScene`):** a framed window you **drag** to scrub the whole day
   — the atmosphere morphs sunrise→noon→dusk→night, sun/moon arc across, stars/clouds/
   birds/village-lights fade in by time. Below it a **quality strip** paints the day
   (best/good/neutral/hold/rest) with a fixed "now" marker + hour axis. **Add-a-task**
   input: type a task → it's auto-placed into the best upcoming window (fake "finding
   the best time…" spinner), toggle done. Tasks are **local state only** — persist via
   backend + reminders.
2. **AskMomentCard** — prominent entry to Ask the Moment (opens the sheet with a seed).
3. **MyPanchang** — today + next 2 days, each a colored quality dot + note. "Open
   full Panchang" → **MonthScreen**.
4. Three tool entries → sheets: **Find a good day** (Muhurat), **Check my plans**
   (Calendar Doctor), **Time Capsule**.

### 5.3 MonthScreen (full overlay, `astro-plan.tsx`)
A month calendar; each day colored by quality with up to two dots (quality + a mark:
festival/moon/grahan/dasha/task). Legend included. Tap a day → bottom sheet with
`dayDetail(n)` (why + good/hold times). "Sync good days" button is **static/DEMO**.

### 5.4 READINGS / "Decode" (bottom-nav center, `DecodeScreen`)
The elevated glossy center nav button (a **kundli-chart icon**). This is the
traditional-kundli-app hub: the **Your Kundli** anchor card (Rashi glyph emblem,
name, birth details, Lagna/Rashi/Nakshatra stats, "Open full chart" — **not wired**),
then rows: **In-depth readings** (Full Life / Marriage / Career, priced in Diyas),
**Matching & timing** (Kundli Matching, Auspicious Days), **Explore yourself**
(Numerology, Palmistry, Face Reading, Tarot). All rows are **display-only/DEMO** —
none open a real reading yet. Prices are Diya costs.

### 5.5 Chat — "Sage" (`ChatScreen`)
A proactive guide chat. Opens with one of **3 warm openers** (`MOON_OPENERS`, picked
by day-of-month). The **Sage** avatar has **3 states** (idle / thinking / delivered)
swapping `chatsage1/2/3.png`. Input works: `pickReply()` classifies your text by
keywords → low/high/ask/warm buckets (`REPLY`), with a typing beat. **Safety:** a
`DISTRESS` keyword list triggers a gentle, non-clinical reply pointing to the **KIRAN
helpline (1800-599-0019)**. **DEMO:** replies are keyword templates, not an LLM;
voice mic is a fake toggle. **Backend: replace `pickReply` with your LLM**, keep the
distress guard as a hard server-side check.

### 5.6 The Mirror — Journal (`JournalScreen`)
Full-screen cozy writing page (ruled paper, ambient glow). Type or "record" (voice is
**faked** — `sendRec` inserts canned text). "Leave it with me" → a warm response
(`MIRROR.responses`) delivered by **sage2.png** holding a pink heart, earns +1 diya,
sets `wrote`. **Backend:** persist entries, classify tone server-side for the
response, run the distress guard.

### 5.7 Diyas Wallet (`WalletScreen`)
Balance hero (flame brightens with balance), **earn list** (check-in done-state is
real-ish), **buy packs** (static), **ASTROLO Plus** subscription card (static),
**history** (static). Wire earn/spend/purchase/subscription to backend + IAP.

### 5.8 Notifications (`NotifScreen`)
Own screen (opened from the bell), grouped New/Earlier, unread dots. **DEMO items** —
feed from a real notifications endpoint.

### 5.9 Sheets (bottom-sheet modals)
`EclipseSheet`, `AreaSheet` (Love/Work/Money detail + why accordion + one contextual
link), `MuhuratSheet`, `CalendarDoctorSheet`, `AskMomentSheet`, `TimeCapsuleSheet`,
plus `WhySheet`/`GoodBadSheet`/`TimingSheet` (defined, some not mounted). All read
their data from the `theme.ts` tables above. `AskMoment` and `TimeCapsule` have
multi-phase flows (ask→casting→done; write→sealing→sealed) driven by `setTimeout` —
replace the fake delays with real API calls.

### 5.10 Placeholders — NOT built
**Timeline, People, Rituals** tabs and the **You/Profile** area are `Placeholder`
("coming soon") / no-ops. Deep-links to them exist (RitualPill → Rituals, AreaSheet
links → People/Timeline). These are the next screens to design/build.

---

## 6. Images / assets (in `screens/astro/`)

| File | Used by | Meaning |
|------|---------|---------|
| `chatfab.png` | `MoonFAB` | the floating companion (a sage; already shaped like a chat bubble) |
| `chatsage1/2/3.png` | `ChatScreen` header | idle / thinking / delivered states |
| `sage1.png` | (available) | sage art |
| `sage2.png` | `JournalScreen` done-state | sage holding the heart |

The companion is a **cute sage**. Keep the same files when porting; they're
referenced by relative path.

---

## 7. Backend wiring checklist (implied endpoints)

Group the demo tables into these calls (names are suggestions):

- **`GET /dashboard/today`** → today's `mood` key, `DAY_LINE`, `HORA_LINE`,
  `PERSONAL_LINES` (from user history, or null), `READ_CHIPS`, `FOCUS`, `FESTIVAL`,
  and `LIFE_AREAS` for the day — computed together so nothing contradicts.
- **`GET /day/clock`** (per user/place) → `DAY_CLOCK` (sunrise/sunset + muhurta).
  Feeds Day's Clock, My Day sky, and every "strongest window" string.
- **`GET /almanac`** → `ALMANAC`. **`GET /eclipse`** → `ECLIPSE` or null.
- **`GET /panchang/soon`** + **`GET /panchang/month?m=`** → `PANCHANG_SOON`, `MONTH`,
  `dayDetail`.
- **`GET /ahead`** → `AHEAD` (looking-ahead / week).
- **`POST /muhurat`** {event, place} → results. **`GET/POST /calendar/check`** (reads
  device calendar) → `CAL_DOCTOR`. **`POST /ask-moment`** {question, instant} →
  verdict+why. **`POST /capsule`** {note, when} → sealed.
- **`POST /checkin`** {mood, energy} → reflection (or keep `CHECKIN_REFLECTION`
  client-side) + diya credit.
- **`POST /mirror`** {text|audio} → tone-classified response; **`GET /mirror/state`**
  → `wrote`. Distress guard server-side.
- **`POST /chat`** {message, history} → LLM reply; distress guard.
- **`GET /wallet`**, **`POST /wallet/earn`**, **`POST /wallet/purchase`**,
  **`POST /subscription`**.
- **`GET /kundli`** + **`GET /reading/:type`** (Full Life, Marriage, Career, Matching,
  Numerology, Palmistry, Face, Tarot) → Decode hub.
- **`GET /notifications`**.
- **Profile/You**, **Timeline**, **People**, **Rituals** — screens not built yet.

---

## 8. Prototype shortcuts to undo when going real

- **Mood tap-to-cycle** (ReadingCard word) — remove; mood comes from backend.
- **Sky-header tap-to-cycle** and **eclipse tile toggle** — preview toys; remove.
- **Hardcoded "11:40–12:30"** timing everywhere — centralize on `DAY_CLOCK`.
- **Chat/Ask/Should-I verdicts** — keyword/length templates → real logic/LLM.
- **Voice recording** — faked; wire real mic + STT.
- **MyDay tasks, Time Capsule shelf, Wallet history** — local/static → persisted.
- **`buildMonth()` seeded RNG** — replace with real day qualities.
- **Identity** `NAME`/`DATE` — from profile + system date.
- Keep the **KIRAN distress guard** — make it server-authoritative, never remove it.

---

## 9. React Native + Expo port notes

- `div→View`, `span/text→Text`, `img→Image`, `onClick→onPress`, `input/textarea→
  TextInput`. `Press` → `Pressable` with a scale transform.
- CSS gradients → `expo-linear-gradient`; box-shadows → `shadow*`/`elevation`;
  `backdrop-filter` (nav/overlays) → `expo-blur`.
- All the `Home.html` `@keyframes` → `react-native-reanimated` loops. The SkyScene
  drag → `react-native-gesture-handler` PanGestureHandler over the same math
  (`SR..SR+span`, `f = (viewT-SR)/span`). The inline SVG scenes → `react-native-svg`
  (paths port 1:1).
- The `window.__astro*` global-sharing pattern → normal ES module imports.
- Numbers are already unit-less/point-friendly (see `theme.ts` note). The 412×892
  frame concept is dropped — use the device screen + SafeArea.
- Fonts: load Newsreader / Hanken Grotesk / Spline Sans Mono via `expo-font`.

---

*Generated from source: `Home.html`, `theme.ts`, `astro.tsx`, `astro-today.tsx`,
`astro-plan.tsx`, `astro-screens.tsx`. If code and doc ever disagree, the code is
right — regenerate this file by re-reading the sources.*
