# Myastro — Mobile App Blueprint (v3 — locked 2026-06-08)

> **Single source of truth for the app.** Self-contained — hand this to any AI coding/design
> tool. When anything changes, update this file (see §13 standing rule). Deep code map lives in
> `SYSTEM_REFERENCE.md`; backend spec in `FEATURE_SPEC.md`.
>
> **v3 is a repositioning.** v1/v2 were "calm Vedic app like CHANI." v3 keeps the real Vedic
> engine and the calm, premium *look*, but gives the app a **self-aware, witty personality** and
> a **viral shareables layer** — to win a niche the big Indian marketplace apps won't copy.

---

## 0. Read this first — the situation in plain English

- The **Python backend already works** (compute engine + most endpoints). The **Streamlit app**
  is the working prototype of the logic (reference only). The **old `mobile/` mockup is a
  throwaway** — design rejected, take nothing from it. v1 mobile is built **fresh** (React
  Native + Expo) on the existing **FastAPI** backend.
- **The app's name is NOT final.** "Myastro" is a placeholder everywhere (incl. watermarks).
- **The engine is frozen.** This whole repositioning changes *language and presentation*, never
  the astrology math. Accuracy is preserved and stays verified (§9, §12).

**Who it's for:** anyone who finds astrology *fun* and wants it to be *real* — from the
chronically-online 22-year-old to the 40-year-old who quietly checks their horoscope. Indian /
Hindu astrology users worldwide (diaspora included). Beginner → believer via **depth-mode**
(§6.10). **Not** marketed "for GenZ" (that caps the audience) — marketed by *attitude*.

---

## 1. The identity — brand laws (govern everything)

1. **Never fake anything.** Every output — even a savage joke — is computed from the real chart.
   The engine is frozen and validated (~99.9% vs Swiss Ephemeris).
2. **Authentic signification → modern expression → real fulfillment.** The meaning is ancient and
   fixed; its *expression* updates with the times (scribe → content creator); remedies are the
   real thing in a form people will actually do.
3. **Wit lives in defined places, not everywhere** (tone zones, §1.1). Sincere where trust
   matters; witty where sharing matters.
4. **No AI-slop words.** Banned: cosmic, mystic, mystical, aura, celestial, ethereal, realm,
   "journey," unlock, elevate, embark, harness, tapestry, "dive deep," filler-"sacred." Character
   comes from **real astrology terms** (nakshatra, gochar, dasha, kundli), not incense words.
5. **Sacred line.** Tease ourselves and folk-characters; **never mock worshipped gods.** Humor
   targets behavior/psychology ("don't text your ex"), never the divine.
6. **Language:** English default; **Hinglish + regional opt-in** (never defaulted — much of India
   doesn't read Hindi). Tone is *adapted* per language, not literally translated.
7. **Money:** **Subscription + Diyas wallet + tasteful affiliate remedy-commerce. No ads.** (See §7.)
8. **Visually calm & premium** (the CHANI-style look stays); the *voice* is what carries the
   personality. Beautiful, uncluttered, component-driven.

### 1.1 Tone zones
- **Witty / savage:** the Daily Roast, the Ask companion, Compatibility cards, the shareables.
- **Sincere & traditional (untouched):** kundli, palmistry, face reading, tarot, Kundli Matching,
  all premium readings, the Mirror, the Proof, the rituals/remedies, life chapters, purpose.
- **Warm but light:** daily forecast, check-in mirror, the Wrapped recaps.

---

## 2. The differentiators (the wedge)

1. **The Companion that knows you** — daily 3-tap check-in + private "Mirror" journal + Pattern
   Engine + memory-aware Ask, as *one growing thing*. The **data moat** (a competitor can't copy
   your months of history; it converts skeptics because it's *their own* data).
2. **The Proof** — back-test the user's *real past* against their dasha/transits. Instant trust.
3. **The viral shareables layer** — funny/savage/uncanny cards people *actually* post (§6.4). The
   growth engine the marketplace apps won't copy (it doesn't sell astrologer minutes).
4. **Personalized Rituals** — every mantra, remedy, fast, and Lal Kitab action derived from *your*
   kundli (§6.7). No meditation app can match chart-specific remedies. A genuine daily-use moat.
5. **Real Vedic accuracy** — the frozen, validated engine + the Proof = the trust that makes the
   wit land as "smart and real," not gimmick. Marketing line: *"astronomer-grade calculations,
   internet-grade humor."*

---

## 3. How every output is produced (the rule)

- **[AI]** — accurate, varied, combinatorial, and **all paid readings**: daily personalized
  forecast, check-in mirror, every Decode reading, the Ask companion.
- **[Curated]** — pre-written lines picked by a rule, for **savage/controlled** content: the Daily
  Roast and savage card lines. *You author every line; the engine only selects one based on the
  real transit.* Full control, zero risk of going rogue, near-zero cost on high-volume content.
- **[Templated]** — deterministic facts phrased by code: the Proof, relationship weather, timing.
- **[Math]** — the frozen `shared/astro/` engine.

**Why curated (not AI) for the savage layer:** we can't let generative AI write public roasts —
it could cross the sacred line, insult someone, break voice, or invent astrology. A curated bank
keyed to the day's *dominant transit* (a small, tractable set) gives daily freshness (lines
rotate, the dominant transit changes every ~2 days) **and** total control. This is how Co-Star
actually scaled.

