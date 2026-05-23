# Myastro — Mobile App Blueprint (v1)

> **Single source of truth for the Myastro mobile app.** Hand this file to any AI
> coding tool (Claude Code, Codex, Gemini) or designer. It is self-contained.

---

## 0. Context for anyone (or any AI) reading this cold

**Myastro** is a Vedic-astrology + AI-divination product. A working Python
**prototype backend** already exists at the repo root:

- **`features/`** — 10 self-contained feature folders (each has `view.py` Streamlit page,
  `api.py` FastAPI route, `service.py` logic, `prompts.py`, `schemas.py`, `README.md`):
  `tarot`, `horoscopes`, `numerology`, `consultation`, `dashboard`, `kundli`,
  `palmistry`, `face_reading`, `oracle`, `vault`.
- **`shared/`** — backend reused across features: `shared/astro/` (Swiss Ephemeris,
  dasha, scoring, palm/face vision), `shared/ai/` (provider-agnostic AI layer + RAG),
  `shared/pdf/` (themes, charts, PDF builder).
- **`fastapi_main.py`** — FastAPI entry; mounts every `features/<feat>/api.py` router.
  **This is the backend the mobile app will call.**

**The mobile app** will be built in **React Native + Expo** and will talk to the
existing **FastAPI** backend. The Streamlit UI (`ui_streamlit/`) is the old prototype
front-end and is NOT ported — it's reference only.

**Audience goal:** an app for *everyone*, including people who know nothing about
astrology. Beautiful, premium, fast, addictive. NOT like cluttered Indian astrology
apps. Closer to Co-Star / The Pattern in polish, but with deeper Vedic substance
hidden underneath plain-English guidance.

---

## 1. The core differentiator (the wedge)

**"The astrology app that learns your patterns and warns you before they repeat."**

Every other astrology app gives readings about a fixed birth chart. Myastro gets
**smarter the more you use it**: a daily 3-tap mood check-in is silently correlated
with the day's planetary positions, and after ~30–90 days the app reveals *your*
personal patterns ("you crash when the Moon is in Scorpio"). This:

