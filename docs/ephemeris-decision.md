# Ephemeris & Accuracy — Decision (locked 2026-06-02)

> **STATUS (2026-06-03): free engine SHIPPED + fully integrated. Runtime is Swiss-Ephemeris-free.**
> `shared/astro/ephem_skyfield.py` covers positions (7 + 3 outer), **all 5 ayanamshas**
> (lahiri/raman/krishnamurti/yukteshwar/fagan_bradley — ≤0.001"), mean node, ascendant,
> whole-sign houses, **Placidus + KP** (0.00", 0/3600 sub-lords), **tropical positions +
> Placidus + ascendant** (Western chart, ≤2.4"), **ecliptic latitude** (Graha Yuddha),
> sunrise/sunset (≤21s), moonrise/moonset (≤36s), eclipses (exact dates), and pure-Python
> calendar helpers (`julday`/`jd_to_utc`). Derived layers (panchanga, all 16 vargas D1–D60,
> dasha) validated: 0 mismatches (D60 irreducible ~0.1%). Regression: `python scripts/validate_ephemeris.py`.
>
> **INTEGRATION — DONE.** (1) Adapter seam wired: `astro_calc`, `kundli`, `scoring`, `muhurta`,
> `dossier_builder`, the `features/*` routers, the Streamlit + FastAPI entry points all call
> `shared.astro.ephemeris`; no `swe` in the runtime path. (2) Rahu/Ketu unified to **Mean** node
> everywhere (was TRUE in astro_calc/kundli, MEAN in scoring — now all MEAN). (3) Lahiri anchor
> FROZEN (all 5 anchors are frozen constants) and the `swisseph` calibration import dropped.
> `constants.PLANETS` are now NAME strings, not Swiss IDs. (4) `pyswisseph` moved to
> `requirements-dev.txt` (dev validation reference only); the Docker image bakes in `de440s.bsp`
> and excludes the old `ephe/` SE data. Dual-provider chart compare (skyfield vs swisseph) =
> 0 sign/nakshatra/house mismatches across all 5 ayanamshas. FastAPI endpoints smoke-tested.

**Plain-English summary:** Build the **free Skyfield + JPL engine** as the **shipping engine
now**, and validate it to **~99.9% practical parity with Swiss Ephemeris**. We keep
`pyswisseph` (Swiss Ephemeris) installed **only as the local validation reference** (the
measuring stick — not shipped, not distributed). **Buying the Swiss Ephemeris license is an
optional FUTURE upgrade**, only if/when the app profits. KP is an optional toggle (default
off). Everything sits behind a swappable adapter seam.

---

## Why this came up
Swiss Ephemeris is **dual-licensed**: free under **AGPL** (which would force open-sourcing the
entire backend — kills the moat) OR a **paid professional license (~CHF 750 one-time)**. We
won't pay now and won't open-source, so the **shipping engine must be a free, permissively-
licensed substitute.** (AGPL only triggers at public launch, so `pyswisseph` is fine to use
*privately during development* as a reference.)

## Verified facts (checked against primary sources, not assumed)
- **Swiss Ephemeris** = AGPL **or** ~CHF 750 one-time. AGPL's network clause means a public
  API/app triggers the open-source obligation → unusable closed-source for free.
- **`libephemeris`** = **AGPL-3.0** — confirmed via GitHub License API (SPDX `AGPL-3.0`) **and**
  PyPI (`AGPL-3.0-only`, v2.0.1). Same trap. (An AI wrongly claimed LGPL.)
- **VedAstro API** = tested live: slow (**2–7 s/call**), finicky format that **silently returns
  wrong-default charts**, free hobby tier (no SLA). Rejected — also splits the chart across
  frames (internal contradictions).
- **Skyfield (MIT) + JPL DE440 (public domain)** = genuinely free + commercial + closed-source-
  safe, **same accuracy source as Swiss Ephemeris** (SE is compressed JPL data).
- Three AIs (ChatGPT, Gemini, Claude) agree: byte-identical SE parity is impossible (different
  ΔT/precession), but **practical parity on what matters — sign/nakshatra/house/dasha — is very
  high (>99.9%)**, differing only at sub-arcsecond boundaries (where the big incumbent apps
  already disagree with each other too).
- **Key truth:** JPL *data* and astrology *math* are both free/public; only Swiss Ephemeris's
  convenient *packaging* is licensed.

## The decision

### The shipping engine = free Skyfield + JPL (built now)
1. **Build the Skyfield + JPL (DE440) engine** as the product's real engine.
2. **Re-implement the small low-level layer** Skyfield doesn't hand you: **Lahiri/Chitrapaksha
   ayanamsa**, **Ascendant**, **whole-sign houses**, **lunar node** (mean node in v1 — avoids
   the true-node root-finder), **sunrise/sunset + eclipses** (Skyfield provides these). All the
   higher Vedic logic (dasha, divisional charts, Ashtakavarga, yogas, panchanga, etc.) is
   existing Python that just consumes these numbers — unchanged.
3. **Validate to ~99.9% practical parity:** a harness diffs the Skyfield engine against the
   local `pyswisseph` reference across thousands of charts incl. boundary-heavy cases
   (sign/nakshatra/cusp edges, high latitudes, eclipses), and spot-checks public charts vs
   AstroSage. We ship a piece only once it meets the bar; if a needed piece can't, we flag it
   and decide (adjust, or use the SE-license upgrade for that).
4. **`pyswisseph` (Swiss Ephemeris) is kept ONLY as the local validation reference** during
   development — not shipped, not distributed, not in the product. It's the measuring stick.

### Adapter seam + KP toggle (built now)
5. **Ephemeris adapter seam:** one internal module exposes `get_planet_longitude`,
   `get_ascendant`, `get_houses`, `get_node`, `sunrise_set`, etc. **The whole app calls the
   adapter, never the engine directly.** → swapping engines later = one-file change.
6. **KP = optional flag-gated module, default OFF.** Placidus cusps computed **only when KP is
   on** (everything else uses whole-sign). KP code kept in the repo. KP's blunt "not promised"
   verdicts are also tonally wrong for a warm beginner-first app → off-by-default fixes that.
   **UPDATE (validated):** Placidus is now implemented on the free engine
   (`ephem_skyfield.placidus_cusps`) and validated to **0.00″ vs Swiss Ephemeris across
   300 charts × 12 cusps (incl. 60°N), with 0/3600 KP cusp sub-lord mismatches** — so KP
   needs **NO Swiss Ephemeris.** It can become a user setting whenever desired, with zero
   SE dependency. (Still off-by-default for tone; the default Vedic chart stays whole-sign.)
7. **Locked conventions (most accepted in Vedic astrology — verified):**
   - **Ayanamsa: Lahiri (Chitrapaksha)** — Government of India official standard; AstroSage default.
   - **Zodiac: Sidereal (Nirayana).**
   - **Houses (main chart): Whole-Sign (Rashi)** — traditional North & South Indian standard.
   - **Dasha: Vimshottari** (primary).
   - **Rahu/Ketu: Mean Node** — the classical Vedic standard (Surya Siddhanta; B.V. Raman,
     *Hindu Predictive Astrology*: "for all practical purposes... the Mean Node should be
     used"). Configurable (True available later); also simpler to build (polynomial, no
     root-finder) and unifies the code.
   - **KP/Placidus: deferred toggle, default off** (Western-derived; advanced-only).
   - **Bug-fix to fold in:** today the main chart/kundli use `TRUE_NODE` while matchmaking
     (`scoring.py`) uses `MEAN_NODE` — they disagree. **Unify everything to Mean.**

### Optional FUTURE upgrade (only if profitable — NOT now)
- **Buy the Swiss Ephemeris professional license** (~CHF 750 one-time, perpetual). Because of
  the adapter seam, switching the engine to SE — and unlocking easy KP/Placidus — is a
  contained, one-file change. Decided later, possibly by AI (Claude Code) or hired
  professionals, when there's revenue.

### Rejected
- **AGPL compliance** (open-sourcing the backend) — gives away the moat.
- **VedAstro / any per-feature external API** — slow, finicky, splits the chart across frames.
  Break-glass fallback only.

## Accuracy guarantee (how we avoid "wrong vs other apps")
Parity is a **measured fact before launch**, via the Swiss-Ephemeris diff harness +
AstroSage spot-checks, not a promise. Honest ceiling: even AstroSage / Drik Panchang /
ProKerala disagree at razor boundaries — matching the *dominant convention* (Lahiri +
whole-sign + common node) is the realistic best for everyone. KP-off in v1 removes the
hardest, most boundary-sensitive pieces (Placidus, true-node), so the ~99.9% bar is very
achievable for what v1 ships.

## What the user does manually
At build time: approve the node convention + ayanamsa default, approve the JPL data file
(~110 MB) in the deploy, and eyeball a few validated sample charts. Otherwise it's agent work.
