# Demo-data ledger — what is REAL vs FAKE in the mobile app

> Written 2026-07-16. **Rebuilt 2026-07-17: the fix below is now DONE.**
>
> **Why this exists:** the mobile app was hand-ported from the ASTROLO design prototype, and the
> prototype's placeholder data came with it. Components take an optional `live` prop and fell
> back to a demo constant when it wasn't passed. That was the right call for the port, but it
> created one dangerous property: **demo data is visually indistinguishable from real data.**
> Nothing turned red. Forget to pass `live` and the app confidently showed Aarav's chart to a
> real user and nobody noticed. Same failure mode as the `birth_time_known` bug: silent,
> plausible, wrong. See [[feedback_accuracy_seam]].

## THE LEDGER IS NOW A COMMAND, NOT A TABLE

Every fake lives in **`mobile/src/theme.demo.ts`**, which **throws at import in production**.
So the list of unwired screens is derived from the code and can never go stale:

```bash
cd mobile && grep -rln 'from "\.\.\?/theme\.demo"' src/
```

That is the ledger. A hand-maintained table would drift the moment someone forgot to update it;
this cannot. **Definition of done for wiring a screen: the `theme.demo` import is DELETED.**

As of 2026-07-17 that command returns:

| Screen | Pulls | Note |
|---|---|---|
| `today/read.tsx` | READ_CHIPS, LIFE_AREAS | fallbacks only, guarded by `demoFallback` |
| `today/LivingSkyHeader.tsx` | HORA_LINE | fallback only, guarded |
| `plan/MyDay.tsx` | DAY_CLOCK | |
| `plan/PlanTab.tsx` | ASK_MOMENT, PANCHANG_SOON | |
| `plan/toolsheets.tsx` | MUHURAT, CAL_DOCTOR, ASK_MOMENT, TIME_CAPSULE | |
| `plan/MonthScreen.tsx` | MONTH, dayDetail | |
| `screens/JournalScreen.tsx` | MIRROR | |

**`today/sheets.tsx` is no longer on that list** — it is wired (task #56).

## The three guards

1. **`theme.demo.ts` throws in prod at import.** Fakes cannot ship. Blast radius is exactly the
   unwired screens, because wired ones don't import it.
2. **`demoFallback(where, live, fake)`** — fires *only when a fallback is actually used*, which
   is precisely the condition worth shouting about. Throws in prod; records in dev.
3. **`<DemoBadge/>` (`ui/DemoBadge.tsx`)** — the on-screen giveaway. **This is the piece that
   was missing:** `__DEV__` is true in Expo Go, which is where the app is actually tested, and a
   `console.warn` goes to the Metro log that nobody reads while holding a phone. Without the
   badge, a dev fallback was still a screen quietly lying. It names every fake source currently
   rendering. Renders nothing in production.

## 🔴 THE SEED PROFILE — the fake that none of the guards could catch

`api/config.ts::SEED_PROFILE` is **Aarav, born 1998-08-14 04:20 in Jaipur**, and it is the
default until `setProfile()` runs.

Every other fake is a fabricated **string**, so it surfaces as a missing `live` value and a guard
fires. The seed fabricates the **person**. The maths on it is real, the backend returns a genuine
chart, nothing is null, no fallback triggers — the app just renders a flawless reading for a
stranger and hands it to whoever is holding the phone.

**It is reachable today.** `buildProfileFromData()` returns `null` on the returning-user LOGIN
path (logging in captures no birth data), and `App.tsx` does `if (p) setProfile(p)`. So a
returning user who logs in reads Aarav's day as their own.

**Now guarded:** `getProfile()` routes the seed through `demoFallback`, so it names itself on the
badge in dev and throws in prod (the reading then fails honestly via the `SkyOffline` banner).
**The real fix is task #54**: load the saved profile from `GET /me/profiles` at login.

## Deleted outright (not moved — they were lies with no live counterpart)
`ECLIPSE`, `LIFE_AREA_META`, `PERSONAL_LINES`, `NAME`, `DATE`, `AHEAD`, `DAY_LINE`, `ALMANAC`,
`FOCUS`, `FESTIVAL`.

- **`LIFE_AREA_META`** asserted *"today the Moon is passing through your partnership area"* under
  Love, for every user, every day. At most one domain can be in focus on a given day; on
  2026-07-16 the true answer was **money**. The backend already returned the real
  `detail`/`why`/`planet`/`houses`.
- **`PERSONAL_LINES`** was the worst of them: it claimed to *remember* the user (*"You usually
  soften on days like this"*) and was shown to people who had never checked in once. It is now
  earned from `/memory/today` or it does not appear.
- **`ECLIPSE`** invented a dated, specific, alarming claim. No live eclipse now means **no card**.

**NOT demo (safe, keep in `theme.ts`):** `MOODS`, `MOOD_BY_KEY`, `CYCLE`, the `Mood` type,
colours, `CHECKIN_REFLECTION`. That is the design system, not fake user data. (`Mood.forecast`
holds prototype prose, but every read of it goes through `demoFallback` first.)

## Still unwired (the mockup shell — expected, but not a working app)
`screens/DecodeScreen.tsx` (hardcoded `["Lagna","Libra"]` — a fake ascendant for everyone; when
wiring, Lagna MUST hide unless `houses_reliable`), `screens/NotifScreen.tsx`,
`screens/WalletScreen.tsx` (inline fake lists), `plan/MonthScreen.tsx`, `screens/JournalScreen.tsx`.
The wallet balance (`bal = 108` in `AstroApp`) is also local fake state.
