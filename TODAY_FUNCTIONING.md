# Today screen — how it actually self-functions (build spec)

> **Why this file exists:** the design says *what* each feature is; this says *how it runs by itself* in
> the app, what loads when, what's automated, how notifications fire, how nothing breaks. Written so a
> future build (or a future me) can wire it without guessing. Companion docs: design prompt in
> `FRONTEND_PROMPTS.md`, AI spend in `AI_COSTS.md`, structure in `MOBILE_APP_BLUEPRINT.md`.

## 0. The golden rule (this is what makes everything "just work")
Mobile background execution (iOS especially) is unreliable. So **we never depend on code running while the
app is closed.** Instead, everything is driven by **one routine that runs every time the app opens (the
"on-open loop")**, plus **local notifications scheduled in advance** (those *do* fire while closed,
because the OS owns them). If the app is opened even once a day, everything stays correct.

**The on-open loop (runs on launch + on resume from background):**
1. **Auth check** — is the Supabase JWT valid? If expiring, refresh it. (Profile + token cached locally.)
2. **Load today's data** — if not already cached for *today's date*, fetch the daily bundle (below) and
   cache it keyed by `(user_id, YYYY-MM-DD)`. If cached, use the cache (instant, no network).
3. **(Re)schedule local notifications** for the rest of today + the near future (windows, check-in
   reminder, any Grahan, any Time Capsule hint/delivery). Cancel stale ones first, then reschedule from
   fresh data. This "rebuild on every open" keeps them always correct.
4. **Check the proactive Moon** — is there a new pattern / look-back / sky-memory match? If yes, set the
   Moon FAB to glow.
5. **Render** from cache. Never block the screen on the network (show cached/placeholder, fill in when it
   arrives).

## 1. Data & caching
- **The daily bundle** (one batch on first open each day): `/dashboard/forecast`, `/dashboard/timing`,
  `/dashboard/day-alerts`, `/memory/today`, `/rituals/today`, and the panchang day-state. All are
  **deterministic for a given profile+date**, so they're computed once and cached for the day (the
  backend also has `cached_daily`). Result: Today opens instantly and costs ~nothing.
- **Cache key** `(user_id, date)`; bust at local midnight (the date rolls). Keep the last few days so
  back-scrolling/look-backs are offline-friendly.
- **Profile** is fetched once (`GET /me/profiles`, the `self` profile) and cached locally; every astro
  call sends it. All Moon-based endpoints work at any birth-time tier (unknown time → noon placeholder),
  so nothing fails without an exact birth time, time-only details just stay hidden.

## 2. Auth & profile
- Supabase Auth (client-side) issues the JWT → stored securely (expo-secure-store) → attached as
  `Authorization: Bearer` on every `/me/*`, `/memory/*` call. Refresh on expiry inside the on-open loop.
- A logged-out or token-dead state routes to sign-in; it never crashes a screen.

## 3. Notifications — the automation engine
**Library:** `expo-notifications` (local scheduled + push) and `expo-calendar` (read/write device
calendar). Permission is requested once, gently, during onboarding; if denied, **every feature still
works in-app**, there are just no pushes.

**Almost everything is a LOCAL scheduled notification** (the app computes the fire-time from data it
already has, schedules it ahead, and the OS fires it even when the app is closed):

| Notification | How it's scheduled | Fires |
|---|---|---|
| **My Day window alert** | when a task is placed in a window, schedule a local notif for `window_start − 15min` | "Your strong window for the pitch opens in 15 min" |
| **Daily check-in reminder** | one repeating local notif at the user's chosen time (default ~10am) | "How are you feeling today?" |
| **Grahan heads-up** | when the daily bundle reports an eclipse within range, schedule one for the day before / Sutak start | "Chandra Grahan tomorrow, a calm day ahead" |
| **Time Capsule hint** | at create time, schedule a local notif for `deliver_date − 3 days` | "A note from your past self is almost here 🌙" |
| **Time Capsule delivery** | at create time, schedule a local notif for `deliver_date` | "Your time capsule has arrived" |

**Push (server-sent, used sparingly)** only for things the device can't precompute from cached data:
a freshly-unlocked **pattern**, or a strong **proactive Moon** moment computed server-side. Backend
sends via Expo Push to the device's saved token. Keep this minimal (cost + restraint).

**User controls (Settings):** master toggle + per-type toggles (daily reading, check-in reminder, window
alerts, Grahan, Time Capsule, proactive Moon) + **quiet hours**. Honour them before scheduling anything.

