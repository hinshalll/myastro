# Myastro — Content Accuracy & Voice Guide

Rules for **any user-facing astrology text** and **any interpretation/meaning table**.
The goal: every word a user reads is **astrologically correct** AND understandable by
someone who knows **nothing** about astrology — warm, human, jargon-free — and costs
**nothing at runtime** (it's pre-baked static data, never a live AI call).

> Read this before writing or editing any meaning table, forecast line, card text,
> reading template, or label. It applies to the mobile app and the API responses it shows.

---

## 1. Accuracy — get the Vedic rules precisely right

- **Math is already trustworthy.** Planetary positions, nakshatras, dashas, panchanga,
  eclipse times, transits all come from **Swiss Ephemeris** (sidereal, Lahiri ayanamsa).
  Don't re-derive these — use the engine.
- **Meanings/interpretations are NOT automatically correct.** When you author or edit any
  interpretation (what a placement/transit/number/card *means*):
  1. **Research authoritative sources first** (classical texts + reputable references) —
     do NOT improvise from general memory.
  2. **Cross-check multiple sources** for anything contested; prefer the *classical* rule
     when classical and "modern/psychological" readings disagree.
  3. **Don't confuse different concepts.** Classic trap (already hit once): a planet's
     *natal house* meaning is NOT the same as its *transit* result. Example: the Moon's
     **transit** is favourable in houses **1,3,6,7,10,11** and challenging in
     **2,4,5,8,9,12** from the natal Moon (Chandra Gochara, Phaladeepika) — even though
     the natal 5th house is about creativity/children.
  4. **Leave a source note in a code comment** (which rule/text it follows) so it's
     auditable later.

## 2. Voice — warm, plain, and human (zero "AI smell")

- **Beginner-first.** Assume the reader knows nothing about astrology. No Sanskrit, no
  technical jargon in any **primary** text (headline, mood, card label, button).
- **Sanskrit / technical terms live ONLY** inside a `why` / depth reveal or a dedicated
  `sanskrit` field — never in the main line.
- **Warm and concrete**, like a thoughtful friend: short sentences, plain words, specific
  ("send the half-finished idea"), not vague ("embrace opportunities").
- **Actionable + reflective, never fate.** "Better for calm talk today" / "a low,
  reflective window" — never "you will fail" or hard predictions (blueprint §2).
- **No AI tells.** No "As an AI…", no hedging boilerplate ("It's important to note…"),
  no robotic bullet lists where one warm sentence works, no em-dash-stuffed filler.
  If it reads like a model wrote it, rewrite it.
- **Translate the jargon** (blueprint §3): Kundli→"Your Chart", Dasha→"Life Chapters",
  Gochara→(invisible, powers "Today"), Prashna→"Ask the stars", etc.

## 3. Cost — pre-bake everything; no runtime AI for this

- All interpretation content is **static data** (lookup tables, templates) authored once.
  At runtime the app does **math + lookup only** → instant, free.
- **Live AI is reserved** for the paywalled / 1-to-1 features (Ask chat, free-text journal,
  palm/face, premium readings) — never for the daily free surfaces.

## 4. Quick checklist before "done"

- [ ] Interpretation verified against an authoritative source (not improvised)?
- [ ] Classical vs modern conflicts resolved in favour of the classical rule (+ noted)?
- [ ] Primary text readable by a total beginner — no jargon, no Sanskrit?
- [ ] Sanskrit/technical only behind "why?" / `sanskrit`?
- [ ] Warm, specific, actionable — doesn't sound AI-written?
- [ ] Pure static lookup — no live AI call added to a free surface?

---

## 5. UI display notes (read when building the frontend)

Running list of decisions the UI must honour (so they're not forgotten):

- **Sanskrit is optional, depth-only.** Never put Sanskrit/Devanagari in primary UI. Show
  it only inside the "why?" reveal (the `sanskrit` field). It's a trust/authenticity touch
  for users who know astrology; beginners ignore it. The app works fine if it's hidden.
- **Good/Avoid times strip (`/dashboard/timing`):** show the **quality colours + times +
  the plain `summary`** as the primary content. The Choghadiya `name` values are Sanskrit
  (Amrit, Labh, Char…) — show them only as a small secondary label or on tap, not as the
  headline.
- **Forecast "why?" (`/dashboard/forecast`):** the `why` text is the depth reveal; the
  `vibe_word` + `mood` are the headline. Keep the `sanskrit` line as a small subtitle inside
  "why?", per blueprint §2.
