"""features.people.api — FastAPI router for the "You & People" shared-day readings.

Mounted at /people in fastapi_main.py. Both endpoints are pure math (no AI, no
new deps) and stateless — the app passes the people it already has.

    POST /people/couple-week    next-7-days weather between two people
    POST /people/family-grid    today's state for several saved people
"""
from __future__ import annotations

from features.people import service
from features.people.schemas import CoupleWeekRequest, FamilyGridRequest

try:
    from fastapi import APIRouter
    router = APIRouter()
except ImportError:  # pragma: no cover
    router = None


if router is not None:

    @router.post("/couple-week")
    def couple_week(req: CoupleWeekRequest) -> dict:
        """Next-N-days "relationship weather" rail between two people (default 7).

        FREE: pure math + a pre-baked meaning lookup, NO AI. Extends the single-day
        /dashboard/relationship-weather over a span (mirrors /dashboard/week). Each
        day carries a coarse `band` (good/neutral/difficult) for the rail colour and
        an `is_today` flag; the durable BASELINE ("how the two of you mesh") is
        lifted once into a top-level `baseline` block. Both profiles use the
        /kundli/compute shape; optional "start_date" (defaults to today, profile_a's
        tz). Moon-based, so it works even when either birth time is unknown.
        Deterministic for the same two profiles + span.
        """
        return service.couple_week(
            req.profile_a, req.profile_b, req.start_date, req.days
        )

    @router.post("/family-grid")
    def family_grid(req: FamilyGridRequest) -> dict:
        """Today's state for several saved people, at a glance.

        FREE: pure math + lookup, NO AI. Each row is that person's own daily
        "Cosmic Weather" (their day); if you pass your own chart as `viewer`, each
        row also gets the relationship-weather tone between you and them (your
        shared day). The whole grid is read on ONE shared calendar day so the cells
        line up. Each `people` item is { name, profile (kundli shape), relation_tag? };
        optional "date" (defaults to today). Moon-based — works at every birth-time
        tier. Deterministic for the same people + date.
        """
        people = [p.model_dump() for p in req.people]
        return service.family_grid(people, req.viewer, req.date)
