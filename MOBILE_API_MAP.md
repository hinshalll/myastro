# Mobile ↔ Backend Wiring Map

> The single contract for wiring the Expo app (`mobile/`) to the FastAPI backend. Each UI
> element → its endpoint → request → the response fields we use → adapter status → UX note.
> Backend is **real Vedic math** (Skyfield + classical rules); AI only where marked. Keep in
> sync as we wire (see `feedback_doc_sync`). Companion doc: `MOBILE_APP_STATUS.md`.

## How it's wired (the seam)
- `mobile/src/api/config.ts` — `API_BASE` (dev = local `http://192.168.18.21:8000`; prod =
  `https://myastroapi.onrender.com`; flip `USE_LOCAL`), timeouts, and the `Profile` type + `SEED_PROFILE`.
- `mobile/src/api/profile.ts` — the current birth profile (seeded now; onboarding calls `setProfile`).
- `mobile/src/api/client.ts` — `apiPost/apiGet`, timeout, `ApiError`, `setAuthToken` (for JWT later).
- `mobile/src/api/<feature>.ts` — adapters that map backend JSON → the exact shape the ported
  components already consume. Components take an optional `live` prop and **fall back to the
  `theme.ts` demo** when it's absent, so the screen never half-breaks (offline / cold start).

## Dev workflow
Run the backend locally (`uvicorn fastapi_main:app --host 0.0.0.0 --port 8000`) for the fast
edit loop — the web preview and a phone on the same Wi-Fi both reach it at the LAN IP. Edit
freely, see it instantly. Flip `USE_LOCAL=false` and redeploy Render at the end. **Render is
already current (84 routes).** Cold start (~50s on free tier) can time out the first call of
the day → a `/` keep-alive ping (UptimeRobot) keeps prod warm.

## Auth model
- **Stateless** (profile in body, no auth) — everything daily/chart/tools. **Wire these first.**
- **JWT** (Supabase `Authorization: Bearer`) — anything that remembers you: `/me/*`, `/planner/*`,
  `/capsule*`, `/moon/*`, `/memory/*`, `/wallet` (balance/spend/earn/history), `/companion/patterns`.
  These need sign-in, which comes with **onboarding** (next phase). Until then they stay demo.

---

