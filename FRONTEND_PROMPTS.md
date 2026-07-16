# Myastro — Frontend design prompts (current, paste-ready)

> Each numbered section is a **self-contained prompt for one screen/flow**, open the one you need and
> paste it into Claude Design (or Stitch). They give structure, content, exact copy, and how things work,
> and leave the look to the tool. **Voice:** warm, plain, cozy, a little tender; no astrology jargon, no
> em dashes, no AI-slop ("cosmic/mystic/aura/manifest"). **No app name or logo anywhere** (a splash comes
> last). How it all self-runs (caching, real-time, notifications) → `TODAY_FUNCTIONING.md`; AI spend →
> `AI_COSTS.md`; the full plan → `MOBILE_APP_BLUEPRINT.md`.

## Status (2026-07-05)
- Today screen was designed + built as a **web React prototype in Claude Code** (codename "ASTROLO").
  An **Antigravity / Gemini port to Expo RN came out BAD → ditched.** **NEW PLAN: Claude Code (me) does
  the port itself**, then wires the live backend, then does final frontend tweaks (one owner, no seam).
  See **§0 — FRONTEND PORT PLAN** just below. Backend is live on Render.
- **Nav (v4.1):** bottom tabs **Today · Timeline · People · Rituals · Readings**; **You** = the
  **top-left avatar**; top-right **Diya chip**; floating **Sage companion**.
- **Recover anything lost to compaction:** scan the transcripts at
  `C:\Users\hinsh\.claude\projects\C--Users-hinsh-Desktop-myastro\*.jsonl` (python: json.loads each line,
  pull `message.content[].text`, grep a keyword), print the match.

---

# 0 — FRONTEND PORT PLAN (Claude Code ports the ASTROLO prototype → Expo RN)

> **⭐ UPDATE 2026-07-14: THE PORT IS DONE.** The whole ASTROLO frontend is built in `mobile/`
> (Expo SDK 54) and verified 1:1 on web (Read/Plan+SkyScene/Chat+KIRAN/Decode/Wallet/Journal/Month).
> On-device crash + missing-icons are fixed. **The current canonical doc is `MOBILE_APP_STATUS.md`
> at repo root** (file map, exact pinned versions, run commands, gotchas, next steps). NEXT = wire
> the Today tab to live Render APIs first. The plan below is kept for historical reference.

## The source: the "ASTROLO" web React prototype (built in Claude Code)
A phone-sized **web** React prototype of the Today screen (React 18 + Babel, no bundler). Files (an IIFE
chain hanging exports on `window`): `Home.html` (frame + ALL CSS keyframes), **`theme.ts` = all data +
copy**, **`astro.tsx` = the design system** (palette, `Icon`, `Press`, `Sheet`, `GlossIcon`, helpers),
`astro-today.tsx`, `astro-plan.tsx`, `astro-screens.tsx` (`AstroApp` = container holding all state + nav).
Claude Code also writes a **design MD** explaining it in detail.
**Key architecture to preserve faithfully:**
- **12-mood engine** (Deep, Warm, Bold…): each mood in `theme.ts` carries accent/accentDeep/glow + a
  motion personality + all its copy; **the whole UI tints off the current mood** while the page stays
  clean white.
- **The Sage companion:** chat avatar has **3 cross-faded states** (`chatsage1` idle / `chatsage2`
  thinking / `chatsage3` delivered); the **floating FAB** (`chatfab.png`, component still named `MoonFAB`
  internally = the Sage) breathes, wiggles on poke, shows a pulsing unread dot; the journal done-state
  shows `sage2.png` (sage holding a heart) with the warm reply.
- **Living-sky header:** reads the real clock → dawn/day/dusk/night (gradient, sun/moon, clouds, stars).
- **My Day "Living Sky" drag slider (SIGNATURE interaction):** drag across the sky → whole atmosphere
  morphs through the day (sky interpolates, sun/moon arc on a sine path, stars/clouds/birds/village-lights
  fade by time); release **eases back to "now"**. Below it a **quality strip** (green good / amber hold /
  grey rest) with a fixed "now" marker + hour axis.
- **Animations** live in `Home.html` `<style>` (floatY, twinkle, cloudDrift, breathe, glowPulse, sheen,
  riseIn, sheetUp, spinSlow, blink); cards stagger via `rise(delayMs)`; `Press` scale-down on tappables;
  bottom sheets slide up; diya "+1" float on earn; casting/sealing spinners; respects reduced-motion.
- **Behaviour:** Diyas soft currency (earn check-in +1 / ritual +2 / journal +1); check-in = 2-step chip
  picker (mood→energy) → instant CLIENT-SIDE warm reflection; chat = keyword-classified replies + a
  **distress-keyword guard → KIRAN helpline (KEEP THIS SAFETY GUARD)**. Bottom-sheets (eclipse, life-area,
  muhurat, calendar-doctor, ask, time-capsule) read from `theme.ts` tables.
