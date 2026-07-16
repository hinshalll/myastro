# Today tab audit — Read + Plan

> Started 2026-07-16. **We finish this tab before touching any other.** Nothing here is "done"
> until it is verified against the live backend, not just rendering.
>
> Companion docs: `DEMO_DATA_LEDGER.md` (what is still fake), memory `feedback_accuracy_seam`
> (why the bugs live at the app↔backend seam).

---

## 🔴 BUG 1 — every daily reading is computed for the user's BIRTH PLACE, not where they are

**This is the biggest accuracy bug found so far and it affects most users, not just travellers.**

`mobile/src/api/today.ts` passes the BIRTH profile's coordinates to every daily endpoint:

```ts
const p = getProfile();                                    // ← the BIRTH profile
apiPost("/dashboard/hora",      { lat: p.lat, lon: p.lon, tz: p.tz });
apiPost("/dashboard/day-alerts",{ date: localDateISO(), tz: p.tz, lat: p.lat, lon: p.lon });
apiPost("/dashboard/timing",    { date: localDateISO(), lat: p.lat, lon: p.lon, tz: p.tz });
apiPost("/dashboard/panchang",  { profile: p, lat: p.lat, lon: p.lon, tz: p.tz, days });
```

**Why it is wrong (Vedic, not opinion):** hora (planetary hour), Rahu Kaal, muhurta windows and
the day's tithi/nakshatra are all cut from **LOCAL SUNRISE**. Sunrise is a property of where you
are standing, not where you were born. The natal chart uses the birth place forever; the daily
sky does not.

**Proven live, same instant, three places:**

| Location | Hora | The line the user is shown |
|---|---|---|
| Shimla (birth — what we send) | **Saturn** | "a slow, steady stretch, better for patient work than for new beginnings" |
| New York (where they are) | **Mercury** | "a sharp stretch for talking, writing, money" |
| Chennai (same country) | **Jupiter** | "one of the day's best stretches, good for anything that matters or a fresh start" |

Sunrise: Shimla 05:28 · New York 05:38 · Chennai 05:50.

**Born in Shimla, living in Chennai → told to avoid new beginnings during one of their best
windows.** Opposite advice, delivered confidently. Most Indians do not live in their birth city,
so this is not an edge case.

**It is also internally incoherent:** `localDateISO()` takes the date from the DEVICE, while the
sunrise comes from the BIRTH place. A traveller gets today's date married to yesterday's sky.

**The fix — two locations, not one:**
- **Birth** lat/lon/tz → the natal chart only. Fixed forever. (Already correct.)
- **Current** lat/lon/tz → every daily/transit computation. (Does not exist yet.)

Getting "current" without a scary permission:
1. Onboarding asks **"Where do you live now?"**, defaulting to the birth place (one tap to
   confirm). Reuses the existing `/geo/search` picker, so lat/lon/tz come free.
2. Store as `current_place/current_lat/current_lon/current_tz` on the profile.
3. Daily endpoints read current; natal reads birth.
4. Later: if the device tz stops matching `current_tz`, offer *"Looks like you're in New York.
   Use it for today's readings?"* — offer, never silently switch. **No GPS.**

---

## ✅ NOT A BUG — the API layer is actually healthy (verified 2026-07-16)

I twice reported a bug that did not exist, both times because my test script read the RAW
backend key instead of the key the app's adapter maps. Recording it so nobody re-raises them:

- **"/dashboard/timing returns 0 windows"** — WRONG. It returns **16 `choghadiya` slots**
  (sunrise 05:42, "Shubh 05:42→07:25", summary "Strong window 12:05pm–1:00pm (Abhijit Muhurta);
  soft dip 2:15pm–3:57pm (Rahu…)"). There is no `windows` key; `fetchTiming` maps `r.choghadiya`.
- **"panchang quality is empty"** — WRONG. There is no `quality` key; the backend returns
  `band`/`label`, and `fetchPanchang` correctly maps `quality: d.band`, `note: d.label`.

**Lesson: test through the app's adapter, or read the adapter first. A "missing" field is far
more often my wrong key than a broken endpoint.**

Live check of every Today endpoint, all returning real data:

| Endpoint | Result |
|---|---|
| `/dashboard/today` | vibe "Tender", Moon Cancer/Ashlesha, chandrashtama False, good_for ×3, life_areas love/work/money filled |
| `/dashboard/hora` | Saturn + real line |
| `/dashboard/timing` | sunrise 05:42, 16 choghadiya, 1 good window, real summary |
| `/dashboard/panchang` | 3 days, band/label/tithi/nakshatra/yoga/karana/best_window |
| `/rituals/today` | ritual + weekday + is_planet_day |

**So the Today tab's problems are NOT the backend or the API layer.** They are: the birth-place
bug above, the demo fallbacks below, and the unwired sheets.

---

## ✅ FIXED this session
- **Birth-time tiers.** `buildProfileFromData` never sent `birth_time_known` (defaults True
  server-side) → users with no birth time were shown a rising sign + houses off a noon
  placeholder. Same person = Cancer/Virgo/Libra rising across tiers. Now sends both flags, and
  both are REQUIRED in the `Profile` type so the compiler enforces it.
- **Check-in moved to evening** (5pm→midnight, device-local = where the user actually is).
  Morning answers stored "breakfast" labelled as the whole day, poisoning the pattern engine
  that correlates a DAY's energy against that day's sky.
- **Chat greeted everyone as "Aarav"** (`${NAME}` baked into a module-scope array at import).
- **Journal's date was frozen at "Tuesday, 17 June"**.

---

## ✅ FIXED 2026-07-17 (this pass)

- **`today/sheets.tsx` is WIRED** (#56). It was pure demo, so tapping into any Today card opened
  fabricated detail. The backend already returned every field it was faking — the **adapter was
  throwing them away**: `fetchDayAlerts` dropped `sutak_note`, the eclipse `why`, and the entire
  `chandra_sandhi` block on the floor. Both sheets now read the SAME live payload as the card
  that opened them, so tapping in cannot show a different day than the card promised.
- **The AreaSheet's fabricated astrology.** `LIFE_AREA_META` asserted *"today the Moon is passing
  through your partnership area"* under Love, for every user, every day. At most one domain can
  be in focus; **proven live on 2026-07-16 the true answer was `money`, not `love`.** Now uses
  the server's real chart-aware `why`, plus `planet`/`houses`/`in_focus` from
  `shared/astro/life_areas.py`. The app no longer keeps a parallel table of which houses rule
  what: one source of truth, or the two drift and the sheet names a house the reading never used.
- **Chandra Sandhi card + sheet** — new, and real (18:12→21:32, Cancer→Leo on the test day). The
  backend had computed it all along and nothing rendered it.
- **The eclipse card can no longer be invented.** It is a dated, specific, alarming claim, so no
  live eclipse = **no card**. The old solar/lunar toggle was a design-preview affordance; the sky
  decides now, not a tap. The backend gained a `short` (card) vs `why` (sheet) split so opening
  the sheet adds something instead of echoing the card back.
- **`todayErr` was set but NEVER RENDERED.** A backend outage looked like a finished screen
  quietly showing the prototype's placeholder day. Now an honest `SkyOffline` banner + Retry.
- **The check-in never saved anything** — the entire point of it. It fed nothing to the pattern
  engine and dropped every answer when the sheet closed. Now POSTs `/me/checkins`.
- **"12 days in a row" was hardcoded** and shown to someone opening the app for the first time.
  Now the real streak from `/me/streaks/checkin`, or nothing.
- **"+1 diya lit" fired over a check-in that was silently discarded.** Now it only celebrates a
  save that actually happened; otherwise it says so.
- **The personal line** (*"You usually soften on days like this"*) claimed to remember users who
  had never checked in once. Deleted; earned from `/memory/today` or absent.
- **Backend user-facing copy had em dashes** (eclipse `why`, sandhi `note`). Fixed.
- **The demo guard is now visible** — `<DemoBadge/>`. `__DEV__` is true in Expo Go, so the old
  console.warn was invisible to anyone testing on a phone: a dev fallback was still a silent lie.

---

## 🔴 THE BIGGEST ONE: the seed profile (detail in DEMO_DATA_LEDGER.md)

`SEED_PROFILE` = **Aarav, Jaipur, 1998**. Every other fake is a fabricated string, so it shows up
as a missing `live` and a guard fires. This one fabricates the **person**: the maths is real,
nothing is null, no guard fired — the app renders a flawless reading for a stranger. **Reachable
today** via the returning-user login path (`buildProfileFromData()` returns null there, and
`App.tsx` does `if (p) setProfile(p)`). Now routed through `demoFallback` so it names itself in
dev and throws in prod. **Real fix = task #54** (load the profile from `GET /me/profiles`).

---

## Order of work
1. **Task #54** — load the saved profile at login. Now the top item: until it lands, a returning
   user reads Aarav's chart.
2. **Finish Bug 1** — the `getCurrentPlace()` seam is in and every daily call now routes through
   it, but it is a **NO-OP until something calls `setCurrentPlace()`** (it falls back to the
   birth place). The remaining work is the UI: ask **"Where do you live now?"** in onboarding
   (default = birth place, one tap to confirm; reuse the `/geo/search` picker so lat/lon/tz come
   free), store it, and surface `looksLikeTheyMoved()` as an offer, never a silent switch.
3. **Rest of #57** — My Day tasks still unwired. (Check-ins + personal line are done, but both
   stay dark until auth exists, since they are JWT-gated.)
4. **The Plan sub-tab's demo** — `DAY_CLOCK`, `PANCHANG_SOON`, `ASK_MOMENT`, `MUHURAT`,
   `CAL_DOCTOR`, `TIME_CAPSULE` still fall back to fakes.

## Deliberately NOT changed (do not "fix" these)
- **The natal chart still uses the BIRTH place, forever.** `/dashboard/today` and panchang's
  `profile` field still send `getProfile()`. Chandrashtama and every natal comparison need the
  natal Moon. Only lat/lon/tz moved to the current place.
- **The backend maths, rules and readings are untouched.** The engine was never the problem.
