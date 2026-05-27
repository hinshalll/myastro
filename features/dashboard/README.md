# Dashboard — "Cosmic Compass"

Daily landing page. All widgets are toggleable from the ⚙️ popover.

## Widgets

| Toggle | What it shows |
|---|---|
| `greeting`    | Personalized 2-sentence transit insight (AI) |
| `consult`     | Quick-link card to the Consultation Room |
| `forecast`    | 4-tile grid: Energy / Focus / Caution / Best Time |
| `decide`      | Astro-Decide widget: ask a yes/no, Tara Bala verdict + AI explainer |
| `calendar`    | 7-day Tara Bala "cosmic week" cards |
| `tarot`       | Daily Tarot card (deterministic from name+date) + interpretation |
| `dasha_alert` | Major dasha shift warning if next AD ≤ 45 days or PD ≤ 14 days |

## What's in this folder

| File | What it holds |
|---|---|
| `prompts.py` | `build_data_prompt` (greeting + tiles) + `build_decide_prompt` |
| `service.py` | `fetch_data` and `fetch_daily_tarot` (AI orchestration) |
| `schemas.py` | Pydantic models |
| `view.py`    | Streamlit page (toggle-driven render) |
| `api.py`     | FastAPI router |

## `/dashboard/day-alerts` — two "Today" heads-up cards (no AI)

`POST /dashboard/day-alerts` returns two optional heads-up cards. Pure Swiss-Ephemeris
math, Moon/Sun based — **no birth time, no AI, no profile**.

- **Input:** `{ "date": "YYYY-MM-DD", "tz": "<IANA tz>" }` (optional `lat`/`lon` for
  future eclipse-Sutak refinement).
- **Output:** `{ chandra_sandhi: {...}, eclipse: {...} }` — each carries its own `present`
  flag so the app shows/hides the card.
  - **`chandra_sandhi`** (blueprint §6.6 — Moon at a sign junction = weak/reflective):
    scans the transiting Moon across the local day; when it's within ~1° of a 30° sign
    boundary it returns `{present, start, end (HH:MM), from_sign, to_sign, label:"Low
    window", note, why, sanskrit:"चन्द्र सन्धि"}`, else `{present:false}`. (The Moon crosses
    at most one boundary per day → at most one window.)
  - **`eclipse`**: soonest upcoming solar OR lunar eclipse on/after the date (global
    search). `{present, type:"Surya Grahan"|"Chandra Grahan", date, days_until,
    sutak_start, sutak_note, why, sanskrit}`. `present` is True only within the next 30
    days. Sutak (caution period) is approximated at ~12h before solar / ~9h before lunar.

Logic lives in `shared/astro/astro_calc.py` (`chandra_sandhi_window`, `next_eclipse`).
NOTE: this is **upcoming-calendar** eclipses — unrelated to `kundli._detect_grahan`
(a natal eclipse-axis dosha).

## `/dashboard/forecast` — daily "Cosmic Weather" hero (no AI)

`POST /dashboard/forecast` powers the mobile Today tab's hero card. **FREE + cheap by
design** (cost rule): pure math + a pre-baked meaning **lookup**, **no AI call**. It's
**Moon-based**, so it works at every birth-time tier (unknown time → noon placeholder).

