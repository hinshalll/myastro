"""shared.astro.calendar_doctor — the "Check my plans" (Calendar Doctor) judge.

The APP reads the user's calendar and MOVES events on-device (expo-calendar,
Android + iOS). This module only does the astrology: given each event's time,
say whether it sits in a weak window and, if so, suggest a better slot the same
day. Pure math (reuses daily_timing_windows), NO AI, and it never needs the
event's title (privacy) — times are enough.
"""
from collections import defaultdict
from datetime import date as _date


def _to_min(hm: str) -> int:
    h, m = hm.split(":")
    return int(h) * 60 + int(m)


def _day_segments(timing: dict):
    return [s for s in timing.get("choghadiya", []) if s.get("period") == "day"]


def _avoid_ranges(timing: dict):
    return [(_to_min(a["start"]), _to_min(a["end"])) for a in timing.get("avoid", [])]


def _judge(timing: dict, start_hm: str):
    """(verdict, label) for an event starting at start_hm."""
    t = _to_min(start_hm)
    in_avoid = any(a_s <= t < a_e for a_s, a_e in _avoid_ranges(timing))
    seg = next((s for s in _day_segments(timing)
                if _to_min(s["start"]) <= t < _to_min(s["end"])), None)
    quality = seg["quality"] if seg else "neutral"
    if in_avoid:
        return "weak", "sits in a hold-off stretch"
    if quality == "avoid":
        return "weak", "a low, tired part of the day"
    if quality == "good":
        return "good", "a warm, easy window"
    return "ok", "fine for everyday things"


def _best_slot(timing: dict, near_min: int):
    """Nearest strong day-window (good Choghadiya clear of Rahu Kaal etc.) to
    `near_min`, so the suggested move is small."""
    avoid = _avoid_ranges(timing)
    good = [s for s in _day_segments(timing)
            if s["quality"] == "good"
            and not any(_to_min(s["start"]) < a_e and a_s < _to_min(s["end"])
                        for a_s, a_e in avoid)]
    if not good:
        return None
    good.sort(key=lambda s: abs(_to_min(s["start"]) - near_min))
    best = good[0]
    return {"start": best["start"], "end": best["end"]}


def check_events(events: list[dict], lat: float, lon: float, tz: str) -> list[dict]:
    """For each event {date, start, end?, id?, title?} return
    {id, title, date, start, verdict (good|ok|weak), window_label, suggested_slot}.
    Only weak events get a suggested_slot (a better window that same day)."""
    from shared.astro.astro_calc import daily_timing_windows

    by_date: dict = defaultdict(list)
    for e in events:
        by_date[e["date"]].append(e)

    out: list[dict] = []
    for d, evs in by_date.items():
        timing = daily_timing_windows(_date.fromisoformat(d), lat, lon, tz)
        for e in evs:
            verdict, label = _judge(timing, e["start"])
            suggested = _best_slot(timing, _to_min(e["start"])) if verdict == "weak" else None
            out.append({
                "id": e.get("id"),
                "title": e.get("title"),
                "date": d,
                "start": e["start"],
                "verdict": verdict,
                "window_label": label,
                "suggested_slot": suggested,
            })
    return out
