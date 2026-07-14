"""shared.astro.festivals — named-festival lookup for the Today greeting + Panchang.

The DATA lives in shared/data/festivals_india.json (edit that, not this file).
This is just the reader: it answers "is `date` a listed festival?" and lists the
festivals in a range (for the Panchang month grid). Dates that fall in a year not
present in the JSON simply return nothing — so a missing/outdated year never
breaks anything, it just shows no festival greeting until the file is updated.

Update flow + rationale: see FESTIVALS.md and the JSON's own `_how_to_update`.
Pure file read + cache, no AI, no network.
"""
from __future__ import annotations

import json
from datetime import date as _date
from functools import lru_cache
from pathlib import Path

_PATH = Path(__file__).resolve().parents[1] / "data" / "festivals_india.json"


@lru_cache(maxsize=1)
def _load() -> dict:
    try:
        with open(_PATH, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _as_date(d):
    return _date.fromisoformat(d) if isinstance(d, str) else d


def _greeting(entry: dict) -> str:
    return entry.get("greeting") or f"Happy {entry.get('name', '')}".strip()


def festival_for(on_date) -> dict | None:
    """{ name, greeting, date } if `on_date` is a listed festival, else None."""
    d = _as_date(on_date)
    for entry in _load().get(str(d.year), []):
        if entry.get("date") == d.isoformat():
            return {"name": entry.get("name", ""), "greeting": _greeting(entry),
                    "date": d.isoformat()}
    return None


def festivals_in_range(start, end) -> list[dict]:
    """All listed festivals within [start, end] inclusive (for the month grid)."""
    s, e = _as_date(start), _as_date(end)
    data = _load()
    out = []
    for yr in range(s.year, e.year + 1):
        for entry in data.get(str(yr), []):
            try:
                d = _date.fromisoformat(entry["date"])
            except (KeyError, ValueError):
                continue
            if s <= d <= e:
                out.append({"name": entry.get("name", ""), "date": entry["date"],
                            "greeting": _greeting(entry)})
    return out
