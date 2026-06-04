"""features.people.service — orchestration for the shared-day readings.

No new astrology math lives here: every calculation goes through shared.astro
(forecast + relationship_weather, which themselves go through the ephemeris
adapter). This layer only loops over people and stitches the pieces the grid
needs together. Lazy imports keep the heavy astro stack off the import path
until an endpoint is actually called.
"""
from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo


def couple_week(profile_a: dict, profile_b: dict,
                start_date: str | None = None, days: int = 7) -> dict:
    """The next-`days` "weather" between two people. Thin pass-through to the
    shared weekly relationship-weather (pure math + lookup)."""
    from shared.astro.relationship_weather import weekly_relationship_weather
    out = weekly_relationship_weather(profile_a, profile_b, start_date, days)
    out["ok"] = True
    return out


def _grid_date(people: list[dict], viewer: dict | None, date: str | None) -> str:
    """Resolve the single shared date the whole grid is read on. Explicit date
    wins; otherwise 'today' in the viewer's tz (falling back to the first
    person's tz) so every cell lines up on the same calendar day."""
    if date:
        return date
    tz = None
    if viewer:
        tz = viewer.get("tz")
    if not tz and people:
        tz = people[0].get("profile", {}).get("tz")
    tz = tz or "Asia/Kolkata"
    return datetime.now(ZoneInfo(tz)).date().isoformat()


def family_grid(people: list[dict], viewer: dict | None = None,
                date: str | None = None) -> dict:
    """Today's state for several saved people at a glance.

    Each row is that person's own daily "Cosmic Weather" (their day), plus — when
    `viewer` is given — the relationship-weather tone between you and them (your
    shared day). Pure math + lookup, no AI; the whole grid is read on one shared
    calendar day so the cells are comparable. `people` items: {name, profile,
    relation_tag?}. Works at every birth-time tier.
    """
    from shared.astro.forecast import daily_moon_forecast, _band
    from shared.astro.relationship_weather import daily_relationship_weather

    on_date = _grid_date(people, viewer, date)

    rows = []
    for p in people:
        prof = p.get("profile", {})
        f = daily_moon_forecast(prof, on_date)
        row = {
            "name": p.get("name", ""),
            "relation_tag": p.get("relation_tag"),
            "vibe_word": f["vibe_word"],
            "vibe_score": f["vibe_score"],
            "band": _band(f["vibe_score"]),
            "mood": f["mood"],
        }
        if viewer:
            w = daily_relationship_weather(viewer, prof, on_date)
            row["together"] = {
                "tone_word": w["tone_word"],
                "score": w["score"],
                "band": _band(w["score"]),
                "summary": w["summary"],
            }
        rows.append(row)

    return {"ok": True, "date": on_date, "people": rows}