---

## 4. Navigation — 5 tabs + floating Ask bubble + widget

```
┌───────────────────────────────────────────────┐
│                   (screen)                       │
├───────────────────────────────────────────────┤
│   Today    People    Decode    Rituals    You    │
└───────────────────────────────────────────────┘
        + floating "Ask" bubble (all tabs)
        + OS home/lock-screen widget
```

| Tab | Human need | Role |
|---|---|---|
| **Today** | "Guide my day" | Daily habit + the viral hook. |
| **People** | "How are my relationships?" | Relationships + the growth loop. |
| **Decode** | "Read my charts / use a tool" | All the real astrology depth (sincere). |
| **Rituals** | "Do something that helps" | Personalized remedies + practice (the daily-use moat). |
| **You** | "Understand myself + my cards" | Data moat + identity + shareables home. |

**Ask** stays a floating bubble (reachable everywhere, no tab slot). *Renames from v2: Explore →
Decode, Practice → Rituals.*

---

## 5. Tab-by-tab

Tags: `[FREE]` · `[Diyas]` costs Diyas · `[SUB]` subscription. **Made by:** `[AI]` / `[Curated]` /
`[Templated]` / `[Math]`. **Share-angle** noted where a card is shareable (so/me · funny · uncanny
· tag · flex — every shareable must name one, or it doesn't ship).

### TAB 1 — Today  *(daily habit + viral hook)*
- **Daily Forecast** `[Math/Templated] [FREE]` — your day from the **deterministic Moon forecast**
  (`/dashboard/forecast` → `daily_moon_forecast`: Chandra house from your natal Moon + Tara Bala —
  classical, verified, NO AI). Returns the **mood word + Mood / Opportunity / Caution / Action + a
  grounded "why"**, all pre-written in the warm-witty (B) voice. **The mood word is one of the
  engine's 12 (locked, source-of-truth):** Settled · Guarded · Bold · Tender · Restless · Capable ·
  Warm · Deep · Wandering · Driven · Upbeat · Quiet — each maps to a cluster image. *(The earlier
  invented "28-word set" was wrong and is dropped — images remap to these 12.)* *Share-angle: so/me.*
- **Daily Roast** `[Curated] [FREE]` — a compact savage one-liner keyed to the day's dominant
  transit; rotates, never repeats, always true to the sky; tap to share. *Share-angle: funny.*
- **Check-in + Mirror** `[AI/Math] [FREE]` — 3 taps (mood/energy) → an instant one-line "mirror"
  reflection tied to today's transit + your streak. Editable through the day. Seeds the data moat.
- **Good / Avoid times** `[Templated] [FREE]` — simplified Choghadiya/Rahu-Kaal; tap → full timing.
- **Today's Ritual** `[Templated] [FREE]` — one small real remedy the chart wants today; opens Rituals.
- **Live event card** `[Templated] [FREE]` — appears only on real eclipse / chandra-sandhi days.
- **3–4 day peek** `[FREE]` · **Wrapped announcements** (month-end + year-end, + notification).
- **Discovery teasers (≤2)** — gentle nudges into other tabs.
- **Floating Ask bubble.**

### TAB 2 — People  *(relationships + the growth engine)*
**Structure: the per-person profile is the hub; only cross-person actions sit at tab level.**
- **Tab level:** your circle (list) · add person · **Rank your circle** · pending invites.
- **Per-person profile** (sections inside the profile, not scattered buttons): the reading ·
  compatibility + share · couple view (if linked) · your private notes · privacy.

Features:
- **Your circle** `[FREE ≤3 people]` — each person shows today's one-line relationship weather.
- **Per-person reading** `[Templated/AI]` — body changes by relationship tag:
  - **Romantic** (crush/partner/spouse) → harmony read + red/green flags + 5–7 day peek; serious
    partner also gets a Kundli-Milan summary linking into the full tool in Decode. **If both are
    app users → a shared Couple view** both see (double retention).
  - **Family** (parent/sibling/child) → bond dynamics + daily nudge ("good day to call Dad"). No kootas.
  - **Social/Work** (friend/colleague/boss) → how you click + nudge.
- **Compatibility share card** `[Curated+Math]` — the red/green-flag verdict, exportable, +
  "invite them to see their side." *Share-angle: tag + savage.* (Date-score uses a vibe scale
  floored at 70 so it never offends.)
- **Rank your circle** `[AI]` — the old Compare engine surfaced as a playful leaderboard ("ranked
  by who actually gets you"); share to tag the group. *Share-angle: tag + funny.*
- **Add a person** — birth details (works solo) or friend-invite (growth).

### TAB 3 — Decode  *(the real astrology — all of it, sincere; no "fun/serious" labels)*
- **Your Kundli / chart** `[Math/Templated]` — **two tiers:** a **Basic kundli free in-app**, and
  a **Premium kundli `[Diyas]`** (detailed report + downloadable **PDF** keepsake, saved to vault,
  one-time unlock per person). **Generate kundlis for others too** (kids, matchmaking, family — a
  core Indian use-case and revenue stream; each extra person's premium kundli/PDF = Diyas).
- **Premium readings** `[AI] [Diyas/SUB]` — Full Life Reading (flagship), Marriage & Destiny,
  Your Purpose, Prashna.
- **Kundli Matching (36-guna)** `[AI+Math]` — classical tool for any two charts; People links in.
- **Palmistry** `[AI vision] [Diyas, 1 free]` · **Face reading** `[AI vision] [Diyas, 1 free]`.
- **Tarot** `[AI] [1/day free]` · **Numerology** `[AI]`.
- **Muhurta** `[Math] [FREE basic]` · **Varshaphal** (year *ahead*) `[AI+Math] [Diyas/SUB]`.
- **Cross-reference-with-kundli pricing:** features like Tarot/Numerology default to a generic
  read; a clear toggle **"Personalize with my kundli (+X 🪔)"** opts into the deeper chart-
  cross-referenced version. **Cost shown on the button, before spending.**
- *(Standalone Horoscopes dropped — daily is covered by the personal forecast, monthly/yearly by
  Wrapped. Festival/Panchanga calendar dropped.)*

### TAB 4 — Rituals  *(personalized remedies — the daily-use moat)*
**The differentiator: everything is derived from the user's actual kundli, not generic.** The
engine already computes the remedy data (`build_lal_kitab` in `kundli_text.py`, mantra/japa data
in `kundli.py`). Two clearly separated zones:

**A) Your practices (free, sincere, never monetized):**
- **Mantras** — the planetary/bija mantra for *your* afflicted planet + ishta; count + (later) audio.
- **Lal Kitab remedies** — *your* specific practical actions (feed dogs, keep water, etc.).
- **Fasting / vrat** — the weekday fast for *your* remedial planet.
- **Charity / daan** — the donation remedy for *your* affliction.
- **Meditation / breathwork** — themed to *your* need (audio — most resource-heavy, ships slightly later).
- **Multi-day practices** — guided 21/40-day remedy paths.

**B) Recommended items (optional, affiliate — the only place we sell):**
- For any **gemstone / rudraksha** the chart suggests, show the authentic Vedic budget tiers:
  **Maharatna** (primary precious stone — premium) → its **lab-certified** version (moderate, if
  available) → **Uparatna** (the genuine semi-precious substitute — most affordable). Each with an
  affiliate link, the honest *"you don't need this to do the remedy"* line, and an affiliate
  disclosure. The **free practices always come first**; the item is an optional add-on.

**Smart mechanics:** every remedy shows **"why this?"** (which chart factor it addresses) ·
**dasha/transit-aware** (remedies change over time → a reason to return) · **time-sensitive
surfacing** ("It's Saturday, do your Saturn remedy" → Today) · **organized by effort**
(daily/weekly/one-time). **Encouragement is a whisper** — a gentle streak + "you showed up," no
points/scoreboard (that would make remedies feel fake). **Earning Diyas happens here** (§7).

### TAB 5 — You  *(identity + history + shareables home)*
- **Your story** `[Templated/AI] [FREE]` — the sincere, plain-English "who you are."
- **The Receipt** `[Curated]` — your personality as a funny "universe receipt." *Share-angle:
  funny + so/me.* *(Birth Card dropped — it duplicated Your story + The Receipt with no share-trigger.)*
- **Dating Resume** `[Curated]` — you as a partner (attachment style, green/red flags, love
  language) + a playful date-score (vibe scale, floor 70). *Share-angle: self-roast + relatable.*
- **Your Year / Month, Wrapped** `[mixed]` — savage-funny recaps ("Biggest enemy: Overthinking.
  Undefeated, 12 months running."). *Share-angle: so/me + funny.* Must be sharp, never bland.
- **Life Chapters** `[Templated/Math] [FREE]` — your dasha timeline as a life story.
- **Self-knowledge zone (grouped, sincere):**
  - **The Mirror** `[AI/store]` — private, earnest journal stamped with each day's sky; reflects
    entries back over time. Never roasted, never shared.
  - **Patterns** `[Math + occasional AI]` — your real correlations ("you run low on Scorpio-Moon
    days"); progress shown while data builds. *Share-angle (when ready): relatable + funny.*
  - **The Proof** `[Templated]` — enter a past date → what the sky was doing + how it repeats.
    *Share-angle: uncanny.*
- **Saved readings (vault)** · account · **Diyas wallet** · settings (depth-mode, language).

### Always-on
- **Ask companion** `[AI]` — chart-grounded, remembers your history; absorbs Decide / yes-no /
  Prashna. `[FREE 3/day]` then `[Diyas/SUB]`.
- **Home/lock-screen widget** — daily mood word + indicator.
- **Notifications** — one restrained daily Signal + the daily-roast push + Wrapped drops.

---

## 6. Cross-cutting systems

### 6.1 Onboarding (6 screens)
welcome → **name + gender** → **birth date + place** (with a "Search by LocationIQ" credit) →
**birth time (3 levels, each consequence explained):** *I know my exact time* (→ time picker) /
*I know it roughly* (→ part-of-day) / *I don't know it* → **depth-mode** → **the reveal** (a warm
"here's who you are" wow, **before** any sign-up or paywall; activation = first reveal). Data
captured: `{ name, gender, birthDate, birthPlace(+lat/lon), birthTimePrecision, birthTime?,
depthMode }`.

### 6.2 The retention loop (the moat)
Daily check-in + Mirror entries feed **Patterns**; around day 30 it reveals *your* correlations.
**The Proof** delivers "wow" before then so users don't leave early. Cold-start shows progress
("12 of 30"). Variable-reward reveals ("Pattern unlocked: …").

### 6.3 The growth loops (how new users arrive)
Compatibility/Couple invite · Rank-your-circle tag · Wrapped (12 monthly + 1 yearly share-moments)
· Daily Roast push · the WhatsApp blessing card (warm daily forward for the family/older
demographic competitors ignore).

### 6.4 The shareables system
**Rule: nothing ships as a shareable unless it names a real share-trigger** — so/me, funny,
uncanny, tag, or flex. People don't post bland horoscope cards.

**Two share tracks (like Apple Music):**
1. **Instagram Story share** — the official "share to story" hook (background/sticker image);
   shows "shared from [App]" automatically (needs the Facebook App ID + Stories URL scheme setup).
2. **Universal share** — render the card to an image → system share sheet (WhatsApp, anywhere).

**Every card image carries a baked-in watermark** (app name + handle + short link) so attribution
survives screenshots/re-shares; universal shares also pre-fill a caption (name + line + download
link). The **first popup is our own in-app share screen** ("Share to Story / Share anywhere / Copy
link"). Mostly `[Curated/Templated]`, not AI.

### 6.5 Social scope (lean — utility + sharing, NOT a network)
Have: connect with real friends (two-way), shared Couple view, compatibility + invite, **gift a
reading/card**, rank-your-circle, optional friend's-vibe-word (opt-in). **Not in v1:** public
feed, DMs/chat, posts (moderation + scope). **Privacy:** mood logs + journal are NEVER shareable,
on any tier; you never see another user's journal/moods.

### 6.6 Two-kundli model & generating for others
Basic free in-app; Premium = Diyas (detailed + PDF, one-time per person, re-downloadable from
vault). Generating kundlis for **other people** is supported and monetized (Diyas per person).

### 6.7 Rituals personalization (detail) — see §5 Tab 4
Everything chart-derived; practices free, items affiliate (maharatna→lab→uparatna tiers);
dasha-aware; "why this?" transparency; time-sensitive surfacing; effort-grouped.

### 6.8 Notifications (Expo Push, free)
One restrained daily "Signal." Optional: eclipse/sandhi, dasha-shift, pattern-unlock, birth-time
reminder (for "add later" users), the daily-roast push, Wrapped drops. Restraint = premium.

### 6.9 Chart precision — THREE tiers (already built)
Frame: **Sidereal / Lahiri.** One chart per person at best precision the data allows.

| Tier | Input | Reliable |
|---|---|---|
| **`exact`** | time known & confirmed | Everything incl. divisionals (D9/D60) |
| **`approximate`** | time given, unconfirmed | Ascendant/houses usually OK; divisionals flagged |
| **`unknown`** | no time | Moon chart only; most of the app still works (Vedic daily = Moon-based) |

Implemented via `BirthData.time_precision` + `houses_reliable`/`divisionals_reliable`; adding
time later = one recompute (cache key includes precision).

### 6.10 Depth mode (built 2026-06-08)
At onboarding the user picks the *default* depth: **Simple / Balanced / Full**. A default, not a
lock — drill up/down anywhere. **It's a pure display setting (zero astrology/accuracy impact):** the
chart "front room" cards (and the forecast) already carry all three layers — `body` (plain English)
· `why` (the plain astrology reason) · `sanskrit` (Devanagari/technical) — so depth-mode just decides
how much shows by default: **Simple = body · Balanced = body+why · Full = body+why+sanskrit** (the
full technical kundli/dashas live in the separate `/kundli/*` surface). Stored on
`app_users.depth_mode` (check `simple|balanced|full`); read/write via **`GET/PUT /me/settings`**
(JWT). No payload regeneration — the layered data already exists.

### 6.11 Languages
English + Hindi/Hinglish first, then ta/te/mr/bn/gu (engine already supports these for PDFs).
**Opt-in, never defaulted.** Voice tone adapted per language, not literally translated.

---

## 7. Monetization — ONE currency (Diyas) + a Plus membership + affiliate, no ads

> **Locked numbers live in code: `features/wallet/prices.py` (the single source of truth).**
> The wallet is server-authoritative — the price always comes from the server, never the client;
> the atomic `apply_coin_delta` SQL function blocks minting/overdraw. Public price book at
> `GET /wallet/prices`.

**Principle: free = data accumulates + math runs + daily habit; paid = the AI/depth/artifacts.**

**Not two competing currencies — ONE (Diyas), plus a membership that improves it:**
1. **Diyas 🪔** = the currency for everything. **You light a diya by doing good** (real practice).
   **Earn (stingy, capped ~5/day):** welcome 25 · check-in 1 · ritual/meditation 2 · streaks
   10/25/60 · referral 25 (+50 if they go Plus). **Spend (server-priced):** Full Life Reading **60**,
   Premium Kundli + PDF (self/**each other person**) **60**, Marriage/Purpose/Varshaphal **40**,
   matching full report **30**, deep palm/face **25**, 7-day couple forecast **25**, Prashna **15**,
   numerology deep **15**, muhurta deep **10**, Proof extra **10**, cross-ref add-on **10**,
   extra person **10**, **AI chat 3/message**, extra tarot **5**.
2. **Plus membership** (not a second currency) — ₹49/wk · ₹199/mo · ₹999/yr, 7-day trial:
   **unlimited AI chat** (fair use) + **couple space / family grid / deep Patterns** + **cross-ref
   free** + **25% off every Diya feature**. (The permanent artifacts stay Diyas even for Plus —
   discounted — so there is no "subscribe a week, extract everything, cancel" exploit, and vision/
   flagship margin is protected.)
3. **Tasteful affiliate remedy-commerce** — gemstone/rudraksha links (Maharatna → lab → Uparatna
   tiers, §5 Tab 4). **NOT ads, NOT a marketplace.** Free remedy first; affiliate disclosed.

**Free tier by COST to us:** daily/unlimited for near-zero-cost deterministic stuff (forecast,
roast, check-in+mirror, good/avoid, ritual, basic chart, quick matching score, basic numerology,
≤3 people, all shareables incl. **Wrapped**); **1 AI chat/day**, **1 tarot/week**, **1 palm + 1
face taste**, Proof 1/month. (Costly AI = weekly/taste, never daily-free.)

**Why it holds:** Full Life is the 4-agent flagship (verified deep) repriced to 60 so it feels a
steal; Diyas vs Plus never cannibalize (different KINDS of value — consumable membership vs
permanent artifacts); chat at 3/msg pushes regulars to Plus. **~15% store cut**, AI cost pennies,
**tier-1 geo pricing 3–4×**. Living dial — tune with usage.

---

## 8. Caching (two layers, for cost)
1. **App-level result caching** (`cached_daily` / `cached_chart`) — generate shared daily content
   once; cache per-chart computes (key includes precision).
2. **API prompt/context caching** (Gemini/DeepSeek) — cache the reused prompt prefix (chart
   dossier + system prompt + RAG) so the chattiest feature (Ask) doesn't re-pay for context.

---

## 9. Technical architecture

> **Ephemeris & accuracy — locked, FROZEN (detail in `docs/ephemeris-decision.md`):** shipping
> engine is **free Skyfield + JPL (DE440s)**, **validated ~99.9% vs Swiss Ephemeris** (`pyswisseph`
> kept only as the dev validation reference, not shipped). The whole app calls the adapter seam
> `shared.astro.ephemeris` (never the engine directly); runtime is fully SE-free (0 mismatches).
> All 5 ayanamshas implemented (Lahiri default). **KP flag-gated, default OFF.** Conventions:
> Lahiri + sidereal + whole-sign houses + Vimshottari dasha + Mean node.

### 9.1 Stack
| Layer | Choice |
|---|---|
| App | **React Native + Expo (SDK 54)** — built fresh, component-driven |
| Push | **Expo Push** (free) |
| Auth + DB | **Supabase** (Postgres + Auth + RLS) |
| RAG vectors | **Qdrant** (FastEmbed/ONNX) |
| Astrology math | **Skyfield + JPL (DE440s)** behind `shared.astro.ephemeris`; SE-free, validated |
| AI — text | **Gemini / DeepSeek** (switchable, per-task ladders + circuit breaker) |
| AI — vision | **Gemini** (palm/face); DeepSeek has no vision |
| Backend | **FastAPI** (existing), Docker on Render |
| Payments | Store **IAP** for digital goods (~15% small-business cut) |

### 9.2 AI provider layer (`shared/ai/config.py`)
ONE file to change models. Per-task ladders, provider auto-detected from name prefix, circuit
breaker (instant failover on 429, auto-recovery). The mobile app inherits this automatically. New
endpoints must read the ladder for a task, never hardcode a model.

### 9.3 Cost rules
Math first, AI last · pre-bake finite interpretations as static data · generate shared daily
content once/day · cache per-chart computes · live AI only for 1:1 unpredictable input (Ask,
journal, prashna, palm/face) — paid or capped · API context caching for the companion. **The
witty/savage layer is curated, not AI — near-zero cost + full control.**

### 9.4 Payments reality
Apple/Google require IAP for in-app digital goods (can't route Diyas/subs through Razorpay
in-app). Design economics around the ~15% cut. Affiliate remedy-links (physical goods) are
external and not subject to IAP.

### 9.5 Data model (Supabase) — foundation built
`shared/db/` (Streamlit-free client) + `features/me/` (`/me/*`, JWT-gated). Tables: `app_users`,
`profiles`, `connections`, `checkins`, `patterns`, `journal_entries`, `streaks`, `subscriptions`,
`purchases`, `groups`+`group_members`, `ritual_journeys`, `rewards`, `ai_conversations`,
`cached_daily`, `cached_chart`, `usage_counters`, `coin_wallets`+`coin_transactions` (server-side
writes only), `referrals`, `gifts`, `depth_mode` column. *Owner step: create live Supabase project
+ keys.* `ad_rewards` table is vestigial (no ads) — unused, no migration needed.

### 9.6 Mapping: backend → mobile
| Backend | Mobile home |
|---|---|
| `dashboard` (forecast/week/timing/day-alerts/decide/relationship-weather/muhurta) | Today + People + Decode |
| `consultation` (`/ask`) | Ask bubble |
| `kundli` | Decode (chart/depth) + You (Life Chapters) |
| `oracle/deep_analysis` | Decode/You (Full Life Reading) |
| `oracle/matchmaking` + `marriage` | Decode (Kundli Matching) + People reading |
| `oracle/prashna` | Ask · `oracle/gochara` → engine behind Today |
| `oracle/compare` | People (Rank your circle) |
| `tarot` / `numerology` / `palmistry` / `face_reading` | Decode |
| `reflect` (purpose/year/proof) | You · `companion` (patterns/micro-insight) | You |
| `vault` | You (saved readings) + account |
| check-ins / patterns / journal / streaks / connections / coins | You + People + Rituals |

---

## 10. Build path
1. **Frontend (now):** built in Google AI Studio (React Native + Expo) from the locked design,
   screen by screen, with placeholder data behind a mock API layer (wiring-ready). Run each tab in
   Expo Go.
2. **The language pivot (§12):** reword the prompt files + build the curated line-banks. Engine frozen.
3. **Wiring:** swap the mock API for the live backend; build the remaining endpoints (§11).
4. Keep it component-driven, theme-tokened, contract-fed.

## 11. Backend gap analysis (for the v3 structure)
**Built (✅):** the engine, daily loop (forecast/checkins/micro-insight/streaks/timing/day-alerts/
week), chart suite, all premium readings, matchmaking, palm, face, tarot, numerology, muhurta,
relationship-weather, couple-week, family-grid, patterns, proof, journal, vault, year, compare,
birth-card (tarot), **Rituals remedies** (`POST /rituals/remedies` — chart-derived practices +
gemstone tiers, built 2026-06-08).
**Verified (2026-06-08):** birth-card = the tarot birth card (`/tarot/birth-card`); Varshaphala
engine exists (`compute_varshaphala`, powers `/reflect/year`) — a standalone year-ahead Decode
endpoint would be a thin wrapper if wanted.
**To build (🔨 — wiring phase, most blocked on decisions/frontend):** the witty-line system
(needs voice locked + lines written), The Receipt, Dating Resume, **Monthly** Wrapped, Compatibility
flag layer, the share-card render engine, Diyas wallet/earn/spend endpoints (need Diya prices),
affiliate-tier data for gemstones, meditation audio, a `/rituals/today` quick-ritual endpoint.
**Infra:** notifications/scheduler, payments (IAP), caching, usage limits.

## 12. The language pivot (engine frozen — only words change)
The repositioning touches the **language layer only**, never `shared/astro/*` (math).
- **AI outputs** → 8 prompt files (`features/*/prompts.py` + `shared/ai/prompts.py`). Sincere
  zones get a light "scrub AI-slop words" pass; the daily forecast gets the warm-witty voice.
- **Curated** → new line-banks + dominant-transit selector (the Daily Roast, savage card lines).
- **Hardcoded interpretation tables** (`kundli_text.py`, `chart/meanings.py`, etc.) → sincere,
  light scrub only.
- **Streamlit `view.py` copy** → ignored (the mobile app has its own copy).
- **Verify** every reading/card type against trusted Vedic sources during the pass.

## 13. Standing rule — keep docs in sync
On any change to features/structure/voice/monetization, update **this blueprint** + the short
notes in `FEATURE_SPEC.md` and `SYSTEM_REFERENCE.md` + `memory/`. This file is authoritative.
