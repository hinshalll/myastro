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

from shared.timeloc import resolve_today


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


# Python date.weekday(): Monday=0 ... Sunday=6 → the planet ruling that day.
_WEEKDAY_PLANET = {0: "Moon", 1: "Mars", 2: "Mercury", 3: "Jupiter",
                   4: "Venus", 5: "Saturn", 6: "Sun"}
_WEEKDAY_NAME = ["Monday", "Tuesday", "Wednesday", "Thursday",
                 "Friday", "Saturday", "Sunday"]


def build_today_ritual(profile: dict, on_date: str | None = None, tz: str | None = None) -> dict:
    """One small, doable ritual for the Today card.

    Prefers the planet ruling today's weekday IF it's one the chart asks the
    user to support ("It's Saturday — do your Saturn remedy"); otherwise the
    top priority planet; otherwise a gentle generic practice.

    `tz` is bucket D (LOCATION_TIME_AUDIT.md): the WEEKDAY decides which planet's remedy is
    offered, so it must be the user's weekday. This used to fall back to `date.today()` — the
    SERVER's day — and the server is UTC, so for the first 5.5 hours of every Indian day it
    offered the PREVIOUS day's planet ("do your Saturn remedy" on a Sunday).
    """
    from shared.astro.kundli import compute_chart, PLANET_REMEDIES

    chart = compute_chart(_profile_to_birthdata(profile))
    rem = getattr(chart, "remedies", None) or {}
    priorities = [p for p in (rem.get("priority_planets") or []) if p in PLANET_REMEDIES]

    # explicit client date > explicit client tz > the profile's tz > IST. Never the server's.
    today = resolve_today(on_date, tz or profile.get("tz"))
    wd = today.weekday()
    day_planet = _WEEKDAY_PLANET[wd]

    if day_planet in priorities:
        chosen, is_planet_day = day_planet, True
    elif priorities:
        chosen, is_planet_day = priorities[0], False
    else:
        chosen, is_planet_day = None, False

    if chosen is None:
        # No priority planet with remedies → a gentle, universal practice.
        return {
            "date": today.isoformat(),
            "weekday": _WEEKDAY_NAME[wd],
            "is_planet_day": False,
            "ritual": {
                "planet": None,
                "action": "Light a ghee lamp at home before sundown and sit quietly for one minute.",
                "mantra": None,
                "daily_count": None,
                "tip": "A small daily flame steadies the mind and the day.",
                "deity": None,
                "why": "A calm, grounding practice for any day.",
            },
        }

    r = PLANET_REMEDIES[chosen]
    lal = r.get("lal_kitab") or []
    if is_planet_day:
        why = (f"Today is {_WEEKDAY_NAME[wd]}, ruled by {chosen} — "
               f"a planet your chart asks you to strengthen.")
    else:
        why = f"{chosen} is a key planet to support in your chart."

    return {
        "date": today.isoformat(),
        "weekday": _WEEKDAY_NAME[wd],
        "is_planet_day": is_planet_day,
        "ritual": {
            "planet": chosen,
            "action": f"Chant {chosen}'s mantra 108 times (one mala).",
            "mantra": r.get("beej_mantra"),
            "daily_count": 108,
            "tip": lal[0] if lal else None,
            "deity": r.get("deity"),
            "why": why,
        },
    }