## 3b. Live appearance while the app is OPEN (real-time) — CRITICAL
> §0 + §3 cover the app-**closed** path (scheduled local notifications). Equally important: when the app
> is **open**, things must appear/update **live, with no manual refresh**, and we **own** that, we do NOT
> rely on the OS notification alone. Four cases (all standard, all cheap):

**A) Open + time-based (no server).** A light **foreground ticker** (`setInterval`, ~every 30–60s) + an
**AppState "active" listener** (fires when the user returns to the app) recompute time-sensitive UI from
already-loaded data: the day-clock "you are here" marker advances, the **Hora** line rolls over, a
**Grahan** that just entered its window appears, a **Time Capsule** whose delivery moment just passed
**flips to revealed right there.** Cheap, it only compares `now()` to known timestamps; no network.

**B) Open + server-driven → Supabase Realtime.** We already use Supabase; its **Realtime** feature streams
Postgres row-changes to the open app over a websocket (**no polling**), **RLS-filtered to the user**. The
app **subscribes** (in a `useEffect` with cleanup, scoped to `user_id`) to the tables that drive live
surprises:
- a new **pattern** unlocked (`patterns`) → the **Moon FAB glows** + a soft banner, instantly.
- a new **proactive Moon message** (a `moon_messages` row the backend inserts) → shows in chat live.
- **Diya balance** (`coin_wallets`) → the chip updates the second a coin is earned/spent.
So when the backend computes something, it appears immediately, no refresh, no reopen.

**C) Closed / background.** Scheduled **local notifications** (known times) + **Expo Push** (server
events). Tapping deep-links into the feature.

**D) The bridge — a notification that fires *while the app is open*.** With `expo-notifications` we set a
**foreground handler** (`setNotificationHandler`) + an **`addNotificationReceivedListener`**, so a
notification firing while you're using the app becomes a **gentle in-app banner / live update**, not a
jarring system pop-up. (iOS shows nothing in the foreground by default unless we wire this.)

**E) On reopen.** The on-open loop (§0) reconciles anything missed while closed and re-subscribes.

**Feature → which mechanism makes it appear on its own:**
| Needs to appear / update live | Mechanism |
|---|---|
| Day-clock marker, Hora rollover | A) foreground ticker |
| Grahan entering its window | A) ticker (open) + C) scheduled notif (closed) |
| Time Capsule reveal at its moment | A) ticker (open) + C) scheduled notif (closed) |
| Proactive Moon message / new pattern | B) Supabase Realtime (open) + C) push (closed) |
| Diya balance, streak update | B) Supabase Realtime |
| My Day window reminder | C) scheduled local notif + D) foreground banner if open |

**Honest gotchas:** (1) the relevant tables must be **enabled for Realtime** in the Supabase dashboard;
(2) every subscription must be **cleaned up on unmount** or it leaks; (3) keep the foreground ticker light
(compare timestamps, don't refetch). All standard.

## 4. Per-feature functioning

### READ tab
- **Header / Moon phase / Hora line** — all from the cached bundle (phase from the ephemeris, Hora = a
  pure weekday+sunrise calc). The time-of-day look and the live Hora update from the device clock; no
  network. Hora recomputes when the planetary hour rolls over (a local timer).
- **Grahan heads-up (conditional)** — shows only if `day-alerts.eclipse.present`. Tapping opens a
  bottom-sheet (cached detail). The heads-up *notification* is scheduled separately (above).
- **The reading (hero) + Today across your life (Love/Work/Money)** — from ONE cached bundle
  **`/dashboard/today`** (mood word, good-for/go-easy chips, why, + the three life-area rows) + the
  personal line from `/memory/today`. **Pure read, no AI, no live calls.** The "why" **expands inline**
  (accordion), not a bottom-sheet. **Contradiction guard (two layers):** (1) the day-quality here is the
  SAME `day_quality()` the Panchang uses for today's colour (one shared source); (2) the bundle
  **reconciles** the reading's chips against the Love/Work/Money tones (`reconcile_chips` drops any clashing
  chip) — so the reading, the rows, and the calendar can never disagree.
- **Good & bad times (compact)** — from cached `/dashboard/timing`; the "you are here" dot is a local
  clock comparison against the cached windows. Tapping opens the full-day bottom-sheet, which carries a
  **"Plan your day →"** link into My Day (same `timing` data, so identical).
