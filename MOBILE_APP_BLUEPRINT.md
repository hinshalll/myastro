# Myastro — Mobile App Blueprint (v2 — locked 2026-06-02)

> **Single source of truth for the Myastro mobile app.** Self-contained — hand this to any
> AI coding/design tool. When anything changes, update this file (see §13 standing rule).
> Deep code map lives in `SYSTEM_REFERENCE.md`; backend spec in `FEATURE_SPEC.md`.

---

## 0. Read this first — the situation in plain English

**Myastro** is a Vedic-astrology + AI product. The **Python backend already works** (the
compute engine + most endpoints). Two things are true and must not be confused:

- The **Streamlit web app** is the real, working *prototype* of the logic. Reference only.
- The **old React Native mockup** in `mobile/` is a **throwaway** — nothing works, the design
  is rejected. **We take nothing from it.** The v1 mobile app is built **fresh**.

**v1 mobile app:** React Native + Expo, talking to the existing **FastAPI** backend
(`fastapi_main.py`). Built fresh, beautiful, **minimal and calm like the CHANI app** — the
opposite of cluttered Indian astrology apps.

**Who it's for:** **Hindus and Indian-astrology users worldwide** — the global diaspora
included, not just India. It serves both the casual/curious user *and* the serious
traditional user, via a **depth-mode** choice (§6.7).

---

## 1. The core wedge — three differentiator clusters (few, real, clustered)

Everything non-essential is cut. Only three things differentiate Myastro, and they're
presented as *clusters*, not scattered features:

