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

| Method & path | What it does |
|---|---|
| `POST /chart/interpret` | The curated "front room" — the hero cards the chart screen shows. |
| `POST /chart/houses` | All 12 houses, warm (sign on the house + any planets there). |
| `POST /chart/planets` | Each of the 9 planets in its sign + house, warm (composed, with dignity/retrograde notes). |

### `POST /chart/interpret`
```jsonc
{ "profile": {…kundli shape, lat/lon…} }
→ { "ok":true,
    "headline":"On the surface you're curious, but the part that actually runs you is steadier than most people ever see.",
    "core":[
      { "title":"You at the core", "body":"…warm, no jargon…", "sanskrit":"लग्न मिथुन · सूर्य वृषभ", "why":"…plain…" },
      { "title":"Your inner world", … }, { "title":"How you love", … },
      { "title":"How you think", … }, { "title":"Your drive", … },
      { "title":"Where you grow", … } ],
    "birth_star":{ "title":"Your birth star · Rohini", "body":"…(27-nakshatra personality)…", … },
    "current_chapter":{ "title":"The season you're in", "body":"…(Mahadasha + sub-period)…", … },
    "highlights":[ { "kind":"gift", "title":"A gift in your chart", … },
                   { "kind":"growth", "title":"A growth area", … } ],
    "precision_note":null }
```
Birth-time tiers: an **exact time** gives the rising sign + houses (all 6 cards +
"Where you grow"); an **unknown time** falls back to the **Sun/Moon sign reads**
(still reliable) + a precision note. `birth_star` (Moon-based) works at every tier.

## Build slices (task #18) — all complete
1. ✅ **Atoms + composition + `/chart/interpret`** — 12 signs, 12 houses, 9 planets.
2. ✅ **27 nakshatras** (`nakshatras.py`) — the birth-star personality (`birth_star`).
3. ✅ **Dasha sub-theme + key yogas/doshas** (`yogas.py`) — richer "season" +
   `highlights` (gifts + gently-framed growth areas).
4. ✅ **`/chart/houses` + `/chart/planets` deep-dives** + docs.

## Design note
Warm **atoms** for the finite sets (signs/houses/planets), **composed** into
sentences (`service.py`) — the same approach `kundli_text.py` uses, so the text
stays classically correct without a 200-combination hand-write or anything
AI-sounding. `meanings.py` holds the atoms; `service.py` composes the cards.