## TODAY → Read  ✅ WIRED + verified live (`mobile/src/api/today.ts`, `loadTodayRead()`)
| UI element | Endpoint | Req | Response fields used | UX note |
|---|---|---|---|---|
| Whole app accent/emblem | `/dashboard/today` | `{profile}` | `reading.vibe_word` → one of the 12 mood keys | Re-tints app to today's real vibe. Mood word is now FIXED to today (cycle tap = no-op when live). |
| Reading card | `/dashboard/today` | `{profile}` | `reading.mood / why / good_for / go_easy / chandrashtama` | Chips + "why this?" all real. `opportunity/caution/action` still unused — good candidates for the expanded "why" or a share card. |
| Across-your-life rows | `/dashboard/today` | `{profile}` | `life_areas.{love,work,money}.line` | Rows live. **AreaSheet (detail) still demo** → wire `.detail/.why/.planet/.link`; the `link.tab` should drive the sheet's "go" button. |
| Living-sky header line | `/dashboard/hora` | `{lat,lon,tz}` | `hora.line`, `festival.name`, `moon_phase` | Real planetary-hour line + festival. `moon_phase` could drive the PhaseMoon art (currently fixed waxing). Location = birth place for now → use device location post-onboarding. |
| Eclipse heads-up | `/dashboard/day-alerts` | `{date,tz,lat,lon}` | `eclipse.{type,days_until,why}` | Card only shows when a real eclipse is upcoming. `chandra_sandhi` (today's low window) is **also returned and unused** — a great second heads-up card. |
| Today's ritual | `/rituals/today` | `{profile,date}` | `ritual.{action,tip,why,mantra,planet}` | Real planet-day ritual. The "+2 🪔" reward is a wallet action (JWT) — wire on ritual-complete later. |
| Check-in chip/sheet | `/me/checkins` (JWT) | `{mood,energy,clarity}` | streak | **Pending auth.** POST upserts + bumps streak; feeds the Pattern Engine. |
| Personal line under reading | `/memory/today` (JWT) | — | distilled personal line | **Pending auth.** Adds the "it remembers me" line above the chips. |

## TODAY → Plan  ✅ WIRED + verified live (`today.ts` timing/panchang on mount, `plan.ts` on-demand)
| UI element | Endpoint | Req | Response | UX note |
|---|---|---|---|---|
| SkyScene windows + strongest window | `/dashboard/timing` | `{date,lat,lon,tz}` | `choghadiya[]{name,start,end,quality,tip,period}`, `rahu_kaal`, `abhijit`, `summary` | Map HH:MM→decimal hours for the slider `DAY_CLOCK.windows`. `summary` → the strongest-window footer + the MyDay status pill. |
| MyPanchang strip | `/dashboard/panchang` | `{profile,lat,lon,tz,days:3}` | `days[]{weekday,band,label,tithi,nakshatra,best_window,markers}` | `band`→dot colour, `label`→line. |
| Month calendar | `/dashboard/panchang` | `{…,days:35,full:false}` | same, light | Full grid + day sheet. |
| AskMoment quick yes/no | `/dashboard/decide-quick` | `{profile,question?}` | `verdict/reason/why/tara` | Instant, no AI. |
| AskMoment deep | `/oracle/prashna` | `{profile,question,lat,lon,tz}` (AI+RAG) | horary verdict | Costs Diyas; the deep answer. |
| Find a good day (Muhurat) | `/dashboard/muhurta` | `{event_type,start_date,end_date,lat,lon,tz,top_n}` | top days + windows | `event_type` free-text is AI-classified server-side. |
| Check my plans (Calendar Doctor) | `/dashboard/calendar-check` | `{events[],lat,lon,tz}` | per-event verdict + better slot | Events read on-device (expo-calendar); server stores nothing. |
| Time Capsule | `/capsule` (JWT) + `/capsule/suggest` | note + delivery | — | **Pending auth.** |
| My Day tasks | `/planner/tasks` (JWT) | task text | auto-placed in best window | **Pending auth.** Auto-placement uses the same windows as `/timing`. |

## READINGS (Decode hub)  ⏳
| UI | Endpoint | AI? | Note |
|---|---|---|---|
| Kundli anchor (Lagna/Rashi/Nakshatra) | `/kundli/compute` `{profile}` | no | The chart summary the card shows. |
| Full chart | `/kundli/compute` + `/kundli/dasha-timeline` | no | Life Chapters = dasha timeline. |
| Warm chart cards | `/chart/interpret` `{profile}` | no | `{title,body,sanskrit,why}` hero cards + birth_star + current_chapter. |
| In-depth readings (Full Life / Marriage / Career) | `/oracle/deep-analysis`, `/oracle/marriage` | yes | Diyas. |
| Kundli Matching / Auspicious days | `/oracle/matchmaking`, `/dashboard/muhurta` | mix | |
| Numerology / Palmistry / Face / Tarot | `/numerology/*`, `/palmistry/*`, `/face_reading/read`, `/tarot/*` | mix | Tools grid. Palm/face need camera + upload. |

## CHAT (Sage)  ⏳
| UI | Endpoint | Note |
|---|---|---|
| Send message | `/consultation/ask` `{profile,question,history?}` | Real chart-aware AI (dossier + Event Timing Atlas + intent RAG). Returns `{intent,reading}`. **KIRAN distress guard stays client-side AND must be server-authoritative.** |
| Proactive opener | `/moon/check` (JWT) | The Sage's glow/opener when you open the app. |
| Voice reply | `/talk` `{text,profile}` | Short spoken reply (+Kokoro audio if `KOKORO_URL` set). |

## Other tabs (build + wire)
- **Timeline** = "The Path" — build LAST per `PATH_TAB_SPEC.md` (zoomable life-map from dasha timeline).
- **People** — `/people/family-grid`, `/people/couple-week`, `/dashboard/relationship-weather` (all stateless, math). Add-person → `/me/profiles` (JWT).
- **Rituals** — `/rituals/remedies` (chart-derived) + `/rituals/today`. Journeys need `ritual_journeys` (JWT).
- **You / profile** — `/me/settings`, `/me/profiles`, `/wallet/*` (JWT).
- **Wallet (Diyas)** — `/wallet/prices` (public) + balance/spend/earn/history (JWT, server-authoritative ledger).
- **Onboarding** ✅ PORTED 1:1 + verified on web (`mobile/src/onboarding/`, 7 screens). Built from the
  Claude Design export (`astrolo1.zip`); gated in `App.tsx` (`!hasRealProfile()` → onboarding). Files:
  `kit.tsx` (palette `P` + scaffold: OScreen/StepChrome/PrimaryButton/Field/PasswordField/Dropdown/SoftChip/ProviderButton),
  `Welcome.tsx`, `steps.tsx` (Name·Place·Time), `Reveal.tsx` (natal-wheel showpiece + gloss triad + proof),
  `Auth.tsx` (SignUp/Login/Done), `Onboarding.tsx` (state machine + `buildProfileFromData` → `Profile`).
  - Place search: `POST /geo/search {query}` → `{results:[{label,lat,lon,tz}]}` — **WIRED LIVE + verified**
    (`mobile/src/api/geo.ts`; debounced in `BirthPlace`). Returns IANA tz (`Asia/Kolkata`). **LocationIQ credit** on screen.
  - On "Enter", `buildProfileFromData(data)` → `setProfile()` (replaces `SEED_PROFILE`) → app loads Today on the
    real chart. Verified: captured profile (Hinshal/1998-08-14/Jaipur/09:00 exact) is a valid `/dashboard/today` payload.
  - **Still mock (next wiring pass):** the Reveal's `buildChart` is deterministic-local (Western sun sign + seeded
    moon/rising + wheel angles). To make it real needs `/chart/interpret` (reading text) + `/companion/proof` (proof line)
    **and** a backend field for the wheel's Sun/Moon/Rising ecliptic longitudes (not currently returned). Auth (Apple/Google/
    email) just advances → wire Supabase (`@supabase/supabase-js`, `EXPO_PUBLIC_SUPABASE_*`) → `setAuthToken()` → `POST /me/profiles`.
    No persistence yet (profile is in-memory; reload restarts onboarding) → add AsyncStorage/Supabase.
  - **Not yet forwarded:** the captured NAME still isn't shown in the Today header/avatar (uses `theme.ts` demo `NAME`).
  - Supabase is LIVE (project `hmspryhmyhegraqccnsh`, keys in backend `.streamlit/secrets.toml`; schema safe to re-run).

