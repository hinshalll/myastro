# Myastro — Mobile App Blueprint (v4 — locked 2026-06-18)

> **Single source of truth for the app.** Self-contained: hand this to any AI coding/design tool.
> When anything changes, update this file (see §18 standing rule). Deep code map lives in
> `SYSTEM_REFERENCE.md`; backend spec in `FEATURE_SPEC.md`; the final-phase plan in `BUILD_PLAYBOOK.md`.
>
> **v4 is a re-spine, informed by deep market research (ChatGPT + Gemini reports on Indian astrology
> users).** v3 made "witty/savage" the identity. The research is blunt: Indians come to astrology
> anxious and want to be "treated like family," and an "unhinged" tone is a logged *complaint*. So v4
> keeps the complete Vedic app and the premium look, but the **spine becomes Trust + Timing + a
> Companion that knows you**; wit moves to the growth/share layer only. The engine stays frozen.

---

## 0. The situation in plain English
- The **Python backend already works** (frozen, validated compute engine + most endpoints). The
  **Streamlit app** is the working reference. The **old `mobile/` mockup is a throwaway**. v1 mobile
  is built fresh (React Native + Expo SDK 54) on the existing **FastAPI** backend.
- **The app name is NOT final.** "Myastro" is a placeholder.
- **The engine is frozen.** v4 changes language, structure, and positioning, never the astrology
  math. Accuracy is preserved and stays verified (§13, §16).

**Who it's for:** anyone who finds astrology useful for navigating real life (career, love, marriage,
money, timing), from the chronically-online 25-year-old to the 40-year-old quietly checking their
chart. Indian / Hindu astrology users worldwide. Beginner → believer via depth-mode (§10).

---

## 1. North Star + the three pillars
**North Star: "The honest astrologer that actually knows you."** Accurate, warm, proactive, and it
never tries to scare money out of you.

