# features/chart — the plain-English chart-interpretation layer ("the front room")

Turns the raw computed chart into **warm, jargon-free meanings any first-time user
understands** — the human voice over the engine. Every meaning's classical
*substance* is the standard, verified signification (reused from the engine's
`kundli_text.py` atoms + cross-checked against BPHS / Phaladeepika / Saravali);
this layer re-voices it warmly and hides all the machinery. **No live AI** (cost
rule) — static atoms + composition, deterministic per profile (cache-friendly).

Every card is `{ title, body, sanskrit, why }`:
* **`body`** — plain English, **no jargon**, written like a thoughtful friend.
* **`sanskrit`** / **`why`** — the technical detail (sign/house/planet names,
  Devanagari), shown only behind a "why?" reveal. Gentle guidance, never fate.

## Endpoints

| Method & path | Status | What it does |
|---|---|---|
| `POST /chart/interpret` | **built (slice 1)** | The curated "front room" — the hero cards the chart screen shows. |
| `POST /chart/houses` | planned (slice 4) | All 12 houses, warm. |
| `POST /chart/planets` | planned (slice 4) | Each planet in its sign + house, warm (composed). |

### `POST /chart/interpret`
```jsonc
{ "profile": {…kundli shape, lat/lon…} }
→ { "ok":true,
    "headline":"You come across as curious and quick, but inside you run restless and meaning-seeking.",
    "core":[
      { "title":"You at the core", "body":"…warm, no jargon…", "sanskrit":"लग्न मिथुन · सूर्य वृषभ", "why":"…plain…" },
      { "title":"Your inner world", … }, { "title":"How you love", … },
      { "title":"How you think", … }, { "title":"Your drive", … },
      { "title":"Where you grow", … } ],
    "current_chapter":{ "title":"The season you're in", "body":"…(dasha theme)…", … },
    "precision_note":null }
```
Birth-time tiers: an **exact time** gives the rising sign + houses (all 6 cards +
"Where you grow"); an **unknown time** falls back to the **Sun/Moon sign reads**
(still reliable) + a precision note.

## Build slices (task #18)
1. ✅ **Atoms + composition + `/chart/interpret`** — 12 signs, 12 houses, 9 planets
   (warm), the hero-card read. *(this slice)*
2. ⏳ **27 nakshatras** — the birth-star personality layer.
3. ⏳ **Dasha themes + key yogas/doshas** — richer "season" + notable highlights.
4. ⏳ **`/chart/houses` + `/chart/planets` deep-dives** + full docs.

## Design note
Warm **atoms** for the finite sets (signs/houses/planets), **composed** into
sentences (`service.py`) — the same approach `kundli_text.py` uses, so the text
stays classically correct without a 200-combination hand-write or anything
AI-sounding. `meanings.py` holds the atoms; `service.py` composes the cards.
