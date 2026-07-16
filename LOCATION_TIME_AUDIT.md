# Location + timezone audit — EVERY feature

> Started 2026-07-16. **The rule below decides every case. Apply it to any new endpoint too.**
>
> Two different questions, constantly confused:
> - **WHERE** (lat/lon) decides **what is calculated** — because it decides SUNRISE.
> - **WHEN** (timezone) decides **what is displayed** and **which day "today" is**.
>
> A feature can need one, both, or neither. Getting this wrong is silent: the app still renders,
> it is just describing someone else's sky. See `TODAY_TAB_AUDIT.md` for the proven case
> (Shimla → Saturn "avoid new beginnings" vs Chennai → Jupiter "one of the day's best stretches",
> same instant, same person).

## THE RULE (four buckets, no exceptions)

**A · NATAL — birth lat/lon/tz. Fixed forever. Travel is irrelevant.**
You were born where you were born. Every tradition agrees. Ascendant, houses, D9/D60, dasha,
natal planet positions, yogas, doshas. **Never** substitute the current place here.

**B · SUNRISE-DERIVED — needs CURRENT lat/lon.**
If the answer is cut from local sunrise/sunset, it belongs to where the user is STANDING:
hora, choghadiya, Rahu Kaal, Gulika, Yamaganda, Abhijit, muhurta windows, the Vedic day
boundary (sunrise→sunrise), and "the tithi/nakshatra AT SUNRISE" (the day's label).

**C · GLOBAL — needs no location at all.**
Angular facts are identical from everywhere at a given instant: the Moon's sign/nakshatra/degree
right now, tithi/yoga/karana as raw angles, planetary transits (gochara), and **chandrashtama**
(transiting Moon vs natal Moon — both terms are location-free).

**D · DISPLAY/SCHEDULING — needs CURRENT tz.**
Any time shown to a human, any "today", and anything **scheduled**: push notifications, capsule
delivery, streak day boundaries.

**Deciding procedure:** ask *"does this answer change if I fly to New York?"*
- No, and it never changes → **A**.
- No, it's an angle → **C**.
- Yes, because sunrise moved → **B**.
- Only the clock/label moved → **D**.

---

## Status

### ✅ FIXED + VERIFIED (Today tab)
| Route | Bucket | Note |
|---|---|---|
| `/dashboard/hora` | B + D | now `getCurrentPlace()` |
| `/dashboard/timing` | B + D | now current lat/lon + `localDateISO(tz)` |
| `/dashboard/panchang` | B + D (+A) | current lat/lon for sunrise; `profile:` still BIRTH for natal terms |
| `/dashboard/day-alerts` | B + D | current lat/lon + tz-aware date |
| `/dashboard/muhurta` | B + D | current lat/lon; a wedding time cut from the birth city's sunrise is the wrong time |
| `/dashboard/today` | A + C | correctly sends the BIRTH profile — reading is Moon/natal based |

Mechanism: `mobile/src/api/place.ts` → `getCurrentPlace()`. Device-tz ≠ birth-tz → the zone's
city; otherwise the birth place (within one zone the tz cannot locate them, and all of India is
`Asia/Kolkata`). **GPS on demand is the agreed upgrade** — only when a feature needs it, with a
plain-English "why" shown BEFORE the OS prompt, never persistent. `expo-location`'s
`getCurrentPositionAsync()` returns `{coords:{latitude,longitude}}` directly; **GPS *is* lat/lon,
there is no conversion**. `reverseGeocodeAsync()` gives the city NAME if we want to show it.

### 🔴 THE BIG ONE — FIXED 2026-07-16: `date.today()` = the SERVER's day = UTC

**Not a traveller bug. This was wrong for the ENTIRE userbase, every single day.** Render runs in
UTC; India is UTC+5:30. So between **00:00 and 05:30 IST — ~23% of every day — a bare
`date.today()` returned YESTERDAY for every Indian user.** Proven:

```
user's wall clock : 2026-07-16 02:00 IST
same instant, UTC : 2026-07-15 20:30 UTC
server would say today = 2026-07-15   <- YESTERDAY for the user
```
(And right now, live: India is on 2026-07-16 while Auckland is already on 2026-07-17.)

Worse, it was **self-suppressing**: the Sage seals an opener keyed on `for_date`, so it wrote
the wrong day's message and then `moon_message_exists` blocked the right one.

Shipped in — all now fixed via **`shared/timeloc.py`** (`user_today` / `resolve_today` / `user_now`):
| File | Was | Now |
|---|---|---|
| `moon/api.py:35` | `_date.today()` | `resolve_today(req.today, req.tz)`; `tz` added to `MoonCheckRequest` |
| `capsule/api.py` ×3 | `_date.today()` | `resolve_today(...)`; `tz` added to both schemas. **Worst UX**: a capsule's whole promise is opening on ITS day |
| `notify/service.py:39` | `_date.today()` | per-user `user_today(_user_tz(...))` from their saved profile |
| `notify/service.py:92` | one shared `today` for EVERY user | `today=None` → each user resolves their own |
| `numerology/prompts.py` | hard-coded `ZoneInfo("Asia/Kolkata")` | threads `tz` (the engine already accepted one; the caller dropped it) |
| `rituals/service.py:153` | `date.today()` | `resolve_today(on_date, tz or profile.tz)`; `tz` added to schema + client. **The WEEKDAY picks which planet's remedy you get** — so for the first 5.5h of every Indian day it offered the PREVIOUS day's planet ("do your Saturn remedy" on a Sunday). **Verified fixed:** same instant now gives Auckland=Friday, India=Thursday. |
| `shared/db/supabase_client.py:213` `increment_streak` | `_date.today()` | uses the check-in's own client-supplied `date`. **Silently STALLED streaks**: 23:00 IST Mon (17:30 UTC Mon) + 02:00 IST Tue (20:30 UTC **Mon**) = same UTC day → "same day again → no change". **Proven: 12→13 with the user's day, 12→12 with the server's.** |

The schema comment literally documented it — `"defaults to today (server)"` — nobody noticed
"server" meant "a machine in a different country from every user".

### ✅ VERIFIED CORRECT — do NOT "fix" these
- **`datetime.now(ZoneInfo("UTC"))` → `ephemeris.julday(...)` is RIGHT.** A Julian Day is a
  universal instant; planetary longitude is a global fact. Localising it would BREAK the maths.
  `dashboard/api.py:221,285` do this correctly for Tara-Bala.
- **`/dashboard/decide-quick`** — bucket **C**. Natal Moon vs transiting Moon, both global. No
  location needed. Correct as written.
- **`/oracle/prashna`** (`oracle/api.py:255-273`) — **already correct.** Requires `place` OR
  `lat+lon+tz` and casts `now` in THAT zone; never touches the birth profile. My earlier
  INFERRED "wrong chart" worry was wrong. The Streamlit view (`oracle/prashna.py`) also asks for
  the current place and geocodes it. *(Not yet called by the mobile app at all.)*
- **`dashboard/api.py:176,194`** — `datetime.now(ZoneInfo(req.tz))`. Correct.
- **`people/service.py:37`** — `datetime.now(ZoneInfo(tz))`. Correct.
- **`companion/service.py:121`** `_db_profile_to_astro` — returns BIRTH data with the birth tz.
  Correct: that is bucket **A**, the natal chart.

### ✅ AUDIT COMPLETE — the rest, read and verified 2026-07-16
| Route | Bucket | Verdict |
|---|---|---|
| `/planner/*` | B + D | **Correct.** `api.py:38` `datetime.now(ZoneInfo(tz)).date()` from the request; passes `req.lat/lon/tz` into `daily_timing_windows`. |
| `/horoscopes/*` | C + D | **Correct.** Takes an explicit `req.today`; `local_to_julian_day(..., profile["tz"])` uses the BIRTH tz for the natal JD, which is right. |
| `/dashboard/calendar-check` | B + D | **Correct.** Takes explicit `req.lat, req.lon, req.tz`. |
| `/people/*` (`compare`, `couple-week`, `family-grid`, `relationship-weather`) | A + D | **Correct.** `service.py:31-37` resolves the day as viewer's tz → first person's tz → IST. Never the server. |
| `/chart/*` (`compute`, `houses`, `planets`, `interpret`, `dasha-timeline`, `reveal`) | **A** | **Correct.** Schemas take only `profile` — no current-location leak. Natal-only, as required. |
| `/memory/*` | A | **Correct.** `service.py:294` `_self_astro` returns BIRTH data (birth tz). |
| `/me/*` | A + D | **Correct.** `service.py:33` `_self_astro` = BIRTH data. Streak now uses the check-in's own date. |
| `/tarot/*`, `/numerology/*` (core), `/palmistry/*` | none | No sky involved. Numerology's *timing* numbers are bucket D and now thread `tz`. |

**Remaining hard-coded `"Asia/Kolkata"` strings are all fine**: either doc comments in schemas
(`tz: str # IANA tz, e.g. "Asia/Kolkata"`), a Streamlit input's default value, or a last-resort
fallback on a NATAL path for a profile with no stored tz. None of them decide a user's day.

### 🟡 STILL OPEN (not location/time bugs — product decisions or unwired)
- **Eclipse visibility** — the event is global ("in 3 days" is true anywhere) but *visibility* is
  local. Only matters if copy ever implies they can SEE it. Currently it does not.
- **Festival dates** — **owner's call, not a bug.** NRIs usually follow the LOCAL panchang (hence
  separate US panchangs); some follow India. Decide, then implement.