- **Input:** same `{ "profile": {...} }` as `/kundli/compute`, plus optional `"date"`
  (`"YYYY-MM-DD"`, defaults to today in the profile's tz).
- **How it works:** computes the transiting Moon today (at **local noon** → deterministic
  & cacheable), its nakshatra/sign, its house **from the natal Moon** (Chandra house 1..12),
  and **Tara Bala** quality (favourable/neutral/challenging) via `calculate_tara_bala`.
  That state is mapped through a static table (`_CHANDRA_HOUSE`, 12 entries × Tara quality)
  in `shared/astro/forecast.py`.
- **Output (display-ready):** `vibe_word` (one word), `vibe_score` (0..1 for the ring),
  `mood`, `opportunity`, `caution`, `action`, `why` (plain-English astrology), `sanskrit`
  (e.g. `चन्द्रः हस्त-नक्षत्रे`), and `astro_state_key` (identical states share it →
  cacheable). Plus debug fields: `moon_nakshatra`, `moon_sign`, `chandra_house`, `tara`,
  `tara_quality`.
- **Framing (blueprint §2):** actionable + reflective, never hard fate claims. Sanskrit
  appears only inside `why` / `sanskrit`.

Pure math + lookup, no AI, no new dependencies, no streamlit. The meaning table is plain
data — easy to expand later (e.g. add a per-nakshatra layer).

## `/dashboard/relationship-weather` — daily per-person "relationship weather" (no AI)

`POST /dashboard/relationship-weather` powers the People tab's daily guidance for how
today feels between the user and ONE saved person. **FREE + cheap by design** (cost rule):
pure math + a pre-baked meaning **lookup**, **no AI call, no new dependencies**. It's
**Moon-based**, so it works even when **either person's birth time is unknown** (unknown
time → noon placeholder for that person's natal Moon).

- **Input:** `{ "profile_a": {...}, "profile_b": {...}, "date": "YYYY-MM-DD" (optional) }`.
  Both profiles use the `/kundli/compute` shape; `profile_a` = the user, `profile_b` = the
  saved person. `date` defaults to today in `profile_a`'s tz.
- **Two classical layers (sourced — see commit + module docstring):**
  1. **Baseline ("how these two mesh"):** the RELATIONSHIP-NEUTRAL kootas only — **Graha
     Maitri** (minds/temperaments, /5) + **Gana** (temperament, /6) from
     `shared/astro/scoring.py::calculate_ashta_koota` — blended 50/50 with the **Rashi
     (Moon-sign) relationship** flavour (same sign = mirrored; 4-10 = respect/practical;
     5-9 Nava-Pancham = warm; 6-8 Shad-Ashtaka = friction; etc.). The full 36-guna Ashta
     Koota *total* is deliberately NOT used here — it's a MARRIAGE-matching tool (Yoni/Nadi
     = sexual compatibility/progeny; its Bhakoot factor penalises the warm 5-9 pairing).
     Full Ashta Koota lives in the dedicated Compatibility & Marriage feature.
  2. **Daily ("how today feels"):** the **Tara Bala** of today's transiting Moon read from
     **each** person's natal Moon (favourable / neutral / challenging), combined into one
     day-tone. Kept deliberately modest and framed as gentle guidance — there is no single
     classical "daily formula for a pair", so it does not overclaim.
- **Output (display-ready):** `tone_word`, `summary`, `good_for`, `avoid`, `score` (0..1,
  today weighted 0.6 / durable baseline 0.4), `why` (plain-English astrology), `sanskrit`
  (e.g. `ग्रह-मैत्री · गण · तारा बल · चन्द्रः …-नक्षत्रे`). Plus `astro_state_key` (cacheable) and
  debug fields: `maitri`, `gana`, `baseline_score`, `rashi_relation`, `moon_sign_distance`,
  `moon_nakshatra`, `moon_sign`, `tara_a`/`tara_b` (+ their qualities), `day_state`.
- **Framing (blueprint §2):** warm, jargon-free, gentle guidance — never fate. Sanskrit
  appears only inside `why` / `sanskrit`. Deterministic for the same two profiles + date.

Logic lives in `shared/astro/relationship_weather.py` (reuses `forecast.py`'s Moon helpers
+ only the Graha Maitri + Gana kootas from `scoring.py`, not the full 36-guna marriage
total). Pure math + lookup, no AI, no new dependencies, no streamlit.

## `/dashboard/timing` — Good / Avoid times strip (no AI)

`POST /dashboard/timing` powers the mobile "Today → Good / Avoid times" strip. It is
**date- and location-based** (weekday + sunrise/sunset), NOT birth-chart based, so it
needs no profile.

- **Input:** `{ "date": "YYYY-MM-DD", "lat": <float>, "lon": <float>, "tz": "<IANA tz>" }`
- **Output (display-ready):**
  - `avoid` — Rahu Kaal, Yamaganda, Gulika Kaal — each `{name, start, end}` (24h `HH:MM`).
  - `good` — Abhijit Muhurta — `{name, start, end}`.
  - `choghadiya` — the 8 daytime + 8 nighttime segments tiling sunrise→next sunrise,
    each `{name, start, end, quality, period}` where `quality ∈ good|neutral|avoid`
    (Amrit/Shubh/Labh = good, Char = neutral, Udveg/Kaal/Rog = avoid).
  - `summary` — one-line plain-English hint (e.g. "Strong window 11:50 am–12:45 pm…").
  - plus `weekday`, `sunrise`, `sunset`.

