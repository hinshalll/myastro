# features/companion — the Companion's payoffs (Pattern Engine + The Proof)

The features that make the app feel like it **knows you over time**. All
**pure math + lookup** (cost rule) — no live AI on these surfaces. The astrology
lives in `shared/astro/` (`forecast.py` + `retrospect.py`, which go through the
ephemeris adapter); this feature adds the self-report mapping and the statistics.

## Endpoints

| Method & path | Auth | What it does |
|---|---|---|
| `POST /companion/micro-insight` | none | The **Day-1 mirror**: today's check-in vs today's real Moon transit. |
| `GET /companion/patterns` | **JWT** | The **Pattern Engine**: statistical correlations across your check-ins. |
| `POST /companion/proof` | none | **"Why did that happen?"**: the dasha chapter + slow transits on a PAST date. |

### `POST /companion/micro-insight` — the mirror (immediate, no history)
Makes the mockup's hardcoded `MIRROR` real. Reads the day's Moon state and says
whether the self-reported mood runs **with** the sky or **against** it.

```jsonc
// request — profile (kundli shape) + the app's check-in vocab
{ "profile":{…}, "mood":"heavy", "energy":"low", "clarity":"tired", "date":"2026-06-01" }
// response
{ "ok":true, "line":"You logged 'heavy' — … The sky agrees with you today, so the
   heaviness is real, not random …", "match":"aligned",   // aligned | crosscurrent | neutral
  "why":"…(Chandra house + Tara Bala)…", "sanskrit":"…" }
```
* **aligned** — felt mood and the day lean the same way ("it's real, not random").
* **crosscurrent** — they cross ("you're lighter than the day — your own momentum").
* **neutral** — neither leans strongly.
* Vocab: mood `calm/tender/sharp/heavy/wired`, energy `low/steady/bright/restless`,
  clarity `rested/okay/tired/off`.

### `GET /companion/patterns` — the Pattern Engine (JWT required)
Reads your check-ins + your `self` birth profile, recomputes each day's Moon
state, and runs **plain 2×2 proportion contrasts** (no ML, no AI). Below the bar
(`30` check-ins) it returns progress; at/above it, the strongest correlations —
and stores newly-unlocked kinds in the `patterns` table.

```jsonc
// not yet
{ "ok":true, "unlocked":false, "progress":{"have":12,"need":30},
  "message":"Keep checking in — 18 more days and your first personal pattern unlocks.",
  "patterns":[] }
// unlocked
{ "ok":true, "unlocked":true, "progress":{"have":31,"need":30},
  "patterns":[{ "pattern_text":"Your low-energy days lean toward challenging day-stars —
     9 of 12 (75%), versus 28% on the other days.", "kind":"energy_tara",
     "confidence":"emerging", "why":"…", "evidence":{…counts…} }] }
```
Candidate contrasts (all Moon-based → every birth-time tier): `energy_tara`
(low energy × challenging Tara Bala), `mood_house` (heavier mood × the Moon's
harder houses 2/4/5/8/9/12 from the natal Moon), `clarity_tara` (foggy × Tara).
A contrast must clear a minimum support **and** effect size to surface.

### `POST /companion/proof` — "Why did that happen?" (the trust-builder)
Given a **past** date, explains which Vimshottari **Mahadasha/Antardasha** were
running then + the slow, era-defining transits over the birth Moon.

```jsonc
// request
{ "profile":{…ideally with birth time…}, "date":"2019-03-15", "event":"I changed jobs" }
// response
{ "ok":true, "date":"2019-03-15",
  "headline":"Back then you were in a Rahu–Saturn chapter, with Saturn passing over your birth Moon.",
  "running":{"mahadasha":"Rahu","antardasha":"Saturn","since":"Jul 2017","until":"May 2020"},
  "transits":[{"what":"Saturn passing over your birth Moon","meaning":"…peak of Sade Sati…"}],
  "story":"warm plain-English tie-together", "why":"…", "sanskrit":"…",
  "precision_note":null }   // a caveat string when birth time is unknown (midday estimate)
```

## Classical sourcing (`shared/astro/retrospect.py`)
All standard Parashari doctrine: Vimshottari dasha-lord natures (BPHS); Sade Sati
= Saturn in the 12/1/2 from the natal Moon, Dhaiya = the 4th (Kantaka) / 8th
(Ashtama); Jupiter's transit supportive in 2/5/7/9/11 from the Moon. Warm/plain
primary text, Sanskrit only in `why`/`sanskrit`, gentle guidance never fate
(blueprint §2).
