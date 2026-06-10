"""features.rituals.service — chart-derived remedies for the Rituals tab.

Pure reshaping over the already-computed `chart.remedies` (no AI, no engine
change, no Streamlit). Every remedy is selected by the user's real chart
(afflicted / weak / dusthana-lord planets) and split into two zones:

  • practices — FREE, do-it actions: mantra / fasting / charity / Lal Kitab.
  • items     — OPTIONAL purchasable items: gemstone budget tiers
                (Maharatna = primary stone, Uparatna = affordable substitute)
                + rudraksha / yantra. The free practices always come first.

The selection + remedy data live in `shared/astro/kundli.py`
(`_recommend_remedies` → `chart.remedies`, `PLANET_REMEDIES`). This module
only presents them in the shape the mobile Rituals tab needs.
"""
from __future__ import annotations

from datetime import date, time as _time


def _profile_to_birthdata(p: dict):
    """Mirror of the kundli converter — keeps this feature self-contained.

    Birth-time tier: no time supplied -> "unknown", fall back to a noon
    placeholder so the chart still computes (Moon-based parts usable).
    """
    from shared.astro.kundli import BirthData

    time_known = bool(p.get("birth_time_known", True))
    raw_t = p.get("time")
    if raw_t in (None, ""):
        time_known = False
    if not time_known:
        t = _time(12, 0)
    elif isinstance(raw_t, str):
        parts = raw_t.split(":")
        t = _time(int(parts[0]), int(parts[1]), int(parts[2]) if len(parts) > 2 else 0)
    else:
        t = raw_t

    return BirthData(
        name=p.get("name", ""),
        date=date.fromisoformat(p["date"]) if isinstance(p["date"], str) else p["date"],
        time=t,
        place=p.get("place", ""),
        lat=float(p["lat"]),
        lon=float(p["lon"]),
        tz=p["tz"],
        gender=p.get("gender", "M"),
        exact_time=bool(p.get("exact_time", False)),
        birth_time_known=time_known,
    )


def _why(chart, planet: str) -> str:
    """A short plain-English reason this planet was selected (the 'why this?')."""
    pp = chart.planets.get(planet)
    if pp is None:
        return "a key planet to support"
    bits: list[str] = []
    if getattr(pp, "dignity", "") == "Debilitated":
        bits.append("debilitated")
    if getattr(pp, "is_combust", False) and planet != "Sun":
        bits.append("combust")
    if getattr(pp, "house", 0) in (6, 8, 12):
        bits.append(f"in the {pp.house}th house")
    return ("weak — " + ", ".join(bits)) if bits else "a key planet to support"


def build_remedies(profile: dict) -> dict:
    """Return the Rituals-tab payload for a profile: practices (free) + items
    (optional, gemstone tiers), all selected by the real chart."""
    from shared.astro.kundli import compute_chart, PLANET_REMEDIES

    chart = compute_chart(_profile_to_birthdata(profile))
    rem = getattr(chart, "remedies", None) or {}
    # Keep only classical planets that have remedies (drop outer planets like
    # Uranus/Neptune/Pluto, which Vedic remedies don't address).
    priorities = [p for p in (rem.get("priority_planets") or []) if p in PLANET_REMEDIES]

    practices: list[dict] = []
    items: list[dict] = []
    for p in priorities:
        r = PLANET_REMEDIES.get(p)
        if not r:
            continue
        why = _why(chart, p)
        practices.append({
            "planet": p,
            "why": why,
            "mantra": {
                "beej": r.get("beej_mantra"),
                "vedic": r.get("vedic_mantra"),
                "japa_count": r.get("japa_count"),
                "stotra": r.get("stotra"),
            },
            "fasting": r.get("vrat"),
            "charity": {"items": r.get("daan", []), "day": r.get("daan_day")},
            "colors": r.get("colors", []),
            "deity": r.get("deity"),
            "lal_kitab": r.get("lal_kitab", []),
        })
        ratna = r.get("ratna", {}) or {}
        items.append({
            "planet": p,
            "why": why,
            # Budget tiers, the authentic Vedic way:
            "gemstone_tiers": {
                "maharatna": ratna.get("primary"),    # primary precious stone (premium)
                "uparatna": ratna.get("substitute"),  # genuine affordable substitute
            },
            "wearing": {
                "finger": ratna.get("finger"),
                "day": ratna.get("day_to_wear"),
                "metal": ratna.get("metal"),
                "carat_range": ratna.get("carat_range"),
            },
            "rudraksha": r.get("rudraksha"),
            "yantra": r.get("yantra"),
            "optional_note": "Optional. The free practices above work on their own.",
        })

    return {
        "priority_planets": priorities,
        "daily_practice": rem.get("daily_practice", []),
        "practices": practices,            # FREE zone
        "items": items,                    # affiliate zone (gemstone tiers)
        "dosha_remedies": rem.get("per_dosha", {}),
        "time_precision": getattr(chart, "time_precision", None),
    }