1. **The Companion that knows you** — a daily 3-tap check-in + a private journal ("the
   Mirror") + the Pattern Engine + a memory-aware "Ask" — presented as *one growing thing*.
   It gets smarter the more you use it. **This is the data moat:** a competitor can't copy
   your months of history, and it converts skeptics because it's *their own* data.
2. **The Proof** — back-test the user's *real past* against their dasha/transits ("don't
   trust us about your future — let us prove it on your past"). Instant trust; only our
   accuracy can do it.
3. **Social / Shareable** — compatibility with *anyone* + everything exports a beautiful
   share card. The growth engine.

---

## 2. Product principles (UX + brand rules)

1. **Minimal & beautiful like CHANI.** Calm, ranked, breathing. Rich but never cluttered.
   At most 1–2 discovery cards on any screen; conditional cards appear only when relevant.
2. **Beginner-first, jargon-free by default.** No Sanskrit in any primary label/headline.
3. **The "why?" depth toggle.** Every plain-English insight has an optional "why?" tap that
   reveals the astrology underneath. Beginners ignore it; believers love it.
4. **Homes vs doors.** Tabs are *homes* (where things live); **Today + onboarding +
   contextual moments are the doors** where deep/premium/social features get discovered — so
   nothing valuable stays buried.
5. **Actionable, not fate.** Guidance and "patterns we've noticed," never hard fate claims.
6. **Shareable by default.** Most outputs export a gorgeous story/social card (free — it's
   marketing).
7. **Honest & private.** No fear-selling, no scammy upsells. "No human ever reads your
   journal; we never sell or train on it." Privacy is part of the brand.
8. **Professional-grade & future-proof.** Component-driven UI from a shared design system,
   theme tokens, screens fed by stable API contracts — so any feature can be restyled,
   upgraded, or added later without breaking others.

---

## 3. Jargon → plain English (UI rule)

Sanskrit becomes a *subtitle under "why?"*, never the label.

| Tradition / code term | What the user sees |
|---|---|
| Kundli / birth chart | **Your Chart** |
| Mahadasha / Dasha | **Life Chapters** |
| Nakshatra | **the Moon's mood today** (or hidden) |
| Choghadiya / Rahu Kaal / Muhurta | **Good times / Best moment to act** |
| Graha Shanti / Upaya | **Practice / Things that help** |
| Prashna | **Ask** |
| Dharma / Atmakaraka | **Your Purpose** |
| Manglik / Ashta Koota | **Compatibility** |
| Grahan | **Eclipse** |
| Gochara | *(invisible — silently powers "Today")* |

Tarot, numerology, palmistry, face reading keep their names — and are treated as **first-class
astrology features, not "fun" novelties.**

---

## 4. Navigation — 5 tabs + a floating Ask bubble

```
┌───────────────────────────────────────────────┐
│                   (screen)                       │
├───────────────────────────────────────────────┤
│  Today    People    Explore    Practice    You   │
└───────────────────────────────────────────────┘
        + floating "Ask" bubble (all tabs)
        + OS home/lock-screen widget
```

**Why 5 (not 4):** 5 is the platform-supported maximum and used by Instagram/YouTube/Spotify.
4 was burying the differentiators; 5 gives each *distinct intent* room. Each tab is a genuinely
different mode: Today = "my day," People = "me + others," Explore = "read my charts / tools,"
**Practice = "do something (meditate, mala, mantra, ritual),"** You = "myself + history."
**Ask** stays a floating bubble (not a tab) so the companion is reachable everywhere without
eating a slot.

| Tab | Human need | Role |
|---|---|---|
| **Today** | "Guide my day" | The daily habit + discovery surface. |
| **People** | "How are my relationships?" | Relationships + social growth loop. |
| **Explore** | "Read my charts / try a tool" | All astrology features + depth (back room). |
| **Practice** | "Help me do something" | The CHANI soul: meditate, mala, mantra, rituals. |
| **You** | "Understand myself over time" | The data moat: Companion, journal, patterns, history. |

---

## 5. Tab-by-tab breakdown

Tags: `[FREE]` cheap/math, everyone · `[COINS]` costs coins (or included in Myastro+) ·
`[SUB]` Myastro+ only. **Powered by:** `math` (free) · `cache` (free) · `AI` (costs) ·
`vision` (palm/face AI, costs).

### TAB 1 — Today  *(daily habit + discovery surface; calm ranked stack)*
**Co-heroes (all genuinely daily):**
| Feature | Plain English | Tag | Powered by |
|---|---|---|---|
| **Daily Forecast** (the Voice hero) | One word + vibe + mood/opportunity/caution/action, in a warm, witty, screenshot-worthy tone | `[FREE]` | math + cache |
| **Good / Avoid times** | Simplified Choghadiya/Rahu-Kaal; tap → full timing | `[FREE]` | math |
| **3-tap Check-in + mirror** | Log mood/energy in 3 taps (editable through the day); instant "mirror" insight; feeds the Pattern Engine; builds a streak | `[FREE]` | math |
| **Today's Ritual** | One tiny doable action; door into the **Practice** tab | `[FREE]` | cache |

**Conditional (render only when real):** Eclipse / Chandra-Sandhi cards — `[FREE]` math.
**Below:** **3–4 day peek** rail (shortened from 7) — `[FREE]` math.
**Discovery layer (≤2 at a time, by relevance, dismissible, never the same nag twice):**
Pattern/Proof teaser → You · contextual premium prompt → Explore · ritual-journey progress →
Practice · "how today feels between you & ___" → People.

### TAB 2 — People  *(relationships + growth; solo-first)*
| Feature | Plain English | Tag | Powered by |
|---|---|---|---|
| **Your circle** (saved people) | Daily relationship weather per person | `[FREE]` ≤3 people, `[SUB]`/`[COINS]` more | math + cache |
| **Per-person view, gated by tag** | crush/partner/spouse → show compatibility; mother/friend/boss → relationship weather only (marriage kootas don't apply) | `[FREE]`/`[COINS]` | math |
| **Couple space** | Shared pulse + multi-day tension forecast | `[SUB]`/`[COINS]` | math |
| **Family grid (across timezones)** | Whole household's day at a glance — the diaspora killer | `[SUB]`/`[COINS]` | math |
| **Add a person** | By birth details (works solo) or friend request (growth) | `[FREE]` | — |
| **Friends / invite / share loop** | Connect with real users; share cards; referrals | `[FREE]` | — |

*Deferred to scale:* **Cosmic Twins** (users born within minutes of you), then later an
**anonymous twin chat**.
*Note:* the **Kundli-Matching / Ashta Koota *tool*** lives in **Explore** (it's a classical
calculator). People surfaces the relationship *reading* per person.

**Add-person paths:** *friend request* = live two-way features + a new user (growth);
*manual chart* = static, for matchmaking/family of non-users (the big Indian use case).
**Privacy tiers** on connections (acquaintance / close). **Mood logs + journal are NEVER
shareable, on any tier.**

### TAB 3 — Explore  *(all astrology features + depth; the back room)*
| Feature | Plain English | Tag | Powered by |
|---|---|---|---|
| **Your Chart (full Kundli)** | Chart, dashas, divisional charts, Ashtakavarga, Shadbala, yogas, doshas — depth shown per **depth-mode** | `[FREE]` core; `[COINS]` premium PDF | math |
| **Premium readings** | Full Life Reading (3-agent), Marriage/Destiny, Prashna | `[COINS]`/`[SUB]` | AI |
| **Kundli Matching (Ashta Koota)** | The classical compatibility tool, any two charts | `[FREE]` quick, `[COINS]` full | math + AI |
| **Varshaphal** | Your year-ahead annual chart | `[COINS]`/`[SUB]` | math + AI |
| **Event Timing Planner (Muhurta)** | "Best dates for X" | `[FREE]` basic, `[COINS]` deep | math |
| **Numerology** | Full profile + cycles | `[FREE]` | math + cache |
| **Palmistry** | Camera palm reading (first-class feature) | `[COINS]` (1 free taste) | vision |
| **Face reading** | Camera face reading (first-class feature) | `[COINS]` (1 free taste) | vision |
| **Tarot** | 78-card interactive picker | `[FREE]` 1/day, `[COINS]` more | cache + AI |
| **Horoscopes** | Daily/monthly/yearly | `[FREE]` | AI (cached) |
| **Festival / Panchanga calendar** | Localized Hindu calendar + reminders (diaspora) | `[FREE]` | math |
| *Compare (2–10 people)* | Advanced ranking tool, tucked away | `[COINS]` | math + AI |

### TAB 4 — Practice  *(the CHANI soul — calm, cheap, sticky; all `[FREE]` unless noted)*
| Feature | Plain English | Powered by |
|---|---|---|
| **Today's ritual** | The daily practice (door from Today lands here) | cache |
| **Mala / japa counter** | Tap-to-count with haptics | — |
| **Mantras** | Personalized mantras with audio | cache (audio) |
| **Guided meditation / breathwork** | Calm audio sessions | cache (audio) |
| **Ritual journeys (21/40-day)** | Gamified remedy journeys; framed as energy-tuning, never superstition | math + cache |

### TAB 5 — You  *(the data moat — the Companion's home; needs the data layer)*
| Feature | Plain English | Tag | Powered by |
|---|---|---|---|
| **Your story** (chart summary) | Plain-English "who you are" + "why?" depth | `[FREE]` | math |
| **Life Chapters** (Dasha timeline) | Visual life timeline | `[FREE]` | math |
| **The Mirror** | Private transit-aware journal; the app reflects it back over time | `[FREE]` write; `[COINS]`/`[SUB]` AI reflections | math + AI |
| **Patterns** | The Pattern Engine payoff — your personal correlations | `[FREE]` basic; `[SUB]` deep | math + occasional AI |
| **"Why did that happen?"** (the Proof) | Enter a past date → explanation + how it repeats | `[COINS]`/`[SUB]` | math + AI |
| **Year in Review** (Cosmic Wrapped) | Shareable recap | `[FREE]` basic, `[COINS]` full | math |
| **Your Purpose** | Soul/career blueprint, cached forever | `[COINS]`/`[SUB]` | math + AI |
| **History + account** | Mood/journal history, streaks, **coin wallet**, subscription, **depth-mode**, language, delete-my-data | `[FREE]` | — |

### Always-on
| Feature | Plain English | Tag | Powered by |
|---|---|---|---|
| **Ask bubble** | The chart-grounded companion that *remembers you* — Ask / quick Decide / Talk. Reads your stored history. Absorbs Decision-mode + Prashna. | `[FREE]` 3/day, then `[COINS]`/`[SUB]` | AI |
| **Home/lock-screen widget** | Daily vibe word + indicator without opening the app. Big retention lever. | `[FREE]` | cache |

---

## 6. Cross-cutting systems

### 6.1 Onboarding (the wow + the conversion moment)
- Conversationally collect **birth date / place** (not a dry form).
- **Birth time — three choices, never required** (see §6.6): "I know it" / "I'll add it later"
  / "I don't know it." App works immediately either way.
- **Depth-mode question** (§6.7), phrased gently: *"How do you like your astrology?"*
- **The Proof reveal** + a personal "here's who you are" wow *before* any paywall. Activation =
  first reveal.

### 6.2 Notifications (Expo Push, free)
One restrained daily "Signal." Optional: eclipse / Chandra-Sandhi / dasha-shift / **pattern-
unlock celebration** / birth-time reminder (only for "add later" users). Restraint = premium.

### 6.3 The Companion & the Mirror journal
- The check-in (Today), the Mirror (You), Patterns (You), and the memory-aware Ask are **one
  system**. The Ask reads stored conversations + moods + journal + tagged events, so it stops
  being a stateless bot and becomes *yours*.
- **The Mirror** stamps each entry with the day's sky, reflects entries back over time
  ("you've written this fear during each Saturn pass"), and feeds the Pattern Engine with far
  richer signal than the 3-tap mood.
- **Privacy is the promise:** owner-only (DB row-level security), encrypted, optional
  biometric lock, no human reads it, never sold or trained on. The deep AI reflection is
  opt-in.

### 6.4 The Pattern Engine (cheap — it's math, not AI)
- **Phase 1 — collect:** each check-in = one row (date, mood, energy + the day's astro-state).
- **Phase 2 — reveal:** after ~30–60 days, plain statistics (group & compare), insight as a
  template sentence. **Not ML.**
- **Day-1 micro-insight:** from the first check-in, mirror state vs today's transit so there's
  value immediately. **Cold start:** show progress ("12 of 30") for long-term patterns.
- **Variable-reward reveals:** patterns surface unpredictably ("Pattern unlocked: …") — a
  dopamine hit whose payoff is self-knowledge.

### 6.5 Rewards & coins-as-habit
- **Reward, never gate.** Organic unlocks (Patterns need data), streak milestones, Cosmic
  Wrapped. No artificial "grind to unlock."
- **Daily coins are meaningful and streak-escalating** (day 1 small → day 7 a nice chunk) so
  returning daily genuinely pays — see §7 for how this stays profitable.

### 6.6 Chart precision — THREE tiers (already built in the engine)
Single frame: **Sidereal / Lahiri.** One chart per person at the best precision the data
allows; every feature reads it, so adding time later sharpens everything at once.

| Tier | Input | Reliable |
|---|---|---|
| **`exact`** | time known & confirmed | Everything, incl. divisional charts (D9/D60) |
| **`approximate`** | time given, unconfirmed | Ascendant/houses usually OK; divisionals NOT (flagged) |
| **`unknown`** | no time | Moon chart only; most of the app still works (Vedic daily = Moon-based) |

Behaviors: **Works** (daily forecast, check-in/Pattern Engine, timing, eclipse, numerology,
tarot, relationship weather, Ashta-Koota) · **Degrades** (Life Chapters dates, Muhurta) ·
**Locked** (chart houses, Purpose, Full Reading at `unknown`; D9/D60 depth needs `exact`).
Implemented via `BirthData.time_precision` + `houses_reliable`/`divisionals_reliable`;
`unknown` uses a noon placeholder; `/kundli/compute` returns the flags; adding time → one
recompute (cache key includes precision).

### 6.7 Depth mode (new — nearly free)
At onboarding, the user picks the *default* depth: **Simple** (plain-English meanings only) or
**Full** (charts, dashas, Sanskrit, the works). Stored in `app_users.settings`. **It's a
default, not a lock** — anyone can drill up/down anywhere, and change it in settings. Backend
unchanged (payloads already return both plain + technical layers). Distinct from birth-time
tier (that's *reliability*; this is *how much to show*).

### 6.8 Languages
Ship in **all major Indian/Hindu languages** (engine already supports en/hi/ta/te/mr/bn/gu for
PDFs). Phase by language (Hindi + English first). **The "Voice" tone is adapted per language,
not literally translated** — Hinglish sass ≠ formal Tamil. Translate the meaning library
(AI-draft → human-verify).

### 6.9 Shareable cards
A shared card-renderer turns any forecast / pattern / compatibility / journal-insight / Cosmic
Wrapped into a beautiful one-tap image for stories & social. **Free — it's the growth engine.**

---

## 7. Monetization — two currencies, India-tuned, store-fee-aware

**Principle: free = the data accumulates + math runs; paid = the AI interprets it.** The
addictive inputs (check-in, journaling, basic patterns) are cheap, so they're free — which is
also what *builds the moat* (gate the inputs and the moat never forms). You charge for the AI
layer on top.

**Only two currencies:**
1. **Coins** (pay-as-you-go). Every paid report/feature is priced in coins. Get coins by:
   **buying** (direct profit), **earning** via daily/streak rewards, or **watching a rewarded
   ad** (the advertiser pays for the coins → free coins become revenue-positive). Big reports
   cost many coins (so they're still a real purchase, in your currency).
2. **Myastro+ subscription** — unlimited AI actions + the always-on companion + deep insights
   + **ad-free**. ₹49/wk · ₹199/mo · ₹999/yr. Push annual. **7-day free trial.**

**Clean rule so dual isn't confusing:** coins and subscription buy the *same* AI actions —
metered vs unlimited. A subscriber never needs coins.

**Ads (tasteful only — no-ads would lose money, intrusive ads would cheapen the app):**
- **Rewarded video** ("watch → earn coins") — opt-in, the backbone.
- **Occasional native ads** styled like content, clearly labeled, only at low-stakes moments —
  **never** during a reading/journal/sacred moment, never full-screen pop-ups.
- **Subscription removes all ads** (so ads also sell the subscription).

**Other revenue streams:** **gifting** (gift a reading/report to family — strong for diaspora),
**referrals** (invite → both earn coins), **festival-timed pushes** (relevant paid reports at
high-intent moments like Diwali — natural, not spammy).

**Profitability math (must always hold):**
- Store cut: ~**15%** under Apple/Google small-business programs (you keep ~85%); plan around
  this, never assume 30%.
- AI cost per action is pennies (cheap models + caching). So every coin price and plan is set
  so that **after the 15% store cut *and* the AI cost, we keep a healthy margin** — no item
  ever loses money.
- **Tier-1 pricing:** charge more in US/UK/etc. (per-country store pricing) — same product,
  several times the revenue from richer markets.
- **Free daily coins stay profitable** because: amounts are small, they point at *cheap*
  actions, a big share are ad-funded, and there are gentle caps (so big-ticket items still
  need a purchase).
- The coin economy is a **living dial** — set starting values, tune with real usage data.

---

## 8. Caching (two layers — both used, for cost)
1. **App-level result caching** (`cached_daily` / `cached_chart`): generate once, serve to
   everyone in the same astro-state; cache per-chart computes. Free, biggest saver.
2. **API prompt/context caching** (Gemini & DeepSeek feature): cache the large reused prompt
   prefix — the chart dossier + system prompt + RAG context — so a user's 2nd/3rd/… question
   in a session doesn't re-pay to process all that context (DeepSeek charges far less for
   cache-hit tokens). Turn on for the Ask/companion. Big saver on the chattiest, costliest
   feature.

---

## 9. Technical architecture

> **Ephemeris & accuracy — locked decision (full detail in `docs/ephemeris-decision.md`):**
> The **shipping engine is free Skyfield + JPL (DE440), built now**, re-implementing the small
> low-level layer (Lahiri/Chitrapaksha ayanamsa, Ascendant, whole-sign houses, mean node,
> sunrise/eclipses); all higher Vedic logic is existing Python on top. It's **validated to
> ~99.9% practical parity against Swiss Ephemeris** (`pyswisseph` is kept **only as the local
> validation reference** — not shipped) + spot-checked vs AstroSage, so chart parity is a
> *measured fact*. Everything sits behind an **ephemeris adapter seam** (app calls one
> interface, never the engine directly). **KP is an optional flag-gated module, default OFF**
> (Placidus only when KP on; KP code kept). Conventions: **Lahiri (Chitrapaksha) ayanamsa + sidereal +
> whole-sign houses + Vimshottari dasha + Mean node** (the classical Vedic standard — Surya
> Siddhanta / B.V. Raman; configurable). **Buying the Swiss Ephemeris license (~CHF 750) is an
> optional FUTURE upgrade if the app profits** — a one-file change thanks to the adapter.
> VedAstro rejected (slow/finicky/inconsistent).

### 9.1 Stack
| Layer | Choice |
|---|---|
| App | **React Native + Expo** (widgets + push) — built **fresh**, component-driven |
| Push | **Expo Push** (free) |
| Auth + DB | **Supabase** (Postgres + Auth + RLS) |
| RAG vectors | **Qdrant** (FastEmbed/ONNX embeddings — re-ingest done) |
| Astrology math | **Skyfield + JPL (DE440)** — free shipping engine, behind a swappable adapter; validated ~99.9% vs Swiss Ephemeris (kept only as the dev reference). See §9 note. |
| AI — text | **DeepSeek / Gemini** (switchable) |
| AI — vision | **Gemini** (palm/face) |
| Backend | **FastAPI** (existing), Docker on Render |
| Payments | Store **IAP** for in-app digital goods (see §9.4) |

### 9.2 AI provider layer (built — `shared/ai/config.py`)
ONE file to change models. Per-task names (`default/chat/json/agent/vision`) + fallback ladder;
provider auto-detected from the name prefix. **The mobile app inherits this automatically** —
it calls the backend, which picks the model; edit `config.py`, push, done (no app change).
Needs `DEEPSEEK_API_KEY` for DeepSeek; vision stays Gemini. **Rule:** new endpoints must read
`model_for(task)`, never hardcode a model.

### 9.3 Cost rules (non-negotiable)
1. Math first, AI last. 2. Pre-bake finite interpretations as static data. 3. Generate shared
daily content once/day, not per-user. 4. Cache per-chart computes (key includes precision).
5. Live AI only for 1:1 unpredictable input (Ask, journal reflection, prashna, palm/face) —
paid or capped. 6. Use API context caching for the companion.

### 9.4 Payments reality (flag early)
Apple/Google require **in-app digital goods to use their IAP** (you generally can't route
coins/subscriptions through Razorpay inside the app). Design coin/plan economics around the
IAP cut (~15% small-business). This is a real constraint, not optional.

### 9.5 Data model (Supabase) — schema exists in `supabase/schema.sql`, NOT yet created in a live DB
**Status:** the SQL is written (17 tables, RLS) but no Supabase project has run it, and there's
no Python client/wiring yet. **First build step = review/harden the schema, create the project,
run it, wire a client + auth.** Existing tables: `app_users`, `profiles`, `connections`,
`checkins`, `patterns`, `journal_entries`, `streaks`, `subscriptions`, `purchases`, `groups` +
`group_members`, `ritual_journeys`, `rewards`, `ai_conversations`, `cached_daily`,
`cached_chart`, `usage_counters`.
**Schema additions needed for this plan:** a **coin wallet + ledger** (balance + transactions:
earned/bought/spent/ad-reward), **referrals**, **gifts**, **ad-reward tracking**, and a
**depth_mode** field (in `app_users.settings`).

### 9.6 Mapping: backend → mobile
| Backend | Mobile home |
|---|---|
| `dashboard` (forecast/week/timing/day-alerts/decide-quick/relationship-weather/muhurta) | **Today** + **People** + **Explore** |
| `consultation` (`/ask`) | **Ask** bubble (memory-aware once data layer is in) |
| `kundli` | **Explore** (chart/depth) + **You** (Life Chapters) |
| `oracle/deep_analysis` | **Explore/You** (Full Life Reading) |
| `oracle/matchmaking` + `marriage` | **Explore** (Kundli Matching) + People reading |
| `oracle/prashna` | **Ask** |
| `oracle/gochara` | engine behind **Today** |
| `oracle/compare` | **Explore** (advanced, tucked) |
| `tarot` / `numerology` / `palmistry` / `face_reading` / `horoscopes` | **Explore** |
| `vault` | **People** + account |
| *(new)* check-ins / patterns / journal / streaks / connections / groups / coins | **You** + **People** + **Practice** (need data layer) |

---

## 10. The v1 build path (the route to a shipped app)
1. **Finish the backend** — above all the **data layer** (the keystone). Freeze all API
   contracts (`schemas.py`).
2. **Deeply understand** the backend + features (this is documented in `SYSTEM_REFERENCE.md`).
3. **Write Claude Design prompt(s)** for the fresh frontend, per feature, against the frozen
   contracts and this blueprint.
4. **Integrate** frontend ↔ backend beautifully.
5. **Keep it future-proof** — component-driven, theme-tokened, contract-fed, so features can
   be added/changed/restyled later without breakage.

## 11. What's left on the backend (gap analysis)
**Done:** the compute engine + read-only/AI endpoints (daily loop, kundli, oracle×6,
horoscopes, numerology, tarot, palm, face, vault, `/ask`), AI config, ONNX re-ingest.
**Not done:**
- **(A) Data layer keystone** — Supabase client + Auth + table read/write + schema additions
  (§9.5). *Unblocks everything stateful.*
- **(B) Stateful features (need A)** — Pattern Engine correlation, the Mirror journal,
  Companion memory, streaks, Practice progress, social (connections/family grid/couple
  multi-day forecast).
- **(C) Pure-compute endpoints (no A needed, can parallelize)** — the Proof back-test, Year in
  Review, Your Purpose, festival/Panchanga calendar.
- **(D) Infra/integrations** — notifications/push + scheduler, **payments (IAP) + coin/sub
  logic**, shareable card rendering, caching (app + API), usage limits.
- **(E) Compliance** — DPDP/GDPR, account deletion/export, journal privacy.

**Build order:** A first → C in parallel → B → D → E.

## 12. Deferred to v2 (do NOT build in v1)
Cosmic Twins community + anonymous twin chat (need scale + moderation) · Temple/Tirtha
journeys · geofenced remedies · planetary soundscapes · calendar sync · Birth-Time
Rectification (the `rectified_offset_minutes` hook exists) · self-hosted AI (only when the AI
bill justifies it).

## 13. Standing rule
Whenever a feature is added/changed/removed, update: **this blueprint**, `SYSTEM_REFERENCE.md`
(engine/endpoints/built-status), `README.md` (if structure/run/deploy changed),
`FEATURE_SPEC.md` (always), and the relevant `features/<feature>/README.md`. Then smoke-test
and commit. Docs must always reflect the live app.