Pure math, no AI, no new dependencies. All logic lives in `shared/astro/astro_calc.py`
(`daily_timing_windows`, `sun_rise_set` via Swiss Ephemeris + classical weekday segment
rules). Day windows split sunrise→sunset into 8 equal parts; the kaal periods pick the
weekday's segment; Choghadiya walks the 7-fold wheel from the weekday's starting period.

## `/dashboard/muhurta` — Event Timing Planner ("best dates & times to do X") (no AI)

`POST /dashboard/muhurta` powers the Explore tab's Muhurta planner — best dates+times for
an event (travel, signing a deal, naming, buying a vehicle, housewarming, general…) over a
date range. **FREE + cheap by design** (cost rule): pure math + a pre-baked **classical
Muhurta lookup**, **no AI call, no new dependencies**. **Date- and location-based**
(panchanga + sunrise/sunset), so **no birth chart is needed**.

- **Input:** `{ "event_type": "travel|signing|naming|vehicle|housewarming|general",
  "start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD", "lat", "lon", "tz", "top_n"? }`.
  Unknown `event_type` falls back to `general`.
- **How it works:** for each day in the range it reads the panchanga **at local sunrise**
  (the day's ruling limbs — classical din-shuddhi) — tithi, nakshatra, yoga, karana,
  weekday — and scores it against **sourced** classical rules for that event:
  - **Nakshatra** is the core gate — each event has its own favourable-star set (verified
    across multiple panchang references; see `_EVENT_RULES` source notes).
  - **Tithi:** penalise Rikta (4/9/14) and Amavasya; reward the broadly auspicious tithis.
  - **Weekday:** per-event good / avoid days.
  - **Yoga:** heavily avoid Vyatipata & Vaidhriti (milder caution for other harsh yogas);
    small bonus for auspicious ones.
  - **Karana:** penalise Vishti (Bhadra).
  Then it picks the best clear daytime window — **Abhijit Muhurta** first, else the first
  "good" Choghadiya (Amrit/Shubh/Labh) — that **steps clear of Rahu Kaal / Yamaganda /
  Gulika Kaal** (reuses `daily_timing_windows`).
- **Output:** `{ event_type, event_label, range, found, message, recommendations: [ {
  date, start, end, score (0..1), reason, why, sanskrit, + debug: nakshatra, tithi,
  weekday, yoga, karana, window, window_clear } ] }`. A day must carry a favourable star
  **and** clear a minimum score to be recommended; if nothing in the range qualifies,
  `found:false` and `message` says so plainly (no forced weak pick).
- **Framing (blueprint §2):** warm, jargon-free, gentle guidance — never fate. Sanskrit
  appears only inside `why` / `sanskrit`. Deterministic for the same inputs.

Logic lives in `shared/astro/muhurta.py` (`plan_muhurta(...)` + the static `_EVENT_RULES`
table). Reuses `get_panchanga`, `nakshatra_info`, `sun_rise_set` and `daily_timing_windows`
from `astro_calc.py`, plus `NAK_NATURES` from `constants.py`. Pure math + lookup — no AI,
no new dependencies, no streamlit.

## AI

- `fetch_data` — 1 Gemini Flash Lite call returning JSON tiles (~₹0.02). Cached 24h.
- `fetch_daily_tarot` — 1 Gemini Flash Lite call returning {MEANING, ACTION, MANTRA}. Cached 24h.
- Astro-Decide — 1 Gemini call per click. Verdict is Python-determined by Tara Bala; AI only explains.

## Editing tips

- Add a new tile → add a key to `build_data_prompt`'s JSON schema + render block in `view.py`.
- Change Tara Bala themes → edit the `themes` dict in `view.py`.
- Change the 45d / 14d shift alert thresholds → edit `view.py` (dasha_alert section).
