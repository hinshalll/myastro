# Myastro — Build Playbook (the "what's left + how" for the final phase)

> **Read this + `MOBILE_APP_BLUEPRINT.md` (esp. §14) + `memory/project_myastro.md` to resume.**
> This is the durable roadmap for the hardest phase: finish frontend, finish remaining backend,
> wire them, test, ship. Written 2026-06-12 so work continues seamlessly after a compaction.
>
> **UPDATED 2026-06-18 for blueprint v4** (Trust + Timing + Companion spine; warm voice, wit in the
> share layer). Nav is now **5 tabs: Today · Timeline · People · Rituals · You** + a top-bar
> **Readings & Tools hub** (the old Decode) + the floating **Sage companion**. See
> `MOBILE_APP_BLUEPRINT.md` v4 for the authoritative structure. Key v4 deltas baked in below.

---

## 0. WHERE WE ARE (one paragraph)
Backend ~80% built + pushed (engine, daily loop, rituals, forecast, wallet, settings, geo, all
readings, matching, vision, patterns, proof, year, journal-store). Frontend being built in
**Google Stitch/Claude Design (design) → Google AI Studio (RN+Expo SDK54 code) → me (wire + polish)**;
**Stitch is being dropped in favor of Claude Design** for a premium/CRED-tier animated look. Today
screen designed; user mid-onboarding. **Supabase is NOT live yet** (the #1 blocker). The `mobile/`
folder has uncommitted frontend work — commit it.

## 1. PHASE ORDER (do in this sequence)
0. **Owner unblocks** (only the user can): Supabase live + keys, Render env keys.
0.5 **Astrology source-audit FIRST** (blueprint §14): verify the rule layer (Vimshottari → Sade Sati
   → 36-guna → Manglik/doshas → divisionals → yogas → remedies) against multiple authoritative
   sources into a written doc. Accuracy is the brand; do this before wiring features.
1. **Frontend** — design each screen (Claude Design) → AI Studio builds RN, screen by screen,
   **wiring-ready** (mock api). Perfect ONE hero screen, then "apply this style to screen X".
2. **Remaining backend** (me) — The Memory, personalized forecast, Daily Roast lines + share-card
   engine, 3 shareables, monthly Wrapped, wallet spend-wiring + usage counters, IAP, notifications.
3. **Wiring** (me) — swap mock api → real backend per screen; polish RN animations to the bar.
4. **Test/diagnose** — run in Expo Go, click every screen, fix.
5. **Launch** — VPS/hosting, store submission, compliance.

## 2. OWNER MANUAL STEPS (only you can do these)
- **Supabase (the keystone):** create the live project → in SQL Editor, paste + run
  `supabase/schema.sql` (idempotent — safe to re-run, do NOT delete tables) → copy 3 keys:
  `SUPABASE_URL`, `SUPABASE_ANON_KEY` (goes in the mobile app, safe), `SUPABASE_SERVICE_ROLE_KEY`
  (backend/Render ONLY, never in the app). Then everything stateful (wallet, settings, checkins,
  journal, streaks, patterns) goes live.
- **Render env vars:** `LOCATIONIQ_API_KEY` (place search), `DEEPSEEK_API_KEY` (AI failover), the 3
  Supabase keys.
- **Commit the `mobile/` folder** when there's frontend work to save.
- **Assets:** the 12 mood images (`assets/today/<word>.png`: settled/guarded/bold/tender/restless/
  capable/warm/deep/wandering/driven/upbeat/quiet), the 3 reveal images by gender, the ritual image.
- **Later/launch:** Apple+Google IAP setup, Expo push credentials, a Facebook App ID (for the
  Instagram-story share), affiliate sign-ups (gemstones), a 4GB/2-core **x86** VPS (NOT ARM —
  MediaPipe has no ARM wheels), a privacy policy + store compliance (data-deletion etc.).

## 3. FRONTEND BUILD (the plan)
> **⭐ FRONTEND RESTARTED (2026-06-25).** The finalized, backend-accurate, **tool-agnostic** design
> prompts (the full Today screen + Sage chat + Diyas wallet, and the whole onboarding flow + Login)
> now live verbatim in **`FRONTEND_PROMPTS.md`** (repo root). Design in **Claude Design OR Google
> Stitch** (the prompts work in both) → port with **Google Antigravity 2 (use Gemini 3.1 Pro)** → I
> wire the backend + we test in Expo Go. (The earlier Claude Design Today build was rejected; AI
> Studio errored; z.ai was poor.) **Recover compacted detail:** the full chat transcripts are at
> `C:\Users\hinsh\.claude\projects\C--Users-hinsh-Desktop-myastro\*.jsonl` — python-scan them
> (json.loads each line, pull `message.content[].text`, grep a keyword) to print any exact past prompt.
- **Tool chain:** Claude Design (premium look, hero screens) → screenshot → AI Studio (RN+Expo
  SDK54 code) → me (wire + animation polish). **Design language = premium dark-cosmic, CRED-tier,
  animated** (was leaning clean-white, pivoted — see chat; user perfecting in Claude Design).
- **The rule that saves tokens:** perfect ONE hero screen, then for every other screen pass it as
  reference: "apply this exact style to screen X." Never "all screens in one prompt" (quality tanks).
- **Wiring-ready architecture (tell AI Studio):** `theme/` tokens (light+dark), reusable primitives
  (Card/Button/etc.), screens in `app/` (Expo Router), **ALL data behind a single mock api module
  `src/api/`** with a TS type per shape, base URL in one `src/config.ts`, screens presentational.
  Plain StyleSheet, no Tailwind. So wiring later = swap mocks for real fetches in one folder.
- **Prompt convention:** **Stitch/Claude Design prompt = the LOOK; AI Studio prompt = LEAN
  data/endpoints/logic only** (it imports the design, don't re-describe layout). **ALWAYS verify the
  endpoint exists before writing "the app calls X."**

### Screen inventory (v4 — what still needs design + build)
- **Onboarding (5):** welcome · name+gender · birth date+place (`/geo/search`) · birth time (3
  opts; exact unlocks houses, rough sharpens Moon only) · reveal → leads with timing+trust, then the
  **Proof** wow.
- **Global elements (every screen):** top cluster (avatar + Diya chip + **Readings & Tools icon**),
  Sage companion FAB (chat, ephemeral + auto-remember).
- **Today** — LOCKED, no structural change (forecast, check-in 2-tap, **Mirror**, good/avoid, ritual,
  event, nav).
- **Timeline (NEW hero tab)** — current chapter (Mahadasha+Antardasha) · life roadmap · **Sade Sati
  tracker** · the four big questions (Career/Love/Marriage/Money) · **Proof** · check-any-date ·
  major weather windows. Framing = windows/periods, never fixed dates.
- **People** — circle · per-person 3-mode reading · **household/family view** · Kundli Matching ·
  **Decode Anyone** · Compatibility share · add-person (baby-name syllables contextual).
- **Rituals (keeps its tab)** — practices (free, chart-derived) · **guided journeys** · **"did it
  help" tracking** · tutorials · items/gemstone-tiers (affiliate).
- **You** — story · **Memory home** (Mirror archive + Patterns + growth/look-back + monthly recap) ·
  **shareables** (Nakshatra Type · Dating Resume · Monthly + Yearly Wrapped) · vault + **privacy
  export/delete** · **Diyas wallet** · settings (depth-mode, language).
- **Readings & Tools hub (old Decode, top-bar + contextual):** kundli (basic/premium PDF) + **Trust
  badge** + full-chart transparency · readings (Full Life/Marriage/Purpose/Prashna) · **Auspicious
  Days planner** (+calendar sync) · tools (numerology/palm/face/tarot/varshaphal) · **Pro view**.
- **Overlays/screens:** Chat (the Sage) · Diyas wallet · paywall/Plus · Diya top-up · share-card sheet.
- **CUT (don't build):** dream log, Past-Life, Receipt, Rank-circle, glossary, save-chat-answer.
- **DEFERRED to post-launch (built, dormant):** the voice "talk to the Sage" feature (`features/talk/`
  + `voice/kokoro_service.py`). On-device STT (free) → `/talk` (RAG-grounded, translate-first for
  Hindi) → free Kokoro TTS (`en`+`hi`). Shelved for v1: can't be flawless at the cost (multi-hop
  latency, unverified Kokoro Hindi voice, free-Kokoro-only). Code is harmless/dormant; flip on later.
  Note: RAG embedder is English-only (`bge-base-en-v1.5`); the Memory extractor now stores facts in English.

## 4. BACKEND — BUILT vs LEFT
**BUILT (verified, pushed; don't redo):** the frozen engine (charts/dashas/divisionals/remedies/
matching/vision, validated 99.9% vs Swiss Eph); daily loop (`/dashboard/forecast` 12-mood
deterministic B-voice, `/me/checkins`, `/companion/micro-insight`, `/me/streaks`, `/dashboard/
timing|week|day-alerts`); `/rituals/remedies` + `/rituals/today`; the **Diya wallet** (`/wallet/
prices|balance|spend|earn|history` + atomic `apply_coin_delta` SQL fn locked to service_role); 
`/me/settings` (depth simple/balanced/full); `/geo/search` (place autocomplete); all readings
(`/oracle/*` Full Life 4-agent / marriage / purpose / prashna / compare, `/kundli/*`, numerology,
palm, face, tarot, horoscopes); `/companion/patterns`; `/companion/proof`; `/reflect/year`;
`/me/journal` (store + sky-stamp); `/consultation/ask`.

**LEFT TO BUILD (me, mostly after Supabase live):** *(v4 note: the Memory ENGINE is BUILT 2026-06-18 —
`features/memory/` extracts durable facts from journal + chat into `memory_facts` (NO Qdrant; facts
loaded+ranked directly), recall via `GET /memory/context`, chat takes optional `memory_context`;
journal save auto-extracts in a background task; check-ins/journal are sky-stamped server-side.
Remaining: surface Sade Sati + the four big-question flows on Timeline, remedy "did it help" tracking,
calendar sync on Auspicious Days, personalize the forecast with the Memory, and frontend-wire it.)*
1. **THE MEMORY (headline):** AI interpret-on-save (one cheap model call per journal entry → themes/
   emotion/recurring concerns, stored) · **embed per-user entries in Qdrant** (you already have
   Qdrant for books) · **semantic recall** over a user's journal · "you've been here before"
   recurrence (match similar astro-state) · growth detection (theme fading) · crisis safety-net
   (distress → care + helpline) · transit-based journal prompts · feed it into forecast/Patterns/Ask.
   **Predictions weigh dasha first, then natal, then transits — not just sky.** Chat convos are
   EPHEMERAL (not stored). Mirror = write/voice → ONE warm reflection, "talk about it?" → Ask.
2. **Personalized daily forecast:** blend the user's check-in/journal history into `/dashboard/
   forecast` ("Scorpio Moon — you usually run low"). + "Pattern unlocked" reveal cards + notification.
3. **Daily Roast (curated, NOT AI):** a hand-written line-bank keyed to the day's dominant transit +
   a selector. Plus the **share-card render engine** (IG-story via FB App ID + universal image;
   watermark on the image).
4. **3 shareables (reuse engine data + content):** **Nakshatra Type** (27-type, → You), **Past-Life**
   (Ketu/karma read, → Decode), **Decode Anyone** (roast any chart, reuse compat, → People).
5. **Monthly Wrapped** (extend `/reflect/year` to a month).
6. **Wallet integration:** wire spend-checks into each paid endpoint (debit before generating) +
   **free-allowance usage counters** (1 chat/day, 1 tarot/week, 1 palm + 1 face taste, ≤3 people,
   Proof 1/month) using the `usage_counters` table.
7. **Onboarding persistence + auth:** Supabase sign-up at the reveal's "Continue" → THEN
   `POST /me/profiles` (self profile) + `PUT /me/settings`. A login screen for "I have an account".
8. **Affiliate** gemstone link data (maharatna/lab/uparatna tiers) on the Rituals items.
9. **Infra:** IAP receipt verification + sub status; Expo push notifications + scheduler; app +
   API caching; rate-limiting.

## 5. WIRING (frontend ↔ backend)
- Swap the mock `src/api/` functions for real `fetch`/axios to the backend (Render URL).
- **Auth:** Supabase JWT; send `Authorization: Bearer <jwt>` on `/me/*` and `/wallet/*`. The
  backend verifies via Supabase + RLS scopes the user. Sign-up happens at onboarding reveal.
- **The `profile` object:** most compute endpoints take a `profile` dict — get the self profile from
  `GET /me/profiles` (relation_tag:'self') and pass it to forecast/ritual/week/timing/ask/etc.
- **Today screen data map (example):** profile → `/dashboard/forecast`, `/rituals/today`,
  `/dashboard/timing` (date,lat,lon,tz), `/dashboard/week` (days:4), `/dashboard/day-alerts`,
  check-in → `/me/checkins` + `/companion/micro-insight` + `/me/streaks/checkin`, Mirror →
  `/me/journal`, Ask → `/consultation/ask`, Diya chip → `/wallet/*`.
- Polish RN animations to the CRED bar (web→RN motion via Reanimated/Moti — budget for this).

## 6. TEST / DIAGNOSE
- Run backend locally (`uvicorn fastapi_main:app`) or use Render. Run the app in **Expo Go** on the
  phone over Wi-Fi (point `src/config.ts` at the local IP or Render URL).
- Click through every screen; watch console + network; fix per screen.
- Verify the daily loop (forecast → check-in → mirror → ritual), the wallet (earn/spend), the
  journal save, and one paid reading end-to-end once Supabase is live.

## 7. HARD RULES (never break)
- **Engine frozen:** never touch `shared/astro/*` math (validated). Only language/presentation.
- **Never fake any output** — every reading/score/card is from the real chart. Accuracy is #1.
- **Verify against trusted Vedic sources**, not memory, for any astrology claim.
- **Secrets:** env-first then `.streamlit/secrets.toml`; `service_role` key server-only; never
  hardcode; `shared/*` must never import streamlit.
- **Voice/brand:** self-aware + witty in defined zones (Daily Roast, Ask, Compatibility, shareables);
  SINCERE everywhere else (kundli, readings, the Mirror); no AI-slop words; tease folk-characters not
  worshipped gods; English default + Hinglish opt-in; no em dashes in user copy.
- **Money:** Diyas + Plus + affiliate, no ads.
- **Falsifiability rule ("a mirror, not a slot machine"):** assume astrology may be placebo/psychology.
  Build REFLECTIVE features (mirror/interpret/prompt — value from the psychology, can never be "wrong");
  AVOID FALSIFIABLE ones (dated verdicts, yes/no oracles, self-scored hit-rates, seal-and-verify loops —
  when they miss, users blame the APP, not astrology, and they break the placebo). Test every feature:
  *if astrology is fake, does this still help the person?* No → cut. Also: NO feature sprawl — fold ideas
  into existing structure (Mirror/Memory, timing, People/Decode), don't add screens we can't place.
- **Commit trailer:** `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`. User pushes main →
  Render auto-deploys.

## 8. THINGS EASILY MISSED (my notes to self)
- The `mobile/` folder is the frontend; commit it when there's work to save.
- The Streamlit app (`ui_streamlit/`) is the working reference — don't break it.
- The chat companion = **the Moon** (Chandra), NOT a flame (flame = the Diya currency, would clash).
- Depth-mode lives in **Settings**, not onboarding (default simple + per-card "why?" tap).
- Check-in = **2 taps** (mood + energy); the journal is the deep signal.
- The "share card" needs a **Facebook App ID** for the Instagram-story path.
- Couple space / family grid / deep Patterns = **Plus** (subscription), not one-day Diya unlocks.
- Vision (palm/face) is the costly bit — keep it metered (1 free taste, then Diyas), not unlimited.
- The Full Life Reading is the **4-agent flagship** (verified deep) priced at **60 Diyas**.