Every feature must serve one of three pillars:
1. **TRUST** — the same true chart every time, verifiable math (NASA-derived, no drift), the whole
   chart shown not hidden, no fear-mongering, no per-minute extraction, free remedies before any
   product. *(Kills the market's #1 complaint cluster.)*
2. **TIMING** — your real life on a timeline: what chapter you're in, what it's for, when the weather
   turns. Answered as **windows / periods (a month or a range), never a single fixed date, never
   vague "seasons."** *(Serves the market's #1 demand.)*
3. **COMPANION** — the Memory: a brain that remembers you forever, personalizes everything, and talks
   to you like family. *(The "context-aware AI" white space; the moat no competitor can copy.)*

---

## 1.1 Brand laws (govern everything)
1. **Never fake anything.** Every output, even a joke, is computed from the real, frozen, validated
   engine (~99.9% vs Swiss Ephemeris).
2. **Warm is the spine; wit lives only in the growth/share layer** (the shareable cards). Sincere and
   warm everywhere trust matters.
3. **The no-fear promise (stated publicly):** we never predict disaster to sell a remedy.
4. **As little jargon as possible.** Plain English everywhere; depth-mode "Full" shows technical
   terms for those who want them. (No glossary system to build, the plain-English rule replaces it.)
5. **No AI-slop words:** cosmic, mystic, aura, celestial, realm, "journey," unlock, elevate, harness,
   tapestry, "dive deep," filler-"sacred." Character comes from real terms (nakshatra, dasha, kundli).
6. **Sacred line.** Tease folk-characters and ourselves; never mock worshipped gods.
7. **Language:** English default; Hinglish + regional opt-in (never defaulted). Tone adapted, not
   literally translated.
8. **Money:** Diyas wallet + Plus membership + disclosed affiliate remedy-commerce. No ads. No human
   astrologer marketplace, no pay-per-minute, no wallet traps. *The model itself is the anti-
   exploitation story.*
9. **Visually calm & premium; the voice carries warmth.** Component-driven, uncluttered.

## 1.2 The feature-worth rule (kills bloat and buried niches)
Every feature must earn one of three roles, or it is cut:
- **(A) Marketed pillar feature** — can headline a screenshot, pulls installs or daily opens.
- **(B) Contextual nicety** — lives *inside* a bigger feature, appears only when relevant, never a
  standalone menu item (e.g. baby-name syllables inside "kundli for a child").
- **(C) Invisible plumbing** — quality woven into everything, never "a feature" (e.g. notifications
  that explain).

**Cut by this rule (v4):** dream log, Past-Life card, the Receipt card, Rank-your-circle card, the
in-app glossary, the "save chat answer" feature (the Memory auto-remembers instead).

---

## 2. Tone zones
- **Warm + sincere (the spine, almost everywhere):** kundli, all readings, Timeline, the Mirror, the
  Proof, rituals, the companion, daily forecast, check-in.
- **Witty (growth/share layer only):** the shareable cards (Compatibility, Nakshatra Type, Dating
  Resume, the Wrapped recaps).

---

## 3. Navigation — 5 tabs + the Readings hub + the companion

```
┌───────────────────────────────────────────────┐
│  top cluster: photo · Diya chip · Readings icon  │
│                   (screen)                       │
├───────────────────────────────────────────────┤
│   Today   Timeline   People   Rituals   You      │
└───────────────────────────────────────────────┘
        + floating Moon companion (all tabs)
        + OS home/lock-screen widget
```

| Tab | Human question | Pillar |
|---|---|---|
| **Today** | "Guide my day" | Companion + daily Timing |
| **Timeline** | "What's happening in my life, and when?" | **Timing (the hero)** |
| **People** | "How are my relationships?" | Relationships + growth |
| **Rituals** | "Do something that helps" | Trust (non-exploitation) + daily habit |
| **You** | "Who am I, my memory, my stuff" | Companion data moat + identity |

**Decode is not a bottom tab.** The readings + tools become a **"Readings & Tools" hub**, reached
from a persistent top-bar icon (so it never hides) *and* surfaced contextually (the Marriage reading
appears when you add a partner, the Full Life Reading is promoted on Timeline). Tabs go to daily
surfaces; occasional deep readings live in the hub. The **Moon companion** floats on every screen.

---

## 4. Tab-by-tab

Tags: `[FREE]` · `[Diyas]` · `[SUB]`. Made by: `[AI]`/`[Curated]`/`[Templated]`/`[Math]`.
Role: `(A)` marketed · `(B)` contextual · `(C)` plumbing.

### TAB 1 — Today *(the daily companion)* — LOCKED, no structural change
The Moon greets you, warmed by the Memory ("Scorpio Moon today, you usually run low, go gentle").
- **Daily forecast** `(A) [Math/Templated] [FREE]` — Moon-based mood word + Mood/Opportunity/Caution/
  Action + a grounded "why," from `daily_moon_forecast` (Chandra house from natal Moon + Tara Bala;
  the 12 mood words: Settled·Guarded·Bold·Tender·Restless·Capable·Warm·Deep·Wandering·Driven·Upbeat·
  Quiet). No AI.
- **2-tap check-in** `(A) [Math] [FREE]` — mood + energy → one warm reflection + streak. Seeds the Memory.
- **The Mirror** `(A) [AI/store] [FREE]` — write or speak a journal entry; the Memory reads, stores,
  reflects one line back (comfort / growth / "you've been here before"). Pure journaling (no dream
  logging). Crisis entry → care + helpline safety net. A soft "talk about it? →" opens the companion.
- **Today's windows** `(B) [Templated] [FREE]` — good/avoid times (Choghadiya/Rahu-Kaal); tap → full timing.
- **Today's ritual** `(A) [Templated] [FREE]` — one chart-derived remedy the day wants; opens Rituals.
- **Live event card** `(B) [Templated] [FREE]` — only on real eclipse/sandhi days.
- The Daily Roast `[Curated]` one-liner stays as an optional light share, growth-layer voice.

### TAB 2 — Timeline *(the hero: your life across time)*
**"Your past, proven. Your future, prepared."** All from the frozen Vedic engine (verified mapping
in §15). Framing rule: chapters, themes, and **windows/periods**, never a fixed date.
- **Where you are now** `(A) [Templated]` — current Mahadasha + Antardasha as a theme + what it's for
  + when it shifts. *(`_vimshottari_timeline`, `get_antardasha_table`.)*
- **The life roadmap** `(A) [Math]` — your whole life as a scrollable sequence of chapters, past and
  future. *(`build_lifetime_dasha_sequence`.)*
- **The Proof, embedded** `(A) [Templated] [FREE]` — scroll into a *past* chapter, check it against
  what actually happened. Your own life is the evidence that converts skeptics. *(`/companion/proof`.)*
- **Sade Sati tracker** `(A) [Math/Templated]` — which phase (rising/peak/setting), what it's for,
  when it eases. Calm, never the doom others sell. *(`sade_sati_timeline`, `_sade_sati_phase`.)*
- **The big questions** `(A) [AI/Math]` — entry chips literally **Career · Love · Marriage · Money**
  (the four reasons people open the app), answered as windows + preparation, deep-linking into the
  relevant reading. *(`build_event_timing_atlas`, `calculate_career_score`, `/oracle/marriage`
  `timing_windows`.)*
- **Major weather windows** `(B) [Templated]` — Saturn/Jupiter returns, Rahu/Ketu transits as seasons.
- **Check any date** `(B) [Templated]` — point at a future/past date for the energy to bring to it
  (preparation, never a good/bad verdict).
- **Dasha-change alert** `(C)` — a gentle notification when a real new chapter begins.

### TAB 3 — People *(relationships + growth)*
- **Your circle** `(A) [FREE ≤3]` — each person shows today's one-line relationship weather.
- **Per-person reading** `(A) [Templated/AI]` — adapts by tag: romantic (harmony + red/green flags +
  5–7 day peek; serious partner → Kundli-Milan summary into the hub; both app users → shared Couple
  view `[SUB]`), family (bond + daily nudge "good day to call Dad"), social/work (how you click).
- **Household / family view** `(A) [SUB]` — everyone's charts in one place + joint planning ("a good
  day for the whole family"). *(`/people/family-grid`.)*
- **Kundli Matching (36-guna)** `(A) [AI+Math] [Diyas/SUB]` — for any two charts; ask the companion
  about a match in plain words. *(`/oracle/matchmaking`.)*
- **Decode Anyone** `(A)` — read any person's chart (ex/crush/celeb), warm and honest, optional share.
- **Compatibility share card** `(A) [Curated+Math]` — red/green-flag verdict, exportable, + "invite
  them to see their side." *The one shareable with a built-in growth loop.* Date-vibe scale floored
  so it never offends.
- **Add a person** — birth details or friend-invite. *Baby-name syllables `(B)` appear only when you
  add a child.*

### TAB 4 — Rituals *(the "agency" pillar — chart-derived remedies, never expensive pujas)*
Everything derived from the user's actual kundli. Two zones:
**A) Your practices (free, sincere, never monetized):**
- Mantras (bija/planetary for *your* afflicted planet + ishta; count + later audio).
- Lal Kitab remedies (*your* specific practical actions).
- Fasting/vrat + Charity/daan (for *your* remedial planet).
- Meditation/breathwork themed to *your* need (audio ships slightly later).
- **Guided journeys** `(A)` — 21/40-day sankalpa with a soft streak (encouragement as a whisper, no
  scoreboard). *(`ritual_journeys` table.)*
- **"Did it help" tracking** `(A)` — the documented white space: tie a journey to check-in data and
  show a gentle before/after ("your low-energy days dropped over these 40 days"). Only possible
  because of the Memory.
- **Short how-to tutorials** `(C)` for each remedy.
- **Dasha/transit-aware** — remedies change over time (a reason to return); time-sensitive surfacing
  ("It's Saturday, do your Saturn remedy" → Today).

**B) Recommended items (optional, affiliate — the only place we sell):**
- Gemstone/rudraksha tiers: **Maharatna** (precious) → **lab-certified** → **Uparatna** (affordable
  genuine substitute). Each with an affiliate link, the honest "you don't need this to do the remedy"
  line, and a disclosure. **Free practice always first.** *(Earning Diyas happens here, §11.)*