- **`setCurrentPlace()` is still never called** — so `getCurrentPlace()` returns the tz-zone city
  when abroad and the birth place otherwise. GPS-on-demand is the agreed upgrade for the
  same-country case (Shimla→Chennai, which the timezone cannot see).

| Route | Likely bucket | Risk if wrong |
|---|---|---|
| `/companion/*` | **D** | **🔴 VERIFIED WRONG.** `features/companion/schemas.py:22`: `date … defaults to today (profile's tz)`. The profile tz is the BIRTH tz, so a traveller in New York is served the Indian day. Also `service.py:121` hard-defaults `"tz": p.get("tz") or "Asia/Kolkata"`. Fix: accept the CURRENT tz from the client and default "today" to it; keep the birth tz for natal terms only. |
| `/moon/messages`, `/moon/messages/{id}/read` | **D** | **Highest-risk.** If scheduled against the profile tz, a traveller is pinged at 3am. Given `/companion/*` is confirmed wrong, assume this shares the flaw until checked. INFERRED |
| `/capsule/*` ("the sky delivers it") | **D** | Delivered at the wrong local hour. INFERRED |
| `/me/streaks/{kind}` | **D** | A streak breaks or double-counts across a date change. INFERRED |
| `/me/checkins` | **D** | Keyed by date; a date-line crossing could double-log. Client side now uses device-local (correct). INFERRED |
| `/rituals/today` | **B?/C?** | If the ritual is tied to a planetary hour or weekday-at-sunrise it is **B**. INFERRED |
| `/planner/*` | **B + D** | Any scheduling/window logic is sunrise-cut. INFERRED |
| `/dashboard/calendar-check`, `/decide`, `/decide-quick` | **B + D** | Date/window based. INFERRED |
| `/dashboard/gochara` | **C** | Transits are global; should need no location. INFERRED |
| `/dashboard/forecast`, `/couple-week`, `/family-grid` | **C + D** | Day boundaries only. INFERRED |
| `/horoscopes/*` | **C + D** | Day-based. INFERRED |
| `/chart/*` (`compute`, `houses`, `planets`, `interpret`, `dasha-timeline`, `reveal`) | **A** | Must stay BIRTH. Verify none quietly take a current location. INFERRED |
| `/people/compare`, `/marriage`, `/matchmaking`, `/relationship-weather` | **A** | Natal-vs-natal. INFERRED |
| `/reflect/*`, `/oracle/prashna` | **A + B?** | Prashna is cast for the time+place of ASKING → **B**, genuinely current-location. INFERRED |
| `/numerology/*`, `/tarot/*`, `/palmistry/*` | none | No sky involved. INFERRED |
| eclipse copy in `/dashboard/day-alerts` | **C + local** | The event is global ("in 3 days" is true anywhere) but **visibility is local**. If any copy implies they can SEE it, that needs location. |
| Festival dates | **product call** | NRIs usually follow the LOCAL panchang (hence separate US panchangs); some follow India. **Owner decides — not a bug.** |

### Notes on two special cases
- **Prashna (`/oracle/prashna`)** is the one place where "current location" is doctrinally
  required rather than a convenience: the chart is cast for the moment and place of the QUESTION.
  Using the birth place here is not a rounding error, it is the wrong chart.
- **Chandrashtama is bucket C**, not B. Both the natal Moon and the transiting Moon are
  location-free; only *which day* it lands on is local (bucket D).

## Order of work
1. `/moon/messages` scheduling (**D**) — the 3am-ping bug, highest live risk.
2. `/oracle/prashna` (**B**) — wrong chart, not a small error.
3. `/rituals/today` + `/planner/*` — classify, then fix.
4. Confirm every `/chart/*` and `/people/*` route is untouched **A**.
5. Eclipse visibility copy; then the owner's festival decision.
