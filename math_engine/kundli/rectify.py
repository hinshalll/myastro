"""
math_engine/kundli/rectify.py
=============================

Birth-Time Rectification (BTR).

Only invoked when `birth_data.exact_time` is False. The user provides 3–5
major life events with dates; this module tries small time-offsets and
finds the one whose Vimshottari Antardasha alignment best fits the events.

Algorithm (event-fit scoring):

    For each candidate offset in ±60 minutes (1-min steps):
        1. Rebuild the chart with this offset.
        2. For each user event (date, life_area):
             - Determine MD-AD lords active on that date
             - Score how well the dasha-lords match the life area:
                  marriage:    Venus, Moon, 7th-lord
                  child:       Jupiter, 5th-lord
                  career:      Sun, Saturn, 10th-lord
                  accident:    Mars, Saturn, Rahu, 8th-lord
                  parent_loss: Sun (father), Moon (mother), 9th, 4th
        3. Sum the per-event scores; track the best-scoring offset.

For v1 we keep the search window tight (±60 min, 1-min step → 121 iterations)
to stay snappy. Users with truly unknown times (e.g. only the day) need a
wider window — exposed as an option.

This module returns the BEST offset; the UI applies it to BirthData and
re-computes the chart.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from math_engine.kundli.dashas import _build as _vim_build, _vimshottari_balance
from math_engine.constants import SIGN_LORDS_MAP


# ─────────────────────────────────────────────────────────────────────────────
# Life-event → significator lord mapping
# ─────────────────────────────────────────────────────────────────────────────

EVENT_SIGNIFICATORS = {
    "marriage":    {"planets": ["Venus", "Moon"],            "houses": [7]},
    "child":       {"planets": ["Jupiter"],                  "houses": [5]},
    "career":      {"planets": ["Sun", "Saturn"],            "houses": [10]},
    "promotion":   {"planets": ["Sun", "Jupiter"],           "houses": [10, 11]},
    "accident":    {"planets": ["Mars", "Saturn", "Rahu"],   "houses": [8, 6]},
    "parent_loss": {"planets": ["Sun", "Moon"],              "houses": [4, 9]},
    "education":   {"planets": ["Mercury", "Jupiter"],       "houses": [4, 5]},
    "property":    {"planets": ["Mars", "Venus"],            "houses": [4]},
    "travel":      {"planets": ["Mercury", "Rahu"],          "houses": [3, 12]},
}


def _score_event(event_date: datetime, life_area: str,
                 vim_periods: list, house_lord_map: dict) -> float:
    """
    Score how well the Vimshottari MD-AD active on event_date matches the
    life-area significators (planets + house lords).
    """
    sig = EVENT_SIGNIFICATORS.get(life_area)
    if not sig:
        return 0.0

    # Find the active MD-AD
    md_lord = ad_lord = None
    for md in vim_periods:
        if md.start <= event_date <= md.end:
            md_lord = md.lord
            for ad in md.children:
                if ad.start <= event_date <= ad.end:
                    ad_lord = ad.lord
                    break
            break
    if not md_lord:
        return 0.0

    score = 0.0
    significator_planets = set(sig["planets"])
    significator_houses = sig["houses"]
    for h in significator_houses:
        if h in house_lord_map:
            significator_planets.add(house_lord_map[h])

    if md_lord in significator_planets: score += 3.0
    if ad_lord in significator_planets: score += 2.0
    return score


def rectify(chart, events: list[dict],
            window_minutes: int = 60, step_minutes: int = 1) -> dict:
    """
    Find the best offset in minutes that explains the user's events.

    events = [{"date": datetime, "area": "marriage"|"career"|...}, ...]

    Returns:
        {
          "best_offset_minutes": float,
          "best_score":          float,
          "scores":              [(offset, score), ...],
          "confidence":          "high" | "medium" | "low",
        }
    """
    if not events:
        return {"best_offset_minutes": 0.0, "best_score": 0.0,
                "scores": [], "confidence": "low"}

    # Build house-lord map for scoring
    ls = chart.lagna.sign_index
    house_lord_map = {h: SIGN_LORDS_MAP[(ls + h - 1) % 12] for h in range(1, 13)}

    base_dt = chart.datetime_local
    moon_lon_base = chart.planets["Moon"].longitude
    # For tight rectification windows we re-use the natal Moon longitude
    # (Moon moves only ~0.5° per minute on average — within ±60 min that's
    # < 30° drift, but Vimshottari starting lord depends on nakshatra which
    # is ~13°; we need to recompute when crossing nakshatra boundaries.)

    scores: list[tuple[float, float]] = []
    for offset_min in range(-window_minutes, window_minutes + 1, step_minutes):
        candidate_dt = base_dt + timedelta(minutes=offset_min)
        # Approximation: Moon shift per minute ≈ 360°/(27.3 × 24 × 60) ≈ 0.00915°.
        moon_shift = offset_min * 0.00915
        moon_lon = (moon_lon_base + moon_shift) % 360

        # Rebuild Vimshottari
        try:
            periods = _vim_build(candidate_dt, moon_lon)
        except Exception:
            continue

        total = sum(_score_event(ev["date"], ev["area"], periods, house_lord_map)
                    for ev in events)
        scores.append((offset_min, total))

    if not scores:
        return {"best_offset_minutes": 0.0, "best_score": 0.0,
                "scores": [], "confidence": "low"}

    scores.sort(key=lambda x: x[1], reverse=True)
    best_offset, best_score = scores[0]
    max_possible = len(events) * 5.0
    confidence = "high" if best_score >= 0.7 * max_possible else (
                 "medium" if best_score >= 0.4 * max_possible else "low")

    return {
        "best_offset_minutes": float(best_offset),
        "best_score":          best_score,
        "max_possible":        max_possible,
        "scores":              scores,
        "confidence":          confidence,
    }
