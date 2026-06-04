# features/people — the "You & People" shared-day readings

Pure-math, AI-free relationship features that read **two or more charts at once**.
They extend the single-day `/dashboard/relationship-weather` into the two shapes
the People tab needs. Everything is Moon-based, so it works at **every birth-time
tier** (an unknown birth time uses a noon placeholder per person), and everything
is **stateless** — the app passes the people it already has (no JWT needed for the
math).

All calculation goes through `shared/astro/` (`relationship_weather.py` +
`forecast.py`, which themselves go through the ephemeris adapter). This feature is
glue only — looping over people and stitching the pieces together.

## Endpoints

| Method & path           | What it does |
|-------------------------|--------------|
| `POST /people/couple-week` | The next-N-days (default 7) "weather" between two people — a rail for the People tab. |
| `POST /people/family-grid` | Today's state for several saved people at a glance, each row optionally paired with your shared tone. |

### `POST /people/couple-week`
Extends the single-day relationship-weather over a span (mirrors `/dashboard/week`).

```jsonc
// request
{ "profile_a": {…kundli shape…}, "profile_b": {…}, "start_date": "2026-06-04", "days": 7 }
// response
{ "ok": true, "start_date": "2026-06-04",
  "baseline": { "score": 0.66, "rashi_relation": "warm", "bond": "There's a natural fondness…" },
  "days": [ { "date":"…","tone_word":"Easy","summary":"…","good_for":"…","avoid":"…",
              "score":0.82,"band":"good","is_today":true,"why":"…","sanskrit":"…" }, … ] }
```

* Each day = the full `daily_relationship_weather` output + a coarse `band`
  (good/neutral/difficult) for the rail colour + an `is_today` flag.
* The durable **baseline** ("how the two of you mesh") is identical every day, so
  it's lifted once into a top-level `baseline` block instead of repeating per card.

### `POST /people/family-grid`
Today's state for several saved people, all read on **one shared calendar day** so
the cells are comparable.

```jsonc
// request
{ "people": [ { "name":"Mom","relation_tag":"mother","profile":{…} },
              { "name":"Priya","relation_tag":"partner","profile":{…} } ],
  "viewer": {…optional: your own chart…},
  "date": "2026-06-04" }
// response
{ "ok": true, "date":"2026-06-04",
  "people": [ { "name":"Mom","relation_tag":"mother",
                "vibe_word":"Quiet","vibe_score":0.55,"band":"neutral","mood":"…",
                "together": { "tone_word":"Light","score":0.66,"band":"good","summary":"…" } }, … ] }
```

* Each row = that person's own daily "Cosmic Weather" (`daily_moon_forecast`).
* Pass `viewer` (your own chart) and each row also gets `together` — the
  relationship-weather tone between you and that person.

## Framing (blueprint §2)
Warm, plain, beginner-friendly primary text; Sanskrit/technical terms only inside
`why` / `sanskrit`. Gentle guidance, never fate.