- **Real vs faked:** interactions are REAL (drag, taps, state, earning, check-in logic); the data +
  "intelligence" are DEMO (timings, panchang, month calendar, chat/ask verdicts, Decode readings) —
  hardcoded/template, ready to swap for backend calls. Timeline / People / Rituals / You = placeholders.

## Why Claude Code ports it (not Antigravity)
1. **Expo migration skills** for exactly this: `expo:web-to-native`, `expo:building-native-ui`,
   `expo:use-dom` (load these when building) → canonical RN patterns, not guesswork.
2. **Self-verify visually:** run the Expo **web target** (`expo start --web`, react-native-web) in the
   Browser pane and iterate (the thing the bad Gemini port never did). **CONSTRAINT: cannot run native
   Expo Go here** → I verify layout/logic on web; **the user verifies final native fidelity (gestures,
   the slider at 60fps) in Expo Go and reports back**; iterate.
3. **One owner for build + wire:** I know the backend cold, so after the port I wire the live Render APIs
   + Supabase auth/JWT + on-open loop + expo-notifications + expo-calendar + Realtime, then final tweaks.
4. **Trick — `use-dom`:** for the hardest-to-reproduce visual bits (esp. the living-sky drag slider),
   wrap the prototype's EXACT web code as an Expo DOM component inside the native shell (preserve the look,
   rebuild natively only where native feel matters: nav, scroll, gestures).