- **Check-in (multi-step, self-collapsing)** — pure local UI + one write:
  1. shows mood row → on pick, swap to energy row → on pick, show both + a **pre-written summary line**
     (lookup table on `mood × energy × today's day-state`; **no AI, no network for the line**).
  2. `POST /me/checkins` writes the pick + bumps the streak (the only network call here).
  3. after ~12s, auto-collapse to a chip (the two picks + **Change** + **Expand**); expanding shows
     **Collapse**. Editable any time of day (re-POST, re-pick line).
  - Offline: the line + collapse work instantly from the lookup; the write queues and syncs later.
- **The Mirror** — `POST /me/journal` saves the entry. The **one warm line back is templated** by detected
  sentiment (no AI). The save triggers a **server-side background Memory extraction** *only if the entry
  has real signal* (selective, see §6); the UI doesn't wait on it.
- **Today's ritual (nudge)** — one line from cached `/rituals/today`; "Begin →" deep-links to the
  **Rituals tab** (the full guided/audio flow lives there, not duplicated).

### PLAN tab
- **My Day** — windows from cached `/dashboard/timing`. **Add a task** → a small on-device classifier
  (keyword/category → favourable window type) places it in the best free window, clear of the avoid
  windows; tasks persist (Supabase so they sync across devices, with a local mirror). Placing a task
  **schedules its `−15min` local notification**; completing/removing it **cancels** that notification.
  Recurring tasks + routine learning read past task history. No birth time needed (windows are
  location-based).