### TAB 5 — You *(identity + the Memory + account)*
- **Your story** `(A) [Templated/AI] [FREE]` — the sincere, plain-English "who you are" (the
  "translate astrology into how I actually am" angle).
- **The Memory home** `(A) [AI/store]` — the Mirror archive + **Patterns** (your real correlations,
  progress while data builds) + **growth tracking** + the **look-back** ("a year ago today you wrote
  X, look how far you've come") + the quiet **monthly recap**.
- **Shareables home** `(A) [Curated]` — **Nakshatra Type** (27-type Vedic identity), **Dating Resume**
  (you as a partner), **Monthly + Yearly Wrapped** (share-ready, never nagged). *The wit lives here.*
- **Vault + privacy controls** `(A/C)` — saved readings + PDFs; **export and delete your data**
  (fixes the "no way to delete my birth data" trust complaint).
- **Diyas wallet · settings** (depth-mode, language).

### The Readings & Tools hub *(the old Decode — Trust on display)*
Reached from the top-bar icon + surfaced contextually.
- **Your kundli** `(A) [Math/Templated]` — Basic free in-app; Premium `[Diyas]` (detailed + PDF
  keepsake to vault, one-time per person); generate for others (kids/family/matchmaking, each premium
  = Diyas). **The Trust badge lives here:** "NASA-derived data, no drift, the same true chart every
  time," and we **show the whole chart** (every degree and varga, never hidden to upsell). **PDF
  export** fixes the "can't download my chart" complaint.
- **Premium readings** `(A) [AI] [Diyas/SUB]` — Full Life Reading (4-agent flagship), Marriage &
  Destiny, Your Purpose, Prashna.
- **Auspicious Days planner** `(A) [Math]` — muhurat as a utility ("good days to buy/travel/start"),
  optional **calendar sync** `(B)`.
- **Tools** `(B) [Diyas, free taste]` — numerology, palmistry, face reading, tarot, varshaphal.
  Metered. Depth and share fuel, not the identity.
- **Pro view** `(B/C)` — inside depth-mode "Full": visual divisional charts (D9/D10), planetary
  strength, retrograde/combust/exalted flags, ayanamsa toggle. Invisible to casuals; a Trust signal
  to believers; near-zero cost (engine already computes it).

### Always-on: the Moon companion (the Ask)
- The conversational door to the Memory + chart + classical-text RAG. Chart-grounded, warm, never
  savage. **Identity: "your astrologer who actually knows you."**
- Absorbs Prashna (moment-question) and quick yes/no Decide as *kinds* of questions it answers.
- **Chat is ephemeral (not stored).** The companion remembers via the Memory it auto-extracts (§7).
- Can **hand off** to structured features ("want the full Marriage reading? →").
- `[FREE a few/day]` then `[Diyas 3/msg or SUB]`.

---

## 5. THE MEMORY (the Companion brain) — headline system
One chart-grounded brain: journal + check-ins + natal chart + **dasha** + transits + the people in
your life. Predictions weigh **dasha first, then natal, then transits** (in Vedic astrology the dasha
is the bigger life-driver).

**How it remembers (auto-remember, no "save" button):**
1. **Extract, don't store transcripts.** On journal save, and at the end of a chat (or every few
   turns), a cheap LLM call distills durable facts (people, events, goals, fears, dates) into short
   notes. A long chat about quitting a job becomes one note: `considering job change, ~June 2026`.