## Target stack + structure
Expo **SDK 54** (pinned to the user's Expo Go), TypeScript, **Expo Router**, **react-native-reanimated**
(motion), **react-native-gesture-handler** (slider), **react-native-svg** (living sky/vector), **expo-image**
(cross-fades), **react-native-safe-area-context**. **Plain StyleSheet, no Tailwind/NativeWind.** Build into
the repo's **`mobile/`** folder (the old rejected port there is being cleared).
Folders: `app/` (Expo Router: `(tabs)/` today+4 placeholders, `chat.tsx`, `you.tsx`) · `src/theme/`
(tokens + `moods.ts` 12-mood table + ThemeProvider) · `src/components/` (Press, Sheet, Icon, GlossIcon,
Card, Chip…) · `src/features/today/{read,plan,checkin}/` + `src/features/chat/` · **`src/api/`** (client +
`types.ts` one type per shape + per-domain fns returning typed MOCKS in `mocks/`) · `src/config.ts`
(BASE_URL placeholder) · `src/hooks/` · `src/lib/` · `assets/`.
**Wiring-ready seam (critical):** ALL demo data lives behind `src/api/` (typed); screens call only those;
Claude Code later swaps the MOCK impl → live Render fetches in that ONE folder (no screen changes).

## Build order (vertical slices; run + verify each before the next)
1. **Scaffold** Expo SDK54 in `mobile/` + deps + babel reanimated plugin + folder tree + `theme/` (tokens
   + 12-mood table + ThemeProvider) + empty `src/api` (types + mocks) + nav shell (tabs + "coming soon"
   placeholders + FAB placeholder). Runs + navigates, empty.
2. **Design system** primitives from `astro.tsx` (Press, Sheet, Icon, GlossIcon, Card, Chip, `rise()`
   stagger, reduced-motion hook).
3. **Today → Read** (THE hero, get it faithful first): LivingSkyHeader, ReadingHero (mood-tinted),
   Today-across-your-life (3 rows→sheets), Mirror, ritual nudge, Grahan sheet.
4. **Today → Plan:** the My Day **Living-Sky drag slider** (hardest; Gesture Handler + Reanimated, or the
   `use-dom` trick), then Ask the Moment, My Panchang, Muhurat, Calendar Doctor, Time Capsule (sheets).
5. **The Sage:** chat + FAB (3 avatar states, breathing, unread dot) + the **KIRAN distress guard**.
6. **Check-in** flow + **Diyas** state.
7. **Polish:** keyframes → Reanimated, Press scale, reduced-motion, the 4 placeholder tabs.
Then **WIRE** the live backend (Claude Code): swap `src/api` mocks → real fetches; the exact endpoint
shapes are in `FEATURE_SPEC.md` + this file's §1; JWT-gated = `/me/* /planner/* /capsule/* /moon/*
/memory/*`; public = `/dashboard/* /rituals/today /oracle/prashna /geo/search`.

## TO START (after compaction): what's needed
The port's ONLY blocker = the prototype SOURCE must be in this repo so Claude Code can read it. **User
drops into the repo (e.g. a `prototype/` folder):** `Home.html`, `theme.ts`, `astro.tsx`, `astro-today.tsx`,
`astro-plan.tsx`, `astro-screens.tsx`, the **design MD**, and the **assets** (sage PNG states, `chatfab`,
mood emblems). Then Claude Code loads `expo:web-to-native`, scaffolds `mobile/`, and builds the **Read-tab
vertical slice first**, verifies on the web target, user checks in Expo Go, then rolls forward.

---

# 1 — TODAY SCREEN  ·  ⬇️ PASTE THIS INTO CLAUDE DESIGN (the Today tab)

> Design the **Today** screen of a warm, premium Vedic-astrology mobile app (phone-sized, iOS + Android).
> I'm giving you structure, content, exact copy, and how each part works; bring your own top-tier visual
> and motion taste, and where I describe a behaviour, weigh your best idea against it and use whichever is
> better. It should feel **warm, cozy, personal, like a caring friend, never clinical or cluttered.**
> **Show no app name or logo anywhere.** Voice for all copy: warm, plain English, a little tender; no
> astrology jargon, no em dashes, no mystical or AI filler.
>
> ## The frame (visible on the Today screen)
> - **Bottom navigation bar — five tabs, left to right: Today (active) · Timeline · People · Rituals ·
>   Readings.** Each tab is a small icon + label; the active tab (Today) is clearly highlighted. There is
>   **no "You" tab**, the profile is reached from the avatar (below). Only Today is built now; the other
>   four are tappable placeholders.
> - **Top cluster (sits above the content):** top-left, the user's round **avatar photo** (tap → their
>   "You" profile); top-right, a small **Diya coin chip** showing a balance ("240 🪔") that briefly
>   animates "+1" when a coin is earned (tap → the Diyas wallet). No other icons in the top bar.
> - **Floating Sage button (bottom-right, floating above the nav bar):** a small, warm **Sage** character
>   that feels alive, softly breathing, with a gentle glow and a subtle chat-bubble hint so it clearly reads
>   as "tap to talk"; it **glows brighter with a small dot when it has something to say.** Tapping it opens
>   the **Sage chat** (that chat is a separate screen with its own prompt, here, just place the floating
>   button and its glow/dot state).
> - **Sub-tab switcher (at the very top, directly under the top cluster, above everything else including
>   the greeting):** a two-option switcher **Read · Plan** (a segment / pill control), pinned at the top
>   as you switch. The screen opens on **Read**. There is **no shared header across both tabs** — the
>   time-aware greeting belongs to the Read tab only (below).
>
> ## Pop-up rule
> Anything that needs more room but not a whole screen opens as a **bottom-sheet** (slides up from the
> bottom, dim behind it, swipe down to close). **Two things get a full screen** (they deserve room to
> breathe): the **month calendar** (inside My Panchang) and the **journal writing view** (the Mirror). A
> card's short "why" instead **expands inline** (a gentle accordion), never a pop-up.
>
> ## Naming rule
> Plain English everywhere; keep only the common words a layman already knows (Panchang, Muhurat, Grahan,
> Dasha, Nakshatra). Describe time windows in plain English ("your strongest window", "best to hold off"),
> never "Abhijit / Rahu Kaal" up front, those names sit behind a small "why?".
>
> ---
> ## READ tab — the daily read + the quick log (top to bottom)
> A short, calm stack that ideally fits about **one screen** (a glance, not a feed). A card's short "why"
> **expands inline**; anything bigger opens a bottom-sheet (or a full screen for the journal / month
> calendar). Let the day's **mood gently tint the ambiance** for cohesion.
>
> **Greeting header — the Read tab's own header, at the top of Read, just under the Read · Plan switcher.**
> Time-aware: the light and mood shift through the day (dawn → noon → dusk → night). It shows tonight's
> real **Moon phase**, a warm greeting with the user's first name + the date ("Good evening, Aanya ·
> Tuesday, 24 June"), one quiet plain-English line for the **live planetary hour** ("a good stretch for
> money and focus right now") — the day's one live-timing nugget — and, **on a festival, a warm one-line
> wish woven in** ("Happy Makar Sankranti"), no separate card. Read-tab only; the Plan tab has none.
> [Header data: `/dashboard/hora` returns the Hora line, Moon phase, and a `festival` field (or null).]
>
> Then a **short, calm stack — aim for 2 to 3 visible cards.** Read is "how today *feels*"; anything to
> *do* with the day lives in **Plan**, and anything to *talk through* lives with the **Sage**. Keep it
> uncluttered, cozy, no fluff.
>
> **1. Grahan heads-up — conditional (only near an eclipse; hidden otherwise).** A gentle card at the very
> top: a countdown ("Chandra Grahan in 4 days"), one calming line ("a few quiet days ahead, nothing to
> fear"), and the traditional caution-time. Tap → a bottom-sheet with the date, fuller gentle guidance, and
> what to ease off. (A **festival greeting is not a card** — it lives woven into the header above.) Make
> the present/absent state toggleable so it can be reviewed.
>
> **2. The reading — THE hero (the one card the whole screen is built around).** Contains, in order:
> a soft mood **image** + a single **mood word** for the day (one of exactly these twelve: Settled,
> Guarded, Bold, Tender, Restless, Capable, Warm, Deep, Wandering, Driven, Upbeat, Quiet); one warm
> **sentence** on the day's texture ("Your heart leans homeward today, you may feel a little softer than
> usual."); a light **personal line** shown only when there's a real one from the user's recent history
> ("you've had a heavy few days, let's keep today gentle"), gracefully hidden otherwise; then two short
> rows of chips, **Good for** (2–3, e.g. "money talks · finishing things") and **Go easy on** (2–3, e.g.
> "signing · travel"); and on the rare off-days, a gentle line "a low-key day for you, keep it light."
> Then one quiet **footer line** carrying the day's single most-useful timing nugget: "Your strongest
> window today: 11:40–12:30" (tap → jumps to **Plan → My Day** for the whole day). A small **"why?"**
> **expands inline** (a gentle collapse/expand, never a pop-up) to reveal the plain-English reason — which
> planet / nakshatra / day-star it comes from, so it feels grounded and true. Same all day; changes daily.
> *(This footer replaces a separate good/bad-times card — the "now" is in the header, the full day in Plan.)*
>
> **3. Today across your life — Love · Work · Money (three slim rows, the daily horoscope substance).**
> Done our honest way: three one-line reads, each **naming the planet behind it, with NO scores and no fake
> precision**. E.g. Love — "warm and easy today, Venus is with you" · Work — "a focused day to push,
> Saturn steadies you" · Money — "hold the big spends, the flow's mixed". Distinct from the reading (that's
> the day's overall *feeling*; this is the three domains). **Each row opens its OWN bottom-sheet** (Love,
> Work, Money alike) that adds more than the card shows: the one-liner, a fuller *what it means today*, and
> a small **"why?"** with the plain astrology (e.g. "Venus is your love marker, and the Moon's moving
> through your partnership area"). At the foot of the sheet, **one contextual link to where more on that
> area lives — shown ONLY when a destination exists**: Love → People, Work → Timeline, Money → Timeline
> (tab-level for now; we point them at the exact feature once the rest of the frontend is built). **No row
> jumps straight to a tab — it always opens its sheet first.** Personalized by the Memory when there's a
> real thread; keep the card itself compact, three tidy rows.
> Backed by **`/dashboard/today`** — ONE bundle returning the reading + these rows, computed together so
> the reading's **Good for / Go easy on** chips and these rows **can never contradict** (a guard drops any
> clashing chip, e.g. no "good for big purchases" chip on a hold-your-money day). [Also `/dashboard/life-areas`
> standalone; each row returns `{ line, detail, why, planet, link }`. love=7th/5th·Venus,
> work=10th/6th·Saturn·Sun, money=2nd·11th·Jupiter; deterministic, no AI, no %.]
>
> **4. The Mirror (journal) — a pretty, cozy invitation card (no controls on its face).** Just a soft
> prompt "What's on your mind?" and a warm, inviting look — **no mic icon, no buttons.** Tapping **anywhere
> on the card opens a FULL-SCREEN writing view** (the journal deserves room, not a cramped sheet). That
> full screen is calm and comfy: the prompt, a generous text area, a **voice / mic** option to speak
> instead of type (no formatting, no pressure), and on save the **Sage returns one warm line** tuned to the
> feeling (comfort if heavy, a quiet smile if happy) with a soft **"talk about it? →"** that opens the Sage
> chat. Back on Read, the card simply marks "you wrote today." It never lists past entries — this is for
> setting things down.
>
> **5. Today's ritual — a slim one-line nudge.** "Today's ritual: light a lamp at dusk · Begin →". "Begin"
> deep-links to the **Rituals tab** (the full step-by-step, mantra audio, etc., lives there, not here).
>
> ### The daily check-in — a POPUP, not a card in the stack
> On the **first open of each day**, a warm **bottom-sheet** rises on its own: "How are you today?" with
> one row of **mood** chips (calm, tender, sharp, heavy, wired); the moment one is tapped it **swaps** to a
> row of **energy** chips (low, steady, bright, restless); then the **two picks + one warm pre-written
> line** ("Heavy, and a tender day, so the weight is real, not random.") + a **streak** ("12 days in a
> row") + a small **"+1 🪔"** flying up to the Diya chip, then it closes. An **"Ask me later"** button
> dismisses it; if dismissed, a slim **"How are you today?"** chip sits at the top of Read so it's
> reachable any time, and the Sage may gently ask once in the evening if it's still not logged. Keeps the
> check-in **off the daily scroll** and makes it a small ritual. Pre-written, **no AI** (`/me/checkins` +
> streak).
>
> ---
> ## PLAN tab — the tools, in two calm groups (what to do *today*, and how to plan *ahead*)
> No greeting header; it opens straight into the tools, split into **two light sections** so it never reads
> as a random pile. Each tool is a **warmly-named card + a one-line description** (the name is the hook, the
> line says what it does — keep the names: My Day, My Panchang, Muhurat, **Calendar Doctor**, **Ask the
> Moment**, **Time Capsule**). Where a card has something **live and useful** to show, it previews it right
> on the card; otherwise just the name + line, never bare filler. Tapping a card opens its bottom-sheet (the
> month calendar is the one full screen).
>
> ### Today
> **My Day (inline hero) — your day, hour by hour.** A clean horizontal strip of windows, **strong / good
> / lie-low**, with a "you are here" marker. An **add-a-task** field: the user types a real to-do ("send
> the pitch", "call mom", "pay the bills") and it **drops onto the best matching window**, keeping
> important things clear of the lie-low stretches. **Vedic timing is window-based** — a Choghadiya / Hora
> *stretch* (e.g. 9:22–11:02) or the ~48-min Abhijit, never a single exact minute — so a task lands in a
> *stretch* and its reminder fires **~15 minutes before that window**; we never fake pinpoint precision.
> Tasks can be ticked off; over time it can suggest recurring ones. With nothing added, it's still a useful
> at-a-glance day.
> [`POST /planner/tasks`; a tiny AI call **reads the to-do** (any language / Hinglish) into an *importance* +
> the *planetary-hour (Hora) energies* that suit it (`shared.ai.understanding`, classify-only). The engine
> then places it: Choghadiya **quality first**, then a **matching Hora** as a tiebreaker (a comms task drifts
> to a Mercury hour, exercise to Mars, money to Jupiter), never a poor window just to match. No API key →
> the client's importance flag + quality-only placement. The response includes `understood` + `placement`.]
>
> **Ask the Moment — ask a real question, get a clear answer for right now.** Give this one **real
> prominence** (it's a daily quick-decision tool, not an occasional one): a **taller card right under My
> Day**, with **2–3 tappable sample questions shown on its face** ("Should I make this call?", "Is today
> good to start?", "Will this work out?"). Tap one (or type your own) → the sheet opens → a chart visibly
> forms for that exact instant → **one clear answer** (Yes / Not yet / No) + a short plain "why". Show a
> small **"Read as: {interpreted}"** line above the answer (e.g. "Read as: will you get the job?") so the
> user sees what the app understood and can rephrase — this is how we handle any language and negation
> honestly. **Progressive disclosure, not a mode-picker:** the yes/no answer is **free and shows instantly**;
> beneath it sits one tempting button **"Go deeper — the full reading (15 🪔)"** that unlocks a warm,
> book-grounded explanation, and a **"Talk it through →"** into the Sage chat. A one-shot oracle, clearly
> different from the Sage's open conversation.
> [This is real horary (Prashna): `POST /oracle/prashna { question, lat, lon, tz, narrate }` → returns
> `verdict, reason, topic, interpreted, reading`. **A tiny AI call READS the question** (any language /
> Hinglish / negation) into the right Vedic house + a positive restatement (`shared.ai.understanding`,
> classify-only — falls back to a keyword house-map with no API key). Then the **deterministic KP engine**
> computes the verdict for that house (the Python verdict is the final word; AI never decides it).
> **`narrate: false` = the FREE path** — verdict + `reason` + `interpreted`, no narrative generated (only the
> tiny classify). **`narrate: true` = the DEPTH path (costs 15 🪔)** — the *same* verdict plus an AI
> narrative grounded in the classical KP text via RAG. The engine does 100% of the astrology; AI only
> understands the words and (on depth) phrases the explanation.]
>
> ### Plan ahead
> **My Panchang — your days ahead, coloured for you.** The card **previews today + the next 2 days** as
> softly-coloured dots (**good / mixed / low for you**). Tap → a **full-screen month** calendar, every day
> coloured the same way, with **festivals, full / new moons, Grahan, and your Dasha changes** marked, plus
> the user's own planned tasks. Tap any day → a sheet (why it's good/low + that day's good times). Can
> **sync your good days to your phone calendar.**
>
> **Muhurat — the best date and time for anything that matters.** Show a handful of quick event chips
> (wedding · travel · buy a vehicle · buy property · new job · start a business · surgery · naming · mundan ·
> start studies) **plus a text box to type your own** ("start a YouTube channel"). Pick or type → the sheet
> returns the **top few dates + exact times** ahead, in plain English. [`/dashboard/muhurta`; the engine now
> has **14 sourced classical rule-sets** (travel, vehicle, marriage, property, housewarming, surgery,
> medical, education, mundan, annaprashana, naming, job, business/signing, general), each cross-checked
> across multiple panchang authorities. A preset chip is used as-is; **free-text is read by a tiny AI call**
> (any language / Hinglish / phrasing → the nearest set, `shared.ai.understanding`), falling back to a
> keyword classifier then "general" with no API key. The AI only classifies — `plan_muhurta` does all the
> date/time astrology. Surgery correctly uses the inverted classical rules (sharp stars, Tue/Sat, Rikta
> tithis favoured). Anything truly outside the sets lands honestly in "general".]
>
> **Calendar Doctor — we check your plans against your good and bad times.** The app **reads and moves
> events on the device** (expo-calendar, Android + iOS, with permission). It sends just the event **times**
> (no titles stored) to `/dashboard/calendar-check`, which returns each event's verdict (**good / ok /
> weak**) + a plain label ("sits in a hold-off stretch", "a warm, easy window") + a **"move to →" slot** for
> weak ones. The card shows a gentle **badge** when something clashes ("2 plans in a rough patch this
> week"); the sheet lists the events with a one-tap **move** button that updates the event on-device. No
> permission or nothing flagged → just the name + line. All the timing math is **free, no AI**.
>
> **Time Capsule — write to your future self; the sky picks when to deliver it.** If a capsule is arriving
> soon the card **previews the hint** ("a note from your past self arrives in 3 days", never the content);
> otherwise the name + line + your small shelf of sealed + landed capsules. Opens a note box, then a
> **custom date picker**, then "**or pick a moment:**" (your next birthday · your next Dasha chapter · the
> next time Jupiter favours you). On save → a **beautiful sealing animation**; on the delivery day it
> **reveals** the note with context.
>
> **Overall:** two calm sub-tabs, a clear bottom nav, satisfying bottom-sheets, a living Sage in the
> corner. Your design judgment leads on look and motion.

---

# 1b — THE SAGE (chat + the floating companion)  ·  ⬇️ PASTE THIS INTO CLAUDE DESIGN

> Design the **Sage**, the app's companion: a warm, cute character that floats on every screen and opens
> into a chat. Same voice everywhere: warm, plain, a little tender, sincere; no jargon, no em dashes, no
> mystical or AI filler. No app name or logo.
>
> ## Who the Sage is
> The user's **astrologer who actually knows them**: a small, kindly sage with a soft round face, a gentle
> smile, a wisp of white beard, calm twinkly eyes, warm and grandfatherly, approachable and a little cute,
> never stern. Keep him an **archetype**, not any real guru, and with no deity markers. He is grounded in
> the user's birth chart, their remembered history (past chats and journal notes), and classical texts, so
> he speaks specifically and truly, never in generic horoscope lines. Always sincere and gentle, never
> witty, never alarming. (His name is **Sage** by default; that is the handle shown in the chat header.)
>
> ## The floating button (make it obviously a chat)
> Bottom-right on every screen, above the nav bar: the **Sage**, small and alive (a soft, slow breathe),
> with a gentle glow. Make it **clearly tappable**: a subtle **chat-bubble hint** by him, and on the very
> first app open a one-time gentle **"Ask me anything"** nudge that fades after a moment. When he has
> something to say he **brightens and shows a small dot**. Tapping opens the chat.
> [For motion, design separable states: **rest** (soft breathe) → **has a message** (glow + dot) → **tap**
> (a small warm reaction) → opens the chat. Built with Rive or Lottie.]
>
> ## The screen
> A warm conversational view (slides up over the current screen, or its own screen, your call). The **Sage
> sits at the top, warm and alive**. Below, a chat thread. An input field at the bottom with a **mic**
> option for voice. Unhurried, like texting someone who genuinely knows you.
>
> ## The first-ever open: a warm welcome (already built on the backend)
> The very first time the user opens the app, the Sage greets them with a one-time intro as the first
> message: who he is, that he reads their real chart (not a generic horoscope), that he quietly remembers
> them over time, that he will reach out now and then with a pattern or a gentle nudge, that they can ask
> him anything, and that everything stays private. Just render it as his opening chat message. [Backend: it
> arrives as the first `GET /moon/messages` entry, kind `welcome`, generated on the first `POST /moon/check`.]
>
> ## Show a real example conversation (so the "it knows me" feeling lands)
> The Sage opens warmly and specifically ("Hey Aanya. The day's running tender, and you've been low this
> week, how are you holding up?"); the user replies in plain words ("yeah, work's been a lot"); the Sage
> answers grounded in their chart and history ("That tracks. With your Moon where it is, these in-between
> days always ask more of you. Want to talk through the job thing you mentioned last week?"). Caring and
> concrete.
>
> ## The Sage reaches out first (the important part)
> He is **proactive**: when he has something for the user, the floating button (on the other screens)
> **glows with a small dot**, and opening the chat shows a fresh message he started, one of:
> - **a pattern he noticed** ("you tend to dip on days like today, when the Moon's in Scorpio, that's not
>   random"),
> - **a look-back** ("a year ago today you wrote about the interview, look how that turned out"),
> - **one thoughtful nudge** ("a warm day for family, and you said you've been missing your dad, a good day
>   to call him").
> He sends **one at a time** (never a pile), and the user can **reply**; what matters is quietly remembered
> for next time. Show one proactive opener as an example state.
>
> ## Tone + safety (hard rules)
> Always warm, calm, sincere, never alarming, never fear-selling. **The Sage never asks for money or pushes
> paid features in his own voice** (any upgrade lives in neutral app UI, never "pay me"). If a user writes
> something heavy or in crisis, he responds with care and gentle support (not astrology advice, and gently
> points toward real help). Plain, kind, present.

---

# 2 — ONBOARDING FLOW (+ Login)

> **Updated 2026-07-15 — endpoint shapes verified live; Supabase is now set up.** Build this to
> MATCH THE EXISTING BUILT APP exactly (the ASTROLO Today/Chat/Readings screens) — same design
> system (`astro.tsx`): bright white, Hanken Grotesk / Newsreader / Spline Sans Mono, one calm
> indigo accent for onboarding, glossy tiles, soft ROUNDED transparent shadows (never square),
> pills, warm plain-English voice (no em dashes, never AI-sounding). Every step: a small mono
> step indicator, back arrow, one primary button, roomy spacing, gentle rise-in. **The daily
> readings already run on the captured profile alone — sign-up only adds saving + "remembers
> you" features.** The Supabase project is LIVE (keys in `.streamlit/secrets.toml`), so sign-up/
> login is REAL (Supabase Auth), not stubbed.

Flow: **Welcome → Name+gender → Birth date+place → Birth time → Reveal → Sign-up**, with **Login**
branching off the Welcome link. No app name/logo. Depth-mode is NOT asked here (it's a Settings toggle,
default 'simple'). **Keep the LocationIQ attribution on the place screen — REQUIRED** ("Search by
LocationIQ", linking https://locationiq.com; it's a condition of the geocoder we use).

**1 — Welcome**
> First screen, same calm visual system. No app name/logo. Headline "Meet yourself, exactly as you are."
> Supporting line "Astrology without the noise." A simple celestial/Moon visual. One main button "Begin".
> Below it a small text link "I already have an account" (opens Login, not onboarding). No input.

**2 — Name + gender**
> Step titled "Tell us about you," small step/progress indicator at top. A first-name field ("What should
> we call you?"), and an optional gender selector as three soft chips, Female / Male / Other, with a small
> note "used for certain Vedic readings." "Continue" enabled once a name is entered. Capture `name`
> (required), `gender` ('Female'|'Male'|'Other'|null). Maps to backend `name`, `gender`.

**3 — Birth date + place**
> Step titled "When and where were you born?", step indicator, generous spacing. A clear date-of-birth
> picker (day/month/year); and a place search showing live city suggestions as they type ("Mumbai, India",
> "Pune, India"), selecting one fills it in. A small note "your town is enough," and directly beneath it a
> subtle attribution line "Search by LocationIQ" (linking https://locationiq.com). "Continue" enabled
> once both set. Capture `birthDate` ("YYYY-MM-DD"), `birthPlace` as `{label,lat,lon,tz}`. Wiring:
> place field calls `POST /geo/search { query }` → **VERIFIED** `{ results:[{label,lat,lon,tz}] }`
> (already wired in `mobile/src/api/geo.ts`); the "Search by LocationIQ" credit MUST stay visible.
> Maps to `birth_date`, `birth_place`(=label), `lat`, `lon`, `tz`.

**4 — Birth time (3 levels, with consequences)**
> Step about birth time, step indicator, designed so the user always understands their choice. "Do you
> know your birth time?" with three soft option cards, each with a one-line consequence note:
> - "I know my exact time" — "Most precise: unlocks your rising sign, houses, and exact timing." → reveal
>   a time picker.
> - "I know it roughly" — "Still accurate: only the finest timing details may shift." → reveal a
>   part-of-day selector (early morning, morning, afternoon, evening, night).
> - "I don't know it" — "No problem: we'll build a Moon-based chart full of insight, and you can add your
>   time anytime to unlock your rising sign and houses."
> Below, a subtle expandable "Why does this matter?" "Continue" always enabled. Capture
> `birthTimePrecision` ('exact'|'approximate'|'unknown'), `birthTime` (exact's time; rough → representative
> time, early morning 06:00 / morning 09:00 / afternoon 14:00 / evening 18:00 / night 22:00; else null).
> Rule: rising sign + houses unlock ONLY when precision is 'exact'. Maps to `birth_time`,
> `birth_time_known` (true unless 'unknown'), `exact_time` (true only for 'exact').

**5 — Reveal (the first wow, with the Proof)**
> A warm, personal "Here's who you are," before any sign-up. A soft image keyed to gender. On load it
> shows: a serif headline naming who they are; two or three short insight cards (small label + warm
> one-line plain-English insight, with the deeper Sanskrit/technical layer behind a quiet "why?" tap); and
> its own section "Where you are right now" describing the life chapter they're in. If birth time is
> rough/unknown, a soft note explains what's already readable and what unlocks later, collapsing
> gracefully. Then "Want to see how real this is? Pick a day that mattered to you," and on a past date it
> reveals what the sky was doing then and how it fits (optional, with "Maybe later"). A primary "Continue"
> to Sign-up. Gentle loading ("Reading your sky...") + soft fallback. No sign-up/paywall here. Wiring: post
> `{ profile }` (profile = `{ name, date:birthDate, time:birthTime or "12:00", place:label, lat,
> lon, tz, gender, exact_time }`) to `/chart/interpret` → **VERIFIED** `{ headline, core:[{title,
> body,sanskrit,why}], birth_star:{title,body}, current_chapter:{title,body}, precision_note }`
> (render `headline` + the `core` cards + `birth_star` + `current_chapter`; "why?" reveals each
> card's `sanskrit`). The Proof posts `{ profile, date }` to `/companion/proof` → **VERIFIED**
> `{ headline, story, running:{mahadasha,antardasha,since} }`. All real + stateless (no auth).

**6 — Sign-up (last onboarding screen)**
> The only place we ask, after they've felt the value. Headline "Let's keep your story safe." Line "So
> your readings, your journal, and your memory are always here." Buttons: "Continue with Apple", "Continue
> with Google", "Continue with email" (stubbed). Privacy line "Your birth details and journal stay private
> to you. Always." After this → Today. Wiring: creates the Supabase account, then saves the self-profile
> via `POST /me/profiles` (`name, gender, birth_date, birth_place, lat, lon, tz, birth_time,
> birth_time_known, exact_time, relation_tag:'self', source:'self'`).

**Login (where "I already have an account" leads)**
> Same calm system. Headline "Welcome back." Line "Pick up right where you left off." Buttons "Continue
> with Apple / Google / email" (email+password for the email option). A small link "New here? Start fresh"
> → Welcome. Wiring: Supabase Auth sign-in, then `GET /me/profiles`, then land on Today, skipping
> onboarding. (Login backend exists: Supabase Auth client-side + `features/me/auth.py` JWT + the
> `handle_new_user` trigger.)

Onboarding state object: `{ name, gender, birthDate, birthPlace{label,lat,lon,tz}, birthTimePrecision,
birthTime }`. Every field maps to an existing endpoint.

---

# 3 — OTHER SCREEN PROMPTS (build after Today + onboarding)

## Diyas wallet (opens from the Diya chip)
> **Balance hero:** a glowing diya/oil-lamp with the count ("240 🪔 lit"), brighter at higher balance.
> **Earn ("light a diya by doing good"):** a checklist with progress, Daily check-in +1 (done), Today's
> ritual +2, A journal note +1, 7-day streak +10, Invite a friend +25, plus a **daily-cap** indicator
> ("3 of 5 earned today"). **Buy Diyas:** three tiles with the bonus, Glow ₹99 → 110, Blaze ₹299 → 380
> (best value), Festival ₹799 → 1,150. **Go Plus card:** "Unlimited chat, couple, family and deep
> Patterns, cross-reference free, and 25% off everything. ₹199 a month, 7-day free trial." **History:** a
> ledger of earned/spent rows (date, what, ± amount). Wiring: `GET /wallet/balance|history`, earn/spend
> via `/wallet/*`.

## Readings tab (the old Decode, now a bottom tab)
> A calm directory, not a dashboard. **Your kundli** (anchor card): mini birth-chart + name + birth line +
> Lagna/Moon/Sun chips + "Open full chart →" (all deep detail, 12 houses, planets-now, divisional charts,
> lives behind this, NOT on the landing) + a small **trust line** ("Built from NASA and JPL data, the same
> true chart every time") + "Save as a PDF keepsake" (60 🪔). [`/kundli/compute`, `/chart/interpret`,
> `/kundli/premium-pdf`] · **Readings** (rows w/ Diya price): Full Life Reading 60 🪔
> [`/oracle/deep-analysis`] · Marriage & Destiny 40 🪔 [`/oracle/marriage`] · Your Purpose 40 🪔
> [`/reflect/purpose`] · Ask one question (Prashna) 15 🪔 [`/oracle/prashna`]. · **Match two charts** (own
> card, prominent for rishta): quick guna score free, full report 30 🪔 [`/oracle/matchmaking`]. ·
> **Tools** (2-col grid): Numerology · Palmistry · Face Reading · Tarot (free taste, then Diyas). **Left
> out on purpose:** the running-Mahadasha card (Timeline's hero), the planets-now grid (inside "Open full
> chart"), and the Auspicious-Days/Muhurat planner (it lives in the Today → Plan tab now). It's a bottom
> tab, so it shows the bottom nav, no back arrow.

## Nav-change (apply across the whole app)
> **Remove "You" from the bottom navigation bar**; instead the user reaches their profile/You by tapping
> their **round avatar photo in the top-left corner** (every screen). The bottom nav has five tabs, left
> to right: **Today, Timeline, People, Rituals, Readings.** Top-right keeps the small **Diya coin chip**.
> Keep the floating Sage companion bottom-right. No separate "Readings" top-bar icon (it's a tab now). No
> app name or logo. Apply this top cluster + five-tab bottom bar consistently everywhere.