- builds a **data moat** (a competitor can't copy your 90 days of history),
- **converts skeptics** (it's their own logged data, not a generic horoscope),
- is **cheap to run** (mostly math, not AI).

Everything else in the app exists to support this daily loop.

---

## 2. Product principles (UX rules — NOT visual design)

> **Visual design is intentionally out of scope here.** Colors, fonts, layouts, and
> look-and-feel will be experimented separately (Google Stitch / Claude Design).
> Below are the product/UX rules that any visual design must serve.

1. **Beginner-first, jargon-free.** No Sanskrit in any primary button/label/headline.
   Plain English by default. (See the translation table in §3.)
2. **The "why?" depth toggle.** Every plain-English insight has an optional "why?"
   tap that reveals the astrology underneath. Beginners ignore it; believers love it.
3. **Fast & glanceable.** The daily experience should take 20–30 seconds. Distill the
   day to **one word + a simple vibe indicator** wherever possible.
4. **Actionable, not predictive.** Frame insights as guidance ("better for calm talk
   today") and "patterns we've noticed," never hard fate claims.

---

## 3. Jargon → plain English (UI rule)

Sanskrit becomes a *subtitle under "why?"*, never the label.

| Tradition / code term | What the user sees |
|---|---|
| Kundli / birth chart | **Your Chart** |
| Mahadasha / Dasha | **Life Chapters** ("You're in a growth chapter") |
| Nakshatra | **the Moon's mood today** (or hidden) |
| Choghadiya / Rahu Kaal / Muhurta | **Good times / Best moment to act** |
| Graha Shanti / Upaya | **Daily ritual / Things that help** |
| Prashna | **Ask the stars** |
| Dharma / Atmakaraka | **Your Purpose / What you're built for** |
| Manglik / Ashta Koota | **Compatibility** |
| Grahan | **Eclipse** |
| Gochara | *(invisible — it silently powers "Today")* |

Tarot, numerology, palm/face reading keep their names (globally understood).

---

## 4. Navigation — 4 tabs + persistent Ask + home widget

Bottom tab bar, organized by **human need**, not astrology technique:

```
┌──────────────────────────────────────────────┐
│                  (screen)                       │
├──────────────────────────────────────────────┤
│   Today      People      Explore       You      │
└──────────────────────────────────────────────┘
        + floating "Ask" button (all tabs)
        + OS home-screen / lock-screen widget
```

| Tab | Human need | Role |
|---|---|---|
| **Today** | "Guide my day" | The daily habit. Hub of daily cards. |
| **People** | "How are my relationships?" | Social engine + growth loop. |
| **Explore** | "I'm curious / try something" | Divination playground + wow features. |
| **You** | "Help me understand myself" | The data moat — chart, patterns, life story. |

**Why 4 (not 5):** concentrates energy on the three retention engines (Today,
People, You) plus one playground (Explore). Cleaner and more premium than 5 tabs;
a beginner never has to decode an esoteric tab name.

---

## 5. Tab-by-tab feature breakdown

Legend — **cost/access tags:**
`[FREE]` cheap to run, give to everyone · `[LIMITED]` free with a soft daily/weekly cap ·
`[PAID]` Myastro+ subscription or one-time unlock.
**Powered by:** `math` = Swiss Ephemeris (free) · `cache` = pre-baked/shared content (free) ·
`AI` = live model call (costs money) · `vision` = palm/face image AI (costs money).

### TAB 1 — Today  *(the daily habit; everything daily surfaces here as cards)*

| Feature | What it does (plain English) | Tag | Powered by |
|---|---|---|---|
| **Daily Forecast** ("Cosmic Weather") | One word + vibe color + mood, one opportunity, one caution, one action tip | `[FREE]` | math + cache |
| **Today's Signal** (notification) | One witty, personal morning push (do/don't), grounded in real transits | `[FREE]` | math + cache |
| **3-tap Check-in** | Log mood/energy in 3 taps; feeds the Pattern Engine; builds a streak | `[FREE]` | math |
| **Good / Avoid Times** strip | Simplified Choghadiya/Rahu-Kaal ("best time to act today"); tap → full timing | `[FREE]` | math |
| **Today's Ritual** card | One tiny doable action (entry into the Rituals hub, see §6) | `[FREE]` | cache |
| **Eclipse card** | Appears only near an eclipse: personal do's/don'ts + Sutak alerts | `[FREE]` | math + cache |
| **"This happened before" alert** | Proactive warning from the user's OWN logged history | `[PAID]` | math + light AI |

### TAB 2 — People  *(social growth loop; absorbs the old `vault`)*

| Feature | What it does | Tag | Powered by |
|---|---|---|---|
| **Add people / friend requests** | Save partner, family, friends, colleagues; invite via shareable card | `[FREE]` | — |
| **Daily relationship weather** | Per-person daily guidance ("with Dad today: practical talk, not emotional") | `[FREE]` for 1–2 people, `[PAID]` unlimited | math + cache |
| **Family grid** | Household "vibe" overview to keep peace under one roof | `[PAID]` | math |
| **Couple space** | Shared pulse + tension forecast for romantic partners | `[PAID]` | math |
| **Compatibility & Marriage Match** | Merge of backend `matchmaking` + `marriage`; one-time deep report | `[LIMITED]` quick check, `[PAID]` full | math + AI |

### TAB 3 — Explore  *(divination playground + acquisition hooks)*

| Feature | What it does | Tag | Powered by |
|---|---|---|---|
| **Palm scan** | Camera palm reading (backend `palmistry`); shareable "wow" hook | `[LIMITED]` 1 free, then `[PAID]` | vision |
| **Face reading** | Camera face reading (backend `face_reading`) | `[LIMITED]` 1 free, then `[PAID]` | vision |
| **Tarot** | 78-card interactive picker (backend `tarot`) | `[LIMITED]` 1/day free | cache + light AI |
| **Numerology** | Numerology profile (backend `numerology`) | `[FREE]` | math + cache |
| **Event timing planner** (Muhurta) | "Best dates for X" (surgery, registration, naming…) | `[PAID]` | math + AI |

### TAB 4 — You  *(the data moat; identity, patterns, life story)*

| Feature | What it does | Tag | Powered by |
|---|---|---|---|
| **Your Chart** | The birth chart (backend `kundli`); plain-English summary + "why?" depth | `[FREE]` | math · PDF export `[PAID]` |
| **Life Chapters** (Dasha timeline) | Visual life timeline; tap any period to understand it | `[FREE]` | math |
| **"Why did that happen?"** | Enter a past date → explanation + how the pattern repeats | `[PAID]` | math + AI |
| **Patterns** | The Pattern Engine payoff: your personal correlations over time | `[PAID]` | math + occasional AI |
| **Year in Review** (Cosmic Wrapped) | Monthly/yearly shareable recap (Spotify-Wrapped style) | `[FREE]` basic, `[PAID]` full | math |
| **Your Purpose** (Dharma Compass) | Soul/career blueprint; computed once, cached forever | `[PAID]` | math + AI |
| **Full Life Reading** | The flagship 3-agent deep reading (backend `oracle/deep_analysis`) | `[PAID]` | heavy AI |
| **Settings / birth details** | Profile, language, notifications, delete-my-data | `[FREE]` | — |

### Always-on

| Feature | What it does | Tag | Powered by |
|---|---|---|---|
| **"Ask" button** | The single place to ask anything. Conversational AI astrologer (backend `consultation`), reachable from any tab. A beginner just types "should I text my ex?" — it routes to the right engine. **Absorbs all other question-asking surfaces** so there's no duplication: Decision Mode / Astro-Decide ("should I take this job?" → "proceed quietly / wait 3 days / favorable window at 2pm") and Prashna/horary (in-the-moment yes/no questions, backend `oracle/prashna`). **Crown jewel; biggest AI cost.** | `[LIMITED]` 3 msgs/day free, `[PAID]` unlimited | heavy AI |
| **Home/lock-screen widget** | Daily vibe word + color + Today's Signal without opening the app. Major retention lever (Expo supports this). | `[FREE]` | cache |

---

## 6. Cross-cutting systems

### 6.1 Onboarding (the "magic" first session)
- Conversationally collect **birth date / time / place** (not a dry form).
- Immediately show a **stunning, personal "here's who you are" reveal**. The user
  must feel wowed before learning any astrology. Activation = first reveal.

### 6.2 Notifications
- **One** "Today's Signal" per morning. Witty, personal, restrained. Never spammy —
  the restraint is what feels premium.
- Optional: nakshatra-change / eclipse / inauspicious-window ("bad next 3 hours to send
  that email") / "this happened before" alerts (some free, some paid).
- Tech: **Expo Push Notifications** (free).

### 6.3 Rituals hub  *(not a tab; reached from Today's "Ritual" card)*
- **Remedy journeys** (21/40-day, gamified) — backend Graha-Shanti style guidance.
- **Streak tracker**, **virtual mala** (tap-to-count with haptics), **daily ritual**.
- All `[FREE]` and cheap (math + cached content).

### 6.4 Rewards — **reward, never gate**
- **DO:** organic unlocks (Patterns unlock because they *need* data), streak-milestone
  delight (badges, animations, a free reading at a 7-day streak), Cosmic Wrapped.
- **Variable-reward reveals (key addictive mechanic):** most days the check-in just
  updates the streak, but *unpredictably* it surfaces a dopamine hit —
  *"Pattern unlocked: you're sharpest on Moon-in-Virgo days."* Unpredictable timing
  (like a slot machine) is what makes the habit stick — but the payoff is
  self-knowledge, not manipulation.
- **DON'T:** lock useful features behind grind. No artificial "use 7 days to unlock X."
- Streak + milestone celebrations + a periodic "taste of premium" drive habit and
  conversion without feeling manipulative.

### 6.5 The Pattern Engine (build in phases)
- **Phase 1 — collect** (easy): each check-in = one DB row (date, mood, energy + the
  day's computed astro-state). A form + a save.
- **Phase 2 — find patterns** (medium, the payoff): after ~30–60 days, basic averages
  (group & compare). Plain statistics, **not ML**. Insight sentence = template fill-in.
- **Phase 3 — ML/forecasting:** intentionally skipped.
- **Framing:** "patterns we've noticed about you," never "scientific prediction."
- **Cold start:** show progress ("12 of 30 check-ins") until there's enough data; a
  wrong pattern on day 3 destroys trust.
- **Privacy:** per-user rows only (DB row-level security); provide delete-my-data.

---

## 7. Monetization (freemium, India-tuned)

**Principle:** never paywall the daily hook (cheap to run, drives habit + virality);
charge for depth and heavy AI (where the real cost is). The expensive features sit
behind the paywall, so cost scales with revenue, not signups.

**Free** — the daily loop: forecast, Today's Signal, check-in + streak, basic chart,
relationship weather for 1–2 people, 3 AI "Ask" messages/day, 1 reading/day,
1 free palm/face scan.

**Myastro+ subscription:**
- Monthly **₹199** (₹149 to be aggressive)
- Annual **₹999** (~₹83/mo) — push hard toward annual (money + retention)
- Weekly **₹49** — impulse tier (converts well in India)

**À la carte one-time unlocks** (captures non-subscribers):
- Full Life Reading **₹149–199**
- Full compatibility/marriage report **₹99–149**
- Deep palm/face report, event Muhurta **₹49–99**

Soft caps (not hard walls) bound free-user AI cost to pennies/month.

---

## 8. Technical architecture

### 8.1 Stack (all free-tier-now / open-source-self-hostable-later)

| Layer | Choice | Notes |
|---|---|---|
| App | **React Native + Expo** | cross-platform; supports widgets + push |
| Push | **Expo Push** | free |
| Auth + DB + storage | **Supabase** | free tier; open-source self-host later; already used in repo |
| User data (journals, check-ins, saved people, streaks) | Postgres rows in Supabase | tiny text; cheap |
| RAG vectors | **Qdrant** | free tier; open-source self-host later; already used |
| Astrology math | **Swiss Ephemeris** | runs in FastAPI; free; the workhorse |
| AI — text | **DeepSeek** (cheapest as of 2026) | default text model |
| AI — vision | **Gemini** (Flash-Lite) | palm/face; DeepSeek can't do these |
| Backend | **FastAPI** (existing) | host on Render/Railway free → Oracle Cloud free-forever VM at scale |

### 8.2 AI provider layer (already built — see `shared/ai/`)
- **`shared/ai/config.py`** is the ONE file to change models. Per-task model names:
  `default` / `chat` / `json` / `agent` / `vision`, plus a fallback ladder.
- **Provider auto-detected from the model-name prefix** (`gemini-*`/`gemma-*` → Gemini,
  `deepseek-*` → DeepSeek). Switch a task or adopt a new model by typing its name.
- Keys: `GEMINI_API_KEY` (+ optional `DEEPSEEK_API_KEY`) from env / `.streamlit/secrets.toml`.
- Caveat: **vision-on-DeepSeek not yet supported** (Gemini image format); falls back to Gemini.

### 8.3 Cost rules (non-negotiable for profitability)
1. **Math first, AI last.** If Swiss Ephemeris can compute it, never call AI.
2. **Pre-bake interpretations once.** 27 nakshatras, 12 houses, 9 planets, dasha themes
   are finite — write the meaning library once, store as static data. Daily forecast =
   math (which house?) + lookup (meaning). ~0 live AI.
3. **Generate shared daily content once/day** (a cron job), not per-user. Users in the
   same astro-state read the same cached line.
4. **Cache anything tied to a chart** (chart never changes): kundli interpretation,
   dharma compass, dasha timeline — compute once per user, store forever.
5. **Live AI only for 1:1 unpredictable input:** Ask chat, free-text journal analysis,
   prashna, palm/face. These are paid or soft-capped.

### 8.4 Data model sketch (Supabase / Postgres)
- `users` (id, auth, settings, language, push_token)
- `profiles` (id, user_id, name, birth_date, birth_time, birth_place, relation_tag) —
  the user AND their saved people (feeds People tab)
- `checkins` (id, user_id, date, mood, energy, clarity, astro_state_json)
- `patterns` (id, user_id, pattern_text, evidence_json, unlocked_at)
- `journal_entries` (id, user_id, date, text, astro_state_json) — optional free-text
- `streaks` (user_id, kind, count, last_date)
- `subscriptions` (user_id, plan, status, renews_at) + `purchases` (one-time unlocks)
- `cached_daily` (date, astro_state_key, content_json) — shared pre-baked daily content
- `cached_chart` (profile_id, kind, content_json) — per-chart computed-once results

### 8.5 Mapping: existing backend → mobile placement

| Backend feature | Mobile home |
|---|---|
| `dashboard` | → **Today** (daily forecast) |
| `horoscopes` | → folded into **Today** forecast |
| `consultation` | → **Ask** button (all tabs) |
| `kundli` | → **You** (Your Chart) + Life Chapters |
| `vault` | → **People** (saved charts) |
| `tarot` | → **Explore** |
| `numerology` | → **Explore** |
| `palmistry` | → **Explore** (camera) |
| `face_reading` | → **Explore** (camera) |
| `oracle/deep_analysis` | → **You** (Full Life Reading) |
| `oracle/matchmaking` + `oracle/marriage` | → **People** (Compatibility & Marriage) |
| `oracle/prashna` | → powers the **Ask** button (in-the-moment yes/no questions) |
| `oracle/gochara` | → *engine behind **Today*** (not a screen) |
| `oracle/compare` | → **cut from v1** |

---

## 9. Build roadmap (priority order for a solo dev)

1. **Foundation:** Expo app shell, 4-tab nav, Supabase auth, magic onboarding +
   first-reveal, connect to FastAPI.
2. **The hook trio:** Today (forecast + Today's Signal push + 3-tap check-in + streak).
   *This alone is a complete, addictive app.*
3. **Pattern Engine Phase 1–2** (collect → reveal patterns) in **You**.
4. **People** (add friends, daily relationship weather, shareable invite).
5. **Rituals hub** + streak rewards.
6. **Explore** (port tarot, palm, face, numerology, prashna).
7. **Depth/paid:** Full Life Reading, Dharma Compass, Life Chapters, Cosmic Wrapped,
   Muhurta planner, subscription + one-time purchases.
8. **Widget** + polish.

---

## 10. Deferred to v2 (do NOT build in v1)

- **Astro-Twins community** (social moderation + scale needed)
- **Temple / Tirtha journeys** (niche, heavy content)
- **Geofenced micro-remedies** (privacy)
- **Planetary Soundscapes** (nice-to-have)
- **Calendar sync** (permissions/trust)
- **Self-hosted AI model** (only when monthly AI bill > ~₹1 lakh; ~50k+ DAU)

---

## 11. Standing rule

Whenever a feature is added/changed/removed, update: this blueprint, `README.md`
(if structure/run/deploy changed), `FEATURE_SPEC.md` (always), and the relevant
`features/<feature>/README.md`. Docs must always reflect the live app.