2. **Dedupe / merge** against existing facts (don't duplicate; supersede if changed).
3. **Store** — text in `memory_facts` (Supabase, tiny). **No vector DB:** a single user's facts are
   few, so they're loaded and ranked directly (salience + recency). Qdrant stays for the shared book
   RAG only; pgvector is an option later only if journal topic-search is ever wanted.
4. **Recall** — load the user's top facts + recent signals (`GET /memory/context`) and inject them
   into the chat (`memory_context` on `/consultation/ask`) and the personalized forecast.
**Privacy/trust:** the user can view, edit, and delete any remembered fact. Chat conversations are
NOT persisted. Cost is one cheap extraction call per conversation; stored facts are bytes.

**"It knows me" surfaces proactively (no chat needed):** the personalized daily forecast, occasional
"Pattern unlocked" cards + a gentle notification, the Patterns screen, Mirror reflections, the
look-back, Wrapped, and the relational memory ("you said things were tense with Rahul, his chart
eases this week").

---

## 6. Onboarding (5 screens)
welcome ("Meet yourself, exactly as you are.") → **name + gender** → **birth date + place**
(`POST /geo/search`) → **birth time** (3 levels, each consequence explained: exact unlocks rising
sign/houses; a rough "when" sharpens the Moon only; unknown → Moon-chart mode) → **the reveal**
(image by gender → `/chart/interpret`). The reveal leads with **timing + trust** ("here's who you are
and what chapter you're in"), then immediately offers **the Proof** ("pick a date that mattered")
so the wow lands before any sign-up or payment. Continue = sign-up → `POST /me/profiles` +
`PUT /me/settings`. Depth-mode is a Settings toggle (default `simple`), not an onboarding step.

---

## 7. The Trust system (the marketed differentiator)
- **Accuracy badge:** "NASA-derived (JPL) data, no iOS/Android drift, the same true chart every time."
  This is the #1 trust gap in the market and we genuinely win it (single backend, validated engine).
- **Full-chart transparency:** show every degree and division, never hidden to upsell.
- **The no-fear promise**, stated in-app.
- **Privacy/data controls:** export + delete (You tab).
- **Pro view** for serious users (depth-mode Full).

---

## 8. Cross-cutting systems
### 8.1 The retention loop
Daily check-in + Mirror feed Patterns; around day 30 your correlations are revealed. The Proof + the
Timeline deliver "wow" before then. The Memory deepens with use, so the app gets *more* valuable the
longer you stay (the opposite of novelty-app decay).

### 8.2 The growth loops
Compatibility/Couple invite, the Wrapped recaps (12 monthly share-ready + 1 yearly event, never
nagged → free promotion), the Daily Roast share, friend invites, gift a reading/card.

### 8.3 Shareables (culled to a lean, strong set)
Rule: nothing ships unless it names a real trigger (so/me, funny, uncanny, tag, flex). **Keep:**
Compatibility (People, growth loop), Nakshatra Type + Dating Resume + Monthly + Yearly Wrapped (You).
**Cut:** Receipt, Rank-circle, Past-Life. Two share tracks: Instagram Story (needs a Facebook App ID)
and universal share-sheet; every card carries a baked-in watermark; mostly `[Curated/Templated]`.

### 8.4 Depth mode (built)
Default Simple / Balanced / Full, a display setting only (zero accuracy impact): Simple = body ·
Balanced = body+why · Full = body+why+sanskrit + the Pro view. Stored on `app_users.depth_mode`,
read/write via `GET/PUT /me/settings`.

### 8.5 Chart precision — three tiers (built)
`exact` (everything incl. divisionals) · `approximate` (ascendant/houses usually OK; divisionals
flagged) · `unknown` (Moon chart; most of the app still works, Vedic daily = Moon-based). Adding a
time later = one recompute (cache key includes precision).

### 8.6 Notifications (Expo Push, free) — restraint is premium
One restrained daily "Signal," **that explains** ("Saturn shifts into your 10th this week, a push on
work"). Optional: eclipse/sandhi, dasha-shift, pattern-unlock, Wrapped drops, birth-time reminder.
Never pushy (the opposite of every incumbent).

### 8.7 Languages
English + Hindi/Hinglish first, then ta/te/mr/bn/gu. Opt-in, never defaulted.

### 8.8 Cost reality (storage is nearly free)
A heavy daily user over 10 years stores ~15–25 MB (text + vectors), a fraction of a cent/month. The
cost is **AI inference, not storage** (already metered via Diyas/Plus; embeddings run on free local
ONNX). So "remembers you forever" is essentially free to keep.

---

## 9. Monetization — ONE currency (Diyas) + Plus membership + affiliate, no ads
> **Locked numbers live in `features/wallet/prices.py` (single source of truth).** Server-authoritative;
> the atomic `apply_coin_delta` SQL function (service_role only) blocks minting/overdraw. Public
> price book at `GET /wallet/prices`.

**Principle: free = data accumulates + math runs + daily habit; paid = the AI/depth/artifacts.**
1. **Diyas 🪔** — earned by doing good (capped ~5/day): welcome 25 · check-in 1 · ritual/meditation 2
   · streaks 10/25/60 · referral 25 (+50 if they go Plus). Spend (server-priced): Full Life Reading
   **60**, Premium Kundli+PDF (self/each person) **60**, Marriage/Purpose/Varshaphal **40**, matching
   full **30**, deep palm/face **25**, 7-day couple forecast **25**, Prashna **15**, numerology deep
   **15**, muhurta deep **10**, Proof extra **10**, cross-ref add-on **10**, extra person **10**, AI
   chat **3/message**, extra tarot **5**.
2. **Plus** — ₹49/wk · ₹199/mo · ₹999/yr, 7-day trial: unlimited chat (fair use) + couple space /
   family view / deep Patterns + cross-ref free + **25% off every Diya feature** (artifacts stay
   Diyas even for Plus, discounted → no subscribe-extract-cancel exploit).
3. **Affiliate remedy-commerce** — gemstone/rudraksha tiers (Maharatna → lab → Uparatna). Free remedy
   first; disclosed. NOT ads, NOT a marketplace.
- **Bundles:** glow ₹99→110 · blaze ₹299→380 · festival ₹799→1150.
- **Free tier by cost-to-us:** daily/unlimited deterministic (forecast, check-in+mirror, good/avoid,
  ritual, basic chart, quick matching score, basic numerology, ≤3 people, all shareables incl.
  Wrapped); **1 chat/day, 1 tarot/week, 1 palm + 1 face taste, Proof 1/month.**
- **~15% store cut**, AI cost pennies, **tier-1 geo pricing 3–4×**. Living dial.

---

## 10. AI models (the brain) — `shared/ai/config.py` is the ONE swap point
Per-task ladders + circuit breaker (instant failover on quota, auto-recovery); provider auto-detected
from name prefix; never hardcode a model. **Strategy: free Gemini/Gemma tiers first, cheapest paid net
last.**

| Task | Ladder (primary → net) |
|---|---|
| chat / agent / json (intelligence) | `gemini-3.1-flash-lite` → `deepseek-v4-flash` |
| default readings (tarot/numerology/horoscope/gochara) | `gemma-4-31b-it` → `deepseek-v4-flash` |
| micro (high-volume tiles/blurbs) | `gemma-4-26b-a4b-it` → `gemma-4-31b-it` → `deepseek-v4-flash` |
| vision (palm/face) | `gemini-3.1-flash-lite` → `gemini-2.5-flash` → `gemma-4-31b-it` |

**Pricing (June 2026, verified):** Gemini 3.1 Flash Lite $0.25/$1.50 per M in/out; DeepSeek V4 Flash
$0.14/$0.28 (cached input $0.0028, 98% off). **Notes:** (a) DeepSeek V4 Flash is the cheapest paid
text model (esp. output), so the "DeepSeek paid net" is well chosen; revisit DeepSeek-as-primary at
large scale. (b) **Vision must stay Gemini** (DeepSeek can't see images); re-verify if V4 added vision.
(c) **Exploit DeepSeek's 98%-off prefix cache for chat** (the chart dossier is resent each message).
(d) Consider a stronger model only for the **paid Full Life Reading** (synthesis quality is the
product). (e) **Accuracy is bounded by design:** the engine computes the astrology; the model only
phrases verified chart data + RAG from classical texts, so the bar is instruction-following + low
hallucination, kept safe by strict "use only the provided chart data" prompts. (f) `deepseek-chat`/
`deepseek-reasoner` aliases deprecate 2026-07-24; we already use `deepseek-v4-flash`.

---

## 11. Technical architecture
> **Ephemeris — FROZEN (`docs/ephemeris-decision.md`):** free **Skyfield + JPL (DE440s)**, validated
> ~99.9% vs Swiss Ephemeris (`pyswisseph` kept only as dev reference, not shipped). The whole app
> calls the seam `shared.astro.ephemeris` (never the engine directly); runtime fully SE-free. Lahiri
> sidereal + whole-sign houses + Vimshottari dasha + Mean node. KP flag-gated, default OFF.

| Layer | Choice |
|---|---|
| App | React Native + Expo (SDK 54), component-driven |
| Push | Expo Push (free) |
| Auth + DB | Supabase (Postgres + Auth + RLS) |
| Book RAG vectors | Qdrant (shared classical texts only) |
| Per-user Memory | Supabase rows (`memory_facts`) — no vector DB |
| Astrology math | Skyfield + JPL (DE440s) behind `shared.astro.ephemeris`; SE-free, validated |
| AI text | Gemini / Gemma / DeepSeek (swappable, per-task ladders + breaker) |
| AI vision | Gemini (palm/face); DeepSeek has no vision |
| Backend | FastAPI, Docker on Render |
| Payments | Store IAP (~15% small-business cut) |

**Cost rules:** math first, AI last; pre-bake finite interpretations; generate shared daily content
once/day; cache per-chart computes (key includes precision); live AI only for 1:1 unpredictable input
(chat, journal, prashna, palm/face), paid or capped; the witty layer is curated, not AI.

---

## 12. Data model (Supabase) — foundation built
`shared/db/` (Streamlit-free client) + `features/me/` (JWT-gated). Tables: `app_users`, `profiles`,
`connections`, `checkins`, `patterns`, `journal_entries`, **`memory_facts` (NEW v4 — the auto-
remembered distilled facts; text only, no vector DB)**, `streaks`, `subscriptions`, `purchases`,
`groups`+`group_members`, `ritual_journeys`, `rewards`, `cached_daily`, `cached_chart`,
`usage_counters`, `coin_wallets`+`coin_transactions` (server-write only), `referrals`, `gifts`,
`depth_mode` column. `ai_conversations` is now **optional/vestigial** (chat is ephemeral). `ad_rewards`
is vestigial (no ads). *Owner step: create live Supabase project + keys; run `supabase/schema.sql`
(idempotent).*

---

## 13. Backend — built vs partial vs to-build (for v4)
**Built + validated (✅):** the engine (positions/dashas/sade-sati/divisionals/matching/manglik/
transits), daily loop (forecast/checkins/micro-insight/streaks/timing/day-alerts/week), chart suite,
all premium readings (deep-analysis 4-agent / marriage / purpose / prashna / compare), matchmaking,
palm, face, tarot, numerology, muhurta, relationship-weather, couple-week, family-grid, patterns,
**proof**, journal store, vault, year, **rituals remedies**, **wallet** (prices/balance/spend/earn/
history + `apply_coin_delta`), **settings**, **geo search**.

**Built but needs surfacing/endpoints (🔧):** Sade Sati tracker (`sade_sati_timeline` → endpoint),
the Timeline big-question flows (`build_event_timing_atlas`, `calculate_career_score`, marriage
`timing_windows` → clean endpoints + window framing), Auspicious Days planner (muhurta → planner +
calendar export).

**Verify + complete (🔎):** the full dosha set beyond Manglik (kaal sarp, pitra, etc.).

**THE MEMORY engine — BUILT 2026-06-18 (✅):** `features/memory/` (AI extract-on-save + chat
extraction + dedupe/merge + recall context + **deterministic forecast personalization**);
`/memory/facts|extract|context|today`; server-side sky-stamping of check-ins/journal; background
fact-extraction on journal save; chat memory-injection (`memory_context`). No Qdrant. *Remaining
Memory work = frontend wiring (see `features/memory/README.md` contract) + live test. Optional later:
a richer AI daily personalization; pgvector journal topic-search.*

**VOICE — "talk to the Moon" — BUILT but DEFERRED to post-launch (2026-06-22):** `features/talk/`
(POST `/talk`: a SHORT, warm, RAG-grounded spoken reply; translate-first so Hindi questions still hit
the English books; `en` + `hi` Devanagari modes) + `voice/kokoro_service.py` (self-hosted Kokoro TTS,
CPU-only, free). Pipeline: on-device STT (free) → `/talk` → Kokoro TTS (free). **Deferred** because it
can't be flawless at v1 cost: multi-hop ~3 to 6s/turn latency, Kokoro's Hindi voice is unverified, and
we ruled out a paid TTS fallback (free-Kokoro-or-nothing). It's a delight layer, not the spine. The
code is dormant + harmless (no UI; returns text-only without `KOKORO_URL`); flip it on post-launch when
on-device Kokoro makes it truly free + flawless. **Related facts now locked:** the RAG embedder is
English-only (`bge-base-en-v1.5`), so Hindi book-search needs translate-first (or swap to `bge-m3`);
the Memory extractor now stores facts in ENGLISH regardless of input language; DeepSeek V4 Flash rates
"strong" at Hindi (Gemini is stronger and stays primary).

**To build new (🔨):** the curated Daily Roast line-bank + share-card render engine, remedy "did it
help" tracking, monthly Wrapped, child-naming syllables
(contextual), wallet spend-wiring + usage counters, payments (IAP), notifications/scheduler, caching.

---

## 14. Astrology accuracy audit (the standing verification task)
Two layers: **(1) astronomical** (positions, dasha dates, transits) is already at the industry gold
standard, validated ~99.9% vs Swiss Ephemeris (the de-facto reference, derived from NASA JPL). **(2)
the rule/interpretation layer** (Vimshottari sequence + proportions, Sade Sati phases, 36-guna
Ashtakoota, Manglik/doshas, divisional construction, yogas, remedies) is classical (mainly Brihat
Parashara Hora Shastra) and **must be source-audited feature by feature** against multiple
authoritative sources, into a written verification doc. **Priority order:** Vimshottari → Sade Sati →
36-guna → Manglik/doshas → divisionals → yogas → remedies. Do this *before* wiring features.

---

## 15. Build path
1. **Astrology source-audit** (§14) first — accuracy is the brand.
2. **Frontend** — design (Claude Design) → AI Studio (RN+Expo) → wire. Perfect one hero screen, then
   "apply this style to screen X." Mock API layer first (wiring-ready). See `BUILD_PLAYBOOK.md`.
3. **Remaining backend** (§13) — the Memory first (the moat).
4. **Wiring** — swap mock API for live backend per screen; polish animations.
5. **Test/diagnose** in Expo Go; then launch (VPS, store, compliance).

## 16. What changed from v3 → v4
1. **Spine swapped:** savage → trustworthy/warm; wit demoted to the share layer only.
2. **Three pillars** named (Trust, Timing, Companion); every feature now serves one.
3. **Timeline promoted to a tab** (the Timing hero): dasha roadmap + Sade Sati + the four big
   questions + the Proof + check-any-date.
4. **Rituals keeps its tab** (the agency pillar, + "did it help" tracking); **Decode becomes a hub**
   (top-bar + contextual), since deep readings are occasional.
5. **Accuracy surfaced** as a marketed Trust badge (NASA data, no drift, full-chart transparency,
   privacy controls).
6. **Timing framing:** windows/periods (a month or range), never a fixed date, never vague "seasons."
7. **The Memory auto-remembers** (AI extract → `memory_facts`, no vector DB; **built 2026-06-18**);
   **chat is ephemeral; "save chat answer" removed.**
8. **Shareables culled** to 4 (Compatibility, Nakshatra Type, Dating Resume, Monthly+Yearly Wrapped).
9. **Cut by the feature-worth rule:** dream log, Past-Life, Receipt, Rank-circle, glossary.
10. **Models documented** with verified June-2026 pricing + strategy; accuracy bounded by engine+RAG.
11. New standing task: the **astrology source-audit** (§14).

## 17. Feature-worth + voice quick-reference
Build (A) marketed / (B) contextual / (C) plumbing, or cut. Warm spine; wit only in shareables. Never
fake; never fear-sell; as little jargon as possible; windows not dates; accuracy verified from
multiple trusted sources.

## 18. Standing rule — keep docs in sync
On any change to features/structure/voice/monetization/models, update **this blueprint** + short notes
in `FEATURE_SPEC.md` and `SYSTEM_REFERENCE.md` + `BUILD_PLAYBOOK.md` + `memory/`. This file is
authoritative.
