"""features.planner.service — auto-place a to-do into the day's best window.

Pure logic (no DB, no clock): given a `daily_timing_windows` result, pick the
best DAYTIME Choghadiya window for a task. Good > neutral > avoid; an *important*
task must land in a strong window clear of Rahu Kaal / Yamaganda / Gulika; tasks
spread out (a window already taken by another task is skipped); only windows
still ahead of `now_hm` are considered. Returns the chosen window + a ~15-min-
before notify time so the client schedules a single local notification.
"""

_QUALITY_RANK = {"good": 0, "neutral": 1, "avoid": 2}
_QUALITY_LABEL = {"good": "a strong window", "neutral": "an ordinary window",
                  "avoid": "a low window"}


def _to_min(hm: str) -> int:
    h, m = hm.split(":")
    return int(h) * 60 + int(m)


def _to_hm(mins: int) -> str:
    mins = max(0, mins) % (24 * 60)
    return f"{mins // 60:02d}:{mins % 60:02d}"


def place_task(timing: dict, now_hm: str = "00:00", importance: str = "normal",
               taken=None, prefer_hora=None) -> dict | None:
    """Pick the best day window for a to-do from a daily_timing_windows result.

    `prefer_hora` (a set/list of planet names from the AI task-reader) nudges the
    choice toward a window whose planetary hour (attached as seg['hora_lord'] by the
    caller) suits the task — but only as a tiebreaker: the Choghadiya QUALITY still
    comes first, so a task never lands in a poor window just to match a Hora."""
    taken = set(taken or [])
    prefer = set(prefer_hora or [])
    now = _to_min(now_hm)
    avoid_ranges = [(_to_min(a["start"]), _to_min(a["end"])) for a in timing.get("avoid", [])]
    day_segs = [s for s in timing.get("choghadiya", []) if s.get("period") == "day"]

    def overlaps_avoid(s) -> bool:
        ss, se = _to_min(s["start"]), _to_min(s["end"])
        return any(ss < ae and a_s < se for a_s, ae in avoid_ranges)

    def key(s) -> str:
        return f'{s["start"]}-{s["end"]}'

    def hora_rank(s) -> int:                     # 0 = the Hora suits this task
        return 0 if (prefer and s.get("hora_lord") in prefer) else 1

    ahead = [s for s in day_segs if _to_min(s["end"]) > now and key(s) not in taken]
    if importance == "important":
        pool = [s for s in ahead if s["quality"] == "good" and not overlaps_avoid(s)]
        pool = pool or [s for s in ahead
                        if s["quality"] in ("good", "neutral") and not overlaps_avoid(s)]
    else:
        pool = [s for s in ahead
                if s["quality"] in ("good", "neutral") and not overlaps_avoid(s)]
    pool = pool or ahead          # last resort: whatever's left today
    if not pool:
        return None               # nothing left in the day → caller stores it unplaced

    # Quality first, then a matching Hora, then earliest.
    pool.sort(key=lambda s: (_QUALITY_RANK.get(s["quality"], 3), hora_rank(s), _to_min(s["start"])))
    chosen = pool[0]
    hora_fit = bool(prefer and chosen.get("hora_lord") in prefer)
    reason = (f'Placed in {_QUALITY_LABEL.get(chosen["quality"], "a window")} '
              f'({chosen["start"]} to {chosen["end"]}).')
    if hora_fit:
        reason += " Its planetary hour suits this kind of task."
    return {
        "window_start": chosen["start"],
        "window_end": chosen["end"],
        "window_quality": chosen["quality"],
        "window_name": chosen.get("name"),
        "hora_lord": chosen.get("hora_lord"),
        "hora_fit": hora_fit,
        "notify_at": _to_hm(_to_min(chosen["start"]) - 15),
        "reason": reason,
    }