- **My Panchang** — the **3-day strip** (today + next 2) renders from `/dashboard/forecast` per day
  (cached) using the **shared day-quality function**. "Open full Panchang →" pushes a **full screen**
  month grid: each day coloured by the same function, overlaid with festivals (a static table),
  Grahan/retrograde/Dasha-change markers, and the user's My-Day events. Tapping a day → a bottom-sheet
  (why + that day's good times). **Calendar sync** writes chosen good days/muhurats to the device
  calendar (`expo-calendar`).
- **Muhurat ("Find a good day")** — its own Plan entry → bottom-sheet: pick an event type → one
  `/dashboard/muhurta` call → top dates+times. On-demand, no background. (Finance event-types live here.)
- **Calendar Doctor ("Check my plans")** — its own Plan entry → reads upcoming device-calendar events
  (`expo-calendar`, opt-in) → rates each against that day's windows → flags weak-slot events + offers a
  better slot → one tap reschedules the calendar event. Pure math, no AI.
- **Ask the Moment** — a bottom-sheet pre-filled with **sample questions** (which also teach what it
  does). Quick "should I now?" = `/dashboard/decide-quick` (Tara math, free). A deeper question / "A or
  B?" = `/oracle/prashna` (casts a chart for the exact tap-time; **RAG-grounded** interpretation).
  **Contradiction guard:** the "now" verdict blends the personal-Moon read *and* the current window so it
  never flatly contradicts the day-clock; it says so ("the moment favours you, though it's a quieter
  slot").
- **Time Capsule** — bottom-sheet: a note box + a custom date picker + "or pick a moment" (next birthday
  / next Dasha chapter / next Jupiter-favourable day; those dates are computed by the backend from the
  engine). On save: store `{note, deliver_date}` (Supabase) + **schedule the hint (−3d) and delivery
  local notifications** + play a **sealing animation**. The note is plain stored text (no AI). On each
  open, the card reflects state: normal → (within 3 days) a **hint glow, never the content** → (on/after
  deliver_date) the **full reveal** with context. The 2–3-day-prior behaviour is a **hint only** (the
  surprise is the point; showing it early adds nothing and kills the magic).

### The Sage companion (FAB)
> Naming note: the companion is the **Sage** (the user-facing character). Its BACKEND system keeps the
> legacy name **`moon`** for now (module `features/moon/`, table `moon_messages`, endpoints `/moon/*`) —
> renaming a live table + endpoints is risky churn for zero user benefit, so "Moon FAB", "moon_messages",
> "proactive Moon" below all mean the Sage. (Astronomical "Moon" — phase, Chandra house — is unrelated.)
- **Chat:** `POST /consultation/ask` with `memory_context` + chart; **RAG-grounded** (intent → classical
  books). Replies are AI (cheap, cached prefix). History kept for the session; **the conversation itself
  is ephemeral** (not stored), the Memory is fed by extraction, not transcripts.
- **Proactive:** the on-open loop asks "does the Sage have something?" = a newly-unlocked
  `/companion/patterns` item, OR a journal entry from ~1 year ago (look-back), OR today's sky matching a
  known personal pattern, OR the one thoughtful suggestion. If yes → **FAB glows with a dot**; opening
  the chat shows that opener (the pattern text is deterministic; only the back-and-forth is AI). The user
  can reply, and the reply feeds the Memory (selective extraction).

## 5. Failure & offline rules (no crashes, ever)
- Every network call is wrapped: on failure, **fall back to cache**; if no cache, show a gentle
  "couldn't reach the sky, tap to retry" and keep the rest of the screen alive. Never a white screen.
- Render's free tier cold-starts (~50s) → the client keeps a **65s timeout** and a "warming up…" state on
  first call (already in `api.ts`).
- Local-only features (cached reading, check-in line, Time Capsule display, Hora) work fully offline.
- Writes (check-in, journal, tasks) **queue and retry** if offline.

## 6. Selective memory (cost + clean data)
On journal save / chat, extraction runs **only when the text carries durable, useful signal** (people,
goals, fears, meaningful events, preferences, recurring feelings, anything that helps future predictions
or the cozy "it knows me" feel). A cheap pre-filter (length/keyword/sentiment gate) **skips the AI call
entirely** on trivia ("had chai, nice day"). Stored facts stay few and high-value, less spend, cleaner
recall. (Tune in `features/memory/service.py`.)

## 7. Build checklist (small new pieces)
**App-closed path:**
- `expo-notifications` + `expo-calendar` setup + permission flow + the Settings toggles/quiet-hours.
- The **on-open loop** (auth → daily bundle cache → reschedule notifications → proactive check →
  re-subscribe → render).
**App-open / live path (§3b):**
- A **foreground ticker** (`setInterval` ~30–60s) + an **AppState "active" listener** that recompute the
  clock marker, Hora rollover, Grahan-now, and Time-Capsule reveal from cached data.
- **Supabase Realtime:** enable Realtime on `patterns`, `coin_wallets`, and a new **`moon_messages`**
  table; subscribe in `useEffect` scoped to `user_id`, **clean up on unmount.**
- A **foreground notification handler** (`setNotificationHandler` + `addNotificationReceivedListener`) so
  notifications that fire while the app is open render as in-app banners, not system pop-ups.
**Backend — BUILT + verified 2026-06-28 (frozen engine, no AI, accuracy cross-checked from multiple sources):**
- `forecast.day_quality(profile,date)` = the ONE canonical band `good/mixed/low`; the Read reading AND the
  Panchang colour both read it → they can't contradict. `band` is now on `daily_moon_forecast`.
- `POST /dashboard/panchang` (`shared/astro/panchang.py`) = today+next-2-days strip + month grid: sunrise
  tithi/nakshatra/yoga/karana (Udaya-Tithi rule), personal band, markers Ekadashi/Purnima/Amavasya/Grahan
  (via `next_eclipse`)/Chandrashtama, best window. Eclipse↔tithi cross-check passed (solar→amavasya, lunar→purnima).
- `POST /dashboard/hora` = `current_hora()` (sunrise→sunset / sunset→sunrise **12+12 split**, weekday-lord
  first + Chaldean order Sun→Venus→Mercury→Moon→Saturn→Jupiter→Mars) + `moon_phase()` for the Read greeting.
- **Chandrashtama** = `chandrashtama` flag on the forecast (Moon in the 8th sign from the natal Moon; named
  clause; surfaced even when Tara softens the band) + Panchang marker.
- **Nakshatra activity-fit** = `constants.NAK_FIT` (the engine's 7-fold `NAK_NATURES` → chips) →
  `good_for`/`go_easy`/`nakshatra_nature` on the forecast (all 27 classify).
- **My Day** = `day_tasks` table + `features/planner/` (`/planner/tasks` CRUD); `place_task()` auto-drops a
  to-do into the best free Choghadiya window (important = a good window clear of Rahu Kaal; tasks spread),
  with `notify_at` ~15 min before for the client's local notification.
- **Time Capsule** = `time_capsules` table + `features/capsule/` (`/capsule`, `/capsule/suggest`, GET, DELETE);
  occasions custom / next birthday / next Dasha chapter (`build_vimshottari_timeline`) / next Jupiter-favours
  (`_jupiter_from_moon` houses 2,5,7,9,11); GET enforces hint(≤3d, no content) → reveal(≤0d, marks delivered).
- **Proactive Moon** = `moon_messages` table + `features/moon/` (`/moon/check`, `/moon/messages`,
  `/messages/{id}/read`); deterministic `pick_opener` lookback > pattern (reuses `memory.personalize_today`)
  > nudge; one per day per kind, only when nothing is already unread.
- **Selective memory** = `memory.service._worth_extracting()` gates `extract_and_save` (skips trivia → no AI
  call; biased to keep real facts).
- **Closed-app PUSH (how the Moon reaches out when the app is shut)** = `shared/notify/expo_push.send_push()`
  (Expo's free push API) + `PUT /me/push-token` (saves the device token → `app_users.push_token`) +
  `features/notify/` (`POST /notify/run-daily`, **cron-secret-gated**: for every user with a token it generates
  the proactive Moon opener + a capsule-arrival alert and pushes them; `POST /notify/test`, JWT, pushes to your
  own device). Known-time events (eclipse, a My Day task, a capsule's date) are NOT pushed from here — the app
  schedules those as **on-device LOCAL notifications** (no server needed when closed). While the app is OPEN, a
  freshly-inserted `moon_messages` row also streams live via Supabase Realtime → the Moon glows in real time.
- New tables (`day_tasks`, `time_capsules`, `moon_messages`) added to `supabase/schema.sql` (idempotent +
  RLS + `set_updated_at` triggers). **All 85 routes boot. Go live when the owner runs the schema + sets the Supabase keys.**

**To make notifications actually fire (owner + frontend steps, not backend):**
1. **Frontend** — the app asks for notification permission, registers its Expo token (`PUT /me/push-token`),
   and schedules the on-device LOCAL notifications for eclipse / My-Day tasks / Time-Capsule dates.
2. **Owner** — set `CRON_SECRET` on Render and point a free daily cron (Render Cron / cron-job.org / a GitHub
   Action) at `POST /notify/run-daily` with the `X-Cron-Secret` header. Push tokens need a real device build
   (Expo Go's push support is limited).
3. **Frontend** — wire real Supabase auth into `api.ts` (replace the mocked `postCheckin`).

---

## 8. What's stored where (NOT Qdrant) + the Sage's proactive-message rules

**Data flow — nothing personal ever goes to Qdrant (a common misconception):**
- **Mood check-in** → a row in `checkins` (Supabase), server-stamped with the day's sky (`astro_state_for`). No AI.
- **Journal** → a row in `journal_entries`; a background task distils durable FACTS → `memory_facts`. The Sage reads those facts.
- **Qdrant** holds ONLY the classical astrology books (the shared RAG that grounds chat/readings). Per-user memory is small and lives in Postgres, ranked by salience + recency.

**Daily check-in delivery:** a once-a-day warm **bottom-sheet on first open** (mood + energy, two taps, a pre-written line, +1 🪔). **"Ask me later"** → a slim chip on Read + one gentle evening Sage nudge. It is NOT a permanent Today card (this declutters Read and makes it a small ritual). Endpoint unchanged (`/me/checkins`).

**The Sage's proactive messages — taxonomy + caps + guardrails.** The Sage may reach out (glow+dot when open, a push when closed). Four categories, on a strict budget so it stays a companion and never a spammer:
- **Care (default, most days)** — look-back / pattern-noticed / gentle nudge / the daily check-in follow-up. Free, warm. (BUILT: `moon.pick_opener`.)
- **Guide (occasional, auto-stops)** — nudges a feature the user hasn't tried ("you haven't written in the journal yet, want to?"). Onboarding; stops once used. ≤1-2/week.
- **Timely (context, agency-framed)** — tied to today's REAL day-quality ("today runs a little low, a small evening ritual could steady it" → Rituals, free first). Never doom.
- **Discover (rare, HONEST tempt)** — one REAL line computed from the chart that opens a paid report ("a striking marriage signature in your 7th house, your Marriage reading goes deep"). Real or not sent; links to a real report (Diyas/paid). ≤1/week, never back-to-back with another commercial nudge. **Built when the Reports tab exists.**

**Hard rules (brand laws):** ≤1 proactive message/day; weekly = mostly Care, ≤1 Guide, ≤1 Discover, ≤1 Timely (commercial ≤~2/week); **NEVER fear-sell** ("your time is bad, pay to fix it" is BANNED — align27's trap, which we exist to beat); every teaser is a REAL computed truth or it isn't sent; free remedy always before a paid one; respect "not now"/mute; crisis → care + a helpline, never a sale. **Build order:** Care (done) → Guide + Timely (deterministic; need a small feature-usage signal) → Discover (with the Reports tab).