---

## Status
- ✅ **Today → Read**: reading + life-areas + hora + eclipse + ritual — live-verified on web.
- ✅ **Today → Plan**: MyDay slider (live choghadiya windows) + status pill + task auto-placement,
  My Panchang, Ask the Moment (real Tara-Bala verdict), Find-a-good-day/Muhurat (real dates) — live-verified.
- ✅ **Accuracy**: swept 4 diverse profiles (India exact, US, unknown-birth-time, UK) — all return
  valid moods (in the 12-set), real moons, populated chips, 16 choghadiya. Engine is robust.
- ✅ **Onboarding**: all 7 screens ported 1:1 + verified on web (Welcome → Name → Place → Time →
  Reveal → Sign-up → Done); live `/geo/search`; the captured profile flows into the app via `setProfile`.
- ⏳ **Still demo on Plan (by design)**: Calendar Doctor (needs expo-calendar device events + a
  `date` per event), Time Capsule + My Day task persistence (JWT), full Month grid.
- ⏭ **Next**: Readings (`/chart/interpret`, `/kundli/compute`), then Chat (`/consultation/ask`).
- 🔒 **Then auth phase**: Supabase sign-in + onboarding → unlocks check-ins, memory/personal-line,
  My Day tasks, Time Capsule, Wallet, the Sage's proactive openers, and real (non-seed) profiles.
